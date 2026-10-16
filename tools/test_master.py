#!/usr/bin/env python3
"""Regression tests for current SCORM exports; fixtures never touch real packages."""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import master


class CurrentExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='scorm-master-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.items = [self.make_package('brc-lg01-ls01')]
        self.save_catalog()

    def make_package(self, package_id, version='1.0'):
        item = {
            'id': package_id,
            'title': 'Lernsituation mit unveränderten Kennungen',
            'bereich': 'BRC',
            'typ': 'Lernsituation',
            'master': f'Fachbereiche/BRC/LG01/{package_id}',
            'version': version,
            'archiveStem': package_id,
        }
        folder = self.root / item['master']
        (folder / 'assets').mkdir(parents=True)
        (folder / 'imsmanifest.xml').write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<manifest xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" '
            'identifier="stable-manifest-id">'
            '<resources><resource identifier="stable-sco-id" href="index.html">'
            '<file href="index.html"/><file href="assets/runtime.js"/>'
            '</resource></resources></manifest>\n', encoding='utf-8')
        (folder / 'index.html').write_text(
            '<!doctype html><html lang="de"><body>'
            '<article data-task-id="old-task-0007">Prüfen Sie die Quelle.</article>'
            '<script src="assets/runtime.js"></script></body></html>\n', encoding='utf-8')
        (folder / 'assets/runtime.js').write_text(
            'const storageKey = "existing-progress";\n'
            'const contentSignature = "already-in-moodle";\n', encoding='utf-8')
        return item

    def save_catalog(self):
        (self.root / master.CATALOG).write_text(
            json.dumps({'schemaVersion': 1, 'packages': self.items}), encoding='utf-8')

    def export(self, selected=None):
        with redirect_stdout(io.StringIO()):
            master.export(self.root, selected)

    def check(self):
        with redirect_stdout(io.StringIO()):
            master.check(self.root, archives=True)

    def archive(self, item=None):
        return self.root / master.archive_path(item or self.items[0])

    def download_snapshot(self):
        return {
            path.relative_to(self.root / 'Downloads').as_posix(): path.read_bytes()
            for path in (self.root / 'Downloads').rglob('*') if path.is_file()
        }

    def test_export_preserves_manifest_task_ids_and_file_bytes(self):
        expected = {
            name: path.read_bytes()
            for name, path in master.files_for(self.root, self.items[0]).items()
        }
        self.export()
        self.check()
        with zipfile.ZipFile(self.archive()) as archive:
            actual = {name: archive.read(name) for name in archive.namelist()}
        self.assertEqual(actual, expected)
        self.assertIn('imsmanifest.xml', actual)
        self.assertIn(b'stable-manifest-id', actual['imsmanifest.xml'])
        self.assertIn(b'old-task-0007', actual['index.html'])
        self.assertIn(b'already-in-moodle', actual['assets/runtime.js'])

    def test_modified_master_is_rejected_until_version_is_raised(self):
        self.export()
        original_downloads = self.download_snapshot()
        page = self.root / self.items[0]['master'] / 'index.html'
        page.write_text(page.read_text(encoding='utf-8') + '<!-- revised -->', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'aktuellen Master'):
            self.check()
        with self.assertRaisesRegex(ValueError, 'Versionsnummer erhöhen'):
            self.export()
        self.assertEqual(self.download_snapshot(), original_downloads)
        self.items[0]['version'] = '1.1'
        self.save_catalog()
        self.export()
        self.check()
        with zipfile.ZipFile(self.archive()) as archive:
            self.assertEqual(archive.read('index.html'), page.read_bytes())

    def test_stale_zip_is_rejected_and_rebuilt_from_current_master(self):
        self.export()
        with zipfile.ZipFile(self.archive()) as archive:
            content = {name: archive.read(name) for name in archive.namelist()}
        content['index.html'] = b'<html>stale exported page</html>'
        with zipfile.ZipFile(self.archive(), 'w') as archive:
            for name, data in content.items():
                archive.writestr(name, data)
        with self.assertRaisesRegex(ValueError, 'ZIP-Inhalt/Prüfsumme'):
            self.check()
        self.export()
        self.check()
        with zipfile.ZipFile(self.archive()) as archive:
            self.assertNotEqual(archive.read('index.html'), content['index.html'])

    def test_invalid_manifest_dependency_leaves_all_previous_exports_untouched(self):
        self.items.append(self.make_package('brc-lg01-ls02'))
        self.save_catalog()
        self.export()
        original_downloads = self.download_snapshot()
        for item in self.items:
            item['version'] = '1.1'
        self.save_catalog()
        first_page = self.root / self.items[0]['master'] / 'index.html'
        first_page.write_text('<html>Ready to update</html>', encoding='utf-8')
        missing = self.root / self.items[1]['master'] / 'assets/runtime.js'
        missing.unlink()
        with self.assertRaisesRegex(ValueError, 'Manifest-Datei fehlt'):
            self.export()
        self.assertEqual(self.download_snapshot(), original_downloads)
        self.assertFalse(self.archive(self.items[0]).exists())

    def test_missing_root_manifest_preserves_previous_downloads(self):
        self.export()
        original_downloads = self.download_snapshot()
        (self.root / self.items[0]['master'] / 'imsmanifest.xml').unlink()
        self.items[0]['version'] = '1.1'
        self.save_catalog()
        with self.assertRaisesRegex(ValueError, 'imsmanifest.xml fehlt'):
            self.export()
        self.assertEqual(self.download_snapshot(), original_downloads)

    def test_invalid_unselected_master_prevents_all_export_changes(self):
        self.items.append(self.make_package('brc-lg01-ls02'))
        self.save_catalog()
        self.export()
        original_downloads = self.download_snapshot()
        self.items[0]['version'] = '1.1'
        self.save_catalog()
        first_page = self.root / self.items[0]['master'] / 'index.html'
        first_page.write_text('<html>Updated selected master</html>', encoding='utf-8')
        (self.root / self.items[1]['master'] / 'assets/runtime.js').unlink()
        with self.assertRaisesRegex(ValueError, 'Manifest-Datei fehlt'):
            self.export([self.items[0]['id']])
        self.assertEqual(self.download_snapshot(), original_downloads)
        self.assertFalse(self.archive(self.items[0]).exists())

    def test_numeric_version_order_and_cleanup_keep_exactly_one_current_zip(self):
        self.items[0]['version'] = '1.9'
        self.save_catalog()
        self.export()
        previous_archive = self.archive()
        obsolete = previous_archive.with_name('old-local-copy.zip')
        obsolete.write_bytes(previous_archive.read_bytes())
        self.items[0]['version'] = '1.10'
        self.save_catalog()
        self.export()
        self.check()
        self.assertGreater(master.version('1.10'), master.version('1.9'))
        self.assertFalse(previous_archive.exists())
        self.assertFalse(obsolete.exists())
        self.assertEqual(list(self.archive().parent.glob('*.zip')), [self.archive()])
        self.assertIn('_v1.10_SCORM12.zip', self.archive().name)
        self.items[0]['version'] = '1.9'
        self.save_catalog()
        original_downloads = self.download_snapshot()
        with self.assertRaisesRegex(ValueError, 'nicht zurückgesetzt'):
            self.export()
        self.assertEqual(self.download_snapshot(), original_downloads)

    def test_deleted_file_is_absent_from_next_export(self):
        obsolete = self.root / self.items[0]['master'] / 'old-material.html'
        obsolete.write_text('<html>Retired material</html>', encoding='utf-8')
        self.export()
        with zipfile.ZipFile(self.archive()) as archive:
            self.assertIn('old-material.html', archive.namelist())
        obsolete.unlink()
        self.items[0]['version'] = '1.1'
        self.save_catalog()
        self.export()
        self.check()
        with zipfile.ZipFile(self.archive()) as archive:
            self.assertNotIn('old-material.html', archive.namelist())

    def test_unchanged_export_is_byte_identical(self):
        self.export()
        original_downloads = self.download_snapshot()
        self.export()
        self.assertEqual(self.download_snapshot(), original_downloads)

    def test_catalog_rejects_duplicate_id_master_or_archive_stem(self):
        second = self.make_package('brc-lg01-ls02')
        for field in ('id', 'master', 'archiveStem'):
            with self.subTest(field=field):
                duplicate = copy.deepcopy(second)
                duplicate[field] = self.items[0][field]
                self.items = [self.items[0], duplicate]
                self.save_catalog()
                with self.assertRaisesRegex(ValueError, 'Doppelter Master'):
                    master.catalog(self.root)

    def test_catalog_rejects_master_path_escape(self):
        for unsafe in ('../outside', '/tmp/outside', 'Fachbereiche/../../outside'):
            with self.subTest(path=unsafe):
                self.items[0]['master'] = unsafe
                self.save_catalog()
                with self.assertRaisesRegex(ValueError, 'Unsicherer Pfad'):
                    master.catalog(self.root)

    def test_manifest_rejects_encoded_path_escape(self):
        manifest = self.root / self.items[0]['master'] / 'imsmanifest.xml'
        text = manifest.read_text(encoding='utf-8')
        manifest.write_text(text.replace('href="index.html"', 'href="%2e%2e/outside.html"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unsicherer Pfad'):
            self.export()
        self.assertFalse((self.root / 'Downloads').exists())

    def test_selected_export_preserves_other_package_and_its_version(self):
        self.items.append(self.make_package('brc-lg01-ls02'))
        self.save_catalog()
        self.export()
        other = self.archive(self.items[1])
        other_bytes = other.read_bytes()
        self.items[0]['version'] = '2.1'
        self.save_catalog()
        self.export([self.items[0]['id']])
        self.check()
        self.assertEqual(other.read_bytes(), other_bytes)
        index = master.read_index(self.root)
        self.assertEqual([entry['version'] for entry in index['packages']], ['2.1', '1.0'])

    def test_download_listing_does_not_claim_an_unexported_version(self):
        second = self.make_package('brc-lg01-ls02')
        second['title'] = 'Noch nicht neu exportiert'
        self.items.append(second)
        self.save_catalog()
        self.export()
        second['version'] = '1.1'
        self.save_catalog()
        self.export([self.items[0]['id']])
        listing = (self.root / 'Downloads/README.md').read_text(encoding='utf-8')
        self.assertIn('| Noch nicht neu exportiert | 1.1 | Export ausstehend |', listing)
        self.assertNotIn(f'[ZIP]({master.archive_path(second)[10:]}', listing)
        self.assertNotIn('brc-lg01-ls02_v1.0_SCORM12.zip', listing)
        with self.assertRaisesRegex(ValueError, 'veraltet'):
            self.check()

    def test_download_listing_hides_unselected_changed_source_at_same_version(self):
        second = self.make_package('brc-lg01-ls02')
        second['title'] = 'Geänderte Quelle'
        self.items.append(second)
        self.save_catalog()
        self.export()
        page = self.root / second['master'] / 'index.html'
        page.write_text('<html>Source newer than exported ZIP</html>', encoding='utf-8')
        self.export([self.items[0]['id']])
        listing = (self.root / 'Downloads/README.md').read_text(encoding='utf-8')
        self.assertIn('| Geänderte Quelle | 1.0 | Export ausstehend |', listing)
        self.assertNotIn('brc-lg01-ls02_v1.0_SCORM12.zip', listing)
        with self.assertRaisesRegex(ValueError, 'aktuellen Master'):
            self.check()

    def test_manifest_only_export_excludes_teacher_pages_without_changing_regular_masters(self):
        for name in ('preview.html', 'teacher.html', 'teacher.js', 'package-writer.js'):
            (self.root / self.items[0]['master'] / name).write_text('teacher-only', encoding='utf-8')
        regular = self.make_package('regular')
        (self.root / regular['master'] / 'extra.html').write_text('retain me', encoding='utf-8')
        self.items[0]['manifestOnly'] = True
        self.items.append(regular)
        self.save_catalog()
        self.export()
        self.check()
        with zipfile.ZipFile(self.archive()) as archive:
            self.assertEqual(set(archive.namelist()), {'imsmanifest.xml', 'index.html', 'assets/runtime.js'})
        with zipfile.ZipFile(self.archive(regular)) as archive:
            self.assertIn('extra.html', archive.namelist())

    def test_manifest_only_rejects_missing_runtime_dependency(self):
        self.items[0]['manifestOnly'] = True
        self.save_catalog()
        (self.root / self.items[0]['master'] / 'assets/runtime.js').unlink()
        with self.assertRaisesRegex(ValueError, 'Manifest-Datei fehlt'):
            self.export()
        self.assertFalse((self.root / 'Downloads').exists())

    def test_teacher_only_edit_does_not_change_student_archive(self):
        self.items[0]['manifestOnly'] = True
        self.save_catalog()
        teacher = self.root / self.items[0]['master'] / 'teacher.html'
        teacher.write_text('before', encoding='utf-8')
        self.export()
        before = self.download_snapshot()
        teacher.write_text('after', encoding='utf-8')
        self.export()
        self.check()
        self.assertEqual(self.download_snapshot(), before)

    def test_manifest_only_requires_boolean_catalog_flag(self):
        self.items[0]['manifestOnly'] = 'true'
        self.save_catalog()
        with self.assertRaisesRegex(ValueError, 'manifestOnly'):
            master.catalog(self.root)

    def test_versions_require_two_numeric_parts(self):
        for value in ('1.2.3', '1', 'v1.2', '01.2', '1.02', '-1.2', '1.2-final', 1.2):
            with self.subTest(version=value):
                with self.assertRaises(ValueError):
                    master.version(value)


if __name__ == '__main__':
    unittest.main()

