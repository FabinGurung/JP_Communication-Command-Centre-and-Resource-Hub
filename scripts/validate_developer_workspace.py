#!/usr/bin/env python3
"""Fail-closed developer-only workspace and software-backlog projection QA.

This validates code/docs and pointers. Never reads private providers or writes
projects, checklists, daily progress, resource catalogues or Google Drive.
"""
from pathlib import Path
from urllib.parse import urlsplit
import json

ROOT=Path(__file__).resolve().parents[1]
def read(path): return (ROOT/path).read_text(encoding="utf-8")
def load(path): return json.loads(read(path))
def fail(text): raise SystemExit("DEVELOPER_SCOPE_FAIL: "+text)
def check(ok,text):
    if not ok: fail(text)

landing=read("workspace/index.html")
software=read("workspace/backlog/index.html")
registry=load("workspace/developer-links.v0.1.json")
backlog=load("workspace/developer-software-backlog.v0.1.json")
roadmap=load("ops/control/website-eight-request-roadmap.v0.1.json")
pending=load("ops/data/pending-works.json")
shell=read("assets/js/site-shell.js")
controls=read("controls/index.html")
check(registry.get("schema_version")=="0.2.0","developer registry schema changed")
check(registry.get("scope")=="WEBSITE_IMPLEMENTATION_NOT_PROJECT_CASE_FILES","developer link registry scope")
check(backlog.get("scope")=="WEBSITE_AND_SYSTEM_SOFTWARE_DEVELOPMENT_ONLY","software backlog scope")
check('id="developer-directory"' in landing and "developer-links.v0.1.json" in landing,"developer directory is not isolated")
check("workspace/backlog/" in shell and '["📌 Software Backlog","pending/"]' not in shell,"global developer menu still links mixed pending work")
check('href="../workspace/backlog/"' in controls and 'href="../pending/"' not in controls,"control tower page links mixed pending instead of software")
check("developer-software-backlog.v0.1.json" in software,"software page does not load curated developer data")
check("pending-works.json" not in software,"developer software page directly fetches mixed operations registry")
check("current-works.json" not in landing and "progress-report-public" not in landing,"developer landing loads project facts")
check("ops/data/current-works.json" not in software and "ops/data/progress-report" not in software,"software page loads project progress")
check("site-operations.html" not in registry.__str__(),"software registry contains field page")

forbidden=(
 "../pending/","../site-operations.html","../site-operations/",
 "../resources/","../map.html","../ops/data/current-works",
 "../ops/data/resource-catalog-normalized", "../ops/data/project-resources",
 "../ops/data/progress-report-public", "../ops/data/progress-history-public"
)
link_ids=set()
for group in registry["categories"]:
    check(group.get("id") and group["id"] not in link_ids,"duplicate developer category")
    link_ids.add(group["id"])
    check(group.get("name") and group.get("explanation") and group.get("links"),"developer category incomplete")
    for item in group["links"]:
        u=item.get("href","")
        check(item.get("label") and u,"incomplete developer source link")
        check(not any(u.startswith(f) for f in forbidden),"developer link points into field case files: "+u)
        if u.startswith("../"):
            resolved=(ROOT/"workspace"/u).resolve()
            check(resolved.is_relative_to(ROOT.resolve()),"developer link escapes repository")
            if resolved.is_dir(): resolved/= "index.html"
            check(resolved.is_file(),"developer link is broken: "+u)
        else:
            parsed=urlsplit(u)
            check(parsed.scheme=="https" and parsed.netloc=="github.com","external developer link not a GitHub source: "+u)

owned_pending={"OPS-PEND-000001","OPS-PEND-000002","OPS-PEND-000003","OPS-PEND-000007","OPS-PEND-000008"}
not_developer={"OPS-PEND-000004","OPS-PEND-000005","OPS-PEND-000006","OPS-PEND-000009"}
check(set(backlog["excluded_registry_ids"])==not_developer,"operational task exclusion boundary drifted")
seen=set()
known_pending={x["pending_id"]:x for x in pending["items"]}
road={x["id"]:x for x in roadmap["completion_order"]}
for item in backlog["items"]:
    task=item["software_task_id"]
    check(task not in seen,"duplicate software task "+task)
    seen.add(task)
    ref=item["source_ref"]
    path=ref["path"]
    if path=="ops/data/pending-works.json":
        check(task in owned_pending and task not in not_developer,"field execution task leaked to workspace: "+task)
        check(task==ref["record_id"] and task in known_pending,"missing original pending source ID")
        src=known_pending[task]
    elif path=="ops/control/website-eight-request-roadmap.v0.1.json":
        number=ref["record_id"]
        check(isinstance(number,int) and number in {5,6,7,8},"unexpected roadmap stage in software backlog")
        check(task==f"JP-AEC-REQ-{number:02d}" and number in road,"incorrect roadmap software FK")
        src=road[number]
    else:
        fail("unapproved backlog input source "+str(path))
    check(item["status"]==src["status"] and item["source_status"]==src["status"],
          "stale software backlog source status: "+task)
    check(item["title"] and item["purpose"] and item["category"],"unfinished software task definition: "+task)
    check(item["source_href"].startswith(
        "https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/blob/main/"
    ),"missing Git source pointer for "+task)

expect={f"JP-AEC-REQ-{i:02d}" for i in [5,6,7,8]}|owned_pending
check(seen==expect,"backlog omits or adds developer software source IDs")
check(len(backlog["items"])==9,"unexpected developer software backlog count")
print(f"DEVELOPER_SCOPE_PASS: {len(registry['categories'])} developer categories; "
      f"{sum(len(g['links']) for g in registry['categories'])} software source links; "
      f"{len(seen)} source-traced software tasks; {len(not_developer)} field/collector tasks excluded")
