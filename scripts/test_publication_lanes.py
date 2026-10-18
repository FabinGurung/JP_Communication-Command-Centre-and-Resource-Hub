#!/usr/bin/env python3
"""Request 06: offline regression tests for protected website publication lanes."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import validate_publication_lanes as lane

class PublicationLaneTests(unittest.TestCase):
    def test_canonical_stage_folders(self):
        self.assertEqual(lane.audit_drive_routes(),10)

    def test_independent_safe_changes(self):
        for changes in (
            ["ops/data/progress-report-public.v0.2.jsonl"],
            ["ops/data/resource-catalog-normalized.v0.1.json"],
            ["site-operations.html"],
            ["ops/discord/schemas/daily-message-index-v1.schema.json"],
            ["ops/control/communication-extract-staging.v0.1.json"],
        ):
            self.assertLessEqual(len(lane.audit_change_lanes(changes)),1)

    def test_cross_lane_mutation_denied(self):
        for changes in (
            ["ops/data/progress-report-public.v0.2.jsonl","ops/data/resource-catalog-normalized.v0.1.json"],
            ["ops/data/progress-report-public.v0.2.jsonl","site-operations.html"],
            ["ops/data/project-resources.json","ops/data/current-works.json"],
            ["ops/discord/schemas/x.json","ops/data/progress-report-public.v0.2.jsonl"],
            ["ops/data/resource-catalog-normalized.v0.1.json","site-operations/history.html"],
            ["ops/data/resource-original-names/a.json","site-operations.html"],
        ):
            with self.subTest(changes=changes),self.assertRaises(lane.GateError):
                lane.audit_change_lanes(changes)

    def test_main_parent_reconciliation_only_checks_actual_merge_delta(self):
        main="b"*40
        before="a"*40
        after="c"*40
        calls=[]
        def fake_git(*args):
            calls.append(args)
            if args==("rev-list","--parents","-n","1",after):
                return " ".join((after,before,main))
            if args==("rev-parse","refs/remotes/origin/main"):
                return main
            if args[:3]==("diff","--name-only","--no-renames"):
                self.assertEqual(args[3:],(main,after))
                return "AGENTS.md\\nops/events/cwo-daily/OPS-0081.json"
            raise AssertionError("Unexpected git invocation: "+repr(args))
        env={"GITHUB_SHA":after,"GITHUB_EVENT_BEFORE":before,"GITHUB_EVENT_NAME":"push"}
        with patch.dict(lane.os.environ,env,clear=True),patch.object(lane,"git",side_effect=fake_git):
            self.assertEqual(lane.audit_change_lanes(lane.changed_files()),set())
        self.assertEqual(len(calls),3)

    def test_main_parent_mismatch_fails_closed(self):
        before="a"*40
        after="c"*40
        with patch.dict(lane.os.environ,{"GITHUB_SHA":after,"GITHUB_EVENT_BEFORE":before,"GITHUB_EVENT_NAME":"push"},clear=True):
            with patch.object(lane,"git",side_effect=lambda *args: (
                " ".join((after,before,"b"*40)) if args[0]=="rev-list" else "d"*40)):
                with self.assertRaisesRegex(lane.GateError,"differs from current production main"):
                    lane.changed_files()

    def test_original_binary_or_raw_folder_denied(self):
        for item in (
            "ops/data/raw_jsonl/archive.jsonl",
            "ops/evidence/private/report.sqlite",
            "ops/discord/attachment_bytes/photo.jpg",
        ):
            with self.subTest(path=item),self.assertRaises(lane.GateError):
                lane.audit_change_lanes([item])

    def test_baseline_and_unreviewed_append(self):
        mainroot=lane.ROOT
        source=json.loads((mainroot/"ops/data/progress-report-public.v0.2.jsonl").read_text().splitlines()[0])
        raw=(json.dumps(source,sort_keys=True)+"\n").encode()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            (root/"ops/data").mkdir(parents=True)
            (root/"ops/control").mkdir(parents=True)
            (root/"ops/data/current-works.json").write_text(json.dumps({"projects":[{"project_id":source["project_id"]}]}))
            contract={
                "status":"LEGACY_FROZEN_NEW_ROWS_DENIED_UNTIL_SOURCE_REVIEW",
                "baseline":{"path":lane.REPORT,"blob_sha":"a"*40,"count":1,"ids":[source["record_id"]]},
                "admitted_new_records":[],"required_review_fields":["record_id","project_id"],
                "review_decision":"PUBLISH_PUBLIC_SAFE",
                "reviewer_role":"AUTHORIZED_HUMAN_SOURCE_REVIEWER",
                "claim_limit":"FIELD_REPORTED_NO_ENGINEER_ACCEPTANCE",
            }
            (root/lane.GATE).write_text(json.dumps(contract))
            path=root/lane.REPORT
            path.write_bytes(raw)
            with patch.object(lane,"ROOT",root),patch.object(lane.subprocess,"check_output",return_value=raw):
                self.assertEqual(lane.audit_report(),(1,0))
                extra=dict(source,record_id="UNREVIEWED-NEW-1")
                path.write_bytes(raw+(json.dumps(extra)+"\n").encode())
                with self.assertRaisesRegex(lane.GateError,"lacks documented review"):
                    lane.audit_report()
                path.write_bytes(raw.replace(source["record_id"].encode(),b"ALTERED-BASE-01"))
                with self.assertRaisesRegex(lane.GateError,"legacy public row changed"):
                    lane.audit_report()

    def test_preexisting_public_seed(self):
        old,new=lane.audit_report()
        self.assertEqual(old,37)
        self.assertEqual(new,0)

if __name__=="__main__":
    unittest.main()
