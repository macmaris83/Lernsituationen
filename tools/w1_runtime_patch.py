"""Retain only W1 in the existing engines; do not change task identity/content."""
from pathlib import Path
import re

MARKER = '/* Tradiert: W1 only; existing task identities are retained. */'
ASSETS = {'progress-core.js','runtime.js','progress.js','teacher.js','export.js','teacher-view.js','revision185-core.js','lg05-adapter.js'}

HTML_FILTER = r'''function singlePathHTML(source,parser){
 const doc=(parser||new DOMParser()).parseFromString('<div>'+source+'</div>','text/html'),template=doc.body.firstElementChild;let changed=false;
 for(const el of template.querySelectorAll('[data-mode-panel]'))if(Number(el.dataset.modePanel)!==1){el.remove();changed=true;}
 for(const select of template.querySelectorAll('[data-student-mode],[data-teacher-mode]'))for(const option of [...select.options])if(Number(option.value)!==1){option.remove();changed=true;}
 return changed?template.innerHTML:source;
}
'''

SET_MODE = r'''function modes(){return [1];}
function setMode(mode,store=true){settings.learningPaths={1:{label:'Tradiert'}};settings.allowStudentMode=false;mode=1;settings.mode=mode;document.body.dataset.mode=mode;$$('[data-mode-panel]').forEach(e=>e.hidden=Number(e.dataset.modePanel)!==mode);$$('[data-mode-label]').forEach(e=>e.textContent='Tradiert');$$('[data-student-mode]').forEach(e=>{e.innerHTML='<option value="1">Tradiert</option>';e.value='1';e.parentElement.hidden=true;});if(store)saveSettings();if(!document.body.dataset.teacher)window.SOZ_PROGRESS?.setMode(mode);}
'''

NORMALIZE = r'''function normalizeSinglePathSettings(){settings.mode=1;settings.allowStudentMode=false;settings.learningPaths={1:{label:'Tradiert'}};for(const [page,html]of Object.entries(settings.overrides||{})){if(!Object.prototype.hasOwnProperty.call(D.pages,page))delete settings.overrides[page];else if(typeof html==='string')settings.overrides[page]=window.SOZ_PROGRESS_CORE.singlePathHTML(html);}}
normalizeSinglePathSettings();
'''

def transform(path, text):
    name=Path(path).name
    if name not in ASSETS or '/assets/' not in str(path).replace('\\','/') or MARKER in text:
        return text
    before=text
    if name=='progress-core.js':
        if 'function availableModes(meta)' not in text:
            text=text.replace('function initial(meta,mode)', "function availableModes(meta){return [...new Set(Object.values(meta.tasks||{}).map(t=>Number(t.mode)))].filter(n=>Number.isInteger(n)&&n>0).sort((a,b)=>a-b);}\nfunction initial(meta,mode)")
            text=text.replace('window.SOZ_PROGRESS_CORE={','window.SOZ_PROGRESS_CORE={availableModes,')
        text=text.replace('m:Number(mode)||1,', 'm:availableModes(meta).includes(Number(mode))?Number(mode):(availableModes(meta)[0]||1),', 1)
        text=text.replace('p.m=Number.isInteger(raw.m)&&raw.m>=1&&raw.m<=5?raw.m:p.m;', 'p.m=Number.isInteger(raw.m)&&availableModes(meta).includes(raw.m)?raw.m:p.m;')
        text=text.replace('for(let m=1;m<=5;m++)', 'for(const m of [1])')
        text=text.replace('function metadataFrom(data,parser){', HTML_FILTER+'function metadataFrom(data,parser){for(const page of Object.keys(data.pages))data.pages[page]=singlePathHTML(data.pages[page],parser);')
        text=text.replace('window.SOZ_PROGRESS_CORE={','window.SOZ_PROGRESS_CORE={singlePathHTML,')
        # Dynamic-mode variants must still require W1 in every phase.
        text=text.replace('const modes=availableModes({tasks});for(', "const modes=availableModes({tasks});if(modes.length!==1||modes[0]!==1)throw Error('Der tradierte Lernweg fehlt.');for(")
    elif name=='runtime.js':
        text=re.sub(r'function modes\(\)\{[^\n]*\}\n', '', text)
        text=re.sub(r'^function setMode\(mode,store=true\)\{[^\n]*\}\n', lambda _: SET_MODE, text, flags=re.M)
        text=text.replace('function validateState(s){', NORMALIZE+'function validateState(s){',1)
        text=text.replace('function saveSettings(){', 'function saveSettings(){normalizeSinglePathSettings();',1)
        if 'availableModes:modes,' not in text:
            text=text.replace('window.SOZ_API={','window.SOZ_API={availableModes:modes,',1)
        text=re.sub(r'labels=\[[^\n;]*\];', "labels=['','Tradiert'];", text, count=1)
        text=text.replace('!Number.isInteger(t.mode)||t.mode<1||t.mode>5', 't.mode!==1')
    elif name=='progress.js':
        text=re.sub(r'get initialMode\(\)\{[^}]+\}', 'get initialMode(){return 1;}', text)
    elif name=='teacher.js':
        text=re.sub(r'^const mode=\$\(\'\[data-teacher-mode\]\'\);[^\n]*\n', "const mode=$('[data-teacher-mode]');if(mode){mode.innerHTML='<option value=\"1\">Tradiert</option>';mode.value='1';mode.disabled=true;mode.closest('label')?.setAttribute('hidden','');}\n", text, flags=re.M)
        text=re.sub(r'^const choice=\$\(\'\[data-allow-mode\]\'\);[^\n]*\n', "const choice=$('[data-allow-mode]');if(choice){choice.checked=false;choice.disabled=true;choice.closest('label')?.setAttribute('hidden','');}\n", text, flags=re.M)
        text=re.sub(r'^\$\(\'\[data-path-module\]\'\)\.addEventListener\([^\n]*\n', '', text, flags=re.M)
        text=text.replace("return t.innerHTML;}", "return window.SOZ_PROGRESS_CORE.singlePathHTML(t.innerHTML);}",1)
        text=re.sub(r'<option value="[2-5]">Weg [2-5]</option>', '', text)
        text=text.replace('filter.hidden=!panels.length;', 'filter.hidden=panels.length<2;')
    elif name=='export.js':
        text=re.sub(r'cfg.mode=Number\(cfg.mode\);[^\n]+', "cfg.mode=1;cfg.allowStudentMode=false;cfg.learningPaths={1:{label:'Tradiert'}};", text)
        text=text.replace('let normalized=content;', 'let normalized=window.SOZ_PROGRESS_CORE.singlePathHTML(content);')
        # Apply filtered saved editor content even in exporters without normalization.
        text=text.replace('replaceContent(decode(files[page]),content,page)', 'replaceContent(decode(files[page]),window.SOZ_PROGRESS_CORE.singlePathHTML(content),page)')
        text=text.replace('edited.pages[page]=content;', 'edited.pages[page]=window.SOZ_PROGRESS_CORE.singlePathHTML(content);')
        # LG05 normalization must use the already filtered content.
        text=text.replace('temp.innerHTML=content;', 'temp.innerHTML=normalized;')
    elif name in ('teacher-view.js','revision185-core.js'):
        text=text.replace('get mode(){return Number(value?.mode)||Number(C.mode)||1;}', 'get mode(){return 1;}')
        text=text.replace('value={active:true,mode:Number(mode)||1}', 'value={active:true,mode:1}')
        text=text.replace('for(let n=1;n<=5;n++)', 'for(const n of [1])')
        if 'paths.append(select);if(select.options.length<2)paths.hidden=true;' not in text:
            text=text.replace('paths.append(select);', 'paths.append(select);if(select.options.length<2)paths.hidden=true;')
    elif name=='lg05-adapter.js':
        text=re.sub(r"const modeNames=\[[^\n]*\];", "const modeNames=['','Tradiert'];", text)
    return MARKER+'\n'+text if text!=before else text

def patch(root, masters):
    changed=[]
    for master in masters:
        for name in ASSETS:
            path=Path(root)/master/'assets'/name
            if not path.exists(): continue
            old=path.read_text();new=transform(str(path),old)
            if new!=old:path.write_text(new);changed.append(str(path.relative_to(root)))
    return changed

if __name__=='__main__':
    import sys,json
    root=Path(sys.argv[1]);catalog=json.loads((root/'master-katalog.json').read_text())
    masters=[p['master'] for p in catalog['packages'] if p['typ']=='Lernsituation' or p['id']=='VORLAGE-TRADIERT']
    print(json.dumps(patch(root,masters),ensure_ascii=False,indent=2))
