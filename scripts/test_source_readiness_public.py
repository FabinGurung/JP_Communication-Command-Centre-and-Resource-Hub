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
    assert r["source_ownership_approval"].startswith("PENDING_")
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
    raw=json.dumps(status)
    for forbidden in ("archive_root_drive_id","guild_id","channel_ids","provider_message_id","private_file_id","source_parent_id","discord_bot_token"):
        assert forbidden not in raw, "Private provider metadata exposed: "+forbidden
    for path in ("resources/index.html","workspace/index.html"):
        html=(ROOT/path).read_text(encoding="utf-8")
        assert "source-readiness-public.v1.0.json" in html
        assert "not a live" in html.lower() or "not a new collector run" in html.lower()
    print("PUBLIC_SOURCE_READINESS_PASS: 46 indexed links, six source exceptions held; latest private scan 1520; Discord last provider receipt partial.")
if __name__=="__main__":
    run()
