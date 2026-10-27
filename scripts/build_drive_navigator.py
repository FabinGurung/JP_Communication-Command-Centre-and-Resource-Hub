#!/usr/bin/env python3
"""Build a private, single-file human navigator outside the public checkout.

The public files/index.html is only an empty application shell. Input files are
private, derived navigation metadata, never a second owner of spreadsheet facts.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDER='application/vnd.google-apps.folder'
SHEET='application/vnd.google-apps.spreadsheet'
ARCHIVE=re.compile(r'ARCHIVE|VERSION[ _]HISTORY|PREVIOUS|RECYCLE|SNAPSHOT|BACKUP|SUPERSEDED|RETIRED|HISTORICAL|ROLLBACK|(?:^|/)(?:PRE|POST)[0-9]?_',re.I)

def assemble(rows:list[dict],spec:dict)->dict:
    by_id={}
    for row in rows:
        ident=row['drive_file_id']
        if ident in by_id:raise ValueError('Duplicate file ID in inventory')
        by_id[ident]=row
    root=spec['root']
    if root not in by_id:raise ValueError('Missing inventory root')
    overrides=spec.get('name_overrides',{})
    for ident,name in overrides.items():
        if ident not in by_id:raise ValueError('Unknown rename ID')
        by_id[ident]={**by_id[ident],'name':name}
    memo={}
    def path_for(ident,visiting=None):
        if ident in memo:return memo[ident]
        visiting=set() if visiting is None else visiting
        if ident in visiting:raise ValueError('Inventory parent cycle')
        visiting.add(ident)
        item=by_id[ident];parent=item['parent_drive_id']
        if ident==root:
            if parent is not None:raise ValueError('Root has parent inside snapshot')
            result=item['name']
        else:
            if parent not in by_id:raise ValueError('Missing inventory parent')
            result=path_for(parent,visiting)+'/'+item['name']
        visiting.remove(ident);memo[ident]=result;return result
    entries=[]
    for ident,row in by_id.items():
        path=path_for(ident)
        if '98_INTAKE_STAGING' in path:raise ValueError('Excluded staging folder in navigation input')
        url=row.get('url')
        if not url:
            if not re.fullmatch(r'[A-Za-z0-9_-]+',ident):raise ValueError('Invalid file identity')
            url=('https://drive.google.com/drive/folders/'+ident if row['mime_type']==FOLDER else 'https://docs.google.com/spreadsheets/d/'+ident+'/edit' if row['mime_type']==SHEET else 'https://drive.google.com/file/d/'+ident+'/view')
        if not url.startswith(('https://drive.google.com/','https://docs.google.com/','https://colab.research.google.com/')):raise ValueError('Invalid original file URL')
        entries.append(dict(id=ident,name=row['name'],parent=row['parent_drive_id'],kind='folder' if row['mime_type']==FOLDER else 'sheet' if row['mime_type']==SHEET else 'file',url=url,historical=bool(ARCHIVE.search(path)),description=spec.get('descriptions',{}).get(ident,'')))
    fields=['root','updated','inventoryAt','inventoryNotice','sheets','stagedCount','master','scope','renameCount','codeUrl','actionsUrl']
    result=dict(format='JP_HUMAN_NAVIGATOR_V1',entries=entries,**{k:spec[k] for k in fields})
    if 'websiteDirectory' in spec:result['websiteDirectory']=spec['websiteDirectory']
    return result

def build(inventory:Path,spec:Path,output:Path,shell:Path=ROOT/'files/index.html'):
    if output.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Private navigator must be written outside the public repository')
    rows=[json.loads(line) for line in inventory.read_text(encoding='utf-8').splitlines() if line.strip()]
    payload=assemble(rows,json.loads(spec.read_text(encoding='utf-8')))
    value=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    source=shell.read_text(encoding='utf-8')
    marker='<script id="navigator-data" type="application/json">null</script>'
    if source.count(marker)!=1:raise ValueError('Public shell must have one empty data marker')
    html=source.replace(marker,'<script id="navigator-data" type="application/json">'+value+'</script>')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(html,encoding='utf-8')
    print(f'PRIVATE_NAVIGATOR_BUILT: {len(rows)} linked inventory entries; no Sheet cells copied')
    return payload

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory',type=Path,required=True)
    p.add_argument('--spec',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    build(a.inventory,a.spec,a.output)
