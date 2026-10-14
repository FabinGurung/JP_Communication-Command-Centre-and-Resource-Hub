#!/usr/bin/env python3
"""REQ07 reviewed-resource promotion STAGING gate (never automatically publishes).

Consumes a SHA-verified private Google Drive snapshot and an independently
authorized PRIVATE decision register. Produces only a PRIVATE draft; a separate
controlled repository change is required before any public resource is added.
Evidence references are mandatory but NOT claimed cryptographically authentic:
the reviewer must verify their source/provider authority independently.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from reconcile_private_resource_inventory import load_snapshot,private_path

ROOT=Path(__file__).resolve().parents[1]
PRIORITIES={"issued_reports":1,"source_models":2,"calculations_and_support":3,"source_folders":4}
MODEL={".dwg",".dxf",".ifc",".skp",".rvt",".e2k",".edb",".sdb",".s2k"}
SENSITIVE=re.compile(r"(BANK|PAYMENT|PAYROLL|SALARY|WAGE|PASSPORT|CITIZENSHIP|NAGARITA|AADHAAR|PERSONNEL|EMPLOYEE|STAFF|KYC|LEGAL|LAND|PERSONAL|PERSON[_ -]?ID|PERS-\d+)",re.I)
APPROVAL_TYPE="REQ07_PRIVATE_RESOURCE_PUBLIC_INDEX_APPROVAL"
def required_evidence(value,decision):
    if not isinstance(value,dict) or value.get("decision")!=decision or not all(
        isinstance(value.get(k),str) and value[k].strip()
        for k in ("approval_record_id","authorized_by","approved_at_npt","independently_verified_sha256")
    ):raise ValueError("Explicit owner/privacy evidence is absent or incomplete")
    if not re.fullmatch(r"[0-9a-f]{64}",value["independently_verified_sha256"]):
        raise ValueError("Evidence SHA256 invalid")

def stage(snapshot_jsonl,snapshot_receipt,private_decisions,output,*,repo=ROOT,known_ids=None):
    rows,meta,sha=load_snapshot(snapshot_jsonl,snapshot_receipt,repo)
    path=private_path(private_decisions,repo);target=private_path(output,repo)
    if target.exists():raise FileExistsError("Reviewed private draft already exists")
    payload=json.loads(path.read_text(encoding="utf8"))
    if payload.get("type")!=APPROVAL_TYPE or payload.get("source_inventory_sha256")!=sha:
        raise ValueError("Approval register does not match authenticated scan")
    approved=payload.get("approved_resources")
    if not isinstance(approved,list):raise ValueError("Expected explicit approved_resources[]")
    published=set(known_ids or ())
    proposed=[];seen=set()
    for record in approved:
        fid=record.get("drive_file_id")
        if fid not in rows or fid in seen or fid in published:raise ValueError("Unknown, duplicate or already indexed Drive ID")
        seen.add(fid);source=rows[fid]
        if source["project_id"]!=record.get("project_id") or source["original_filename"]!=record.get("original_filename"):
            raise ValueError("Project association or original source name mismatch")
        if source["mime_type"]!=record.get("mime_type"):raise ValueError("MIME mismatch")
        if SENSITIVE.search(source["original_filename"]):raise ValueError("Sensitive source requires private exclusion")
        if not record.get("root_project_provenance_verified") is True:
            raise ValueError("No reviewed source-root ownership evidence")
        required_evidence(record.get("source_owner_authorization"),"PUBLIC_RESOURCE_POINTER_ALLOWED")
        required_evidence(record.get("privacy_authorization"),"NAME_AND_SOURCE_LINK_ALLOWED")
        category=record.get("category")
        ext=Path(source["original_filename"]).suffix.lower()
        if category=="issued_reports" and ext!=".pdf":raise ValueError("Wrong drawing/report file type")
        if category=="source_models" and ext not in MODEL:raise ValueError("Wrong editable model type")
        if category=="source_folders" and source["mime_type"]!="application/vnd.google-apps.folder":
            raise ValueError("Only folders may be source_folders")
        if category=="calculations_and_support" and ext not in (".pdf",".xls",".xlsx",".ods",".csv",".docx"):
            raise ValueError("Wrong calculation file type")
        if category not in PRIORITIES:raise ValueError("Unknown category")
        for key in ("resource_id","normalized_name","discipline"):
            if not isinstance(record.get(key),str) or not record[key].strip():
                raise ValueError("Missing resource identity/usable label")
        if not re.fullmatch(r"RES-P\d{3}-[A-Z0-9-]+",record["resource_id"]):
            raise ValueError("Malformed future resource PK")
        if record.get("technical_issue_status")!="UNVERIFIED_AS_CURRENT_ISSUE":
            raise ValueError("Filename or owner review cannot assert engineering issuance")
        proposed.append({
            "resource_id":record["resource_id"],"project_id":source["project_id"],
            "source_drive_file_id":fid,"original_drive_filename":source["original_filename"],
            "mime_type":source["mime_type"],"category":category,
            "sort_priority":PRIORITIES[category],"normalized_name":record["normalized_name"],
            "discipline":record["discipline"],"approval_status":"UNVERIFIED_AS_CURRENT_ISSUE",
            "source_receipt_sha256":sha,
            "publication_state":"PRIVATE_STAGING_REQUIRES_SEPARATE_GITHUB_REVIEW_AND_QA"
        })
    if len({x["resource_id"] for x in proposed})!=len(proposed):
        raise ValueError("Duplicate future resource PK")
    body={"type":"REQ07_PRIVATE_APPROVED_PUBLIC_CANDIDATES","schema_version":"1.0",
          "source_inventory_sha256":sha,"source_original_modifications":0,
          "public_resource_admissions":0,"proposed_count":len(proposed),
          "reviewed_candidates":sorted(proposed,key=lambda x:(x["project_id"],x["resource_id"]))}
    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    data=(json.dumps(body,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf8")
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"wb") as f:f.write(data)
    if target.read_bytes()!=data:raise IOError("Private readback failed")
    return {"proposed_count":len(proposed),"private_output_sha256":hashlib.sha256(data).hexdigest(),"public_admissions":0}

def main():
    p=argparse.ArgumentParser()
    for flag in ("snapshot-jsonl","snapshot-receipt","private-decisions","private-output"):
        p.add_argument("--"+flag,required=True)
    a=p.parse_args()
    catalog=json.loads((ROOT/"ops/data/resource-catalog-normalized.v0.1.json").read_text(encoding="utf8"))
    known={item["source_drive_file_id"] for site in catalog["sites"] for item in site["files"]}
    print(json.dumps(stage(a.snapshot_jsonl,a.snapshot_receipt,a.private_decisions,a.private_output,
                           known_ids=known),sort_keys=True))
if __name__=="__main__":main()
