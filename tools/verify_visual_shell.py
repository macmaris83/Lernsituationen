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
   for width,height in [(2000,900),(1024,768),(390,844)]:
    page.set_viewport_size({'width':width,'height':height})
    for name in ['index.html','handlungssituation.html','informieren.html','m1.html']:
     page.goto(base+name)
     document=page.locator('.footer-utils [data-document-pdf]');assert document.count()==1
     assert document.locator('svg').count()==1
     assert document.get_attribute('href')=='druckansicht.html' or 'Gesamtdruck' in document.get_attribute('href')
     assert 'Gesamtdokument als PDF' in document.inner_text()
     assert page.evaluate("getComputedStyle(document.body,'::before').backgroundImage.includes('bbs1-campus-background.png')")
     asset=page.request.get(base+'assets/bbs1-campus-background.png');assert asset.ok and asset.body()==(repo/'Vorlagen/Lernsituation_fuenf_Lernwege/assets/bbs1-campus-background.png').read_bytes()
     frame=page.locator('.shell');assert 'rgba' in frame.evaluate('e=>getComputedStyle(e).backgroundColor')
     assert page.evaluate("getComputedStyle(document.body,'::before').position==='fixed'&&getComputedStyle(document.body,'::before').backgroundSize==='cover'")
     assert abs(page.evaluate("parseFloat(getComputedStyle(document.body,'::before').width)")-width)<1
     page.evaluate('scrollTo(0,document.body.scrollHeight)')
     assert page.evaluate("getComputedStyle(document.body,'::before').top==='0px'")
     if name=='m1.html':
      assert page.locator('.material-topbar [data-document-pdf]').count()==0
      assert document.is_visible()
     if name=='informieren.html':
      page.evaluate('''()=>{const p=SOZ_PROGRESS.read(),m=SOZ_PROGRESS_META;p.o=true;for(const q of m.quiz)p.q[q.id]=[q.correct,true];for(const [id,t]of Object.entries(m.tasks))p.t[id]=t.signature;SOZ_PROGRESS.write(p);}''')
      page.locator('.task-original-preview:visible').first.click()
      assert page.locator('.task-accordion[open] .document-pdf-link').count()==0
      assert document.is_visible()
     assert page.locator('[data-document-pdf]').count()==1
     assert document.locator('xpath=following-sibling::a').first.get_attribute('href')=='lehrkraft.html'
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    page.emulate_media(media='print');assert page.evaluate("getComputedStyle(document.body,'::before').display==='none'");page.emulate_media(media='screen')
   assert not errors,errors
   print('PASS:',root.name,'full-document PDF only in bottom utilities beside teacher, also visible in materials/focus, glass surfaces, fixed full-width layer at 2000/1024/390 pixels, print background hidden',flush=True)
   context.close()
  browser.close()
finally:server.shutdown()
