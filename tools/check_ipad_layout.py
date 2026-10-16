#!/usr/bin/env python3
"""Check touch layout in SCORM iframes at iPad sizes and on a mouse monitor.

Use --preview-css to inspect the shared stylesheet before installing it.
Default: two templates and uploaded LS01. --all --delivery PATH checks all 14.
"""
import argparse
import functools
import http.server
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

REPO=Path(__file__).resolve().parents[1]
IPADS=((768,1024),(820,1180),(1024,768),(1180,820),(507,768))


def visible_targets(frame,selector):
    return [item for item in frame.locator(selector).all() if item.is_visible()]


def assert_size(locator,label):
    box=locator.bounding_box()
    assert box and box['height']>=43.9 and box['width']>=43.9, f'{label}: target below 44×44 {box}'


def check(browser,server,root,reports,preview_css):
    url=f'http://127.0.0.1:{server.server_port}/'+root.relative_to(REPO).as_posix()+'/'
    context=browser.new_context(viewport={'width':820,'height':1180},has_touch=True,reduced_motion='reduce')
    page=context.new_page();page.set_default_timeout(10000)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url+'scorm.html')
    page.wait_for_function('document.querySelector("iframe")?.contentWindow?.SOZ_READY===true')
    frame=next(f for f in page.frames if f!=page.main_frame)
    def ready():
        frame.wait_for_function('window.SOZ_READY===true')
        if preview_css: frame.add_style_tag(content=(REPO/'Komponenten/iPad/ipad.css').read_text())
        else: assert frame.locator('link[href^="assets/ipad.css"]').count()==1,'iPad CSS installed once'
    ready()
    assert frame.evaluate("matchMedia('(any-pointer:coarse)').matches"),'Touch media query'
    orientation=frame.locator('.orientation-completion label')
    assert_size(orientation,'Orientation read label')
    orientation.tap()
    assert frame.locator('[data-orientation-complete]').is_checked(),'Orientation can be marked by touch'
    frame.evaluate('''()=>{const m=SOZ_PROGRESS_META,p=SOZ_PROGRESS.read();p.o=true;for(const [id,t]of Object.entries(m.tasks))p.t[id]=t.signature;for(const q of m.quiz)p.q[q.id]=[q.correct,true];SOZ_PROGRESS.write(p);}''')
    cases=[]
    for name in ('index.html','informieren.html','reflektieren.html','m1.html'):
        frame.goto(url+name);ready()
        if name=='informieren.html':
            frame.wait_for_function("document.body.dataset.taskFocusReady==='true'")
            frame.locator('[data-mode-panel="1"] .assignment-frame').first.locator('.task-original-preview').click()
        if name=='m1.html': frame.locator('.material-switch').evaluate('(e)=>e.open=true')
        for width,height in IPADS:
            page.set_viewport_size({'width':width,'height':height})
            assert frame.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),f'{name} {width}: page overflow'
            metrics=frame.evaluate('''()=>{const visible=e=>{if(!e.checkVisibility({checkVisibilityCSS:true}))return false;for(let p=e.parentElement;p;p=p.parentElement){if(p.tagName==='DETAILS'&&!p.open&&!p.querySelector(':scope>summary')?.contains(e))return false;}return true;};const targets=[...document.querySelectorAll('button,a.button,summary,.orientation-completion label,.task-accordion[open] .task-completion,.task-accordion[open] .focus-sound,.material-link,.footer-utils>a')].filter(visible).map(e=>({label:e.textContent.trim().slice(0,50),height:e.getBoundingClientRect().height,width:e.getBoundingClientRect().width}));const fields=[...document.querySelectorAll('textarea,input[type=text],input[type=url],select')].filter(visible).map(e=>parseFloat(getComputedStyle(e).fontSize));return {targets,fields};}''')
            count=len(metrics['targets'])
            for target in metrics['targets']:
                assert target['height']>=43.9 and target['width']>=43.9,f'{name} {width}: target below 44×44 {target}'
            assert all(size>=16 for size in metrics['fields']),'Editable field avoids Safari focus zoom'
            if name=='informieren.html':
                heading=frame.locator('.task-accordion[open] .focus-task-heading')
                columns=heading.evaluate('e=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
                if frame.locator('.task-accordion[open] .focus-timer').count():
                    assert columns==(1 if width<=600 else 2),'Tablet competence/time layout'
                menu=frame.locator('.lesson-content>details.material-access,.lesson-content>details.phase-materials').first
                menu.evaluate('(e)=>e.open=true')
                grid=menu.locator('.material-grid')
                assert grid.evaluate('e=>e.clientHeight<=innerHeight*.32+2'),'Expanded menu leaves task space'
                assert grid.evaluate('e=>e.scrollWidth<=e.clientWidth+1'),'No sideways material chooser'
                menu.evaluate('(e)=>e.open=false')
                frame.locator('.task-accordion[open] .focus-task-footer').scroll_into_view_if_needed()
            if name=='m1.html':
                nav=frame.locator('.material-phase-links')
                assert nav.locator('a').count()==8,'All eight phases'
                columns=nav.evaluate('e=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
                assert columns==(8 if width>=960 else 4),'Eight phases in landscape, four columns in portrait/Split View'
                assert nav.evaluate('e=>e.scrollWidth<=e.clientWidth+1'),'All phases fit without sideways scrolling'
                assert nav.evaluate('''e=>{const p=e.getBoundingClientRect();return [...e.querySelectorAll('a')].every(a=>{const b=a.getBoundingClientRect();return b.left>=p.left-1&&b.right<=p.right+1;});}'''),'Phase inside navigation'
                launch=frame.locator('.bbs-calculator-launcher');ret=frame.locator('.return-task')
                if launch.count() and ret.count():
                    a,b=launch.bounding_box(),ret.bounding_box()
                    assert a['x']+a['width']<=b['x'] or a['y']+a['height']<=b['y'],'Calculator and task return do not overlap'
            if width in (768,1024) and name in ('index.html','informieren.html','m1.html'):
                page.screenshot(path=str(reports/(root.name+'_'+name.removesuffix('.html')+'_'+str(width)+'.png')))
            cases.append({'page':name,'width':width,'height':height,'touchTargetsChecked':count,'status':'PASS'})
    assert not errors,errors
    context.close()
    # Existing fine-pointer monitor layout must remain unaffected by this sheet.
    monitor=browser.new_context(viewport={'width':1440,'height':900},has_touch=False)
    mp=monitor.new_page();mp.goto(url+'m1.html');mp.wait_for_function('window.SOZ_READY===true')
    signature='''()=>{const sels=['.shell','.main','.material-phase-links','.material-phase-links a','.material-switch>summary'];return Object.fromEntries(sels.map(s=>{const e=document.querySelector(s),c=getComputedStyle(e),b=e.getBoundingClientRect();return [s,{width:b.width,height:b.height,display:c.display,font:c.fontSize,columns:c.gridTemplateColumns}]}))}'''
    before=mp.evaluate(signature)
    mp.add_style_tag(content=(REPO/'Komponenten/iPad/ipad.css').read_text())
    assert mp.evaluate(signature)==before,'Mouse monitor geometry remains unchanged'
    monitor.close()
    return {'package':root.relative_to(REPO).as_posix(),'SCORMIframe':True,'touchOrientationCompletion':True,'iPadCases':cases,'mouseMonitorUnchanged':True,'status':'PASS'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--all',action='store_true')
    ap.add_argument('--delivery',type=Path,default=REPO/'work/delivery-v1.5/preview')
    ap.add_argument('--root',type=Path,action='append')
    ap.add_argument('--preview-css',action='store_true')
    ap.add_argument('--report',type=Path,default=REPO/'work/ipad-audit/iPad_Pruefung.json')
    args=ap.parse_args()
    if args.root: roots=[p.resolve() for p in args.root]
    elif args.all:
        entries=json.loads((REPO/'master-katalog.json').read_text())['packages']
        roots=[REPO/item['master'] for item in entries if item['id'].startswith('BRC-LG01-') or item['id'] in ('VORLAGE-TRADIERT','VORLAGE-FUENF-LERNWEGE')]
        roots+=sorted(args.delivery.resolve().glob('LS??'))
    else: roots=[REPO/'Vorlagen/Lernsituation_fuenf_Lernwege',REPO/'Vorlagen/Lernsituation_tradiert',args.delivery.resolve()/'LS01']
    args.report.parent.mkdir(parents=True,exist_ok=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(REPO)))
    threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for root in roots:
                results.append(check(browser,server,root,args.report.parent,args.preview_css))
                print('PASS iPad layout in SCORM:',root.relative_to(REPO),flush=True)
                args.report.write_text(json.dumps({'results':results},ensure_ascii=False,indent=2)+'\n')
            browser.close()
    finally:server.shutdown();server.server_close()
    args.report.write_text(json.dumps({'status':'PASS','packages':len(results),'results':results,'limits':'Chromium touch/SCORM iframe simulation at 768×1024, 820×1180, 1024×768, 1180×820, 507×768 and mouse monitor 1440×900. No physical iPad, Safari, or Moodle-App test.'},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
