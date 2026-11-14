"""Project reviewed operations Sheets into a small, independent Pages artifact."""
import argparse
import csv
import json
import re
import shutil
from datetime import date
from pathlib import Path

from notification_projection import compile_notifications, records as notification_records
from sheets_read import ROOT, load_tables, records

SOURCES = {
    "projects": ("1JqzjBNBCT_AAIBkuGsIR5VBOJ3_HyifdPDc7K_jF5Bo", "projects"),
    "choices": ("1tDpsphzARq-rk1MExU4DXC8mG_clh-0TXJwRr2qljXU", "project_publication_settings"),
    "messages": ("1aWHzjEK0doiUcBbqhySiA6DWCp8d-aq2I08McslilAQ", "message_sources"),
    "notices": ("1ZPtTos8t9Cym_qnpiUhiyuTxndSc6sGzzv390ahAw4I", "site_notifications"),
    "progress": ("17YPRpaXIdHloH5-lzsjUpNvXLbsDfrIrlsn2jZ-7KKc", "project_work_items"),
    "organizations": ("1cwubE_4nB2SAEdLu6ry80G0HeNjbBdu4X3DA6jrcQ1E", "organizations"),
    "directory": ("17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4", "00_SOURCE_DIRECTORY"),
}
LIBRARY = "https://fabingurung.github.io/jp-field-desk-library/"
# Astam land-feasibility content now belongs to the Field & Desk Resource
# Library. Operations emits backward-compatible client redirects only.
ASTAM_LIBRARY = LIBRARY + "feasibility/"


def yes(value):
    return value.upper() == "TRUE"


def verify_directory(tables):
    """Fail closed if the live published directory no longer points to the owning Sheets.

    The directory is a pointer-only dependency, NEVER a public data master.
    No joined site data, payments, workforce, coordinates or source messages
    from its other 35 tabs are fetched or projected.
    """
    directory = {}
    for row in records(tables["directory"], "subject", "google_sheet", "data_or_view"):
        tab = row["data_or_view"]
        # Directory includes many other private/review-only sources. Ignore them.
        for key, (sheet_id, wanted_tab) in SOURCES.items():
            if key == "directory" or tab != wanted_tab:
                continue
            if key in directory:
                raise ValueError("Duplicate source directory mapping: " + key)
            uri = row["google_sheet"].split("/d/")
            if len(uri) != 2 or uri[1].split("/", 1)[0] != sheet_id:
                raise ValueError("Source directory ID mismatch: " + key)
            directory[key] = sheet_id
    expected = set(SOURCES) - {"directory"}
    if set(directory) != expected:
        raise ValueError("Source directory missing original sources: " + ",".join(sorted(expected - set(directory))))
    return directory


def public_organization_names(tables):
    """Only vetted public organization names from owning live Google Sheet."""
    labels = {}
    for row in records(tables["organizations"], "organization_id", "organization_name",
                       "is_public", "data_quality_status", "active"):
        if (yes(row["is_public"]) and yes(row["active"])
                and row["data_quality_status"] == "VALID"):
            labels[row["organization_id"]] = row["organization_name"]
    return labels


def build(tables, out, received_at):
    directory = verify_directory(tables)
    organization_names = public_organization_names(tables)
    # Live public identities come exclusively from the Projects and Locations
    # Sheet. Historical Git snapshots are archival comparisons, not inputs.
    project_record_dates = []
    choices = {}
    for row in records(tables["choices"], "publication_setting_id", "project_id",
                       "show_project_name", "show_coordinates", "show_ward_number", "show_status"):
        if row["project_id"] in choices:
            raise ValueError("Duplicate project display settings")
        choices[row["project_id"]] = row
    projects = {}
    for row in records(tables["projects"], "project_id", "is_public", "display_name",
                       "data_quality_status", "latitude", "longitude", "status", "location_ward_number",
                       "legacy_project_code"):
        if not yes(row["is_public"]) or row["data_quality_status"] == "RETIRED_ALIAS_ONLY":
            continue
        pid = row["project_id"]
        if not re.fullmatch(r"PRJ-[0-9]{6}", pid):
            raise ValueError("Invalid public project ID")
        setting = choices.get(pid)
        if not setting:
            continue
        project = {"id": pid, "name": row["display_name"] if yes(setting["show_project_name"]) else pid,
                   "status": row["status"] if yes(setting["show_status"]) else "",
                   "ward": row["location_ward_number"] if yes(setting["show_ward_number"]) else ""}
        if re.fullmatch(r"P[0-9]{3}", row["legacy_project_code"]):
            project["site"] = row["legacy_project_code"]
        # A public project identity can still carry unresolved quality warnings.
        # Do not imply that the project name, owner or works are certified.
        quality = row["data_quality_status"]
        if quality != "VALID":
            project["quality"] = quality or "UNVERIFIED"
        if row.get("last_updated"):
            date.fromisoformat(row["last_updated"])
            project_record_dates.append(row["last_updated"])
        organization_id = row.get("executing_company_id", "")
        if organization_id in organization_names:
            project.update(company_id=organization_id, company=organization_names[organization_id])
        if yes(setting["show_coordinates"]) and row["latitude"] and row["longitude"]:
            lat, lng = float(row["latitude"]), float(row["longitude"])
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                raise ValueError("Invalid map coordinates")
            project.update(lat=lat, lng=lng)
        projects[pid] = project
    # Filter by public project before joining. The version, digest and source
    # pointers in each reviewed instruction must match the original registry.
    source_rows = tables["messages"]
    sources = list(notification_records(source_rows, "source_id"))
    grants = {r["source_id"]: {"version": r["source_version"], "sha256": r["source_sha256"],
             "source_url": r["source_message"], "drive_source_url": r["saved_original"],
             "project_id": r["project_id"]} for r in sources}
    notice_rows = tables["notices"]
    project_column = notice_rows[0].index("Project ID")
    selected = [notice_rows[0], *(r for r in notice_rows[1:] if
                len(r) > project_column and r[project_column] in projects)]
    compiled = compile_notifications(source_rows, selected,
        {"admitted_sources": grants, "source_sheet_url": ""},
        project_ids=set(projects), mode="ACTIONS_SHEETS_REFRESH")
    source_dates = {s["source_id"]: s["date_npt"] for s in compiled["sources"]}
    notice_keys = ("notification_id", "project_id", "category", "instruction", "due_date", "display_order")
    notices = [{**{k: item[k] for k in notice_keys}, "date": source_dates[item["source_id"]]}
               for item in compiled["items"]]
    progress = []
    for row in records(tables["progress"], "project_work_id", "project_id", "is_public",
                       "description_override", "last_updated", "work_status", "verification_status"):
        if row["project_id"] not in projects or not yes(row["is_public"]):
            continue
        date.fromisoformat(row["last_updated"])
        progress.append({"id": row["project_work_id"], "project_id": row["project_id"],
            "work": row["description_override"], "status": row["work_status"],
            "date": row["last_updated"], "verification": row["verification_status"]})
    progress.sort(key=lambda r: (r["date"], r["id"]), reverse=True)
    notices.sort(key=lambda r: (r["date"], -r["display_order"]), reverse=True)
    out.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "app.js", "styles.css", "navigation.js", "owner-help.html", "memory-wall.html",
                 "progress.html", "progress.js", "sources.html", "sources.js",
                 "extraction.html", "extraction.js"):
        shutil.copyfile(ROOT / "publication/operations" / name, out / name)
    (out / ".nojekyll").touch()
    source_dates = {
        "projects": {
            "latest_public_record_date": max(project_record_dates, default=None),
            "date_field": "Projects and Locations / Last Updated",
            "meaning": "SOURCE_ROW_DATE_NOT_WORKBOOK_MODIFIED_TIME"
        },
        "notifications": {
            "latest_public_record_date": max((n["date"] for n in notices if n["date"]), default=None),
            "date_field": "Message Sources / Date NPT",
            "meaning": "REVIEWED_SOURCE_MESSAGE_DATE"
        },
        "progress": {
            "latest_public_record_date": progress[0]["date"] if progress else None,
            "date_field": "Project Work / Last Updated",
            "meaning": "REPORTED_WORK_ROW_DATE_NOT_CERTIFIED_COMPLETION"
        }
    }
    result = {
        "projects": list(projects.values()),
        "notices": notices,
        "progress": progress,
        "refreshed_at_npt": received_at,
        "identity": {
            "schema_version": "1.0.0",
            "current_authority": "LIVE_GOOGLE_SHEETS_APPROVED_PUBLIC_ROWS",
            "historical_git_index_role": "ARCHIVED_HISTORICAL_RELEASE_NOT_LIVE_INPUT",
            "historical_git_index_count": None,
            "public_project_count": len(projects),
            "public_ids_added_since_historical_index": [],
            "live_project_ids_from": "Projects and Locations / projects",
            "nonpublic_or_retired_rows_excluded": True,
        },
        "provenance": {
            "schema_version": "1.2.0",
            "kind": "PUBLIC_SAFE_READ_ONLY_SHEETS_PROJECTION",
            "source_readback_at_npt": received_at,
            "source_dates": source_dates,
            "provider_modified_at": None,
            "provider_modified_at_status": "NOT_AVAILABLE_WITH_CURRENT_SHEETS_READONLY_SCOPE",
            "latest_public_report_date": source_dates["progress"]["latest_public_record_date"],
            "source_families": ["Projects and Locations", "Website Display Choices",
                                "Notification Center - Message Sources",
                                "Notification Center - Instructions", "Project Work",
                                "Companies and Organizations", "Website Publishing and Source Directory"],
            "live_workbook_count": len(SOURCES),
            "organization_authority": "Companies and Organizations / organizations",
            "directory_role": "READ_ONLY_SOURCE_POINTER_VALIDATION",
            "directory_verified_inputs": sorted(directory),
            "source_authority": "GOOGLE_SHEETS",
            "direct_slack_collector": "NOT_CONNECTED_TO_THIS_PUBLISHER",
            "direct_discord_collector": "ON_HOLD",
            "engineering_completion": "NOT_CERTIFIED_BY_THIS_DASHBOARD"
        }
    }
    # A bounded public extraction receipt is a generated view only, never a
    # second editable master or a raw provider message archive.
    source_key_columns = {
        "projects": "project_id", "choices": "publication_setting_id",
        "messages": "source_id", "notices": "notification_id",
        "progress": "project_work_id", "organizations": "organization_id",
        "directory": "subject"
    }
    counts = {key: len(list(records(tables[key], source_key_columns[key])))
              for key in SOURCES}
    all_project_rows = list(records(tables["projects"], "project_id"))
    project_ids = {r["project_id"] for r in all_project_rows}
    organization_ids = {r["organization_id"] for r in records(tables["organizations"], "organization_id")}
    message_ids = {r["source_id"] for r in records(tables["messages"], "source_id")}
    foreign_key_warnings = (
        sum(r["project_id"] not in project_ids for r in records(tables["choices"], "publication_setting_id", "project_id"))
        + sum(r["project_id"] not in project_ids for r in records(tables["notices"], "notification_id", "project_id"))
        + sum(r["source_id"] not in message_ids for r in records(tables["notices"], "notification_id", "source_id"))
        + sum(r["project_id"] not in project_ids for r in records(tables["progress"], "project_work_id", "project_id"))
        + sum(bool(r["executing_company_id"]) and r["executing_company_id"] not in organization_ids
              for r in all_project_rows)
    )
    title_roles = {
        "projects": ("Projects and Locations", "Owner"),
        "choices": ("Website Display Choices", "Permissions"),
        "messages": ("Notification Message Sources", "Provenance"),
        "notices": ("Notification Instructions", "Review"),
        "progress": ("Project Work", "Field reports"),
        "organizations": ("Companies and Organizations", "Labels"),
        "directory": ("Website Publishing and Source Directory", "Pointer check"),
    }
    source_books = [{"key": key, "title": title_roles[key][0], "tab": tab,
                     "role": title_roles[key][1],
                     "url": "https://docs.google.com/spreadsheets/d/" + book + "/edit",
                     "row_count": counts[key]}
                    for key, (book, tab) in SOURCES.items()]
    status = {
        "schema_version": "1.0.0",
        "kind": "PUBLIC_AGGREGATE_SHEETS_EXTRACTION_RECEIPT",
        "batch_id": "OPS-B001",
        "checkpoint": "OPS-CP000001",
        "readback_at_npt": received_at,
        "source_books": source_books,
        "counts": counts,
        "source_dates": source_dates,
        "public_project_count": len(projects),
        "reviewed_notice_count": len(notices),
        "published_work_count": len(progress),
        "validation": {"directory_verified": True,
                       "foreign_key_warnings": foreign_key_warnings,
                       "keys_unique_per_registered_source": True,
                       "double_read": True,
                       "historical_work_is_not_certified": True},
        "lanes": {
            "01_messages": {"status": "SHEETS_PROVENANCE_ONLY", "rows": counts["messages"],
                            "slack_collector": "NOT_CONNECTED_TO_ACTIONS",
                            "discord_collector": "NOT_CONNECTED",
                            "telegram_collector": "NOT_CONNECTED"},
            "02_notifications": {"status": "REVIEWED_PUBLIC_ROWS", "rows": len(notices)},
            "03_work": {"status": "HISTORICAL_REPORTED_ROWS", "rows": len(progress)},
            "04_demands": {"status": "SOURCE_NOT_CONNECTED", "material": None,
                           "equipment": None, "manpower": None},
        },
        "stop_point": "Seven existing original source Sheets read and cross-referenced; no new provider messages ingested.",
        "next_batch": "One approved site channel, up to three messages, after evidence/permission verification and PRE snapshot."
    }
    (out / "extraction-status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "operations.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    for path, target in {
        "map.html": "./#map",
        "site-operations.html": "./#notifications",
        "site-operations/history.html": "../progress.html",
        "workspace.html": "./owner-help.html#workspace",
        "workspace/index.html": "../owner-help.html#workspace",
        "guide/index.html": "../owner-help.html#guide",
        "guide/3-pages/index.html": "../../owner-help.html#guide",
        "guide/7-pages/index.html": "../../owner-help.html#guide",
        "guide/15-pages/index.html": "../../owner-help.html#guide",
        "resources/index.html": LIBRARY,
        "resources/project-documents.html": LIBRARY + "resources/project-documents.html",
        "feasibility/index.html": ASTAM_LIBRARY,
        "feasibility/buyer-guide/index.html": ASTAM_LIBRARY + "buyer-guide/",
    }.items():
        file = out / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(
            f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Continue</title>'
            f'<p><a href="{target}">Continue to the current page</a></p>'
            f'<script>const u = new URL({json.dumps(target)}, location.href);'
            'u.search = location.search; location.replace(u);</script></html>', encoding="utf-8")
    return len(projects), len(notices), len(progress)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args()
    tables, stamp = load_tables(SOURCES, args.fixture)
    print("Projects, notifications and progress:", *build(tables, args.output, stamp))
