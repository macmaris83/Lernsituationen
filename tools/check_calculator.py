#!/usr/bin/env python3
"""Exercise the calculator inside real SCORM iframes, including touch dragging."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

REPO=Path(__file__).resolve().parents[1]


def check(browser,server,root,reports):
    base=f'http://127.0.0.1:{server.server_port}/'+root.relative_to(REPO).as_posix()+'/'
    context=browser.new_context(viewport={'width':1024,'height':768},has_touch=True,reduced_motion='reduce')
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'scorm.html')
    page.wait_for_function('document.querySelector("iframe")?.contentWindow?.SOZ_READY===true')
    frame=next(f for f in page.frames if f!=page.main_frame)
    assert frame.locator('.bbs-calculator-launcher').count()==0,'No introductory calculator overlay'
    frame.evaluate('''()=>{const p=SOZ_PROGRESS.read();p.o=true;for(const q of SOZ_PROGRESS_META.quiz)p.q[q.id]=[q.correct,true];SOZ_PROGRESS.write(p);}''')
    frame.goto(base+'informieren.html');frame.wait_for_function('window.SOZ_READY===true')
    launcher=frame.locator('.bbs-calculator-launcher');assert launcher.is_visible()
    assert frame.locator('.bbs-calculator').is_hidden(),'Closed by default'
    previous=frame.evaluate('JSON.stringify(SOZ_PROGRESS.read())')
    launcher.tap();panel=frame.locator('.bbs-calculator');assert panel.is_visible()
    def keys(sequence):
        for key in sequence:frame.locator(f'.bbs-calc-key[data-key="{key}"]').tap()
    keys(['AC','2','0','0','+','1','0','%','='])
    assert frame.locator('.bbs-calc-display').inner_text()=='220'
    keys(['AC','0',',','1','+','0',',','2','='])
    assert frame.locator('.bbs-calc-display').inner_text()=='0,3'
    assert frame.evaluate('JSON.stringify(SOZ_PROGRESS.read())')==previous,'No calculator writes to assessed progress'
    before=panel.bounding_box();handle=frame.locator('.bbs-calc-drag');h=handle.bounding_box();x=h['x']+h['width']/2;y=h['y']+h['height']/2
    scroll=frame.evaluate('scrollY');cdp=context.new_cdp_session(page)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]})
    for step in range(1,7):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+100*step/6,'y':y-100*step/6,'id':1}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});cdp.detach()
    after=panel.bounding_box()
    assert abs(after['x']-before['x'])>50 and abs(after['y']-before['y'])>50,'Real touch moves the flyover'
    assert frame.evaluate('scrollY')==scroll,'Dragging must not scroll the learning task'
    keys(['AC','2','0','0','+','1','0','%'])
    frame.goto(base+'m1.html');frame.wait_for_function('window.SOZ_READY===true')
    assert frame.locator('.bbs-calculator').is_visible(),'Open state survives material navigation'
    restored=frame.locator('.bbs-calculator').bounding_box()
    assert abs(restored['x']-after['x'])<2 and abs(restored['y']-after['y'])<2,'Position survives navigation'
    keys(['=']);assert frame.locator('.bbs-calc-display').inner_text()=='220','Pending arithmetic survives navigation'
    page.set_viewport_size({'width':390,'height':844})
    frame.wait_for_function('''()=>{const r=document.querySelector('.bbs-calculator').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;}''')
    assert frame.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'No mobile page overflow'
    launcher_box=frame.locator('.bbs-calculator-launcher').bounding_box();return_box=frame.locator('.return-task').bounding_box()
    assert launcher_box['x']+launcher_box['width']<=return_box['x'] or launcher_box['y']+launcher_box['height']<=return_box['y'],'Mobile launcher must not cover task return'
    handle=frame.locator('.bbs-calc-drag');handle.focus();before=frame.locator('.bbs-calculator').bounding_box();page.keyboard.press('ArrowLeft');after=frame.locator('.bbs-calculator').bounding_box()
    assert after['x']<=before['x'],'Keyboard movement works'
    frame.locator('.bbs-calc-display').focus();keys(['AC']);frame.locator('.bbs-calc-display').focus();page.keyboard.type('12+3');page.keyboard.press('Enter')
    assert frame.locator('.bbs-calc-display').inner_text()=='15','Keyboard calculation'
    if root.as_posix().endswith('preview/LS01'):page.screenshot(path=str(reports/'Rechner_SCORM_Touch.png'),full_page=True)
    page.keyboard.press('Escape');assert frame.locator('.bbs-calculator').is_hidden(),'Escape closes the flyover'
    launcher=frame.locator('.bbs-calculator-launcher');assert launcher.get_attribute('aria-expanded')=='false'
    frame.goto(base+'informieren.html');frame.wait_for_function('window.SOZ_READY===true');assert frame.locator('.bbs-calculator').is_hidden(),'Closed state survives navigation'
    launcher=frame.locator('.bbs-calculator-launcher');launcher.tap();page.set_viewport_size({'width':667,'height':320})
    frame.wait_for_function('''()=>{const r=document.querySelector('.bbs-calculator').getBoundingClientRect();return r.right<=innerWidth&&r.bottom<=innerHeight;}''')
    page.emulate_media(media='print');assert frame.locator('.bbs-calculator').is_hidden() and launcher.is_hidden(),'Calculator excluded from print'
    assert not errors,errors
    context.close()
    return {'package':root.relative_to(REPO).as_posix(),'SCORMIframe':True,'touchArithmetic':True,'touchDrag':True,'materialPersistence':True,'keyboard':True,'smallViewport':True,'noAssessedProgressWrites':True,'status':'PASS'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--delivery',type=Path);ap.add_argument('--report',type=Path,default=REPO/'work/calculator-report.json');args=ap.parse_args()
    entries=json.loads((REPO/'master-katalog.json').read_text())['packages']
    roots=[REPO/item['master'] for item in entries if item['id'].startswith('BRC-LG01-') or item['id'] in ('VORLAGE-TRADIERT','VORLAGE-FUENF-LERNWEGE')]
    if args.delivery:roots += sorted(args.delivery.resolve().glob('LS??'))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(REPO)))
    threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for root in roots:
                results.append(check(browser,server,root,args.report.parent));print('PASS calculator in SCORM:',root.relative_to(REPO),flush=True)
                args.report.write_text(json.dumps({'results':results},ensure_ascii=False,indent=2)+'\n')
            browser.close()
    finally:server.shutdown();server.server_close()
    args.report.write_text(json.dumps({'status':'PASS','packages':len(results),'results':results,'limits':'Chromium touch and SCORM iframe simulation; no physical Moodle/iPad test.'},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
