#!/usr/bin/env python3
"""Create phase-only GoodNotes imports from unchanged original PDF pages."""
from pathlib import Path
import argparse,base64,json,xml.etree.ElementTree as ET
import fitz
PHASES={'informieren':'Informieren','planen':'Planen','entscheiden':'Entscheiden','durchfuehren':'Durchführen','bewerten':'Bewerten','reflektieren':'Reflektieren'}
def prepare(root):
    data=json.loads((root/'lesson-data.js').read_text().split('=',1)[1].rstrip(';\n'))
    workbooks=data.get('workbooks') or {'1':data['workbook']}
    added=[]
    for mode,filename in workbooks.items():
        source=fitz.open(root/filename);groups={p:[] for p in PHASES};active=None
        for i,page in enumerate(source):
            lines=[s.strip() for s in page.get_text().splitlines()[:14]]
            found=[key for key,label in PHASES.items() if label in lines or any(s.endswith('-'+label) for s in lines)]
            assert len(found)<=1,(filename,i,found)
            if found:active=found[0]
            # SozPaed orientation sheets at the beginning/end are not phase tasks.
            if any(s.endswith('-Orientierung') for s in lines):active=None
            if active:groups[active].append(i)
        assert all(groups.values()),(filename,groups)
        for phase,pages in groups.items():
            pdf=fitz.open()
            for i in pages:pdf.insert_pdf(source,from_page=i,to_page=i)
            file=f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf';pdf.save(root/file,garbage=4,deflate=True);pdf.close()
            check=fitz.open(root/file)
            assert len(check)==len(pages)
            for index,original in enumerate(pages):assert check[index].get_text()==source[original].get_text()
            for page in check:
                lines=page.get_text().splitlines()[:14]
                for other,label in PHASES.items():
                    if other!=phase:assert label not in lines and not any(s.strip().endswith('-'+label) for s in lines)
            check.close()
            script=f'goodnotes-phase-{phase}-W{mode}.js'
            payload={f'{phase}:{mode}':base64.b64encode((root/file).read_bytes()).decode()}
            (root/script).write_text('window.GOODNOTES_PHASES=Object.assign(window.GOODNOTES_PHASES||{},'+json.dumps(payload)+');\n')
            added.extend([file,script])
        source.close()
    path=root/'imsmanifest.xml';tree=ET.parse(path);resource=next(n for n in tree.getroot().iter() if n.tag.split('}')[-1]=='resource')
    ns=resource.tag.split('}')[0][1:];existing={n.get('href') for n in resource if n.tag.split('}')[-1]=='file'}
    for name in added:
        if name not in existing:ET.SubElement(resource,'{'+ns+'}file',{'href':name})
    ET.register_namespace('',ns)
    ET.register_namespace('adlcp','http://www.adlnet.org/xsd/adlcp_rootv1p2')
    tree.write(path,encoding='utf-8',xml_declaration=True)
    print(f'Prepared {len(added)//2} phase-only workbooks in {root.name}')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('--regenerate-masters',action='store_true',help='PDF- und eingebettete Arbeitsheftdateien im Master neu erzeugen')
    args=parser.parse_args()
    if not args.regenerate_masters:
        parser.error('Normaler Export: python tools/master.py export --all. Eine Neuerzeugung der Master-Arbeitshefte erfordert --regenerate-masters.')
    prepare(args.folder)
