#!/usr/bin/env python3
"""Validate 14 private-Sheet-backed reviewed public JSON projections and initial CSV rollback parity."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read_json(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8"))

def main():
    registry=read_json("ops/control/map-sheets-source.v1.0.json")
    config=read_json("map-config.json")
    assert registry["authority_id"]=="JP_AEC_MAP_GOOGLE_SHEETS_SOURCE_20261021"
    assert registry["tab_count"]==14 and len(registry["tabs"])==14
    assert registry["source_rows"]==162
    assert config["data_provider"]["type"]=="GOOGLE_SHEETS_PRIVATE_SOURCE__REVIEWED_GITHUB_JSON_PROJECTION"
    assert len(config["data_files"])==14
    script=(ROOT/"assets/js/app.js").read_text(encoding="utf-8")
    assert "loadMapTable(" in script and "loadCSV(" not in script
    assert "return parseCSV" not in script
    total=0
    project_ids=set()
    for tab in registry["tabs"]:
        name=tab["tab"]
        projection=tab["public_projection"]
        assert config["data_files"].get(name)==projection, (name,projection)
        assert projection==f"ops/data/map-sheets-public.v1/{name}.json"
        payload=read_json(projection)
        assert payload["schema_version"]=="1.0.0"
        assert payload["table"]==name
        assert payload["source_worksheet"]==name
        assert payload["origin"]=="PRIVATE_GOOGLE_SHEET_MANUAL_REVIEWED_SNAPSHOT"
        assert len(payload["records"])==payload["row_count"],name
        assert payload["columns"] and len(payload["columns"])==len(set(payload["columns"]))
        assert all(set(r)==set(payload["columns"]) and all(isinstance(v,str) for v in r.values()) for r in payload["records"])
        pk=tab["pk"]
        assert pk in payload["columns"]
        values=[r[pk] for r in payload["records"]]
        assert all(values) and len(values)==len(set(values)),(name,"duplicate PK")
        if name=="projects":
            project_ids=set(values)
            assert len(project_ids)>=28
            for item in payload["records"]:
                if item["latitude"] and item["longitude"]:
                    assert -90<=float(item["latitude"])<=90
                    assert -180<=float(item["longitude"])<=180
        # Migration baseline evidence is exact, but subsequent reviewed projections
        # may intentionally diverge from the frozen CSV rollback files.
        if payload.get("projection_scope")=="BASELINE_IDENTICAL_TO_EXISTING_PUBLIC_CSV":
            with (ROOT/tab["source_csv_rollback"]).open(encoding="utf-8-sig",newline="") as f:
                legacy=list(csv.DictReader(f))
            legacy=[{k:(v or "").strip() for k,v in r.items()} for r in legacy]
            assert payload["records"]==legacy,(name,"baseline mismatch")
            assert tab["row_count"]==payload["row_count"],(name,"initial readback changed")
        total+=payload["row_count"]
    assert project_ids
    for name in ["project_parties","project_funding","project_components","project_source_links","project_publication_settings"]:
        for item in read_json(f"ops/data/map-sheets-public.v1/{name}.json")["records"]:
            assert item["project_id"] in project_ids,(name,item["project_id"])
    print(f"MAP_SHEETS_PROJECTION_PASS: 14 Google Sheets-backed JSON tables, {total} reviewed public rows, PK/FK checks, no runtime CSV fetch; frozen CSV rollback remains.")

if __name__=="__main__":
    main()
