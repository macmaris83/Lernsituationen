#!/usr/bin/env python3
"""Build the six BioCasa SCORM packages from the supplied narrative series.

The latest five-path template supplies the application, editor and SCORM code.
Pandoc preserves source prose, lists, tables and links. Only competency perspective
and added task time estimates change editorial presentation.
"""
from pathlib import Path
import argparse, base64, copy, functools, hashlib, http.server, json, math, re
import shutil, subprocess, threading, zipfile, xml.etree.ElementTree as ET
from lxml import html as H
from playwright.sync_api import sync_playwright
import fitz
from prepare_businessplan_scorm import businessplan_timer

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO/'Lernsituation_fuenf_Lernwege'
OUT = REPO/'Reihen/BRC_LG01'
PHASES = ['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren']
NAMES = ['Informieren','Planen','Entscheiden','Durchführen','Überprüfen','Reflektieren']
MODES = ['Stark geführt','Begleitet','Teiloffen','Selbstgesteuert mit Checkpoints','Löppt']
COLORS = ['#333333','#E6E8EA','#EFF5CE','#E5F5FC','#CCEBF7']
ESC = lambda s: __import__('html').escape(str(s), quote=True)
VERSION = '2026-10-14.lg01-reihe.1'

def markdown(value):
    result = subprocess.run(['pandoc','-f','markdown','-t','html5','--wrap=none'],input=value,text=True,capture_output=True,check=True).stdout
    root = H.fragment_fromstring(result,create_parent='div')
    for table in root.xpath('.//table'):
        wrapper=H.Element('div',{'class':'table-scroll'});table.addprevious(wrapper);wrapper.append(table)
    return ''.join(H.tostring(e,encoding='unicode') for e in root)

def text(value):
    return ' '.join(H.fragment_fromstring(value,create_parent='div').text_content().split())

def sections(value,level):
    matches=list(re.finditer(r'^'+('#'*level)+r' (.+)$',value,re.M))
    return [(m.group(1),value[m.end():matches[i+1].start() if i+1<len(matches) else len(value)].strip()) for i,m in enumerate(matches)]

def load_source(path):
    source=path.read_text();lessons=[]
    for title,body in sections(source,1):
        match=re.match(r'LS (\d+) [–-] (.+)',title)
        if not match:continue
        number=int(match[1]);parts={int(re.match(r'(\d+)\.',k)[1]):v for k,v in sections(body,2)}
        modes={}
        for label,value in sections(parts[5],3):
            mode=int(re.match(r'Lernweg W(\d)',label)[1]);phase_sections=sections(value,4)
            assert len(phase_sections)==6,(number,mode)
            first=re.search(r'^#### ',value,re.M)
            modes[mode]={'intro':value[:first.start()].strip(),'phases':[v for k,v in phase_sections]}
        assert sorted(modes)==[1,2,3,4,5]
        budgets=[]
        for phase in modes[1]['phases']:
            match=re.search(r'\*\*Arbeitszeit:\*\* ([\d,.]+) Unterrichtsstunde',phase)
            assert match,(number,phase[:100]);budgets.append(float(match[1].replace(',','.'))*45)
        hours=int(re.search(r'\*\*Zeitrichtwert:\*\* (\d+) Unterrichtsstunden',parts[1])[1])
        assert sum(budgets)==hours*45
        materials=sections(parts[6],3)
        assert all(re.match(r'M\d+ [–-]',k) for k,v in materials)
        lessons.append({'number':number,'title':re.match(r'LS \d+ [–-] (.+)',title)[1],
                        'parts':parts,'modes':modes,'budgets':budgets,'hours':hours,'materials':materials})
    assert len(lessons)==6
    return lessons

def metadata_and_tasks(source):
    meta={}
    lines=[]
    for line in source.splitlines():
        m=re.match(r'\*\*(Arbeitszeit|Arbeitsform|Materialien):\*\*\s*(.+)',line)
        if m:meta[m[1]]=m[2].strip()
        else:lines.append(line)
    root=H.fragment_fromstring(markdown('\n'.join(lines)),create_parent='div')
    tasks=[]
    for node in root:
        # Numbered and bulleted instructions become separate cards. Nested lists
        # remain with their parent task; surrounding prose is never truncated.
        if node.tag in ['ol','ul']:
            for li in node:
                inner=ESC(li.text or '')+''.join(H.tostring(c,encoding='unicode') for c in li)
                fragment=H.fragment_fromstring(inner,create_parent='div')
                block_tags={'p','ul','ol','blockquote','div','table','h1','h2','h3','h4','h5','h6'}
                chunks=[];inline=ESC(fragment.text or '')
                for child in fragment:
                    if child.tag in block_tags:
                        if inline.strip():chunks.append('<p>'+inline+'</p>');inline=''
                        chunks.append(H.tostring(child,encoding='unicode'))
                    else:inline+=H.tostring(child,encoding='unicode')
                if inline.strip():chunks.append('<p>'+inline+'</p>')
                inner=''.join(chunks)
                tasks.append(inner)
        elif node.tag=='p' and text(H.tostring(node,encoding='unicode')).startswith('Handlungsergebnis:') and tasks:
            tasks[-1]+=H.tostring(node,encoding='unicode')
        else:
            tasks.append(H.tostring(node,encoding='unicode'))
    assert tasks
    # Split operator-led sentences visually without rewriting their content.
    operators={'Identifizieren','Nennen','Arbeiten','Analysieren','Ermitteln','Ordnen','Erläutern','Einordnen','Begründen','Vergleichen','Skizzieren','Erstellen','Entwickeln','Stellen','Diskutieren','Beurteilen','Überprüfen','Formulieren','Beschreiben','Berechnen','Bewerten','Entscheiden','Prüfen','Reflektieren','Untersuchen','Benennen','Dokumentieren','Nutzen','Halten','Zeigen','Leiten','Verfassen'}
    result=[]
    for value in tasks:
        frag=H.fragment_fromstring(value,create_parent='div')
        for strong in frag.xpath('.//strong'):
            if strong.text_content().capitalize() in operators:strong.set('class','operator')
        value=''.join(H.tostring(c,encoding='unicode') for c in frag)
        result.append(value)
    return meta,result

def times(tasks,minutes):
    # Allocate in half-minute units, including 1.5/0.5-UE budgets, with no drift.
    units=round(minutes*2);weights=[max(1,math.sqrt(len(text(t).split()))) for t in tasks]
    free=units-len(tasks);assert free>=0
    quotas=[free*w/sum(weights) for w in weights];allocated=[1+int(q) for q in quotas]
    for i in sorted(range(len(tasks)),key=lambda i:quotas[i]%1,reverse=True)[:units-sum(allocated)]:allocated[i]+=1
    assert sum(allocated)==units
    return [n/2 for n in allocated]

def number(value):return f'{value:g}'.replace('.',',')

def radar(competencies):
    cx,cy,r=350,215,155
    def point(i,value):
        a=(i*72-90)*math.pi/180;return cx+math.cos(a)*r*value/6,cy+math.sin(a)*r*value/6
    def points(value):return ' '.join(f'{x:.2f},{y:.2f}' for i in range(5) for x,y in [point(i,value)])
    svg='<svg viewBox="0 0 700 435" role="img" aria-label="Kompetenznetz und Gewichtung"><title>Kompetenznetz</title>'
    for v in range(1,7):svg+=f'<polygon points="{points(v)}" fill="none" stroke="#c8dce7"/>'
    for i,c in enumerate(competencies):
        x,y=point(i,6);tx,ty=point(i,7.55)
        svg+=f'<line x1="350" y1="215" x2="{x}" y2="{y}" stroke="#d2e3ea"/><text x="{tx}" y="{ty}" text-anchor="middle" dominant-baseline="middle" fill="#173a63" font-size="15">{ESC(c["label"])}</text>'
    data=' '.join(f'{x:.2f},{y:.2f}' for i,c in enumerate(competencies) for x,y in [point(i,c['weight'])])
    return svg+f'<polygon points="{data}" fill="#afca0b" fill-opacity=".27" stroke="#009bd9" stroke-width="2.5"/></svg>'

def quiz_html(questions):
    data=[];panels=''
    for i,q in enumerate(questions,1):
        options=[{'value':chr(65+n),'label':label,'feedback':q['feedback']} for n,label in enumerate(q['options'])]
        correct=chr(65+q['correct']);qid=f'situation-{i}'
        data.append({'id':qid,'title':q['title'],'question':q['question'],'options':options,'correct':correct})
        labels=''.join(f'<label><input type="radio" name="{qid}" value="{a["value"]}"><span>{ESC(a["label"])}</span></label>' for a in options)
        panels+=f'<details><summary>{i}. {ESC(q["title"])}<span data-quiz-marker></span></summary><div data-quiz-question="{qid}"><p>{ESC(q["question"])}</p>{labels}<div class="quiz-actions"><button data-quiz-submit>Antwort prüfen</button><button data-quiz-reset>Auswahl löschen</button></div><p class="quiz-feedback" data-quiz-feedback hidden role="status"></p></div></details>'
    return '<section class="card quiz-check" data-situation-quiz><h2>Kurz prüfen · Handlungssituation</h2><p>Wählen Sie jeweils die begründete Antwort.</p>'+panels+'<p data-quiz-progress role="status"></p><script type="application/json">'+json.dumps(data,ensure_ascii=False).replace('</',r'<\/')+'</script></section>'

def build_content(ls,competencies,questions):
    num=ls['number'];title=ls['title'];pages={};titles={'index.html':'Orientierung','handlungssituation.html':'Handlungssituation'}
    titles.update({p+'.html':n for p,n in zip(PHASES,NAMES)})
    materials=[(k.split(' – ',1)[-1].split(' - ',1)[-1],v) for k,v in ls['materials']]
    materials.extend([('Fachsystematische Sicherung',ls['parts'][7]),('KI-Einsatz · Prüfen und dokumentieren',ls['parts'][11])])
    for i,(label,source) in enumerate(materials,1):titles[f'm{i}.html']=f'M{i} · {label}'
    titles['erwartungshorizont.html']='Erwartungshorizont und Lehrkräftehinweise'
    def hero(label):return f'<section class="card hero"><div class="eyebrow">BRC · LG01 · LS{num:02d} · {ESC(title)}</div><h1>{ESC(label)}</h1></section>'
    access='<section class="card phase-materials material-access" aria-label="Materialzugriff"><h2>Materialzugriff</h2><nav class="material-grid" aria-label="Materialien">'+''.join(f'<a class="material-link" href="m{i}.html"><b>M{i}</b><span> · {ESC(label)}</span></a>' for i,(label,_) in enumerate(materials,1))+'</nav></section>'
    # The F card carries the priority statement for the compact orientation,
    # whereas the focus and final assessment use the detailed F statement.
    detail=''.join('<article class="card"><h3><strong>'+ESC(c['label'])+'</strong></h3><p>'+ESC(competencies['priorityStatement'] if c['label']=='Fachkompetenz' else c['statement'])+'</p></article>' for c in competencies['competencies'])
    ways='<section class="card"><h2>Fünf alternative Lernwege</h2><p>Alle Lernwege führen zum gleichen fachlichen Ziel. Die Wege unterscheiden sich in der Anleitung und Selbststeuerung.</p><div class="series-ways">'+''.join(f'<div style="background:{color};color:{"white" if i==1 else "#173a63"}"><strong>W{i} · {ESC(label)}</strong></div>' for i,(color,label) in enumerate(zip(COLORS,MODES),1))+'</div></section>'
    pages['index.html']=hero(title)+'<section class="card"><h2>Einordnung</h2>'+markdown(ls['parts'][1])+'</section><section class="card relevance"><h2>Darum ist das Thema relevant</h2>'+markdown(ls['parts'][2])+'</section><section class="card priority-section"><h2>Kompetenzprofil</h2><section class="weight-radar">'+radar(competencies['competencies'])+'</section><div class="competence-cards orientation-competencies">'+detail+'</div></section>'+ways
    pages['handlungssituation.html']=hero('Handlungssituation')+access+'<section class="card situation-prose">'+markdown(ls['parts'][4])+'</section>'+quiz_html(questions)
    instructions={};source_counts={}
    for pi,phase in enumerate(PHASES):
        content=hero(NAMES[pi])+access;instructions[phase]={};source_counts[phase]={}
        for mode in range(1,6):
            raw=ls['modes'][mode]['phases'][pi];meta,tasks=metadata_and_tasks(raw);allocated=times(tasks,ls['budgets'][pi]);instructions[phase][mode]={'meta':meta,'tasks':tasks,'times':allocated};source_counts[phase][mode]=len(tasks)
            form=meta.get('Arbeitsform','Lernteam; Rollen und Arbeitsaufteilung selbst festlegen.' if mode in [3,5] else 'Lernteam')
            clock='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg>'
            social='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="8" cy="7" r="3"/><path d="M2 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6m1 4a5 5 0 0 1 5 5v2"/></svg>'
            content+=f'<section class="task-card phase-mode" data-mode-panel="{mode}" data-phase="{phase}"><h2 class="phase-mode-title">W{mode} · {ESC(MODES[mode-1])}</h2><div class="phase-meta"><p>{clock}<span><strong>Arbeitszeit:</strong> {number(ls["budgets"][pi]/45)} Unterrichtsstunden · {number(ls["budgets"][pi])} Minuten</span></p><p>{social}<span><strong>Arbeitsform:</strong> {ESC(form)}</span></p></div>'
            if meta.get('Materialien'):content+='<p class="phase-source-materials"><strong>Materialien:</strong> '+ESC(meta['Materialien'])+'</p>'
            if ls['modes'][mode]['intro']:content+='<details class="series-way-brief"><summary>Auftrag und Zielkern · W'+str(mode)+'</summary>'+markdown(ls['modes'][mode]['intro'])+'</details>'
            content+='<div class="task-text">'
            for i,(task,time) in enumerate(zip(tasks,allocated),1):
                single=pi==5 or ('Einzelarbeit' in form and 'anschließend' not in form and 'Gruppen' not in form)
                icon=('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="6" r="3"/><path d="M5 22v-4a7 7 0 0 1 14 0v4"/></svg>' if single else social)
                content+=f'<article class="assignment-frame" data-task-number="{i}" data-goodnotes-task="true"><span class="assignment-number" aria-label="Auftrag {i}">{i}</span><button type="button" class="assignment-goodnotes-button" data-share-workbook aria-label="Arbeitsheft dieser Phase in GoodNotes importieren"><img class="assignment-goodnotes" src="assets/goodnotes.png" alt="GoodNotes"></button><span class="assignment-social">{icon}<small>{"Einzelarbeit" if single else "Lernteam"}</small></span><div class="assignment-body">{task}<span class="assignment-time" data-time-ui="true" data-minutes="{time}"> {clock} ca. {number(time)} Min.</span></div></article>'
            content+='</div></section>'
        if phase=='reflektieren':content+='<div data-assessment-widget></div>'
        pages[phase+'.html']=content
    for i,(label,source) in enumerate(materials,1):
        pages[f'm{i}.html']=hero(f'M{i} · {label}')+access+'<div class="source-document"><div class="app acrobat"><div class="viewerbar"><span class="dots">•••</span><strong>Adobe Acrobat Reader</strong><span class="file">'+ESC(label)+'</span><span class="grow"></span><span aria-hidden="true">— □ ×</span></div><div class="subbar"><span>Werkzeuge | Kommentieren | Ansicht</span><span class="zoom">100 %</span></div><section class="canvas"><article class="paper">'+markdown(source)+'</article></section></div></div>'
    teacher=''
    for key,label in [(8,'Erwartungshorizont'),(9,'Operatoren'),(10,'Rolle der Lehrkraft'),(12,'SchuCu-Qualitätscheck')]:teacher+='<section class="card"><h2>'+label+'</h2>'+markdown(ls['parts'][key])+'</section>'
    pages['erwartungshorizont.html']=hero('Erwartungshorizont und Lehrkräftehinweise')+teacher
    return pages,titles,instructions,source_counts

def shell(page,content,title,ls):
    # Preserve the approved brand/navigation/footer and teacher surface exactly.
    original=(TEMPLATE/page if (TEMPLATE/page).is_file() else TEMPLATE/'m1.html').read_text()
    if page=='erwartungshorizont.html':original=(TEMPLATE/page).read_text()
    if page not in ['lehrkraft.html','scorm.html','druckansicht.html']:
        start=original.index('<div class="lesson-content">')+len('<div class="lesson-content">');end=original.index('</div></main>',start)
        original=original[:start]+content+original[end:]
    original=re.sub(r'<title>.*?</title>','<title>'+ESC(title)+' · BBS 1 Aurich</title>',original)
    original=re.sub(r'data-page="[^"]*"',f'data-page="{page}"',original)
    original=re.sub(r'data-ls-id="[^"]*"',f'data-ls-id="BRC-LG01-LS{ls:02d}"',original)
    original=original.replace('pdf/LG01_LS03_Gesamtdruck_A4.pdf',f'pdf/LG01_LS{ls:02d}_Gesamtdruck_A4.pdf')
    original=original.replace('M1–M5 analysieren','Materialien analysieren').replace('Bewerten</span>','Überprüfen</span>')
    original=re.sub(r'((?:assets/(?:runtime|styles|teacher|progress-core|progress|situation))\.(?:js|css))\?[^"\s]*',r'\1?v=lg01-reihe-20261014',original)
    for i,label in enumerate(MODES,1):original=re.sub(r'(<option value="'+str(i)+r'">)[^<]+',lambda m:m[1]+f'W{i} · {ESC(label)}',original)
    return original

EXTRA_CSS='''
body.task-focus .lesson-content .assignment-frame.focus-suppressed{display:none!important}
.series-ways{display:grid;gap:8px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}.series-ways>div{border-radius:10px;padding:12px}
.series-way-brief{margin:12px 0;border:1px solid #b8e0f2;border-radius:10px;padding:10px 12px}.series-way-brief summary{font-weight:650;color:#173a63}
.assignment-body>ul,.assignment-body>ol{padding-left:22px}.assignment-body .assignment-time{display:inline-flex;align-items:center;color:#58717e;font-size:.78rem;margin-top:6px;gap:4px}.assignment-time svg{width:15px;height:15px;color:#009bd9}
.material-document .table-scroll table{min-width:0;width:100%;overflow-wrap:anywhere}.material-document .table-scroll{max-width:100%}
body.material-reading .source-document .paper{min-height:0;padding:28px 32px}
body.material-reading .source-document .paper table{table-layout:auto;min-width:0;overflow-wrap:anywhere}
@media(max-width:600px){body.material-reading .source-document .paper{padding:20px 16px}}
.task-focus-panel .focus-assignment-copy p{margin-bottom:1em}
body[data-mode="1"] .mode-badge{background:#333;color:white}body[data-mode="2"] .mode-badge{background:#E6E8EA;color:#333}body[data-mode="3"] .mode-badge{background:#EFF5CE;color:#333}body[data-mode="4"] .mode-badge{background:#E5F5FC;color:#333}body[data-mode="5"] .mode-badge{background:#CCEBF7;color:#333}
'''

def workbook_html(ls,phase,mode,instruction):
    blocks=[]
    for i,(task,minutes) in enumerate(zip(instruction['tasks'],instruction['times']),1):
        blocks.append(f'<section class="worksheet-task"><header><b>{i}</b><span>ca. {number(minutes)} Min.</span></header>{task}<div class="writing-space"></div></section>')
    return f'''<!doctype html><html lang="de"><meta charset="utf-8"><title>Arbeitsheft</title><style>
    @page{{size:A4;margin:16mm 14mm}}body{{font:11pt/1.5 Arial,sans-serif;color:#173a63}}h1{{font-size:20pt}}h2{{font-size:13pt;color:#007fac}}p{{margin:8px 0}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #b8dfee;padding:6px}}.worksheet-task{{margin:18px 0;border:1px solid #b8dfee;border-radius:10px;padding:12px;break-inside:avoid}}.worksheet-task header{{display:flex;justify-content:space-between;color:#007fac}}.writing-space{{min-height:65mm;margin-top:12px;background:repeating-linear-gradient(white,white 26px,#d8e7ef 27px)}}footer{{font-size:9pt;color:#58717e}}
    </style><body><header><p>BBS 1 Aurich · BRC · LG01 · LS{ls['number']:02d}</p><h1>{ESC(ls['title'])}</h1><h2>{NAMES[PHASES.index(phase)]} · W{mode} · {ESC(MODES[mode-1])}</h2><p>Arbeitszeit dieser Phase: {number(ls['budgets'][PHASES.index(phase)])} Minuten</p></header>{''.join(blocks)}<footer>Arbeitsheft ausschließlich für diese Phase und diesen Lernweg.</footer></body></html>'''

def manifest(root,ls):
    ns='http://www.imsproject.org/xsd/imscp_rootv1p1p2';adl='http://www.adlnet.org/xsd/adlcp_rootv1p2';ET.register_namespace('',ns);ET.register_namespace('adlcp',adl)
    e=lambda tag:'{'+ns+'}'+tag
    tree=ET.Element(e('manifest'),{'identifier':f'BRC_LG01_LS{ls["number"]:02d}_SCORM_REIHE','version':'1.0'})
    meta=ET.SubElement(tree,e('metadata'));ET.SubElement(meta,e('schema')).text='ADL SCORM';ET.SubElement(meta,e('schemaversion')).text='1.2'
    orgs=ET.SubElement(tree,e('organizations'),{'default':'ORG_MAIN'});org=ET.SubElement(orgs,e('organization'),{'identifier':'ORG_MAIN','structure':'hierarchical'});ET.SubElement(org,e('title')).text=ls['title']
    item=ET.SubElement(org,e('item'),{'identifier':'ITEM_MAIN','identifierref':'RES_MAIN','isvisible':'true'});ET.SubElement(item,e('title')).text=ls['title']
    resources=ET.SubElement(tree,e('resources'));resource=ET.SubElement(resources,e('resource'),{'identifier':'RES_MAIN','type':'webcontent','href':'scorm.html','{'+adl+'}scormtype':'sco'})
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name!='imsmanifest.xml':ET.SubElement(resource,e('file'),{'href':p.relative_to(root).as_posix()})
    ET.ElementTree(tree).write(root/'imsmanifest.xml',encoding='utf-8',xml_declaration=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=REPO/'Quellen/BRC_LG01/Reihenplan.md');args=parser.parse_args()
    lessons=load_source(args.source);checks=json.loads((REPO/'Quellen/BRC_LG01/Einstiegskontrollen.json').read_text());comps=json.loads((REPO/'Quellen/BRC_LG01/Kompetenzen_Ich.json').read_text());OUT.mkdir(parents=True,exist_ok=True)
    summaries=[];built=[]
    for ls in lessons:
        n=ls['number'];root=OUT/f'LS{n:02d}';root.mkdir(exist_ok=True);(root/'pdf').mkdir(exist_ok=True)
        shutil.copytree(TEMPLATE/'assets',root/'assets',dirs_exist_ok=True)
        runtime=root/'assets/runtime.js';s=runtime.read_text().replace("['','Tradiert · stark geführt','Geführt','Begleitet','Teiloffen','Löppt']",json.dumps(['']+MODES,ensure_ascii=False)).replace('["","STARK GEFÜHRT","GEFÜHRT","BEGLEITET","TEILOFFEN","LÖPPT"]',json.dumps(['']+[m.upper() for m in MODES],ensure_ascii=False)).replace(r'/(\d+)\s*Min/i',r'/(\d+(?:[.,]\d+)?)\s*Min/i').replace('Number(match[1])*60',"Math.round(Number(match[1].replace(',','.'))*60)")
        runtime.write_text(businessplan_timer(s).replace("!card.querySelector('.assignment-social')", "!strip.querySelector('.assignment-social')"))
        core=root/'assets/progress-core.js';core.write_text(core.read_text().replace("const text=e=>(e.textContent||'').replace(/\\s+/g,' ').trim();", "const text=e=>{const copy=e.cloneNode(true);copy.querySelectorAll('.assignment-time[data-time-ui]').forEach(t=>t.remove());return (copy.textContent||'').replace(/\\s+/g,' ').trim();};"))
        progress=root/'assets/progress.js';progress.write_text(progress.read_text().replace(' renderAccess(p,mode);\n}', ' renderAccess(p,mode);window.SOZ_TASK_FOCUS?.refresh();\n}'))
        css=root/'assets/styles.css';css.write_text(css.read_text()+EXTRA_CSS)
        cc=copy.deepcopy(comps[str(n)])
        for c in cc['competencies']:c['id']=f'BRC-LG01-LS{n:02d}-'+{'Fachkompetenz':'F','Personalkompetenz':'P','Sozialkompetenz':'S','Methodenkompetenz':'M','Medienkompetenz':'D'}[c['label']]
        pages,titles,instructions,counts=build_content(ls,cc,checks[str(n)])
        data={'id':f'BRC-LG01-LS{n:02d}','title':ls['title'],'version':VERSION,'priorityStatement':cc['priorityStatement'],'competencies':cc['competencies'],'pages':pages,'pageTitles':titles,'printOrder':[p for p in pages if p!='erwartungshorizont.html'],'workbook':f'pdf/GoodNotes_LG01_LS{n:02d}_W1.pdf','workbooks':{str(m):f'pdf/GoodNotes_LG01_LS{n:02d}_W{m}.pdf' for m in range(1,6)},'phaseBudgets':dict(zip(PHASES,ls['budgets'])),'sourceTaskCounts':counts}
        cfg=json.loads((TEMPLATE/'Konfiguration.json').read_text());cfg.update({'mode':1,'packageRevision':f'BRC-LG01-LS{n:02d}-REIHE-20261014','overrides':{},'media':{},'moodle':{}})
        (root/'Konfiguration.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2));(root/'mode-config.js').write_text('window.SOZ_CONFIG='+json.dumps(cfg,ensure_ascii=False)+';\n')
        media={'slots':{'orientation':{'src':'','alt':'','label':'Orientierung · optionales Motiv'},'situation':{'src':'','alt':'','label':'Handlungssituation · optionales Motiv'}}}
        (root/'media-map.js').write_text('window.SOZ_MEDIA='+json.dumps(media,ensure_ascii=False)+';\n');(root/'media-map.json').write_text(json.dumps(media,ensure_ascii=False,indent=2))
        built.append((ls,root,data,instructions))
        summaries.append({'folder':root.name,'id':data['id'],'title':data['title'],'hours':ls['hours'],'budgets':ls['budgets'],'materials':len(ls['materials']),'tasks':counts,'zip':f'Downloads/BRC_LG01_LS{n:02d}_SCORM.zip'})
    # Browser DOM parsing is the same operation the approved editor uses.
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page()
        for ls,root,data,instructions in built:
            page.goto('about:blank');page.add_script_tag(path=str(root/'assets/progress-core.js'))
            result=page.evaluate('d=>{const meta=SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser());return {data:d,meta};}',json.loads(json.dumps(data)));data=result['data']
            (root/'lesson-data.js').write_text('window.SOZPAED='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n');(root/'progress-meta.js').write_text('window.SOZ_PROGRESS_META='+json.dumps(result['meta'],ensure_ascii=False,separators=(',',':'))+';\n')
            for name,content in data['pages'].items():(root/name).write_text(shell(name,content,ls['title'],ls['number']))
            for name in ['lehrkraft.html','druckansicht.html','scorm.html']:(root/name).write_text(shell(name,'',ls['title'],ls['number']))
            for phase in PHASES:
                for mode in range(1,6):
                    page.set_content(workbook_html(ls,phase,mode,instructions[phase][mode]));file=root/f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf';page.pdf(path=str(file),print_background=True,prefer_css_page_size=True)
                    payload=base64.b64encode(file.read_bytes()).decode();(root/f'goodnotes-phase-{phase}-W{mode}.js').write_text('window.GOODNOTES_PHASES=window.GOODNOTES_PHASES||{};window.GOODNOTES_PHASES['+json.dumps(phase+':'+str(mode))+']='+json.dumps(payload)+';\n')
            for mode in range(1,6):
                book=fitz.open()
                for phase in PHASES:
                    with fitz.open(root/f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf') as fragment:book.insert_pdf(fragment)
                book.save(root/f'pdf/GoodNotes_LG01_LS{ls["number"]:02d}_W{mode}.pdf');book.close()
            print('Built:',root.name,ls['title'],len(result['meta']['tasks']),'tasks; 30 phase PDFs',flush=True)
        browser.close()
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(REPO)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page()
            for ls,root,data,instructions in built:
                page.goto(f'http://127.0.0.1:{server.server_port}/'+root.relative_to(REPO).as_posix()+'/druckansicht.html');page.wait_for_function('window.SOZ_READY===true')
                # A complete printable student document: orientation, situation,
                # default W1 tasks and all source materials; other ways have books.
                page.pdf(path=str(root/f'pdf/LG01_LS{ls["number"]:02d}_Gesamtdruck_A4.pdf'),print_background=True,prefer_css_page_size=True)
                manifest(root,ls)
                target=REPO/f'Downloads/BRC_LG01_LS{ls["number"]:02d}_SCORM.zip'
                with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
                    for file in sorted(root.rglob('*')):
                        if file.is_file():z.write(file,file.relative_to(root).as_posix())
            browser.close()
    finally:server.shutdown()
    series={'title':'BRC LG01 · Ein Unternehmen gründen','hours':80,'templateCommit':'712a1200e1a67df2992e869730b1f26facfe7cbc','sourceSha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'lessons':summaries}
    (OUT/'series.json').write_text(json.dumps(series,ensure_ascii=False,indent=2))
    links=''.join(f'<article><small>LS{i["folder"][2:]} · {i["hours"]} Unterrichtsstunden</small><h2>{ESC(i["title"])}</h2><p><a href="{i["folder"]}/index.html">Lernsituation öffnen</a> · <a href="../../{i["zip"]}" download>SCORM-ZIP herunterladen</a></p></article>' for i in summaries)
    (OUT/'index.html').write_text('<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BioCasa · Plug-and-Play-Reihe</title><link rel="stylesheet" href="LS01/assets/styles.css"><style>article{padding:18px;border:1px solid #b8e0f2;border-radius:14px;background:#ffffffbb;margin:14px 0}</style><body><main class="shell main"><h1>BioCasa · Ein Unternehmen gründen</h1><p>Sechs Lernsituationen · fünf alternative Lernwege je Lernsituation · 80 Unterrichtsstunden</p>'+links+'</main></body></html>')
    collection=REPO/'Downloads/BRC_LG01_PlugAndPlay_Gesamtreihe_SCORM.zip'
    with zipfile.ZipFile(collection,'w',zipfile.ZIP_DEFLATED) as z:
        for lesson in summaries:z.write(REPO/lesson['zip'],Path(lesson['zip']).name)
        z.writestr('LIESMICH.txt','BioCasa · BRC LG01 · 80 Unterrichtsstunden\nSechs Einzelpakete, jeweils fünf alternative Lernwege.\nDieses Gesamtarchiv zuerst entpacken. In Moodle jede enthaltene SCORM-ZIP als eigene SCORM-Aktivität hochladen.\nDie Lehrkraft wählt den Lernweg im vorhandenen Lehrkräftemodus und exportiert bei Bedarf das konfigurierte Paket.\nPDF-/Druckzugriff und phasenbezogener GoodNotes-Import sind getrennt.\n')
    print('Built six individually importable packages and collection:',collection,flush=True)

if __name__=='__main__':main()
