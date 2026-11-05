#!/usr/bin/env python3
"""Privacy and source-of-truth guard for the JP Enterprise Astam feasibility page."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = "ops/data/land-feasibility/astam-village-public.v1.0.json"
PAGE_PATH = "feasibility/index.html"
data = json.loads((ROOT / DATA_PATH).read_text(encoding="utf-8"))
page = (ROOT / PAGE_PATH).read_text(encoding="utf-8")
home = (ROOT / "index.html").read_text(encoding="utf-8")
allowlist = json.loads((ROOT / "ops/control/pages-public-file-allowlist.v1.json").read_text(encoding="utf-8"))["files"]
assert data["kind"] == "PUBLIC_SAFE_FEASIBILITY_PROJECTION"
assert data["publication_scope"] == "PUBLIC_SAFE_ONLY"
assert data["project"]["organization"] == "JP_Enterprise"
assert data["project"]["globally_registered_project_id"] is None
assert data["project"]["exact_coordinates_published"] is False
assert data["project"]["geometry_published"] is False
assert data["project"]["decision_status"] == "NO_PURCHASE_APPROVAL"
assert len(data["checks"]) == 10 and all(x["status"] == "PENDING" for x in data["checks"])
assert len(data["summary"]) == 3 and data["summary"][0]["value"] == 8
assert len(data["resources"]) >= 1
assert all(x["type"] == "permission_gated_folder" and re.fullmatch(
    r"https://drive\.google\.com/drive/folders/[A-Za-z0-9_-]+", x["url"]
) for x in data["resources"])
assert DATA_PATH in allowlist and PAGE_PATH in allowlist
assert 'href="feasibility/"' in home
assert DATA_PATH in page
assert "textContent" in page and "innerHTML" not in page
serialized = json.dumps(data, ensure_ascii=False)
assert not re.search(r"\b(?:28[.]295\d+|83[.]908\d+)\b|[0-9]{2}°[0-9]{1,2}['′]", serialized)
assert not re.search(r"\b[A-Z]{2}-\d{6}\b|@|\+977\d{9,10}", serialized)
assert ".png" not in serialized and ".jpeg" not in serialized and ".jpg" not in serialized
assert "PRIVATE" not in data["publication_scope"]
print("ASTAM_PUBLIC_FEASIBILITY_PASS: 10 pending gates, 8 originals in permission-gated Drive, no exact plot or raw evidence")
