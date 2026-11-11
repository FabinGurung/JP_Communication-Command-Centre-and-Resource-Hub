#!/usr/bin/env python3
"""Guard the Astam resource ownership transfer; do not resurrect duplicated Pages."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
publisher = (root / "scripts/publish_operations.py").read_text(encoding="utf-8")
test = (root / "scripts/test_ops_publication.py").read_text(encoding="utf-8")
assert 'ASTAM_LIBRARY = LIBRARY + "feasibility/"' in publisher
assert '"feasibility/index.html": ASTAM_LIBRARY' in publisher
assert '"feasibility/buyer-guide/index.html": ASTAM_LIBRARY + "buyer-guide/"' in publisher
assert "u.search = location.search" in publisher, "Backward compatible query forwarding required"
for legacy in ("feasibility/index.html", "feasibility/buyer-guide/index.html"):
    html = (root / legacy).read_text(encoding="utf-8")
    assert "jp-field-desk-library/feasibility/" in html
    assert "location.search" in html
    assert "files-grid" not in html and "domain-chart" not in html, "Original site content not retired"
for old in ("feasibility/buyer-guide/guide.json",
            "ops/data/land-feasibility/astam-village-public.v1.0.json",
            "ops/data/land-feasibility/astam-buyer-guide-public.v1.0.json"):
    assert not (root / old).exists(), "Astam data still duplicated in Operations: " + old
assert "astam_home" in test and "astam_guide" in test
print("ASTAM_RESOURCE_OWNER_REDIRECT_PASS: canonical Library-owned documents; Operations retains redirects only")
