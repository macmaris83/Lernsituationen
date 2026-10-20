#!/usr/bin/env python3
"""Import supplied original LG03 images without cropping or re-encoding.

Accept one or several ZIPs, or a directory containing the original files.
Archive paths are inspected, never extracted directly. A complete set contains
LS01..LS12 with one Orientierung and one Handlungssituation each.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile
from PIL import Image
from lg03_source import load_source

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / 'Quellen/BRC_LG03'
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}


def candidates(path):
    if path.is_dir():
        for image in sorted(path.rglob('*')):
            if image.is_file() and image.suffix.lower() in EXTENSIONS:
                yield image.relative_to(path).as_posix(), image.read_bytes()
    else:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.is_dir() or '__MACOSX' in info.filename or Path(info.filename).name.startswith('._'):
                    continue
                if Path(info.filename).suffix.lower() in EXTENSIONS:
                    yield info.filename, archive.read(info)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path, nargs='+')
    parser.add_argument('--partial', action='store_true', help='Import a first ZIP while waiting for the remaining parts.')
    args = parser.parse_args()
    lessons = {ls['number']:ls for ls in load_source(SOURCE / 'Reihenplan.md')}
    mapping_path = SOURCE / 'Bildzuordnung.json'
    mapping = json.loads(mapping_path.read_text()) if mapping_path.exists() else {}
    destination = SOURCE / 'Bilder'; destination.mkdir(exist_ok=True)
    seen = set()
    for source in args.sources:
        for name, data in candidates(source):
            match = re.search(r'LS[ _-]*0?(\d{1,2})(?!\d)', name, re.I)
            if not match:
                raise ValueError('No lesson number in image path: ' + name)
            n = int(match[1])
            if n not in lessons: raise ValueError('Unknown lesson number: ' + name)
            role = 'orientation' if re.search(r'orient', name, re.I) else 'situation' if re.search(r'handlung|situation', name, re.I) else None
            if not role: raise ValueError('No image role in image path: ' + name)
            key = (n, role)
            if key in seen: raise ValueError('Duplicate supplied image role: ' + name)
            seen.add(key)
            with Image.open(io.BytesIO(data)) as image:
                image.verify()
            with Image.open(io.BytesIO(data)) as image:
                dimensions = list(image.size)
            filename = f'biocasa-lg03-ls{n:02d}-{role}' + Path(name).suffix.lower()
            target = destination / filename
            if target.exists() and target.read_bytes() != data:
                raise ValueError('Different original already imported: ' + filename)
            target.write_bytes(data)
            mapping.setdefault(str(n), {})[role] = {
                'archive_path': name, 'filename': filename,
                'alt': ('Orientierungsbild' if role == 'orientation' else 'Bild zur Handlungssituation') + ' · BioCasa · ' + lessons[n]['title'],
                'sha256': hashlib.sha256(data).hexdigest(), 'dimensions': dimensions,
            }
            print(f'Imported LS{n:02d} {role}: {dimensions[0]}×{dimensions[1]}, unchanged bytes')
    mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
    missing = [(n, role) for n in range(1,13) for role in ['orientation','situation'] if role not in mapping.get(str(n), {})]
    if missing and not args.partial:
        raise ValueError('Original images still missing: ' + ', '.join(f'LS{n:02d} {role}' for n,role in missing))
    print('Original image roles available:', 24-len(missing), '/ 24')


if __name__ == '__main__': main()
