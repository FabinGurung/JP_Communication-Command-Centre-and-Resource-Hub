#!/usr/bin/env python3
"""Actions-owned source Sheets -> publishing Sheet -> approved public map JSON.

Private cell values stay in memory. Only the approved public bundle is written to
disk. A Google failure never falls back to a fresh-looking stale publication.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CONFIG = "ops/control/sheets-actions-publishing.v1.json"
OUTPUT = "ops/data/map-data.v1.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
ERRORS = {"#REF!", "#N/A", "#VALUE!", "#ERROR!", "#DIV/0!", "#NAME?", "#NUM!"}


class SyncError(RuntimeError):
    """Safe error codes only: no provider response bodies or private values."""


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def column(number):
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def normalize(rows):
    result = [[str(v).strip() for v in row] for row in rows]
    for row in result:
        while row and not row[-1]:
            row.pop()
    while result and not result[-1]:
        result.pop()
    return result


def records(rows, key):
    rows = normalize(rows)
    if not rows:
        raise SyncError("SOURCE_HEADER_MISSING")
    headers = [s.lower() for s in rows[0]]
    if key not in headers or not all(headers) or len(headers) != len(set(headers)):
        raise SyncError("SOURCE_HEADER_INVALID")
    result = []
    for raw in rows[1:]:
        if not raw:
            continue
        if len(raw) > len(headers) or any(v in ERRORS for v in raw):
            raise SyncError("SOURCE_CELL_ERROR")
        result.append(dict(zip(headers, raw + [""] * (len(headers) - len(raw)))))
    keys = [r[key] for r in result]
    if not all(keys) or len(keys) != len(set(keys)):
        raise SyncError("SOURCE_PRIMARY_KEY_INVALID")
    return result


def validate_relations(tables):
    ids = {name: {r[key] for r in rows} for name, (key, rows) in tables.items()}
    joins = {
        "projects": [("executing_company_id", "organizations")],
        "project_funding": [("project_id", "projects"), ("funding_party_id", "organizations")],
        "project_parties": [("project_id", "projects")],
        "project_work_items": [("project_id", "projects"), ("work_id", "work_catalog")],
        "project_material_inventory": [("project_id", "projects"), ("material_id", "materials_master")],
        "project_components": [("project_id", "projects")],
        "project_source_links": [("project_id", "projects")],
        "project_publication_settings": [("project_id", "projects")],
        "organization_locations": [("organization_id", "organizations")],
        "organizations": [("parent_organization_id", "organizations")],
    }
    for name, pairs in joins.items():
        for row in tables[name][1]:
            for field, target in pairs:
                if row.get(field) and row[field] not in ids[target]:
                    raise SyncError("SOURCE_FOREIGN_KEY_INVALID")
    for row in tables["project_parties"][1]:
        target = {"PERSON": "people", "ORGANIZATION": "organizations"}.get(row.get("party_entity_type"))
        if target is None or row.get("party_id") not in ids[target]:
            raise SyncError("PARTY_FOREIGN_KEY_INVALID")
    for _, rows in tables.values():
        for row in rows:
            for key, limit in (("latitude", 90), ("longitude", 180)):
                if row.get(key):
                    try:
                        valid = abs(float(row[key])) <= limit
                    except ValueError:
                        valid = False
                    if not valid:
                        raise SyncError("COORDINATE_INVALID")


def project_public(root, source_tables):
    """Refresh only explicitly granted public fields and already-admitted IDs.

    New people/projects, private rows, free-text evidence, financial values and
    previously redacted cells are not silently admitted by an automated refresh.
    """
    config = json.loads((root / CONFIG).read_text())
    registry = json.loads((root / "ops/control/map-sheets-source.v1.0.json").read_text())
    settings = {r["project_id"]: r for r in source_tables["project_publication_settings"][1]}
    output = {}
    for item in registry["tabs"]:
        name, key = item["tab"], item["pk"]
        approved = json.loads((root / item["public_projection"]).read_text())
        live = {r[key]: r for r in source_tables[name][1]}
        allowed_fields = set(config["refresh_fields"].get(name, []))
        if not allowed_fields <= set(approved["columns"]):
            raise SyncError("PUBLIC_FIELD_CONTRACT_INVALID")
        rows = []
        for baseline in approved["records"]:
            current = live.get(baseline[key])
            if current is None or ("is_public" in current and current["is_public"].upper() != "TRUE"):
                continue
            row = copy.deepcopy(baseline)
            for field in allowed_fields:
                if field not in current:
                    raise SyncError("PUBLIC_SOURCE_COLUMN_MISSING")
                row[field] = current[field]
            if name == "projects":
                visibility = settings.get(row[key])
                if visibility is None:
                    raise SyncError("PROJECT_PUBLICATION_SETTINGS_MISSING")
                for flag, fields in config["project_visibility_fields"].items():
                    if visibility.get(flag, "").upper() != "TRUE":
                        for field in fields:
                            row[field] = ""
            elif name == "project_components":
                if settings.get(row["project_id"], {}).get("show_coordinates", "").upper() != "TRUE":
                    row["latitude"], row["longitude"] = "", ""
            rows.append(row)
        output[name] = {**approved, "records": rows, "row_count": len(rows),
                        "origin": "ACTIONS_GOOGLE_SHEETS_APPROVED_FIELDS",
                        "projection_scope": "ADMITTED_IDS_AND_APPROVED_FIELDS_ONLY"}
    # Remove dependants of withdrawn records, never expose their private parents.
    projects = {r["project_id"] for r in output["projects"]["records"]}
    orgs = {r["organization_id"] for r in output["organizations"]["records"]}
    people = {r["person_id"] for r in output["people"]["records"]}
    for name, payload in output.items():
        if name != "projects":
            payload["records"] = [r for r in payload["records"] if not r.get("project_id") or r["project_id"] in projects]
        if name == "project_parties":
            payload["records"] = [r for r in payload["records"] if r["party_id"] in
                                  (orgs if r["party_entity_type"] == "ORGANIZATION" else people)]
            payload["records"] = [r for r in payload["records"] if r.get("role") != "CONTRACTOR" or
                                  settings.get(r["project_id"], {}).get("show_legal_contractor", "").upper() == "TRUE"]
        payload["row_count"] = len(payload["records"])
    validate_relations({x["tab"]: (x["pk"], output[x["tab"]]["records"]) for x in registry["tabs"]})
    return output


class Google:
    def __init__(self, snapshot_history_id):
        import google.auth
        from google.auth.transport.requests import AuthorizedSession
        credentials, _ = google.auth.default(scopes=SCOPES)
        self.session = AuthorizedSession(credentials)
        self.snapshot_history_id = snapshot_history_id

    def request(self, method, url, **kwargs):
        for attempt in range(6):
            try:
                response = self.session.request(method, url, timeout=90, **kwargs)
            except Exception:
                raise SyncError("GOOGLE_TRANSPORT_FAILED") from None
            if response.status_code not in {429, 500, 502, 503, 504} or attempt == 5:
                break
            time.sleep(min(2 ** (attempt + 1), 32))
        if not response.ok:
            raise SyncError(f"GOOGLE_HTTP_{response.status_code}")
        return response

    def call(self, method, url, **kwargs):
        return self.request(method, url, **kwargs).json()

    def meta(self, fid):
        return self.call("GET", f"https://sheets.googleapis.com/v4/spreadsheets/{fid}",
                         params={"fields": "spreadsheetId,sheets.properties"})

    def read(self, fid, tab, meta=None):
        meta = meta or self.meta(fid)
        found = [x["properties"] for x in meta["sheets"] if x["properties"]["title"] == tab]
        if len(found) != 1:
            raise SyncError("REQUIRED_SOURCE_TAB_MISSING")
        grid = found[0]["gridProperties"]
        if grid["rowCount"] > 10000 or grid["columnCount"] > 100:
            raise SyncError("SOURCE_EXCEEDS_REVIEWED_READ_BOUND")
        name = "'" + tab.replace("'", "''") + "'!A1:" + column(grid["columnCount"]) + str(grid["rowCount"])
        result = self.call("GET", f"https://sheets.googleapis.com/v4/spreadsheets/{fid}/values/{quote(name, safe='')}",
                           params={"valueRenderOption": "FORMATTED_VALUE"})
        return normalize(result.get("values", []))

    def snapshot(self, fid, folder, previous_hash, state):
        # A service account cannot own new My Drive files. Append immutable PRE
        # records to this existing, user-owned archive file instead of files.copy.
        archive_id = self.snapshot_history_id
        url = f"https://www.googleapis.com/drive/v3/files/{archive_id}"
        metadata = self.call("GET", url, params={"fields": "id,parents,mimeType"})
        if folder not in metadata.get("parents", []) or metadata.get("mimeType", "").startswith("application/vnd.google-apps."):
            raise SyncError("PREVIOUS_VERSIONS_DESTINATION_INVALID")
        response = self.request("GET", url, params={"alt": "media"})
        raw = response.content
        etag = response.headers.get("ETag")
        if not etag:
            raise SyncError("ARCHIVE_CONDITIONAL_WRITE_TOKEN_MISSING")
        updated, record_id = append_snapshot(raw, fid, previous_hash, state)
        if updated != raw:
            self.call("PATCH", f"https://www.googleapis.com/upload/drive/v3/files/{archive_id}",
                      params={"uploadType": "media", "fields": "id"}, data=updated,
                      headers={"Content-Type": "application/x-ndjson", "If-Match": etag})
        readback = self.request("GET", url, params={"alt": "media"}).content
        if readback != updated:
            raise SyncError("PREVIOUS_VERSION_READBACK_FAILED")
        return archive_id + "#" + record_id

    def write(self, fid, requests):
        self.call("POST", f"https://sheets.googleapis.com/v4/spreadsheets/{fid}:batchUpdate", json={"requests": requests})


def append_snapshot(raw, fid, previous_hash, state):
    """Verify every earlier record and append; never rewrite previous snapshots."""
    if len(raw) > 32 * 1024 * 1024:
        raise SyncError("PREVIOUS_VERSIONS_ROTATION_REQUIRED")
    try:
        rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
    except (ValueError, UnicodeError):
        raise SyncError("PREVIOUS_VERSIONS_FILE_INVALID") from None
    if not rows or rows[0] != {"type": "header", "format": "JP_PUBLISHING_RESTORE_HISTORY_V1", "publishing_workbook_id": fid}:
        raise SyncError("PREVIOUS_VERSIONS_HEADER_INVALID")
    chain = digest(rows[0])
    existing = None
    for number, row in enumerate(rows[1:], 1):
        check = {k: v for k, v in row.items() if k != "record_hash"}
        if row.get("id") != f"R{number:06d}" or row.get("previous_hash") != chain or row.get("record_hash") != digest(check):
            raise SyncError("PREVIOUS_VERSIONS_CHAIN_INVALID")
        chain = row["record_hash"]
        if row.get("snapshot_key") == previous_hash:
            if row.get("state") != state:
                raise SyncError("PREVIOUS_VERSION_KEY_COLLISION")
            existing = row["id"]
    if existing:
        return raw, existing
    row = {"id": f"R{len(rows):06d}", "type": "pre_snapshot", "snapshot_key": previous_hash,
           "previous_hash": chain, "captured_utc": datetime.now(timezone.utc).isoformat(), "state": state}
    row["record_hash"] = digest(row)
    updated = raw + (b"" if raw.endswith(b"\n") else b"\n") + (json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode()
    return updated, row["id"]


def update_values(sid, rows, clear_grid=None):
    requests = []
    if clear_grid:
        requests.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0,
            "endRowIndex": clear_grid["rowCount"], "startColumnIndex": 0, "endColumnIndex": clear_grid["columnCount"]},
            "cell": {}, "fields": "userEnteredValue"}})
    requests.append({"updateCells": {"start": {"sheetId": sid, "rowIndex": 0, "columnIndex": 0},
        "rows": [{"values": [{"userEnteredValue": {"stringValue": str(v)}} for v in row]} for row in rows],
        "fields": "userEnteredValue"}})
    return requests


def sync(api, root=ROOT):
    cfg = json.loads((root / CONFIG).read_text())
    registry = json.loads((root / "ops/control/map-sheets-source.v1.0.json").read_text())
    master = cfg["publishing_workbook_id"]
    meta = api.meta(master)
    tabs = {x["properties"]["title"]: x["properties"] for x in meta["sheets"]}
    router = api.read(master, "_SOURCE_ROUTER", meta)
    manifest = api.read(master, "00_MANIFEST", meta)
    history = api.read(master, "01_VERSION_HISTORY", meta)
    route_rows = records(router, "table")
    routes = {r["table"]: r for r in route_rows}
    expected = {x["tab"] for x in registry["tabs"]}
    if set(routes) != expected or set(cfg["sources"]) != expected:
        raise SyncError("SOURCE_COVERAGE_INCOMPLETE")
    incoming, before, source_tables = {}, {}, {}
    for spec in registry["tabs"]:
        name = spec["tab"]
        spec_source = cfg["sources"][name]
        route = routes[name]
        if (route["source_workbook_id"] not in {spec_source["legacy_id"], spec_source["workbook_id"]}
                or route["source_tab"] != name or route["master_tab"] != name
                or route["target_workbook_id"] != spec_source["workbook_id"]):
            raise SyncError("UNREVIEWED_SOURCE_ROUTE")
        target = api.read(spec_source["workbook_id"], name)
        if route["source_workbook_id"] != spec_source["workbook_id"]:
            legacy = api.read(route["source_workbook_id"], name)
            if normalize(legacy) != normalize(target):
                raise SyncError("STAGED_SOURCE_CHANGED_CUTOVER_REVIEW_REQUIRED")
        incoming[name] = target
        approved_columns = json.loads((root / spec["public_projection"]).read_text())["columns"]
        if not target or not set(approved_columns) <= {s.lower() for s in target[0]}:
            raise SyncError("REQUIRED_SOURCE_COLUMNS_MISSING")
        source_tables[name] = (spec["pk"], records(target, spec["pk"]))
        before[name] = api.read(master, name, meta)
        # Never silently truncate the publishing replica.
        width = max(map(len, target), default=0)
        if len(target) > tabs[name]["gridProperties"]["rowCount"] or width > tabs[name]["gridProperties"]["columnCount"]:
            raise SyncError("PUBLISHING_GRID_EXPANSION_REQUIRED")
    validate_relations(source_tables)
    project_public(root, source_tables)  # Reject unsafe joins before any write.
    fingerprint = digest(incoming)
    previous = {r[0]: r[1] for r in manifest if len(r) > 1}
    active = all(r["source_workbook_id"] == cfg["sources"][r["table"]]["workbook_id"]
                 and r["read_mode"] == "GITHUB_ACTIONS_API" for r in route_rows)
    changed = before != incoming or previous.get("ACTIONS_SOURCE_DIGEST") != fingerprint or not active
    if changed:
        # Re-read the sources immediately before mutation: a concurrent edit must not
        # create a mixed-scan release. Source errors occur before the PRE copy/write.
        for name, rows in incoming.items():
            if api.read(cfg["sources"][name]["workbook_id"], name) != rows:
                raise SyncError("SOURCE_CHANGED_DURING_READ")
        if api.read(master, "_SOURCE_ROUTER", meta) != router or api.read(master, "00_MANIFEST", meta) != manifest:
            raise SyncError("PUBLISHING_CONTROLS_CHANGED_DURING_READ")
        for name, rows in before.items():
            if api.read(master, name, meta) != rows:
                raise SyncError("PUBLISHING_COPY_CHANGED_DURING_READ")
        prior_state = {"data": before, "manifest": manifest, "router": router, "history": history}
        snap = api.snapshot(master, cfg["previous_versions_folder_id"], digest(prior_state), prior_state)
        numbers = [int(r[0][1:]) for r in history[1:] if r and re.fullmatch(r"V[0-9]{6}", r[0])]
        if not numbers:
            raise SyncError("PUBLISHING_VERSION_HISTORY_MISSING")
        version = f"V{max(numbers)+1:06d}"
        stamp = datetime.now(timezone.utc).isoformat()
        requests = []
        for name, rows in incoming.items():
            requests += update_values(tabs[name]["sheetId"], rows, tabs[name]["gridProperties"])
        for row in router[1:]:
            if row:
                row += [""] * (len(router[0]) - len(row))
                spec = cfg["sources"][row[0]]
                row[1], row[5], row[6], row[11], row[12] = spec["workbook_id"], "GITHUB_ACTIONS_API", "API_READBACK_REQUIRED", "API_OWNER_ACTIVE", "Edit the individual source Sheet; Actions rebuilds this copy"
                row[4] = str(len(source_tables[row[0]][1]))
        control_values = {"CONTROL_VERSION": version, "ACTIONS_SOURCE_DIGEST": fingerprint,
                          "PAGES_CONNECTION": "GITHUB_ACTIONS_API", "PUBLISHING_RULE": "SOURCE SHEETS → ACTIONS → PUBLISHING COPY → VALIDATED JSON → PAGES"}
        for row in manifest:
            if row and row[0] in control_values:
                row[1:2] = [control_values.pop(row[0])]
        manifest += [[key, value] for key, value in control_values.items()]
        requests += update_values(tabs["_SOURCE_ROUTER"]["sheetId"], router)
        requests += update_values(tabs["00_MANIFEST"]["sheetId"], manifest)
        history.append([version, stamp, "Automatic publishing copy", "Rebuilt from 14 individual source Sheets", snap,
                        "SOURCE_VALIDATED; READBACK_REQUIRED", "Restore PRE content into same publishing ID", fingerprint])
        requests += update_values(tabs["01_VERSION_HISTORY"]["sheetId"], history)
        api.write(master, requests)  # One atomic Sheets batch; no source writes.
    # Build from the provider readback of the assembled Sheet, not the input arrays.
    readback_tables = {}
    for spec in registry["tabs"]:
        name = spec["tab"]
        actual = api.read(master, name)
        if actual != incoming[name]:
            raise SyncError("PUBLISHING_READBACK_MISMATCH")
        if api.read(cfg["sources"][name]["workbook_id"], name) != incoming[name]:
            raise SyncError("SOURCE_CHANGED_BEFORE_PUBLICATION")
        readback_tables[name] = (spec["pk"], records(actual, spec["pk"]))
    # Record successful readback in the same history row, including on recovery
    # from an interruption after the first atomic write. This is no new version.
    verified_router = api.read(master, "_SOURCE_ROUTER")
    verified_history = api.read(master, "01_VERSION_HISTORY")
    receipt_changed = False
    for row in verified_router[1:]:
        if row and row[6] != "API_READBACK_VERIFIED":
            row[6] = "API_READBACK_VERIFIED"
            receipt_changed = True
    if verified_history[-1][5] != "SOURCE_AND_MASTER_READBACK_VERIFIED":
        verified_history[-1][5] = "SOURCE_AND_MASTER_READBACK_VERIFIED"
        receipt_changed = True
    if receipt_changed:
        api.write(master, update_values(tabs["_SOURCE_ROUTER"]["sheetId"], verified_router)
                  + update_values(tabs["01_VERSION_HISTORY"]["sheetId"], verified_history))
        if api.read(master, "_SOURCE_ROUTER") != verified_router or api.read(master, "01_VERSION_HISTORY") != verified_history:
            raise SyncError("SUCCESS_RECEIPT_READBACK_MISMATCH")
    public = project_public(root, readback_tables)
    payload = {"schema_version": "1.0.0", "bundle_id": "JP_MAP_REVIEWED_SHEETS_V1",
               "publication_mode": "ACTIONS_SHEETS_REFRESH_APPROVED_FIELDS", "live_google_sheets_fetch": True,
               "reviewed_static_fields_retained": True, "table_count": len(public),
               "source_evidence": {name: {"source": "PUBLISHING_SHEET_READBACK", "row_count": item["row_count"],
                                          "sha256": digest(item)} for name, item in public.items()}, "tables": public}
    validate_bundle(payload, root)
    output = root / OUTPUT
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    temporary.replace(output)
    return {"live_google_sheets_fetch": True, "publishing_copy_changed": changed,
            "public_tables": len(public), "public_rows": sum(x["row_count"] for x in public.values())}


def validate_bundle(payload, root=ROOT):
    baseline = json.loads((root / "ops/control/map-sheets-source.v1.0.json").read_text())
    config = json.loads((root / CONFIG).read_text())
    map_config = json.loads((root / "map-config.json").read_text())
    if set(payload["tables"]) != {x["tab"] for x in baseline["tabs"]} or payload["table_count"] != 14:
        raise SyncError("PUBLIC_TABLE_COVERAGE_INVALID")
    tables = {}
    for spec in baseline["tabs"]:
        name, pk = spec["tab"], spec["pk"]
        item = payload["tables"][name]
        approved = json.loads((root / spec["public_projection"]).read_text())
        permitted_ids = {r[pk] for r in approved["records"]}
        approved_rows = {r[pk]: r for r in approved["records"]}
        mutable = set(config["refresh_fields"].get(name, []))
        masked = {f for fields in config["project_visibility_fields"].values() for f in fields} if name == "projects" else set()
        if item["columns"] != approved["columns"] or item["row_count"] != len(item["records"]):
            raise SyncError("PUBLIC_COLUMN_OR_COUNT_INVALID")
        keys = []
        for row in item["records"]:
            if set(row) != set(approved["columns"]) or any(not isinstance(v, str) for v in row.values()):
                raise SyncError("PUBLIC_ROW_INVALID")
            if row[pk] not in permitted_ids:
                raise SyncError("UNADMITTED_PUBLIC_RECORD")
            for field, value in row.items():
                if field not in mutable and value != approved_rows[row[pk]][field] and not (field in masked and value == ""):
                    raise SyncError("UNAPPROVED_PUBLIC_FIELD_CHANGE")
            if name == "projects" and row.get("status") and row["status"] not in map_config["status_styles"]:
                raise SyncError("PUBLIC_PROJECT_STATUS_INVALID")
            if "active" in mutable and row.get("active") not in {"TRUE", "FALSE"}:
                raise SyncError("PUBLIC_ACTIVE_FLAG_INVALID")
            if name == "project_publication_settings" and any(row.get(f) not in {"TRUE", "FALSE"} for f in mutable):
                raise SyncError("PUBLIC_VISIBILITY_FLAG_INVALID")
            keys.append(row[pk])
        if len(keys) != len(set(keys)):
            raise SyncError("DUPLICATE_PUBLIC_RECORD")
        tables[name] = (pk, item["records"])
    validate_relations(tables)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-bundle", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_bundle:
            validate_bundle(json.loads((ROOT / OUTPUT).read_text()))
            print("PUBLIC_SHEETS_BUNDLE_VALIDATED")
        else:
            cfg = json.loads((ROOT / CONFIG).read_text())
            print(json.dumps(sync(Google(cfg["previous_versions_file_id"])), sort_keys=True))
    except SyncError as exc:
        raise SystemExit("SHEETS_SYNC_STOPPED: " + str(exc)) from None
    except Exception:
        # Provider errors may contain cell contents, URLs, credentials or responses.
        raise SystemExit("SHEETS_SYNC_STOPPED: UNEXPECTED_PROVIDER_OR_CONTRACT_ERROR") from None
