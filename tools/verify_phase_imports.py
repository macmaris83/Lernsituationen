#!/usr/bin/env python3
"""Check phase-only imports, no empty intro toolbar, and reading typography."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,functools,http.server,threading
parser=argparse.ArgumentParser();parser.add_argument('folders',nargs='+',type=Path);args=parser.parse_args();workspace=Path(__file__).resolve().parents[2]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(workspace)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for folder in args.folders:
            base=f'http://127.0.0.1:{server.server_port}/'+folder.resolve().relative_to(workspace).as_posix()+'/'
            context=browser.new_context();context.add_init_script('navigator.canShare=()=>true;navigator.share=async({files})=>{window.shared={name:files[0].name,size:files[0].size};}')
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            for intro in ['index.html','handlungssituation.html']:
                page.goto(base+intro);assert page.locator('[data-share-workbook]').count()==0;assert page.locator('.tools-bar:visible').count()==0
                assert page.locator('a[href*="Gesamtdruck"]').count()==0
                if intro=='index.html':assert page.locator('.material-access,.phase-materials,.material-menu').count()==0
                assert page.locator('.lesson-content .reading-prose').count()>0
                assert page.locator('.reading-prose').first.evaluate("e=>getComputedStyle(e).textAlign==='justify'&&getComputedStyle(e).hyphens==='auto'")
                assert page.evaluate('document.documentElement.lang')=='de'
            assert page.locator('.lesson-content>.hero').evaluate("e=>getComputedStyle(e).borderColor")=='rgb(220, 235, 241)'
            modes=page.evaluate('Object.keys(SOZPAED.workbooks||{1:SOZPAED.workbook})')
            for mode in modes:
                for phase in ['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren']:
                    page.goto(base+phase+'.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'")
                    page.evaluate('''mode=>{const p=SOZ_PROGRESS.read(),m=SOZ_PROGRESS_META;p.m=Number(mode);p.o=true;for(const q of m.quiz)p.q[q.id]=[q.correct,true];for(const [id,t]of Object.entries(m.tasks))p.t[id]=t.signature;SOZ_PROGRESS.write(p);SOZ_API.setMode(mode);}''',mode)
                    assert page.locator('a[href*="Gesamtdruck"]').count()==0
                    assert page.locator('.task-original-preview:visible').first.evaluate("e=>getComputedStyle(e).textAlign!=='justify'")
                    page.locator('[data-share-workbook]').click();page.wait_for_function('!!window.shared')
                    shared=page.evaluate('shared');expected=f'GoodNotes_Phase_{phase}_W{mode}.pdf';assert shared['name']==expected and shared['size']==(folder/'pdf'/expected).stat().st_size
            assert not errors,errors
            print('PASS:',folder.name,'phase PDF shares, no intro import/toolbar/full-print link, long prose justified/hyphenated, short tasks left, situation card borders',flush=True)
            context.close()
        browser.close()
finally:server.shutdown()
