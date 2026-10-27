#!/usr/bin/env python3
"""Guard public/private separation and hostile or corrupt navigation inputs."""
import copy,json,re,tempfile,unittest
from pathlib import Path
from build_drive_navigator import assemble,build,ROOT

class NavigatorTests(unittest.TestCase):
    def setUp(self):
        self.rows=[dict(drive_file_id='root',name='Library',parent_drive_id=None,mime_type='application/vnd.google-apps.folder',url='https://drive.google.com/drive/folders/root'),dict(drive_file_id='child',name='Working',parent_drive_id='root',mime_type='application/vnd.google-apps.folder',url='https://drive.google.com/drive/folders/child'),dict(drive_file_id='history',name='99_VERSION_HISTORY',parent_drive_id='root',mime_type='application/vnd.google-apps.folder',url='https://drive.google.com/drive/folders/history'),dict(drive_file_id='old',name='Old Sheet',parent_drive_id='history',mime_type='application/vnd.google-apps.spreadsheet',url='https://docs.google.com/spreadsheets/d/old/edit')]
        sheet=dict(id='s',name='Source',url='https://docs.google.com/spreadsheets/d/s/edit',description='Source facts')
        self.spec=dict(root='root',updated='25 October 2026',inventoryAt='25 October 2026',inventoryNotice='Historical snapshot',sheets=[sheet],stagedCount=0,master=sheet,scope=['Library'],renameCount=0,codeUrl='https://github.com/example/repo',actionsUrl='https://github.com/example/repo/actions')
    def test_public_shell_has_no_inventory(self):
        html=(ROOT/'files/index.html').read_text()
        self.assertIn('<script id="navigator-data" type="application/json">null</script>',html)
        self.assertNotIn('drive_file_id',html)
        self.assertNotIn('1LPZ1ikU5Jx6r5WA7skKJC2uQ-Py-lVGj',html)
    def test_version_history_ancestor_is_historical(self):
        result=assemble(self.rows,self.spec)
        self.assertTrue(next(x for x in result['entries'] if x['id']=='old')['historical'])
    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):assemble(self.rows+[self.rows[0]],self.spec)
    def test_missing_parent_rejected(self):
        self.rows[1]['parent_drive_id']='missing'
        with self.assertRaisesRegex(ValueError,'Missing'):assemble(self.rows,self.spec)
    def test_cycle_rejected(self):
        self.rows[1]['parent_drive_id']='old';self.rows[2]['parent_drive_id']='child'
        with self.assertRaisesRegex(ValueError,'cycle'):assemble(self.rows,self.spec)
    def test_excluded_staging_rejected(self):
        self.rows[1]['name']='98_INTAKE_STAGING'
        with self.assertRaisesRegex(ValueError,'Excluded'):assemble(self.rows,self.spec)
    def test_link_protocol_rejected(self):
        self.rows[1]['url']='javascript:alert(1)'
        with self.assertRaisesRegex(ValueError,'URL'):assemble(self.rows,self.spec)
    def test_missing_web_url_uses_recorded_file_identity(self):
        self.rows[1]['url']=None
        e=next(x for x in assemble(self.rows,self.spec)['entries'] if x['id']=='child')
        self.assertEqual(e['url'],'https://drive.google.com/drive/folders/child')
    def test_private_output_cannot_be_in_repository(self):
        with self.assertRaisesRegex(ValueError,'outside'):build(Path('unused'),Path('unused'),ROOT/'files/private.html')
    def test_name_with_script_tag_is_data(self):
        self.rows[1]['name']='</script><script>alert("fixture")</script>'
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);inv=base/'in.jsonl';spec=base/'spec.json';out=base/'out.html'
            inv.write_text('\n'.join(json.dumps(x) for x in self.rows));spec.write_text(json.dumps(self.spec))
            build(inv,spec,out)
            embedded=re.search(r'<script id="navigator-data" type="application/json">(.*?)</script>',out.read_text(),re.S).group(1)
            self.assertNotIn('<script>',embedded)
            self.assertEqual(json.loads(embedded)['entries'][1]['name'],self.rows[1]['name'])
    def test_website_directory_is_preserved_without_public_snapshot(self):
        self.spec['websiteDirectory']={'verifiedAt':'27 October 2026','stars':[], 'checklist':[]}
        result=assemble(self.rows,self.spec)
        self.assertEqual(result['websiteDirectory'],self.spec['websiteDirectory'])
        self.assertIn('navigator-data', (ROOT/'files/index.html').read_text())
        self.assertNotIn('SUBIN_SUPPLIERS', (ROOT/'files/index.html').read_text())
    def test_rename_preserves_file_and_parent_ids(self):
        self.spec['name_overrides']={'child':'Readable folder'}
        e=next(e for e in assemble(self.rows,self.spec)['entries'] if e['id']=='child')
        self.assertEqual((e['name'],e['parent']),('Readable folder','root'))

if __name__=='__main__':unittest.main()
