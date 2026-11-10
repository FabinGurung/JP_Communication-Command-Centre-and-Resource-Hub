import json
import tempfile
import unittest
from pathlib import Path

from publish_operations import SOURCES, build


class OperationsPublicationTest(unittest.TestCase):
    def test_scope_privacy_and_legacy_routes(self):
        tables = {
            "projects": [
                ["Project ID", "Is Public", "Display Name", "Data Quality Status",
                 "Executing Company ID", "Latitude", "Longitude", "Status", "Location Ward Number", "Legacy Project Code"],
                ["PRJ-000001", True, "Reviewed name", "VALID", "ORG-000001", "28", "84", "Unknown", "14", "P001"],
                ["PRJ-000002", False, "Private name", "VALID", "ORG-000002", "29", "83", "Unknown", "15", "P002"],
            ],
            "choices": [
                ["Publication Setting ID", "Project ID", "Show Project Name", "Show Coordinates", "Show Ward Number", "Show Status"],
                ["PPS-001", "PRJ-000001", True, False, False, False],
            ],
            "messages": [["Source ID"]],
            "notices": [["Notification ID", "Project ID"]],
            "progress": [
                ["Project Work ID", "Project ID", "Is Public", "Description Override", "Last Updated",
                 "Work Status", "Verification Status", "Rate NPR"],
                ["PROG-001", "PRJ-000001", True, "Reported work", "2026-11-09",
                 "IN_PROGRESS", "UNVERIFIED", "Private rate"],
                ["PROG-002", "PRJ-000002", True, "Private work", "2026-11-09",
                 "IN_PROGRESS", "UNVERIFIED", "Private rate"],
            ],
        }
        self.assertEqual(set(SOURCES), set(tables))
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            self.assertEqual(build(tables, out, "test"), (1, 0, 1))
            raw = (out / "operations.json").read_text()
            data = json.loads(raw)
            self.assertEqual(data["projects"], [{"id": "PRJ-000001", "name": "Reviewed name",
                                                "status": "", "ward": "", "site": "P001",
                                                 "company_id": "ORG-000001", "company": "Fishtail Builders Pvt Ltd"}])
            self.assertNotIn("Private", raw)
            self.assertEqual(data["progress"][0]["verification"], "UNVERIFIED")
            self.assertEqual(data["provenance"]["kind"], "PUBLIC_SAFE_READ_ONLY_SHEETS_PROJECTION")
            self.assertEqual(data["provenance"]["latest_public_report_date"], "2026-11-09")
            self.assertEqual(data["provenance"]["direct_discord_collector"], "ON_HOLD")
            self.assertNotIn("Private rate", raw)
            self.assertNotIn("ORG-000002", raw)
            self.assertIn("source_readback_at_npt", data["provenance"])
            self.assertEqual(data["provenance"]["schema_version"], "1.2.0")
            self.assertEqual(data["provenance"]["source_dates"]["progress"]["latest_public_record_date"], "2026-11-09")
            self.assertIsNone(data["provenance"]["source_dates"]["projects"]["latest_public_record_date"])
            self.assertIsNone(data["provenance"]["provider_modified_at"])
            self.assertEqual(data["identity"]["public_project_count"], 1)
            self.assertTrue(data["identity"]["nonpublic_or_retired_rows_excluded"])
            library = "https://fabingurung.github.io/jp-field-desk-library/"
            for path in ("index.html", "owner-help.html", "resources/index.html"):
                with self.subTest(path=path):
                    html = (out / path).read_text()
                    self.assertIn(f'href="{library}"', html)
                    self.assertNotIn("https://fabingurung.github.io/JP_Field_and_Desk_Resource_Library/", html)
            redirect = (out / "resources/project-documents.html").read_text()
            self.assertIn(f'href="{library}resources/project-documents.html"', redirect)
            self.assertIn("u.search = location.search", redirect)
            self.assertNotIn("https://fabingurung.github.io/JP_Field_and_Desk_Resource_Library/", redirect)
            for route, target in {
                "workspace.html": "./owner-help.html#workspace",
                "workspace/index.html": "../owner-help.html#workspace",
                "guide/index.html": "../owner-help.html#guide",
                "guide/3-pages/index.html": "../../owner-help.html#guide",
                "guide/7-pages/index.html": "../../owner-help.html#guide",
                "guide/15-pages/index.html": "../../owner-help.html#guide",
            }.items():
                self.assertIn(target, (out / route).read_text())
            self.assertTrue((out / "owner-help.html").is_file())
            guide = json.loads((out / "feasibility/buyer-guide/guide.json").read_text())
            self.assertEqual(guide["public_scope"], "EDUCATIONAL_PUBLIC_SAFE")
            self.assertIs(guide["project"]["coordinates_public"], False)
            self.assertTrue((out / "feasibility/buyer-guide/index.html").is_file())
            self.assertFalse((out / "document-packets.json").exists())
            self.assertFalse((out / "ops/data/current-works.json").exists())


    def test_public_warning_identity_and_retired_alias_do_not_leak(self):
        # Synthetic fixture: real nonpublic source IDs and source references
        # must never be copied into a public repository or website.
        tables = {
            "projects": [
                ["Project ID", "Is Public", "Display Name", "Data Quality Status", "Last Updated",
                 "Executing Company ID", "Latitude", "Longitude", "Status", "Location Ward Number", "Legacy Project Code",
                 "Source Reference"],
                ["PRJ-999998", True, "Public project awaiting review", "WARNING", "2026-11-10",
                 "ORG-000002", "", "", "In progress", "14", "", ""],
                ["PRJ-999999", False, "SECRET RETIRED ALIAS", "RETIRED_ALIAS_ONLY", "2026-11-10",
                 "ORG-000001", "28", "84", "", "14", "", "PRIVATE_SOURCE_TOKEN"],
            ],
            "choices": [
                ["Publication Setting ID", "Project ID", "Show Project Name", "Show Coordinates",
                 "Show Ward Number", "Show Status"],
                ["PPS-999998", "PRJ-999998", True, True, True, True],
                ["PPS-999999", "PRJ-999999", True, True, True, True],
            ],
            "messages": [["Source ID"]],
            "notices": [["Notification ID", "Project ID"]],
            "progress": [
                ["Project Work ID", "Project ID", "Is Public", "Description Override",
                 "Last Updated", "Work Status", "Verification Status"],
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            self.assertEqual(build(tables, out, "2026-11-10T14:00+05:45"), (1, 0, 0))
            raw = (out / "operations.json").read_text()
            data = json.loads(raw)
            self.assertEqual(data["identity"]["public_project_count"], 1)
            self.assertEqual(data["identity"]["public_ids_added_since_historical_index"], ["PRJ-999998"])
            self.assertEqual(data["projects"][0]["quality"], "WARNING")
            self.assertEqual(data["provenance"]["source_dates"]["projects"]["latest_public_record_date"],
                             "2026-11-10")
            self.assertIsNone(data["provenance"]["source_dates"]["progress"]["latest_public_record_date"])
            self.assertNotIn("PRJ-999999", raw)
            self.assertNotIn("SECRET RETIRED ALIAS", raw)
            self.assertNotIn("PRIVATE_SOURCE_TOKEN", raw)


if __name__ == "__main__":
    unittest.main()
