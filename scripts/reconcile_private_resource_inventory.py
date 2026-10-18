#!/usr/bin/env python3
"""REQ07 authenticated private Drive inventory delta; never publish from metadata.

Input snapshots must be fully paginated, scope-checked, SHA256-verified private
Google Drive exports. Identifies new, changed, out-of-scope and cross-project IDs.
NOT_SEEN_IN_CURRENT_SCOPE does not claim the source was deleted.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE_TYPE = "PRIVATE_DRIVE_RECURSIVE_METADATA_INVENTORY"
COLUMNS = ("project_id","original_filename","mime_type","parent_ids","source_root_ids","modified_time")

def private_path(value, repo=REPO):
    p=Path(value).expanduser().resolve()
    repo=Path(repo).resolve()
    if p == repo or repo in p.parents:
        raise ValueError("Private records may not be read or written inside the public repository")
    return p

def canonical(obj):
    return (json.dumps(obj, sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf8")

def load_snapshot(path, receipt_path, repo=REPO):
    path=private_path(path,repo);receipt_path=private_path(receipt_path,repo)
    if path == receipt_path:raise ValueError("Receipt and source must be distinct")
    meta=json.loads(receipt_path.read_text(encoding="utf8"))
    raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    if meta.get("type") != SOURCE_TYPE:raise ValueError("Wrong source type")
    if digest != meta.get("jsonl_sha256"):raise ValueError("Source SHA256/readback mismatch")
    if any(meta.get(k)!=0 for k in ("public_admissions","drive_modifications","byte_downloads")):
        raise ValueError("Source has unapproved mutations or admissions")
    if meta.get("scope")!="ONLY_REVIEWED_PROJECT_ROOTS" or meta.get("duplicate_policy")!="ONE_DRIVE_ID_ONE_PROJECT_OR_STOP":
        raise ValueError("Unapproved provider scan scope/duplicate contract")
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(rows)!=meta.get("files_and_folders"):raise ValueError("Source row count mismatch")
    byid={}
    for x in rows:
        fid=x.get("drive_file_id")
        if not fid or fid in byid:raise ValueError("Blank or duplicate Drive ID")
        if not all(x.get(k) for k in ("project_id","original_filename","mime_type")):
            raise ValueError("Incomplete provider metadata")
        if not isinstance(x.get("parent_ids"),list) or not isinstance(x.get("source_root_ids"),list):
            raise ValueError("Invalid source ancestry")
        byid[fid]=x
    return byid,meta,digest

def diff_snapshots(previous,current,prior_receipt,current_receipt):
    for key in ("project_root_count","indexed_project_count","root_registry_source","scope"):
        if prior_receipt.get(key)!=current_receipt.get(key):raise ValueError("Changed root scope requires a new validated baseline")
    if prior_receipt.get("root_registry_source")!="ops/data/project-resources.json":
        if not prior_receipt.get("reviewed_root_mapping_sha256") or prior_receipt.get("reviewed_root_mapping_sha256")!=current_receipt.get("reviewed_root_mapping_sha256"):
            raise ValueError("Alternate root map changed or was not authorized")
    if prior_receipt.get("registered_source_coverage",{}).get("registered_sources_checked")!=current_receipt.get("registered_source_coverage",{}).get("registered_sources_checked"):
        raise ValueError("Source registry changed; require separate approved migration")
    changes=[]
    for fid in sorted(set(previous)|set(current)):
        old=previous.get(fid);new=current.get(fid)
        if old is None:kind="NEW_METADATA_CANDIDATE"
        elif new is None:kind="NOT_SEEN_IN_CURRENT_SCOPE_NOT_DELETION"
        elif old["project_id"]!=new["project_id"]:kind="PROJECT_FOREIGN_KEY_CONFLICT"
        elif any(old.get(k)!=new.get(k) for k in COLUMNS):kind="CHANGED_METADATA_REQUIRES_REVIEW"
        else:continue
        x=new or old
        changes.append({
            "drive_file_id":fid,"project_id":x["project_id"],
            "prior_project_id":old["project_id"] if old else None,
            "change_kind":kind,
            "prior_original_filename":old["original_filename"] if old else None,
            "current_original_filename":new["original_filename"] if new else None,
            "prior_mime_type":old["mime_type"] if old else None,
            "current_mime_type":new["mime_type"] if new else None,
            "prior_parent_ids":old["parent_ids"] if old else None,
            "current_parent_ids":new["parent_ids"] if new else None,
            "prior_source_root_ids":old["source_root_ids"] if old else None,
            "current_source_root_ids":new["source_root_ids"] if new else None,
            "review_status":"PRIVATE_REVIEW_QUEUE","source_owner_verified":False,
            "privacy_cleared":False,"current_issued_engineering_approval":False,
            "public_admission":"BLOCKED"
        })
    return changes,dict(sorted(Counter(x["change_kind"] for x in changes).items()))

def run(previous_path,previous_receipt_path,current_path,current_receipt_path,out_jsonl,out_receipt,repo=REPO):
    previous,old_meta,old_sha=load_snapshot(previous_path,previous_receipt_path,repo)
    current,new_meta,new_sha=load_snapshot(current_path,current_receipt_path,repo)
    changes,counts=diff_snapshots(previous,current,old_meta,new_meta)
    target=private_path(out_jsonl,repo);receipt=private_path(out_receipt,repo)
    if target==receipt or target.exists() or receipt.exists():
        raise FileExistsError("Private outputs are append-only: no overwrite")
    body=b"".join(canonical(x) for x in changes)
    result={"type":"PRIVATE_DRIVE_METADATA_INCREMENTAL_DELTA","schema_version":"1.0.0",
        "previous_inventory_sha256":old_sha,"current_inventory_sha256":new_sha,
        "delta_sha256":hashlib.sha256(body).hexdigest(),
        "previous_rows":len(previous),"current_rows":len(current),
        "changed_rows":len(changes),"change_kind_counts":counts,
        "registered_source_coverage_current":new_meta.get("registered_source_coverage",{}),
        "public_admissions":0,"source_original_modifications":0,
        "scan_is_complete_for_approved_roots":True,"all_changed_candidates_remain_private":True,
        "note":"Not seen in current inventory does NOT assert deletion. This receipt grants no permission to publish."}
    for path,contents in ((target,body),(receipt,json.dumps(result,indent=2,sort_keys=True).encode("utf8")+b"\n")):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"wb") as handle:handle.write(contents)
        if path.read_bytes()!=contents:raise IOError("Private readback mismatch")
    return result

def main():
    ap=argparse.ArgumentParser()
    for k in ("previous-jsonl","previous-receipt","current-jsonl","current-receipt","out-jsonl","out-receipt"):
        ap.add_argument("--"+k,required=True)
    a=ap.parse_args()
    result=run(a.previous_jsonl,a.previous_receipt,a.current_jsonl,a.current_receipt,a.out_jsonl,a.out_receipt)
    print(json.dumps({k:result[k] for k in ("previous_rows","current_rows","changed_rows","change_kind_counts","delta_sha256","public_admissions")},sort_keys=True))
if __name__=="__main__":main()
