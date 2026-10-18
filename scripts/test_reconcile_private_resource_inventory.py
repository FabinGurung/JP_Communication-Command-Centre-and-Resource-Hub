#!/usr/bin/env python3
"""Synthetic-only, metadata-only REQ07 incremental collector tests."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import reconcile_private_resource_inventory as delta

BASE={
    "type":"PRIVATE_DRIVE_RECURSIVE_METADATA_INVENTORY",
    "project_root_count":9,"indexed_project_count":8,
    "root_registry_source":"ops/data/project-resources.json",
    "scope":"ONLY_REVIEWED_PROJECT_ROOTS",
    "duplicate_policy":"ONE_DRIVE_ID_ONE_PROJECT_OR_STOP",
    "registered_source_coverage":{"registered_sources_checked":46},
    "public_admissions":0,"drive_modifications":0,"byte_downloads":0
}
class PrivateDeltaTests(unittest.TestCase):
    def row(self,id="synth-one",name="Foundation.dwg",project="P001"):
        return {"drive_file_id":id,"project_id":project,"original_filename":name,"mime_type":"application/dwg",
                "parent_ids":["synth-parent"],"source_root_ids":["synth-root"],"modified_time":"2026-10-15"}
    def source(self,folder,name,rows):
        raw=b"".join(delta.canonical(x) for x in rows)
        obj=dict(BASE,files_and_folders=len(rows),jsonl_sha256=hashlib.sha256(raw).hexdigest())
        p=folder/(name+".jsonl");p.write_bytes(raw)
        r=folder/(name+".receipt.json");r.write_text(json.dumps(obj))
        return p,r
    def test_zero_changes_append_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);a,b=self.source(root,"old",[self.row()])
            c,e=self.source(root,"new",[self.row()])
            result=delta.run(a,b,c,e,root/"delta.jsonl",root/"delta.json",repo=root/"public-repo")
            self.assertEqual(result["changed_rows"],0)
            self.assertEqual(result["public_admissions"],0)
            with self.assertRaises(FileExistsError):
                delta.run(a,b,c,e,root/"delta.jsonl",root/"delta.json",repo=root/"public-repo")
    def test_new_changed_gone_conflicting_owner(self):
        old=[self.row("changed","a.dwg"),self.row("gone"),self.row("foreign",project="P001")]
        new=[self.row("changed","b.dwg"),self.row("added"),self.row("foreign",project="P002")]
        changes,counts=delta.diff_snapshots({x["drive_file_id"]:x for x in old},{x["drive_file_id"]:x for x in new},BASE,BASE)
        self.assertEqual([x["drive_file_id"] for x in changes],["added","changed","foreign","gone"])
        self.assertEqual(set(counts),{"NEW_METADATA_CANDIDATE","CHANGED_METADATA_REQUIRES_REVIEW",
                                      "PROJECT_FOREIGN_KEY_CONFLICT","NOT_SEEN_IN_CURRENT_SCOPE_NOT_DELETION"})
        self.assertTrue(all(x["public_admission"]=="BLOCKED" and not x["source_owner_verified"] for x in changes))
    def test_change_scope_refused(self):
        with self.assertRaisesRegex(ValueError,"root scope"):
            delta.diff_snapshots({}, {}, BASE,dict(BASE,project_root_count=10))
    def test_private_path_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/"public-repo"
            with self.assertRaisesRegex(ValueError,"public repository"):
                delta.private_path(p/"secret.jsonl",repo=p)
    def test_duplicate_id(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);a,b=self.source(p,"dup",[self.row(),self.row()])
            with self.assertRaisesRegex(ValueError,"duplicate"):
                delta.load_snapshot(a,b,repo=p/"public-repo")
    def test_sha_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);a,b=self.source(p,"tamper",[self.row()]);a.write_bytes(b"{}\n")
            with self.assertRaisesRegex(ValueError,"SHA256"):
                delta.load_snapshot(a,b,repo=p/"public-repo")
if __name__=="__main__":unittest.main()
