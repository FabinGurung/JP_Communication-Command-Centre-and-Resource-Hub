#!/usr/bin/env python3
"""Validate the permission-gated A/B/C public document pointer projection."""
import json, re
from pathlib import Path
P=Path(__file__).resolve().parents[1]
d=json.loads((P/"ops/data/client-document-packets.v1.json").read_text(encoding="utf-8"))
assert d["schema_version"]=="1.0.0" and d["record_purpose"]=="PUBLIC_SAFE_DOCUMENT_POINTERS_ONLY"
projects=d["projects"];documents=d["documents"]
assert len(projects)==1 and projects[0]["project_id"]=="PRJ-000029"
assert projects[0]["map_master_status"]=="NOT_ENROLLED_IN_PUBLIC_PROJECT_MASTER"
assert len(documents)==6
assert len({x["document_id"] for x in documents})==6
assert len({x["drive_file_id"] for x in documents})==6
assert {(x["role"],x["language"]) for x in documents}=={("A","en"),("A","ne"),("B","source"),("B","ne"),("C","en"),("C","ne")}
for x in documents:
    assert x["project_id"]=="PRJ-000029" and x["pages"]>0
    assert re.fullmatch(r"[A-Za-z0-9_-]+",x["drive_file_id"])
    assert x["drive_url"]==f'https://drive.google.com/file/d/{x["drive_file_id"]}/view'
    assert "SIGNED" not in x["kind"] and x["approval"]
assert next(x for x in documents if x["document_id"]=="BASANTI-B-ORIGINAL")["pages"]==21
assert next(x for x in documents if x["document_id"]=="BASANTI-B-NE-REFERENCE")["kind"]=="TRANSLATED_REFERENCE_ONLY"
page=(P/"resources/project-documents.html").read_text(encoding="utf-8")
listing=(P/"resources/index.html").read_text(encoding="utf-8")
assert "client-document-packets.v1.json" in page and "drive_url" in page
assert 'id="preview"' in page and 'id="document-list"' in page
assert "project-documents.html?project=PRJ-000029" in listing
assert "progress-report-public" not in page
assert "57,50,000" not in page and "57,50,000" not in json.dumps(d)
print("CLIENT_DOCUMENT_PACKETS_PASS: 6 exact Drive links, 3 document families, bilingual versions, gated preview, original B unchanged")
