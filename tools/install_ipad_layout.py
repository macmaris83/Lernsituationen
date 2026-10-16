#!/usr/bin/env python3
"""Install the shared touch layout without changing lesson/progress content."""
from pathlib import Path
import argparse
import shutil
import xml.etree.ElementTree as ET

REPO=Path(__file__).resolve().parents[1]
ASSET='assets/ipad.css'


def install(root):
    root=Path(root)
    shutil.copyfile(REPO/'Komponenten/iPad/ipad.css',root/ASSET)
    for page in root.glob('*.html'):
        source=page.read_text()
        if ASSET not in source:
            source=source.replace('</head>','<link rel="stylesheet" href="assets/ipad.css?v=ipad-first-1"></head>')
            page.write_text(source)
    manifest=root/'imsmanifest.xml'
    tree=ET.parse(manifest)
    for resource in tree.getroot().iter():
        if resource.tag.split('}')[-1]!='resource':continue
        ns=resource.tag.rsplit('}',1)[0]+'}' if '}' in resource.tag else ''
        current={e.get('href') for e in resource if e.tag.split('}')[-1]=='file'}
        if ASSET not in current:ET.SubElement(resource,ns+'file',{'href':ASSET})
    tree.write(manifest,encoding='utf-8',xml_declaration=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('packages',type=Path,nargs='+')
    args=ap.parse_args()
    for package in args.packages:
        install(package)
        print('Installed iPad layout:',package)
