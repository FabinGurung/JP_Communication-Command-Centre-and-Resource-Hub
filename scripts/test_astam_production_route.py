#!/usr/bin/env python3
"""Guard public Astam route in the canonical production deployment."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
page = root / "feasibility/index.html"
projection = root / "ops/data/land-feasibility/astam-village-public.v1.0.json"
home = (root / "index.html").read_text(encoding="utf-8")
resources = (root / "resources/index.html").read_text(encoding="utf-8")
html = page.read_text(encoding="utf-8")
public = json.loads(projection.read_text(encoding="utf-8"))
assert 'href="feasibility/"' in home, "Homepage Astam link missing"
assert 'href="../feasibility/"' in resources, "Resources Astam link missing"
assert "../ops/data/land-feasibility/astam-village-public.v1.0.json" in html, "Client data URL missing"
assert "files-grid" in html and "domain-chart" in html, "Client presentation incomplete"
assert "buyer-guide" in html and "dashboard-layout" in html and "right-rail" in html
assert "../ops/data/land-feasibility/astam-buyer-guide-public.v1.0.json" in html
buyer = json.loads((root / "ops/data/land-feasibility/astam-buyer-guide-public.v1.0.json").read_text(encoding="utf-8"))
assert buyer["kind"] == "PUBLIC_GENERAL_BUYER_GUIDE"
assert buyer["source_registry"]["tab"] == "06_BUYER_CHECKLIST"
assert len(buyer["items"]) == 30 and len({row["item_id"] for row in buyer["items"]}) == 30
assert all(row["publication_approved"] == "YES" for row in buyer["items"])
assert "innerHTML" not in html, "Do not inject externally supplied HTML"
assert public["kind"] == "PUBLIC_SAFE_FEASIBILITY_PROJECTION"
assert public["publication_scope"] == "PUBLIC_SAFE_ONLY"
assert public["project"]["organization"] == "JP_Enterprise"
assert public["project"]["exact_coordinates_published"] is False
assert public["project"]["geometry_published"] is False
assert public["project"]["decision_status"] == "NO_PURCHASE_APPROVAL"
assert public["project"]["globally_registered_project_id"] is None
assert len(public["checks"]) == 10
assert all(c["status"] in {"PENDING","ON_HOLD","BLOCKED","IN_REVIEW"} for c in public["checks"])
assert len(public["resources"]) == 6
for r in public["resources"]:
    assert r["access_mode"] == "DRIVE_PERMISSION_GATED"
    assert re.fullmatch(r"https://drive\.google\.com/(?:file/d/|drive/folders/)[A-Za-z0-9_-]+(?:/view)?",r["url"])
text = json.dumps(public, ensure_ascii=False)
assert not re.search(r"\b(?:28\.29\d+|83\.90\d+)\b|Naren Gurung|90 lakh|50 lakh", text, re.I)
print("ASTAM_MAIN_PAGES_ROUTE_PASS: Production contains reviewed client page and JSON, safe navigation, no exact plot geometry")
