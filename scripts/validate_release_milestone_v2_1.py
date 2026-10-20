#!/usr/bin/env python3
"""Read-only, deterministic release v2.1.0 packet and source-boundary QA."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    return (ROOT/path).read_text(encoding="utf-8")
def load(path):
    return json.loads(read(path))
def main():
    version=read("VERSION").strip()
    packet=load("ops/control/milestone-v2.1.0.json")
    roadmap=load("ops/control/c-web11-post-alias-roadmap.v1.0.json")
    progress=load("ops/data/project-document-review-public.v1.0.json")
    pending=load("ops/data/pending-works.json")
    cycle=load("ops/control/daily-communication-web-cycle.json")
    aliases=load("ops/data/resource-project-name-aliases.v1.0.json")
    # The v2.1.0 packet/tag remain frozen; later platform releases have their own validators.
    assert version in ("2.1.0","2.2.0") and packet["version"]=="2.1.0"
    assert packet["tag"]=="v2.1.0" and packet["milestone_id"]=="JP-AEC-PLATFORM-v2.1.0"
    assert packet["source_baseline_commit"]==packet["rollback_pre_release_commit"]
    assert len(packet["source_baseline_commit"])==40
    assert packet["release_state"]=="AWAITING_MAIN_ACTIONS_SUCCESS_AND_IMMUTABLE_GIT_TAG"
    assert "v2.1.0" in read("README.md") and "v2.1.0" in read("CHANGELOG.md")
    notes=read("docs/releases/v2.1.0.md")
    assert "Project" in notes and "software" in notes and "rollback" in notes.lower()
    assert "live PostgreSQL" not in notes or "not" in notes
    assert len(aliases["rows"])==6
    assert progress["software_release_blocker"] is False
    assert len(progress["records"])==3
    assert len([x for x in read("ops/data/progress-report-public.v0.2.jsonl").splitlines() if x.strip()])==37
    assert roadmap["platform_health"]["software_release_blocked_by_project_approval"] is False
    assert roadmap["platform_health"]["live_postgres_service"]=="NOT_DEPLOYED"
    assert len(roadmap["now_open"])>=1
    assert next(x for x in pending["items"] if x["pending_id"]=="OPS-PEND-000004")["status"]=="ON_HOLD_USER_REQUEST_20261019"
    assert next(x for x in cycle["source_providers"] if x["provider"]=="DISCORD")["execution_hold"]["run_discord_apis"] is False
    wf=read(".github/workflows/release-v2.1.0.yml")
    for token in ("workflow_run:","Operations Hub production","permissions:","contents: write","Field Desk and Map visual QA","Validate branch and lane registry","git push origin","gh release create","refs/tags/v2.1.0"):
        if token=="refs/tags/v2.1.0":
            assert 'TAG=v2.1.0' in wf and 'refs/tags/$TAG' in wf
        else: assert token in wf, token
    assert "workflow_dispatch:" not in wf, "Release job must trigger only after production deploy."
    print("MILESTONE_V2_1_0_PASS: release packet, source boundaries, paused provider, backlog and release-job gating verified.")
if __name__=="__main__":
    main()
