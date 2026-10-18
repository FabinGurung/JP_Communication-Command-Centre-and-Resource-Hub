#!/usr/bin/env python3
"""REQ07 synthetic-only staged approval tests: never add source rows to site."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from reconcile_private_resource_inventory import canonical
from stage_reviewed_resource_admission import stage

class ReviewedStageTests(unittest.TestCase):
    def setup(self,dir):
        row={"drive_file_id":"synthetic-99","project_id":"P001","original_filename":"concept-plan.pdf",
             "mime_type":"application/pdf","parent_ids":["parent"],"source_root_ids":["root"]}
        raw=canonical(row);sha=hashlib.sha256(raw).hexdigest()
        src=dir/"snapshot.jsonl";src.write_bytes(raw)
        receipt=dir/"snapshot.receipt.json";receipt.write_text(json.dumps({
            "type":"PRIVATE_DRIVE_RECURSIVE_METADATA_INVENTORY","jsonl_sha256":sha,
            "files_and_folders":1,"public_admissions":0,"drive_modifications":0,"byte_downloads":0,
            "scope":"ONLY_REVIEWED_PROJECT_ROOTS","duplicate_policy":"ONE_DRIVE_ID_ONE_PROJECT_OR_STOP"
        }))
        proof=lambda decision:{"decision":decision,"approval_record_id":"synthetic-evidence",
            "authorized_by":"synthetic-reviewer","approved_at_npt":"2026-10-15",
            "independently_verified_sha256":"a"*64}
        rec={"drive_file_id":"synthetic-99","project_id":"P001","original_filename":"concept-plan.pdf",
             "mime_type":"application/pdf","root_project_provenance_verified":True,
             "source_owner_authorization":proof("PUBLIC_RESOURCE_POINTER_ALLOWED"),
             "privacy_authorization":proof("NAME_AND_SOURCE_LINK_ALLOWED"),
             "category":"issued_reports","resource_id":"RES-P001-TEST-001",
             "normalized_name":"Concept Plan","discipline":"architecture",
             "technical_issue_status":"UNVERIFIED_AS_CURRENT_ISSUE"}
        decision={"type":"REQ07_PRIVATE_RESOURCE_PUBLIC_INDEX_APPROVAL","source_inventory_sha256":sha,"approved_resources":[rec]}
        p=dir/"decisions.json";p.write_text(json.dumps(decision))
        return src,receipt,p,decision
    def test_valid_explicit_approval_only_creates_private_draft(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src,receipt,p,_=self.setup(root);out=root/"private-proposal.json"
            r=stage(src,receipt,p,out,repo=root/"public-repo")
            self.assertEqual(r["proposed_count"],1)
            self.assertEqual(r["public_admissions"],0)
            self.assertEqual(json.loads(out.read_text())["reviewed_candidates"][0]["approval_status"],"UNVERIFIED_AS_CURRENT_ISSUE")
            with self.assertRaises(FileExistsError):stage(src,receipt,p,out,repo=root/"public-repo")
    def test_reject_missing_owner_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src,receipt,p,v=self.setup(root)
            del v["approved_resources"][0]["source_owner_authorization"];p.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,"owner/privacy evidence"):
                stage(src,receipt,p,root/"draft.json",repo=root/"public-repo")
    def test_reject_false_engineering_issue(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src,receipt,p,v=self.setup(root)
            v["approved_resources"][0]["technical_issue_status"]="APPROVED_FOR_CONSTRUCTION";p.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,"engineering issuance"):
                stage(src,receipt,p,root/"draft.json",repo=root/"public-repo")
    def test_reject_already_public(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src,receipt,p,_=self.setup(root)
            with self.assertRaisesRegex(ValueError,"already indexed"):
                stage(src,receipt,p,root/"draft.json",repo=root/"public-repo",known_ids={"synthetic-99"})
    def test_empty_approvals_are_zero_admission(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src,receipt,p,v=self.setup(root)
            v["approved_resources"]=[];p.write_text(json.dumps(v))
            r=stage(src,receipt,p,root/"draft.json",repo=root/"public-repo")
            self.assertEqual(r["proposed_count"],0)
            self.assertEqual(r["public_admissions"],0)

if __name__=="__main__":unittest.main()
