#!/usr/bin/env python3
"""Transfer the current catalogue master's UI to an uploaded SCORM, without editing content.

The output is an external delivery, never a replacement for a catalogue master.
Lesson data, progress metadata, configuration, media and original PDFs remain byte-identical.
Only the page shell, technical assets and manifest file inventory change. Phase-only
GoodNotes imports are copies of pages from the original workbooks.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONTENT_START = '<div class="lesson-content">'
CONTENT_END = '</div></main>'
PROTECTED = {'lesson-data.js', 'progress-meta.js', 'mode-config.js', 'Konfiguration.json',
             'media-map.js', 'media-map.json'}
STALE = {'package-data.js', 'goodnotes-share-data.js'}


def prepare_workbooks(root: Path) -> None:
    # PyMuPDF is needed for actual PDF copies, not for the stdlib-only regression checks.
    from prepare_phase_workbooks import prepare
    prepare(root)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payload(raw: bytes) -> dict:
    return json.loads(raw.decode('utf-8').split('=', 1)[1].strip().removesuffix(';'))


def content_of(source: str) -> str | None:
    start = source.find(CONTENT_START)
    if start < 0:
        return None
    start += len(CONTENT_START)
    end = source.find(CONTENT_END, start)
    if end < 0:
        raise ValueError('Unvollständiger Inhaltsbereich')
    return source[start:end]


def shell(original: str, template: str, page: str, lesson_id: str) -> str:
    content = content_of(original)
    if content is not None:
        start = template.index(CONTENT_START) + len(CONTENT_START)
        end = template.index(CONTENT_END, start)
        template = template[:start] + content + template[end:]
    title = re.search(r'<title>.*?</title>', original, re.S)
    if title:
        template = re.sub(r'<title>.*?</title>', lambda _: title[0], template, flags=re.S)
    template = re.sub(r'data-page="[^"]*"', lambda _: f'data-page="{page}"', template)
    template = re.sub(r'data-ls-id="[^"]*"', lambda _: f'data-ls-id="{lesson_id}"', template)
    # The whole-document PDF must point to the upload's document, not the template's.
    old_pdf = re.search(r'href="(pdf/[^"]*Gesamtdruck[^"]*\.pdf)"', original)
    if old_pdf:
        template = re.sub(r'href="pdf/[^"]*Gesamtdruck[^"]*\.pdf"',
                          lambda _: f'href="{old_pdf[1]}"', template)
    return template


def read_archive(raw: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Doppelte ZIP-Pfade')
        result = {}
        for name in names:
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name:
                raise ValueError(f'Unsicherer ZIP-Pfad: {name}')
            if not name.endswith('/'):
                result[name] = archive.read(name)
        return result


def archive(path: Path, files: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, raw)


def manifest(root: Path, original: bytes) -> None:
    tree = ET.ElementTree(ET.fromstring(original))
    resource = next(n for n in tree.getroot().iter() if n.tag.split('}')[-1] == 'resource')
    ns = resource.tag.split('}')[0][1:]
    for node in list(resource):
        if node.tag.split('}')[-1] == 'file':
            resource.remove(node)
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.name != 'imsmanifest.xml':
            ET.SubElement(resource, '{' + ns + '}file', {'href': path.relative_to(root).as_posix()})
    ET.register_namespace('', ns)
    ET.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')
    tree.write(root / 'imsmanifest.xml', encoding='utf-8', xml_declaration=True)


def transfer(raw: bytes, target: Path, template: Path) -> dict:
    original = read_archive(raw)
    if target.exists():
        raise ValueError(f'Ziel muss neu sein: {target}')
    data = payload(original['lesson-data.js'])
    target.mkdir(parents=True)
    for name, source in original.items():
        if name in STALE:
            continue
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source)
    copied = []
    # Shared technical files only; never copy lesson-specific images or PDF content.
    for path in sorted((template / 'assets').iterdir()):
        if not path.is_file():
            continue
        if path.suffix not in {'.js', '.css', '.otf', '.txt'} and path.name != 'bbs1-campus-background.png':
            continue
        relative = path.relative_to(template).as_posix()
        shutil.copyfile(path, target / relative)
        copied.append(relative)
    for name, source in original.items():
        if not name.endswith('.html') or name == 'scorm.html':
            continue
        source_html = source.decode('utf-8')
        current = template / name
        if not current.is_file():
            if re.search(r'http-equiv=["\']refresh["\']', source_html, re.I):
                # Legacy launch aliases have no UI shell and keep their exact bytes.
                continue
            if not re.fullmatch(r'm\d+\.html', name):
                raise ValueError(f'Keine freigegebene Hülle für {name}')
            current = template / 'm1.html'
        result = shell(source_html, current.read_text(), name, data['id'])
        (target / name).write_text(result)
        assert content_of(result) == content_of(source_html), name
    prepare_workbooks(target)
    manifest(target, original['imsmanifest.xml'])
    protected = {}
    for name, source in original.items():
        if name in PROTECTED or name.startswith('pdf/') or (
                name.startswith('assets/') and name not in copied):
            assert (target / name).read_bytes() == source, name
            protected[name] = sha(source)
    # Check every data page, not merely the tasks used by the selected learning path.
    assert (target / 'lesson-data.js').read_bytes() == original['lesson-data.js']
    assert (target / 'progress-meta.js').read_bytes() == original['progress-meta.js']
    for node in ET.parse(target / 'imsmanifest.xml').getroot().iter():
        if node.tag.split('}')[-1] in {'file', 'resource'} and node.get('href'):
            assert (target / node.get('href')).is_file(), node.get('href')
    return {'lesson': data['id'], 'title': data['title'], 'sourceSha256': sha(raw),
            'sourceDataSha256': sha(original['lesson-data.js']),
            'sourceProgressSha256': sha(original['progress-meta.js']),
            'contentPagesUnchanged': len(data['pages']), 'protectedFiles': protected,
            'designFiles': {name: sha((target / name).read_bytes()) for name in copied},
            'template': template.relative_to(ROOT).as_posix()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--version', required=True, help='Anzeigenummer, z. B. 1.1; ändert keine Lernstandskennung')
    args = parser.parse_args()
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)', args.version):
        parser.error('Version muss zwei Zahlen enthalten')
    # Exported deliveries stay separate from the authoritative source masters.
    if args.output.resolve().is_relative_to(ROOT):
        parser.error('Ausgabe außerhalb des Repositorys wählen; vorhandene Master bleiben erhalten')
    if args.output.exists():
        parser.error('Ausgabeordner muss neu sein')
    data = read_archive(args.source.read_bytes())
    packages = {args.source.name: args.source.read_bytes()} if 'imsmanifest.xml' in data else {
        name: raw for name, raw in data.items() if name.endswith('.zip')}
    if not packages:
        parser.error('Kein SCORM-Paket gefunden')
    catalog = json.loads((ROOT / 'master-katalog.json').read_text())
    args.output.mkdir(parents=True)
    reports, combined = [], {}
    for name, raw in packages.items():
        match = re.search(r'LG01[_-]LS(\d{2})', name)
        if not match:
            raise ValueError(f'Keine eindeutige Lernsituation: {name}')
        number = match[1]
        entry = next(p for p in catalog['packages'] if p['id'] == f'BRC-LG01-LS{number}')
        template = ROOT / entry['master']
        target = args.output / 'preview' / f'LS{number}'
        report = transfer(raw, target, template)
        filename = f'BRC_LG01_LS{number}_v{args.version}_SCORM12.zip'
        files = {p.relative_to(target).as_posix(): p.read_bytes() for p in target.rglob('*') if p.is_file()}
        archive(args.output / filename, files)
        combined[filename] = (args.output / filename).read_bytes()
        report.update(archive=filename, archiveSha256=sha(combined[filename]))
        reports.append(report)
        print(f'{report["lesson"]}: Originalinhalte und Fortschritt unverändert; GitHub-Oberfläche übernommen', flush=True)
    archive(args.output / f'BioCasa_LG01_Moodle_Lernpakete_v{args.version}.zip', combined)
    report = {'designCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'packageVersion': args.version, 'packages': reports}
    (args.output / 'Designtransfer_Pruefung.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
