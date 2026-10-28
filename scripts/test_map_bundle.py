#!/usr/bin/env python3
"""Exercise bundle failure modes and verify that the browser consumes it."""
import copy
import json
import subprocess
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
    # Execute the browser's real loader against both supported publishing modes.
    loader = script[script.index("async function loadMapBundle("):script.index("async function loadWorkingProjectIds(")]
    live = copy.deepcopy(expected)
    live.update(live_google_sheets_fetch=True, publication_mode="ACTIONS_SHEETS_REFRESH_APPROVED_FIELDS",
                publication_receipt={"workflow_run_id": "123", "commit_sha": "a" * 40,
                                     "fetched_at_utc": "2026-10-28T14:27:33+00:00"})
    for table in live["tables"].values():
        table.update(origin="ACTIONS_GOOGLE_SHEETS_APPROVED_FIELDS",
                     projection_scope="ADMITTED_IDS_AND_APPROVED_FIELDS_ONLY")
    cases = [(expected, True), (live, True)]
    for defect in ("origin", "scope", "receipt", "mode", "count"):
        bad = copy.deepcopy(live)
        if defect == "receipt":
            bad.pop("publication_receipt")
        elif defect == "mode":
            bad["publication_mode"] = "UNKNOWN"
        else:
            table = bad["tables"]["materials_master"]
            table[{"origin": "origin", "scope": "projection_scope", "count": "row_count"}[defect]] = "INVALID"
        cases.append((bad, False))
    harness = loader + """
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
(async () => {
  for (const [bundle, accepted] of cases) {
    global.fetch = async () => ({ok:true,json:async()=>bundle});
    let result;
    try { result = await loadMapBundle('public.json','test'); }
    catch (error) { if (accepted) throw error; continue; }
    if (!accepted || Object.keys(result).length !== 14) throw Error('Browser loader contract failed');
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
"""
    subprocess.run(["node", "-e", harness], input=json.dumps(cases), text=True, check=True)
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
