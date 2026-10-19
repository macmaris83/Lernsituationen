#!/usr/bin/env python3
"""Install the shared BBS calculator without modifying lesson/progress content."""
from pathlib import Path
import argparse
import shutil
import xml.etree.ElementTree as ET

REPO=Path(__file__).resolve().parents[1]
ASSETS=('calculator-engine.js','calculator.js','calculator.css')


def install(root):
    root=Path(root)
    for name in ASSETS: shutil.copyfile(REPO/'Komponenten/Rechner'/name,root/'assets'/name)
    for page in root.glob('*.html'):
        text=page.read_text()
        if 'assets/calculator.css' not in text:
            text=text.replace('</head>','<link rel="stylesheet" href="assets/calculator.css?v=bbs-rechner-1"></head>')
        if 'assets/calculator.js' not in text:
            scripts='<script src="assets/calculator-engine.js?v=bbs-rechner-1"></script><script src="assets/calculator.js?v=bbs-rechner-1"></script>'
            text=text.replace('</body>',scripts+'</body>')
        page.write_text(text)
    manifest=root/'imsmanifest.xml'; tree=ET.parse(manifest)
    for resource in tree.getroot().iter():
        if resource.tag.split('}')[-1]!='resource':continue
        ns=resource.tag.rsplit('}',1)[0]+'}' if '}' in resource.tag else ''
        current={e.get('href') for e in resource if e.tag.split('}')[-1]=='file'}
        for name in ASSETS:
            if 'assets/'+name not in current:ET.SubElement(resource,ns+'file',{'href':'assets/'+name})
    tree.write(manifest,encoding='utf-8',xml_declaration=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('packages',type=Path,nargs='+');args=ap.parse_args()
    for package in args.packages:install(package);print('Installed calculator:',package)
