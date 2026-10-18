#!/usr/bin/env python3
"""Synthetic-only tests: never fetch or log private project filenames/IDs."""
import hashlib, json, pathlib, sys, tempfile, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import classify_private_resource_inventory as c

class PrivateResourceClassificationTests(unittest.TestCase):
    def inputs(self,path):
        root='synthetic-root'; records=[
            dict(drive_file_id='synthetic-folder',project_id='P999',original_filename='01_SOURCES',
                 mime_type='application/vnd.google-apps.folder',parent_ids=[root],source_root_ids=[root]),
            dict(drive_file_id='synthetic-technical',project_id='P999',original_filename='beam_plan.dxf',
                 mime_type='application/dxf',parent_ids=['synthetic-folder'],source_root_ids=[root]),
            dict(drive_file_id='synthetic-private',project_id='P999',original_filename='CLIENT_PAYMENT.csv',
                 mime_type='text/csv',parent_ids=['synthetic-folder'],source_root_ids=[root]),
            dict(drive_file_id='synthetic-pre',project_id='P999',original_filename='PRE__draft_plan.dwg',
                 mime_type='application/dwg',parent_ids=['synthetic-folder'],source_root_ids=[root]),
            dict(drive_file_id='synthetic-md',project_id='P999',original_filename='00_READ_FIRST.md',
                 mime_type='text/markdown',parent_ids=['synthetic-folder'],source_root_ids=[root]),
        ]
        preview={'source_export_receipt':None,'automatic_publication':False,'rows':[
            dict(drive_file_id=r['drive_file_id'],candidate_id='SYN-'+r['drive_file_id'],project_id=r['project_id'],
                 original_filename=r['original_filename'],mime_type=r['mime_type'],review_status='REVIEW_REQUIRED')
            for r in records]}
        raw=b''.join((json.dumps(x)+'\n').encode() for x in records);digest=hashlib.sha256(raw).hexdigest()
        preview['source_export_receipt']=digest
        receipt={'jsonl_sha256':digest,'files_and_folders':len(records),
                 'registered_source_coverage':{'known_sources_outside_scanned_parents':0}}
        paths=[path/'private.jsonl',path/'private-preview.json',path/'private-receipt.json']
        paths[0].write_bytes(raw);paths[1].write_text(json.dumps(preview));paths[2].write_text(json.dumps(receipt))
        return paths
    def test_classification_and_ancestry(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=self.inputs(pathlib.Path(tmp))
            items,summary=c.classify_inventory(*paths)
            lookup={r['drive_file_id']:r for r in items}
            self.assertEqual(summary['total_rows'],5)
            self.assertEqual(summary['snapshot_ancestry_verified_rows'],5)
            self.assertEqual(summary['public_admissions'],0)
            self.assertEqual(lookup['synthetic-technical']['private_bucket'],'ENGINEERING_DESIGN_CANDIDATE')
            self.assertEqual(lookup['synthetic-private']['private_bucket'],'RESTRICTED_QUARANTINE')
            self.assertEqual(lookup['synthetic-pre']['private_bucket'],'HISTORICAL_VERSION_AND_AUDIT')
            self.assertTrue(all(not x['engineering_issuance_approved'] for x in items))
            self.assertTrue(all(x['public_admission']=='BLOCKED' for x in items))
    def test_hash_tamper_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=self.inputs(pathlib.Path(tmp));paths[0].write_bytes(paths[0].read_bytes()+b'{}')
            with self.assertRaisesRegex(ValueError,'SHA-256'):
                c.classify_inventory(*paths)
    def test_foreign_source_edge_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=self.inputs(pathlib.Path(tmp))
            lines=[json.loads(x) for x in paths[0].read_text().splitlines()]
            lines[1]['parent_ids']=['unregistered-parent']
            raw=b''.join((json.dumps(x)+'\n').encode() for x in lines)
            receipt=json.loads(paths[2].read_text());receipt['jsonl_sha256']=hashlib.sha256(raw).hexdigest()
            review=json.loads(paths[1].read_text());review['source_export_receipt']=receipt['jsonl_sha256']
            paths[0].write_bytes(raw);paths[1].write_text(json.dumps(review));paths[2].write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'parent'):
                c.classify_inventory(*paths)
    def test_public_repository_path_rejected(self):
        with self.assertRaisesRegex(ValueError,'OUTSIDE public repository'):
            c.private_file(c.ROOT/'invalid-private.jsonl')

if __name__=='__main__':unittest.main()
