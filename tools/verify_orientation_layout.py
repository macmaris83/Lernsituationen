#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,functools,http.server,threading
parser=argparse.ArgumentParser();parser.add_argument('folders',nargs='+',type=Path);args=parser.parse_args();repo=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(repo.parent)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for root in args.folders:
   base=f'http://127.0.0.1:{server.server_port}/'+root.resolve().relative_to(repo.parent).as_posix()+'/'
   context=browser.new_context();page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   for width,height in [(1024,768),(768,1024),(390,844)]:
    page.set_viewport_size({'width':width,'height':height});page.goto(base+'index.html')
    chart=page.locator('.orientation-competence-chart');details=page.locator('.orientation-competence-list');assert chart.count()==details.count()==1
    assert details.locator(':scope>div,:scope>article').count()==5
    assert details.locator('p').count()==0
    assert details.inner_text().count('kompetenz')==5
    assert page.evaluate("SOZPAED.competencies.every(c=>c.statement.startsWith('Ich '))")
    assert page.locator('.competence-overview>p,.priority-section>p').count()==0
    assert page.locator('.material-access,.phase-materials').count()==0
    assert page.locator('[data-share-workbook]').count()==0
    c=chart.bounding_box();d=details.bounding_box();assert chart.locator('svg').bounding_box()['width']<=421
    if width>600:assert d['x']>=c['x']+c['width']+20
    else:assert d['y']>c['y']
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    page.locator('[data-orientation-complete]').check();page.reload();assert page.locator('[data-orientation-complete]').is_checked()
    if width==1024:
     page.locator('.orientation-competence-layout').scroll_into_view_if_needed();name='Businessplan' if 'BRC' in root.name else 'Sozialpaedagogik'
     page.locator('.orientation-competence-layout').locator('..').screenshot(path=str(repo/'Pruefberichte'/f'{name}_Orientierung_Kompetenzen.png'))
   assert not errors,errors
   print('PASS:',root.name,'chart <=420px, five competency names alongside, no duplicate statement, responsive, orientation completion retained',flush=True)
   context.close()
  browser.close()
finally:server.shutdown()
