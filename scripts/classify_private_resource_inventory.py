#!/usr/bin/env python3
"""Req07: deterministic private-only metadata classifier.

Inputs: SHA-verified Drive metadata JSONL, its receipt, and existing private review preview.
Outputs: private JSONL and non-sensitive count receipt OUTSIDE the public repository.
No source downloads, owner permission inference, engineering issuance, or public admission.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, pathlib, re

ROOT=pathlib.Path(__file__).resolve().parents[1]
FOLDER='application/vnd.google-apps.folder'
TECHNICAL_MIMES={'application/dwg','image/vnd.dwg','application/dxf','application/acad','application/x-autocad','application/x-dwg','application/ifc'}
HISTORY=re.compile(r'(^|[_\W])(PRE|POST|FINAL_POST|PRE_MOVE|POST_MOVE|ARCHIVE|ARCHIVED|BACKUP|ROLLBACK|ROLLED_BACK|REDUNDANT|DUPLICATE|SNAPSHOT|TRASH_CAN|DO_NOT_USE|ABORTED|SUPERSEDED|HISTORICAL|DEPRECATED|VERSION_HISTORY|VERSION_ARCHIVE)([_\W]|$)', re.I)
SENSITIVE=re.compile(r'(PASSPORT|CITIZENSHIP|NAGARITA|NAGARIKTA|AADHAAR|PERSONAL_DATA|PERSONNEL|EMPLOYEE|STAFF|KYC|BANK|ACCOUNT[_ -]?NUMBER|SALARY|PAYROLL|WAGE|LABOU?R[_ -]?PAYMENT|CONTRACTOR[_ -]?PAYMENT|CLIENT[_ -]?PAYMENT|PHONE[_ -]?NUMBER|MEDICAL|BIRTH[_ -]?CERTIFICATE|PERS-\d+)', re.I)
FINANCE=re.compile(r'(BILL|INVOICE|FINANCE|LEDGER|COST|RATE|BOQ|QTO|ESTIMATE|PAYMENT|PURCHASE|PROCUREMENT|RECEIPT|ACCOUNT|CASH|MONEY|VOUCHER|MILESTONE|CONTRACT|MEASUREMENT)', re.I)
FIELD=re.compile(r'(SITE|PROGRESS|DAILY|CEMENT|MATERIAL|ATTENDANCE|CURING|QUALITY|WORKLOG|WORK[_ -]?ORDER|FIELD|SUPPLY|DELIVERY|RFI|INSPECTION|PHOTO|REPORT)', re.I)
ENG=re.compile(r'(ARCHITECT|STRUCTUR|DRAWING|DESIGN|FOUNDATION|FOOTING|BEAM|COLUMN|SLAB|RCC|SEISMIC|ETABS|CAD|BIM|IFC|DXF|DWG|GEOMETRY|REBAR|BAR[_ -]?BENDING|SECTION|STAIR|PLAN|ELEVATION|SCHEDULE|DETAIL|REINFORC|MODEL|ANALYSIS)', re.I)
CONTROL=re.compile(r'(CHECKPOINT|CONTROL|LIBRARY|REGISTRY|MANIFEST|INDEX|PROMPT|WORKSPACE|CONFIG|SYSTEM|AI_|GITHUB|GIT_|COLAB|NOTEBOOK|AUTOMAT|PROTOCOL|README|READ_FIRST|SCHEMA|PIPELINE|SCRIPT|SQL|TEST|LOG|BACKLOG|STATUS|EVENT|SYNC|HANDOVER)', re.I)
SYSTEM_MIMES={'application/json','application/x-jsonlines','application/x-ndjson','application/x-ipynb+json','text/markdown','text/html','text/javascript','text/css','application/sql','text/sql','application/vnd.sqlite3','application/x-sqlite3','application/zip','application/gzip','application/octet-stream','text/csv','text/plain'}
MEDIA_MIMES={'image/jpeg','image/png','image/tiff','image/svg+xml'}

def private_file(p):
    path=pathlib.Path(p).expanduser().resolve()
    if path==ROOT or ROOT in path.parents:raise ValueError('Private inventory input/output must remain OUTSIDE public repository')
    return path

def classify(row, previous):
    n=row['original_filename'];mime=row['mime_type'];state=previous['review_status']
    if state=='ALREADY_INDEXED':return 'EXISTING_CATALOG_REFERENCE'
    if state=='QUARANTINED' or SENSITIVE.search(n):return 'RESTRICTED_QUARANTINE'
    if HISTORY.search(n):return 'HISTORICAL_VERSION_AND_AUDIT'
    if mime==FOLDER:return 'FOLDER_METADATA_ONLY'
    if FINANCE.search(n):return 'FINANCE_COMMERCIAL_PRIVATE'
    if mime in TECHNICAL_MIMES or n.lower().endswith(('.dwg','.dxf','.ifc','.e2k','.edb','.rvt','.skp')):
        return 'ENGINEERING_DESIGN_CANDIDATE'
    if mime=='application/pdf' and (ENG.search(n) or 'REPORT' in n.upper()):return 'ENGINEERING_DESIGN_CANDIDATE'
    if ENG.search(n) and mime in (MEDIA_MIMES | SYSTEM_MIMES | {'application/pdf','application/vnd.google-apps.document'}):
        return 'ENGINEERING_SUPPORT_PRIVATE'
    if FIELD.search(n):return 'SITE_OPERATIONS_PRIVATE'
    if CONTROL.search(n) or mime in SYSTEM_MIMES | {'application/vnd.google-apps.spreadsheet','application/vnd.google-apps.document'}:
        return 'SYSTEM_AUTOMATION_CONTROL'
    if mime in MEDIA_MIMES:return 'MEDIA_EVIDENCE_PRIVATE'
    return 'UNRESOLVED_METADATA'

def classify_inventory(inventory,preview,receipt):
    inventory=private_file(inventory);preview=private_file(preview);receipt=private_file(receipt)
    binary=inventory.read_bytes();digest=hashlib.sha256(binary).hexdigest()
    expected=json.loads(receipt.read_text(encoding='utf8'))
    if digest!=expected['jsonl_sha256']:raise ValueError('Source SHA-256 mismatch')
    rows=[json.loads(x) for x in binary.splitlines()]
    if len(rows)!=expected['files_and_folders']:raise ValueError('Row count mismatch')
    original=json.loads(preview.read_text(encoding='utf8'))
    if original.get('source_export_receipt')!=digest or original.get('automatic_publication') is not False:
        raise ValueError('Preview source/private-only boundary mismatch')
    byid={x['drive_file_id']:x for x in rows}
    old={x['drive_file_id']:x for x in original['rows']}
    if len(rows)!=len(byid) or len(rows)!=len(old) or set(byid)!=set(old):
        raise ValueError('Duplicate ID or mismatch between preview and inventory')
    classified=[]
    for x in rows:
        oldrow=old[x['drive_file_id']]
        if any(x[k]!=oldrow[k] for k in ('project_id','original_filename','mime_type')):
            raise ValueError('Inventory/preview content mismatch')
        seen={x['drive_file_id']};parents=x.get('parent_ids',[]);hops=0
        while parents:
            if len(parents)!=1:raise ValueError('Multiple or ambiguous parent paths')
            parent=parents[0];hops+=1
            if parent in x['source_root_ids']:break
            if parent in seen:raise ValueError('Cycle in Drive inventory')
            seen.add(parent)
            p=byid.get(parent)
            if not p or p['project_id']!=x['project_id'] or p['mime_type']!=FOLDER:
                raise ValueError('Missing or cross-project parent in snapshot')
            parents=p['parent_ids']
        else:raise ValueError('No registered root reached')
        classified.append({
            'candidate_id':oldrow['candidate_id'],
            'project_id':x['project_id'],
            'drive_file_id':x['drive_file_id'],
            'original_filename':x['original_filename'],
            'mime_type':x['mime_type'],
            'parent_ids':x['parent_ids'],
            'source_root_ids':x['source_root_ids'],
            'modified_time':x.get('modified_time'),
            'prior_review_status':oldrow['review_status'],
            'private_bucket':classify(x,oldrow),
            'snapshot_ancestry_verified':True,
            'snapshot_ancestry_hops':hops,
            'source_owner_authorized':False,
            'privacy_approved':False,
            'engineering_issuance_approved':False,
            'public_admission':'BLOCKED',
            'source_receipt_sha256':digest,
        })
    counts=dict(sorted(collections.Counter(x['private_bucket'] for x in classified).items()))
    return classified,{
        'schema_version':'1.0.0','source_receipt_sha256':digest,'total_rows':len(classified),
        'snapshot_ancestry_verified_rows':len(classified),
        'source_owner_authorized_rows':0,'private_classification_counts':counts,
        'outside_registered_root_exceptions':expected['registered_source_coverage']['known_sources_outside_scanned_parents'],
        'public_admissions':0,'source_originals_changed':0,
        'note':'Metadata-only heuristic; technical/revision/ownership/privacy and public approval are NOT inferred.'
    }

def main():
    ap=argparse.ArgumentParser()
    for n in ('inventory','preview','receipt','out-jsonl','out-receipt'):ap.add_argument('--'+n,required=True)
    a=ap.parse_args()
    items,counts=classify_inventory(a.inventory,a.preview,a.receipt)
    paths=[private_file(a.out_jsonl),private_file(a.out_receipt)]
    if len(set(paths))!=2 or any(p.exists() for p in paths):raise FileExistsError('No overwrite of classified run receipts')
    for path in paths:path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    contents=''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in items).encode('utf8')
    counts['classified_sha256']=hashlib.sha256(contents).hexdigest()
    for path,body in ((paths[0],contents),(paths[1],(json.dumps(counts,indent=2)+'\n').encode('utf8'))):
        fd=path.open('xb');fd.write(body);fd.close();path.chmod(0o600)
        if path.read_bytes()!=body:raise IOError('Private readback failed')
    print(json.dumps(counts,sort_keys=True))
if __name__=='__main__':main()
