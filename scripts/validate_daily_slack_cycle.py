#!/usr/bin/env python3
"""Public-safe cycle contract invariants; no private Slack data is read by CI."""
import json
from pathlib import Path
p = Path("ops/control/daily-slack-web-cycle.json")
c = json.loads(p.read_text(encoding="utf-8"))
assert c["schema_version"] == "1.0.0"
assert c["control_id"] == "OPS-DAILY-SLACK-WEB-CYCLE-001"
assert c["status"] == "ACTIVE_PROCESS_CONTRACT"
assert c["authorities"]["private_archive"].startswith("EXISTING_PRIVATE_A9_SLACK_RECOVERY_ARCHIVE")
assert c["collection"]["archived_record_identity"] == "workspace_id + channel_id + message_ts"
assert "PRIVATE Drive raw JSONL" in c["collection"]["original_text"]
assert c["admission"]["output_formats"] == ["JSON", "JSONL", "CSV", "SQL_DDL"]
assert c["publication"]["repository_production_lane"] == "main"
assert c["publication"]["repository_working_lane"] == "feature/daily-ops-current-work"
assert c["publication"]["slack_delivery"]["readback"].startswith("After each authorized post")
rollups = c["coverage"]["company_rollups"]
assert {r["company_id"]: r["route"] for r in rollups} == {
  "ORG-000001": "FBL_COMPANY_ROLLUP",
  "ORG-000002": "REB_COMPANY_ROLLUP",
}
assert all(r["required_in_daily_scan"] for r in rollups)
assert c["coverage"]["existing_project_tracker_count"] >= 8
assert len(c["coverage"]["current_known_reb_not_in_ops"]) >= 2
assert c["run_closeout"]["require_source_window_per_channel"]
assert c["run_closeout"]["do_not_report_full_success_on_partial_archival"]
assert not c["publication"]["slack_delivery"]["authorization"].startswith("UNRESTRICTED")
print("PASS: private-archive / public-data / both company rollups / provider readback cycle contract")
