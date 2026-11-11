#!/usr/bin/env python3
"""Group the traditional tasks into 1–4 coherent assignments per phase.

No instructional sub-step is removed. Existing singleton identities and content
remain unchanged; grouped completion requires every previous constituent task.
The report is also the explicit old/new migration fixture for regression tests.
Uses only the Python standard library and the repository's span parser.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from w1_content_patch import SpanParser

PHASES = ['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren']
VERSION = '2026-11-11.coherent-tasks.1'
PLANS = {
 'BRC-LG01-LS01': {'informieren': [[1,2,3],[4,5],[6,7,8]]},
 'BRC-LG01-LS02': {'informieren': [[1,2],[3,4],[5,6],[7,8]]},
 'BRC-LG01-LS03': {'informieren': [[1,2],[3,4,5],[6,7],[8,9]],'entscheiden': [[1,2],[3],[4,5]]},
 'BRC-LG01-LS05': {'informieren': [[1,2,3],[4,5],[6,7],[8,9]],'entscheiden': [[1,2,3],[4,5]]},
 'BRC-LG01-LS06': {'informieren': [[1,2,3,4,5],[6],[7,8,9],[10,11,12]],'planen': [[1,2],[3,4],[5]],'entscheiden': [[1,2],[3,5],[4]]},
 'BRC-LG05-LS05': {'informieren': [[1,2,3],[4,5],[6]],'entscheiden': [[1],[2,3],[4,5]]},
 'BRC-LG05-LS06': {'informieren': [[1,2],[3,4],[5,6]]},
 'BRC-LG05-LS09': {'informieren': [[1,2],[3,4],[5,6]]},
 'BRC-LG05-LS10': {'informieren': [[1,2],[3,4],[5]]},
 'VORLAGE-TRADIERT': {'informieren': [[1,2],[3,4],[5,6]],'planen': [[1,2],[3,4],[5,6]],'entscheiden': [[1,2,3],[4,5],[6,7]],'durchfuehren': [[1,2],[3,4],[5,6,7]]},
}
PLANS['LS-MASTER'] = PLANS['BRC-LG01-LS03']
CLOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 6v6l4 2"></path></svg>'

def payload(path):
    return json.loads(path.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))

def write_payload(path, name, value):
    path.write_text(name+'='+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

def has(node, cls): return cls in node.attrs.get('class','').split()
def nodes(source, cls): return [n for n in SpanParser(source).nodes if has(n,cls)]
def inner(source,node): return source[node.open_end:source.rfind('</',node.open_end,node.end)]
def replace_spans(source, edits):
    for start,end,value in sorted(edits, reverse=True):source=source[:start]+value+source[end:]
    return source

class Text(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True);self.parts=[];self.feed(source)
    def handle_data(self,data):self.parts.append(data)

def text(source):return re.sub(r'\s+',' ',''.join(Text(source).parts)).strip()
def strip_times(source, only_ui=False):
    return replace_spans(source,[(n.start,n.end,'') for n in nodes(source,'assignment-time') if not only_ui or 'data-time-ui' in n.attrs])
def signature(source):
    value=text(strip_times(source,True));result=2166136261
    encoded=value.encode('utf-16-le')
    for i in range(0,len(encoded),2):result=((result^(encoded[i]+256*encoded[i+1]))*16777619)&0xffffffff
    return f'{result:08x}'

def attr(source,name,value):
    end=source.index('>');opening=source[:end]
    pattern=r'\s'+re.escape(name)+r'=(?:"[^"]*"|\x27[^\x27]*\x27)'
    pair=' '+name+'="'+html.escape(str(value),quote=True)+'"'
    opening=re.sub(pattern,lambda _:pair,opening,count=1) if re.search(pattern,opening) else opening+pair
    return opening+source[end:]

def minutes(card):
    times=nodes(card,'assignment-time')
    if not times:return 0.0
    assert len(times)==1,('Expected one duration',len(times))
    n=times[0];value=n.attrs.get('data-minutes')
    if value is None:
        match=re.search(r'(\d+(?:[.,]\d+)?)\s*Min',text(card[n.start:n.end]));assert match
        value=match[1].replace(',','.')
    return float(value)

def task_body(card):
    n=nodes(card,'assignment-body');assert len(n)==1;return inner(card,n[0])

def task_id(card):return nodes(card,'assignment-frame')[0].attrs['data-task-id']

def markdown(source):
    source=strip_times(source)
    source=re.sub(r'<(?:strong|b)\b[^>]*>(.*?)</(?:strong|b)>',r'**\1**',source,flags=re.S)
    source=re.sub(r'</(?:p|li|div|section)>','\n\n',source)
    source=re.sub(r'<li\b[^>]*>','• ',source)
    source=re.sub(r'<br\s*/?>','\n',source)
    source=re.sub(r'<[^>]+>','',source)
    return re.sub(r'\n\s*\n','\n\n',html.unescape(source)).strip()

def grouped_card(cards, number, key, refs):
    first=cards[0];body=task_body(first);total=sum(minutes(c) for c in cards)
    if len(cards)>1:
        bodies=[]
        for card in cards:
            source=strip_times(task_body(card))
            for old,new in refs.items():source=source.replace(old,new)
            bodies.append('<section class="assignment-step" data-source-task-id="'+task_id(card)+'">'+source+'</section>')
        timer='<span class="assignment-time" data-time-ui="true" data-minutes="'+format(total,'g')+'">'+CLOCK+' ca. '+format(total,'g').replace('.',',')+' Minuten</span>'
        body='\n'.join(bodies)+'\n'+timer
        body_node=nodes(first,'assignment-body')[0]
        first=replace_spans(first,[(body_node.open_end,first.rfind('</',body_node.open_end,body_node.end),body)])
        # Keep an honest combined work-form label, with the established icon.
        labels=[]
        for card in cards:
            badge=nodes(card,'assignment-social')
            if badge:
                label=text(card[badge[0].start:badge[0].end])
                if label not in labels:labels.append(label)
        badges=nodes(first,'assignment-social')
        if badges and len(labels)>1:
            n=badges[0];badge=first[n.start:n.end];label=' → '.join(labels)
            badge=re.sub(r'(<(?:small|span)(?:\s[^>]*)?>)[^<]*(</(?:small|span)>)',lambda m:m[1]+html.escape(label)+m[2],badge,count=1)
            badge=attr(badge,'title',label)
            first=replace_spans(first,[(n.start,n.end,badge)])
            first=attr(first,'data-workform-label',label)
        kinds=[]
        for card in cards:
            for n in nodes(card,'assignment-kind'):
                markup=card[n.start:n.end]
                if text(markup) not in [text(k) for k in kinds]:kinds.append(markup)
        if len(kinds)>1:
            n=nodes(first,'assignment-kind')[0];first=replace_spans(first,[(n.start,n.end,''.join(kinds))])
        first=attr(first,'data-task-minutes',format(total,'g'))
    else:
        changed=body
        for old,new in refs.items():changed=changed.replace(old,new)
        if changed!=body:
            n=nodes(first,'assignment-body')[0];first=replace_spans(first,[(n.open_end,first.rfind('</',n.open_end,n.end),changed)])
    sig=signature(task_body(first))
    first=attr(first,'data-task-stable-id',key)
    first=attr(first,'data-task-number',number)
    first=attr(first,'data-task-signature',sig)
    n=nodes(first,'assignment-number')[0]
    badge=attr(first[n.start:n.open_end]+'</'+n.tag+'>','aria-label','Aufgabe '+str(number))
    badge=badge[:badge.index('>')+1]+str(number)+'</'+n.tag+'>'
    first=replace_spans(first,[(n.start,n.end,badge)])
    first=re.sub(r'aria-label="Aufgabe \d+ als erledigt markieren"','aria-label="Aufgabe '+str(number)+' als erledigt markieren"',first)
    first=re.sub(r'title="Goodnotes: Seiten [^"]*"','title="GoodNotes-Arbeitsheft dieser Phase"',first)
    return first,sig,total

MIGRATE = """const migrationSource={...(raw.t||{})};const matches=(rule,source)=>(rule.from?.length&&rule.from.every(t=>source[t.id]===t.signature))||(rule.alternatives||[]).some(chain=>chain.length&&chain.every(t=>source[t.id]===t.signature));for(const stage of meta.migration?.stages||[]){const previous={...migrationSource};for(const [id,rule]of Object.entries(stage.tasks||{}))if(matches(rule,previous))migrationSource[id]=rule.signature;}for(const [id,value]of Object.entries(migrationSource))if(meta.tasks[id]?.signature===value)p.t[id]=value;for(const [id,rule]of Object.entries(meta.migration?.tasks||{})){if(meta.tasks[id]?.signature===rule.signature&&matches(rule,migrationSource))p.t[id]=rule.signature;}"""

def patch_core(path):
    source=path.read_text(encoding='utf-8')
    # The traditional template's original timer belongs to its legacy body
    # signature. Only new display-only group timers carry data-time-ui and
    # must be excluded here, exactly as they are in signature() above.
    source=source.replace(
        "const text=e=>(e.textContent||'').replace(/\\s+/g,' ').trim();",
        "const text=e=>{const copy=e.cloneNode(true);copy.querySelectorAll('.assignment-time[data-time-ui]').forEach(t=>t.remove());return (copy.textContent||'').replace(/\\s+/g,' ').trim();};")
    if 'const migrationSource=' not in source:
        start=source.find('for(const [id,rule]of Object.entries(meta.migration?.tasks||{}))')
        if start>=0:
            end=source.index('p.o=raw.o',start);source=source[:start]+MIGRATE+source[end:]
        else:
            point=source.index('p.o=raw.o');source=source[:point]+MIGRATE+source[point:]
    old="const id=phases.indexOf(phase)+':'+mode+':'+number;"
    source=source.replace(old,"const scope=phases.indexOf(phase)+':'+mode+':',stable=a.dataset.taskStableId;const id=stable&&stable.startsWith(scope)?stable:scope+number;")
    source=source.replace("'Aufgabe '+number+' als erledigt markieren'","'Aufgabe '+(a.dataset.taskNumber||number)+' als erledigt markieren'")
    if 'legacyTaskDictionaries:data.legacyTaskDictionaries' not in source:
        source=source.replace('return {id:data.id,', 'return {id:data.id,legacyTaskDictionaries:data.legacyTaskDictionaries||[],')
    if 'migration:data.progressMigration' not in source:
        source=source.replace('return {id:data.id,', 'return {id:data.id,migration:data.progressMigration||null,')
    path.write_text(source,encoding='utf-8')

def patch_codec(path):
    source=path.read_text(encoding='utf-8')
    if 'legacyTaskDictionaries' in source:return
    source=source.replace('function dictionary(){const tasks=window.SOZ_PROGRESS_META.tasks,ids=Object.keys(tasks).sort();','function dictionary(tasks=window.SOZ_PROGRESS_META.tasks){const ids=Object.keys(tasks).sort();')
    source=source.replace("const p=unpacked(v.slice(5)),d=dictionary();p.t={};if(p.th===d.hash)","const p=unpacked(v.slice(5)),d=[dictionary(),...(window.SOZ_PROGRESS_META.legacyTaskDictionaries||[]).map(tasks=>dictionary(tasks))].find(entry=>entry.hash===p.th);p.t={};if(d)")
    assert 'legacyTaskDictionaries' in source,'Unknown bitmap codec'
    path.write_text(source,encoding='utf-8')

def source_updates(root, reports):
    base=root/'Fachbereiche/BRC/LG01/quellen';source=base/'Reihenplan.md'
    if not source.exists():return
    content=source.read_text(encoding='utf-8');forms_path=base/'Arbeitsformen.json'
    forms=json.loads(forms_path.read_text()) if forms_path.exists() else {};oldforms=copy.deepcopy(forms)
    for report in reports:
        if not report['changed'] or not report['id'].startswith('BRC-LG01-'):continue
        ls=report['id'].split('-')[-1];lsnum=int(ls[2:]);data=payload(root/report['master']/'lesson-data.js')
        pattern=re.compile(r'(^# LS '+str(lsnum)+r' [^\n]*\n)(.*?)(?=^# LS |\Z)',re.M|re.S);match=pattern.search(content)
        if not match:raise AssertionError(('Source LS absent',ls))
        section=match[2]
        for index,phase in enumerate(PHASES):
            names=['Informieren / Analysieren','Planen','Entscheiden','Durchführen','Kontrollieren / Überprüfen','Reflektieren']
            pat=re.compile(r'(^#### '+re.escape(names[index])+r'\n)(.*?)(?=^####? |^## |\Z)',re.M|re.S);phase_match=pat.search(section)
            if not phase_match:raise AssertionError(('Source phase absent',ls,phase))
            before=phase_match[2];metadata=re.match(r'\A\s*(?:\*\*(?:Arbeitszeit|Arbeitsform|Materialien):\*\*[^\n]*\n)+\s*',before)
            if not metadata:raise AssertionError(('Source phase metadata absent',ls,phase))
            pieces=[]
            page=data['pages'][phase+'.html']
            for card_node,group in zip(nodes(page,'assignment-frame'),report['groups'][phase]):
                card=page[card_node.start:card_node.end];md=markdown(task_body(card));paragraphs=md.split('\n\n')
                pieces.append(str(group['number'])+'. '+paragraphs[0]+''.join('\n\n   '+p.replace('\n','\n   ') for p in paragraphs[1:]))
            new=before[:metadata.end()]+'\n\n'.join(pieces)+'\n\n'
            section=section[:phase_match.start(2)]+new+section[phase_match.end(2):]
            # Generator work-form source follows the new task positions.
            keys=[k for k in forms if k.startswith(ls+':'+phase+':1:')]
            for k in keys:del forms[k]
            for position,group in enumerate(report['groups'][phase],1):
                values=[oldforms.get(ls+':'+phase+':1:'+str(int(t['id'].split(':')[-1])),{}) for t in group['from']]
                values=[v for v in values if v]
                if values:
                    value=copy.deepcopy(values[0]);value['label']=' → '.join(dict.fromkeys(v['label'] for v in values));value['reason']=' '.join(dict.fromkeys(v.get('reason','') for v in values));forms[ls+':'+phase+':1:'+str(position)]=value
        content=content[:match.start(2)]+section+content[match.end(2):]
    source.write_text(content,encoding='utf-8')
    if forms_path.exists():forms_path.write_text(json.dumps(forms,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def apply(root):
    root=Path(root).resolve();catalog=json.loads((root/'master-katalog.json').read_text())
    packages=[p for p in catalog['packages'] if p['typ']=='Lernsituation' or p['id']=='VORLAGE-TRADIERT']
    report_path=root/'tools/fixtures/task-slimming-report.json';saved=json.loads(report_path.read_text()) if report_path.exists() else {'schemaVersion':1,'version':VERSION,'packages':[]}
    old_reports={r['id']:r for r in saved['packages']};reports=[];changed=[]
    for package in packages:
        master=root/package['master'];data_path=master/'lesson-data.js';meta_path=master/'progress-meta.js'
        data=payload(data_path);meta=payload(meta_path)
        if data.get('taskGroupingVersion')==VERSION:
            assert package['id'] in old_reports,('Missing migration report',package['id'])
            if old_reports[package['id']]['changed'] and (master/'assets/progress-core.js').exists():patch_core(master/'assets/progress-core.js')
            reports.append(old_reports[package['id']]);continue
        old_data=copy.deepcopy(data);old_meta=copy.deepcopy(meta);plan=PLANS.get(package['id'],{})
        old_numbers=[int(n.attrs.get('data-task-number','0')) for phase in PHASES for n in nodes(data['pages'][phase+'.html'],'assignment-frame')]
        transform=bool(plan) or old_numbers!=list(range(1,len(old_numbers)+1))
        report={'id':package['id'],'master':package['master'],'changed':False,'pdfChanged':False,'beforeMeta':old_meta,'afterMeta':None,'phaseCounts':{},'groups':{},'crossReferences':[]}
        all_tasks={};rules={};number=0;expected_count=0;instruction_checks=[]
        refs={'Aufgabe 5; endgültig':'Aufgabe 6 in der Phase Planen; endgültig'} if package['id']=='VORLAGE-TRADIERT' else {}
        for phase in PHASES:
            page=phase+'.html';before=data['pages'][page];card_nodes=nodes(before,'assignment-frame');cards=[before[n.start:n.end] for n in card_nodes]
            groups=plan.get(phase,[[i+1] for i in range(len(cards))]);flat=[i for g in groups for i in g]
            assert sorted(flat)==list(range(1,len(cards)+1)),(package['id'],phase,'Invalid grouping',flat)
            assert 1<=len(groups)<=4,(package['id'],phase,len(groups))
            report['phaseCounts'][phase]={'before':len(cards),'after':len(groups)};report['groups'][phase]=[]
            replacements=[]
            for group in groups:
                source_cards=[cards[i-1] for i in group];key=task_id(source_cards[0]);number+=1
                if transform:card,sig,total=grouped_card(source_cards,number,key,refs)
                else:card=source_cards[0];sig=old_meta['tasks'][key]['signature'];total=minutes(card)
                # Exact instruction preservation, allowing only the recorded reference correction.
                original=' '.join(text(strip_times(task_body(c))) for c in source_cards)
                for old,new in refs.items():original=original.replace(old,new)
                assert text(strip_times(task_body(card)))==original,(package['id'],phase,key,'Instruction loss')
                instruction_checks.append(hashlib.sha256(original.encode()).hexdigest())
                requirements=[{'id':task_id(c),'signature':old_meta['tasks'][task_id(c)]['signature']} for c in source_cards]
                all_tasks[key]=dict(old_meta['tasks'][key],signature=sig)
                if len(group)>1 or sig!=old_meta['tasks'][key]['signature']:rules[key]={'signature':sig,'from':requirements}
                report['groups'][phase].append({'id':key,'number':number,'from':requirements,'minutes':total})
                replacements.append((card_nodes[group[0]-1].start,card_nodes[group[0]-1].end,card))
                for i in group[1:]:replacements.append((card_nodes[i-1].start,card_nodes[i-1].end,''))
            after=replace_spans(before,replacements)
            # A nonadjacent semantic group may move a later sub-step into its coherent block.
            assert sum(minutes(c) for c in cards)==sum(g['minutes'] for g in report['groups'][phase]),(package['id'],phase,'Duration changed')
            data['pages'][page]=after
            if data.get('sourceTaskCounts',{}).get(phase) is not None:data['sourceTaskCounts'][phase]={'1':len(groups)}
            if phase in data.get('phases',{}):
                mode=data['phases'][phase]['modes']['1'];parts=[]
                for n,g in zip(nodes(after,'assignment-frame'),report['groups'][phase]):parts.append(str(g['number'])+'. '+markdown(task_body(after[n.start:n.end])).replace('\n\n','\n\n   '))
                mode['markdown']='\n\n'.join(parts)
            if before!=after:report['changed']=True;report['pdfChanged']=True
            static=master/page
            if static.exists():
                markup=static.read_text(encoding='utf-8')
                if before in markup:markup=markup.replace(before,after,1)
                else:
                    existing=nodes(markup,'assignment-frame');assert len(existing)==len(cards),(static,'Static assignment count mismatch')
                    for n,old in zip(existing,cards):assert markup[n.start:n.end]==old,(static,'Static assignment differs')
                    # Reuse exact card edits without touching the surrounding page or materials.
                    offsets=[(n.start,n.end) for n in existing];new_edits=[]
                    for group,g in zip(groups,report['groups'][phase]):
                        value=next(e[2] for e in replacements if e[0]==card_nodes[group[0]-1].start)
                        new_edits.append((*offsets[group[0]-1],value))
                        for i in group[1:]:new_edits.append((*offsets[i-1],''))
                    markup=replace_spans(markup,new_edits)
                static.write_text(markup,encoding='utf-8')
        if not report['changed']:
            report['afterMeta']=old_meta;reports.append(report);continue
        migration=copy.deepcopy(old_meta.get('migration') or data.get('progressMigration') or {})
        old_rules=migration.get('tasks',{})
        if old_rules:migration.setdefault('stages',[]).append({'tasks':old_rules})
        # Retain migrations for singleton tasks and apply them after historical stages.
        current_rules={k:v for k,v in old_rules.items() if k in all_tasks and all_tasks[k]['signature']==v['signature']}
        current_rules.update(rules);migration['tasks']=current_rules
        data['progressMigration']=migration;meta['migration']=migration;meta['tasks']=all_tasks
        if package['id']=='VORLAGE-TRADIERT':
            dictionaries=data.setdefault('legacyTaskDictionaries',[])
            if old_meta['tasks'] not in dictionaries:dictionaries.append(old_meta['tasks'])
            meta['legacyTaskDictionaries']=copy.deepcopy(dictionaries)
        if refs:report['crossReferences']=[{'from':k,'to':v} for k,v in refs.items()]
        data['taskGroupingVersion']=VERSION;report['instructionChecks']=instruction_checks;report['afterMeta']=copy.deepcopy(meta)
        assert data['competencies']==old_data['competencies'] and meta['quiz']==old_meta['quiz']
        assert data['pages']['index.html']==old_data['pages']['index.html'] and data['pages']['handlungssituation.html']==old_data['pages']['handlungssituation.html']
        write_payload(data_path,'window.SOZPAED',data);write_payload(meta_path,'window.SOZ_PROGRESS_META',meta)
        core=master/'assets/progress-core.js'
        if core.exists():patch_core(core)
        if package['id']=='VORLAGE-TRADIERT' and (master/'assets/scorm-codec.js').exists():patch_codec(master/'assets/scorm-codec.js')
        reports.append(report);changed.append(package)
    source_updates(root,[r for r in reports if r['id'] in {p['id'] for p in changed}])
    baseline=root/'tools/fixtures/traditional-path-baseline.json'
    if baseline.exists() and changed:
        from check_traditional_paths import capture
        snapshot=json.loads(baseline.read_text())
        for package in changed:
            after=capture(root,package);before=snapshot[package['id']]
            for key in set(before)-{'tasks','frames'}:assert before[key]==after[key],(package['id'],'Unexpected baseline change',key)
            snapshot[package['id']]=after
        baseline.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    saved['packages']=reports;report_path.parent.mkdir(parents=True,exist_ok=True);report_path.write_text(json.dumps(saved,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'changed':[p['id'] for p in changed],'audited':len(reports),'before':sum(len(r['beforeMeta']['tasks']) for r in reports),'after':sum(len(r['afterMeta']['tasks']) for r in reports)},ensure_ascii=False))
    return saved

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args();apply(args.root)
