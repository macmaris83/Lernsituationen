#!/usr/bin/env python3
"""Export only masters affected by a push; preserve deliberately removed old downloads."""
import argparse,json,subprocess
from pathlib import Path
import master
ROOT=Path(__file__).resolve().parents[1]
def selected_ids(root,base):
    current=master.catalog(root)
    if not base or set(base)=={'0'}:return [p['id'] for p in current['packages']]
    previous=json.loads(subprocess.check_output(['git','show',base+':master-katalog.json'],cwd=root,text=True))
    old={p['id']:p for p in previous['packages']}
    changed=subprocess.check_output(['git','diff','--name-only',base,'HEAD'],cwd=root,text=True).splitlines()
    return [p['id'] for p in current['packages'] if p!=old.get(p['id']) or any(name.startswith(p['master']+'/') for name in changed)]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base');args=ap.parse_args()
    ids=selected_ids(ROOT,args.base)
    if not ids:print('Keine geänderten Master; bestehende Downloads bleiben erhalten.');return
    print('Betroffene Master: '+', '.join(ids))
    master.export(ROOT,ids);master.check(ROOT,archives=True,selected=ids)
if __name__=='__main__':main()
