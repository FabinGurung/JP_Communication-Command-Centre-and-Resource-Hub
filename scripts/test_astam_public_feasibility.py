#!/usr/bin/env python3
"""Static QA for the public-safe, source-backed Astam client portal."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data_path="ops/data/land-feasibility/astam-village-public.v1.0.json"
page_path="feasibility/index.html"
data=json.loads((ROOT/data_path).read_text(encoding="utf-8"))
page=(ROOT/page_path).read_text(encoding="utf-8")
home=(ROOT/"index.html").read_text(encoding="utf-8")
allowed=json.loads((ROOT/"ops/control/pages-public-file-allowlist.v1.json").read_text(encoding="utf-8"))["files"]
source=json.loads((ROOT/"ops/control/astam-sheet-source.v1.json").read_text(encoding="utf-8"))
assert data["kind"]=="PUBLIC_SAFE_FEASIBILITY_PROJECTION"
assert data["publication_scope"]=="PUBLIC_SAFE_ONLY"
assert data["project"]["organization"]=="JP_Enterprise"
assert data["project"]["globally_registered_project_id"] is None  # do not imply allocated ID
assert data["project"]["exact_coordinates_published"] is False
assert data["project"]["geometry_published"] is False
assert data["project"]["decision_status"]=="NO_PURCHASE_APPROVAL"
assert len(data["checks"])==10
assert all(x["status"] in {"PENDING","IN_REVIEW","BLOCKED","ON_HOLD"} for x in data["checks"])
assert int(data["summary"][0]["value"])==8
assert len(data["resources"])==6
assert all(x["access_mode"]=="DRIVE_PERMISSION_GATED" for x in data["resources"])
assert all(re.fullmatch(r"https://drive\.google\.com/(?:file/d/|drive/folders/)[A-Za-z0-9_-]+(?:/view)?",x["url"]) for x in data["resources"])
assert data_path in allowed and page_path in allowed
assert 'href="feasibility/"' in home
assert data_path in page
assert "textContent" in page and "innerHTML" not in page
assert source["authoritative_live_id_unchanged"] is True
assert source["live_workbook_id"] and source["source_version"]=="V000001"
assert "sync_astam_feasibility.py" in (ROOT/".github/workflows/daily-ops-branch-preview.yml").read_text(encoding="utf-8")
assert not re.search(r"(?:28[.]29\d+|83[.]90\d+|\b\d{2}°\d{1,2}['′])",json.dumps(data))
assert not re.search(r"\+977\d+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",str(data))
assert not any(f in json.dumps(data) for f in ["IMG_0101.png","IMG_0102.png","IMG_0103.png","Naren Gurung"])
print("ASTAM_CLIENT_SITE_PRIVACY_AND_LINK_QA_PASS")
