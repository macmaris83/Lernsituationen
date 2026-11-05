#!/usr/bin/env python3
"""Apply the shared presentation source without regenerating lesson content."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

import master

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'Formmaster/manifest.json'
TEMPLATES = {'VORLAGE-TRADIERT', 'VORLAGE-FUENF-LERNWEGE'}
PROTECTED = {'runtime.js', 'progress.js', 'progress-core.js', 'revision185-core.js',
             'scorm.js', 'scorm-codec.js', 'teacher.js', 'export.js', 'situation.js'}
FOCUS_START = '/* Aufgabenfokus innerhalb der bestehenden Phasenseite. */'
FOCUS_END = '/* End shared task focus UI. */'
FOCUS_OPTIONS = '/* LS_TASK_FOCUS_OPTIONS */'


def focus_region(original, shared):
    """Replace only the isolated focus component, retaining local AI routing data.

    The runtime's storage, editor, media, assessment, and material functions outside
    this bounded IIFE are never replaced by another lesson's runtime.
    """
    if original.count(FOCUS_START) != 1 or shared.count(FOCUS_OPTIONS) != 1:
        raise ValueError('Aufgabenfokus: eindeutiger Komponentenanschluss fehlt')
    start = original.index(FOCUS_START)
    tail = original[start:]
    if FOCUS_END in tail:
        if tail.count(FOCUS_END) != 1:
            raise ValueError('Aufgabenfokus: mehrdeutige Endgrenze')
        stop = start + tail.index(FOCUS_END) + len(FOCUS_END)
    else:
        # First migration of the existing, isolated task-focus IIFE. The next
        # top-level IIFE is the material view and must remain byte-identical.
        first = tail.find('\n(()=>{')
        next_iife = tail.find('\n(()=>{', first + 1) if first >= 0 else -1
        if next_iife < 0 or not tail[:next_iife].rstrip().endswith('})();'):
            raise ValueError('Aufgabenfokus: vorhandene Komponentengrenze fehlt')
        stop = start + next_iife
    region = original[start:stop]
    if FOCUS_OPTIONS in region:
        if region.count(FOCUS_OPTIONS) != 1:
            raise ValueError('Aufgabenfokus: mehrdeutige lokale Optionen')
        options, _ = json.JSONDecoder().raw_decode(region.split(FOCUS_OPTIONS, 1)[1].lstrip())
    else:
        match = re.search(r'iframe\.src=(.*?);const info=', region)
        if not match:
            raise ValueError('Aufgabenfokus: vorhandenes KI-Ziel fehlt')
        expression = match[1]
        route = re.fullmatch(r"(\[[^\]]+\])\.includes\(document\.body\.dataset\.page\)\?('[^']+'):(\x27[^']+\x27)", expression)
        try:
            if route:
                pages, selected, default = map(ast.literal_eval, route.groups())
                if not isinstance(pages, list) or any(not isinstance(p, str) for p in pages):
                    raise ValueError('Ungültige phasenbezogene KI-Ziele')
                options = {'aiHelpUrl': default, 'aiHelpByPhase': dict.fromkeys(pages, selected)}
            else:
                options = {'aiHelpUrl': ast.literal_eval(expression)}
        except (SyntaxError, TypeError) as error:
            raise ValueError('Aufgabenfokus: unbekannte KI-Konfiguration') from error
    if (not isinstance(options, dict) or set(options) - {'aiHelpUrl', 'aiHelpByPhase'}
            or not isinstance(options.get('aiHelpUrl'), str)
            or not isinstance(options.get('aiHelpByPhase', {}), dict)
            or any(not isinstance(v, str) for v in options.get('aiHelpByPhase', {}).values())):
        raise ValueError('Aufgabenfokus: ungültige lokale Optionen')
    placeholder = FOCUS_OPTIONS + '{}'
    if shared.count(placeholder) != 1:
        raise ValueError('Aufgabenfokus: Optionsplatzhalter fehlt')
    component = shared.replace(placeholder, FOCUS_OPTIONS + json.dumps(options, ensure_ascii=False, separators=(',', ':')))
    return original[:start] + FOCUS_START + '\n' + component.rstrip() + '\n' + FOCUS_END + original[stop:]


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()


def targets(data):
    return [p for p in data['packages'] if p['typ'] == 'Lernsituation' or p['id'] in TEMPLATES]


def validate_coverage(root, data):
    """A new unpacked LS cannot silently bypass the shared master or its tests."""
    registered = {master.within(root, p['master']) for p in targets(data)}
    other_types = [master.within(root, p['master']) for p in data['packages']
                   if p['typ'] != 'Lernsituation' and p['id'] not in TEMPLATES]
    for content in (Path(root) / 'Fachbereiche').rglob('lesson-data.js'):
        folder = content.parent.resolve()
        if any(folder.is_relative_to(p) for p in other_types):
            continue
        if ((folder / 'imsmanifest.xml').is_file()
                and (folder / 'assets/runtime.js').is_file() and folder not in registered):
            raise ValueError('Nicht registrierte Lernsituation: ' + str(folder.relative_to(root)))


def bump(value):
    parts = list(master.version(value))
    parts += [0] * (3 - len(parts))
    parts[-1] += 1
    return '.'.join(map(str, parts))


def plan(root):
    """Validate the complete operation before writing any generated file."""
    root = Path(root)
    source = root / 'Formmaster'
    spec = json.loads((root / SOURCE).read_text(encoding='utf-8'))
    if spec.get('schemaVersion') != 1 or not spec.get('files'):
        raise ValueError('Ungültiger Formmaster')
    master.version(spec['version'])
    data = master.catalog(root)
    validate_coverage(root, data)
    selected = targets(data)
    previous = {p['id']: p for p in master.read_index(root)['packages']}
    source_bytes = {}

    def read_source(name):
        path = master.within(source, name)
        lexical = source / name
        if any(p.is_symlink() for p in [lexical, *lexical.parents] if p.is_relative_to(source)) or not path.is_file():
            raise ValueError(f'Formmaster-Quelle fehlt oder ist ein Symlink: {name}')
        source_bytes[name] = path.read_bytes()
        return source_bytes[name]

    # Preload every profile too: an invalid unused source must not hide until later.
    seen = set()
    for rule in spec['files']:
        target = rule['target']
        master.within(source, target)
        if not target.startswith('assets/') or Path(target).suffix not in {'.css', '.js'} or Path(target).name in PROTECTED:
            raise ValueError(f'Kein freigegebenes Gestaltungsziel: {target}')
        if target in seen:
            raise ValueError(f'Doppeltes Gestaltungsziel: {target}')
        seen.add(target)
        read_source(rule['source'])
        for extra in rule.get('append', {}).values():
            for name in extra:
                read_source(name)
        for name in rule.get('override', {}).values():
            read_source(name)
    region_targets = set()
    for rule in spec.get('components', []):
        if rule.get('component') != 'task-focus' or rule.get('target') != 'assets/runtime.js':
            raise ValueError('Unbekannte gemeinsame Bedienkomponente')
        if rule['target'] in region_targets:
            raise ValueError('Doppelte Bedienkomponente')
        region_targets.add(rule['target'])
        component = read_source(rule['source']).decode('utf-8')
        if component.count(FOCUS_OPTIONS + '{}') != 1:
            raise ValueError('Aufgabenfokus: Optionsplatzhalter fehlt')
    for rule in spec.get('regions', []):
        read_source(rule['source'])
        if rule['marker'] not in {'/* Metallic point UI from supplied reference. */', '/* Shared XP UI from IDN. */'}:
            raise ValueError('Unbekannte Grenze für das gemeinsame XP-UI')
        if any(p not in {'assets/progress-core.js', 'assets/revision185-core.js'} for p in rule['targets']):
            raise ValueError('Geschützte Logik darf nur an der XP-UI-Grenze ergänzt werden')
        for target in rule['targets']:
            if target in region_targets:
                raise ValueError(f'Doppelte XP-UI-Zielregion: {target}')
            region_targets.add(target)
    fingerprint = hashlib.sha256(encoded({'manifest': spec, 'sources': {
        name: master.digest(value) for name, value in sorted(source_bytes.items())}})).hexdigest()
    writes, changed = {}, {}

    def stage(path, value, package_changes, folder):
        if path.is_symlink():
            raise ValueError(f'Symlink im Gestaltungsziel: {path}')
        if not path.exists() or path.read_bytes() != value:
            writes[path] = value
            package_changes.add(path.relative_to(folder).as_posix())

    for item in selected:
        folder = master.within(root, item['master'])
        if not (folder / 'imsmanifest.xml').is_file():
            raise ValueError(f'{item["id"]}: imsmanifest.xml fehlt')
        # Also reject missing dependencies before applying any changes.
        master.files_for(root, item)
        package_changes = set()
        for rule in spec['files']:
            destination = master.within(folder, rule['target'])
            if rule.get('existingOnly') and not destination.exists():
                continue
            content = source_bytes[rule.get('override', {}).get(item['id'], rule['source'])]
            for extra in rule.get('append', {}).get(item['id'], []):
                content = content.rstrip() + b'\n\n' + source_bytes[extra]
            stage(destination, content, package_changes, folder)
        matched = 0
        for rule in spec.get('components', []):
            destination = master.within(folder, rule['target'])
            if not destination.is_file() or (folder / rule['target']).is_symlink():
                raise ValueError(f'{item["id"]}: Bedienkomponente fehlt oder ist ein Symlink')
            content = focus_region(destination.read_bytes().decode('utf-8'), source_bytes[rule['source']].decode('utf-8'))
            stage(destination, content.encode(), package_changes, folder)
        for rule in spec.get('regions', []):
            for name in rule['targets']:
                destination = master.within(folder, name)
                if not destination.exists():
                    continue
                old = destination.read_bytes()
                marker = rule['marker'].encode()
                if marker not in old:
                    if rule.get('skipMissingMarker'):
                        continue
                    raise ValueError(f'{item["id"]}: XP-UI-Grenze fehlt in {name}')
                if old.count(marker) != 1:
                    raise ValueError(f'{item["id"]}: mehrdeutige XP-UI-Grenze in {name}')
                matched += 1
                # The computation and storage core before the marker is never rewritten.
                content = old.split(marker)[0] + marker + b'\n' + source_bytes[rule['source']]
                stage(destination, content, package_changes, folder)
        if spec.get('regions') and not matched:
            raise ValueError(f'{item["id"]}: kein kompatibler XP-UI-Anschluss')
        form_changed = item.get('formVersion') != spec['version'] or item.get('formSourceSha256') != fingerprint
        old_version = item['version']
        new_version = max([old_version, spec['version']], key=master.version)
        exported = previous.get(item['id'])
        if (package_changes or form_changed) and exported and master.version(new_version) <= master.version(exported['version']):
            new_version = bump(exported['version'])
        item.update(version=new_version, formVersion=spec['version'], formSourceSha256=fingerprint)

        # Presentation metadata is separate from packageRevision and all storage IDs.
        config = folder / 'mode-config.js'
        if config.exists():
            original = config.read_bytes().decode('utf-8')
            match = re.search(r'window\.SOZ_CONFIG\s*=\s*', original)
            if not match:
                raise ValueError(f'{item["id"]}: SOZ_CONFIG fehlt')
            settings, length = json.JSONDecoder().raw_decode(original[match.end():])
            settings.update(packageVersion=new_version, formVersion=spec['version'])
            value = original[:match.end()] + json.dumps(settings, ensure_ascii=False, separators=(',', ':')) + original[match.end()+length:]
            stage(config, value.encode(), package_changes, folder)
        info_file = folder / 'Paketversion.json'
        if info_file.exists():
            info = json.loads(info_file.read_text(encoding='utf-8'))
            info.update(version=new_version, formVersion=spec['version'], formSourceSha256=fingerprint)
            stage(info_file, encoded(info), package_changes, folder)
        # Only version labels change; lesson HTML and stable manifest identifiers stay intact.
        managed = {rule['target'] for rule in spec['files']}
        managed.update(name for rule in spec.get('regions', []) for name in rule['targets'])
        managed.update(rule['target'] for rule in spec.get('components', []))
        for page in folder.glob('*.html'):
            original = page.read_bytes().decode('utf-8')
            value = re.sub(r'(<[^>]+data-package-version[^>]*>\s*Version\s+)[0-9]+\.[0-9]+(?:\.[0-9]+)?',
                           lambda m: m[1] + new_version, original)
            def cache_key(match):
                if match[3] not in managed:
                    return match[0]
                return match[1] + match[2] + match[3] + '?v=form-' + fingerprint[:16] + match[2]
            value = re.sub(r'''((?:src|href)=)(["'])(assets/[^?"'#]+)(?:\?[^"']*)?\2''', cache_key, value)
            stage(page, value.encode(), package_changes, folder)
        manifest = folder / 'imsmanifest.xml'
        original = manifest.read_bytes().decode('utf-8')
        value = re.sub(r'(<title>[^<]*? · )[0-9]+\.[0-9]+(?:\.[0-9]+)?(</title>)',
                       lambda m: m[1] + new_version + m[2], original)
        stage(manifest, value.encode(), package_changes, folder)
        if package_changes or form_changed or old_version != new_version:
            changed[item['id']] = sorted(package_changes)
    catalog_path = root / master.CATALOG
    if changed:
        writes[catalog_path] = encoded(data)
    return writes, changed


def sync(root):
    writes, changed = plan(root)
    for path, content in writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return changed


def check(root):
    writes, changed = plan(root)
    if writes:
        raise ValueError('Abweichung vom Formmaster: ' + ', '.join(changed) +
                         '. python tools/form_master.py sync ausführen.')
    return len(targets(master.catalog(Path(root))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['sync', 'check', 'inventory'])
    args = parser.parse_args()
    try:
        if args.command == 'inventory':
            data = master.catalog(ROOT)
            validate_coverage(ROOT, data)
            selected = targets(data)
            areas = sorted({'BRC', 'Geschichte', 'BFS dual', 'ReNo'} |
                           {p['bereich'] for p in selected if p['typ'] == 'Lernsituation'})
            print(json.dumps({'formVersion': json.loads((ROOT / SOURCE).read_text())['version'],
                'areas': {area: [p['id'] for p in selected if p['bereich'] == area and p['typ'] == 'Lernsituation']
                          for area in areas},
                'templates': [p['id'] for p in selected if p['id'] in TEMPLATES]}, ensure_ascii=False, indent=2))
        elif args.command == 'sync':
            changes = sync(ROOT)
            print(f'Formmaster synchronisiert: {len(changes)} Pakete aktualisiert.')
        else:
            print(f'{check(ROOT)} Lernsituationen/Vorlagen entsprechen dem Formmaster.')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Fehler: {error}\n')


if __name__ == '__main__':
    main()
