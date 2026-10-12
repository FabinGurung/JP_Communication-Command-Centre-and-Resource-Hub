#!/usr/bin/env python3
"""Request 06: fail-closed Git/Pages data-owner lane and publication validator.

Uses Git and public-safe repository metadata only; never invokes private providers.
All original Discord/Slack bytes and Drive permissions remain outside this repo.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
GATE="ops/control/progress-publication-gate.v0.1.json"
REPORT="ops/data/progress-report-public.v0.2.jsonl"
STAGE="ops/control/communication-extract-staging.v0.1.json"
DRIVE="ops/control/req06-drive-folder-readback.v0.1.json"
SHA=re.compile(r"^[a-f0-9]{64}$")
ALLOWED_KIND={"FIELD_REPORTED_OBSERVATION","PREVIOUS_UI_DAILY_ROUTINE_TEMPLATE","SOURCE_LINKED_PENDING_COMMUNICATION"}
BLOCKED_BINARY={".db",".sqlite",".sqlite3",".parquet",".jpg",".jpeg",".png",".mp4",".zip",".7z"}

class GateError(ValueError):
    pass

def require(test,message):
    if not test: raise GateError(message)

def read_json(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def git(*args):
    return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()

def owned_data_lanes(path):
    p=path.strip("/")
    out=set()
    if p in {REPORT,"ops/data/progress-history-public.v0.1.jsonl"}:out.add("progress")
    if p in {"ops/data/resource-catalog-normalized.v0.1.json","ops/data/project-resources.json"} or p.startswith("ops/data/resource-original-names/"):out.add("resources")
    if p=="site-operations.html" or p.startswith("ops/data/site-daily-checklist"):out.add("checklist")
    if p=="ops/data/current-works.json":out.add("daily_operations")
    if p=="projects.csv":out.add("project_master")
    if p.startswith("ops/discord/") or p.startswith("ops/data/communication-web-daily/"):out.add("provider_capture")
    return out

def changed_files():
    override=os.getenv("JP_AEC_CHANGED_PATHS")
    if override is not None:
        return [x for x in override.splitlines() if x.strip()]
    after=os.getenv("GITHUB_SHA") or git("rev-parse","HEAD")
    before=os.getenv("GITHUB_EVENT_BEFORE","")
    if os.getenv("GITHUB_EVENT_NAME")=="pull_request" and os.getenv("GITHUB_BASE_REF"):
        base=git("merge-base",after,"origin/"+os.environ["GITHUB_BASE_REF"])
    elif re.fullmatch(r"[a-f0-9]{40}",before) and set(before)!={"0"}:
        base=before
    else:
        base=git("rev-parse",after+"^")
    return [x for x in git("diff","--name-only","--no-renames",base,after).splitlines() if x]

def audit_change_lanes(paths):
    data_lanes=set()
    for path in paths:
        normalized=path.replace("\\","/")
        require(not normalized.startswith("/") and ".." not in Path(normalized).parts,"unsafe changed path")
        data_lanes.update(owned_data_lanes(normalized))
        if normalized.startswith(("ops/data/","ops/evidence/","ops/discord/")):
            require(not (Path(normalized).suffix.lower() in BLOCKED_BINARY),
                    "binary/private provider content cannot be committed: "+normalized)
            require("RAW_JSONL/" not in normalized.upper() and "ATTACHMENT_BYTES/" not in normalized.upper(),
                    "provider original storage lane leaked into public repo: "+normalized)
    require(len(data_lanes)<=1,"independent source-data lanes changed together: "+", ".join(sorted(data_lanes)))
    if "progress" in data_lanes:
        require(not any(p in {"resources/index.html","site-operations.html",
                              "workspace/index.html","projects.csv"} for p in paths),
                "progress publication attempted to edit checklist, resources, workspace or project master")
    if "resources" in data_lanes:
        require(not any(p in {"site-operations/history.html","site-operations.html",
                              "map.html"} for p in paths),
                "resource librarian attempted to modify progress, checklist or map")
    if "provider_capture" in data_lanes:
        require(not any(p in {REPORT,"site-operations/history.html","resources/index.html",
                              "site-operations.html"} for p in paths),
                "provider capture may not write public publication or project-facing pages")
    return data_lanes

def audit_drive_routes():
    stage=read_json(STAGE); snap=read_json(DRIVE)
    require(stage["status"].startswith("FOLDERS_VERIFIED"),"unexpected private staging state")
    require(snap["status"]=="FOLDER_METADATA_READBACK_ONLY","Drive snapshot implies unverified ingestion")
    require(snap["staging_root_id"]==stage["staging_root"]["id"],"staging root identity changed")
    expected={x["name"]:x["drive_id"] for x in stage["categories"]}
    actual={x["name"]:x["drive_id"] for x in snap["verified_folders"]}
    require(len(expected)==10 and actual==expected,"Drive folder names/IDs do not match metadata readback")
    require(len(set(actual.values()))==10,"reused/duplicate Google Drive folder ID")
    require(all(x.get("parent_id")==snap["staging_root_id"] for x in snap["verified_folders"]),
            "Drive child folder does not resolve to registered staging root")
    require(snap["new_raw_provider_rows_certified"] is False,"raw provider ingestion falsely marked complete")
    require(snap["private_pointer_stage_populated"] is False,"future source pointer stage falsely marked populated")
    return len(actual)

def audit_report():
    contract=read_json(GATE)
    require(contract["status"]=="LEGACY_FROZEN_NEW_ROWS_DENIED_UNTIL_SOURCE_REVIEW","unexpected publication gate")
    base=contract["baseline"]
    require(base["path"]==REPORT and re.fullmatch("[0-9a-f]{40}",base["blob_sha"]),"unsafe baseline source")
    try:
        frozen=subprocess.check_output(["git","cat-file","blob",base["blob_sha"]],cwd=ROOT)
    except subprocess.CalledProcessError as err:
        raise GateError("Cannot retrieve original frozen public Git blob; full history checkout required") from err
    historical=[x for x in frozen.splitlines() if x.strip()]
    current=[x for x in (ROOT/REPORT).read_bytes().splitlines() if x.strip()]
    require(len(historical)==base["count"]==len(base["ids"]),"frozen legacy seed count mismatch")
    require(len(current)>=len(historical),"legacy public record was removed")
    require(current[:len(historical)]==historical,"legacy public row changed or reordered without supersession governance")
    ids=set()
    sites={x["project_id"] for x in read_json("ops/data/current-works.json")["projects"]}
    admitted={x["record_id"]:x for x in contract["admitted_new_records"]}
    require(len(admitted)==len(contract["admitted_new_records"]),"duplicate publication approvals")
    require(len({x["record_id"] for x in contract["admitted_new_records"]})==len(admitted),
            "duplicate review keys")
    for i,raw in enumerate(current):
        try:row=json.loads(raw)
        except (ValueError,UnicodeDecodeError) as e:raise GateError("invalid public progress JSONL row") from e
        rid=row.get("record_id")
        require(isinstance(rid,str) and rid and rid not in ids,"duplicate or missing progress identity")
        ids.add(rid)
        require(row.get("project_id") in sites,"unmatched project FK in public progress")
        require(row.get("record_kind") in ALLOWED_KIND,"unsupported progress evidence kind")
        require(row.get("engineer_accepted") is not True and row.get("quantity_verified") is not True,
                "unsupported engineer acceptance or verified construction quantity")
        text=row.get("text") or ""
        require(isinstance(text,str),"missing public text")
        require(not re.search(r"(?:cdn\.discordapp\.com\/attachments|discordapp\.net\/attachments|"
                              r"googleapis\.com\/drive\/v3\/files)",text,re.I),
                "raw/private attachment pointer present in public text")
        require(not any(k in row for k in ("provider_raw_payload","private_attachment_bytes",
                                             "user_access_token","raw_discord_message")),
                "private provider payload field leaked to published row")
        link=row.get("source_url") or ""
        if link:
            parts=urlsplit(link)
            require(parts.scheme=="https" and (parts.hostname or "").lower() in {
                "discord.com","www.discord.com","slack.com","app.slack.com","jp09.slack.com"
            },"public source link outside approved provider origins")
            require(not any(x in (parts.query or "").lower() for x in (
                "token=","signature=","x-amz-","auth=",
            )),"signed or credential-bearing provider URL blocked")
        if i<len(historical):
            require(rid==base["ids"][i],"legacy record ID/order changed")
            continue
        review=admitted.get(rid)
        require(review is not None,"new public record lacks documented review: "+rid)
        for field in contract["required_review_fields"]:
            require(field in review,"missing publication review field "+field)
        require(review["project_id"]==row["project_id"],"approval project FK differs from record")
        require(review["review_decision"]==contract["review_decision"] and
                review["reviewer_role"]==contract["reviewer_role"],
                "source review not admitted for public publication")
        require(all(review.get(k) is True for k in ("privacy_verified","project_fk_verified",
                  "provider_provenance_verified","media_excluded_or_verified")),
                "public record missing privacy, provenance or attachment gate")
        require(SHA.fullmatch(review.get("source_content_sha256","")),"source SHA256 missing")
        require(review["engineering_claim_limit"]==contract["claim_limit"],
                "source review improperly certifies engineering completion")
        require(bool(review.get("reviewed_at_utc")) and bool(review.get("source_receipt_ref")),
                "source review date or receipt missing")
        require(row["record_kind"] in {"FIELD_REPORTED_OBSERVATION",
                                      "SOURCE_LINKED_PENDING_COMMUNICATION"},
                "new publication cannot add historical template rows")
    require(set(admitted)==ids-set(base["ids"]),"review record set does not match new public rows")
    return len(historical),len(current)-len(historical)

def main():
    changed=changed_files()
    lanes=audit_change_lanes(changed)
    folders=audit_drive_routes()
    legacy,added=audit_report()
    print("PUBLICATION_LANE_PASS: "
          f"change_paths={len(changed)},data_owner_lanes={','.join(sorted(lanes)) or 'none'},"
          f"private_stage_folders={folders},historical_public_rows={legacy},"
          f"new_reviewed_rows={added},raw_provider_ingestion_not_asserted")

if __name__=="__main__":
    try: main()
    except (GateError,KeyError,TypeError) as error:
        raise SystemExit("PUBLICATION_LANE_FAIL: "+str(error))
