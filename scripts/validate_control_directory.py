import json
from pathlib import Path
d=json.loads(Path("ops/control/control-tower-directory.json").read_text(encoding="utf-8"))
assert d["schema_version"]=="0.1.0" and d["status"]=="SOURCE_LINK_INDEX_PILOT"
assert d["freshness"]=="MANUAL_SNAPSHOT_NOT_LIVE_DRIVE_SYNC"
r=d["records"]
assert len(r)>=10 and len({x["id"] for x in r})==len(r)
assert {"CONTROL","MAIN","SLACK","GITHUB"} <= {x["group"] for x in r}
assert any(x["name"]=="Main Library" and x["url"].startswith("https://docs.google.com/spreadsheets/") for x in r)
assert all(x["url"].startswith("https://") and x["version"] and x["note"] for x in r)
html=Path("controls/index.html").read_text(encoding="utf-8")
assert "control-tower-directory.json" in html and "A9-SWO" in html
assert 'href="controls/"' in Path("index.html").read_text(encoding="utf-8")
assert "OPS-PEND-000003" in Path("ops/data/pending-works.json").read_text(encoding="utf-8")
print("PASS: control directory indexed, linked, traceable and explicitly not live-synced")
