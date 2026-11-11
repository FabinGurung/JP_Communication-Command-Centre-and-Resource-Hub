#!/usr/bin/env python3
"""Validate the Operations source/decision memory wall without creating a second fact authority."""
from pathlib import Path
import json
from publish_operations import SOURCES, LIBRARY

ROOT=Path(__file__).resolve().parents[1]
ledger=json.loads((ROOT/"ops/control/operations-source-decision-ledger.v1.json").read_text(encoding="utf-8"))
assert ledger["authority"]=="ROUTING_AND_RELEASE_EVIDENCE_ONLY__NOT_A_DOMAIN_FACT_DATABASE"
assert set(ledger["source_books"])==set(SOURCES)
for key,(book,tab) in SOURCES.items():
    assert ledger["source_books"][key]["id"]==book, key
    assert ledger["source_books"][key]["tab"]==tab, key
    assert len(ledger["source_books"][key]["fields"])>=3
assert ledger["source_observation"]["public_rows"]==29
assert sum(ledger["source_observation"]["listed_status_counts"].values())==29
assert ledger["source_observation"]["public_status_published_count"]==28
assert ledger["source_observation"]["excluded_retired_alias_ids"]==["PRJ-000030"]
assert ledger["source_observation"]["listed_status_counts"]["unpublished"]==1
assert len({d["id"] for d in ledger["decisions"]})==len(ledger["decisions"])
assert {"OPS-DEC-20261112-STATUS-UI","OPS-DEC-20261112-SOURCE-MEMORY"}.issubset({d["id"] for d in ledger["decisions"]})
for d in ledger["decisions"]:
    assert d["fact_sources"] and d["artifacts"] and d["decision"] and d["date_npt"]
    for file in d["artifacts"]:
        assert (ROOT/file).is_file(), file
page=(ROOT/"publication/operations/memory-wall.html").read_text(encoding="utf-8")
html=(ROOT/"publication/operations/index.html").read_text(encoding="utf-8")
owner=(ROOT/"publication/operations/owner-help.html").read_text(encoding="utf-8")
policy=(ROOT/"AGENTS.md").read_text(encoding="utf-8")
doc=(ROOT/"docs/operations/OPERATIONS_SOURCE_DECISIONS_MEMORY_WALL.md").read_text(encoding="utf-8")
for value in ("memory-wall.html","data-project-status","status-filter"):
    assert value in html
assert "memory-wall.html" in owner
assert "01 Website Source Sheets" in page
assert "02 Website Sheets and Registers" in page
assert "source-decision-ledger" in page
assert "original Google Sheets" in doc
assert "Projects and Locations" in doc
assert "OPERATIONS_SOURCE_DECISIONS_MEMORY_WALL.md" in policy
assert "SHEETS_V2" in policy
assert LIBRARY in page
print("OPS_SOURCE_MEMORY_PASS: owner sources=5, fact/code distinction=verified, public status controls and page linked")
