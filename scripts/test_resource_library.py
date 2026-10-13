#!/usr/bin/env python3
"""Request 07 deterministic Tests: authenticated metadata receipt, safe priorities, quarantine."""
from __future__ import annotations
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import validate_resource_library as validator
import preview_resource_intake as intake
import collect_private_drive_resource_metadata as collector

class ResourcesTests(unittest.TestCase):
    def test_existing_metadata_and_tiers(self):
        self.assertEqual(validator.validate(),{
            "issued_reports":14,"source_models":15,
            "calculations_and_support":2,"source_folders":15})
    def test_bad_historical_metadata_rejected(self):
        original=validator.load
        def fake(path):
            if path!=validator.READBACK:return original(path)
            j=copy.deepcopy(original(path))
            j["verified_entries"][0]["original_drive_filename"]="tampered-original.pdf"
            return j
        with patch.object(validator,"load",side_effect=fake):
            with self.assertRaisesRegex(ValueError,"authenticated metadata snapshot changed"):
                validator.validate()
    def test_private_filename_not_published(self):
        self.assertTrue(validator.SENSITIVE.search("Nagarita.pdf"))
        self.assertTrue(validator.SENSITIVE.search("personal_data__restricted"))
        self.assertFalse(validator.SENSITIVE.search("Sabitri_Giri__Cost_Estimate.pdf"))
    def test_priority_classification(self):
        self.assertEqual(intake.candidate_category("Cost_Estimate_AS_RECEIVED.pdf","application/pdf"),
                         ("calculations_and_support",3))
        self.assertEqual(intake.candidate_category("Footing_rebar_curtailment.pdf","application/pdf"),
                         ("calculations_and_support",3))
        self.assertEqual(intake.candidate_category("architecture drawing.pdf","application/pdf"),
                         ("issued_reports",1))
        self.assertEqual(intake.candidate_category("house.e2k","text/plain"),("source_models",2))
    def test_duplicate_safe_intake_and_quarantine(self):
        rows=[
            {"drive_file_id":"new-a","original_filename":"House architecture.pdf",
             "mime_type":"application/pdf","project_id":"P007","source_receipt_id":"receipt-1",
             "source_parent_verified":True},
            {"drive_file_id":"new-a","original_filename":"House architecture.pdf",
             "mime_type":"application/pdf","project_id":"P007","source_receipt_id":"receipt-1",
             "source_parent_verified":True},
            {"drive_file_id":"new-b","original_filename":"Personal_data__restricted.pdf",
             "mime_type":"application/pdf","project_id":"P007","source_receipt_id":"receipt-1",
             "source_parent_verified":True},
            {"drive_file_id":"new-c","original_filename":"unmapped.pdf",
             "mime_type":"application/pdf","project_id":"P999"},
        ]
        out=intake.review_candidates(rows,{},{"P007"})
        self.assertEqual(len(out),3)
        self.assertEqual([x["review_status"] for x in out].count("REVIEW_REQUIRED"),1)
        self.assertEqual([x["review_status"] for x in out].count("QUARANTINED"),2)
        self.assertTrue(all(x["publication_status"].startswith("BLOCKED") for x in out))
        with self.assertRaisesRegex(ValueError,"conflicting duplicate"):
            intake.review_candidates(rows+[dict(rows[0],original_filename="different.pdf")],{},{"P007"})
        self.assertEqual(out,intake.review_candidates(rows,{},{"P007"}))
    def test_recursive_private_drive_inventory_and_pagination(self):
        calls=[]
        def fetch(parent,token):
            calls.append((parent,token))
            if parent=="root-a" and token is None:
                return ([{"id":"f01","name":"building.pdf","mimeType":"application/pdf",
                          "parents":["root-a"]},
                         {"id":"dir1","name":"01_SOURCE","mimeType":collector.FOLDER,
                          "parents":["root-a"]}],"next")
            if parent=="root-a" and token=="next":
                return ([{"id":"f02","name":"estimated cost.pdf","mimeType":"application/pdf",
                          "parents":["root-a"]}],None)
            if parent=="dir1":
                return ([{"id":"f03","name":"Private_data.pdf","mimeType":"application/pdf",
                          "parents":["dir1"]}],None)
            raise AssertionError("Unexpected pagination")
        rows,visited=collector.crawl({"P007":"root-a"},fetch)
        self.assertEqual(len(rows),4)
        self.assertEqual(visited,2)
        self.assertEqual(len(calls),3)
        self.assertTrue(all(r["admission_status"]=="PRIVATE_METADATA_ONLY_REVIEW_REQUIRED" for r in rows))
        self.assertEqual(collector.crawl({"P007":"root-a"},fetch)[0],rows)
        with self.assertRaisesRegex(ValueError,"Max records"):
            collector.crawl({"P007":"root-a"},fetch,max_rows=2)
        def shared(parent,token):
            if parent in {"root-a","root-b"}:
                return ([{"id":"same","name":"same.pdf","mimeType":"application/pdf"}],None)
            return ([],None)
        with self.assertRaisesRegex(ValueError,"Cross-project"):
            collector.crawl({"P001":"root-a","P002":"root-b"},shared)

    def test_provider_search_hole_detected_by_file_parent_readback(self):
        # Recreates the observed Drive discrepancy: folder search returns zero
        # although metadata-by-ID confirms the DWG belongs in that parent.
        pid="P004"
        parent="source-folder"
        file_id="known-dwg"
        known={"sites":[{"project_id":pid,"files":[{
            "resource_id":"RES-TEST-P004-DWG",
            "source_drive_file_id":file_id,
            "original_drive_filename":"Verified drawing.dwg",
            "mime_type":"application/dwg",
        }]}]}
        def fetch(folder,token):
            if folder=="root":
                return ([{"id":parent,"name":"CAD","mimeType":collector.FOLDER,
                          "parents":["root"]}],None)
            if folder==parent: return ([],None)
            raise AssertionError(folder)
        rows,visited=collector.crawl({pid:"root"},fetch,return_visited=True)
        self.assertEqual(len(rows),1)
        def by_id(fid):
            self.assertEqual(fid,file_id)
            return {"id":fid,"name":"Verified drawing.dwg","mimeType":"application/dwg",
                    "parents":[parent],"trashed":False}
        with self.assertRaisesRegex(ValueError,"PARENT_LIST_COVERAGE_GAP"):
            collector.reconcile_indexed_sources(
                rows,visited,{pid:["root"]},by_id,known)
        # A correctly enumerated known child is accepted.
        def fixed_fetch(folder,token):
            if folder==parent:
                return ([{"id":file_id,"name":"Verified drawing.dwg","mimeType":"application/dwg",
                          "parents":[parent]}],None)
            return fetch(folder,token)
        rows,visited=collector.crawl({pid:"root"},fixed_fetch,return_visited=True)
        x=collector.reconcile_indexed_sources(rows,visited,{pid:["root"]},by_id,known)
        self.assertEqual(x["covered_registered_sources"],1)
        self.assertEqual(x["known_sources_outside_scanned_parents"],0)

    def test_source_alternate_root_support_and_outside_parent_flag(self):
        normalized=collector.normalize_roots({"P007":["alternate","canonical"]})
        self.assertEqual(normalized["P007"],["alternate","canonical"])
        with self.assertRaisesRegex(ValueError,"Same Drive root"):
            collector.normalize_roots({"P001":"shared","P002":"shared"})
        with self.assertRaisesRegex(ValueError,"Duplicate authorized"):
            collector.normalize_roots({"P007":["same","same"]})
        catalog={"sites":[{"project_id":"P007","files":[{
            "resource_id":"OUTSIDE-1","source_drive_file_id":"unseen",
            "original_drive_filename":"model.e2k","mime_type":"text/plain"
        }]}]}
        def meta(fid):
            return {"id":fid,"name":"model.e2k","mimeType":"text/plain",
                    "parents":["unscanned-parent"],"trashed":False}
        x=collector.reconcile_indexed_sources([], {("P007","canonical")},
                                             normalized,meta,catalog)
        self.assertEqual(x["known_sources_outside_scanned_parents"],1)
        self.assertEqual(x["uncovered_resource_ids"],["OUTSIDE-1"])

    def test_cycle_pagination_denied(self):
        def repeating(parent,token):
            return ([],"repeated")
        with self.assertRaisesRegex(ValueError,"Repeated provider page token"):
            collector.crawl({"P004":"root"},repeating)

    def test_no_candidate_writes_inside_public_repo(self):
        with self.assertRaisesRegex(ValueError,"public repository"):
            intake.private_path(intake.ROOT/"ops/data/danger.json")
        with tempfile.TemporaryDirectory() as t:
            self.assertTrue(intake.private_path(Path(t)/"safe.json").is_relative_to(Path(t).resolve()))

if __name__=="__main__":
    unittest.main()
