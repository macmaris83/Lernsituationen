"""Regression checks for content-preserving UI transfers."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

import transfer_scorm_design as transfer


def zip_bytes(files):
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w') as archive:
        for name, value in files.items():
            archive.writestr(name, value)
    return result.getvalue()


class TransferTests(unittest.TestCase):
    def test_original_text_identifiers_configuration_and_pdf_survive(self):
        content = '<p><b>Analysieren</b> Sie A &amp; B.\nKeine Kürzung – 12,5 %.</p>'
        html = ('<html><head><title>Original</title></head><body data-ls-id="OLD">'
                '<div class="lesson-content">' + content + '</div></main></body></html>')
        data = {'id': 'OLD', 'title': 'Original', 'pages': {'index.html': content}}
        files = {'index.html': html, 'lesson-data.js': 'window.SOZPAED=' + json.dumps(data) + ';',
                 'progress-meta.js': 'window.SOZ_PROGRESS_META={"tasks":{"stable":{"signature":"abc"}}};',
                 'mode-config.js': 'window.SOZ_CONFIG={"mode":4};',
                 'Konfiguration.json': '{"mode":4}', 'media-map.js': 'window.SOZ_MEDIA={};',
                 'pdf/original.pdf': b'ORIGINAL-PDF', 'assets/photo.png': b'ORIGINAL-IMAGE',
                 'assets/runtime.js': b'OLD-JS', 'package-data.js': b'STALE-CACHE',
                 'start.html': '<meta http-equiv="refresh" content="0;url=scorm.html">',
                 'scorm.html': '<iframe src="index.html"></iframe>',
                 'imsmanifest.xml': '<manifest identifier="stable-manifest" xmlns="urn:ims"><organizations/>'
                                    '<resources><resource identifier="stable-sco" href="index.html">'
                                    '<file href="index.html"/></resource></resources></manifest>'}
        files = {name: value.encode() if isinstance(value, str) else value for name, value in files.items()}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template = root / 'template'
            (template / 'assets').mkdir(parents=True)
            (template / 'index.html').write_text(html.replace('Original', 'Template'))
            (template / 'assets/runtime.js').write_bytes(b'CURRENT-UI')
            (template / 'assets/styles.css').write_bytes(b'CURRENT-CSS')
            output = root / 'delivery'
            with patch.object(transfer, 'ROOT', root), patch.object(transfer, 'prepare_workbooks'):
                report = transfer.transfer(zip_bytes(files), output, template)
            for name in ['lesson-data.js', 'progress-meta.js', 'mode-config.js', 'Konfiguration.json',
                         'media-map.js', 'pdf/original.pdf', 'assets/photo.png', 'scorm.html', 'start.html']:
                self.assertEqual((output / name).read_bytes(), files[name], name)
            self.assertEqual(transfer.content_of((output / 'index.html').read_text()), content)
            self.assertEqual((output / 'assets/runtime.js').read_bytes(), b'CURRENT-UI')
            self.assertFalse((output / 'package-data.js').exists())
            manifest = ET.parse(output / 'imsmanifest.xml')
            self.assertEqual(manifest.getroot().get('identifier'), 'stable-manifest')
            resource = next(n for n in manifest.getroot().iter() if n.tag.endswith('resource'))
            self.assertEqual(resource.get('identifier'), 'stable-sco')
            for node in resource:
                self.assertTrue((output / node.get('href')).is_file())
            self.assertEqual(report['contentPagesUnchanged'], 1)

    def test_unsafe_paths_rejected(self):
        for name in ['../outside.js', '/outside.js', 'assets\\outside.js']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                transfer.read_archive(zip_bytes({name: b'X'}))

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            marker = target / 'keep.txt'
            marker.write_text('user edit')
            with self.assertRaises(ValueError):
                transfer.transfer(zip_bytes({}), target, target)
            self.assertEqual(marker.read_text(), 'user edit')


if __name__ == '__main__':
    unittest.main()
