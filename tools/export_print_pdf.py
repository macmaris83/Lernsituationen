#!/usr/bin/env python3
"""Render the current master print view as a complete A4 PDF without rebuilding content."""
import argparse
import functools
import http.server
from pathlib import Path
import threading
import xml.etree.ElementTree as ET
import fitz
from playwright.sync_api import sync_playwright

REPO=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('packages',type=Path,nargs='+')
    args=ap.parse_args()
    roots=[p.resolve() for p in args.packages]
    for root in roots:
        if not root.is_relative_to(REPO) or not (root/'druckansicht.html').is_file():
            ap.error(f'No current print master inside this repository: {root}')
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(REPO)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for root in roots:
                context=browser.new_context()
                page=context.new_page();page.emulate_media(media='print')
                page.goto(f'http://127.0.0.1:{server.server_port}/'+root.relative_to(REPO).as_posix()+'/druckansicht.html')
                page.wait_for_function('window.SOZ_READY===true&&!!window.SOZ_PRINT')
                page.evaluate('async()=>{await SOZ_PRINT.ready();}')
                target=root/'pdf/Gesamtdokument_A4.pdf';target.parent.mkdir(exist_ok=True)
                page.pdf(path=str(target),print_background=True,prefer_css_page_size=True,display_header_footer=False)
                context.close()
                with fitz.open(target) as document:
                    for number,sheet in enumerate(document,1):
                        if abs(sheet.rect.width-595.276)>1 or abs(sheet.rect.height-841.89)>1:
                            raise ValueError(f'{root}: page {number} is not A4')
                        if not sheet.get_text().strip() and not sheet.get_images():
                            raise ValueError(f'{root}: page {number} is empty')
                manifest=root/'imsmanifest.xml';tree=ET.parse(manifest)
                for resource in tree.getroot().iter():
                    if resource.tag.split('}')[-1]!='resource':continue
                    ns=resource.tag.rsplit('}',1)[0]+'}' if '}' in resource.tag else ''
                    if not any(node.tag.split('}')[-1]=='file' and node.get('href')=='pdf/Gesamtdokument_A4.pdf' for node in resource):
                        ET.SubElement(resource,ns+'file',{'href':'pdf/Gesamtdokument_A4.pdf'})
                tree.write(manifest,encoding='utf-8',xml_declaration=True)
                print('Rendered current A4 PDF:',root.relative_to(REPO),flush=True)
            browser.close()
    finally:server.shutdown();server.server_close()


if __name__=='__main__':main()
