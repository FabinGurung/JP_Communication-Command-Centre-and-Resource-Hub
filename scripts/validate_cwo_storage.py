"""Validate versioned A9-CWO machine contract & Colab notebook syntax without API access."""
import ast
import json
from pathlib import Path

P = Path("ops/control")
pin = json.loads((P / "storage-routing-rules.json").read_text(encoding="utf-8"))
parent = json.loads((P / "daily-communication-web-cycle.json").read_text(encoding="utf-8"))
legacy = json.loads((P / "daily-slack-web-cycle.json").read_text(encoding="utf-8"))
notebook_path = Path("ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb")
notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
assert pin["id"] == "A9-CWO-PIN-001"
assert len(pin["storage"]) == 6 and len(pin["steps"]) == 6
assert pin["control_alias"] == "A9-CWO"
assert {x["home"] for x in pin["storage"]} >= {"GitHub", "Google Drive", "GitHub Pages"}
assert pin["two_channel_discord"]["status"] == "NOTEBOOK_STAGED_UNRUN"
guild = "682670494658330644"
chans = {"1463826087841890417", "1492168056858738809"}
assert pin["two_channel_discord"]["guild_id"] == guild
assert set(pin["two_channel_discord"]["parent_channel_ids"]) == chans
assert parent["operation_name"] == "A9-CWO"
assert {x["provider"] for x in parent["source_providers"]} == {"SLACK", "DISCORD"}
assert set(next(x for x in parent["source_providers"] if x["provider"] == "DISCORD")["channel_ids"]) == chans
assert legacy["alias"] == "SLACK_ADAPTER_OF_A9_CWO"
assert notebook["nbformat"] == 4
codes = [("".join(c["source"]) if isinstance(c["source"], list) else c["source"])
         for c in notebook["cells"] if c["cell_type"] == "code"]
assert len(codes) >= 2
for i, code in enumerate(codes):
    python = "\n".join(ln for ln in code.splitlines() if not ln.lstrip().startswith("%"))
    ast.parse(python, filename=str(notebook_path) + ":cell" + str(i))
source = "\n".join(codes)
for channel in chans:
    assert channel in source
assert "with requests.get(url" in source
assert "with http.get(url" not in source  # no Discord Authorization header to CDN
assert 'BOT_TOKEN = userdata.get("DISCORD_BOT_TOKEN")' in source
assert "MAX_PAGES_PER_SOURCE" in source
assert "state_current.json" in source and "handoff_current.json" in source
assert "hashlib.sha256" in source and "MediaFileUpload" in source
assert "CANDIDATES_JSONL" in source and "RUN_RECEIPTS" in source
assert "INCLUDE_ACTIVE_CHILD_THREADS = True" in source
assert 'horizon = datetime.fromtimestamp(previous_ms/1000, timezone.utc) - timedelta(days=REVISIT_DAYS)' in source
site = Path("controls/storage.html").read_text(encoding="utf-8")
assert "storage-routing-rules.json" in site and "A9-CWO" in site
assert 'href="storage.html"' in Path("controls/index.html").read_text(encoding="utf-8")
pending = Path("ops/data/pending-works.json").read_text(encoding="utf-8")
assert "OPS-PEND-000004" in pending
print("PASS: A9-CWO storage pin, Slack+Discord contract and Colab source syntactically valid")
