"""Offline invariants for A9-CWO's strictly bounded, non-original derivative pilot.

This verifies notebook structure and guards. It does not claim a live Discord/Drive test,
that C04 has run, or that derivative bytes satisfy the original-attachment debt.
"""
import ast
import json
from pathlib import Path

notebook = json.loads(Path(
    "ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb"
).read_text(encoding="utf-8"))
c04 = next(cell for cell in notebook["cells"]
           if cell.get("id") == "a9-cwo-c04-derivative-pilot")
code = "".join(c04["source"])
tree = ast.parse(code, filename="C04 BOUNDED DERIVATIVE PILOT")
manifest = json.loads(Path("ops/discord/notebook-versions.json").read_text(encoding="utf-8"))

# C04 was introduced in revision 007 and must remain unchanged as the daily
# notebook advances to later revisions. Verify both ledger identity and lineage.
assert manifest["current_revision"] == notebook["metadata"]["a9_cwo_revision"]["version_id"]
assert manifest["current_revision"] >= "20261009-007"
c04_lineage = next(v for v in manifest["versions"] if v["revision"] == "20261009-007")
assert c04_lineage["status"] == "ARCHIVED_PRE"
assert c04_lineage["git_blob_sha"] == "cb8a4228ab4e9c59ffbfab680aaaac37d4734e22"
assert c04_lineage["archive_path"].endswith("007__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_SEVEN_DAY_DAILY_INDEX.ipynb")
assert "PROVIDER_DERIVATIVE_NOT_ORIGINAL" in code
assert "UNVERIFIED_ORIGINAL_MEDIA_FAILURE_OPEN" in code
assert "ONE_DERIVATIVE_SAVED_OR_READBACK_VERIFIED" in code
assert "original_certified\": False" in code
assert "collector_cursors_advanced\": False" in code
assert "frozen_receipt_changed\": False" in code
assert "DERIVATIVE_BYTES" in code
assert "RUN_RECEIPTS" in code
assert "c04_read_bytes" in code
assert "25 * 1024 * 1024" in code
assert "digest != source_info.get(\"sha256\")" in code
assert "len(raw) != source_info.get(\"observed_bytes\")" in code
assert 'parts.hostname != "cdn.discordapp.com"' in code
assert "C04 requires C01 SETUP then C03 CDN PROBE" in code
assert "state_current.json" not in code
assert "handoff_current.json" not in code
assert "drive.files().update" not in code
assert "drive.files().delete" not in code
assert "BOT_TOKEN" in code  # checked in-memory; never printed or persisted

image_downloads = [
    node for node in ast.walk(tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and node.func.attr == "get"
    and isinstance(node.func.value, ast.Name)
    and node.func.value.id == "requests"
]
assert len(image_downloads) == 1, "C04 must GET exactly one source variant"
drive_creates = [
    node for node in ast.walk(tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and node.func.attr == "create"
    and isinstance(node.func.value, ast.Call)
    and isinstance(node.func.value.func, ast.Attribute)
    and node.func.value.func.attr == "files"
]
assert len(drive_creates) == 3, "At most folder, derivative, and receipt creation"
assert "else:" in code and "if prior:" in code
print("PASS: C04 bounded one-JPEG private derivative policy; original certification remains open")
