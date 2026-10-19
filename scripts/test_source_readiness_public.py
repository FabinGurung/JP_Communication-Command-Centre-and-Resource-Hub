#!/usr/bin/env python3
"""Fail closed on stale/misleading public source-readiness projections."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def run():
    status=read("ops/data/source-readiness-public.v1.0.json")
    inv=read("ops/control/req07-20261015-live-connected-drive-readback.v1.0.json")
    owners=read("ops/control/req07-20261015-incremental-and-provenance-control.v1.0.json")
    resources=read("ops/data/resource-catalog-normalized.v0.1.json")
    cycle=read("ops/control/daily-communication-web-cycle.json")
    assert status["kind"]=="PUBLIC_SAFE_SOURCE_READINESS_SNAPSHOT"
    assert status["scope"]=="GOVERNED_READ_ONLY_PROJECTION_NOT_LIVE_PROVIDER_COLLECTION"
    r=status["resources"]
    assert r["inventory_date_npt"]==inv["date_npt"]
    assert r["private_metadata_records"]==inv["current"]["rows"]
    assert r["folders_reviewed"]==inv["current"]["scanned_source_folders"]
    assert r["registered_project_roots"]==inv["current"]["project_roots"]
    assert r["existing_public_resource_links"]==owners["currently_published_resources"]==inv["immutability"]["public_catalog_total"]
    assert sum(len(site["files"]) for site in resources["sites"])==r["existing_public_resource_links"]
    assert r["existing_reference_metadata_accessible"]==r["source_root_exceptions"]["count"]==inv["external_source_exceptions"]["count"]
    assert r["new_public_links_admitted"]==inv["delta"]["new_public_admissions"]==0
    assert sum(r["source_root_exceptions"][x] for x in ("P001","P002"))==6
    assert r["file_specific_engineer_acceptance"]=="NOT_CERTIFIED"
    assert r["source_ownership_approval"]=="PROJECT_SOURCE_ASSOCIATION_USER_CONFIRMED__INDEPENDENT_ENGINEER_ISSUE_PENDING"
    assert r["full_provider_cursor_exhaustion"]=="NOT_CERTIFIED"
    assert r["original_drive_files_modified"]==0
    discord=next(p for p in cycle["source_providers"] if p["provider"]=="DISCORD")
    receipt=discord["last_frozen_run"]
    c=status["communication"]
    assert c["last_provider_receipt_date_npt"]==receipt["run_id"][:4]+"-"+receipt["run_id"][4:6]+"-"+receipt["run_id"][6:8]
    assert c["last_receipt_status"]==receipt["status"]=="PARTIAL"
    assert c["messages_new_or_changed"]==receipt["messages_new_or_changed"]
    assert c["media_fidelity_mismatches"]==receipt["attachments_failed"]
    assert c["new_authenticated_collector_run_certified"] is False
    assert c["scoped_full_history_v2_live_execution"]=="NOT_VERIFIED"

    review=read("ops/data/resource-review-dispositions-public.v1.0.json")
    pending=read("ops/data/pending-works.json")
    assert review["kind"]=="PUBLIC_SAFE_EXISTING_RESOURCE_DISPOSITIONS"
    assert review["totals"]=={"reviewed":6,"folders":1,"drawings":5,"engineer_approved":0,"existing_catalog_links_preserved":46,"project_associations_user_confirmed":6}
    assert len(review["items"])==len({x["resource_id"] for x in review["items"]})==6
    assert all(i["project_association"]=="USER_CONFIRMED_SCOPED_20261019" for i in review["items"])
    assert status["resources"]["file_specific_review"]["project_associations_user_confirmed"]==6
    assert status["resources"]["file_specific_review"]["engineer_issued_for_construction"]==0
    assert status["resources"]["file_specific_review"]["titleblock_person_identity_equivalence_asserted"] is False
    fkeys={f["resource_id"] for site in resources["sites"] for f in site["files"]}
    assert all(i["resource_id"] in fkeys and i["engineering_use"]!="APPROVED_FOR_CONSTRUCTION" for i in review["items"])
    assert set((i["project_id"] for i in review["items"]))=={"P001","P002"}
    assert status["resources"]["file_specific_review"]["reviewed_references"]==6
    assert status["resources"]["file_specific_review"]["engineer_issued_for_construction"]==0
    assert status["communication"]["collector_operational_mode"]=="ON_HOLD_BY_USER"
    assert status["communication"]["user_resume_required"] is True
    assert discord["status"]=="ON_HOLD_BY_USER_20261019"
    assert discord["execution_hold"]["run_discord_apis"] is False
    p4=next(x for x in pending["items"] if x["pending_id"]=="OPS-PEND-000004")
    assert p4["status"]=="ON_HOLD_USER_REQUEST_20261019"
    assert p4["hold"]["resume_condition"]=="NEW_EXPLICIT_USER_INSTRUCTION_TO_RESUME"
    assert "resource-review-dispositions-public.v1.0.json" in (ROOT/"resources/index.html").read_text()
    assert status["communication"]["collector_operational_mode"]=="ON_HOLD_BY_USER"
    assert "source-readiness-public.v1.0.json" not in (ROOT/"workspace/index.html").read_text()
    for banned in ("1gfhTtWBinNvF0F6vjQnzxsSZW8grB8ID","1pvCubGYJvfHOrNG1ynoxBrWFafZuooC6","1TzUCNxZ3WExD7H0mWYJ42KHsx11-A7BG"):
        assert banned not in json.dumps(review)
    raw=json.dumps(status)
    for forbidden in ("archive_root_drive_id","guild_id","channel_ids","provider_message_id","private_file_id","source_parent_id","discord_bot_token"):
        assert forbidden not in raw, "Private provider metadata exposed: "+forbidden
    resource_page=(ROOT/"resources/index.html").read_text(encoding="utf-8")
    developer_page=(ROOT/"workspace/index.html").read_text(encoding="utf-8")
    assert "source-readiness-public.v1.0.json" in resource_page
    assert "not a live" in resource_page.lower()
    assert "c-web11-post-alias-roadmap.v1.0.json" in developer_page
    assert "source-readiness-public.v1.0.json" not in developer_page
    assert "not a live" in developer_page.lower()
    print("PUBLIC_SOURCE_READINESS_PASS: 46 indexed links, six project-linked source exceptions operationally tracked; platform software remains independent; Discord paused.")
if __name__=="__main__":
    run()
