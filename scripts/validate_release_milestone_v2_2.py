#!/usr/bin/env python3
"""Fail-closed v2.2.0 exact-source release housekeeping and source-boundary validator."""
from pathlib import Path
import subprocess
import json
ROOT=Path(__file__).resolve().parents[1]
IMPL="599e487c6dceb52d620405f085c48912260d4755"
def read(p): return (ROOT/p).read_text(encoding="utf-8")
def data(p): return json.loads(read(p))
def verify():
    p=data("ops/control/milestone-v2.2.0.json")
    arc=data("ops/control/botanical-workspace-arc.v1.0.json")
    progress=data("ops/data/project-document-review-public.v1.0.json")
    pending=data("ops/data/pending-works.json")
    cycle=data("ops/control/daily-communication-web-cycle.json")
    assert read("VERSION").strip()=="2.2.0" and p["version"]=="2.2.0"
    assert p["tag"]=="v2.2.0" and p["implementation_sha"]==IMPL
    assert p["previous_release_tag"]=="v2.1.0"
    assert p["previous_release_peeled_sha"]=="d2963c2380c359dff3ea2f23f4a702c6074cb642"
    assert p["release_state"]=="AWAITING_SUCCESSFUL_MAIN_DEPLOY_AND_SAME_COMMIT_VISUAL_BRANCH_QA"
    assert arc["arc_id"]=="JP-AEC-BOTANICAL-WORKSPACE-20261020"
    assert arc["baseline_commit"]==p["previous_release_peeled_sha"]
    assert len(arc["active_pages"])==20
    assert p["evidence"]["responsive_route_viewport_count"]==160
    assert p["evidence"]["active_routes"]==20 and len(p["evidence"]["viewport_widths"])==8
    assert "v2.2.0" in read("README.md") and "v2.2.0" in read("CHANGELOG.md")
    assert "Botanical" in read("docs/releases/v2.2.0.md")
    assert progress["software_release_blocker"] is False and len(progress["records"])==3
    assert next(x for x in pending["items"] if x["pending_id"]=="OPS-PEND-000004")["status"]=="ON_HOLD_USER_REQUEST_20261019"
    assert next(x for x in cycle["source_providers"] if x["provider"]=="DISCORD")["execution_hold"]["run_discord_apis"] is False
    assert len([v for v in read("ops/data/progress-report-public.v0.2.jsonl").splitlines() if v.strip()])==37
    assert read("scripts/validate_release_milestone_v2_1.py").count('packet["version"]=="2.1.0"')==1
    release_wf=read(".github/workflows/release-v2.2.0.yml")
    assert "workflow_run:" in release_wf and "gh release create" in release_wf
    assert "TAG=v2.2.0" in release_wf and "refs/tags/$TAG" in release_wf
    assert "git merge-base --is-ancestor" in release_wf
    assert "Field Desk and Map visual QA" in release_wf
    assert "Validate branch and lane registry" in release_wf
    assert "contents: write" in release_wf
    assert "workflow_dispatch:" not in release_wf
    check=subprocess.run(["git","diff","--name-only",IMPL,"HEAD"],cwd=ROOT,text=True,capture_output=True)
    if check.returncode:
        raise AssertionError("Unable to compare release to implementation: "+check.stderr)
    changed={x for x in check.stdout.splitlines() if x}
    allowed=set(p["allowed_housekeeping_paths"])
    assert changed and changed<=allowed,"Release includes unrelated changes: "+repr(sorted(changed-allowed))
    assert set(("VERSION","README.md","CHANGELOG.md","docs/releases/v2.2.0.md"))<=changed
    for protected in arc["protected_records"]:
        assert protected["path"] not in changed,"Protected project data touched"
    print("BOTANICAL_RELEASE_V220_PASS: release-only diff, 20-page arc, preserved 2.1 baseline, Discord hold and exact-CI gates.")
if __name__=="__main__":
    verify()
