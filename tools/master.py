#!/usr/bin/env python3
"""Maintain one current SCORM export per catalogued master (Python stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CATALOG = 'master-katalog.json'
IGNORED = {'AGENTS.md', '.gitignore', '.DS_Store', 'master.json'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)', value):
        raise ValueError(f'Version muss zwei Zahlen enthalten, z. B. 1.2: {value!r}')
    return tuple(map(int, value.split('.')))


def within(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError(f'Unsicherer Pfad: {relative}')
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f'Pfad außerhalb des Masters: {relative}')
    return resolved


def catalog(root):
    data = json.loads((root / CATALOG).read_text(encoding='utf-8'))
    if data.get('schemaVersion') != 1 or not data.get('packages'):
        raise ValueError('Ungültiger oder leerer Master-Katalog')
    ids, masters, stems = set(), set(), set()
    for item in data['packages']:
        version(item['version'])
        if 'manifestOnly' in item and not isinstance(item['manifestOnly'], bool):
            raise ValueError(f'{item["id"]}: manifestOnly muss ein Wahrheitswert sein')
        for field in ('id', 'archiveStem'):
            if not re.fullmatch(r'[A-Za-z0-9_-]+', item[field]):
                raise ValueError(f'Ungültiges {field}: {item[field]}')
        master = within(root, item['master'])
        if item['id'] in ids or master in masters or item['archiveStem'] in stems:
            raise ValueError(f'Doppelter Master im Katalog: {item["id"]}')
        ids.add(item['id']); masters.add(master); stems.add(item['archiveStem'])
    return data


def files_for(root, item):
    folder = within(root, item['master'])
    if not (folder / 'imsmanifest.xml').is_file():
        raise ValueError(f'{item["id"]}: imsmanifest.xml fehlt im Master')
    files = {}
    for path in sorted(folder.rglob('*')):
        relative = path.relative_to(folder)
        if path.is_symlink():
            raise ValueError(f'Symlink im Master: {path}')
        if any(part.startswith('.') or part == '__pycache__' for part in relative.parts):
            continue
        if path.is_file() and path.name not in IGNORED and path.suffix not in ('.pyc', '.zip'):
            files[relative.as_posix()] = path
    manifest = ET.fromstring(files['imsmanifest.xml'].read_bytes())
    if manifest.tag.split('}')[-1] != 'manifest':
        raise ValueError(f'{item["id"]}: kein SCORM-Manifest')
    resources = [node for node in manifest.iter() if node.tag.split('}')[-1] == 'resource']
    if not resources:
        raise ValueError(f'{item["id"]}: keine Startressource')
    declared = {'imsmanifest.xml'}
    for node in manifest.iter():
        if node.tag.split('}')[-1] not in ('resource', 'file') or not node.get('href'):
            continue
        href = urlsplit(node.get('href'))
        if href.scheme or href.netloc:
            raise ValueError(f'{item["id"]}: externe Manifest-Datei {node.get("href")}')
        name = unquote(href.path)
        within(folder, name)
        if name not in files:
            raise ValueError(f'{item["id"]}: Manifest-Datei fehlt: {name}')
        declared.add(name)
    # Opt-in for tools with authoring/teacher pages beside their learner runtime.
    # Existing masters retain their complete current-file export unchanged.
    if item.get('manifestOnly', False):
        files = {name: path for name, path in files.items() if name in declared}
    return files


def snapshot(files):
    hashes = {name: digest(path.read_bytes()) for name, path in files.items()}
    encoded = json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode()
    return digest(encoded), hashes


def archive_path(item):
    return f'Downloads/{item["id"]}/{item["archiveStem"]}_v{item["version"]}_SCORM12.zip'


def archive_matches(path, hashes):
    if not path.is_file():
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or set(names) != set(hashes):
                return False
            return all(digest(archive.read(name)) == expected for name, expected in hashes.items())
    except (OSError, zipfile.BadZipFile, RuntimeError, KeyError):
        return False


def write_zip(path, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, file in files.items():
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file.read_bytes())


def read_index(root):
    path = root / 'Downloads/aktuell.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'packages': []}


def lesson_identity(read, package_id):
    """Read stable Lernsituation storage/SCO identifiers without executing JavaScript."""
    identities = {}
    for name, variable in (('lesson-data.js', 'SOZPAED'), ('progress-meta.js', 'SOZ_PROGRESS_META')):
        source = read(name).decode('utf-8-sig')
        match = re.fullmatch(r'\s*window\.' + variable + r'\s*=\s*(\{.*\})\s*;?\s*', source, re.S)
        if not match:
            raise ValueError(f'{package_id}: {name} enthält keine lesbaren Fortschrittsdaten')
        value = json.loads(match[1]).get('id')
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{package_id}: feste Lernstandskennung fehlt in {name}')
        identities[name] = value
    if identities['lesson-data.js'] != identities['progress-meta.js']:
        raise ValueError(f'{package_id}: Lernstandskennung in progress-meta.js stimmt nicht '
                         'mit lesson-data.js überein')
    manifest = ET.fromstring(read('imsmanifest.xml'))
    identities['manifest'] = manifest.get('identifier')
    for tag in ('organizations', 'organization', 'item', 'resource'):
        attributes = {
            'organizations': ('default',), 'organization': ('identifier',),
            'item': ('identifier', 'identifierref'), 'resource': ('identifier',),
        }[tag]
        identities[tag] = sorted(tuple(node.get(key, '') for key in attributes)
                                 for node in manifest.iter() if node.tag.split('}')[-1] == tag)
    identities['launch'] = sorted((node.get('identifier', ''),
                                   Path(unquote(urlsplit(node.get('href')).path)).as_posix())
                                  for node in manifest.iter()
                                  if node.tag.split('}')[-1] == 'resource' and node.get('href'))
    return identities


def verify_lesson_identity(root, item, files, previous):
    # Lernpfadübungen and BioCasa OS have independent data schemas.
    if item['typ'] != 'Lernsituation' and 'lesson-data.js' not in files:
        return
    try:
        current = lesson_identity(lambda name: files[name].read_bytes(), item['id'])
        if previous:
            prior_path = within(root, previous['archive'])
            with zipfile.ZipFile(prior_path) as archive:
                prior = lesson_identity(archive.read, item['id'])
            changed = [key for key in current if current[key] != prior[key]]
            if changed:
                raise ValueError(f'{item["id"]}: feste Lernstands-/SCORM-Kennung geändert '
                                 f'({", ".join(changed)}). Neue Paketversionen müssen die '
                                 'bisherigen Kennungen und die Startdatei erhalten.')
    except (KeyError, OSError, zipfile.BadZipFile, UnicodeError, ET.ParseError) as error:
        raise ValueError(f'{item["id"]}: Lernstandsidentität kann nicht sicher geprüft werden: '
                         f'{error}. Bisherigen Export wiederherstellen; Downloads bleiben unverändert.') from error


def write_index(root, data, entries, master_hashes=None):
    if master_hashes is None:
        master_hashes = {p['id']: snapshot(files_for(root, p))[0] for p in data['packages']}
    destination = root / 'Downloads'
    destination.mkdir(exist_ok=True)
    ordered = [entries[p['id']] for p in data['packages'] if p['id'] in entries]
    index = {'schemaVersion': 1, 'packages': ordered}
    (destination / 'aktuell.json').write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Aktuelle SCORM-Pakete', '',
             'Pro Master genau eine aktuelle ZIP. Versionsnummern haben zwei Teile (z. B. 1.2).',
             'Die Dateien werden aus den gepflegten Mastern erzeugt; frühere Fassungen liegen in der Git-Historie.',
             'Jede ZIP einzeln als SCORM-Aktivität in Moodle importieren. Vorhandene Moodle-Kopien werden nicht automatisch ersetzt.', '',
             '| Bereich | Lernsituation / Vorlage | Version | Aktuelles Paket |',
             '|---|---|---|---|']
    for item in data['packages']:
        entry = entries.get(item['id'])
        label = item['title'].replace('|', '\\|')
        current_hash = master_hashes[item['id']]
        if entry and entry['version'] == item['version'] and entry['master'] == item['master'] and entry['masterSha256'] == current_hash:
            lines.append(f'| {item["bereich"]} | {label} | {entry["version"]} | [ZIP]({entry["archive"][10:]}) |')
        else:
            lines.append(f'| {item["bereich"]} | {label} | {item["version"]} | Export ausstehend |')
    lines.extend(['', 'Maschinenlesbare Zuordnung und Prüfsummen: [aktuell.json](aktuell.json).',
                  'Vor einer automatischen Nutzung: `python tools/master.py check --archives`.', ''])
    (destination / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    rows = []
    for item in data['packages']:
        entry = entries.get(item['id'])
        valid = entry and entry['version'] == item['version'] and entry['master'] == item['master'] and entry['masterSha256'] == master_hashes[item['id']]
        link = f'<a download href="{html.escape(entry["archive"][10:], quote=True)}">SCORM-ZIP</a>' if valid else 'Export ausstehend'
        rows.append('<tr>' + ''.join(f'<td>{html.escape(str(item[key]))}</td>' for key in ('bereich', 'title', 'version')) + f'<td>{link}</td></tr>')
    page = '<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aktuelle SCORM-Pakete</title><style>body{font:16px/1.5 system-ui,sans-serif;color:#173a63;background:#f6fafc;margin:0}main{max-width:1100px;margin:auto;padding:24px}h1{border-bottom:5px solid #afca0b;padding-bottom:12px}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;padding:12px;border-bottom:1px solid #d9e6eb}a{color:#006a9d}.table{overflow:auto}</style><main><h1>Aktuelle SCORM-Pakete</h1><p>Pro Master eine aktuelle ZIP mit sichtbarer Versionsnummer. Jede ZIP einzeln in Moodle importieren.</p><div class="table"><table><thead><tr><th>Bereich</th><th>Lernsituation / Vorlage</th><th>Version</th><th>Download</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div><p>Bereits hochgeladene Moodle-Pakete werden durch Änderungen hier nicht automatisch ersetzt.</p></main></html>\n'
    (destination / 'index.html').write_text(page, encoding='utf-8')


def export(root, selected=None):
    data = catalog(root)
    previous = {item['id']: item for item in read_index(root)['packages']}
    entries = dict(previous)
    selected = set(selected or [p['id'] for p in data['packages']])
    unknown = selected - {p['id'] for p in data['packages']}
    if unknown:
        raise ValueError(f'Unbekannte Master: {sorted(unknown)}')
    # An invalid unselected master must not cause a late partial update of the index.
    master_hashes = {p['id']: snapshot(files_for(root, p))[0] for p in data['packages']}
    # Validate and stage every selected package before replacing any current export.
    with tempfile.TemporaryDirectory(prefix='scorm-current-') as temporary:
        staged = []
        for item in data['packages']:
            if item['id'] not in selected:
                continue
            files = files_for(root, item)
            master_hash, hashes = snapshot(files)
            old = previous.get(item['id'])
            verify_lesson_identity(root, item, files, old)
            if old and version(item['version']) < version(old['version']):
                raise ValueError(f'{item["id"]}: Versionsnummer darf nicht zurückgesetzt werden')
            if old and old['masterSha256'] != master_hash and old['version'] == item['version']:
                raise ValueError(f'{item["id"]}: Master geändert. Vor Export Versionsnummer erhöhen: '
                                 f'python tools/master.py set-version {item["id"]} X.Y')
            relative = archive_path(item)
            target = within(root, relative)
            stage = Path(temporary) / (item['id'] + '.zip')
            # Retain an existing byte-identical archive; no gratuitous binary rewrites.
            candidate = target
            legacy = item.get('legacyArchive')
            if not candidate.exists() and legacy:
                candidate = within(root, legacy)
            if archive_matches(candidate, hashes):
                shutil.copyfile(candidate, stage)
            else:
                write_zip(stage, files)
            if not archive_matches(stage, hashes):
                raise ValueError(f'{item["id"]}: Exportprüfung fehlgeschlagen')
            entries[item['id']] = {key: item[key] for key in ('id', 'title', 'bereich', 'typ', 'master', 'version')}
            entries[item['id']].update(archive=relative, masterSha256=master_hash,
                                       archiveSha256=digest(stage.read_bytes()), files=len(files))
            staged.append((item, stage, target))
        for item, stage, target in staged:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(stage, target)
            # Only this master's dedicated output directory is pruned.
            for old_archive in target.parent.glob('*.zip'):
                if old_archive != target:
                    old_archive.unlink()
            print(f'{item["id"]} · {item["version"]} → {target.relative_to(root)}')
    write_index(root, data, entries, master_hashes)


def check(root, archives=False):
    data = catalog(root)
    index = {item['id']: item for item in read_index(root)['packages']}
    for item in data['packages']:
        files = files_for(root, item)
        master_hash, hashes = snapshot(files)
        if archives:
            entry = index.get(item['id'])
            target = within(root, archive_path(item))
            if not entry or any(entry.get(key) != item[key] for key in ('version', 'master', 'title', 'bereich', 'typ')):
                raise ValueError(f'{item["id"]}: aktuelle ZIP-Zuordnung fehlt oder ist veraltet')
            if entry.get('archive') != archive_path(item) or entry['masterSha256'] != master_hash:
                raise ValueError(f'{item["id"]}: ZIP gehört nicht zum aktuellen Master')
            if not archive_matches(target, hashes) or digest(target.read_bytes()) != entry['archiveSha256']:
                raise ValueError(f'{item["id"]}: ZIP-Inhalt/Prüfsumme stimmt nicht')
            if len(list(target.parent.glob('*.zip'))) != 1:
                raise ValueError(f'{item["id"]}: mehrere aktuelle ZIPs')
    if archives and set(index) != {item['id'] for item in data['packages']}:
        raise ValueError('Download-Katalog enthält nicht genau die registrierten Master')
    print(f'{len(data["packages"])} Master geprüft' + ('; alle ZIPs aktuell und inhaltsgleich.' if archives else '.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    verify = commands.add_parser('check'); verify.add_argument('--archives', action='store_true')
    pack = commands.add_parser('export'); group = pack.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true'); group.add_argument('--id', action='append')
    bump = commands.add_parser('set-version'); bump.add_argument('id'); bump.add_argument('version')
    args = parser.parse_args()
    try:
        if args.command == 'export':
            export(ROOT, args.id)
        elif args.command == 'check':
            check(ROOT, args.archives)
        elif args.command == 'set-version':
            data = catalog(ROOT); new = version(args.version)
            item = next((p for p in data['packages'] if p['id'] == args.id), None)
            if item is None:
                raise ValueError(f'Unbekannter Master: {args.id}')
            if new <= version(item['version']):
                raise ValueError('Neue Version muss größer als die aktuelle sein')
            item['version'] = args.version
            (ROOT / CATALOG).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(f'{args.id}: {args.version}. Anschließend exportieren und prüfen.')
        else:
            for item in catalog(ROOT)['packages']:
                print(f'{item["id"]}\t{item["version"]}\t{item["master"]}')
    except (ValueError, OSError, KeyError, ET.ParseError) as error:
        parser.exit(1, f'Fehler: {error}\n')


if __name__ == '__main__':
    main()

