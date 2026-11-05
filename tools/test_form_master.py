#!/usr/bin/env python3
"""Exercise shared design propagation using small independent SCORM fixtures."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

import form_master
import master


class FormMasterTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='form-master-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'Formmaster'
        (self.source / 'assets').mkdir(parents=True)
        (self.source / 'assets/styles.css').write_text(
            'body { color: #173a63; }\n', encoding='utf-8')
        self.manifest = {
            'schemaVersion': 1,
            'version': '1.8.8',
            'reference': {'package': 'GESCHICHTE-IDN', 'version': '1.8.8'},
            'files': [{'source': 'assets/styles.css', 'target': 'assets/styles.css'}],
        }
        self.save_manifest()
        self.items = [self.make_package('BRC-LS01'), self.make_package('GESCHICHTE-LS02')]
        self.save_catalog()

    def make_package(self, package_id, kind='Lernsituation', version='1.8.5'):
        item = {
            'id': package_id, 'title': 'Lernsituation mit stabilen Kennungen',
            'bereich': 'Test', 'typ': kind,
            'master': f'Fachbereiche/Test/{package_id}',
            'version': version, 'archiveStem': package_id,
        }
        folder = self.root / item['master']
        (folder / 'assets').mkdir(parents=True)
        files = {
            'index.html': '<!doctype html><html lang="de"><head>'
                '<link rel="stylesheet" href="assets/styles.css"></head><body>'
                '<article data-task-id="existing-task-7">Prüfen Sie die Quelle.</article>'
                '<script src="mode-config.js"></script></body></html>\n',
            'assets/styles.css': 'body { color: #000; }\n',
            'assets/runtime.js': 'const storageKey = "existing-progress";\n',
            'lesson-data.js': 'window.SOZPAED={id:"existing-lesson",tasks:["existing-task-7"]};\n',
            'progress-meta.js': 'window.SOZ_PROGRESS_META={signature:"already-in-moodle"};\n',
            'mode-config.js': 'window.SOZ_CONFIG=' + json.dumps({
                'mode': 1, 'overrides': {'original': 'keep me'},
                'packageRevision': 'stable-storage-revision',
                'packageVersion': version, 'formVersion': '1.8.5',
            }) + ';\n',
        }
        for name, content in files.items():
            (folder / name).write_text(content, encoding='utf-8')
        (folder / 'imsmanifest.xml').write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<manifest xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" '
            'identifier="stable-manifest-id"><organizations>'
            '<organization identifier="stable-organization-id"><title>Fixture</title>'
            '</organization></organizations><resources>'
            '<resource identifier="stable-sco-id" href="index.html">'
            + ''.join(f'<file href="{name}"/>' for name in files)
            + '</resource></resources></manifest>\n', encoding='utf-8')
        return item

    def save_catalog(self):
        (self.root / master.CATALOG).write_text(json.dumps({
            'schemaVersion': 1, 'packages': self.items,
        }), encoding='utf-8')

    def save_manifest(self):
        (self.source / 'manifest.json').write_text(
            json.dumps(self.manifest), encoding='utf-8')

    def sync(self):
        with redirect_stdout(io.StringIO()):
            return form_master.sync(self.root)

    def check(self):
        with redirect_stdout(io.StringIO()):
            form_master.check(self.root)

    def export(self):
        with redirect_stdout(io.StringIO()):
            master.export(self.root)

    def packages(self):
        return {item['id']: item for item in master.catalog(self.root)['packages']}

    def path(self, item, relative):
        return self.root / item['master'] / relative

    def snapshot(self):
        return {
            p.relative_to(self.root).as_posix(): p.read_bytes()
            for p in self.root.rglob('*') if p.is_file()
        }

    def test_one_design_change_reaches_every_catalogued_lesson_and_both_templates(self):
        self.items.extend([
            self.make_package('VORLAGE-TRADIERT', kind='Vorlage'),
            self.make_package('VORLAGE-FUENF-LERNWEGE', kind='Vorlage'),
        ])
        self.save_catalog()
        self.sync()
        self.check()
        expected = (self.source / 'assets/styles.css').read_bytes()
        for item in self.items:
            self.assertEqual(self.path(item, 'assets/styles.css').read_bytes(), expected)
            self.assertEqual(self.packages()[item['id']]['formVersion'], '1.8.8')
            self.assertEqual(self.packages()[item['id']]['version'], '1.8.8')

    def test_lesson_content_and_existing_progress_identifiers_are_preserved(self):
        preserved = ['lesson-data.js', 'progress-meta.js', 'assets/runtime.js', 'index.html']
        for p in self.items:
            page = self.path(p, 'index.html')
            page.write_bytes(page.read_bytes().replace(b'\n', b'\r\n'))
        before = {(p['id'], name): self.path(p, name).read_bytes()
                  for p in self.items for name in preserved}
        self.sync()
        for p in self.items:
            for name in preserved:
                actual = self.path(p, name).read_bytes()
                if name == 'index.html':
                    # Only the managed stylesheet's generated cache key may differ.
                    # Keep all lesson markup, IDs, other URLs and line endings exact.
                    actual = re.sub(
                        rb'''((?:href|src)=["']assets/styles\.css)\?v=form-[0-9a-f]{16}(["'])''',
                        rb'\1\2', actual)
                self.assertEqual(actual, before[p['id'], name])
            config = self.path(p, 'mode-config.js').read_text(encoding='utf-8')
            self.assertIn('stable-storage-revision', config)
            self.assertIn('keep me', config)
            manifest = self.path(p, 'imsmanifest.xml').read_text(encoding='utf-8')
            for stable_id in ('stable-manifest-id', 'stable-organization-id', 'stable-sco-id'):
                self.assertIn(stable_id, manifest)

    def test_cache_keys_change_with_shared_source_but_leave_other_resources_untouched(self):
        (self.source / 'assets/ui.js').write_bytes(b'window.sharedUi = true;\n')
        self.manifest['files'].append({'source': 'assets/ui.js', 'target': 'assets/ui.js'})
        self.save_manifest()
        for item in self.items:
            page = self.path(item, 'index.html')
            page.write_bytes(page.read_bytes().replace(b'</body>',
                b'<script src="assets/runtime.js?v=stable"></script>'
                b"<script src='assets/ui.js?v=older'></script>"
                b'<a href="https://example.org/assets/styles.css?v=external">Quelle</a>'
                b'</body>'))
        self.sync()
        first_tokens = {}
        for item in self.items:
            page = self.path(item, 'index.html').read_bytes()
            token = re.search(rb'href="assets/styles\.css\?v=(form-[0-9a-f]{16})"', page)
            self.assertIsNotNone(token)
            first_tokens[item['id']] = token[1]
            self.assertIn(b"src='assets/ui.js?v=" + token[1] + b"'", page)
            self.assertIn(b'src="assets/runtime.js?v=stable"', page)
            self.assertIn(b'href="https://example.org/assets/styles.css?v=external"', page)
        (self.source / 'assets/styles.css').write_bytes(b'body { color: #009; }\n')
        self.sync()
        self.check()
        for item in self.items:
            page = self.path(item, 'index.html').read_bytes()
            token = re.search(rb'href="assets/styles\.css\?v=(form-[0-9a-f]{16})"', page)
            self.assertIsNotNone(token)
            self.assertNotEqual(token[1], first_tokens[item['id']])
            self.assertIn(b"src='assets/ui.js?v=" + token[1] + b"'", page)
            self.assertIn(b'src="assets/runtime.js?v=stable"', page)
            self.assertIn(b'href="https://example.org/assets/styles.css?v=external"', page)
        before = self.snapshot()
        self.sync()
        self.assertEqual(self.snapshot(), before)

    def test_lernpfad_and_biocasa_remain_untouched(self):
        excluded = [self.make_package('VORLAGE-LERNPFAD', kind='Lernpfadübung'),
                    self.make_package('BRC-BIOCASA-OS', kind='Lernunternehmen')]
        self.items.extend(excluded)
        self.save_catalog()
        before = {p['id']: {f.relative_to(self.root / p['master']): f.read_bytes()
                           for f in (self.root / p['master']).rglob('*') if f.is_file()}
                  for p in excluded}
        self.sync()
        for p in excluded:
            self.assertEqual(self.packages()[p['id']], p)
            after = {f.relative_to(self.root / p['master']): f.read_bytes()
                     for f in (self.root / p['master']).rglob('*') if f.is_file()}
            self.assertEqual(after, before[p['id']])

    def test_newly_registered_lesson_receives_design_without_a_second_target_list(self):
        self.sync()
        self.items = list(self.packages().values())
        added = self.make_package('RENO-NEW-LS')
        self.items.append(added)
        self.save_catalog()
        self.sync()
        self.check()
        self.assertEqual(self.path(added, 'assets/styles.css').read_bytes(),
                         (self.source / 'assets/styles.css').read_bytes())
        self.assertEqual(self.packages()[added['id']]['formVersion'], '1.8.8')

    def test_check_rejects_local_drift_and_new_source_until_resynchronized(self):
        self.sync()
        self.path(self.items[0], 'assets/styles.css').write_text('body { color: red; }')
        with self.assertRaises(ValueError):
            self.check()
        self.sync()
        self.check()
        (self.source / 'assets/styles.css').write_text('body { color: blue; }')
        with self.assertRaises(ValueError):
            self.check()
        self.sync()
        self.check()

    def test_repeated_sync_changes_neither_versions_nor_file_bytes(self):
        self.sync()
        before = self.snapshot()
        self.sync()
        self.check()
        self.assertEqual(self.snapshot(), before)

    def test_changed_exported_design_gets_one_package_patch_increment(self):
        self.sync()
        self.export()
        (self.source / 'assets/styles.css').write_text('body { color: #456; }\n')
        self.sync()
        for p in self.packages().values():
            self.assertEqual(p['version'], '1.8.9')
            self.assertEqual(p['formVersion'], '1.8.8')
        before = self.snapshot()
        self.sync()
        self.assertEqual(self.snapshot(), before)
        self.export()
        with redirect_stdout(io.StringIO()):
            master.check(self.root, archives=True)
        for p in self.packages().values():
            with zipfile.ZipFile(self.root / master.archive_path(p)) as archive:
                self.assertEqual(archive.read('assets/styles.css'),
                                 (self.source / 'assets/styles.css').read_bytes())
                self.assertIn(b'already-in-moodle', archive.read('progress-meta.js'))

    def test_normal_export_applies_latest_shared_source_and_records_design_provenance(self):
        self.export()
        (self.source / 'assets/styles.css').write_text('body { color: #036; }\n')
        self.export()
        entries = {entry['id']: entry for entry in master.read_index(self.root)['packages']}
        for item in self.packages().values():
            self.assertEqual(item['version'], '1.8.9')
            self.assertEqual(entries[item['id']]['formVersion'], '1.8.8')
            self.assertEqual(entries[item['id']]['formSourceSha256'], item['formSourceSha256'])
            with zipfile.ZipFile(self.root / master.archive_path(item)) as archive:
                self.assertEqual(archive.read('assets/styles.css'),
                                 (self.source / 'assets/styles.css').read_bytes())
        with redirect_stdout(io.StringIO()):
            master.check(self.root, archives=True)

    def test_package_version_newer_than_design_is_never_downgraded(self):
        self.items[0]['version'] = '2.1.4'
        config = self.path(self.items[0], 'mode-config.js')
        config.write_text(config.read_text().replace('1.8.5', '2.1.4'))
        self.save_catalog()
        self.export()
        (self.source / 'assets/styles.css').write_text('body { color: #789; }\n')
        self.sync()
        self.assertEqual(self.packages()[self.items[0]['id']]['version'], '2.1.5')
        self.assertEqual(self.packages()[self.items[0]['id']]['formVersion'], '1.8.8')

    def test_optional_asset_only_updates_existing_consumers(self):
        (self.source / 'assets/preview.css').write_text('.preview { max-width: 340px; }\n')
        self.manifest['files'].append({
            'source': 'assets/preview.css', 'target': 'assets/preview.css', 'existingOnly': True,
        })
        self.save_manifest()
        existing = self.path(self.items[0], 'assets/preview.css')
        existing.write_text('.preview { max-width: 500px; }\n')
        self.sync()
        self.check()
        self.assertEqual(existing.read_bytes(), (self.source / 'assets/preview.css').read_bytes())
        self.assertFalse(self.path(self.items[1], 'assets/preview.css').exists())

    def test_missing_source_is_rejected_before_any_target_or_catalog_changes(self):
        self.manifest['files'].append({'source': 'assets/missing.css', 'target': 'assets/missing.css'})
        self.save_manifest()
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.sync()
        self.assertEqual(self.snapshot(), before)

    def test_source_and_target_path_escape_are_rejected_without_partial_sync(self):
        for field in ('source', 'target'):
            for unsafe in ('../outside.css', '/tmp/outside.css', 'assets/../../outside.css'):
                with self.subTest(field=field, path=unsafe):
                    self.manifest['files'] = [
                        {'source': 'assets/styles.css', 'target': 'assets/styles.css'},
                        {'source': 'assets/styles.css', 'target': 'assets/second.css', field: unsafe},
                    ]
                    self.save_manifest()
                    before = self.snapshot()
                    with self.assertRaises(ValueError):
                        self.sync()
                    self.assertEqual(self.snapshot(), before)

    def add_regions(self, marker='/* Metallic point UI from supplied reference. */',
                    skip_missing=False):
        (self.source / 'assets/points-ui.js').write_bytes(
            b'window.SOZ_POINTS_UI = {render: function () { return "shared"; }};\n')
        self.manifest['regions'] = [{
            'source': 'assets/points-ui.js',
            'targets': ['assets/progress-core.js', 'assets/revision185-core.js'],
            'marker': marker, 'skipMissingMarker': skip_missing,
        }]
        self.save_manifest()
        return marker.encode()

    def test_shared_ui_region_propagates_without_changing_storage_prefix_bytes(self):
        marker = self.add_regions()
        prefixes = {}
        for number, item in enumerate(self.items):
            # CRLF and non-ASCII make an accidental text-normalizing rewrite visible.
            prefix = ('const lesson = "Lernsituation ä ' + str(number) + '";\r\n'
                      'const signature = "persisted-signature";\r\n').encode('utf-8')
            prefixes[item['id']] = prefix
            self.path(item, 'assets/progress-core.js').write_bytes(
                prefix + marker + b'\r\nwindow.SOZ_POINTS_UI = {old: true};\r\n')
        self.sync()
        self.check()
        source = (self.source / 'assets/points-ui.js').read_bytes()
        for item in self.items:
            actual = self.path(item, 'assets/progress-core.js').read_bytes()
            self.assertEqual(actual, prefixes[item['id']] + marker + b'\n' + source)
        before = self.snapshot()
        self.sync()
        self.assertEqual(self.snapshot(), before)

    def test_region_can_skip_one_unmarked_file_when_another_file_matches(self):
        marker = self.add_regions(skip_missing=True)
        unchanged = b'const stableStorageSignature = "no-ui-in-this-core";\n'
        for item in self.items:
            self.path(item, 'assets/progress-core.js').write_bytes(unchanged)
            self.path(item, 'assets/revision185-core.js').write_bytes(
                b'const extension = "keep";\n' + marker + b'\nold-ui();\n')
        self.sync()
        self.check()
        for item in self.items:
            self.assertEqual(self.path(item, 'assets/progress-core.js').read_bytes(), unchanged)
            self.assertIn(b'window.SOZ_POINTS_UI',
                          self.path(item, 'assets/revision185-core.js').read_bytes())

    def test_missing_or_ambiguous_region_stops_every_write(self):
        marker = self.add_regions(skip_missing=True)
        self.path(self.items[0], 'assets/progress-core.js').write_bytes(
            b'const signature = "keep";\n' + marker + b'\nold-ui();\n')
        for invalid in (b'const noMarker = true;\n', marker + b'\n' + marker):
            with self.subTest(invalid=invalid):
                self.path(self.items[1], 'assets/progress-core.js').write_bytes(invalid)
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.sync()
                self.assertEqual(self.snapshot(), before)

    def test_missing_region_marker_requires_explicit_skip(self):
        self.add_regions(skip_missing=False)
        for item in self.items:
            self.path(item, 'assets/progress-core.js').write_bytes(b'const noMarker = true;\n')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.sync()
        self.assertEqual(self.snapshot(), before)

    def test_unapproved_regions_or_complete_core_replacement_are_rejected(self):
        self.add_regions()
        cases = [
            ('marker', 'const storageSignature ='),
            ('targets', ['assets/scorm-codec.js']),
        ]
        valid = dict(self.manifest['regions'][0])
        for field, invalid in cases:
            with self.subTest(field=field):
                self.manifest['regions'] = [{**valid, field: invalid}]
                self.save_manifest()
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.sync()
                self.assertEqual(self.snapshot(), before)
        self.manifest.pop('regions')
        for protected in ('progress-core.js', 'revision185-core.js', 'runtime.js',
                          'scorm-codec.js', 'teacher.js', 'export.js'):
            with self.subTest(protected=protected):
                self.manifest['files'] = [{
                    'source': 'assets/points-ui.js', 'target': 'assets/' + protected,
                }]
                self.save_manifest()
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.sync()
                self.assertEqual(self.snapshot(), before)

    def add_focus_component(self, expression="'https://example.test/coaching'"):
        self.manifest['components'] = [{'component': 'task-focus',
            'source': 'assets/task-focus.js', 'target': 'assets/runtime.js'}]
        (self.source / 'assets/task-focus.js').write_text(
            '((options)=>{window.focus=options;})(/* LS_TASK_FOCUS_OPTIONS */{});\n')
        self.save_manifest()
        legacy = (form_master.FOCUS_START + '\n(()=>{\n'
            'iframe.src=' + expression + ';const info=1;\n})();\n\n'
            '(()=>{window.materials="original";})();\n')
        for item in self.items:
            self.path(item, 'assets/runtime.js').write_text('/* Original storage */\n' + legacy)

    def test_shared_focus_reaches_brc_history_reno_and_bfs_without_replacing_storage(self):
        self.items.extend([self.make_package('RENO-LS01'), self.make_package('BFSDUAL-LS01')])
        for item, area in zip(self.items, ['BRC', 'Geschichte', 'ReNo', 'BFS dual']):
            item['bereich'] = area
        self.save_catalog()
        self.add_focus_component()
        original = {p['id']: self.path(p, 'assets/runtime.js').read_text() for p in self.items}
        self.sync();self.check()
        for item in self.items:
            current = self.path(item, 'assets/runtime.js').read_text()
            self.assertTrue(current.startswith('/* Original storage */\n'))
            self.assertTrue(current.endswith('(()=>{window.materials="original";})();\n'))
            self.assertIn('https://example.test/coaching', current)
            self.assertIn(form_master.FOCUS_END, current)
        before = self.snapshot();self.sync();self.assertEqual(before, self.snapshot())

    def test_phased_ai_routes_are_preserved_as_local_data(self):
        self.add_focus_component("['planen.html','durchfuehren.html'].includes(document.body.dataset.page)?'https://example.test/planning':'https://example.test/default'")
        self.sync();self.check()
        value = self.path(self.items[0], 'assets/runtime.js').read_text()
        self.assertIn('"aiHelpUrl":"https://example.test/default"', value)
        self.assertIn('"planen.html":"https://example.test/planning"', value)
        self.assertIn('"durchfuehren.html":"https://example.test/planning"', value)

    def test_focus_sync_preserves_existing_line_endings_outside_the_component(self):
        self.add_focus_component()
        path=self.path(self.items[0], 'assets/runtime.js')
        path.write_bytes(path.read_bytes().replace(b'\n',b'\r\n'))
        self.sync()
        value=path.read_bytes()
        self.assertTrue(value.startswith(b'/* Original storage */\r\n'))
        self.assertTrue(value.endswith(b'(()=>{window.materials="original";})();\r\n'))
        self.check()

    def test_missing_focus_boundary_or_unknown_ai_route_stops_all_writes(self):
        for expression in ["window.unknownAI()", "'https://example.test/coaching'"]:
            with self.subTest(expression=expression):
                self.add_focus_component(expression)
                if expression.startswith("'"):
                    self.path(self.items[-1], 'assets/runtime.js').write_text('existing runtime without focus')
                before=self.snapshot()
                with self.assertRaises(ValueError):self.sync()
                self.assertEqual(before,self.snapshot())

    def test_component_cannot_replace_arbitrary_runtime_files(self):
        self.add_focus_component()
        self.manifest['components'][0]['target']='assets/scorm.js'
        self.save_manifest();before=self.snapshot()
        with self.assertRaises(ValueError):self.sync()
        self.assertEqual(before,self.snapshot())

    def test_uncatalogued_lesson_cannot_be_skipped_by_sync(self):
        self.make_package('RENO-UNREGISTERED')
        before=self.snapshot()
        with self.assertRaisesRegex(ValueError,'Nicht registrierte Lernsituation'):self.sync()
        self.assertEqual(before,self.snapshot())

    def test_source_symlink_is_rejected_before_any_generated_changes(self):
        alias = self.source / 'assets/alias.css'
        alias.symlink_to('styles.css')
        self.manifest['files'][0]['source'] = 'assets/alias.css'
        self.save_manifest()
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.sync()
        self.assertEqual(self.snapshot(), before)

    def test_target_symlink_is_rejected_before_other_packages_change(self):
        target = self.path(self.items[1], 'assets/styles.css')
        target.unlink()
        target.symlink_to('runtime.js')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.sync()
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
