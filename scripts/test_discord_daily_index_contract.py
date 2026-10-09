#!/usr/bin/env python3
"""Offline executable C05 contract test with synthetic, private-like Drive files.

No Discord token, real Discord API, Google Drive network, personal data or site facts.
Confirms exact source readback, immutable pointer-only JSONL, date partitions,
idempotent same-run index creation, and older-window fail-closed behavior.
"""
import ast
import contextlib
import hashlib
import io
import json
import pathlib
import re
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
NB = ROOT / "ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb"
ROW_SCHEMA = ROOT / "ops/discord/schemas/daily-message-index-v1.schema.json"
MAN_SCHEMA = ROOT / "ops/discord/schemas/daily-run-index-manifest-v1.schema.json"


def canonical(x):
    return (json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def check(cond, why):
    if not cond:
        raise AssertionError(why)


def assert_schema(doc, spec):
    for name in spec["required"]:
        check(name in doc, "Missing required schema property: " + name)
    check(set(doc).issubset(spec["properties"]), "Unexpected schema property")
    for k, field in spec["properties"].items():
        if "const" in field and k in doc:
            check(doc[k] == field["const"], "Schema constant mismatch: " + k)
    check(not any(k in doc for k in ("text_original", "content", "token", "authorization")), "Raw content leaked to index")


class PrivateDriveFixture:
    def __init__(self, run_id):
        self.run_id = run_id
        self.files = {}
        self.folders = {("ROOT", "A9_CWO_DAILY_TWO_CHANNELS"): "PRIVATE_RUN_ROOT"}
        self.name_index = {}
        self.writes = 0

    def store(self, key, name, parent, data):
        self.files[key] = data
        self.name_index[(parent, name)] = key
        return key

    def children(self, parent, name):
        key = self.name_index.get((parent, name))
        return {"id": key} if key else None

    def directory(self, parent, name):
        key = (parent, name)
        if key not in self.folders:
            self.folders[key] = "synthetic_folder_" + str(len(self.folders))
        return self.folders[key]

    def byte_readback(self, key):
        return self.files[key]

    def save_bytes(self, parent, name, contents, mime="application/json"):
        existing = self.children(parent, name)
        sha = hashlib.sha256(contents).hexdigest()
        if existing:
            check(self.byte_readback(existing["id"]) == contents, "Reused path has conflicting bytes")
            return {"id": existing["id"], "sha256": sha, "bytes": len(contents), "reused": True}
        self.writes += 1
        key = "synthetic_drive_file_" + str(self.writes).zfill(3)
        self.store(key, name, parent, contents)
        return {"id": key, "sha256": sha, "bytes": len(contents), "reused": False}


def fixtures():
    run_id = "20261010T220000Z"
    f = PrivateDriveFixture(run_id)
    cases = [
        ("333333333333333333", "2026-10-08T22:45:00+00:00", "SYNTHETIC_PRIVATE_NEVER_PUBLISH_1"),
        ("444444444444444444", "2026-10-09T20:10:00+00:00", "SYNTHETIC_PRIVATE_NEVER_PUBLISH_2"),
    ]
    raw = []
    candidate = []
    for mid, timestamp, msg in cases:
        raw.append({"id": mid, "timestamp": timestamp, "content": msg, "attachments": [{"id": "555555555555555555"}]})
        candidate.append({"provider": "DISCORD", "guild_id": "123456789012345678",
                          "parent_channel_id": "111111111111111111", "channel_id": "222222222222222222",
                          "message_id": mid, "created_at": timestamp, "text_original": msg,
                          "attachment_ids": ["555555555555555555"], "fact_admission": "NEEDS_RECONCILIATION"})
    rb, cb = b"".join(canonical(x) for x in raw), b"".join(canonical(x) for x in candidate)
    f.store("synthetic_raw_source_file", "raw.jsonl", "PRIVATE_RUN_ROOT", rb)
    f.store("synthetic_cand_source_file", "candidates.jsonl", "PRIVATE_RUN_ROOT", cb)
    receipt = {
        "run_id": run_id, "guild_id": "123456789012345678",
        "scan_rule": "ROLLING_SEVEN_DAYS_WITH_CATCHUP_EXTENSION",
        "replay_lookback_days": 7, "status": "PARTIAL",
        "collection_started_at": "2026-10-10T22:00:00+00:00",
        "target_parent_channels": ["111111111111111111", "999999999999999999"],
        "sources": [{"channel_id": "222222222222222222", "parent_channel_id": "111111111111111111",
                     "status": "PARTIAL_ATTACHMENTS", "new_or_changed_messages": 2,
                     "raw_jsonl": {"id": "synthetic_raw_source_file", "sha256": hashlib.sha256(rb).hexdigest()},
                     "candidate_jsonl": {"id": "synthetic_cand_source_file", "sha256": hashlib.sha256(cb).hexdigest()}}]
    }
    f.store("synthetic_immutable_receipt", "C02.json", "PRIVATE_RUN_ROOT", canonical(receipt))
    f.store("synthetic_handoff_current", "handoff_current.json", "PRIVATE_RUN_ROOT",
            canonical({"run_id": run_id, "receipt_file_id": "synthetic_immutable_receipt"}))
    f.store("synthetic_state_current", "state_current.json", "PRIVATE_RUN_ROOT", b'{"highwater":"UNTOUCHED"}\n')
    return f


def main():
    nb = json.loads(NB.read_text("utf-8"))
    check(nb["metadata"]["a9_cwo_revision"]["version_id"] == "20261009-008", "Unexpected notebook revision")
    cells = {cell["id"]: "".join(cell["source"]) for cell in nb["cells"]}
    for name in ("a9-cwo-c02-collector", "a9-cwo-c03-cdn-probe", "a9-cwo-c04-derivative-pilot", "a9-cwo-c05-daily-index"):
        ast.parse(cells[name], filename=name)
    check("REVISIT_DAYS = 7" in cells["a9-cwo-c01-setup"], "Daily revisit must be seven days")
    check("BACKFILL_OVERLAP_DAYS = 1" in cells["a9-cwo-c01-setup"], "Catch-up safety overlap missing")
    check("horizon = min(horizon, catchup_start)" in cells["a9-cwo-c02-collector"], "Missed-day catch-up rule absent")
    check("DAILY_INDEX_JSONL" in cells["a9-cwo-c05-daily-index"], "Private date partitions absent")

    drive = fixtures()
    ctx = {
        "__name__": "__test__", "drive": object(), "GUILD_ID": "123456789012345678",
        "ROOT_DRIVE_ID": "ROOT", "RUN_FOLDER_NAME": "A9_CWO_DAILY_TWO_CHANNELS",
        "TZ": ZoneInfo("Asia/Kathmandu"), "children": drive.children,
        "directory": drive.directory, "byte_readback": drive.byte_readback,
        "save_bytes": drive.save_bytes, "jsonbytes": canonical,
    }
    src = compile(cells["a9-cwo-c05-daily-index"], "C05", "exec")
    logs = io.StringIO()
    with contextlib.redirect_stdout(logs):
        exec(src, ctx)
    check("[A9-CWO C05 DAILY INDEX | 06/06] PASS" in logs.getvalue(), "No final pass marker")
    partitions = [(parent, name) for (parent, name) in drive.name_index if name.endswith(".jsonl") and "DAY_INDEX__" in name]
    check(len(partitions) == 2, "Cross-Nepal-midnight examples must produce two date partitions")
    indexed = [json.loads(x) for parent, name in partitions for x in drive.files[drive.name_index[(parent, name)]].splitlines()]
    check(len(indexed) == 2 and {x["date_npt"] for x in indexed} == {"2026-10-09", "2026-10-10"}, "NPT day labels wrong")
    schema = json.loads(ROW_SCHEMA.read_text("utf-8"))
    for row in indexed:
        assert_schema(row, schema)
        check(row["attachments_original_certification"] == "SOURCE_PARTIAL", "Failed originals falsely certified")
        check(row["raw_line_1_based"] > 0 and row["candidate_line_1_based"] > 0, "Missing source line pointer")
    manifest_key = next(key for (parent, name), key in drive.name_index.items() if "DAILY_INDEX_MANIFEST" in name)
    manifest = json.loads(drive.files[manifest_key])
    assert_schema(manifest, json.loads(MAN_SCHEMA.read_text("utf-8")))
    check(manifest["rows_indexed"] == 2 and manifest["source_receipt_status"] == "PARTIAL", "Manifest count/state")
    check(manifest["media_completeness"] == "PARTIAL", "Source media mismatch erased")
    check(b"SYNTHETIC_PRIVATE_NEVER_PUBLISH" not in b"".join(drive.files[drive.name_index[x]] for x in partitions), "Raw message text was duplicated in day index")
    state_before, writes_before = drive.files["synthetic_state_current"], drive.writes

    with contextlib.redirect_stdout(io.StringIO()):
        exec(src, ctx)
    check(drive.writes == writes_before, "Repeated C05 run created duplicate immutable objects")
    check(drive.files["synthetic_state_current"] == state_before, "C05 modified the old verified cursor")

    old_receipt = json.loads(drive.files["synthetic_immutable_receipt"])
    old_receipt["scan_rule"] = "OLDER_TWO_DAY_RULE"
    drive.files["synthetic_immutable_receipt"] = canonical(old_receipt)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(src, ctx)
    except RuntimeError as exc:
        check("older window" in str(exc), "Wrong rejection for outdated C02 receipt")
    else:
        raise AssertionError("C05 accepted a non-seven-day receipt")
    print("PASS: notebook syntax for C02/C03/C04/C05")
    print("PASS: seven-day replay and catch-up policy")
    print("PASS: SHA-readback, pointer-only private indexes, Nepal day partitions, manifest PARTIAL")
    print("PASS: exact same-run idempotence; old state unmodified; older-window refused")


if __name__ == "__main__":
    main()
