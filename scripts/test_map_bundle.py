#!/usr/bin/env python3
"""Exercise bundle failure modes and verify that the browser consumes it."""
import copy
import json
import tempfile
from pathlib import Path
from build_map_bundle import ROOT, OUTPUT, build

def run():
    expected = json.loads((ROOT / OUTPUT).read_text())
    assert build() == expected
    assert expected["live_google_sheets_fetch"] is False
    assert expected["tables"]["people"]["records"] == []
    script = (ROOT / "assets/js/app.js").read_text()
    assert "loadMapBundle(state.config.data_bundle" in script
    for defect in ("duplicate", "count", "path"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ["map-config.json", "ops/control/map-sheets-source.v1.0.json"]:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / name).read_bytes())
            for item in expected["source_evidence"].values():
                dest = root / item["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / item["path"]).read_bytes())
            file = root / "ops/data/map-sheets-public.v1/projects.json"
            data = json.loads(file.read_text())
            if defect == "duplicate":
                data["records"][1]["project_id"] = data["records"][0]["project_id"]
            elif defect == "count":
                data["row_count"] += 1
            else:
                config = json.loads((root / "map-config.json").read_text())
                config["data_files"]["projects"] = "private-input.json"
                (root / "map-config.json").write_text(json.dumps(config))
            file.write_text(json.dumps(data))
            try:
                build(root)
            except ValueError:
                pass
            else:
                raise AssertionError(f"Expected rejection: {defect}")
    print("MAP_BUNDLE_TEST_PASS: exact baseline, no People rows, duplicate/count/path rejection")

if __name__ == "__main__":
    run()
