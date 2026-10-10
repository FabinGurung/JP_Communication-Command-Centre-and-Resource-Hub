"""Privacy and stable identity sanity tests for A9-CWO offline engine."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cwo_evidence_engine import IntegrityError, digest, secure_external_path


class EvidenceTests(unittest.TestCase):
    def test_sha256_known_vector(self):
        self.assertEqual(digest(b"abc"),hashlib.sha256(b"abc").hexdigest())
        self.assertEqual(len(digest(b"abc")),64)

    def test_private_write_protected(self):
        with self.assertRaises(IntegrityError):
            secure_external_path(Path(__file__).resolve().parents[1] / "ops/evidence/raw.jsonl",write=True)


    def test_public_schema_and_inventory(self):
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root/"ops/evidence/schema/evidence-record.v0.1.schema.json").read_text())
        fidelity = json.loads((root/"ops/evidence/schema/attachment-fidelity.v0.1.schema.json").read_text())
        policy = json.loads((root/"ops/evidence/control/publication-policy.v0.1.json").read_text())
        mapping = json.loads((root/"ops/evidence/control/project-source-map.v0.1.json").read_text())
        report = json.loads((root/"ops/evidence/inventory/20261010T005617Z.public-summary.json").read_text())
        self.assertEqual(schema["$schema"],"https://json-schema.org/draft/2020-12/schema")
        self.assertTrue({"record_id","source_content_sha256","supersedes_id","project_id","company_id"}.issubset(schema["required"]))
        self.assertIn("FAILED_SIZE_MISMATCH",fidelity["properties"]["status"]["enum"])
        self.assertEqual(policy["publication_default"],"DENY")
        self.assertEqual(mapping["source_channel_bindings"],[])
        self.assertEqual((report["attachment_archived_this_run"] +
                          report["attachment_previously_archived_unreconfirmed"] +
                          report["attachment_failed_size_mismatch"]),459)
        self.assertEqual(sum(x["rows"] for x in report["partitions"]),89)
        self.assertEqual(report["candidates_admitted_as_construction_truth"],0)

    def test_index_verification_and_private_quarantine(self):
        from cwo_evidence_engine import normalize_private,verify_index
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp)
            index=t/"index"; index.mkdir()
            raw_path=t/"raw.jsonl"
            raw={"id":"m1","channel_id":"child1","content":"private image caption",
                 "attachments":[{"id":"a1"}],"timestamp":"2026-10-03T00:00:00+00:00"}
            raw_path.write_text(json.dumps(raw,sort_keys=True)+"\n",encoding="utf-8")
            pointer={"run_id":"R1","source_receipt_id":"receipt1","parent_channel_id":"parent1",
                     "provider":"DISCORD","channel_id":"child1","message_id":"m1",
                     "raw_drive_id":"rawfile1","raw_line_1_based":1,"admission_status":"NOT_RECONCILED"}
            partition=index/"day__2026-10-03__R1.jsonl"
            partition.write_text(json.dumps(pointer)+"\n",encoding="utf-8")
            manifest={"run_id":"R1","source_receipt_status":"PARTIAL","source_receipt_drive_id":"receipt1",
                      "source_scope":{"parent_channel_ids":["parent1","parent2"],"archived_threads_covered":False},
                      "partitions":[{"date_npt":"2026-10-03","sha256":digest(partition.read_bytes()),"rows":1}],
                      "rows_indexed":1}
            receipt={"run_id":"R1","status":"PARTIAL","target_parent_channels":["parent1","parent2"],
                     "messages_new_or_changed":1,"attachment_failures":0,
                     "collection_finished_at":"2026-10-10T00:00:00+00:00",
                     "sources":[{"parent_channel_id":"parent1","attachments":0,"attachments_evidence":[]}]}
            man_file=t/"manifest.json";man_file.write_text(json.dumps(manifest))
            rec_file=t/"receipt.json";rec_file.write_text(json.dumps(receipt))
            self.assertEqual(verify_index(man_file,rec_file,index)["index_rows_verified"],1)
            rawmap=t/"rawmap.json"; rawmap.write_text(json.dumps({"rawfile1":str(raw_path)}))
            output=t/"private-v1.jsonl"
            result=normalize_private(man_file,rec_file,index,rawmap,output)
            row=json.loads(output.read_text())
            self.assertEqual(result["admitted"],0)
            self.assertEqual(row["admission_status"],"QUARANTINED_UNMAPPED")
            self.assertEqual(row["project_id"],None)
            self.assertEqual(row["access_classification"],"PRIVATE_RESTRICTED")
            self.assertEqual(row["attachment_ids"],["a1"])
            again=normalize_private(man_file,rec_file,index,rawmap,t/"private-v2.jsonl",output)
            self.assertEqual(again["new_records"],0)
            self.assertEqual(again["replayed_unchanged"],1)
            with self.assertRaises(IntegrityError):
                normalize_private(man_file,rec_file,index,rawmap,output)

    def test_private_new_path(self):
        with tempfile.TemporaryDirectory() as temp:
            result = secure_external_path(Path(temp)/"private"/"output.jsonl",write=True)
            self.assertTrue(result.parent.exists())
            self.assertFalse(Path(__file__).resolve().parents[1] in result.parents)


if __name__ == "__main__":
    unittest.main()
