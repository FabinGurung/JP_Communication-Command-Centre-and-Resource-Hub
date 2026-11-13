import json
import tempfile
import unittest
from pathlib import Path

from publish_operations import SOURCES, build as original_build

def add_live_source_fixtures(tables):
    """Synthetic seven-source layout; production always reads Google Sheets."""
    tables["organizations"] = [
        ["Organization ID", "Organization Name", "Is Public", "Active", "Data Quality Status"],
        ["ORG-000001", "Fishtail Builders Pvt Ltd", True, True, "VALID"],
        ["ORG-000002", "PRIVATE ORGANIZATION NAME", False, True, "VALID"],
    ]
    tables["directory"] = [
        ["Subject", "Google Sheet", "Data or View"],
        *[("QA " + name, "https://docs.google.com/spreadsheets/d/" + book + "/edit", tab)
          for name, (book, tab) in SOURCES.items() if name != "directory"]
    ]
    return tables

def build(tables, out, timestamp):
    return original_build(add_live_source_fixtures(tables), out, timestamp)


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
        self.assertEqual(set(SOURCES), set(add_live_source_fixtures(tables)))
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
            # Library-owned Astam content is no longer duplicated by Operations.
            astam_home = (out / "feasibility/index.html").read_text()
            astam_guide = (out / "feasibility/buyer-guide/index.html").read_text()
            self.assertIn("https://fabingurung.github.io/jp-field-desk-library/feasibility/", astam_home)
            self.assertIn("https://fabingurung.github.io/jp-field-desk-library/feasibility/buyer-guide/", astam_guide)
            self.assertIn("u.search = location.search", astam_home)
            self.assertIn("u.search = location.search", astam_guide)
            self.assertFalse((out / "feasibility/buyer-guide/guide.json").exists())
            self.assertFalse((out / "ops/data/land-feasibility/astam-village-public.v1.0.json").exists())
            self.assertFalse((out / "ops/data/land-feasibility/astam-buyer-guide-public.v1.0.json").exists())
            ops_html = (out / "index.html").read_text()
            for key in ("projects", "work", "resources", "manpower", "activities"):
                self.assertIn('data-map-mode="' + key + '"', ops_html)
            self.assertIn("field-pulse", ops_html)
            self.assertIn('data-project-status="Completed"', ops_html)
            self.assertIn('data-project-status="Construction"', ops_html)
            self.assertIn('data-project-status="Approval"', ops_html)
            self.assertIn('data-project-status="unpublished"', ops_html)
            self.assertIn('id="status-filter"', ops_html)
            wall = (out / "memory-wall.html").read_text()
            self.assertIn("Projects and Locations", wall)
            self.assertIn("01 Website Source Sheets", wall)
            self.assertIn("02 Website Sheets and Registers", wall)
            self.assertIn('href="./memory-wall.html"', ops_html)
            # Hybrid navigation: notifications first, map second. Reports and
            # source provenance have their own internal pages on the same site.
            self.assertLess(ops_html.index('id="notifications"'), ops_html.index('id="map"'))
            self.assertNotIn('id="progress"', ops_html)
            self.assertNotIn('id="sources"', ops_html)
            self.assertIn('href="./progress.html"', ops_html)
            self.assertIn('href="./sources.html"', ops_html)
            self.assertIn('aria-current="page">Notifications</a>', ops_html)
            self.assertIn('id="notice-site"', ops_html)
            for key in ("all", "Work", "Materials", "Supervision"):
                self.assertIn('data-notice-category="' + key + '"', ops_html)
            report = (out / "progress.html").read_text()
            sources = (out / "sources.html").read_text()
            self.assertIn('id="progress-list"', report)
            self.assertIn('id="report-trend"', report)
            self.assertIn('id="source-dates"', sources)
            self.assertIn('href="./#notifications"', report)
            self.assertIn('href="./#notifications"', sources)
            self.assertIn('aria-current="page">Daily progress</a>', report)
            self.assertIn('aria-current="page">Sources &amp; history</a>', sources)
            self.assertTrue((out / "progress.js").is_file())
            self.assertTrue((out / "sources.js").is_file())
            # Legacy anchors are preserved by a client-side same-site redirect.
            self.assertIn('location.hash === "#progress"', (out / "app.js").read_text())
            self.assertIn('location.hash === "#sources"', (out / "app.js").read_text())
            self.assertIn("../progress.html", (out / "site-operations/history.html").read_text())

            app = (out / "app.js").read_text()
            self.assertIn("demand not connected", app)
            self.assertIn("remaining-task backlog", app)
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
            self.assertEqual(data["identity"]["public_ids_added_since_historical_index"], [])
            self.assertEqual(data["provenance"]["live_workbook_count"], 7)
            self.assertEqual(data["provenance"]["directory_role"], "READ_ONLY_SOURCE_POINTER_VALIDATION")
            self.assertEqual(data["projects"][0]["quality"], "WARNING")
            self.assertEqual(data["provenance"]["source_dates"]["projects"]["latest_public_record_date"],
                             "2026-11-10")
            self.assertIsNone(data["provenance"]["source_dates"]["progress"]["latest_public_record_date"])
            self.assertNotIn("PRJ-999999", raw)
            self.assertNotIn("SECRET RETIRED ALIAS", raw)
            self.assertNotIn("PRIVATE_SOURCE_TOKEN", raw)


    def test_project_status_visible_only_with_source_and_display_grants(self):
        tables = {
            "projects": [
                ["Project ID","Is Public","Display Name","Data Quality Status","Executing Company ID",
                 "Latitude","Longitude","Status","Location Ward Number","Legacy Project Code"],
                ["PRJ-990001",True,"Public completed","VALID","ORG-000001","28.2","83.98","Completed","1",""],
                ["PRJ-990002",True,"Public but status hidden","WARNING","ORG-000001","28.3","83.99",
                 "SECRET_STATUS_DO_NOT_PUBLISH","2",""],
                ["PRJ-990003",False,"Private site","VALID","ORG-000001","28.4","84.0","Approval","3",""],
            ],
            "choices":[
                ["Publication Setting ID","Project ID","Show Project Name","Show Coordinates",
                 "Show Ward Number","Show Status"],
                ["Q-1","PRJ-990001",True,True,True,True],
                ["Q-2","PRJ-990002",True,True,True,False],
                ["Q-3","PRJ-990003",True,True,True,True],
            ],
            "messages":[["Source ID"]],
            "notices":[["Notification ID","Project ID"]],
            "progress":[["Project Work ID","Project ID","Is Public","Description Override",
                         "Last Updated","Work Status","Verification Status"]]
        }
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            self.assertEqual(build(tables,out,"source-filter-fixture"),(2,0,0))
            raw=(out/"operations.json").read_text()
            rows=json.loads(raw)["projects"]
            self.assertEqual([p["status"] for p in rows],["Completed",""])
            self.assertEqual(rows[1]["quality"],"WARNING")
            self.assertNotIn("SECRET_STATUS_DO_NOT_PUBLISH",raw)
            self.assertNotIn("Private site",raw)
            self.assertNotIn("PRJ-990003",raw)
            self.assertEqual(len(rows),2)


if __name__ == "__main__":
    unittest.main()
