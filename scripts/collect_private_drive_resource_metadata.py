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

def normalize_roots(roots):
    """Allow a single root or explicitly reviewed alternate roots per project."""
    if not isinstance(roots, dict) or not roots:
        raise ValueError("Reviewed project root mapping is required")
    clean={}
    for pid, value in roots.items():
        identifiers=[value] if isinstance(value,str) else value
        if not isinstance(identifiers,list) or not identifiers or any(
            not isinstance(x,str) or not x.strip() for x in identifiers
        ):
            raise ValueError("Project roots must be nonempty strings or lists of Drive IDs")
        if len(set(identifiers))!=len(identifiers):
            raise ValueError("Duplicate authorized root ID within one project")
        clean[pid]=sorted(identifiers)
    if len({id for values in clean.values() for id in values})!=sum(len(v) for v in clean.values()):
        raise ValueError("Same Drive root assigned to more than one project")
    return clean

def crawl(roots, fetch_page, *, max_rows=100000, return_visited=False):
    rows={}
    visited_folders=set()  # Unique provider folders visited (reporting and source reconciliation)
    visited_source_scopes=set()  # A folder may occur beneath two authorized roots
    for project_id,root_ids in sorted(normalize_roots(roots).items()):
        queue=[(root_id,root_id) for root_id in root_ids]
        while queue:
            folder,source_root=queue.pop(0)
            key=(project_id,folder,source_root)
            if key in visited_source_scopes:continue
            visited_source_scopes.add(key)
            visited_folders.add((project_id,folder))
            page_token=None
            page_tokens=set()
            while True:
                if page_token in page_tokens:
                    raise ValueError("Repeated provider page token; inventory is not complete")
                page_tokens.add(page_token)
                children,next_token=fetch_page(folder,page_token)
                for file in children:
                    fid=file["id"]
                    name=file["name"]
                    mime=file["mimeType"]
                    if not fid or not name or not mime:raise ValueError("Incomplete Drive metadata")
                    if fid in rows and rows[fid]["project_id"]!=project_id:
                        raise ValueError("Cross-project Drive ID collision requires private review")
                    if fid in rows:
                        previous=rows[fid]
                        if previous["original_filename"]!=name or previous["mime_type"]!=mime:
                            raise ValueError("Conflicting metadata for duplicate Drive ID")
                        previous["source_root_ids"]=sorted(set(previous["source_root_ids"]+[source_root]))
                        # Even a previously indexed folder needs traversal for this
                        # source root, or its descendants lose alternate-root lineage.
                        if mime==FOLDER:queue.append((fid,source_root))
                        continue
                    rows[fid]={
                        "project_id":project_id,"source_root_ids":[source_root],
                        "drive_file_id":fid,"original_filename":name,"mime_type":mime,
                        "parent_ids":file.get("parents") or [],"modified_time":file.get("modifiedTime"),
                        "drive_view_url":file.get("webViewLink"),
                        "admission_status":"PRIVATE_METADATA_ONLY_REVIEW_REQUIRED",
                    }
                    if len(rows)>max_rows:raise ValueError("Max records reached; no partial source inventory is certified")
                    if mime==FOLDER:queue.append((fid,source_root))
                if not next_token:break
                page_token=next_token
    result=list(sorted(rows.values(),key=lambda x:(x["project_id"],x["drive_file_id"])))
    if return_visited:
        return result,visited_folders
    return result,len(visited_folders)

def reconcile_indexed_sources(rows, visited_folders, reviewed_roots, fetch_meta, catalog):
    """Detect provider-search omissions using independent metadata-by-ID readback.

    Known files outside scanned parent folders are flagged as uncovered, never
    misrepresented as a complete inventory. Missing known children STOP release.
    """
    indexed={r["drive_file_id"]:r for r in rows}
    covered=0
    uncovered=[]
    for site in catalog["sites"]:
        pid=site["project_id"]
        if pid not in reviewed_roots: continue
        scanned={folder for owner,folder in visited_folders if owner==pid}
        for item in site["files"]:
            fid=item["source_drive_file_id"]
            meta=fetch_meta(fid)
            if not meta or meta.get("trashed"):
                raise ValueError("Indexed Drive source no longer resolves; stop: "+item["resource_id"])
            if meta.get("name")!=item["original_drive_filename"] or meta.get("mimeType")!=item["mime_type"]:
                raise ValueError("Previously indexed source metadata drift: "+item["resource_id"])
            if fid in reviewed_roots[pid]:
                # The root folder itself is a traversal input, not its own child.
                covered+=1
                continue
            parents=set(meta.get("parents") or [])
            if parents & scanned:
                if fid not in indexed or indexed[fid]["project_id"]!=pid:
                    raise ValueError("PARENT_LIST_COVERAGE_GAP: registered resource omitted by child listing: "+
                                     item["resource_id"])
                covered+=1
            else:
                uncovered.append(item["resource_id"])
    return {"registered_sources_checked":covered+len(uncovered),
            "covered_registered_sources":covered,
            "known_sources_outside_scanned_parents":len(uncovered),
            "uncovered_resource_ids":sorted(uncovered)}

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
    def by_id(file_id):
        return service.files().get(
            fileId=file_id,
            fields="id,name,mimeType,parents,trashed",
            supportsAllDrives=True
        ).execute()
    return fetch,by_id

def main():
    ap=argparse.ArgumentParser()
    origin=ap.add_mutually_exclusive_group(required=True)
    origin.add_argument("--roots",type=Path,help="private JSON map of project_id to authorized Drive root id(s)")
    origin.add_argument("--registered-roots",action="store_true",
                        help="read exact existing authorized project root IDs from GitHub's versioned source pointers")
    ap.add_argument("--projects",help="optional comma-separated project IDs for --registered-roots; default all")
    ap.add_argument("--private-jsonl",type=Path,required=True)
    ap.add_argument("--receipt",type=Path,required=True)
    ap.add_argument("--max-rows",type=int,default=100000)
    a=ap.parse_args()
    source=private_file(a.roots) if a.roots else None
    output=private_file(a.private_jsonl)
    receipt=private_file(a.receipt)
    if output==receipt or (source is not None and (output==source or receipt==source)):
        raise ValueError("Input and output paths must differ")
    if output.exists() or receipt.exists():raise FileExistsError("No overwriting existing private inventories or receipts")
    if source is not None:
        if a.projects:raise ValueError("--projects applies only to --registered-roots")
        roots=json.loads(source.read_text(encoding="utf-8"))
    else:
        registry=json.loads((ROOT/"ops/data/project-resources.json").read_text(encoding="utf-8"))
        roots={}
        selected=set(a.projects.split(",")) if a.projects else None
        for project in registry["projects"]:
            pid=project["project_id"]
            if selected is not None and pid not in selected:continue
            ids=[item["drive_file_id"] for item in project["resources"]
                 if item["resource_type"]=="PROJECT_DRIVE_FOLDER"]
            if not ids:raise ValueError("Project is missing an authoritative registered Drive root: "+pid)
            roots[pid]=ids
        if selected is not None and set(roots)!=selected:
            raise ValueError("Unknown or unregistered project root in --projects filter")
    canon=json.loads((ROOT/"ops/data/project-identity-index.v0.1.json").read_text(encoding="utf-8"))
    known={r["legacy_project_code"] for r in canon["records"] if r["legacy_project_code"]}
    normalized_roots=normalize_roots(roots)
    if any(pid not in known for pid in normalized_roots):
        raise ValueError("Every root must have a verified project foreign key")
    fetch_page,fetch_meta=google_fetch_page()
    for pid, ids in normalized_roots.items():
        for root_id in ids:
            m=fetch_meta(root_id)
            if not m or m.get("trashed") or m.get("mimeType")!=FOLDER:
                raise ValueError("Registered project Drive root metadata verification failed: "+pid)
    rows,visited=crawl(normalized_roots,fetch_page,max_rows=a.max_rows,return_visited=True)
    folders=len(visited)
    catalog=json.loads((ROOT/"ops/data/resource-catalog-normalized.v0.1.json").read_text(encoding="utf-8"))
    coverage=reconcile_indexed_sources(rows,visited,normalized_roots,fetch_meta,catalog)
    body="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows).encode("utf-8")
    metadata={
        "type":"PRIVATE_DRIVE_RECURSIVE_METADATA_INVENTORY",
        "status":"METADATA_COLLECTED_NOT_APPROVED_FOR_PUBLICATION__ALTERNATE_ROOTS_OPEN"
            if coverage["known_sources_outside_scanned_parents"] else
            "METADATA_COLLECTED_NOT_APPROVED_FOR_PUBLICATION",
        "project_root_count":sum(len(ids) for ids in normalized_roots.values()),
        "indexed_project_count":len(normalized_roots),
        "root_registry_source":"ops/data/project-resources.json" if a.registered_roots else "PRIVATE_EXTERNAL_REVIEWED_ROOT_MAP",
        "visited_folders":folders,
        "files_and_folders":len(rows),"jsonl_sha256":hashlib.sha256(body).hexdigest(),
        "scope":"ONLY_REVIEWED_PROJECT_ROOTS",
        "duplicate_policy":"ONE_DRIVE_ID_ONE_PROJECT_OR_STOP",
        "registered_source_coverage":coverage,
        "byte_downloads":0,"drive_modifications":0,"public_admissions":0,
    }
    for path,contents in ((output,body),(receipt,(json.dumps(metadata,indent=2)+"\n").encode())):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"wb") as f:f.write(contents)
        if path.read_bytes()!=contents:raise IOError("Private file readback mismatch")
    print("PRIVATE_DRIVE_INVENTORY_RECEIPT: roots="+str(sum(len(v) for v in normalized_roots.values()))+
          " folders="+str(folders)+" entries="+str(len(rows))+
          " hash="+metadata["jsonl_sha256"]+
          "; no public resource ingestion/approval and no source byte writes")

if __name__=="__main__":main()
