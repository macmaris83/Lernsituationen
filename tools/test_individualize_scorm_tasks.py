import copy
import unittest
from lxml import html
from individualize_scorm_tasks import PHASES, normalized, signature, split_body, update_data


class IndividualTasksTest(unittest.TestCase):
    def fixture(self):
        data = {'pages': {}}
        meta = {'tasks': {}, 'orientationSignature': 'orientation-original', 'quizSignature': 'quiz-original'}
        for index, phase in enumerate(PHASES):
            panels = []
            for mode in range(1, 6):
                text = '<p><strong>Prüfen</strong> Sie das Ergebnis.</p><ul><li>Kriterium A</li><li>Kriterium B</li></ul>'
                if mode == 5 and phase != 'bewerten':
                    text = '<p><strong>Erstellen</strong> Sie das Produkt.</p>'
                if mode == 5 and phase == 'informieren':
                    text = '<ul><li><strong>Analysieren</strong> Sie M1.</li><li><strong>Berechnen</strong> Sie den Bedarf.</li><li>Checkpoint A: Ergebnisse abgleichen.</li></ul>'
                if mode == 5 and phase == 'reflektieren':
                    text = '<p><strong>Beantworten</strong> Sie schriftlich:</p><ul><li>Was gelang?</li><li>Was ändern Sie?</li></ul>'
                text += '<p class="book-line">Lehrbuch S. 30-31</p>'
                body = html.fragment_fromstring(text, create_parent='div')
                task = f'{index}:{mode}:1'
                meta['tasks'][task] = {'phase': phase, 'mode': mode, 'signature': signature(body.text_content())}
                panels.append(f'<section data-mode-panel="{mode}"><article class="assignment-frame" data-task-id="{task}"><span class="assignment-number">1</span><div class="assignment-body">{text}</div><label><input data-task-complete="" data-task-id="{task}"></label></article></section>')
            data['pages'][phase + '.html'] = ''.join(panels)
        return data, meta

    def test_numbering_crosses_all_six_phases_and_keeps_identities(self):
        data, meta = self.fixture()
        original_ids = set(meta['tasks'])
        counts, _ = update_data(data, meta, 'FIXTURE')
        self.assertEqual(counts, {1: 6, 2: 6, 3: 6, 4: 6, 5: 8})
        self.assertTrue(original_ids <= set(meta['tasks']))
        for mode, count in counts.items():
            numbers = []
            for phase in PHASES:
                doc = html.fragment_fromstring(data['pages'][phase + '.html'], create_parent='div')
                cards = doc.xpath(f'.//*[@data-mode-panel="{mode}"]/*')
                for card in cards:
                    numbers.append(int(card.get('data-task-number')))
                    self.assertEqual(card.get('data-task-id'), card.get('data-task-stable-id'))
                    self.assertEqual(card.xpath('.//input')[0].get('data-task-id'), card.get('data-task-id'))
            self.assertEqual(numbers, list(range(1, count + 1)))

    def test_criteria_and_checkpoints_stay_with_their_order(self):
        data, meta = self.fixture()
        update_data(data, meta, 'FIXTURE')
        doc = html.fragment_fromstring(data['pages']['bewerten.html'], create_parent='div')
        self.assertEqual(len(doc.xpath('.//*[@data-mode-panel="5"]//article')), 1)
        self.assertIn('Kriterium A', doc.text_content())
        doc = html.fragment_fromstring(data['pages']['informieren.html'], create_parent='div')
        cards = doc.xpath('.//*[@data-mode-panel="5"]//article')
        self.assertEqual(len(cards), 2)
        self.assertIn('Checkpoint A:', cards[1].text_content())
        self.assertEqual(len(cards[0].xpath('.//strong')), 1)

    def test_reflection_retains_its_original_intro_on_every_card(self):
        data, meta = self.fixture()
        update_data(data, meta, 'FIXTURE')
        doc = html.fragment_fromstring(data['pages']['reflektieren.html'], create_parent='div')
        cards = doc.xpath('.//*[@data-mode-panel="5"]//article')
        self.assertEqual(len(cards), 2)
        for card in cards:
            self.assertIn('Beantworten Sie schriftlich:', card.text_content())
            self.assertTrue(card.xpath('.//strong'))

    def test_migration_requires_the_original_bundle_signature(self):
        data, meta = self.fixture()
        before = copy.deepcopy(meta)
        update_data(data, meta, 'FIXTURE')
        for task, rule in meta['migration']['tasks'].items():
            self.assertEqual(rule['signature'], meta['tasks'][task]['signature'])
            source = rule['from'][0]
            self.assertEqual(source['signature'], before['tasks'][source['id']]['signature'])
        self.assertEqual(meta['orientationSignature'], before['orientationSignature'])
        self.assertEqual(meta['quizSignature'], before['quizSignature'])

    def test_partition_preserves_wording_and_inline_operators(self):
        body = html.fragment_fromstring('<p><strong>Analysieren</strong> Sie M1. Entscheiden Sie, welche Materialien zuerst erforderlich sind.</p>', create_parent='div')
        parts = split_body(body, 'LS01:0:4:1', 'informieren', 4)
        self.assertEqual(len(parts), 2)
        self.assertEqual(normalized(body.text_content()), normalized(' '.join(c.text_content() for group in parts for c in group)))
        self.assertEqual(parts[0][0].xpath('.//strong')[0].text, 'Analysieren')


if __name__ == '__main__':
    unittest.main()
