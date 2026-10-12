#!/usr/bin/env python3
"""Derived public-safe project name/PK/FK index. projects.csv alone owns canonical identity.

Usage: python scripts/project_identity_index.py --check
       python scripts/project_identity_index.py --write
Never edits projects.csv, current-works, resources, progress, or Drive originals.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MASTER="projects.csv"
INDEX="ops/data/project-identity-index.v0.1.json"

def require(value, problem):
    if not value: raise SystemExit("PROJECT_IDENTITY_FAIL: "+problem)

def load(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

def clean(v):
    return str(v or "").strip()

def build():
    source=(ROOT/MASTER).read_bytes()
    digest=hashlib.sha1(b"blob "+str(len(source)).encode("ascii")+b"\x00"+source).hexdigest()
    with (ROOT/MASTER).open(newline="",encoding="utf-8-sig") as f:
        master=list(csv.DictReader(f))
    require(master,"Empty project identity master")
    ids, codes, aliases = set(), set(), set()
    records=[]
    for i,r in enumerate(master,2):
        pk=clean(r.get("project_id"))
        label=clean(r.get("display_name"))
        company=clean(r.get("company_project_code"))
        alias=clean(r.get("legacy_project_code"))
        slug=clean(r.get("project_name"))
        require(pk and label and company and slug,f"Missing canonical identity on CSV row {i}")
        require(pk not in ids,f"Duplicate global project PK {pk}")
        require(company not in codes,f"Duplicate company project code {company}")
        require(not alias or alias not in aliases,f"Duplicate legacy site code {alias}")
        ids.add(pk);codes.add(company)
        if alias: aliases.add(alias)
        records.append({
            "project_id":pk,
            "display_name":label,
            "company_project_code":company,
            "legacy_project_code":alias or None,
            "project_slug":slug,
            "executing_company_id":clean(r.get("executing_company_id")),
            "ward_number":clean(r.get("location_ward_number")) or None,
            "master_source_row":i,
        })
    records.sort(key=lambda x:x["project_id"])
    by_pk={r["project_id"]:r for r in records}
    by_alias={r["legacy_project_code"]:r for r in records if r["legacy_project_code"]}
    current=load("ops/data/current-works.json")["projects"]
    current_ids=set()
    for item in current:
        alias=clean(item.get("project_id"))
        require(alias not in current_ids,f"Duplicate current-works project FK {alias}")
        current_ids.add(alias)
        master_row=by_alias.get(alias)
        require(master_row is not None,f"Missing legacy FK in canonical CSV: {alias}")
        for expected,actual in (
            ("project_id",item.get("map_project_id")),
            ("display_name",item.get("display_name")),
            ("company_project_code",item.get("company_project_code")),
            ("legacy_project_code",item.get("legacy_project_code")),
            ("project_slug",item.get("project_slug")),
        ):
            require(master_row[expected]==clean(actual),
                    f"Identity drift {alias}.{expected}: canonical={master_row[expected]!r}, linked={actual!r}")
    resources=load("ops/data/project-resources.json")["projects"]
    normalized=load("ops/data/resource-catalog-normalized.v0.1.json")["sites"]
    for kind,sites in (("resource source",resources),("normalized resource directory",normalized)):
        seen=set()
        for s in sites:
            alias=clean(s.get("project_id"))
            require(alias not in seen,f"Duplicate {kind} site {alias}")
            seen.add(alias)
            require(alias in current_ids,f"Unmapped {kind} project FK: {alias}")
            row=by_alias[alias]
            if kind=="resource source":
                require(clean(s.get("map_project_id"))==row["project_id"],
                        f"Wrong global project FK in resources: {alias}")
            else:
                require(clean(s.get("project_name"))==row["display_name"],
                        f"Resource library display name drift: {alias}")
    require({x["project_id"] for x in resources}=={x["project_id"] for x in normalized},
            "Resource source and normalized directory site sets differ")
    raw=(ROOT/"ops/data/progress-report-public.v0.2.jsonl").read_text(encoding="utf-8")
    observations=[json.loads(line) for line in raw.splitlines() if line.strip()]
    require(len({x["record_id"] for x in observations})==len(observations),
            "Duplicate progress record identifier")
    for x in observations:
        require(clean(x.get("project_id")) in current_ids,
                f"Orphan progress record {x.get('record_id')!r}")
    return {
        "schema_version":"0.1.0",
        "kind":"DERIVED_READ_ONLY_PROJECT_IDENTITY_INDEX",
        "canonical_master":MASTER,
        "canonical_git_blob_sha":digest,
        "authority_rule":"projects.csv is the sole authoritative source for project names and global identifiers; all website project references are foreign keys.",
        "project_count":len(records),
        "indexed_site_count":len(current_ids),
        "records":records,
    }

def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--write",action="store_true")
    args=ap.parse_args()
    expected=json.dumps(build(),ensure_ascii=False,indent=2)+"\n"
    path=ROOT/INDEX
    if args.check:
        require(path.exists(),"Missing derived identity index "+INDEX)
        require(path.read_text(encoding="utf-8")==expected,
                "Derived identity index has drifted; regenerate from canonical projects.csv")
        print("PROJECT_IDENTITY_PASS: 28 canonical project PKs; 8 indexed site FKs; "
              "all resource/progress links and human names agree with projects.csv")
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(expected,encoding="utf-8")
        print("WROTE: "+INDEX)

if __name__=="__main__": main()
