#!/usr/bin/env python3
"""REQ07 private production runner: authenticated full rescan + classified incremental queue.

Must run where Google Drive OAuth service credentials are available. This is NOT
a GitHub Actions workflow; private data NEVER goes into the public repository.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from reconcile_private_resource_inventory import private_path

ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent

def step(*argv):
    subprocess.run([sys.executable,*map(str,argv)],cwd=ROOT,check=True,
                   stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def upload_private(paths,destination_id):
    """Upload to a demonstrably non-shared Drive folder; check remote MD5/size."""
    import google.auth
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    credentials,_=google.auth.default(scopes=["https://www.googleapis.com/auth/drive.file"])
    service=build("drive","v3",credentials=credentials,cache_discovery=False)
    folder=service.files().get(fileId=destination_id,
        fields="id,mimeType,trashed,shared,permissions(type,role)",
        supportsAllDrives=True).execute()
    if folder.get("trashed") or folder.get("mimeType")!="application/vnd.google-apps.folder":
        raise ValueError("Destination is not an active Drive folder")
    if folder.get("shared") is not False or any(
        p.get("type") not in (None,"user") for p in folder.get("permissions",[])
    ):raise PermissionError("Destination private access could not be verified")
    created=[]
    for p in paths:
        escaped=destination_id.replace("\\","\\\\").replace("'","\\'")
        query=f"'{escaped}' in parents and name = '{p.name}' and trashed = false"
        existing=service.files().list(q=query,fields="nextPageToken,files(id)",pageSize=1000,
            supportsAllDrives=True,includeItemsFromAllDrives=True).execute()
        if existing.get("files") or existing.get("nextPageToken"):
            raise FileExistsError("Private run file exists; no replacement is allowed")
        expected_md5=hashlib.md5(p.read_bytes()).hexdigest()
        out=service.files().create(body={
            "name":p.name,"parents":[destination_id],
            "description":"REQ07 PRIVATE resource metadata; not approved for publication"},
            media_body=MediaFileUpload(str(p),mimetype="application/octet-stream",resumable=True),
            fields="id,md5Checksum,size,parents",supportsAllDrives=True).execute()
        if out.get("md5Checksum")!=expected_md5 or int(out.get("size",-1))!=p.stat().st_size or destination_id not in out.get("parents",[]):
            raise IOError("Authenticated Drive remote MD5, byte size or parent readback failed")
        created.append(out["id"])
    return len(created)

def run(baseline_jsonl,baseline_receipt,run_dir,upload_folder_id=None):
    old=private_path(baseline_jsonl);oldreceipt=private_path(baseline_receipt)
    folder=private_path(run_dir)
    if folder.exists():raise FileExistsError("Run folder already exists; do not duplicate")
    folder.mkdir(parents=True,mode=0o700)
    inventory=folder/"registered_roots_metadata.jsonl"
    receipt=folder/"registered_roots_metadata.receipt.json"
    preview=folder/"private_candidate_review.json"
    classified=folder/"classified_private_resources.jsonl"
    classreceipt=folder/"classified_private_resources.receipt.json"
    delta=folder/"private_incremental_delta.jsonl"
    deltareceipt=folder/"private_incremental_delta.receipt.json"
    step(HERE/"collect_private_drive_resource_metadata.py","--registered-roots",
         "--private-jsonl",inventory,"--receipt",receipt)
    step(HERE/"preview_resource_intake.py","--input",inventory,"--receipt",receipt,"--output",preview)
    step(HERE/"classify_private_resource_inventory.py","--inventory",inventory,
         "--preview",preview,"--receipt",receipt,"--out-jsonl",classified,"--out-receipt",classreceipt)
    step(HERE/"reconcile_private_resource_inventory.py","--previous-jsonl",old,
         "--previous-receipt",oldreceipt,"--current-jsonl",inventory,"--current-receipt",receipt,
         "--out-jsonl",delta,"--out-receipt",deltareceipt)
    changes=json.loads(deltareceipt.read_text(encoding="utf8"))
    inventory_meta=json.loads(receipt.read_text(encoding="utf8"))
    if any(inventory_meta.get(k)!=0 for k in ("byte_downloads","drive_modifications","public_admissions")):
        raise ValueError("Unexpected writes/source bytes in metadata-only scan")
    outputs=(inventory,receipt,preview,classified,classreceipt,delta,deltareceipt)
    saved=upload_private(outputs,upload_folder_id) if upload_folder_id else 0
    return {"metadata_entries":inventory_meta["files_and_folders"],
        "change_rows":changes["changed_rows"],"change_categories":changes["change_kind_counts"],
        "private_artifacts_verified":len(outputs),"uploaded_into_private_drive":saved,
        "public_admissions":0,"source_original_modifications":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-jsonl",required=True)
    p.add_argument("--baseline-receipt",required=True)
    p.add_argument("--new-private-run-folder",required=True)
    p.add_argument("--upload-private-folder-id")
    a=p.parse_args()
    print(json.dumps(run(a.baseline_jsonl,a.baseline_receipt,a.new_private_run_folder,a.upload_private_folder_id),sort_keys=True))
if __name__=="__main__":main()
