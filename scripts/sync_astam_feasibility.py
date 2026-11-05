#!/usr/bin/env python3
"""A9 public-only Astam projection from one immutable live Google Sheet ID.

Google Drive holds private originals; the source Sheet owns editable classified
facts. An allowlist and explicit per-row approval are both required for
publication. Never write secrets, source Sheet rows, exact parcel data or
personal correspondence to GitHub Pages.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/"ops/control/astam-sheet-source.v1.json"
OUT=ROOT/"ops/data/land-feasibility/astam-village-public.v1.0.json"
STATUSES={"PENDING","IN_REVIEW","BLOCKED","ON_HOLD"}
PUBLIC_KEYS={"title","organization","area_general","phase","concept","decision","updated_date"}
SAFE_DRIVE=re.compile(r"^https://drive\.google\.com/(?:drive/folders/|file/d/)[A-Za-z0-9_-]+(?:/view)?$")
SENSITIVE=re.compile(r"@|(?:\+977[\d -]{7,})|(?:28[.]29\d+|83[.]90\d+)|(?:\b(?:price|ask|offer|sale|valuation)\s*[:=]\s*(?:NPR|Rs)[\d,]+)",re.I)
class AdmissionError(Exception):pass

def fail(message):
    raise AdmissionError(message)

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def tab_rows(session,spreadsheet_id,tab):
    a1="'"+tab.replace("'","''")+"'!A1:J100"
    url="https://sheets.googleapis.com/v4/spreadsheets/"+quote(spreadsheet_id,safe="")+"/values/"+quote(a1,safe="")
    response=session.get(url,params={"valueRenderOption":"FORMATTED_VALUE"},timeout=30)
    response.raise_for_status()
    rows=response.json().get("values",[])
    if not rows:fail("Empty or unreadable source tab "+tab)
    cols=[str(v).strip().lower() for v in rows[0]]
    if len(cols)!=len(set(cols)):fail("Duplicate columns in "+tab)
    return [{key: str(row[idx]).strip() if idx<len(row) else "" for idx,key in enumerate(cols)} for row in rows[1:] if any(str(v).strip() for v in row)]

def expected(rows,required,limit,tab):
    if len(rows)>limit:fail(tab+" exceeds expected maximum")
    for x in rows:
        if not required.issubset(x):fail(tab+" missing required header(s)")
    return rows

def admit(rows,config,original):
    bytab=rows
    meta=expected(bytab["04_PUBLIC_FIELDS"],{"key","value","public"},50,"public fields")
    published={}
    for r in meta:
        key=r["key"]
        if r["public"].upper()=="YES" and key in PUBLIC_KEYS:
            value=r["value"]
            if SENSITIVE.search(value):fail("Restricted content in admitted public field")
            published[key]=value
    if set(published)!=PUBLIC_KEYS:fail("Missing approved public-field keys")
    if published["organization"]!="JP_Enterprise":fail("Organization ownership mismatch")
    if published["decision"] not in {"HOLD","ON_HOLD","PENDING_REVIEW"}:fail("Unapproved acquisition decision")
    source_checks=expected(bytab["01_DUE_DILIGENCE"],{"check_id","domain","check_name","status","evidence_required","publication_approved"},24,"checks")
    checks=[];ids=set()
    for row in source_checks:
        if row["publication_approved"].upper()!="YES":continue
        key=row["check_id"]
        if key in ids or not re.fullmatch("AST-[0-9]{2}",key):fail("Bad or duplicate check key")
        ids.add(key)
        if row["status"] not in STATUSES:
            fail("Unsupported status: evidence/approval required before a check may be certified")
        checks.append({"id":key,"label":row["check_name"],"group":row["domain"],"status":row["status"],"evidence":"Required: "+row["evidence_required"]})
    if len(checks)!=10:fail("Ten review checks must remain explicit")
    observed=expected(bytab["02_OBSERVATIONS"],{"observation_id","evidence_type","subject","public_summary","publication_approved"},50,"observations")
    observations=[]
    for r in observed:
        if r["publication_approved"].upper()!="YES":continue
        observations.append({"label":r["subject"],"detail":r["public_summary"],"kind":r["evidence_type"]})
    approved=expected(bytab["03_CLIENT_DOCUMENTS"],{"resource_id","class","client_label","drive_url","show_on_public_page","access_mode"},80,"client documents")
    resources=[]; resource_ids=set()
    for r in approved:
        if r["show_on_public_page"].upper()!="YES":continue
        if r["resource_id"] in resource_ids or not SAFE_DRIVE.fullmatch(r["drive_url"]):
            fail("Duplicate document or unapproved destination")
        resource_ids.add(r["resource_id"])
        if r["access_mode"]!="DRIVE_PERMISSION":fail("Original file link not permission-gated")
        resources.append({"resource_id":r["resource_id"],"label":r["client_label"],"category":r["class"],"url":r["drive_url"],"access_mode":"DRIVE_PERMISSION_GATED"})
    if not resources:fail("Client document list is empty")
    groups=Counter(x["group"] for x in checks)
    status=Counter(x["status"] for x in checks)
    out=copy.deepcopy(original)
    out["schema_version"]="1.1.0"
    out["kind"]="PUBLIC_SAFE_FEASIBILITY_PROJECTION"
    out["publication_scope"]="PUBLIC_SAFE_ONLY"
    out["as_of"]=published["updated_date"]
    out["project"]["title"]=published["title"]
    out["project"]["organization"]=published["organization"]
    out["project"]["location_general"]=published["area_general"]
    out["project"]["phase"]=published["phase"]
    out["project"]["use_concept"]=published["concept"]
    out["project"]["decision_status"]="NO_PURCHASE_APPROVAL"
    out["project"]["exact_coordinates_published"]=False
    out["project"]["geometry_published"]=False
    out["checks"]=checks
    out["observations"]=observations
    out["resources"]=resources
    out["metrics"]={
        "check_count":len(checks),
        "approved_or_accepted":0,
        "open_checks":len(checks),
        "check_domain_counts":dict(sorted(groups.items())),
        "status_counts":dict(sorted(status.items())),
        "source_kind":"COUNT_OF_REVIEW_ROWS_NOT_A_PHYSICAL_LAND_MEASUREMENT"
    }
    out["source_sync"]={
        "mode":"GOOGLE_SHEETS_ACTIONS_READ",
        "source_facts":"PERMISSION_GATED_NATIVE_GOOGLE_SHEET",
        "validation":"PUBLIC_ALLOWLIST_AND_SOURCE_READBACK",
        "source_id_retained":True,
        "publication_time_note":"GitHub Actions refresh on registered publishing branch pushes or manually dispatched runs; editing Sheets alone does not trigger a run."
    }
    check_payload(out)
    return out

def check_payload(v):
    if v.get("publication_scope")!="PUBLIC_SAFE_ONLY":fail("Wrong scope")
    project=v.get("project",{})
    if project.get("exact_coordinates_published") is not False or project.get("geometry_published") is not False:fail("Private geometry")
    checks=v.get("checks",[])
    if len(checks)!=10 or len({x["id"] for x in checks})!=len(checks):fail("Check table invalid")
    if any(x["status"] not in STATUSES for x in checks):fail("Unsupported certified approval")
    res=v.get("resources",[])
    if not all(SAFE_DRIVE.fullmatch(x["url"]) for x in res):fail("Unsafe source URL")
    if SENSITIVE.search(str(project.get("title",""))+str(project.get("location_general",""))):fail("Privacy leak")
    if "private_messages" in v or "negotiated_rate" in v:fail("Private data key")
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--validate-bundle",action="store_true")
    ap.add_argument("--refresh",action="store_true")
    ap.add_argument("--require-live",action="store_true")
    args=ap.parse_args()
    config=load_json(CFG)
    baseline=load_json(OUT)
    check_payload(baseline)
    if args.validate_bundle:
        print("ASTAM_PUBLIC_BUNDLE_PASS")
        return
    if not args.refresh:
        print("ASTAM_BASELINE_QA_PASS")
        return
    try:
        import google.auth
        from google.auth.transport.requests import AuthorizedSession
        creds,_=google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
        session=AuthorizedSession(creds)
        tabs={name:tab_rows(session,config["live_workbook_id"],name) for name in (
            "01_DUE_DILIGENCE","02_OBSERVATIONS","03_CLIENT_DOCUMENTS","04_PUBLIC_FIELDS")}
        out=admit(tabs,config,baseline)
        OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("ASTAM_LIVE_SHEET_READBACK_AND_PUBLIC_PROJECTION_PASS")
    except Exception as exc:
        if args.require_live:raise SystemExit("ASTAM_REQUIRED_LIVE_REFRESH_FAILED: "+type(exc).__name__) from None
        # Preserve the committed, already privacy-reviewed snapshot.
        print("::warning::ASTAM_LIVE_SHEET_UNAVAILABLE; prior approved public projection retained",flush=True)
        if os.getenv("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:
                f.write("\nAstam source refresh: NOT VERIFIED; approved last-reviewed snapshot retained.\n")
    check_payload(load_json(OUT))

if __name__=="__main__":
    try:main()
    except AdmissionError as exc:raise SystemExit("ASTAM_PUBLICATION_HOLD: "+str(exc)) from None
