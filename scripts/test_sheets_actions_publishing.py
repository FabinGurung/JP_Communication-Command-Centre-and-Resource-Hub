#!/usr/bin/env python3
"""Offline integration tests: source -> atomic replica -> readback -> safe JSON."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from sync_sheets_to_pages import CONFIG, OUTPUT, ROOT, SyncError, append_snapshot, digest, normalize, records, sync, validate_bundle


class FakeGoogle:
    def __init__(self, root):
        self.config = json.loads((root / CONFIG).read_text())
        self.master = self.config["publishing_workbook_id"]
        registry = json.loads((root / "ops/control/map-sheets-source.v1.0.json").read_text())
        self.data = {}
        self.ids = {}
        header = ["table", "source_workbook_id", "source_tab", "master_tab", "owner_source_rows", "read_mode",
                  "connection", "edit_owner", "primary_key", "target_workbook_id", "target_link", "cutover_status", "instruction"]
        router = [header]
        for i, spec in enumerate(registry["tabs"]):
            name = spec["tab"]
            approved = json.loads((root / spec["public_projection"]).read_text())
            rows = [approved["columns"]] + [[r[c] for c in approved["columns"]] for r in approved["records"]]
            cfg = self.config["sources"][name]
            for fid in {self.master, cfg["workbook_id"], cfg["legacy_id"]}:
                self.data[fid, name] = normalize(rows)
            router.append([name, cfg["legacy_id"], name, name, str(len(rows)-1), "DIRECT_IMPORTRANGE", "CONNECTED",
                           name, spec["pk"], cfg["workbook_id"], "", "STAGED", ""])
            self.ids[i + 1] = name
        self.ids.update({50: "_SOURCE_ROUTER", 51: "00_MANIFEST", 52: "01_VERSION_HISTORY"})
        if self.config.get("resources_source"):
            catalog = json.loads((root / "ops/data/resource-catalog-normalized.v0.1.json").read_text())
            rows = [["Resource ID", "Site Reference", "Display Name", "Document Slot", "Source Drive File ID", "Source URL", "Publish"]]
            for site in catalog["sites"]:
                for item in site["files"]:
                    rows.append([item["resource_id"], item["project_id"], item["normalized_name"], item["document_slot"], item["source_drive_file_id"], item["source_drive_url"], "TRUE"])
            self.ids[53] = "project_resources"
            self.data[self.master, "project_resources"] = copy.deepcopy(rows)
            self.data[self.config["resources_source"]["workbook_id"], "project_resources"] = copy.deepcopy(rows)
        self.data[self.master, "_SOURCE_ROUTER"] = normalize(router)
        self.data[self.master, "00_MANIFEST"] = [["Field", "Value"], ["CONTROL_VERSION", "V000002"]]
        self.data[self.master, "01_VERSION_HISTORY"] = [["Version", "Time", "Scope", "Change", "PRE", "QA", "Rollback", "Data"],
                                                      ["V000002", "2026-10-25", "Navigation", "Rename", "PRE1", "VERIFIED", "Restore", "UNCHANGED"]]
        self.writes, self.snapshots = [], []
        self.fail_snapshot = False
        self.bad_readback = False
        self.change_during_scan = False
        self.source_reads = {}

    def meta(self, fid):
        return {"spreadsheetId": fid, "sheets": [{"properties": {"sheetId": sid, "title": name,
                "gridProperties": {"rowCount": 1000, "columnCount": 50}}}
                for sid, name in self.ids.items() if (fid, name) in self.data]}

    def read(self, fid, tab, meta=None):
        if (fid, tab) not in self.data:
            raise SyncError("REQUIRED_SOURCE_TAB_MISSING")
        rows = copy.deepcopy(self.data[fid, tab])
        key = (fid, tab)
        self.source_reads[key] = self.source_reads.get(key, 0) + 1
        if self.change_during_scan and fid == self.config["sources"]["projects"]["workbook_id"] and tab == "projects" and self.source_reads[key] > 1:
            rows[1][3] += " changed"
        if self.bad_readback and self.writes and fid == self.master and tab == "projects":
            rows[1][3] += " changed"
        return normalize(rows)

    def snapshot(self, fid, folder, prior_hash, state):
        if self.fail_snapshot:
            raise SyncError("PREVIOUS_VERSION_NOT_VERIFIED")
        self.snapshots.append(copy.deepcopy(self.data))
        return "VERIFIED_PRE_COPY"

    def write(self, fid, requests):
        assert fid == self.master, "The synchronizer must never write source cells"
        candidate = copy.deepcopy(self.data)
        for request in requests:
            if "repeatCell" in request:
                item = request["repeatCell"]
                candidate[fid, self.ids[item["range"]["sheetId"]]] = []
            else:
                item = request["updateCells"]
                name = self.ids[item["start"]["sheetId"]]
                # Every value is a literal, including strings beginning with '='.
                assert all(set(c["userEnteredValue"]) == {"stringValue"} for r in item["rows"] for c in r["values"])
                candidate[fid, name] = normalize([[c["userEnteredValue"]["stringValue"] for c in r["values"]] for r in item["rows"]])
        self.data = candidate
        self.writes.append(copy.deepcopy(requests))


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in [CONFIG, "ops/control/map-sheets-source.v1.0.json", "map-config.json", "ops/data/resource-catalog-normalized.v0.1.json"]:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / name).read_bytes())
        for src in (ROOT / "ops/data/map-sheets-public.v1").glob("*.json"):
            dest = self.root / "ops/data/map-sheets-public.v1" / src.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
        self.api = FakeGoogle(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_chain_and_idempotent_rerun(self):
        result = sync(self.api, self.root)
        self.assertTrue(result["live_google_sheets_fetch"])
        self.assertEqual(result["public_rows"], 165)
        self.assertEqual(len(self.api.snapshots), 1)
        bundle = json.loads((self.root / OUTPUT).read_text())
        self.assertEqual(bundle["tables"]["people"]["records"], [])
        router = records(self.api.data[self.api.master, "_SOURCE_ROUTER"], "table")
        self.assertEqual(len({r["source_workbook_id"] for r in router}), 14)
        self.assertTrue(all(r["connection"] == "API_READBACK_VERIFIED" for r in router))
        writes = len(self.api.writes)
        self.assertFalse(sync(self.api, self.root)["publishing_copy_changed"])
        self.assertEqual(len(self.api.snapshots), 1)
        self.assertEqual(len(self.api.writes), writes)
        self.assertEqual(bundle, json.loads((self.root / OUTPUT).read_text()))

    def test_readable_headers_with_individual_owners(self):
        router = self.api.data[self.api.master, "_SOURCE_ROUTER"]
        for row in router[1:]:
            spec = self.api.config["sources"][row[0]]
            row[1] = spec["workbook_id"]
            row[5] = "CONNECTED_API_INITIAL_ASSEMBLY"
        for spec in self.api.config["sources"].values():
            rows = self.api.data[spec["workbook_id"], spec["tab"]]
            rows[0] = [name.replace("_", " ").title() for name in rows[0]]
        sync(self.api, self.root)
        bundle = json.loads((self.root / OUTPUT).read_text())
        self.assertEqual(bundle["table_count"], 14)
        self.assertEqual(bundle["tables"]["people"]["records"], [])

    def test_resource_url_change_stops_before_any_write(self):
        spec = self.api.config["resources_source"]
        rows = self.api.data[spec["workbook_id"], "project_resources"]
        rows[1][rows[0].index("Source URL")] = "https://drive.google.com/file/d/unreviewed/view"
        with self.assertRaisesRegex(SyncError, "RESOURCE_SOURCE_CHANGE_REQUIRES_REVIEW"):
            sync(self.api, self.root)
        self.assertEqual(self.api.writes, [])

    def test_resource_slot_refresh_uses_joined_readback(self):
        spec = self.api.config["resources_source"]
        rows = self.api.data[spec["workbook_id"], "project_resources"]
        rows[1][rows[0].index("Document Slot")] = "Architectural and structural drawings"
        sync(self.api, self.root)
        bundle = json.loads((self.root / OUTPUT).read_text())
        self.assertEqual(bundle["resources"]["sites"][0]["files"][0]["document_slot"], "Architectural and structural drawings")
        self.assertEqual(self.api.data[self.api.master, "project_resources"], rows)

    def test_approved_live_field_and_no_new_version_for_unchanged_run(self):
        sync(self.api, self.root)
        fid = self.api.config["sources"]["projects"]["workbook_id"]
        rows = self.api.data[fid, "projects"]
        index = rows[0].index("display_name")
        rows[1][index] = "Public project name revised"
        sync(self.api, self.root)
        bundle = json.loads((self.root / OUTPUT).read_text())
        self.assertEqual(bundle["tables"]["projects"]["records"][0]["display_name"], "Public project name revised")
        self.assertEqual(self.api.data[self.api.master, "01_VERSION_HISTORY"][-1][0], "V000004")

    def test_staged_source_drift_stops_before_any_write(self):
        fid = self.api.config["sources"]["project_funding"]["workbook_id"]
        self.api.data[fid, "project_funding"][1][2] = "ORG-000001"
        with self.assertRaisesRegex(SyncError, "STAGED_SOURCE_CHANGED"):
            sync(self.api, self.root)
        self.assertEqual(self.api.writes, [])
        self.assertEqual(self.api.snapshots, [])

    def test_permission_or_snapshot_failure_keeps_previous_output(self):
        output = self.root / OUTPUT
        output.write_text("last working public bundle")
        self.api.fail_snapshot = True
        with self.assertRaisesRegex(SyncError, "PREVIOUS_VERSION"):
            sync(self.api, self.root)
        self.assertEqual(self.api.writes, [])
        self.assertEqual(output.read_text(), "last working public bundle")

    def test_concurrent_source_change_stops(self):
        self.api.change_during_scan = True
        with self.assertRaisesRegex(SyncError, "SOURCE_CHANGED_DURING_READ"):
            sync(self.api, self.root)
        self.assertEqual(self.api.writes, [])

    def test_failed_provider_readback_does_not_export(self):
        self.api.bad_readback = True
        with self.assertRaisesRegex(SyncError, "PUBLISHING_READBACK_MISMATCH"):
            sync(self.api, self.root)
        self.assertFalse((self.root / OUTPUT).exists())

    def test_private_fields_and_new_rows_never_escape(self):
        sync(self.api, self.root)
        fid = self.api.config["sources"]["projects"]["workbook_id"]
        rows = self.api.data[fid, "projects"]
        rows[1][rows[0].index("public_notes")] = "UNREVIEWED_PRIVATE_NOTE"
        secret = copy.deepcopy(rows[1])
        secret[0] = "PRJ-999999"
        secret[rows[0].index("display_name")] = "UNADMITTED_PROJECT_NAME"
        rows.append(secret)
        people_id = self.api.config["sources"]["people"]["workbook_id"]
        people = self.api.data[people_id, "people"]
        people.append(["PER-999999", "P1", "PRIVATE_PERSON", "TRUE", "PRIVATE_PHONE", "FALSE"])
        sync(self.api, self.root)
        public = (self.root / OUTPUT).read_text()
        for value in ["UNREVIEWED_PRIVATE_NOTE", "PRJ-999999", "UNADMITTED_PROJECT_NAME", "PRIVATE_PERSON", "PRIVATE_PHONE"]:
            self.assertNotIn(value, public)

    def test_visibility_revocation_is_respected(self):
        sync(self.api, self.root)
        fid = self.api.config["sources"]["projects"]["workbook_id"]
        rows = self.api.data[fid, "projects"]
        removed = rows[1][0]
        rows[1][rows[0].index("is_public")] = "FALSE"
        sync(self.api, self.root)
        bundle = json.loads((self.root / OUTPUT).read_text())
        for table in bundle["tables"].values():
            self.assertFalse(any(r.get("project_id") == removed for r in table["records"]))

    def test_duplicate_or_bad_join_stops_before_write(self):
        fid = self.api.config["sources"]["projects"]["workbook_id"]
        self.api.data[fid, "projects"][2][0] = self.api.data[fid, "projects"][1][0]
        with self.assertRaisesRegex(SyncError, "PRIMARY_KEY"):
            sync(self.api, self.root)
        self.assertEqual(self.api.writes, [])

    def test_field_visibility_changes_reach_the_browser_settings(self):
        sync(self.api, self.root)
        fid = self.api.config["sources"]["project_publication_settings"]["workbook_id"]
        rows = self.api.data[fid, "project_publication_settings"]
        project = rows[1][rows[0].index("project_id")]
        for flag in ["show_project_name", "show_coordinates", "show_legal_contractor"]:
            rows[1][rows[0].index(flag)] = "FALSE"
        sync(self.api, self.root)
        bundle = json.loads((self.root / OUTPUT).read_text())["tables"]
        public = next(r for r in bundle["projects"]["records"] if r["project_id"] == project)
        for key in ["display_name", "project_name", "latitude", "longitude", "executing_company_id"]:
            self.assertEqual(public[key], "")
        settings = next(r for r in bundle["project_publication_settings"]["records"] if r["project_id"] == project)
        self.assertEqual(settings["show_project_name"], "FALSE")
        self.assertFalse(any(r["project_id"] == project and r["role"] == "CONTRACTOR" for r in bundle["project_parties"]["records"]))

    def test_validated_bundle_rejects_private_injection(self):
        sync(self.api, self.root)
        bundle = json.loads((self.root / OUTPUT).read_text())
        bundle["tables"]["projects"]["records"][0]["public_notes"] = "UNREVIEWED_NOTE"
        with self.assertRaisesRegex(SyncError, "UNAPPROVED_PUBLIC_FIELD"):
            validate_bundle(bundle, self.root)

    def test_archive_is_append_only_and_recovers_without_duplicate(self):
        header = {"type": "header", "format": "JP_PUBLISHING_RESTORE_HISTORY_V1", "publishing_workbook_id": "MASTER"}
        raw = (json.dumps(header) + "\n").encode()
        state = {"data": {"projects": [["project_id"], ["PRJ-000001"]]}}
        first, record_id = append_snapshot(raw, "MASTER", digest(state), state)
        self.assertTrue(first.startswith(raw))
        self.assertEqual(record_id, "R000001")
        self.assertEqual(append_snapshot(first, "MASTER", digest(state), state), (first, "R000001"))
        second, record_id = append_snapshot(first, "MASTER", digest({"next": 2}), {"next": 2})
        self.assertTrue(second.startswith(first))
        self.assertEqual(record_id, "R000002")
        corrupt = first.replace(b"PRJ-000001", b"PRJ-999999")
        with self.assertRaisesRegex(SyncError, "CHAIN_INVALID"):
            append_snapshot(corrupt, "MASTER", "next", {})


if __name__ == "__main__":
    unittest.main()
