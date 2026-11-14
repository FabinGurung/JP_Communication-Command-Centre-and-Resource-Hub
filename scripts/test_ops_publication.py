import json
import tempfile
import unittest
from pathlib import Path

from publish_operations import SOURCES, build as original_build, reviewed_closure

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
            for key in ("projects", "work", "activities"):
                self.assertIn('data-map-mode="' + key + '"', ops_html)
            for key in ("resources", "manpower"):
                self.assertNotIn('data-map-mode="' + key + '"', ops_html)
            self.assertIn("field-pulse", ops_html)
            self.assertIn('data-project-status="Completed"', ops_html)
            self.assertIn('data-project-status="Construction"', ops_html)
            self.assertIn('data-project-status="Approval"', ops_html)
            self.assertIn('data-project-status="unpublished"', ops_html)
            self.assertIn('id="status-filter"', ops_html)
            wall = (out / "memory-wall.html").read_text()
            self.assertIn("Projects and Locations", wall)
            self.assertIn("01 Website Source Sheets", wall)
            self.assertIn("Companies and Organizations", wall)
            self.assertIn("Publishing Source Directory", wall)
            self.assertIn("02 Website Sheets and Registers", wall)
            self.assertIn('href="./memory-wall.html"', ops_html)
            # Hybrid navigation: notifications first, map second. Reports and
            # source provenance have their own internal pages on the same site.
            self.assertLess(ops_html.index('id="map"'), ops_html.index('id="notifications"'))
            self.assertIn('id="notifications" class="surface notification-centre" hidden', ops_html)
            self.assertIn('id="back-to-sites"', ops_html)
            self.assertIn('id="directory-toggle"', ops_html)
            self.assertNotIn('id="progress"', ops_html)
            self.assertNotIn('id="sources"', ops_html)
            self.assertIn('href="./progress.html"', ops_html)
            self.assertIn('href="./sources.html"', ops_html)
            self.assertIn('aria-current="page">Map</a>', ops_html)
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
            self.assertIn('<h1>Daily reported progress</h1>', report)
            self.assertIn('<h1>Sources &amp; history</h1>', sources)
            self.assertTrue((out / "progress.js").is_file())
            self.assertTrue((out / "sources.js").is_file())
            self.assertTrue((out / "extraction.html").is_file())
            self.assertTrue((out / "extraction.js").is_file())
            extraction = json.loads((out / "extraction-status.json").read_text())
            self.assertEqual(extraction["schema_version"], "1.0.0")
            self.assertEqual(extraction["batch_id"], "OPS-EXTRACT-R01-20261114")
            self.assertEqual(extraction["source_counts"]["workbooks"], 7)
            self.assertEqual(extraction["public_counts"]["projects"], 1)
            self.assertEqual(extraction["public_counts"]["reviewed_notices"], 0)
            self.assertEqual(extraction["public_counts"]["unverified_work_reports"], 1)
            self.assertEqual(extraction["provider_collection"]["slack"], "NO_DIRECT_COLLECTOR")
            self.assertNotIn("Private rate", (out / "extraction-status.json").read_text())
            closed = json.loads((out / "closed-work.json").read_text())
            self.assertEqual(closed["kind"], "SOURCE_REVIEWED_CLOSED_WORK")
            self.assertEqual(closed["total"], 0)
            self.assertEqual(closed["records"], [])
            self.assertTrue(closed["closure_contract"]["private_reviewer_reason_evidence_excluded"])
            self.assertTrue((out / "closed-work.html").is_file())
            self.assertTrue((out / "closed-work.js").is_file())
            self.assertIn('href="./closed-work.html"', (out / "extraction.html").read_text())
            self.assertNotIn('href="./closed-work.html"', ops_html.split('<nav class="desktop-nav compact-nav"')[1].split('</nav>')[0])

            self.assertIn('class="desktop-nav compact-nav"', ops_html)
            self.assertIn('class="desktop-nav compact-nav"', sources)
            self.assertIn('class="desktop-nav compact-nav"', report)
            self.assertNotIn('class="phone-menu"', ops_html)
            self.assertNotIn('class="phone-menu"', sources)
            self.assertNotIn('class="phone-menu"', report)
            self.assertIn('href="./extraction.html"', ops_html)
            self.assertIn('id="updates-project"', (out / "extraction.html").read_text())
            self.assertIn('id="updates-meaning"', (out / "extraction.html").read_text())
            self.assertNotIn('class="extract-lane"', (out / "extraction.html").read_text())
            updates_raw = (out / "site-updates.json").read_text()
            updates = json.loads(updates_raw)
            self.assertEqual(updates["kind"], "DERIVED_PUBLIC_SITE_INTERPRETATION")
            self.assertEqual(updates["summary"]["public_site_count"], len(data["projects"]))
            self.assertEqual(updates["summary"]["reviewed_notice_count"], len(data["notices"]))
            self.assertEqual(updates["summary"]["published_work_report_count"], len(data["progress"]))
            self.assertEqual(updates["summary"]["unverified_work_report_count"], 1)
            self.assertEqual(len(updates["site_summaries"]), 1)
            self.assertEqual(updates["site_summaries"][0]["unverified_report_count"], 1)
            self.assertFalse(updates["interpretation"]["new_provider_ingestion"])
            self.assertNotIn("Private rate", updates_raw)
            self.assertNotIn("Private name", updates_raw)
            self.assertNotIn("ORG-000002", updates_raw)

            # Legacy anchors are preserved by a client-side same-site redirect.
            self.assertIn('location.hash === "#progress"', (out / "app.js").read_text())
            self.assertIn('location.hash === "#sources"', (out / "app.js").read_text())
            self.assertIn("../progress.html", (out / "site-operations/history.html").read_text())

            app = (out / "app.js").read_text()
            self.assertIn("demand not connected", app)
            self.assertIn("remaining-task backlog", app)
            self.assertFalse((out / "document-packets.json").exists())
            self.assertFalse((out / "ops/data/current-works.json").exists())



    def test_reviewed_closure_requires_provenance_and_never_leaks_private_details(self):
        base = {
            "closure_decision": "COMPLETED",
            "closure_approved": "TRUE",
            "closure_date": "2026-11-14",
            "closure_reason": "PRIVATE_REASON",
            "closure_reviewer": "PRIVATE_REVIEWER",
            "closure_evidence": "PRIVATE_EVIDENCE",
            "superseded_by": ""
        }
        self.assertEqual(reviewed_closure(base, "W-001")["decision"], "COMPLETED")
        self.assertIsNone(reviewed_closure({**base, "closure_approved": "FALSE"}, "W-001"))
        self.assertIsNone(reviewed_closure({**base, "closure_decision": ""}, "W-001"))
        with self.assertRaises(ValueError):
            reviewed_closure({**base, "closure_evidence": ""}, "W-001")
        with self.assertRaises(ValueError):
            reviewed_closure({**base, "closure_date": "not-a-date"}, "W-001")
        with self.assertRaises(ValueError):
            reviewed_closure({**base, "closure_decision": "SUPERSEDED"}, "W-001")

        tables = {
            "projects": [
                ["Project ID", "Is Public", "Display Name", "Data Quality Status",
                 "Executing Company ID", "Latitude", "Longitude", "Status",
                 "Location Ward Number", "Legacy Project Code"],
                ["PRJ-000001", True, "Approved location", "VALID", "ORG-000001",
                 "28.20", "83.98", "Construction", "14", "P001"],
            ],
            "choices": [
                ["Publication Setting ID", "Project ID", "Show Project Name",
                 "Show Coordinates", "Show Ward Number", "Show Status"],
                ["PPS-001", "PRJ-000001", True, True, True, True],
            ],
            "messages": [["Source ID"]],
            "notices": [["Notification ID", "Project ID"]],
            "progress": [
                ["Project Work ID", "Project ID", "Is Public", "Description Override",
                 "Last Updated", "Work Status", "Verification Status", "Closure Decision",
                 "Closure Approved", "Closure Date", "Closure Reason", "Closure Reviewer",
                 "Closure Evidence", "Superseded By", "Rate NPR"],
                ["W-01", "PRJ-000001", True, "Reviewed finished works", "2026-11-13",
                 "COMPLETED", "VERIFIED", "COMPLETED", "TRUE", "2026-11-14",
                 "PRIVATE_REASON", "PRIVATE_REVIEWER", "PRIVATE_EVIDENCE", "", "PRIVATE_RATE"],
                ["W-02", "PRJ-000001", True, "Discarded work plan", "2026-11-13",
                 "NOT_REQUIRED", "UNVERIFIED", "NOT_REQUIRED", "TRUE", "2026-11-14",
                 "Out of scope", "PRIVATE_REVIEWER", "", "", "PRIVATE_RATE"],
                ["W-03", "PRJ-000001", True, "Unreviewed closure proposal", "2026-11-13",
                 "IN_PROGRESS", "UNVERIFIED", "NOT_REQUIRED", "FALSE", "2026-11-14",
                 "PRIVATE_REASON", "PRIVATE_REVIEWER", "", "", "PRIVATE_RATE"]
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            self.assertEqual(build(tables, out, "fixture-readback"), (1, 0, 1))
            archived = json.loads((out / "closed-work.json").read_text())
            active = json.loads((out / "operations.json").read_text())
            self.assertEqual(archived["total"], 2)
            self.assertEqual({r["decision"] for r in archived["records"]},
                             {"COMPLETED", "NOT_REQUIRED"})
            self.assertEqual({r["id"] for r in archived["records"]}, {"W-01", "W-02"})
            self.assertEqual([r["id"] for r in active["progress"]], ["W-03"])
            self.assertEqual(len(active["projects"]), 1)
            raw = (out / "closed-work.json").read_text()
            for secret in ("PRIVATE_REASON", "PRIVATE_REVIEWER", "PRIVATE_EVIDENCE", "PRIVATE_RATE"):
                self.assertNotIn(secret, raw)
            updates = json.loads((out / "site-updates.json").read_text())
            self.assertEqual(updates["summary"]["published_work_report_count"], 1)

        # Work marked completed without an independent verified status
        # must never be silently archived.
        tables["progress"][1][6] = "UNVERIFIED"
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "requires separate VERIFIED"):
                build(tables, Path(temp), "fixture-readback")

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
            updates_raw = (out / "site-updates.json").read_text()
            self.assertIn("PRJ-999998", updates_raw)
            self.assertNotIn("PRJ-999999", updates_raw)
            self.assertNotIn("SECRET RETIRED ALIAS", updates_raw)
            self.assertNotIn("PRIVATE_SOURCE_TOKEN", updates_raw)


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
            site_updates = (out/"site-updates.json").read_text()
            self.assertNotIn("SECRET_STATUS_DO_NOT_PUBLISH",site_updates)
            self.assertNotIn("PRJ-990003",site_updates)
            self.assertEqual(len(rows),2)


if __name__ == "__main__":
    unittest.main()
