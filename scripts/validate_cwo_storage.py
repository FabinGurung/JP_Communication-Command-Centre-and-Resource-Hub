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
# Regression guard: googleapiclient's discovery client uses camelCase parameters.
assert "page_size=" not in source and "page_token=" not in source
assert "pageSize=100" in source and "pageToken=token" in source
assert "httplib2.Http(timeout=120)" in source
assert "AuthorizedHttp(credentials" in source
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
# Immutable notebook creation-date enumeration and exact archival snapshots.
import hashlib
import re
ledger = json.loads(Path("ops/discord/notebook-versions.json").read_text(encoding="utf-8"))
assert ledger["schema_version"] == "1.0.0"
assert ledger["timezone"] == "Asia/Kathmandu"
assert ledger["numbering"] == "YYYYMMDD-NNN"
assert ledger["current_revision"] == "20261009-006"
assert ledger["stable_working_path"] == str(notebook_path)
assert ledger["drive_native_same_id"].startswith("NOT_APPLICABLE")
revisions = ledger["versions"]
assert len(revisions) >= 3
assert len({x["revision"] for x in revisions}) == len(revisions)
assert sum(x["status"] == "CURRENT" for x in revisions) == 1
assert revisions[-1]["status"] == "CURRENT" and revisions[-1]["revision"] == ledger["current_revision"]
assert notebook["metadata"]["a9_cwo_revision"]["version_id"] == ledger["current_revision"]
for entry in revisions:
    date, seq = entry["revision"].split("-")
    assert re.fullmatch(r"\d{8}", date) and re.fullmatch(r"\d{3}", seq)
    assert date == entry["created_date_npt"].replace("-", "")
    artifact_path = Path(entry["archive_path"] or ledger["stable_working_path"])
    assert artifact_path.is_file(), str(artifact_path)
    content = artifact_path.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\x00" + content).hexdigest()
    assert git_blob == entry["git_blob_sha"], entry["revision"]
    if entry["archive_path"]:
        assert entry["archive_path"].startswith(ledger["archive_base"] + "/" + date + "/" + seq)
        assert entry["status"] in {"ARCHIVED_RETROACTIVE", "ARCHIVED_PRE"}
assert pin["notebook_versioning_policy"]["manifest"] == "ops/discord/notebook-versions.json"
assert "notebook-versions.json" in site
assert "20261009-006" == notebook["metadata"]["a9_cwo_revision"]["version_id"]
assert 'progress("Drive: verifying existing A9 Discord archive root")' in source
assert '_HEARTBEAT_STOP.wait(20)' in source
assert 'progress("Discord: BEGIN source' in source
assert 'progress("FAILED source' in source
assert 'progress("FINAL RECEIPT:' in source
assert 'finally:' in source
assert '"Accept-Encoding": "identity"' in source
assert '"Attachment size mismatch, id=%s declared=%d observed=%d "' in source
assert "MEDIA FAILURE DETAIL" in source
# Durable cell identifiers and visible Setup milestones; do not re-number with cell position.
code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
assert [c["id"] for c in code_cells] == ["a9-cwo-c01-setup", "a9-cwo-c02-collector", "a9-cwo-c03-cdn-probe"]
assert "A9-CWO-C01-SETUP" in code_cells[0]["metadata"]["tags"]
assert "A9-CWO-C02-COLLECTOR" in code_cells[1]["metadata"]["tags"]
assert all((f"[A9-CWO C01 SETUP | {i:02d}/06]" in codes[0]) for i in range(1,7))
assert "[A9-CWO C02 COLLECTOR |" in codes[1]
assert "A9-CWO-C03-CDN-PROBE" in code_cells[2]["metadata"]["tags"]
assert "A9-CWO C03 CDN PROBE | 05/05" in codes[2]
assert "diagnostics = [c03_probe(" in codes[2]
assert 'receipt["run_id"]' not in codes[2]  # deliberate: uses handoff match instead
assert "MediaFileUpload" not in codes[2] and "drive.files().create" not in codes[2]
assert "drive.files().update" not in codes[2]
assert "with requests.get(" in codes[2] and "get_media(" in codes[2]
assert {c["id"] for c in notebook["cells"] if c["cell_type"] == "markdown"} >= {"a9-cwo-c01-guide", "a9-cwo-c02-guide", "a9-cwo-c03-guide"}
assert "scripts/test_cwo_media_diagnostics.py" in Path(".github/workflows/daily-ops-branch-preview.yml").read_text(encoding="utf-8")
assert Path("controls/memory-wall.html").exists()
assert 'notebook-versions.json' in Path("controls/memory-wall.html").read_text(encoding="utf-8")
assert 'memory-wall.html' in Path("controls/index.html").read_text(encoding="utf-8")
assert 'memory-wall.html' in Path("controls/storage.html").read_text(encoding="utf-8")

print("PASS: source-date enumerations, immutable archive blobs, stable Colab link and current notebook revision")

print("PASS: A9-CWO storage pin, Slack+Discord contract and Colab source syntactically valid")
