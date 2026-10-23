#!/usr/bin/env python3
"""Assemble only explicitly reviewed Pages assets; public GitHub source is never private."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
EXT={".html",".css",".js",".json",".jsonl",".csv",".svg",".png",".jpg",".jpeg",".webp",".ico",".txt"}
REQUIRED={"index.html","map.html","site-operations.html","resources/index.html","workspace/index.html","guide/index.html"}
KEYS={"schema_version","project_id","submission_id","title","workstream","publication_state","privacy_review","engineering_status"}
def die(msg): raise SystemExit("PAGES_ARTIFACT_FAIL: "+msg)
def checked(root,raw):
    if not isinstance(raw,str) or not raw or "\\" in raw or ":" in raw: die("bad path")
    p=PurePosixPath(raw)
    if p.is_absolute() or any(part in {"",".",".."} for part in raw.split("/")): die("unsafe path "+raw)
    if raw!=".nojekyll" and (any(q.startswith(".") for q in p.parts) or p.suffix.lower() not in EXT): die("hidden/unlisted extension "+raw)
    f=root
    for q in p.parts:
        f=f/q
        if f.is_symlink(): die("symlink in public assets "+raw)
    if not f.is_file() or not f.resolve().is_relative_to(root.resolve()): die("missing or escaped file "+raw)
    return f
def approved(root):
    out=[]
    for f in sorted((root/"contributions").glob("*/*/manifest.json")):
        rel=f.relative_to(root)
        if len(rel.parts)!=4 or not re.fullmatch(r"PRJ-[0-9]{6}",rel.parts[1]) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,48}",rel.parts[2]): die("bad project path")
        checked(root,rel.as_posix())
        try: info=json.loads(f.read_text(encoding="utf-8"))
        except (ValueError,UnicodeError): die("malformed manifest")
        if not isinstance(info,dict) or set(info)!=KEYS or info["project_id"]!=rel.parts[1] or info["submission_id"]!=rel.parts[2]: die("bad manifest identity")
        if info["publication_state"]=="PUBLIC_CANDIDATE": continue
        if info["publication_state"]!="APPROVED_PUBLIC" or info["privacy_review"]!="PUBLIC_SAFE_ATTESTED": die("unapproved manifest")
        out.append(rel.as_posix())
    return out
def build(root,out,policy_path):
    root=root.resolve();out=out.resolve()
    if out.exists(): die("output already exists; refusing stale artifact")
    cfg=json.loads(policy_path.read_text(encoding="utf-8"))
    if cfg.get("schema_version")!="1.0.0" or cfg.get("policy_id")!="OPS_PAGES_EXPLICIT_PUBLIC_FILES_V1": die("invalid public policy")
    files=cfg.get("files")
    if not isinstance(files,list) or any(not isinstance(x,str) for x in files) or len(files)!=len(set(files)): die("invalid inventory")
    if not REQUIRED.issubset(set(files)) or any(x.startswith("contributions/") for x in files): die("invalid static routes")
    selected=sorted(files+["contributions/index.html"]+approved(root))
    sources=[(name,checked(root,name)) for name in selected]
    out.mkdir(parents=True)
    items=[]
    for name,src in sources:
        target=out/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,target)
        items.append({"path":name,"sha256":hashlib.sha256(src.read_bytes()).hexdigest()})
    report={"schema_version":"1.0.0","source_commit":os.environ.get("GITHUB_SHA","LOCAL_BUILD"),"asset_count":len(items),"assets":items}
    (out/"publication-manifest.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"PAGES_ARTIFACT_ALLOWLIST_PASS: {len(items)} reviewed public files, no whole-repository upload")
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,default=ROOT)
    a.add_argument("--output",type=Path,default=ROOT/"_site")
    a.add_argument("--allowlist",type=Path,default=ROOT/"ops/control/pages-public-file-allowlist.v1.json")
    x=a.parse_args()
    build(x.source,x.output,x.allowlist)
