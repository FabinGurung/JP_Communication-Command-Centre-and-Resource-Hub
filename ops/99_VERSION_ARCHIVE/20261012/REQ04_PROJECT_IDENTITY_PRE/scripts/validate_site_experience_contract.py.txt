#!/usr/bin/env python3
"""Machine-checked separations: map/checklist, progress publication, resource originals and developer UI."""
from pathlib import Path
from collections import Counter
import csv, json, re, subprocess
ROOT=Path(__file__).resolve().parent.parent
def read(p): return (ROOT/p).read_text(encoding="utf-8")
def load(p): return json.loads(read(p))
def rows(p): return [json.loads(line) for line in read(p).splitlines() if line.strip()]
def require(x, msg):
    if not x: raise SystemExit("SITE_EXPERIENCE_CONTRACT_FAIL: "+msg)
contract=load("ops/control/site-experience-and-pipeline-isolation.v0.1.json")
require(contract["schema_version"]=="0.1.0","control contract version")
current=load("ops/data/current-works.json")
site_ids={s["project_id"] for s in current["projects"]}
raw=load("ops/data/project-resources.json")
normalized=load("ops/data/resource-catalog-normalized.v0.1.json")
source={r["resource_id"]: (p["project_id"],r) for p in raw["projects"] for r in p["resources"]}
files=[r for p in normalized["sites"] for r in p["files"]]
require(len(source)==len(files),"normalized directory must preserve every source resource")
require(len(set(r["resource_id"] for r in files))==len(files),"duplicate normalized resource ID")
for r in files:
    require(r["resource_id"] in source,"normalized resource has no source row")
    pid, s=source[r["resource_id"]]
    require(r["project_id"]==pid and pid in site_ids,"wrong resource-to-project FK")
    require(r["source_drive_file_id"]==s["drive_file_id"],"source Drive ID was rewritten")
    require(r["source_drive_url"]==s["drive_url"],"source URL was rewritten")
    require(r["source_registry_label"]==s["display_name"],"original registry caption lost")
    require(r["original_drive_filename"] is not None or not r["original_filename_verified"],"original filename lacks provenance")
    require(r["sort_priority"] in (1,2,3,4),"invalid resource sorting tier")
    require(r["approval_status"]=="UNVERIFIED_AS_CURRENT_ISSUE","drawing incorrectly certified")
progress=rows("ops/data/progress-report-public.v0.2.jsonl")
require(len(set(r["record_id"] for r in progress))==len(progress),"duplicate progress record")
for r in progress:
    require(r["project_id"] in site_ids,"progress-to-project FK mismatch")
    require(r["record_kind"] in ("FIELD_REPORTED_OBSERVATION","SOURCE_LINKED_PENDING_COMMUNICATION","PREVIOUS_UI_DAILY_ROUTINE_TEMPLATE"),"unknown historical evidence type")
    require(not r.get("engineer_accepted") and not r.get("quantity_verified"),"unsupported engineering/material acceptance")
    u=r.get("source_url") or ""
    if u.startswith("https://discord.com/"): require(r.get("source_provider")=="DISCORD","Discord evidence misattributed")
    if u.startswith("https://jp09.slack.com/"): require(r.get("source_provider")=="SLACK","Slack evidence misattributed")
    if r["record_kind"]=="PREVIOUS_UI_DAILY_ROUTINE_TEMPLATE":require(not r.get("work_performed_verified"),"routine reminder promoted to completed work")
homepage=read("index.html")
for url in ('href="map.html"','href="site-operations.html"','href="site-operations/history.html"','href="resources/"','href="workspace/"','href="guide/"'):
    require(url in homepage,"missing main-page link "+url)
require('id="field-hero-canvas"' in homepage and 'assets/js/hero-field.js' in homepage,"interactive home hero unavailable")
checklist=read("site-operations.html")
require("JPAEC:diy-checklist:v1:" in checklist,"personal checklist storage contract changed")
for forbidden in ("progress-report-public.v0.2.jsonl","progress-history-public.v0.1.jsonl","resource-catalog-normalized.v0.1.json","site-execution-questions.v0.1.json"):
    require(forbidden not in checklist,"daily personal checklist ingests "+forbidden)
resource_html=read("resources/index.html")
require("resource-catalog-normalized.v0.1.json" in resource_html and "progress-report-public" not in resource_html,"resource page data-isolation violation")
history=read("site-operations/history.html")
require("progress-report-public.v0.2.jsonl" in history and "JPAEC:diy-checklist:v1:" not in history,"progress page data-isolation violation")
workspace=read("workspace/index.html")
require("developer-links.v0.1.json" in workspace and 'id="live-project-grid"' not in workspace,"developer workspace must not display project operations data")
mapjs=read("assets/js/app.js")
require("personalChecklistForMap" in mapjs and "map-technical" in mapjs,"map missing on-demand checklist and compact technical detail")
require("ops/data/progress-report-public" not in mapjs,"map imports entire historic progress stream")
# Prevent an individual commit from modifying multiple independent DATA domains.
try:
    changed=subprocess.check_output(["git","diff-tree","--no-commit-id","--name-only","-r","HEAD"],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).splitlines()
except (OSError,subprocess.CalledProcessError):changed=[]
lanes=set()
for p in changed:
    if p.startswith("ops/data/progress-report-public") or p.startswith("ops/data/progress-history-public"):lanes.add("progress_publishing")
    if p.startswith("ops/data/resource-catalog-normalized") or p.startswith("ops/data/project-resources"):lanes.add("resource_library")
    if p.startswith("ops/data/site-daily-checklist") or p=="site-operations.html":lanes.add("engineer_checklist")
require(len(lanes)<=1,"one commit modified unrelated data domains: "+",".join(sorted(lanes)))
print("SITE_EXPERIENCE_CONTRACT_PASS: "+str(len(site_ids))+" site FKs, "+str(len(files))+" preserved file identities, "+str(len(progress))+" source-attributed history records; no pipeline cross-writes")
