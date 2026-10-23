#!/usr/bin/env python3
"""Generate a minimal public-safe Pages index from already MERGED project submissions.

Source files in private Google Drive are never read or copied.
Unapproved PUBLIC_CANDIDATE entries are deliberately omitted.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"contributions"
ID=re.compile(r"^PRJ-[0-9]{6}$")
SUB=re.compile(r"^[a-z0-9][a-z0-9-]{2,48}$")
out=[]
for file in sorted(BASE.glob("*/*/manifest.json")):
    rel=file.relative_to(BASE)
    project,submission=rel.parts[:2]
    if not ID.fullmatch(project) or not SUB.fullmatch(submission):
        raise SystemExit("Unsafe contribution directory name")
    info=json.loads(file.read_text(encoding="utf-8"))
    if info.get("publication_state")!="APPROVED_PUBLIC":
        continue
    if info.get("privacy_review")!="PUBLIC_SAFE_ATTESTED" or info.get("project_id")!=project or info.get("submission_id")!=submission:
        raise SystemExit("Rejected unpublished/incorrect contribution")
    label=html.escape(str(info.get("title","Untitled")))
    workstream=html.escape(str(info.get("workstream","other")))
    path=f"{project}/{submission}/manifest.json"
    out.append(f'<li><a href="{html.escape(path)}">{label}</a> — {html.escape(project)} / {workstream}</li>')
markup="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JP Project Contributions</title><style>body{font:1rem/1.6 system-ui,sans-serif;max-width:56rem;padding:2rem;margin:auto}a{color:#135a88}li{margin:.7rem 0}</style></head><body><h1>JP project contributions</h1><p>Reviewed public-safe project submissions generated from versioned GitHub manifests. Original files remain with their owning provider.</p>""" + ("<ul>"+"".join(out)+"</ul>" if out else "<p>No reviewed project submissions published yet.</p>") + "</body></html>"
(BASE/"index.html").write_text(markup,encoding="utf-8")
print(f"CONTRIBUTION_INDEX_PASS: {len(out)} approved public submission(s)")
