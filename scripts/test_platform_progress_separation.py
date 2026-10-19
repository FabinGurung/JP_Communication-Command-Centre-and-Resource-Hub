#!/usr/bin/env python3
"""Verify platform work and field-project issues have different owners and views."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    return (ROOT/path).read_text(encoding="utf-8")
def load(path):
    return json.loads(read(path))
def verify():
    roadmap=load("ops/control/c-web11-post-alias-roadmap.v1.0.json")
    original=load("ops/control/website-eight-request-roadmap.v0.1.json")
    developer=load("workspace/developer-software-backlog.v0.1.json")
    project=load("ops/data/project-document-review-public.v1.0.json")
    review=load("ops/data/resource-review-dispositions-public.v1.0.json")
    current=load("ops/data/current-works.json")
    pending=load("ops/data/pending-works.json")
    discord=load("ops/control/daily-communication-web-cycle.json")
    assert roadmap["goal"]=="BUILD_AND_VALIDATE_REPRODUCIBLE_SOFTWARE_PLATFORM_NOT_CERTIFY_CONSTRUCTION_PROJECTS"
    assert roadmap["platform_health"]["software_release_blocked_by_project_approval"] is False
    assert roadmap["platform_health"]["continuous_backend_service"]=="NONE"
    assert roadmap["platform_health"]["live_postgres_service"]=="NOT_DEPLOYED"
    software={r["key"] for r in roadmap["now_open"]}
    projects={r["key"] for r in roadmap["project_progress_tracked"]}
    moved={"ENGINEERING_DRAWING_ISSUES","P002_ARCHIVE_PRESERVATION","P007_ENGINEERING_SOURCE_CERTIFICATION","ENGINEER_TRADE_REPORTS"}
    assert moved<=projects and not (moved & software)
    assert all(x["software_release_blocker"] is False for x in roadmap["project_progress_tracked"])
    assert all(x["blocker_type"]=="SOFTWARE_OR_INTEGRATION_ONLY" for x in roadmap["now_open"])
    assert project["kind"]=="PUBLIC_SAFE_PROJECT_DOCUMENT_PROGRESS"
    assert project["software_release_blocker"] is False and project["raw_provider_content_included"] is False
    assert project["historical_progress_stream_changed"] is False
    cases=project["records"]
    assert len(cases)==3 and {c["project_id"] for c in cases}=={"P001","P002","P007"}
    assert len({c["record_id"] for c in cases})==3
    siteids={p["project_id"] for p in current["projects"]}
    assert set(c["project_id"] for c in cases)<=siteids
    assert all(c["issuer_confirmation"] is False and c["verification_state"]=="OPEN_PROJECT_RECORD_NOT_SOFTWARE_BLOCKER" for c in cases)
    joined={r["resource_id"]:r for r in review["items"]}
    assert sum(len(c["drawing_resource_ids"]) for c in cases)==project["drawings_count"]==5
    for case in cases:
        assert all(joined[rid]["project_id"]==case["project_id"] and joined[rid]["engineering_use"]=="NOT_APPROVED_FOR_CONSTRUCTION" for rid in case["drawing_resource_ids"])
    assert review["totals"]["engineer_approved"]==0
    historical=[x for x in read("ops/data/progress-report-public.v0.2.jsonl").splitlines() if x.strip()]
    assert len(historical)==37,"Frozen historical observations were changed"
    progress_page=read("site-operations/history.html")
    assert "progress-report-public.v0.2.jsonl" in progress_page
    assert "project-document-status.js" in progress_page and 'id="doc-status-rows"' in progress_page
    assert "project-document-review-public.v1.0.json" in read("assets/js/project-document-status.js")
    assert "source-readiness-public.v1.0.json" not in read("workspace/index.html")
    assert "engineer responses are operational data" in read("workspace/index.html")
    assert developer["scope"]=="WEBSITE_AND_SYSTEM_SOFTWARE_DEVELOPMENT_ONLY"
    assert set(developer["excluded_registry_ids"])=={"OPS-PEND-000004","OPS-PEND-000005","OPS-PEND-000006","OPS-PEND-000009"}
    plan={x["id"]:x for x in original["completion_order"]}
    for t in developer["items"]:
        if t["software_task_id"].startswith("JP-AEC-REQ-"):
            p=int(t["software_task_id"][-2:])
            assert t["status"]==t["source_status"]==plan[p]["status"]
    assert plan[7]["project_decisions_not_software_milestones"] is True
    hold=next(x for x in pending["items"] if x["pending_id"]=="OPS-PEND-000004")
    provider=next(x for x in discord["source_providers"] if x["provider"]=="DISCORD")
    assert hold["status"]=="ON_HOLD_USER_REQUEST_20261019"
    assert provider["execution_hold"]["run_discord_apis"] is False
    print("PLATFORM_PROGRESS_SCOPE_PASS: 2 project reviews/5 drawing states in Progress; 37 frozen historical records; software roadmap free of engineer-release gates; Discord remains on hold.")
if __name__=="__main__":
    verify()
