#!/usr/bin/env python3
"""Req07 private resource metadata intake PREVIEW, not a public-file publisher.

Accepts an external authenticated Drive metadata JSON export. Writes a stable,
review-needed candidate ledger outside the public repository, never to GitHub,
never into the published catalog, and never modifies original Drive bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SENSITIVE=re.compile(r"(citizenship|nagarita|lalpurja|passport|bank|tax|kitta|legal|personal|restricted|salary)",re.I)
MODELS={"DWG","DXF","IFC","E2K","EDB","SKP","RVT","S2K","SDB"}
SUPPORT={"XLS","XLSX","ODS","CSV","DOCX"}
PUBLIC_CATALOG=ROOT/"ops/data/resource-catalog-normalized.v0.1.json"

def require(value,message):
    if not value: raise ValueError("RESOURCE_INTAKE_REVIEW: "+message)

def private_path(path):
    p=Path(path).expanduser().resolve()
    require(p!=ROOT and ROOT not in p.parents,
            "provider metadata/review candidates cannot be read from or written into the public repository")
    return p

def candidate_category(name,mime):
    if mime=="application/vnd.google-apps.folder":return ("source_folders",4)
    ext=Path(name).suffix.lstrip(".").upper()
    if ext in MODELS:return ("source_models",2)
    if ext in SUPPORT:return ("calculations_and_support",3)
    if ext=="PDF":
        if re.search(r"(estimate|boq|calculation|curtailment|quantity.?takeoff|qto|rate.?analysis)",name,re.I):
            return ("calculations_and_support",3)
        return ("issued_reports",1)
    return ("UNCLASSIFIED",None)

def review_candidates(rows,existing,known_projects):
    used={}
    out=[]
    for row in rows:
        pid=str(row.get("project_id") or "")
        fid=str(row.get("drive_file_id") or "")
        name=str(row.get("original_filename") or "")
        mime=str(row.get("mime_type") or "")
        require(fid and name and mime, "metadata row requires Drive file ID, original filename and MIME")
        if fid in used:
            require(used[fid]==(pid,name,mime),"conflicting duplicate Drive ID in intake batch")
            continue
        used[fid]=(pid,name,mime)
        classification,priority=candidate_category(name,mime)
        existing_entry=existing.get(fid)
        flags=[]
        if existing_entry:flags.append("ALREADY_INDEXED_DO_NOT_INGEST")
        if pid not in known_projects:flags.append("UNMAPPED_PROJECT_FK")
        if SENSITIVE.search(name):flags.append("POTENTIALLY_PRIVATE_QUARANTINE")
        if classification=="UNCLASSIFIED":flags.append("UNKNOWN_FORMAT_REVIEW")
        if not row.get("source_receipt_id"):flags.append("PROVIDER_READBACK_RECEIPT_MISSING")
        if not row.get("source_parent_verified"):flags.append("SOURCE_PARENT_PROJECT_UNVERIFIED")
        status="ALREADY_INDEXED" if existing_entry else "REVIEW_REQUIRED"
        if any(flag in flags for flag in ("UNMAPPED_PROJECT_FK","POTENTIALLY_PRIVATE_QUARANTINE")):
            status="QUARANTINED"
        key=hashlib.sha256((pid+"\x00"+fid).encode()).hexdigest()[:24]
        out.append({
            "candidate_id":"RES-CAND-"+key,"project_id":pid,"drive_file_id":fid,
            "original_filename":name,"mime_type":mime,
            "source_receipt_id":row.get("source_receipt_id"),
            "source_parent_verified":row.get("source_parent_verified") is True,
            "proposed_category":classification,"proposed_priority":priority,
            "review_status":status,"flags":flags,
            "publication_status":"BLOCKED_UNTIL_SOURCE_METADATA_PRIVACY_AND_ENGINEER_REVIEW",
            "normalized_label":"REQUIRES_REVIEW_NO_AUTOMATIC_APPROVAL",
        })
    return sorted(out,key=lambda r:(r["project_id"],r["drive_file_id"]))

def read_private_metadata_export(source,receipt=None):
    """Adapt the private recursive inventory into review candidates with SHA readback.

    A receipt is required for JSONL output from collect_private_drive_resource_metadata.
    Source parent verification remains FALSE for candidates until separately reviewed.
    """
    source=private_path(source)
    if receipt is None:
        result=json.loads(source.read_text(encoding="utf-8"))
        require(isinstance(result,dict) and isinstance(result.get("files"),list),
                "JSON metadata input must contain files[]")
        return result
    receipt=private_path(receipt)
    require(receipt!=source,"receipt must be separate from the inventory")
    record=json.loads(receipt.read_text(encoding="utf-8"))
    raw=source.read_bytes()
    require(record.get("type")=="PRIVATE_DRIVE_RECURSIVE_METADATA_INVENTORY",
            "wrong private provider inventory receipt")
    require(hashlib.sha256(raw).hexdigest()==record.get("jsonl_sha256"),
            "PRIVATE_PROVIDER_READBACK_SHA256_MISMATCH")
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
    require(len(rows)==record.get("files_and_folders"),
            "private inventory row count does not match signed receipt")
    require(record.get("public_admissions")==0 and record.get("byte_downloads")==0,
            "input scan was incorrectly declared to have published or downloaded bytes")
    receipt_id=record["jsonl_sha256"]
    for row in rows:
        row["source_receipt_id"]=receipt_id
        # Parent in list is not independent parent/owner identity verification;
        # Drive child listings may be incomplete (REQ07 documented failure).
        row["source_parent_verified"]=False
    return {"source_export_receipt":receipt_id,
            "coverage_warning":record.get("status"),
            "files":rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True,help="authenticated Drive metadata JSON export kept outside public repository")
    ap.add_argument("--receipt",type=Path,help="private SHA-256 JSON receipt for --input JSONL from recursive Drive scan")
    ap.add_argument("--output",type=Path,required=True,help="private review candidate JSON (must be outside public repository)")
    a=ap.parse_args()
    source=private_path(a.input)
    target=private_path(a.output)
    require(source!=target and (not a.receipt or target!=private_path(a.receipt)),
            "output cannot overwrite provider scan or receipt")
    require(not target.exists(),"refusing to overwrite existing reviewed candidate batch")
    payload=read_private_metadata_export(source,a.receipt)
    catalog=json.loads(PUBLIC_CATALOG.read_text(encoding="utf-8"))
    existing={f["source_drive_file_id"]:f for s in catalog["sites"] for f in s["files"]}
    known={s["project_id"] for s in catalog["sites"]}
    candidates=review_candidates(payload["files"],existing,known)
    result={"schema_version":"0.1.0","type":"PRIVATE_METADATA_ADMISSION_PREVIEW",
            "source_export_receipt":payload.get("source_export_receipt"),
            "coverage_warning":payload.get("coverage_warning"),
            "automatic_publication":False,"rows":candidates}
    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    target.chmod(0o600)
    summaries={k:sum(r["review_status"]==k for r in candidates)
               for k in ("ALREADY_INDEXED","QUARANTINED","REVIEW_REQUIRED")}
    print("RESOURCE_INTAKE_PREVIEW_ONLY: "+str(summaries)+
          "; candidate source details remain in your private output; no public files or originals changed.")

if __name__=="__main__":main()
