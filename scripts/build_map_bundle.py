#!/usr/bin/env python3
"""Build one deterministic Pages payload from the reviewed Sheet projections.

This stage never authenticates to Drive and never reads private source workbooks.
Source ingestion and public admission precede this build stage.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = "ops/data/map-data.v1.json"

def build(root=ROOT):
    config = json.loads((root / "map-config.json").read_text())
    registry = json.loads((root / "ops/control/map-sheets-source.v1.0.json").read_text())
    tables, evidence = {}, {}
    expected = {x["tab"] for x in registry["tabs"]}
    if set(config["data_files"]) != expected or len(expected) != 14:
        raise ValueError("Map table coverage differs from the 14-table contract")
    for tab in registry["tabs"]:
        name = tab["tab"]
        path = config["data_files"][name]
        if path != f"ops/data/map-sheets-public.v1/{name}.json":
            raise ValueError("Unreviewed input path")
        raw = (root / path).read_bytes()
        payload = json.loads(raw)
        records, columns = payload["records"], payload["columns"]
        if (payload["table"] != name or payload["schema_version"] != "1.0.0"
                or payload["origin"] != "PRIVATE_GOOGLE_SHEET_MANUAL_REVIEWED_SNAPSHOT"
                or payload["row_count"] != len(records)
                or len(columns) != len(set(columns))
                or any(set(r) != set(columns) for r in records)):
            raise ValueError(f"Invalid reviewed source: {name}")
        keys = [r[tab["pk"]] for r in records]
        if any(not k for k in keys) or len(keys) != len(set(keys)):
            raise ValueError(f"Invalid primary key: {name}")
        tables[name] = payload
        evidence[name] = {"path": path, "sha256": hashlib.sha256(raw).hexdigest(),
                          "row_count": len(records)}
    payload = {"schema_version": "1.0.0", "bundle_id": "JP_MAP_REVIEWED_SHEETS_V1",
               "publication_mode": "REVIEWED_SNAPSHOT_BUILD",
               "live_google_sheets_fetch": False,
               "table_count": len(tables), "source_evidence": evidence, "tables": tables}
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    target = root / OUTPUT
    target.write_text(text, encoding="utf-8")
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    previous = (ROOT / OUTPUT).read_bytes() if args.check and (ROOT / OUTPUT).exists() else None
    result = build()
    if args.check and previous != (ROOT / OUTPUT).read_bytes():
        raise SystemExit("MAP_BUNDLE_STALE: regenerate before committing")
    print(f"MAP_BUNDLE_PASS: {result['table_count']} reviewed tables in one generated JSON")
