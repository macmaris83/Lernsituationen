#!/usr/bin/env python3
"""Install the shared A4 print layout; preserve lesson data, settings and progress."""
from pathlib import Path
import argparse
import json
import shutil
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
ASSETS = {'print.css': 'print-layout.css', 'print.js': 'print-layout.js'}
PRINTER = '<svg class="document-print-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8V3h12v5M6 17H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v7H6zM18 11h.01"/></svg>'
GEAR = '<svg class="editor-settings-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 3-1 3-3 1-2 3 2 2-1 3 2 3 3-1 2 2h3l1-3 3-1 2-3-2-2 1-3-2-3-3 1-2-2z"/><circle cx="12" cy="11" r="3"/></svg>'


def patch_runtime(root):
    path = root / 'assets/runtime.js'
    source = path.read_text()
    start = source.index('function decorateDocumentPDF(){')
    end = source.index('function phaseWorkbook()', start)
    printer = json.dumps(PRINTER + '<span class="document-pdf-label">Gesamtdokument als PDF</span>', ensure_ascii=False)
    editor = json.dumps(GEAR + '<span>Editor</span>', ensure_ascii=False)
    replacement = '''function decorateDocumentPDF(){
 const links=[...document.querySelectorAll('.footer-utils a[href]')].filter(a=>a.hasAttribute('data-document-pdf')||a.getAttribute('href').split('?')[0]==='druckansicht.html'||(/^pdf\\//i.test(a.getAttribute('href'))&&/Gesamtdruck|Gesamtdokument/i.test(a.getAttribute('href'))));
 for(const a of links){a.dataset.documentPdf='';a.href='druckansicht.html';a.removeAttribute('target');a.removeAttribute('download');a.innerHTML=PRINTER_HTML;a.title='Gesamtes Dokument auf A4 drucken oder als PDF speichern';a.setAttribute('aria-label','Gesamtdokument als PDF öffnen und drucken');}
 for(const a of document.querySelectorAll('.footer-utils a[href="lehrkraft.html"]')){a.innerHTML=EDITOR_HTML;a.setAttribute('aria-label','Editor öffnen');a.title='Editor öffnen';}
 window.SOZ_DOCUMENT_PDF={makeLink(compact=false){const original=links[0];if(!original)return null;const a=original.cloneNode(true);a.className='button document-pdf-link'+(compact?' document-pdf-compact':'');if(compact)a.querySelector('.document-pdf-label')?.remove();a.setAttribute('aria-label','Gesamtdokument als PDF öffnen und drucken');return a;}};
}
'''.replace('PRINTER_HTML', printer).replace('EDITOR_HTML', editor)
    source = source[:start] + replacement + source[end:]
    # The tradiert master already has an asynchronous font/image handler;
    # replace the complete known binding rather than only its synchronous form.
    binding = source.index("$$('[data-print]').forEach(")
    after_binding = source.index(';status(', binding)
    source = source[:binding] + "$$('[data-print]').forEach(e=>e.addEventListener('click',()=>window.SOZ_PRINT?window.SOZ_PRINT.print():window.print()))" + source[after_binding:]
    source = source.replace("function layoutOrientationCompetencies(){if(document.body.dataset.page!=='index.html')return;", "function layoutOrientationCompetencies(){if(!['index.html','druckansicht.html'].includes(document.body.dataset.page))return;")
    old_key = "const k=page+':'+(e.dataset.workId||i);"
    source_key = "const chapter=e.closest('[data-print-source]'),sourcePage=chapter?.dataset.printSource||page,number=chapter?[...chapter.querySelectorAll('input[data-work-surface],textarea[data-work-surface],[contenteditable=true][data-work-surface]')].indexOf(e):i;const k=sourcePage+':'+(e.dataset.workId||number);"
    source = source.replace(old_key, source_key)
    path.write_text(source)
    teacher = root / 'assets/teacher-view.js'
    if teacher.exists():
        teacher.write_text(teacher.read_text().replace("a.textContent='Editor';", 'a.innerHTML=' + editor + ';'))
    lesson = root / 'assets/lg01.js'
    if lesson.exists():
        text = lesson.read_text()
        if 'const printView=' not in text:
            text = text.replace('const D=window.SOZPAED;if(!D)return;', "const D=window.SOZPAED;if(!D)return;const printView=document.body.dataset.page==='druckansicht.html';", 1)
        text = text.replace('det.open=read(k,false);det.addEventListener', 'det.open=printView||read(k,false);if(!printView)det.addEventListener')
        text = text.replace("const key=document.body.dataset.page+':'+det.dataset.microId", "const key=(det.closest('[data-print-source]')?.dataset.printSource||document.body.dataset.page)+':'+det.dataset.microId")
        text = text.replace('det.open=!!saved.open;', 'det.open=printView||!!saved.open;')
        if 'if(printView){show();continue;}' not in text:
            text = text.replace(" det.addEventListener('toggle',()=>store(key,state()));", " if(printView){show();continue;}\n det.addEventListener('toggle',()=>store(key,state()));")
        lesson.write_text(text)


def install(root):
    root = Path(root)
    patch_runtime(root)
    for source, target in ASSETS.items():
        shutil.copyfile(REPO / 'Komponenten/Druckansicht' / source, root / 'assets' / target)
    for page in root.glob('*.html'):
        source = page.read_text()
        # Last stylesheet wins over legacy print and tablet styles. Runtime and
        # lesson scripts restore editor/media state before this final script.
        if 'assets/print-layout.css' not in source:
            source = source.replace('</head>', '<link rel="stylesheet" href="assets/print-layout.css?v=a4-print-1"></head>')
        if 'assets/print-layout.js' not in source:
            source = source.replace('</body>', '<script src="assets/print-layout.js?v=a4-print-1"></script></body>')
        page.write_text(source)
    manifest = root / 'imsmanifest.xml'
    tree = ET.parse(manifest)
    for resource in tree.getroot().iter():
        if resource.tag.split('}')[-1] != 'resource':
            continue
        ns = resource.tag.rsplit('}', 1)[0] + '}' if '}' in resource.tag else ''
        current = {element.get('href') for element in resource if element.tag.split('}')[-1] == 'file'}
        for target in ASSETS.values():
            href = 'assets/' + target
            if href not in current:
                ET.SubElement(resource, ns + 'file', {'href': href})
    tree.write(manifest, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packages', type=Path, nargs='+')
    args = parser.parse_args()
    for package in args.packages:
        install(package)
        print('Installed A4 print layout:', package)
