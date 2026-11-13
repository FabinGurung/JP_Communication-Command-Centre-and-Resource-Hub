#!/usr/bin/env python3
"""Synthetic, public-safe mobile/desktop QA fixture. Never reads private Sheets."""
from pathlib import Path
import sys
from publish_operations import build, SOURCES

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



out = Path(sys.argv[1] if len(sys.argv) > 1 else "_status_preview")
projects = [
    ["Project ID", "Is Public", "Display Name", "Data Quality Status",
     "Executing Company ID", "Latitude", "Longitude", "Status", "Location Ward Number",
     "Legacy Project Code", "Last Updated"]
]
choices = [
    ["Publication Setting ID", "Project ID", "Show Project Name", "Show Coordinates",
     "Show Ward Number", "Show Status"]
]
scenarios = [
    ("PRJ-999901", "Construction", True, True, "Demo construction"),
    ("PRJ-999902", "Completed", True, True, "Demo completed"),
    ("PRJ-999903", "Approval", True, True, "Demo approval"),
    ("PRJ-999904", "Maintenance", True, True, "Demo maintenance"),
    ("PRJ-999905", "HIDDEN_RAW_STATUS_DO_NOT_PUBLISH", True, False, "Demo status hidden"),
    ("PRJ-999906", "Completed", False, True, "PRIVATE DEMO MUST NEVER PUBLISH"),
]
for i, (pid, status, is_public, show_status, name) in enumerate(scenarios):
    projects.append([pid, is_public, name, "VALID", "ORG-000001",
                     28.20 + i * .004, 83.98 + i * .004, status, str(i + 1), "", "2026-11-12"])
    choices.append(["PPS-QA-" + str(i), pid, True, True, True, show_status])

tables = {
    "projects": projects,
    "choices": choices,
    "messages": [["Source ID"]],
    "notices": [["Notification ID", "Project ID"]],
    "progress": [
        ["Project Work ID", "Project ID", "Is Public", "Description Override",
         "Last Updated", "Work Status", "Verification Status"],
        ["PWI-QA-001", "PRJ-999901", True, "Synthetic work report", "2026-11-12",
         "IN_PROGRESS", "UNVERIFIED"],
    ]
}
assert build(add_live_source_fixtures(tables), out, "Synthetic QA — not a source read") == (5, 0, 1)
# Additional synthetic notices exercise site/category UX. These do not originate
# from providers and must never be used outside the test-only preview output.
import json
output = out / "operations.json"
preview = json.loads(output.read_text(encoding="utf-8"))
preview["notices"] = [
    {"notification_id":"QAN-001","project_id":"PRJ-999901","category":"Work",
     "instruction":"Synthetic worksite safety instruction","due_date":"2026-11-15",
     "display_order":1,"date":"2026-11-12"},
    {"notification_id":"QAN-002","project_id":"PRJ-999901","category":"Supervision",
     "instruction":"Synthetic site-supervision note","due_date":"",
     "display_order":2,"date":"2026-11-11"},
    {"notification_id":"QAN-003","project_id":"PRJ-999903","category":"Materials",
     "instruction":"Synthetic materials instruction","due_date":"",
     "display_order":1,"date":"2026-11-12"},
]
output.write_text(json.dumps(preview), encoding="utf-8")
body = (out / "operations.json").read_text(encoding="utf-8")
assert "HIDDEN_RAW_STATUS_DO_NOT_PUBLISH" not in body
assert "PRIVATE DEMO MUST NEVER PUBLISH" not in body
assert '"status": ""' in body
print("STATUS_FIXTURE_PASS: five synthetic public projects, hidden status never leaks")
