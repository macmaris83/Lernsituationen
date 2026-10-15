from pathlib import Path
from playwright.sync_api import sync_playwright
import functools,http.server,threading,argparse
repo=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('folders',nargs='*',type=Path);args=parser.parse_args();folders=args.folders or [repo/'Vorlagen/Lernsituation_tradiert',repo/'Vorlagen/Lernsituation_fuenf_Lernwege']
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(repo.parent)));threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for target in folders:
   folder=target.resolve().relative_to(repo.parent).as_posix()
   context=browser.new_context(viewport={'width':1024,'height':768});context.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new DOMException('Denied','SecurityError')}})");page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base+folder+'/informieren.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'")
   page.evaluate('''()=>{const p=SOZ_PROGRESS.read(),m=SOZ_PROGRESS_META;for(const q of m.quiz)p.q[q.id]=[q.correct,true];p.o=true;for(const [id,t]of Object.entries(m.tasks))p.t[id]=t.signature;SOZ_PROGRESS.write(p);}''')
   assert page.locator('.material-grid').first.evaluate('e=>e.scrollWidth<=e.clientWidth+1')
   first=page.locator('.assignment-frame:visible').first
   assert first.evaluate("e=>getComputedStyle(e).minHeight==='0px'")
   assert first.evaluate('e=>e.getBoundingClientRect().height>=e.querySelector(".focus-symbol-strip").getBoundingClientRect().height')
   if 'BRC_' in folder:
    assert first.bounding_box()['height']<170
    first.scroll_into_view_if_needed();page.screenshot(path=str(repo/'Pruefberichte/BRC_LG01_LS03_Kompakte_Karten.png'))
   page.locator('.task-original-preview:visible').first.click();task=page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')
   page.locator('.phase-materials a[href^="m1.html"],.material-access a[href^="m1.html"]').first.click()
   materials=page.locator('.material-switch a').count()
   for width,height in [(1024,768),(768,1024),(390,844)]:
    page.set_viewport_size({'width':width,'height':height})
    for i in range(1,materials+1):
     if i>1:
      page.locator('.material-switch summary').click();page.locator(f'.material-switch a[href^="m{i}.html"]').click()
     assert page.locator('.return-task-inline,.material-phase-turn').count()==0
     assert page.locator('.material-topbar [data-document-pdf]').count()==0
     assert page.locator('.footer-utils [data-document-pdf]').is_visible()
     assert page.locator('.return-task').is_visible()
     for scroll in [0,500,2000]:
      page.evaluate('(y)=>scrollTo(0,y)',scroll)
      rect=page.locator('.return-task').bounding_box();assert 0<=rect['y'] and rect['y']+rect['height']<=height
      assert page.locator('.return-task').evaluate('e=>{const r=e.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2).closest(".return-task")===e}')
     assert page.locator('.lesson-content>.hero').is_hidden()
     page.locator('.material-switch summary').click()
     assert page.locator('.material-switch>nav').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
     assert page.locator('.material-switch a').last.is_visible()
     page.locator('.material-switch summary').click()
     assert page.locator('.material-phase-navigation').bounding_box()['y']>page.locator('.lesson-content').bounding_box()['y']
     assert page.evaluate('SOZ_MATERIAL_RETURN.read().task')==task
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    page.goto(base+folder+'/m1.html?rueckaufgabe='+task.replace(':','%3A'))
   page.set_viewport_size({'width':1024,'height':768})
   # A WebView keyboard/zoom narrows the visible viewport without changing layout height.
   page.evaluate("()=>{const v=visualViewport;Object.defineProperty(v,'height',{configurable:true,value:588});Object.defineProperty(v,'offsetTop',{configurable:true,value:40});v.dispatchEvent(new Event('resize'));}")
   rect=page.locator('.return-task').bounding_box();assert rect['y']+rect['height']<=628
   page.evaluate("()=>{delete visualViewport.height;delete visualViewport.offsetTop;visualViewport.dispatchEvent(new Event('resize'));}")
   if 'BRC_' in folder:page.screenshot(path=str(repo/'Pruefberichte/BRC_LG01_LS03_Materialansicht.png'))
   page.locator('.return-task').click();page.wait_for_function("document.body.dataset.taskFocusReady==='true'")
   assert page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')==task
   page.goto(base+folder+'/m1.html?rueckaufgabe=constructor');assert page.locator('.return-task').get_attribute('aria-disabled')=='true'
   assert not errors,errors
   print('PASS:',folder,'all materials at three widths, blocked storage, exact return, no overflow, compact cards',flush=True)
   context.close()
  browser.close()
finally:server.shutdown()
