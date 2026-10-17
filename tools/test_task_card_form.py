import copy
import unittest
from lxml import html
from transfer_task_card_form import body_text, phase_budgets, task_clocks, patch_runtime


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

    def test_task_clocks_keep_source_budget_and_identity(self):
        data=self.fixture()
        source=copy.deepcopy(data)
        report=task_clocks(data,{'phaseBudgets':{'informieren':180}})
        self.assertEqual(report[0]['allocatedMinutes'],180)
        before=html.fragment_fromstring(source['pages']['informieren.html'])
        after=html.fragment_fromstring(data['pages']['informieren.html'])
        self.assertEqual(body_text(before.xpath('.//*[@class="assignment-body"]')[0]),
                         body_text(after.xpath('.//*[@class="assignment-body"]')[0]))
        self.assertEqual(after.xpath('.//*[@data-minutes]')[0].get('data-minutes'),'180.0')
        self.assertEqual(after.xpath('.//article')[0].get('data-task-signature'),'original')
        once=copy.deepcopy(data)
        task_clocks(data,{'phaseBudgets':{'informieren':180}})
        self.assertEqual(data,once)

    def test_all_learning_paths_share_the_existing_budget(self):
        data=self.fixture()
        panel=data['pages']['informieren.html']
        data['pages']['informieren.html']+=panel.replace('data-mode-panel="1"','data-mode-panel="3"').replace('180 Minuten','im Gesamtzeitbudget planen')
        report=task_clocks(data,{'phaseBudgets':{'informieren':180}})
        self.assertEqual([r['minutes'] for r in report],[180,180])
        self.assertIn('im Gesamtzeitbudget planen',data['pages']['informieren.html'])


if __name__=='__main__':
    unittest.main()
