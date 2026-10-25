#!/usr/bin/env python3
"""Keep the existing textbook logo and its original reference visibly together.

Only a presentation stylesheet and its HTML links are added. Lesson wording,
progress metadata and task signatures are untouched. The bitmap is the original
asset from the catalogue master, copied only when a package does not contain it.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
LOGO = 'assets/lehrbuch-icon.png'
STYLESHEET = 'assets/book-reference.css'
LINK = '<link rel="stylesheet" href="' + STYLESHEET + '">'
CSS = '''/* Original textbook logo, kept beside its existing reference. */
.book-line{display:flex;align-items:center;gap:6px;max-width:100%}
.book-line .book-ref-icon{display:block;flex:0 0 32px;width:32px!important;max-width:32px;height:auto!important;margin:0!important;object-fit:contain}
.book-line .book-reference{min-width:0;overflow-wrap:anywhere}
.task-original-preview .book-line .book-reference,
.task-focus-panel .assignment-body .book-line .book-reference{margin-top:0!important}
@media print{.book-line{break-inside:avoid}.book-line .book-ref-icon{flex-basis:24px;width:24px!important;max-width:24px}}
'''


def patch(root: Path) -> dict:
    """Add the compact logo/reference layout to one extracted SCORM package."""
    root = Path(root)
    source = ROOT / 'Fachbereiche/BRC/LG01/LS01' / LOGO
    target = root / LOGO
    copied = not target.is_file()
    if copied:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    # Leave a package's existing bitmap untouched, including embedded metadata.
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (root / STYLESHEET).write_text(CSS, encoding='utf-8')
    changed = 0
    for page in root.glob('*.html'):
        markup = page.read_text(encoding='utf-8')
        if '<div class="lesson-content">' not in markup or STYLESHEET in markup:
            continue
        if '</head>' not in markup:
            raise ValueError('HTML head missing: ' + str(page))
        page.write_text(markup.replace('</head>', LINK + '</head>', 1), encoding='utf-8')
        changed += 1
    return {'logoAsset': LOGO, 'logoSha256': digest, 'copiedOriginalLogo': copied,
            'stylesheet': STYLESHEET, 'linkedPages': changed}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    print(json.dumps(patch(parser.parse_args().root), ensure_ascii=False))
