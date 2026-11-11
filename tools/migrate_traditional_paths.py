#!/usr/bin/env python3
"""Bounded, idempotent removal of W2–W5 from the current registered LS masters.

This is a subtractive migration, never a generator. W1 task bodies, signatures,
storage identities and PDFs are checked against the original GitHub checkout.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path
import w1_content_patch as content
import w1_runtime_patch as runtime
import w1_embedded_patch as embedded
import w1_tools_patch as sources
import check_traditional_paths as checks

ROOT = Path(__file__).resolve().parents[1]
REMOVED = re.compile(r'(?:^|[-_/])W(?:eg)?[2-5](?=[._/-]|$)', re.I)
TEXT = {'.html','.js','.cjs','.css','.json','.xml','.md','.txt'}
REPORT = 'tools/fixtures/traditional-path-migration.json'
FIXTURE = 'tools/fixtures/traditional-path-baseline.json'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def obsolete(path):
    return bool(REMOVED.search(path)) or Path(path).name=='README_5_STUFEN.txt'

def convert_master(root, master):
    """Convert one existing master in place; public for intentional regeneration."""
    folder=root/master
    original_pdfs={str(p.relative_to(folder)):digest(p) for p in folder.rglob('*.pdf') if not obsolete(str(p.relative_to(folder)))}
    removed=[]; changed=[]
    for p in sorted(folder.rglob('*')):
        if not p.is_file():continue
        relative=p.relative_to(folder).as_posix();repo_path=p.relative_to(root).as_posix()
        if obsolete(relative):
            p.unlink();removed.append(relative);continue
        if p.suffix not in TEXT:continue
        before=p.read_text(encoding='utf-8');after=before
        for module in (content,runtime,embedded):after=module.transform(repo_path,after)
        if p.name=='imsmanifest.xml':
            after=re.sub(r'<file\b[^>]*\bhref=[\"\']([^\"\']+)[\"\'][^>]*(?:/>|>\s*</file>)',lambda m:'' if obsolete(m.group(1)) else m.group(0),after)
        if after!=before:
            p.write_text(after,encoding='utf-8');changed.append(relative)
    for rel,sha in original_pdfs.items():
        assert (folder/rel).is_file() and digest(folder/rel)==sha,(master,'W1/shared PDF changed',rel)
    return {'master':master,'removedFiles':removed,'changedFiles':changed,'preservedPdfs':original_pdfs}

def main(root=ROOT):
    marker=root/REPORT
    if marker.exists():
        print('Traditional-path migration already applied; preservation checks run separately.')
        return
    catalog_path=root/'master-katalog.json';catalog=json.loads(catalog_path.read_text())
    targets=[p for p in catalog['packages'] if p['typ']=='Lernsituation' or p['id']=='VORLAGE-TRADIERT']
    before={p['id']:checks.capture(root,p) for p in targets}
    fixture=root/FIXTURE
    if fixture.exists():assert json.loads(fixture.read_text())==before,'Preservation baseline differs from current source.'
    else:
        fixture.parent.mkdir(parents=True,exist_ok=True)
        fixture.write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
    reports=[]
    for item in targets:
        report=convert_master(root,item['master'])
        assert checks.capture(root,item)==before[item['id']],(item['id'],'W1 content/identity changed')
        if report['changedFiles'] or report['removedFiles']:
            version=item['version'].split('.');version[-1]=str(int(version[-1])+1);item['version']='.'.join(version)
            vp=root/item['master']/'Paketversion.json';v=json.loads(vp.read_text());v.update(version=item['version'],updated='2026-11-11',changes='Ausschließlich tradierter Lernweg 1. Alternative Aufgaben, Lernwege und PDF-Dateien entfernt; W1-Aufgaben, Kennungen, PDFs und vorhandene Lernstände erhalten.')
            vp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
        report.update(id=item['id'],version=item['version'],preservedTaskCount=len(before[item['id']]['tasks']))
        reports.append(report)
        print(item['id'],':',len(report['removedFiles']),'obsolete files removed;',report['preservedTaskCount'],'W1 tasks preserved',flush=True)
    for path in ['tools/test_form185_browser.cjs','tools/test_form185.cjs','tools/test_idn_completion.cjs','tools/verify_brc_editorial.py','tools/build_brc_series.py','tools/verify_brc_series.py','Fachbereiche/BRC/LG01/quellen/Reihenplan.md','Fachbereiche/BRC/LG01/quellen/Arbeitsformen.json']:
        p=root/path;p.write_text(sources.transform(path,p.read_text()),encoding='utf-8')
    p=root/'Fachbereiche/BRC/LG01/README.md'
    t=p.read_text().replace('jeweils fünf alternative Lernwege','jeweils ausschließlich der tradierte Lernweg 1').replace('fünf Lernwege','den tradierten Lernweg 1')
    p.write_text(t)
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    marker.write_text(json.dumps({'sourceCommit':'581506d3d513f8b0fbac0f69e569fa126ca8a6b0','policy':'Nur W1; Fachinhalte, Aufgabenkennungen, Signaturen und W1-PDFs unverändert','packages':reports},ensure_ascii=False,indent=2)+'\n')
    subprocess.run(['python3',str(root/'tools/check_traditional_paths.py'),'--root',str(root)],check=True)

if __name__=='__main__':main()
