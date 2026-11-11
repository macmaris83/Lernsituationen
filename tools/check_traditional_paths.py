#!/usr/bin/env python3
"""Verify W1-only packages against their explicit preservation snapshot.

Use --snapshot once on the unmodified source tree. The committed fixture records
existing W1 content, task identities/signatures, quiz and competency definitions.
A deliberate grouping migration may update the snapshot after checking original
content preservation; ordinary checks cannot silently refresh it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

PHASES = ['informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren']
REMOVED = re.compile(r'(?:^|[-_/])W(?:eg)?[2-5](?=[._/-]|$)', re.I)
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

def payload(path):
    return json.loads(path.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))

class Tasks(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=False)
        self.stack=[]; self.tasks=[]; self.current=None; self.body=None; self.panels=[]
        self.feed(markup)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); classes=a.get('class','').split()
        mode=a.get('data-mode-panel') or next((x[1] for x in reversed(self.stack) if x[1]), None)
        if 'data-mode-panel' in a:self.panels.append(a['data-mode-panel'])
        if 'assignment-frame' in classes and mode=='1':
            self.current={'id':a.get('data-task-id'), 'number':a.get('data-task-number'), 'body':'', 'minutes':[]}
            self.tasks.append(self.current)
        if self.current is not None and 'data-minutes' in a:self.current['minutes'].append(a['data-minutes'])
        if self.body is not None:self.current['body']+=self.get_starttag_text()
        if self.current is not None and 'assignment-body' in classes:self.body=len(self.stack)
        if tag not in VOID:self.stack.append((tag, mode, 'assignment-frame' in classes))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if not self.stack:return
        if self.body is not None:
            if len(self.stack)-1==self.body:self.body=None
            else:self.current['body']+='</'+tag+'>'
        _,_,frame=self.stack.pop()
        if frame:self.current=None
    def handle_data(self,data):
        if self.body is not None:self.current['body']+=data
    def handle_entityref(self,name):self.handle_data('&'+name+';')
    def handle_charref(self,name):self.handle_data('&#'+name+';')
    def handle_comment(self,data):
        if self.body is not None:self.current['body']+='<!--'+data+'-->'

class InstructionText(HTMLParser):
    """Read task text without the timer UI, independently of the grouping tool."""
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.parts=[];self.suppressed=[];self.feed(markup)
    def handle_starttag(self,tag,attrs):
        hidden=any(self.suppressed) or 'assignment-time' in dict(attrs).get('class','').split()
        if tag not in VOID:self.suppressed.append(hidden)
    def handle_startendtag(self,tag,attrs):pass
    def handle_endtag(self,tag):
        if self.suppressed:self.suppressed.pop()
    def handle_data(self,data):
        if not any(self.suppressed):self.parts.append(data)
    def normalized(self):return re.sub(r'\s+',' ',''.join(self.parts)).strip()

def check_grouping(item, data, meta, report):
    key=item['id'];before=report['beforeMeta'];after=report['afterMeta']
    assert after['tasks']==meta['tasks'],(key,'Current assignments differ from the grouping report')
    assert after.get('migration')==meta.get('migration'),(key,'Current migration differs from the grouping report')
    seen=[];numbers=[];checks=[]
    for phase in PHASES:
        groups=report['groups'][phase];cards=Tasks(data['pages'][phase+'.html']).tasks
        assert len(groups)==len(cards),(key,phase,'Reported groups differ from current cards')
        assert report['phaseCounts'][phase]=={'before':sum(t['phase']==phase and t['mode']==1 for t in before['tasks'].values()),'after':len(cards)},(key,phase,'Incorrect grouping counts')
        for group,card in zip(groups,cards):
            assert group['id']==card['id'],(key,phase,'Group order or stable ID changed')
            assert group['number']==int(card['number']),(key,phase,'Reported task number differs')
            assert group['from'],(key,phase,'A group has no original assignments')
            numbers.append(group['number'])
            for old in group['from']:
                assert before['tasks'][old['id']]['signature']==old['signature'],(key,'Incorrect original signature',old['id'])
                assert before['tasks'][old['id']]['phase']==phase and before['tasks'][old['id']]['mode']==1,(key,'A group crosses a phase or learning path',old['id'])
                seen.append(old['id'])
            checks.append(hashlib.sha256(InstructionText(card['body']).normalized().encode()).hexdigest())
    expected=[task for task,value in before['tasks'].items() if value['mode']==1]
    assert len(seen)==len(set(seen)) and set(seen)==set(expected),(key,'Every original W1 assignment must occur in exactly one group')
    assert numbers==list(range(1,len(numbers)+1)),(key,'Reported task numbers must be continuous')
    if report['changed']:assert checks==report['instructionChecks'],(key,'Grouped instruction text differs from the preserved original text')

def capture(root, item):
    master=root/item['master']; data=payload(master/'lesson-data.js'); meta=payload(master/'progress-meta.js')
    frames={}
    for phase in PHASES:
        parsed=Tasks(data['pages'][phase+'.html'])
        frames[phase]=[dict(t, body=hashlib.sha256(t['body'].encode()).hexdigest()) for t in parsed.tasks]
    return {'id':data['id'], 'storageVersion':data.get('version'),
            'tasks':{k:v for k,v in meta['tasks'].items() if v['mode']==1},
            'frames':frames, 'competencies':data.get('competencies'),
            'quiz':meta.get('quiz'), 'quizSignature':meta.get('quizSignature'),
            'orientationSignature':meta.get('orientationSignature'),
            'flashcard':meta.get('flashcard'), 'orientationVideo':meta.get('orientationVideo')}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--snapshot',action='store_true')
    parser.add_argument('--fixture',type=Path)
    args=parser.parse_args();root=args.root.resolve()
    fixture=args.fixture or root/'tools/fixtures/traditional-path-baseline.json'
    packages=[p for p in json.loads((root/'master-katalog.json').read_text())['packages'] if p['typ']=='Lernsituation' or p['id']=='VORLAGE-TRADIERT']
    actual={p['id']:capture(root,p) for p in packages}
    if args.snapshot:
        if fixture.exists():raise SystemExit('Refusing to overwrite the existing preservation fixture.')
        fixture.parent.mkdir(parents=True,exist_ok=True)
        fixture.write_text(json.dumps(actual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'Captured {len(actual)} original W1 packages.');return
    baseline=json.loads(fixture.read_text(encoding='utf-8'))
    report_path=root/'tools/fixtures/task-slimming-report.json'
    reports={p['id']:p for p in json.loads(report_path.read_text())['packages']} if report_path.exists() else {}
    for item in packages:
        key=item['id'];master=root/item['master'];data=payload(master/'lesson-data.js');meta=payload(master/'progress-meta.js')
        assert key in baseline,(key,'Missing explicit preservation baseline')
        if data.get('taskGroupingVersion'):
            assert key in reports,(key,'Missing explicit task grouping report')
            check_grouping(item,data,meta,reports[key])
        for field in baseline[key]:assert actual[key][field]==baseline[key][field],(key,'W1 content or identity changed',field)
        assert {t['mode'] for t in meta['tasks'].values()}=={1},(key,'Nontraditional metadata')
        expected_numbers=[]
        for phase in PHASES:
            parsed=Tasks(data['pages'][phase+'.html']);static=Tasks((master/(phase+'.html')).read_text())
            assert set(parsed.panels)=={'1'},(key,phase,'Unexpected data panels',parsed.panels)
            assert set(static.panels)=={'1'},(key,phase,'Unexpected HTML panels',static.panels)
            assert parsed.tasks==static.tasks,(key,phase,'HTML/data divergence')
            assert parsed.tasks,(key,phase,'Missing W1 assignments')
            assert 1<=len(parsed.tasks)<=4,(key,phase,'Expected one to four clearly grouped assignments',len(parsed.tasks))
            for t in parsed.tasks:
                assert t['id'] in meta['tasks'],(key,phase,'Unregistered assignment',t['id'])
                assert t['number'] is not None,(key,phase,'Missing visible task number',t['id'])
                expected_numbers.append(int(t['number']))
        assert expected_numbers==list(range(1,len(expected_numbers)+1)),(key,'Task numbers must continue across phases',expected_numbers)
        for field in ['workbooks','sourceTaskCounts']:
            value=data.get(field,{})
            if field=='workbooks':assert set(value)<={'1'},(key,field)
            else:
                for phase,modes in value.items():assert set(modes)<={'1'},(key,field,phase)
        cfg=json.loads((master/'Konfiguration.json').read_text()) if (master/'Konfiguration.json').is_file() else payload(master/'mode-config.js')
        assert cfg.get('mode',1)==1 and not cfg.get('allowStudentMode',False),(key,'Configuration permits another path')
        paths=cfg.get('learningPaths',{})
        if isinstance(paths,dict):assert set(paths)<={'1'},(key,'Editor paths')
        for p in master.rglob('*'):
            if p.is_file():assert not REMOVED.search(p.relative_to(master).as_posix()),(key,'Unused path file',str(p))
        for node in ET.parse(master/'imsmanifest.xml').iter():
            href=node.get('href')
            if href:
                assert not REMOVED.search(href),(key,'Unused path in manifest',href)
                assert (master/href).is_file(),(key,'Missing manifest file',href)
        print('PASS traditional path:',key,'recorded W1 content, 1–4 tasks per phase, continuous numbering, checks, files and manifest')
    print(f'PASS: {len(packages)} packages use only the traditional path.')

if __name__=='__main__':main()
