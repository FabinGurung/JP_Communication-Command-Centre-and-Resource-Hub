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
            self.assertIn("u.search = location.search", (out / "resources/project-documents.html").read_text())
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


if __name__ == "__main__":
    unittest.main()
