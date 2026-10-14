#!/usr/bin/env python3
"""Compare the narrative source with task and material text in all six packages."""
from pathlib import Path
import json, re, subprocess
from lxml import html

REPO=Path(__file__).resolve().parents[1]
PHASES=['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren']
def normalized(value):return re.sub(r'\s+','',value)
def rendered(source):
    out=subprocess.run(['pandoc','-f','markdown','-t','html5'],input=source,text=True,capture_output=True,check=True).stdout
    return html.fragment_fromstring(out,create_parent='div')
def split_sections(source,level):
    matches=list(re.finditer(r'^'+('#'*level)+r' (.+)$',source,re.M))
    return [(m[1],source[m.end():matches[i+1].start() if i+1<len(matches) else len(source)]) for i,m in enumerate(matches)]

def main():
    source=(REPO/'Quellen/BRC_LG01/Reihenplan.md').read_text()
    for title,content in split_sections(source,1):
        match=re.match(r'LS (\d+) [–-]',title)
        if not match:continue
        number=int(match[1]);root=REPO/f'Reihen/BRC_LG01/LS{number:02d}'
        data=json.loads((root/'lesson-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
        sections={int(re.match(r'(\d+)\.',heading)[1]):body for heading,body in split_sections(content,2)}
        for i,(heading,body) in enumerate(split_sections(sections[6],3),1):
            page=html.fragment_fromstring(data['pages'][f'm{i}.html'],create_parent='div')
            document=page.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," paper ") or contains(concat(" ",normalize-space(@class)," ")," material-document ")]')
            assert len(document)==1,(number,i)
            assert normalized(document[0].text_content())==normalized(rendered(body).text_content()),(number,i,'material')
        for heading,body in split_sections(sections[5],3):
            mode=int(re.match(r'Lernweg W(\d)',heading)[1]);phases=split_sections(body,4);assert len(phases)==6
            for phase,(_,original) in zip(PHASES,phases):
                original=re.sub(r'^\*\*(Arbeitszeit|Arbeitsform|Materialien):\*\*.*$', '',original, flags=re.M)
                page=html.fragment_fromstring(data['pages'][phase+'.html'],create_parent='div')
                panel=page.xpath(f'.//*[@data-mode-panel="{mode}"]')[0]
                bodies=panel.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," assignment-body ")]')
                for task in bodies:
                    for timer in task.xpath('.//*[@data-time-ui]'):timer.getparent().remove(timer)
                actual=''.join(task.text_content() for task in bodies)
                assert normalized(actual)==normalized(rendered(original).text_content()),(number,mode,phase,'task prose')
        print(f'PASS: LS{number:02d} original material text and all five paths/six phase instructions unchanged',flush=True)

if __name__=='__main__':main()
