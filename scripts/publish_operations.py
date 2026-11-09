"""Project reviewed operations Sheets into a small, independent Pages artifact."""
import argparse
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
}
LIBRARY = "https://fabingurung.github.io/JP_Field_and_Desk_Resource_Library/"
# Preserve the already-live Astam client route independently of the migrated catalogue.
LEGACY_CLIENT_FILES = (
    "feasibility/index.html",
    "feasibility/buyer-guide/index.html",
    "feasibility/buyer-guide/guide.json",
    "ops/data/land-feasibility/astam-buyer-guide-public.v1.0.json",
    "ops/data/land-feasibility/astam-village-public.v1.0.json",
    "assets/css/jp-theme-tokens.css",
    "assets/css/site-shell.css",
    "assets/css/jp-botanical.css",
    "assets/botanical/garden-left.svg",
    "assets/botanical/garden-right.svg",
    "assets/botanical/corner-sprig.svg",
    "assets/botanical/empty-garden.svg",
    "assets/botanical/tree-silhouette.svg",
)


def yes(value):
    return value.upper() == "TRUE"


def build(tables, out, received_at):
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
    for name in ("index.html", "app.js", "styles.css", "owner-help.html"):
        shutil.copyfile(ROOT / "publication/operations" / name, out / name)
    for name in LEGACY_CLIENT_FILES:
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    (out / ".nojekyll").touch()
    (out / "operations.json").write_text(json.dumps({"projects": list(projects.values()),
        "notices": notices, "progress": progress, "refreshed_at_npt": received_at},
        ensure_ascii=False), encoding="utf-8")
    for path, target in {
        "map.html": "./#map",
        "site-operations.html": "./#notifications",
        "site-operations/history.html": "../#progress",
        "workspace.html": "./owner-help.html#workspace",
        "workspace/index.html": "../owner-help.html#workspace",
        "guide/index.html": "../owner-help.html#guide",
        "guide/3-pages/index.html": "../../owner-help.html#guide",
        "guide/7-pages/index.html": "../../owner-help.html#guide",
        "guide/15-pages/index.html": "../../owner-help.html#guide",
        "resources/index.html": LIBRARY,
        "resources/project-documents.html": LIBRARY + "resources/project-documents.html",
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
