from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from playwright.sync_api import sync_playwright
import fitz
import re
import os
import shutil
BASE=Path(os.environ.get('BFS_REPO',Path(__file__).resolve().parents[2])).resolve()
BFS=BASE/'Fachbereiche/BFSdual'
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):
  self.send_header('Cache-Control','no-store');super().end_headers()
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=BASE))
Thread(target=server.serve_forever,daemon=True).start()
origin=f'http://127.0.0.1:{server.server_port}/'
phases=('informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren')
def inspect_pdf(data):
 d=fitz.open(stream=data,filetype='pdf')
 assert len(d)>0
 assert all(s.get_text().strip() or s.get_images() for s in d),'Leerseite'
 return ' '.join(' '.join(s.get_text() for s in d).split())
def case(d):
 old=d.name=='LS09';ls='6.9' if old else f'{int(d.parent.name[2:])}.{int(d.name[2:])}'
 url=origin+quote(d.relative_to(BASE).as_posix())+'/'
 def addr(phase):return url+('index.html#'+phase if old else phase+'.html')
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ.get('BFS_CHROMIUM') or shutil.which('chromium'),args=['--no-sandbox'])
  page=b.new_page(viewport={'width':390,'height':850},accept_downloads=True)
  page.add_init_script("Object.defineProperty(navigator,'share',{value:undefined})")
  errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
  errors_response=[];page.on('response',lambda r: errors_response.append(r.url) if r.status>=400 else None)
  page.goto(addr('index'))
  assert not page.get_by_text('GoodNotes-Export',exact=True).is_visible()
  page.goto(addr('handlungssituation'))
  assert not page.get_by_text('GoodNotes-Export',exact=True).is_visible()
  page.get_by_role('link',name='Gesamtdokument als PDF').last.wait_for()
  nav=page.get_by_role('link',name='Gesamtdokument als PDF').last
  nav.scroll_into_view_if_needed();nr=nav.bounding_box()
  assert nr['x']>130,(ls,nr)
  for phase in phases:
   page.goto(addr(phase))
   if phase=='durchfuehren':
    page.get_by_text(re.compile('Wähle .*zuerst deinen Lernweg')).wait_for()
    for path in 'ABC':
     page.goto(addr('entscheiden'))
     if old:page.locator('[data-save="paket"]').select_option(path)
     else:page.locator(f'input[name="lernweg"][value="{path}"]').check()
     page.goto(addr(phase))
     link=page.get_by_role('link',name='GoodNotes-Export')
     assert link.count()==1,(ls,phase,path)
     with page.expect_download() as event:link.click()
     pdf=event.value
     assert pdf.suggested_filename==f'GoodNotes-LS-{ls}-{phase}-{path}.pdf'
     text=inspect_pdf(pdf.path().read_bytes())
     assert f'Lernweg {path}' in text,(ls,phase,path)
     assert all(f'Lernweg {x}' not in text for x in 'ABC' if x!=path)
   else:
    with page.expect_download() as event:page.get_by_role('link',name='GoodNotes-Export').click()
    pdf=event.value
    assert pdf.suggested_filename==f'GoodNotes-LS-{ls}-{phase}.pdf'
    text=inspect_pdf(pdf.path().read_bytes())
    assert 'Notizen' in text or '5-mm-Karo' in text
  page.get_by_role('link',name='Gesamtdokument als PDF').click()
  page.wait_for_function("document.querySelector('#pdf-lernweg')?.value === 'C'",timeout=7000)
  assert page.locator('[data-pdf-path="A"]:visible').count()==0
  assert page.locator('[data-pdf-path="C"]:visible').count()>0
  page.evaluate("window.print=()=>window.printCalled=true")
  page.locator('[data-print-document]').click()
  page.wait_for_function('window.printCalled===true')
  with page.expect_download() as event:page.get_by_role('link',name='PDF mit allen Lernwegen herunterladen').click()
  assert len(inspect_pdf(event.value.path().read_bytes()))>1000
  if not old:
   for route in ('index','handlungssituation','begriffstraining',*phases):
    page.goto(addr(route))
    try:inspect_pdf(page.pdf(prefer_css_page_size=True,print_background=True))
    except AssertionError as e:raise AssertionError((ls,route,str(e))) from e
  assert not errors,(ls,errors)
  assert not errors_response,(ls,errors_response)
  print(ls,'Phasen-Downloads A/B/C, Gesamtdokument, Fußleiste, A4 ohne Leerseiten',flush=True)
  b.close()
selected=set(os.environ.get('BFS_PDF_CASES','').split())
folders=[*sorted(BFS.glob('LF0[123]/LS*')),BFS/'LF06/Buero/LS09']
if selected:
 folders=[d for d in folders if ('6.9' if d.name=='LS09' else f'{int(d.parent.name[2:])}.{int(d.name[2:])}') in selected]
with ThreadPoolExecutor(3) as pool:
 list(pool.map(case,folders))
