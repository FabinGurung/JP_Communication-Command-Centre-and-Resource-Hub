#!/usr/bin/env python3
"""Req07: authenticated metadata-only recursive Drive inventory into PRIVATE storage.

Run in authorized Colab/Google runtime with google-api-python-client and
google-auth. Does not run on public GitHub Actions, download file bytes,
change Drive originals, or publish any candidate to the public Resources site.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDER="application/vnd.google-apps.folder"

def private_file(value):
    p=Path(value).expanduser().resolve()
    if p==ROOT or ROOT in p.parents:
        raise ValueError("Source inventory output/input must stay OUTSIDE the public repository")
    return p

def crawl(roots, fetch_page, *, max_rows=100000):
    rows={}
    visited_folders=set()
    for project_id,root_id in sorted(roots.items()):
        queue=[(root_id,root_id)]
        while queue:
            folder,source_root=queue.pop(0)
            key=(project_id,folder)
            if key in visited_folders:continue
            visited_folders.add(key)
            page_token=None
            while True:
                children,next_token=fetch_page(folder,page_token)
                for file in children:
                    fid=file["id"]
                    name=file["name"]
                    mime=file["mimeType"]
                    if not fid or not name or not mime:raise ValueError("Incomplete Drive metadata")
                    if fid in rows and rows[fid]["project_id"]!=project_id:
                        raise ValueError("Cross-project Drive ID collision requires private review")
                    rows[fid]={
                        "project_id":project_id,"source_root_id":source_root,
                        "drive_file_id":fid,"original_filename":name,"mime_type":mime,
                        "parent_ids":file.get("parents") or [],"modified_time":file.get("modifiedTime"),
                        "drive_view_url":file.get("webViewLink"),
                        "admission_status":"PRIVATE_METADATA_ONLY_REVIEW_REQUIRED",
                    }
                    if len(rows)>max_rows:raise ValueError("Max records reached; no partial source inventory is certified")
                    if mime==FOLDER:queue.append((fid,source_root))
                if not next_token:break
                page_token=next_token
    return list(sorted(rows.values(),key=lambda x:(x["project_id"],x["drive_file_id"]))),len(visited_folders)

def google_fetch_page():
    import google.auth
    from googleapiclient.discovery import build
    credentials,_=google.auth.default(scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"])
    service=build("drive","v3",credentials=credentials,cache_discovery=False)
    def fetch(parent,page_token):
        escaped=parent.replace("\\","\\\\").replace("'","\\'")
        kwargs={"q":f"'{escaped}' in parents and trashed = false",
                "fields":"nextPageToken,files(id,name,mimeType,parents,modifiedTime,webViewLink)",
                "pageSize":1000,"supportsAllDrives":True,
                "includeItemsFromAllDrives":True}
        if page_token:kwargs["pageToken"]=page_token
        result=service.files().list(**kwargs).execute()
        return result.get("files",[]),result.get("nextPageToken")
    return fetch

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--roots",type=Path,required=True,help="private JSON map of reviewed project_id to authorized Drive root id")
    ap.add_argument("--private-jsonl",type=Path,required=True)
    ap.add_argument("--receipt",type=Path,required=True)
    ap.add_argument("--max-rows",type=int,default=100000)
    a=ap.parse_args()
    source=private_file(a.roots)
    output=private_file(a.private_jsonl)
    receipt=private_file(a.receipt)
    if output==receipt or output==source or receipt==source:raise ValueError("Input and output paths must differ")
    if output.exists() or receipt.exists():raise FileExistsError("No overwriting existing private inventories or receipts")
    roots=json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(roots,dict) or not roots:raise ValueError("Private authorized root map required")
    canon=json.loads((ROOT/"ops/data/project-identity-index.v0.1.json").read_text(encoding="utf-8"))
    known={r["legacy_project_code"] for r in canon["records"] if r["legacy_project_code"]}
    if any(pid not in known or not isinstance(fid,str) or not fid for pid,fid in roots.items()):
        raise ValueError("Every root must have a verified project foreign key and provider folder ID")
    rows,folders=crawl(roots,google_fetch_page(),max_rows=a.max_rows)
    body="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows).encode("utf-8")
    metadata={
        "type":"PRIVATE_DRIVE_RECURSIVE_METADATA_INVENTORY",
        "status":"METADATA_COLLECTED_NOT_APPROVED_FOR_PUBLICATION",
        "project_root_count":len(roots),"visited_folders":folders,
        "files_and_folders":len(rows),"jsonl_sha256":hashlib.sha256(body).hexdigest(),
        "scope":"ONLY_REVIEWED_PROJECT_ROOTS",
        "duplicate_policy":"ONE_DRIVE_ID_ONE_PROJECT_OR_STOP",
        "byte_downloads":0,"drive_modifications":0,"public_admissions":0,
    }
    for path,contents in ((output,body),(receipt,(json.dumps(metadata,indent=2)+"\n").encode())):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"wb") as f:f.write(contents)
        if path.read_bytes()!=contents:raise IOError("Private file readback mismatch")
    print("PRIVATE_DRIVE_INVENTORY_RECEIPT: roots="+str(len(roots))+
          " folders="+str(folders)+" entries="+str(len(rows))+
          " hash="+metadata["jsonl_sha256"]+
          "; no public resource ingestion/approval and no source byte writes")

if __name__=="__main__":main()
