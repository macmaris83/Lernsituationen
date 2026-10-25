#!/usr/bin/env python3
"""Keep situation MC usable as a local exercise in SCORM review mode.

The LMS review record remains read-only. Only the transient quiz UI changes;
question text, answers, feedback, signatures and learner progress are untouched.
"""
from pathlib import Path

MARKER = '/* Situation MC: review practice without progress writes. */'


def patch(root):
    root = Path(root)
    source = root / 'assets' / 'situation.js'
    original = source.read_text(encoding='utf-8')
    if MARKER in original:
        return {'changed': False, 'file': 'assets/situation.js', 'reviewPractice': True}
    text = original
    replacements = [
        ("const P=window.SOZ_PROGRESS;const completed=", "const P=window.SOZ_PROGRESS;const reviewPractice=!!P?.readOnly;" + MARKER + "\nfunction saveAnswer(id,value,submitted){if(!reviewPractice)P?.quiz(id,value,submitted);}\nif(reviewPractice){const note=document.createElement('p');note.className='muted';note.dataset.quizPracticeNote='';note.setAttribute('role','status');note.textContent='Übungsansicht: Du kannst die Fragen beantworten. Dein gespeicherter Lernstand bleibt unverändert.';root.querySelector('h2')?.after(note);}\nconst completed="),
        ("input.disabled=!!P?.readOnly;", "input.disabled=false;"),
        ("submit.disabled=reset.disabled=!!P?.readOnly;", "submit.disabled=reset.disabled=false;"),
        ("P?.quiz(q.id,input.value,false);", "saveAnswer(q.id,input.value,false);"),
        ("P?.quiz(q.id,selected.value,true);", "saveAnswer(q.id,selected.value,true);"),
        ("P?.quiz(q.id,null,false);", "saveAnswer(q.id,null,false);"),
    ]
    for before, after in replacements:
        if text.count(before) != 1:
            raise ValueError(f'Expected situation MC anchor exactly once: {before}')
        text = text.replace(before, after, 1)
    source.write_text(text, encoding='utf-8')
    return {'changed': True, 'file': 'assets/situation.js', 'reviewPractice': True,
            'cause': 'SCORM review disabled all situation radio buttons and quiz actions.'}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(patch(args.root), ensure_ascii=False))
