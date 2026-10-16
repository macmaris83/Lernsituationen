"""Release checks use disposable project copies; never modify the real master."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import re
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import project


class ProjectReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='biocasa-release-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / 'Fachbereiche/BRC/BioCasaOS'
        shutil.copytree(project.PROJECT / 'dist', self.project / 'dist')
        for name in ('README.md', 'package.json'):
            shutil.copy2(project.PROJECT / name, self.project / name)
        data, item = project.project_item()
        self.item = dict(item)
        self.data = dict(data, packages=[self.item])
        self.catalog = self.root / project.master.CATALOG
        self.catalog.write_text(json.dumps(self.data), encoding='utf-8')
        self.scope = patch.multiple(project, ROOT=self.root, PROJECT=self.project)
        self.scope.start()
        self.addCleanup(self.scope.stop)

    def quiet(self, function, *args):
        with redirect_stdout(io.StringIO()):
            return function(*args)

    def test_version_updates_display_and_catalog_without_changing_financial_or_storage_code(self):
        preserved = {p: p.read_bytes() for p in (self.project / 'dist').rglob('*') if p.is_file() and p.name not in ('index.html', 'preview.html', 'KURZSTART.txt')}
        old = self.item['version']
        guide = self.project / 'dist/KURZSTART.txt'
        guide.write_text(guide.read_text() + '\nTestdatum 30.10.2026; Referenzversion 0.10.0.\n', encoding='utf-8')
        dates = re.findall(r'\b\d{2}\.\d{2}(?:\.\d{4})?', guide.read_text())
        major, minor = map(int, old.split('.'))
        new = f'{major}.{minor + 1}'
        self.quiet(project.set_version, new)
        self.quiet(project.check)
        self.assertEqual(json.loads(self.catalog.read_text())['packages'][0]['version'], new)
        self.assertEqual(json.loads((self.project / 'package.json').read_text())['version'], new + '.0')
        self.assertEqual(re.findall(r'\b\d{2}\.\d{2}(?:\.\d{4})?', guide.read_text()), dates)
        self.assertIn('Referenzversion 0.10.0', guide.read_text())
        for path, content in preserved.items():
            self.assertEqual(path.read_bytes(), content, path.name)

    def test_same_version_rejected_without_writing_project_files(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(ValueError, 'größer'):
            self.quiet(project.set_version, self.item['version'])
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_archive_is_byte_checked_and_excludes_teacher_runtime(self):
        self.quiet(project.master.export, self.root)
        self.quiet(project.check, True)
        path = self.root / project.master.archive_path(self.item)
        with zipfile.ZipFile(path) as archive:
            self.assertFalse(project.TEACHER_FILES.intersection(archive.namelist()))
            self.assertIn('calculator.js', archive.namelist())
        calculator = self.project / 'dist/calculator.js'
        calculator.write_text(calculator.read_text() + '\n// changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'veraltet'):
            self.quiet(project.check, True)

    def test_catalog_cannot_silently_switch_to_unfiltered_export(self):
        self.data['packages'][0]['manifestOnly'] = False
        self.catalog.write_text(json.dumps(self.data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'manifestOnly'):
            project.check()


if __name__ == '__main__':
    unittest.main()

