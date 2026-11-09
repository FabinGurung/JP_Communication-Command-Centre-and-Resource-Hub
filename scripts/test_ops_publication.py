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
                 "Latitude", "Longitude", "Status", "Location Ward Number", "Legacy Project Code"],
                ["PRJ-000001", True, "Reviewed name", "VALID", "28", "84", "Unknown", "14", "P001"],
                ["PRJ-000002", False, "Private name", "VALID", "29", "83", "Unknown", "15", "P002"],
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
                                                "status": "", "ward": "", "site": "P001"}])
            self.assertNotIn("Private", raw)
            self.assertEqual(data["progress"][0]["verification"], "UNVERIFIED")
            self.assertIn("u.search = location.search", (out / "resources/project-documents.html").read_text())
            self.assertFalse((out / "document-packets.json").exists())


if __name__ == "__main__":
    unittest.main()
