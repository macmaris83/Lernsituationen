import copy
import unittest
from lxml import html
from transfer_task_card_form import body_text, phase_budgets, patch_runtime


class PhaseBudgetTests(unittest.TestCase):
    def fixture(self):
        return {'pages': {'informieren.html': '<section data-mode-panel="1"><div class="phase-meta"><p><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/></svg><span>Arbeitszeit: 4 Unterrichtsstunden · 180 Minuten</span></p><p>Arbeitsform: Einzelarbeit</p></div><article class="assignment-frame" data-task-id="0:1:1" data-task-signature="original"><div class="assignment-body"><p><strong>Analysieren</strong> Sie M1.</p><p class="book-line">S. 33–38</p></div></article></section>'}}

    def test_original_budget_labelled_as_phase_and_instructions_unchanged(self):
        data=self.fixture()
        before=html.fragment_fromstring(data['pages']['informieren.html'])
        expected=body_text(before.xpath('.//*[@class="assignment-body"]')[0])
        self.assertEqual(phase_budgets(data),1)
        after=html.fragment_fromstring(data['pages']['informieren.html'])
        body=after.xpath('.//*[@class="assignment-body"]')[0]
        self.assertEqual(body_text(body),expected)
        budget=body.xpath('.//*[@data-phase-budget]')[0]
        self.assertEqual(budget.get('data-phase-budget-value'),'4 Unterrichtsstunden · 180 Minuten')
        self.assertIn('Arbeitszeit der Phase:',budget.text_content())
        self.assertIsNone(budget.get('data-minutes'))
        self.assertEqual(after.xpath('.//article')[0].get('data-task-signature'),'original')

    def test_real_task_times_are_kept_and_application_is_idempotent(self):
        data=self.fixture()
        data['pages']['informieren.html']=data['pages']['informieren.html'].replace('</strong> Sie M1.</p>','</strong> Sie M1.</p><span class="assignment-time" data-time-ui="true" data-minutes="12">12 Min.</span>')
        original=copy.deepcopy(data)
        self.assertEqual(phase_budgets(data),0)
        self.assertEqual(data,original)
        data=self.fixture();phase_budgets(data);once=copy.deepcopy(data)
        self.assertEqual(phase_budgets(data),0)
        self.assertEqual(data,once)


if __name__=='__main__':
    unittest.main()
