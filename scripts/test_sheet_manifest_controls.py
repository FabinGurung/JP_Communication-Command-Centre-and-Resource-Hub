"""Offline mutation contract tests for authenticated Colab control maintenance."""
from maintain_sheet_manifests import ensure_controls

class API:
    def __init__(self, service): self.service = service
    def spreadsheets(self): return self
    def files(self): return self
    def get(self, **kwargs): return (self.service, 'get', kwargs)
    def list(self, **kwargs): return (self.service, 'list', kwargs)
    def copy(self, **kwargs): return (self.service, 'copy', kwargs)
    def create(self, **kwargs): return (self.service, 'create', kwargs)
    def batchUpdate(self, **kwargs): return (self.service, 'batch', kwargs)

def main():
    sheets, drive = API('sheets'), API('drive')
    tabs = [{'properties': {'sheetId': 1, 'title': 'source_data'}}]
    copies, writes, snapshots, folders = [], [], [], []
    def execute(req):
        service, op, args = req
        if service == 'sheets' and op == 'get':
            return {'spreadsheetId': 'S', 'sheets': list(tabs)}
        if op == 'list': return {'files': list(folders if 'mimeType' in args['q'] else snapshots)}
        if op == 'create':
            assert args['body']['parents'] == ['V']
            folders.append({'id': 'OWNER', **args['body']})
            return folders[-1]
        if op == 'copy':
            assert args['body']['parents'] == ['OWNER']
            copies.append(args)
            snapshots.append({'id': 'PRE', 'parents': ['OWNER'], 'name': 'PRE_MANIFEST_V000001__S'})
            return snapshots[0]
        if service == 'drive' and op == 'get':
            return ({'id': 'OWNER', 'parents': ['V'], 'mimeType': 'application/vnd.google-apps.folder'}
                    if args['fileId'] == 'OWNER' else
                    {'id': 'PRE', 'parents': ['OWNER'], 'mimeType': 'application/vnd.google-apps.spreadsheet'})
        if op == 'batch':
            writes.append(args)
            for request in args['body']['requests']:
                if 'addSheet' in request:
                    tabs.append({'properties': request['addSheet']['properties']})
                if 'updateCells' in request:
                    assert request['updateCells']['range']['sheetId'] != 1
            return {}
        raise AssertionError(req)
    items = [
        {'id': 'R', 'name': '01_JP', 'mime_type': 'folder'},
        {'id': 'A', 'name': '99_ARCHIVE_GALLERY', 'mime_type': 'folder', 'parent_id': 'R'},
        {'id': 'S', 'name': 'Active', 'mime_type': 'application/vnd.google-apps.spreadsheet', 'parent_id': 'R'},
        {'id': 'OLD', 'name': 'Old source', 'mime_type': 'application/vnd.google-apps.spreadsheet', 'parent_id': 'A'}]
    first = list(ensure_controls(items, sheets, drive, 'A', 'V', execute))
    assert {x['status'] for x in first} == {'ARCHIVED_NO_LIVE_CONSUMER_REQUIRED', 'MISSING_CONTROLS_ADDED_VERIFIED'}
    second = list(ensure_controls(items, sheets, drive, 'A', 'V', execute))
    assert len(copies) == len(writes) == 1
    assert len(folders) == 1
    assert any(x['status'] == 'CONTROL_TABS_PRESENT_CONTENT_REVIEW_PENDING' for x in second)
    assert all(x['consumer_status'] == 'UNMAPPED_REQUIRES_OWNER_REVIEW' for x in first)
    # Readable folder names must not accidentally reactivate archived workbooks.
    from maintain_sheet_manifests import is_archived
    renamed = {'id': 'H', 'name': 'Earlier Copies', 'parent_id': 'R'}
    child = {'id': 'HS', 'name': 'Old workbook', 'parent_id': 'H'}
    assert is_archived(child, {'H': renamed}, 'A', archive_roots=['H'])
    assert is_archived({'id': 'P', 'name': 'PRE1__Old workbook'}, {}, 'A')
    assert is_archived({'id': 'P', 'name': 'POST2__Old workbook'}, {}, 'A')
    assert is_archived({'id': 'P', 'name': '99 Previous Records'}, {}, 'A')
    assert is_archived({'id': 'P', 'name': '99_VERSION_HISTORY'}, {}, 'A')
    assert is_archived({'id': 'P', 'name': 'FINAL_POST2__Old workbook'}, {}, 'A')
    from maintain_sheet_manifests import owner_archive_folder
    folders[0]['name'] = 'Earlier title — S'
    assert owner_archive_folder(drive, 'V', {'id': 'S', 'name': 'Renamed source'}, execute) == 'OWNER'
    assert len(folders) == 1
    print('SHEET_CONTROL_TEST_PASS: archive exclusion, PRE-before-edit, no source-cell writes, idempotent retry, no invented consumers')

if __name__ == '__main__': main()
