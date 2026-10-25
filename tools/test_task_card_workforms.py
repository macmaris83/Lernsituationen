"""Focused checks for content-preserving master work-form metadata."""
from copy import deepcopy
import unittest

from task_card_workforms import apply_task_workforms


ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M1 2h3"></path></svg>'
SOCIAL = '<span class="assignment-social" data-workform="pair" title="Partnerarbeit">' + ICON + '<small>Partnerarbeit</small></span>'


def card(body, social="", task="0:1:1"):
    return ('<article class="assignment-frame" data-task-id="' + task
            + '" data-task-stable-id="' + task + '" data-source-task="0:1:1" data-task-number="9" data-task-signature="keep-signature">'
            '<span class="assignment-number" aria-label="Aufgabe 9">9</span>'
            '<button class="assignment-goodnotes-button" data-share-workbook=""><img class="assignment-goodnotes" src="assets/goodnotes.png" alt="GoodNotes"></button>'
            + social + '<div class="assignment-body">' + body + '</div>'
            '<label data-completion-label=""><input type="checkbox" data-task-complete="" data-task-id="'
            + task + '" disabled><span class="sr-only">Aufgabe erledigt</span></label></article>')


def page(cards, form="zunächst Einzelarbeit, anschließend Vierergruppen", mode=1):
    return ('<section data-mode-panel="' + str(mode) + '"><div class="phase-meta">'
            '<p><strong>Arbeitszeit:</strong> 45 Minuten</p><p>' + ICON
            + '<span><strong>Arbeitsform:</strong> ' + form + '</span></p></div>' + cards + '</section>')


def data(page_html, phase="informieren"):
    return {"id": "original-id", "version": "original-version", "pages": {phase + ".html": page_html},
            "progressMigration": {"tasks": {"original": {"signature": "keep"}}}}


class WorkformTests(unittest.TestCase):
    def test_exact_master_markup_added_without_changing_content_or_progress(self):
        body = ('<p><strong class="operator">Vergleichen</strong> Sie die beiden Angebote &amp; begründen Sie Ihre Wahl.</p>'
                '<p class="book-line"><img src="book.png"><a href="buch.html#s42">S. 42–43</a></p>')
        original = page(card(body))
        source = data(original)
        before = deepcopy(source)
        canonical = data(page(card('<p>Vergleichen Sie die beiden Angebote &amp; begründen Sie Ihre Wahl.</p>', SOCIAL)))
        report = apply_task_workforms(source, canonical)
        actual = source["pages"]["informieren.html"]
        self.assertEqual(actual.replace(SOCIAL, ""), original)
        self.assertIn('<div class="assignment-body">' + body + '</div>', actual)
        self.assertEqual(source["id"], before["id"])
        self.assertEqual(source["version"], before["version"])
        self.assertEqual(source["progressMigration"], before["progressMigration"])
        self.assertEqual(report["exact"], 1)
        self.assertNotIn("assignment-time", actual)

    def test_split_context_and_book_time_do_not_prevent_parent_match(self):
        question = "Welche betriebliche Folge ergibt sich aus der gewählten Zahlungsbedingung?"
        body = ('<p data-split-context="">Beantworten Sie schriftlich:</p><p>' + question + '</p>'
                '<p class="book-line">Zahlungsbedingungen, S. 41</p>')
        original = page(card(body, task="0:1:1.2"))
        source = data(original)
        canonical = data(page(card('<p>Prüfen Sie zunächst die Lieferbedingungen. ' + question
                                   + '</p><span class="assignment-time" data-time-ui="true">ca. 8 Min.</span>', SOCIAL)))
        report = apply_task_workforms(source, canonical)
        self.assertEqual(report["contained"], 1)
        self.assertEqual(source["pages"]["informieren.html"].replace(SOCIAL, ""), original)
        self.assertNotIn("ca. 8 Min.", source["pages"]["informieren.html"])

    def test_notes_links_controls_and_existing_phase_text_stay_exact(self):
        body = ('<p>Prüfen Sie Ihre Ergebnisse sorgfältig anhand der Quellen.</p>'
                '<aside class="assignment-note">Optional: <a href="m2.html?a=1&amp;b=2">KI-Hilfe</a></aside>'
                '<p><input type="text" value="&quot;Notiz&quot;" data-work="beleg"></p>')
        original = page(card(body))
        source = data(original)
        apply_task_workforms(source, {"pages": {}})
        actual = source["pages"]["informieren.html"]
        start = actual.index('<span class="assignment-social"')
        end = actual.index('</small></span>', start) + len('</small></span>')
        self.assertEqual(actual[:start] + actual[end:], original)
        self.assertIn('data-workform="phase-plan"', actual)
        self.assertIn('<small>Nach Phasenplan</small>', actual)
        self.assertIn('title="Nach Phasenplan · Arbeitsform der Phase: zunächst Einzelarbeit, anschließend Vierergruppen"', actual)
        self.assertIn(body, actual)

    def test_personal_reflection_uses_individual_form(self):
        source = data(page(card('<p>Reichen Sie Ihre persönliche Lernbilanz in Moodle ein. Eine Gruppenreflexion ersetzt Ihre individuelle Reflexion nicht.</p>')), "reflektieren")
        report = apply_task_workforms(source, {"pages": {}})
        result = source["pages"]["reflektieren.html"]
        self.assertIn('data-workform="individual"', result)
        self.assertIn('<small>Einzelarbeit</small>', result)
        self.assertEqual(report["source"], 1)
        self.assertEqual(report["fallback"], 0)

    def test_explicit_joint_canva_and_personal_task_are_distinguished(self):
        source = data(page(card('<p>Gestalten Sie Ihr Handlungsergebnis gemeinsam in Canva Education.</p>')
                           + card('<p>Erstellen Sie in Einzelarbeit Ihre persönliche Stellungnahme.</p>', task="0:1:2")))
        report = apply_task_workforms(source, {"pages": {}})
        result = source["pages"]["informieren.html"]
        self.assertIn('<small>Gruppenarbeit</small>', result)
        self.assertIn('<small>Einzelarbeit</small>', result)
        self.assertEqual(report["source"], 2)

    def test_tiny_boilerplate_does_not_copy_canonical_mandatory_workform(self):
        source = data(page(card('<p>Prüfen Sie das.</p>')))
        report = apply_task_workforms(source, data(page(card('<p>Prüfen Sie das.</p>', SOCIAL))))
        self.assertEqual(report["exact"], 0)
        self.assertEqual(report["fallback"], 1)
        self.assertIn('<small>Nach Phasenplan</small>', source["pages"]["informieren.html"])

    def test_open_product_task_is_only_a_group_recommendation(self):
        source = data(page(card('<p>Erstellen Sie die Beschlussvorlage in einem selbst gewählten professionellen Format.</p>')), "durchfuehren")
        report = apply_task_workforms(source, {"pages": {}})
        self.assertEqual(report["source"], 1)
        self.assertIn('<small>Gruppenarbeit (Empfehlung)</small>', source["pages"]["durchfuehren.html"])

    def test_matching_stays_in_same_learning_path(self):
        task = '<p>Vergleichen Sie die wirtschaftlichen Folgen der beiden Angebote.</p>'
        source = data(page(card(task), mode=2))
        report = apply_task_workforms(source, data(page(card(task, SOCIAL), mode=1)))
        self.assertEqual(report["exact"], 0)
        self.assertEqual(report["fallback"], 1)

    def test_existing_metadata_replaced_once_and_second_run_is_identical(self):
        task = '<p>Vergleichen Sie die wirtschaftlichen Folgen der beiden Angebote.</p>'
        old = '<span class="assignment-social" data-workform="group"><small>Alt</small></span>'
        source = data(page(card(task, old)))
        canonical = data(page(card(task, SOCIAL)))
        first = apply_task_workforms(source, canonical)
        result = deepcopy(source)
        second = apply_task_workforms(source, canonical)
        self.assertEqual(source, result)
        self.assertEqual(first, second)
        self.assertEqual(source["pages"]["informieren.html"].count('class="assignment-social"'), 1)
        self.assertIn(SOCIAL, source["pages"]["informieren.html"])


if __name__ == "__main__":
    unittest.main()
