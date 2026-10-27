#!/usr/bin/env python3
"""Offline integration tests: source -> atomic replica -> readback -> safe JSON."""
import copy
import json
import tempfile
import unittest
import hashlib
from pathlib import Path
from sync_sheets_to_pages import CONFIG, OUTPUT, ROOT, SyncError, append_snapshot, digest, normalize, records, sync, validate_bundle
from field_sheet_sources import HEADERS, collect


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
        if self.config.get("notification_sources"):
            self.original_text = "Synthetic planner instruction for source-quote tests."
            sha = hashlib.sha256(self.original_text.encode()).hexdigest()
            payload = json.loads((root / "ops/data/site-notifications-public.v1.json").read_text())
            for grant in self.config["notification_policy"]["admitted_sources"].values():
                grant["sha256"] = sha
            (root / CONFIG).write_text(json.dumps(self.config))
            s = payload["sources"][0]
            i = payload["items"][0]
            source_rows = [["Project", "Date", "Origin", "Source Message", "Saved Original", "Source ID", "Project ID", "Site Reference", "Company", "Source Version", "Source SHA256"],
                           [i["project_name"], s["date_npt"], s["provider"], s["source_url"], s["drive_source_url"], s["source_id"], i["project_id"], i["site_reference"], i["company"], s["version"], sha]]
            headers = ["Notification ID", "Notice ID", "Source ID", "Project", "Project ID", "Site Reference", "Company", "Category", "Instruction", "Quantity", "Unit", "Due Date", "Detail State", "Display Order", "Source Message", "Saved Original", "Source Version", "Source SHA256", "Source Quote", "Review State", "Publish"]
            rows = [headers]
            for i in payload["items"]:
                rows.append([i["notification_id"], i["notice_id"], i["source_id"], i["project_name"], i["project_id"], i["site_reference"], i["company"], i["category"], i["instruction"], i["quantity"], i["unit"], i["due_date"], i["detail_state"], str(i["display_order"]), s["source_url"], s["drive_source_url"], s["version"], sha, self.original_text, "Reviewed", "TRUE"])
            for sid, name, values in [(54, "message_sources", source_rows), (55, "site_notifications", rows)]:
                self.ids[sid] = name
                self.data[self.master, name] = copy.deepcopy(values)
                self.data[self.config["notification_sources"][name]["workbook_id"], name] = copy.deepcopy(values)
        if self.config.get("field_sources"):
            self.source_reads = {}
            self.writes = []
            self.bad_readback = False
            self.change_during_scan = False
            admitted = json.loads((root / self.config["contacts_reviewed_projection"]).read_text())
            for spec in self.config["field_sources"]:
                kind = spec["adapter"]
                headers = spec["expected_header"][:]
                body = []
                if kind == "contacts":
                    directory = next(d for d in admitted["directories"] if d["company"] == spec["company"])
                    body = [[r["name"], r["phone"], r["role"], r["projects"], r["verification"], "PRIVATE_CONTACT_NOTE", r["contact_id"]] for r in directory["records"]]
                elif kind == "materials":
                    body = [[spec["company"] + "-MOV1", "2026-10-01", "PRJ-000007", "Site", "Cement", "Consumption", "1", "Bag", "PRIVATE_MATERIAL_NOTE"]]
                elif kind == "progress":
                    body = [["2026-10-01", "Site", "Reported", "PRIVATE_WORK_DETAIL", "PRIVATE_PROGRESS_NOTE", spec["company"] + "-PROG1", "PRJ-000007", ""]]
                elif kind == "readiness":
                    body = [["2026-10-01", "Site", "W1", "PRIVATE_ACTIVITY"]]
                elif kind == "attendance_split":
                    body = [["2026-10-01", "Reported status", "", "2026-10-01", "PRIVATE_SITE", "PRIVATE_ATTENDANCE_NOTE"]]
                elif kind == "attendance_checkbox":
                    body = [["2026-10-01", "TRUE"], ["2026-10-02", "FALSE"]]
                elif kind == "expenses_rich":
                    body = [["EXP1", "2026-10-01", "PRIVATE_ITEM", "Site", "1", "", "", "PRIVATE_EXPENSE_NOTE"]]
                elif kind == "expenses_simple":
                    body = [["2026-10-01", "Site", "1", "PRIVATE_SIMPLE_EXPENSE"]]
                elif kind == "vendor_summary":
                    body = [["1", "PRIVATE_VENDOR", "1", "", ""]]
                elif kind == "supplier_review":
                    body = [["", "PRIVATE_TRANSCRIPTION", "", "", "", "", "", "Not reviewed", "", "", "", "", "", "", "", "", "file", "PRIVATE_EVIDENCE"]]
                elif kind == "measurement_review":
                    body = [["MEAS1", "", "", "", "", "", "PRIVATE_MEASUREMENT_SOURCE", "", "", "", "", ""]]
                values = ([['Private vendor summary']] if kind == "vendor_summary" else []) + [headers] + body
                self.data[spec["workbook_id"], spec["tab"]] = normalize(values)
            joined, _ = collect(self, self.config["field_sources"])
            for sid, (name, values) in enumerate(joined.items(), 60):
                self.ids[sid] = name
                self.data[self.master, name] = copy.deepcopy(values)
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
                "gridProperties": {"rowCount": 2000, "columnCount": 50}}, "tables": [t for t in getattr(self, "native_tables", []) if t["range"]["sheetId"] == sid]}
                for sid, name in self.ids.items() if (fid, name) in self.data]}

    def original(self, fid):
        return self.original_text

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
            elif "updateTable" in request:
                item = request["updateTable"]["table"]
                for table in self.native_tables:
                    if table["tableId"] == item["tableId"]:
                        table["range"] = copy.deepcopy(item["range"])
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
        for name in [CONFIG, "ops/control/map-sheets-source.v1.0.json", "map-config.json", "ops/data/resource-catalog-normalized.v0.1.json", "ops/data/site-notifications-public.v1.json", "ops/data/company-contacts-reviewed.v1.json"]:
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

    def test_field_tables_keep_private_rows_out_of_public_bundle(self):
        sync(self.api, self.root)
        payload = json.loads((self.root / OUTPUT).read_text())
        self.assertEqual(payload["contacts"]["published_records"], 26)
        self.assertFalse(any(v in json.dumps(payload) for v in ["PRIVATE_CONTACT_NOTE", "PRIVATE_MATERIAL_NOTE", "PRIVATE_WORK_DETAIL", "PRIVATE_PROGRESS_NOTE", "PRIVATE_ACTIVITY", "PRIVATE_ATTENDANCE_NOTE", "PRIVATE_ITEM", "PRIVATE_EXPENSE_NOTE", "PRIVATE_SIMPLE_EXPENSE", "PRIVATE_VENDOR", "PRIVATE_TRANSCRIPTION", "PRIVATE_EVIDENCE", "PRIVATE_MEASUREMENT_SOURCE"]), "Private field sentinel reached public projection")
        self.assertEqual(len(self.api.data[self.api.master, "site_attendance"]) - 1, 5)
        self.assertEqual(payload["contacts"]["refresh_mode"], "ACTIONS_JOINED_SHEET_READBACK")

    def test_contact_refresh_and_new_contact_withheld_with_native_table_growth(self):
        spec = next(s for s in self.api.config["field_sources"] if s["adapter"] == "contacts")
        rows = self.api.data[spec["workbook_id"], spec["tab"]]
        admitted = rows[1][6]
        rows[1][1] = "+9779800000001"
        rows.append(["PRIVATE_NEW_PERSON", "+9779800000002", "Role", "Project", "", "PRIVATE_NOTE", "FBL-CON-999999"])
        sid = next(k for k, v in self.api.ids.items() if v == "company_contacts")
        self.api.native_tables = [{"tableId": "NATIVE_CONTACTS", "name": "JP_Publishing_company_contacts", "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 27, "startColumnIndex": 0, "endColumnIndex": 10}}]
        sync(self.api, self.root)
        payload = json.loads((self.root / OUTPUT).read_text())
        published = {r["contact_id"]: r for d in payload["contacts"]["directories"] for r in d["records"]}
        self.assertEqual(published[admitted]["phone"], "+9779800000001")
        self.assertNotIn("FBL-CON-999999", published)
        self.assertNotIn("PRIVATE_NEW_PERSON", json.dumps(payload))
        self.assertEqual(self.api.native_tables[0]["range"]["endRowIndex"], 28)

    def test_withdrawn_contacts_do_not_reappear_from_the_reviewed_snapshot(self):
        for spec in self.api.config["field_sources"]:
            if spec["adapter"] == "contacts":
                self.api.data[spec["workbook_id"], spec["tab"]] = [spec["expected_header"]]
        sync(self.api, self.root)
        payload = json.loads((self.root / OUTPUT).read_text())
        self.assertEqual(payload["contacts"]["published_records"], 0)
        self.assertTrue(all(d["records"] == [] for d in payload["contacts"]["directories"]))

    def test_contact_identity_reassignment_stops_before_any_write(self):
        spec = next(s for s in self.api.config["field_sources"] if s["adapter"] == "contacts")
        self.api.data[spec["workbook_id"], spec["tab"]][1][0] = "PRIVATE_REPLACEMENT_PERSON"
        with self.assertRaisesRegex(SyncError, "CONTACT_IDENTITY_CHANGE_REQUIRES_REVIEW"):
            sync(self.api, self.root)
        self.assertEqual(self.api.writes, [])
        self.assertEqual(self.api.snapshots, [])

    def test_field_layout_drift_stops_before_any_write(self):
        spec = self.api.config["field_sources"][0]
        self.api.data[spec["workbook_id"], spec["tab"]][0][0] = "Unexpected field"
        with self.assertRaisesRegex(SyncError, "FIELD_SOURCE_LAYOUT_CHANGED"):
            sync(self.api, self.root)
        self.assertEqual(self.api.writes, [])

    def test_contact_status_cannot_claim_live_in_a_snapshot_bundle(self):
        sync(self.api, self.root)
        payload = json.loads((self.root / OUTPUT).read_text())
        payload["live_google_sheets_fetch"] = False
        with self.assertRaisesRegex(SyncError, "CONTACT_REFRESH_MODE_MISMATCH"):
            validate_bundle(payload, self.root)

    def test_unapproved_private_bundle_section_is_rejected(self):
        sync(self.api, self.root)
        payload = json.loads((self.root / OUTPUT).read_text())
        payload["site_expenses"] = {"private": "PRIVATE_MONEY"}
        with self.assertRaisesRegex(SyncError, "UNAPPROVED_PUBLIC_BUNDLE_SECTION"):
            validate_bundle(payload, self.root)

    def test_full_chain_and_idempotent_rerun(self):
        result = sync(self.api, self.root)
        self.assertTrue(result["live_google_sheets_fetch"])
        self.assertEqual(result["public_rows"], 165)
        self.assertEqual(len(self.api.snapshots), 1)
        bundle = json.loads((self.root / OUTPUT).read_text())
        self.assertEqual(bundle["tables"]["people"]["records"], [])
        router = records(self.api.data[self.api.master, "_SOURCE_ROUTER"], "table")
        self.assertEqual(len({r["source_workbook_id"] for r in router}), 14)
        self.assertTrue(all(r["connection"] == ("NOT_CONNECTED_EMPTY_TEMPLATE" if r["table"] == "project_material_inventory" else "API_READBACK_VERIFIED") for r in router))
        writes = len(self.api.writes)
        self.assertFalse(sync(self.api, self.root)["publishing_copy_changed"])
        self.assertEqual(len(self.api.snapshots), 1)
        self.assertEqual(len(self.api.writes), writes)
        repeated = json.loads((self.root / OUTPUT).read_text())
        # An unchanged source causes no additional Sheet/archive writes. Each
        # actual fetch still receives its own honest observation timestamp.
        self.assertGreaterEqual(repeated["publication_receipt"]["fetched_at_utc"],
                                bundle["publication_receipt"]["fetched_at_utc"])
        repeated["publication_receipt"]["fetched_at_utc"] = bundle["publication_receipt"]["fetched_at_utc"]
        self.assertEqual(bundle, repeated)

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
