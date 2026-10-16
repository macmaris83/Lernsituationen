#!/usr/bin/env python3
"""Check/package BioCasa OS with the repository's single current-master exporter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import master

PACKAGE_ID = 'BRC-BIOCASA-OS'
VISIBLE_PAGES = ('dist/index.html', 'dist/preview.html')
TEACHER_FILES = {'preview.html', 'teacher-preview.js', 'teacher.html', 'teacher.js', 'package-writer.js'}


def project_item():
    data = master.catalog(ROOT)
    item = next(p for p in data['packages'] if p['id'] == PACKAGE_ID)
    if item['master'] != PROJECT.relative_to(ROOT).as_posix() + '/dist' or item.get('manifestOnly') is not True:
        raise ValueError('BioCasa OS muss denselben dist-Master mit manifestOnly verwenden')
    return data, item


def check(archive=False):
    _, item = project_item()
    for name in VISIBLE_PAGES:
        versions = re.findall(r'<span class="version">([^<]+)</span>', (PROJECT / name).read_text(encoding='utf-8'))
        if versions != [item['version']]:
            raise ValueError(f'{name}: sichtbare Version passt nicht zum Katalog')
    package = json.loads((PROJECT / 'package.json').read_text(encoding='utf-8'))
    if package['version'] != item['version'] + '.0':
        raise ValueError('npm-SemVer passt nicht zur Paketversion')
    files = master.files_for(ROOT, item)
    if TEACHER_FILES.intersection(files):
        raise ValueError('Lehrkräftedatei in der Schüler-ZIP')
    if 'calculator.js' not in files:
        raise ValueError('Rechner fehlt im Manifest')
    signature, hashes = master.snapshot(files)
    if archive:
        entries = master.read_index(ROOT)['packages']
        entry = next((p for p in entries if p['id'] == PACKAGE_ID), None)
        relative = master.archive_path(item)
        path = ROOT / relative
        if not entry or entry['version'] != item['version'] or entry['master'] != item['master'] or entry['archive'] != relative or entry['masterSha256'] != signature:
            raise ValueError('Aktueller BioCasa-OS-Export fehlt oder ist veraltet')
        if not master.archive_matches(path, hashes) or master.digest(path.read_bytes()) != entry['archiveSha256']:
            raise ValueError('BioCasa-OS-ZIP weicht vom aktuellen Master ab')
    print(f'{PACKAGE_ID} {item["version"]}: {len(files)} Schülerdateien geprüft' + ('; ZIP bytegenau' if archive else ''))


def set_version(value):
    check()
    data, item = project_item()
    if master.version(value) <= master.version(item['version']):
        raise ValueError('Neue Version muss größer als die aktuelle sein')
    old = item['version']
    replacements = {}
    for name in VISIBLE_PAGES:
        path = PROJECT / name
        replacements[path] = path.read_text(encoding='utf-8').replace(f'<span class="version">{old}</span>', f'<span class="version">{value}</span>')
    path = PROJECT / 'dist/KURZSTART.txt'
    replacements[path] = path.read_text(encoding='utf-8').replace(old, value)
    path = PROJECT / 'README.md'
    text = path.read_text(encoding='utf-8')
    replacements[path] = re.sub(r'\*\*Paketversion: [0-9]+\.[0-9]+\.\*\*', f'**Paketversion: {value}.**', text)
    path = PROJECT / 'package.json'
    package = json.loads(path.read_text(encoding='utf-8'))
    package['version'] = value + '.0'
    replacements[path] = json.dumps(package, ensure_ascii=False, indent=2) + '\n'
    item['version'] = value
    replacements[ROOT / master.CATALOG] = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    for path, text in replacements.items():
        path.write_text(text, encoding='utf-8')
    print(f'{PACKAGE_ID}: {old} → {value}. Anschließend testen und zentral exportieren.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    verify = commands.add_parser('check')
    verify.add_argument('--archive', action='store_true')
    bump = commands.add_parser('version')
    bump.add_argument('value')
    commands.add_parser('export')
    args = parser.parse_args()
    try:
        if args.command == 'version':
            set_version(args.value)
        elif args.command == 'export':
            check()
            master.export(ROOT, [PACKAGE_ID])
            check(True)
        else:
            check(args.archive)
    except (ValueError, OSError, KeyError, StopIteration) as error:
        parser.exit(1, f'Fehler: {error}\n')


if __name__ == '__main__':
    main()

