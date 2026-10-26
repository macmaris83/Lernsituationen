#!/usr/bin/env python3
"""Reproducible, content-preserving footer patch for the approved 1.8 reference."""
from pathlib import Path
import argparse, hashlib, io, json, re, os, zipfile, copy
ROOT=Path(__file__).resolve().parents[1]
FOOTERS={f'assets/footer-{n}.svg' for n in range(3,7)}
FRAME=re.compile(r'<rect fill="#FFFFFF"[^>]*stroke="#009BD9"[^>]*></rect>')
def icon(data):
    text=data.decode('utf-8');updated,count=FRAME.subn('',text,count=1)
    if count != 1: raise ValueError('Expected exactly one inner icon frame')
    return updated.encode('utf-8')
def patch(data):
    source=zipfile.ZipFile(io.BytesIO(data));assert source.testzip() is None
    metadata=json.loads(source.read('Paketversion.json'))
    if metadata['version']!='1.8':raise ValueError('Expected version 1.8')
    metadata['version']='1.8.1';metadata['styleRevision']='footer-ohne-inneren-rahmen'
    changed={name:icon(source.read(name)) for name in FOOTERS}
    changed['Paketversion.json']=(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n').encode()
    result=io.BytesIO()
    with zipfile.ZipFile(result,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
        for item in source.infolist():target.writestr(copy.copy(item),changed.get(item.filename,source.read(item.filename)))
    output=result.getvalue()
    with zipfile.ZipFile(io.BytesIO(output)) as check:
        assert check.testzip() is None
        assert set(check.namelist())==set(source.namelist())
        assert {n for n in check.namelist() if check.read(n)!=source.read(n)}==FOOTERS|{'Paketversion.json'}
    return output

def write_atomic(path,data):
    temp=path.with_suffix('.tmp');temp.write_bytes(data);os.replace(temp,path)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'Lieferungen/BioCasa_LG01')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    folder=ROOT/'Lieferungen/BioCasa_LG01'
    source=folder/'BRC_LG01_LS04_v1.8_SCORM12.zip'
    target=args.output/'BRC_LG01_LS04_v1.8.1_SCORM12.zip'
    output=patch(source.read_bytes());write_atomic(target,output)
    old=zipfile.ZipFile(folder/'BioCasa_LG01_LS04-LS06_v1.8.zip');bundle=args.output/'BioCasa_LG01_LS04-LS06_v1.8.1.zip';tmp=bundle.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for item in old.infolist():
            if item.filename==source.name:
                entry=copy.copy(item);entry.filename=target.name;z.writestr(entry,output)
            elif item.filename=='README.txt':z.writestr(copy.copy(item),old.read(item.filename).decode().replace('LS04_v1.8_SCORM12','LS04_v1.8.1_SCORM12')+'\nLS04 1.8.1: ausschließlich zusätzliche innere Rahmen der vier rechten Fußsymbole entfernt. LS05 und LS06 unverändert in 1.7.\n')
            else:z.writestr(copy.copy(item),old.read(item.filename))
    with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
    os.replace(tmp,bundle)
    for p in [target,bundle]:print(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p,hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':main()
