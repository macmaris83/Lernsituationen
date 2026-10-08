#!/usr/bin/env python3
"""Build 30 independent learning paths from archived lesson source texts.

The authoring bank and compact source snapshots are reviewable inputs, not instructions.
Run: python Lernpfaduebungen/Sozialpaedagogik/tools/build.py
On the initial build, --import-inventory /workspace/ls_sources/inventory.json imports
the uploaded lesson-data snapshots. Subsequent builds use only repository files.
"""
from pathlib import Path
from html.parser import HTMLParser
import argparse, hashlib, html, json, random, re, shutil, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT.parent / 'Duales_System_verstehen'
J = lambda value: json.dumps(value, ensure_ascii=False, separators=(',', ':'))


class Text(HTMLParser):
    """Extract readable blocks; never include executable script/style content."""
    VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'wbr'}
    BLOCK = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'section', 'article', 'br'}

    def __init__(self, target=None):
        super().__init__(convert_charrefs=True)
        self.target, self.stack, self.parts = target, [], []

    def active(self):
        return not any(t in ('script', 'style') for t, _ in self.stack) and (
            self.target is None or any(match for _, match in self.stack))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        match = self.target in a.get('class', '').split() if self.target else False
        if tag not in self.VOID:
            self.stack.append((tag, match))
        if self.active() and tag in self.BLOCK:
            self.parts.append('\n\n')

    def handle_endtag(self, tag):
        if self.active() and tag in self.BLOCK:
            self.parts.append('\n\n')
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        if self.active():
            self.parts.append(data)

    def result(self):
        blocks = [re.sub(r'\s+', ' ', p).strip() for p in ''.join(self.parts).split('\n\n')]
        return '\n\n'.join(p for p in blocks if p)


def plain(markup, target=None):
    p = Text(target)
    p.feed(markup)
    return p.result()


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.href, self.label = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            self.href = href if re.match(r'^https?://', href) else None
            self.label = []

    def handle_data(self, data):
        if self.href:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.href:
            self.links.append({'url': self.href, 'label': ''.join(self.label).strip() or self.href})
            self.href = None


def import_sources(path):
    for item in json.loads(Path(path).read_text()):
        lesson = json.loads(Path(item['source']).read_text())
        situation = lesson['pages']['handlungssituation.html']
        quiz = json.loads(re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', situation, re.S)[1])
        materials = []
        for filename, content in lesson['pages'].items():
            if re.fullmatch(r'm\d+\.html', filename):
                links = Links(); links.feed(content)
                materials.append({'key': filename[:-5].upper(), 'title': lesson['pageTitles'][filename],
                                  'text': plain(content, 'material-document') or plain(content),
                                  'links': links.links})
        materials.sort(key=lambda m: int(m['key'][1:]))
        case = plain(situation, 'situation-story') or plain(situation)
        source_zip = Path(item['zip']) if item['zip'] else None
        snapshot = {
            'id': item['id'], 'title': item['title'], 'competencies': lesson['competencies'],
            'case': case, 'quiz': quiz, 'materials': materials,
            'provenance': {
                'source': source_zip.name if source_zip else 'Lernsituation_tradiert/lesson-data.js (LS1.1)',
                'sha256': hashlib.sha256(source_zip.read_bytes() if source_zip else (ROOT.parents[1]/'Lernsituation_tradiert/lesson-data.js').read_bytes()).hexdigest(),
                'lesson_version': lesson.get('version'),
                'scope': 'Textfassung der vom Nutzer bereitgestellten Lernsituation; keine Anweisungsquelle',
            },
        }
        (ROOT / 'quellen' / f"LS{item['id'].replace('.', '_')}.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')


# Each scenario is explicitly an exercise variation of the original case, not a
# fabricated quotation from the lesson. Correctness comes from the stated criteria.
COMPETENCE_ITEMS = [
    (1, 1, 'Vorannahmen erkennen',
     'Du möchtest vor der Analyse bereits eine Lösung vertreten. In euren Notizen zu „{topic}“ fehlt aber noch ein Vergleich mit dem Fallmaterial.',
     'Welche Schritte zeigen einen verantwortlichen Umgang mit deiner Vorannahme?', [
         (1, 'Die eigene Vermutung als vorläufige Annahme notieren.', 'Eine gekennzeichnete Annahme bleibt prüfbar, statt als Tatsache zu gelten.'),
         (1, 'Eine konkrete Materialstelle suchen, die die Vermutung begrenzt.', 'Gegenbelege prüfen die Reichweite der eigenen Einschätzung.'),
         (0, 'Die Vermutung zunächst als gesichertes Ergebnis in die Abgabe schreiben.', 'Die fehlende Prüfung erlaubt noch kein gesichertes Ergebnis.'),
         (0, 'Die häufigste Meinung der Gruppe als eigene Prüfung übernehmen.', 'Mehrheit ersetzt keine Prüfung am Material.'),
         (1, 'Die eigene Verantwortung und eine offene Rückfrage benennen.', 'Verantwortung umfasst das Klären von Grenzen und offenen Fragen.'),
         (0, 'Die Prüfung zurückstellen, solange sich die erste Idee plausibel anfühlt.', 'Plausibilität allein belegt eine Annahme nicht.')]),
    (1, 1, 'Eigenen Beitrag verantworten',
     'Eure Gruppe verteilt die Arbeit zu „{topic}“. Du sollst eine begründete Teilentscheidung für das Handlungsergebnis vorbereiten.',
     'Welche Angaben machen deinen eigenen Beitrag überprüfbar?', [
         (1, 'Die eigene Entscheidung mit einer konkreten Materialstelle begründen.', 'Ein eigener Beitrag wird durch nachvollziehbare Begründung sichtbar.'),
         (0, 'Die gemeinsame Endfassung ausschließlich als eigene Leistung beschreiben.', 'Gruppenleistung und eigener Anteil dürfen nicht gleichgesetzt werden.'),
         (1, 'Benennen, welchen Teil du selbst geprüft und welchen du übernommen hast.', 'Die Trennung macht Verantwortung und Zusammenarbeit transparent.'),
         (0, 'Offene Fragen auslassen, damit die persönliche Einschätzung sicher wirkt.', 'Verdeckte Unsicherheit verhindert eine realistische Reflexion.'),
         (0, 'Die eigene Entscheidung allein mit der benötigten Arbeitszeit begründen.', 'Arbeitszeit zeigt Aufwand, aber nicht die fachliche Tragfähigkeit.'),
         (0, 'Den eigenen Anteil aus der Zahl der Seiten der Gruppe ableiten.', 'Umfang der gemeinsamen Arbeit belegt keine eigene Entscheidung.')]),
    (1, 2, 'Sichtweisen abgleichen',
     'Beim Thema „{topic}“ kommen zwei Personen in eurer Gruppe zu verschiedenen Deutungen derselben Fallstelle.',
     'Was unterstützt einen fachlichen Abgleich der Sichtweisen?', [
         (1, 'Die beiden Deutungen mit ihren jeweiligen Belegen gegenüberstellen.', 'Die Sichtweisen werden dadurch sachlich vergleichbar.'),
         (0, 'Die Deutung der zuerst sprechenden Person als verbindlich festhalten.', 'Die Reihenfolge des Sprechens entscheidet keine fachliche Frage.'),
         (1, 'Nachfragen, welche Beobachtung die andere Person für wichtig hält.', 'Nachfragen klärt den Bezug zwischen Sichtweise und Material.'),
         (0, 'Die abweichende Deutung als fehlende Teamfähigkeit behandeln.', 'Fachlich begründete Unterschiede sind kein Beleg fehlender Teamfähigkeit.'),
         (1, 'Festhalten, worüber Einigkeit besteht und was noch geprüft werden muss.', 'Ein transparenter Zwischenstand wahrt Gemeinsamkeiten und offene Punkte.'),
         (0, 'Die offene Frage ohne Materialprüfung durch eine Abstimmung beenden.', 'Abstimmen kann organisieren, ersetzt aber keine fachliche Prüfung.')]),
    (1, 2, 'Beteiligung ermöglichen',
     'Eine Person spricht in eurer Auswertung zu „{topic}“ viel. Eine andere hat bisher ihre abweichende Fallnotiz noch nicht eingebracht.',
     'Welche Handlungen ermöglichen eine überprüfbare gemeinsame Entscheidung?', [
         (0, 'Die ausführlichste Wortmeldung ohne weitere Rückfrage als Konsens protokollieren.', 'Ausführlichkeit zeigt nicht, dass alle beteiligt waren.'),
         (1, 'Die bisher nicht eingebrachte Fallnotiz gezielt in den Vergleich aufnehmen.', 'Eine fehlende Perspektive kann wichtige Belege enthalten.'),
         (1, 'Den Beitrag jeder Person zur Begründung der Entscheidung kenntlich machen.', 'Die Beiträge bleiben in der gemeinsamen Entscheidung nachvollziehbar.'),
         (0, 'Schweigen als Zustimmung zur bisherigen Deutung eintragen.', 'Schweigen belegt keine ausdrückliche Zustimmung.'),
         (0, 'Die Entscheidung der redegewandten Person ohne Belege übertragen.', 'Redegewandtheit ersetzt keine fachliche Begründung.'),
         (0, 'Abweichende Notizen bis nach der Abgabe aus dem Gespräch heraushalten.', 'Dann können sie die gemeinsame Entscheidung nicht mehr beeinflussen.')]),
    (1, 3, 'Fallinformationen ordnen',
     'Für „{topic}“ liegen wörtliche Aussagen, Beobachtungen und erste Erklärungen nebeneinander in euren Notizen.',
     'Welche Schritte schaffen eine methodisch tragfähige Grundlage?', [
         (1, 'Beobachtete Vorgänge und mögliche Erklärungen getrennt erfassen.', 'Diese Trennung verhindert, dass Deutungen als Beobachtung erscheinen.'),
         (0, 'Die erste Erklärung als Überschrift für alle weiteren Notizen verwenden.', 'Das könnte widersprechende Informationen vorschnell einordnen.'),
         (1, 'Zu jeder wichtigen Aussage die zugehörige Materialstelle notieren.', 'Die Fallinformationen werden so überprüfbar.'),
         (0, 'Nur Informationen aufnehmen, die die bisherige Lösung bestätigen.', 'Eine einseitige Auswahl verdeckt Gegenbelege.'),
         (1, 'Fehlende Angaben als offen kennzeichnen und eine Prüffrage formulieren.', 'Fehlendes Wissen wird dadurch zum konkreten nächsten Arbeitsschritt.'),
         (0, 'Lücken mit einer typischen Alltagserfahrung als Falltatsache ergänzen.', 'Erfahrung kann eine Hypothese liefern, aber fehlende Fallangaben nicht ersetzen.')]),
    (1, 3, 'Vergleichskriterien festlegen',
     'Ihr wollt zwei Handlungsoptionen zu „{topic}“ vergleichen, bevor ihr euch für das Handlungsergebnis entscheidet.',
     'Welche Vorgehensweisen machen den Vergleich nachvollziehbar?', [
         (0, 'Für jede Option erst nach der Auswahl passende Kriterien suchen.', 'Nachträgliche Kriterien könnten die Vorentscheidung nur bestätigen.'),
         (1, 'Vor der Auswahl dieselben fachlichen Kriterien für beide Optionen festlegen.', 'Gemeinsame Kriterien ermöglichen einen fairen Vergleich.'),
         (1, 'Den Bezug jeder Bewertung zu einer konkreten Fallangabe dokumentieren.', 'Bewertungen werden durch Fallbelege nachvollziehbar.'),
         (0, 'Die vertrautere Option wählen und ihren Fallbezug erst später ergänzen.', 'Vertrautheit belegt keine Passung zum Fall.'),
         (0, 'Die Zahl der zustimmenden Personen als einziges Qualitätskriterium nutzen.', 'Zustimmung allein misst nicht die fachliche Qualität.'),
         (0, 'Die optisch überzeugendere Option unabhängig von den Kriterien bevorzugen.', 'Die Gestaltung ersetzt keine inhaltliche Bewertung.')]),
    (1, 4, 'Quellen kenntlich machen',
     'In eurem digitalen Handlungsergebnis zu „{topic}“ stehen ein Materialzitat, eine eigene Deutung und eine ergänzende Recherche.',
     'Was macht diese Informationen überprüfbar?', [
         (1, 'Das Materialzitat als Zitat mit Materialnummer kennzeichnen.', 'Zitat und Quelle werden eindeutig zugeordnet.'),
         (1, 'Die eigene Deutung als eigene Schlussfolgerung ausweisen.', 'Dadurch wird sie nicht mit einer Quellenaussage verwechselt.'),
         (0, 'Alle drei Aussagen ohne Kennzeichnung in einen gemeinsamen Absatz mischen.', 'Lesende könnten Herkunft und Status nicht unterscheiden.'),
         (1, 'Bei der Recherche Herkunft und gegebenenfalls den Quellenstand angeben.', 'Der Nachweis ermöglicht eine erneute Prüfung.'),
         (0, 'Eine passende KI-Antwort als Beleg für das Originalmaterial verwenden.', 'Eine generierte Antwort beweist nicht, was im Original steht.'),
         (0, 'Nur den Namen der Datei nennen, in der die Gruppe gearbeitet hat.', 'Die Arbeitsdatei benennt nicht die fachliche Informationsquelle.')]),
    (1, 4, 'Digitales Ergebnis prüfen',
     'Die Ergebnisse zu „{topic}“ sollen im Team auf einem Tablet gelesen und am Material überprüft werden können.',
     'Welche Gestaltungsentscheidungen unterstützen diesen Zweck?', [
         (0, 'Materialbezüge durch Animationen statt durch Quellenangaben zeigen.', 'Animationen ermöglichen keine Prüfung der Informationsherkunft.'),
         (1, 'Belege so zuordnen, dass sie der jeweiligen Aussage folgen.', 'Aussage und Beleg können gemeinsam geprüft werden.'),
         (0, 'Für die mobile Ansicht möglichst viele Informationen in eine kleine Grafik setzen.', 'Eine überfüllte kleine Grafik erschwert die Lesbarkeit.'),
         (1, 'Die Lesbarkeit der exportierten Fassung auf Tabletbreite kontrollieren.', 'Die tatsächliche Nutzungssituation gehört zur Medienprüfung.'),
         (0, 'Nur die bearbeitbare Datei prüfen und den Export ungeöffnet weitergeben.', 'Der Export kann anders aussehen als die Arbeitsdatei.'),
         (0, 'Die Gestaltung unabhängig von der Nachvollziehbarkeit der Argumente optimieren.', 'Medien dienen hier einer lesbaren, überprüfbaren Argumentation.')]),
    (2, 1, 'Eine Einschätzung revidieren',
     'Du hast zu „{topic}“ eine Lösung vorgeschlagen. Eine zweite Materialstelle begrenzt deine bisherige Begründung.',
     'Welche Reaktionen zeigen fachliche Selbstreflexion?', [
         (1, 'Benennen, welcher Teil der eigenen Begründung durch den neuen Beleg begrenzt wird.', 'Die Revision wird an einem konkreten Unterschied festgemacht.'),
         (0, 'Den neuen Beleg weglassen, damit die ursprüngliche Lösung konsistent aussieht.', 'Das verdeckt eine fachliche Begrenzung.'),
         (1, 'Den weiterhin belegten Teil erhalten und die offene Aussage überarbeiten.', 'Eine begründete Revision muss nicht alles Vorherige verwerfen.'),
         (0, 'Die gesamte bisherige Arbeit ohne Prüfung als wertlos einstufen.', 'Eine begrenzte Aussage macht nicht automatisch jede Leistung wertlos.'),
         (1, 'Eine konkrete zusätzliche Prüffrage für die verbleibende Unsicherheit formulieren.', 'Unsicherheit wird in einen bearbeitbaren Lernschritt übersetzt.'),
         (0, 'Die Überarbeitung einer anderen Person überlassen und den eigenen Anteil unverändert nennen.', 'Das würde die tatsächliche eigene Verantwortung verschleiern.')]),
    (2, 1, 'Verantwortungsgrenzen klären',
     'Bei „{topic}“ soll eure Praxisgruppe eine Entscheidung vorbereiten. Im Material steht keine ausdrückliche Freigabe, diese selbst verbindlich umzusetzen.',
     'Welche nächsten Schritte sind verantwortlich?', [
         (1, 'Die eigene Zuständigkeit vor einer verbindlichen Zusage klären.', 'Eine Vorbereitung ist noch keine Freigabe zur Umsetzung.'),
         (1, 'Eine begründete Empfehlung mit der zuständigen Fachkraft besprechen.', 'Eine fachliche Rückfrage verbindet Mitarbeit und Zuständigkeitsklärung.'),
         (0, 'Die verbindliche Umsetzung zusagen, weil die Gruppe den Fall gelesen hat.', 'Fallkenntnis allein überträgt keine Zuständigkeit.'),
         (0, 'Alle eigenen Beobachtungen zurückhalten, bis jede Unsicherheit verschwunden ist.', 'Eigene Beobachtungen können bereits jetzt zur Klärung beitragen.'),
         (1, 'Festhalten, welche Informationen für die Entscheidung noch fehlen.', 'So wird der Klärungsbedarf konkret.'),
         (0, 'Die eigene Zuständigkeit aus der Zustimmung einer anderen Praxisperson ableiten.', 'Diese Zustimmung ist keine verlässliche Übertragung von Verantwortung.')]),
    (2, 2, 'Unterschiedliche Deutungen bearbeiten',
     'Zwei Gruppenmitglieder begründen zu „{topic}“ verschiedene Optionen. Eine Begründung nutzt eine wörtliche Aussage, die andere eine Interpretation.',
     'Wie lässt sich die gemeinsame Entscheidung fachlich weiterführen?', [
         (1, 'Beide Personen den Bezug zwischen Beleg und Schlussfolgerung erklären lassen.', 'Damit kann die Gruppe die beiden Argumentationen prüfen.'),
         (0, 'Wörtliche Aussage und Interpretation ohne Kennzeichnung als zwei Fakten zählen.', 'Die unterschiedlichen Informationsarten müssen erkennbar bleiben.'),
         (1, 'Die Optionen an denselben vereinbarten Kriterien vergleichen.', 'Gleiche Kriterien machen Unterschiede im Ergebnis sichtbar.'),
         (0, 'Die weniger selbstsicher vertretene Option ohne Prüfung aussortieren.', 'Sicherheit beim Sprechen ist kein fachliches Kriterium.'),
         (1, 'Eine noch offene Differenz mit einer konkreten Rückfrage im Protokoll sichern.', 'Das Protokoll wahrt die verbleibende fachliche Klärung.'),
         (0, 'Den Konflikt durch einen Mittelwert der beiden Meinungen fachlich lösen.', 'Ein Mittelwert von Meinungen ist keine begründete Fallentscheidung.')]),
    (2, 2, 'Beteiligung und Rückmeldung sichern',
     'Eure Planung zu „{topic}“ soll mit Beteiligten besprochen werden. Noch ist nicht festgehalten, wie ihre Rückmeldungen in die Entscheidung eingehen.',
     'Welche Maßnahmen ermöglichen tatsächliche Beteiligung?', [
         (1, 'Die Entscheidung verständlich erläutern und vor dem Abschluss Rückfragen ermöglichen.', 'Beteiligung braucht Verständlichkeit und einen noch offenen Einflusszeitpunkt.'),
         (0, 'Den bereits unveränderlichen Beschluss vorstellen und dies als Mitentscheidung bezeichnen.', 'Information über einen Beschluss ist keine Mitentscheidung.'),
         (1, 'Vereinbaren, wann und wie die Beteiligten eine Rückmeldung zur Verwendung erhalten.', 'Eine Rückmeldung macht den Umgang mit ihren Beiträgen sichtbar.'),
         (0, 'Nur zustimmende Rückmeldungen dokumentieren, um den Prozess übersichtlich zu halten.', 'Das würde die tatsächlichen Rückmeldungen verzerren.'),
         (1, 'Festhalten, welche Vorschläge übernommen und welche begründet nicht übernommen werden.', 'Die Entscheidung über Beiträge bleibt nachvollziehbar.'),
         (0, 'Ausbleibende Antworten als Zustimmung zu jedem Planungspunkt werten.', 'Keine Antwort belegt nicht automatisch Einverständnis.')]),
    (2, 3, 'Eine Kriterienmatrix auswerten',
     'Beim Vergleich zu „{topic}“ erfüllt Option A ein fachliches Kriterium gut, ihr Aufwand ist aber noch ungeklärt. Option B ist machbar, ihr fachlicher Bezug jedoch schwächer.',
     'Welche Schlussfolgerungen sind methodisch gerechtfertigt?', [
         (1, 'Die offene Aufwandsschätzung von Option A vor der endgültigen Auswahl prüfen.', 'Eine ungeklärte Machbarkeit begrenzt die Entscheidung.'),
         (0, 'Option A allein wegen des einen guten Kriteriums endgültig auswählen.', 'Ein gutes Kriterium beantwortet die offene Machbarkeit nicht.'),
         (1, 'Die unterschiedliche Bedeutung der Kriterien im Entscheidungsweg erläutern.', 'Eine transparente Gewichtung begründet die Abwägung.'),
         (0, 'Option B wählen und den schwächeren fachlichen Bezug aus der Matrix entfernen.', 'Ein Nachteil darf nicht aus dem Vergleich gelöscht werden.'),
         (1, 'Die offene Information und die vorläufige Empfehlung getrennt dokumentieren.', 'Vorläufigkeit bleibt so erkennbar und überprüfbar.'),
         (0, 'Die Anzahl gefüllter Felder statt ihrer Inhalte als entscheidenden Nachweis verwenden.', 'Vollständige Felder sind noch keine inhaltlich tragfähige Bewertung.')]),
    (2, 3, 'Wirkung überprüfbar planen',
     'Für „{topic}“ schlägt eure Gruppe einen Handlungsschritt vor. Ihr wollt später prüfen, ob er unter den Bedingungen des Falls hilfreich war.',
     'Was gehört zu einem überprüfbaren Plan?', [
         (1, 'Ein beobachtbares Kriterium passend zum fachlichen Ziel festlegen.', 'Eine Wirkung muss am Ziel und an konkreten Beobachtungen geprüft werden.'),
         (1, 'Den Zeitpunkt der Auswertung und die benötigten Belege vereinbaren.', 'Ohne Zeitpunkt und Belege bleibt die Prüfung unbestimmt.'),
         (0, 'Die eigene Zufriedenheit als einzigen Wirksamkeitsnachweis verwenden.', 'Zufriedenheit der Planenden belegt die Wirkung für Beteiligte nicht.'),
         (1, 'Benennen, welche Zuständigkeit und welcher Aufwand für den Schritt nötig sind.', 'Der Plan muss unter den tatsächlichen Bedingungen machbar sein.'),
         (0, 'Ein günstiges einzelnes Ereignis als sicheren Beweis einer dauerhaften Wirkung werten.', 'Ein Ereignis rechtfertigt keine sichere dauerhafte Wirkungsbehauptung.'),
         (0, 'Die Auswertung erst dann festlegen, wenn ein gutes Ergebnis sichtbar ist.', 'Die nachträgliche Auswahl könnte die Prüfung verzerren.')]),
    (2, 4, 'Eine digitale Behauptung prüfen',
     'Eine Person ergänzt eure Arbeit zu „{topic}“ mit einer überzeugend formulierten KI-Antwort. Deren Aussage ist in den angegebenen Originalquellen noch nicht gefunden.',
     'Wie nutzt ihr diese Information fachlich verantwortbar?', [
         (1, 'Die Aussage vor der Übernahme an der angegebenen Originalquelle prüfen.', 'Die Originalquelle muss den Inhalt tatsächlich tragen.'),
         (0, 'Die sprachliche Sicherheit der KI als Nachweis der fachlichen Richtigkeit verwenden.', 'Sprachliche Sicherheit belegt keine Richtigkeit.'),
         (1, 'Die ungeprüfte Aussage bis zur Klärung als offene Frage kennzeichnen.', 'Das verhindert ihre Verwechslung mit gesichertem Wissen.'),
         (0, 'Die Quellenangabe übernehmen, ohne zu prüfen, ob sie die Aussage enthält.', 'Eine Quellenangabe allein bestätigt den Inhalt nicht.'),
         (1, 'Eine Abweichung vom Original in der eigenen Fassung nachvollziehbar korrigieren.', 'Eine dokumentierte Korrektur wahrt die fachliche Nachvollziehbarkeit.'),
         (0, 'Die Aussage durch eine zweite KI-Antwort statt am Original absichern.', 'Übereinstimmende Generierungen ersetzen die Prüfung des Originals nicht.')]),
    (2, 4, 'Eine Exportfassung überprüfen',
     'Die digitale Endfassung zu „{topic}“ ist exportiert. Auf einem Tablet ist eine Quellenangabe abgeschnitten; die Arbeitsdatei zeigt sie noch vollständig.',
     'Welche Maßnahmen sichern eine überprüfbare Abgabe?', [
         (1, 'Den Fehler in der Gestaltung korrigieren und die Fassung neu exportieren.', 'Die tatsächlich gelesene Endfassung muss vollständig sein.'),
         (1, 'Den neuen Export auf dem Tablet öffnen und die betroffene Stelle prüfen.', 'Erst die Prüfung des neuen Exports bestätigt die Korrektur.'),
         (0, 'Die alte Endfassung abgeben, weil die Arbeitsdatei den Nachweis enthält.', 'Lesende der Endfassung könnten den Nachweis weiterhin nicht prüfen.'),
         (0, 'Die Quellenangabe streichen, damit die abgeschnittene Stelle verschwindet.', 'Das beseitigt den Fehler optisch, aber verliert den Nachweis.'),
         (0, 'Die Lesbarkeit ausschließlich am größeren Bearbeitungsbildschirm beurteilen.', 'Das erklärt nicht die Lesbarkeit auf dem vorgesehenen Tablet.'),
         (0, 'Eine zusätzliche Animation statt einer lesbaren Quellenangabe ergänzen.', 'Die Animation löst das Problem des fehlenden Nachweises nicht.')]),
]


def rotate_options(pairs, seed):
    pairs = list(pairs)
    random.Random(seed).shuffle(pairs)
    return ([p[1] for p in pairs], [i for i, p in enumerate(pairs) if p[0]],
            [p[2] for p in pairs])


def material_excerpt(source, i):
    mat = source['materials'][i % len(source['materials'])]
    blocks = mat['text'].split('\n\n')
    substantive = [b for b in blocks if len(b) >= 100]
    # Complete paragraph, never clip the last sentence or invent a quotation.
    excerpt = substantive[min(1, len(substantive) - 1)] if substantive else mat['text']
    return mat, excerpt


def base_question(source, id, c, level, title, scene, ask, pairs, why, hint, refs):
    opts, answer, feedback = rotate_options(pairs, int(source['id'].replace('.', '')) * 100 + id)
    return {'id': id, 'c': c, 'l': level, 'type': 'multi', 'title': title, 'scene': scene,
            'ask': ask, 'options': opts, 'answer': answer, 'optionFeedback': feedback,
            'why': why, 'hint': hint,
            'steps': 'Lies die Situation. Prüfe jede der sechs Aussagen einzeln am Material und an den genannten Kriterien. Wähle alle zutreffenden Aussagen.',
            'example': 'Eine belegte Beobachtung und eine plausible Vermutung können nebeneinanderstehen. Die Vermutung wird dadurch noch nicht zur belegten Tatsache.',
            'caseLabel': f"LS {source['id']} · {source['title']}",
            'criteria': 'Eine oder mehrere Antworten sind richtig. Wähle alle zutreffenden Aussagen.',
            'sourceRefs': refs}


def make_bank(source, topics):
    bank = []
    # Reuse all three authoritative source checks; add one true and one plausible
    # false thematic conclusion and change the stem so all six statements fit.
    for i, quiz in enumerate(source['quiz']):
        topic, t1, t2, f1, f2 = topics[i]
        pairs = [(o['value'] == quiz['correct'], o['label'], o['feedback']) for o in quiz['options']]
        pairs += [(1, t1, f'Fachlicher Prüfschritt zu „{topic}“: {t2}'),
                  (0, f1, f'Diese Verallgemeinerung trägt nicht: {t1} {t2}')]
        bank.append(base_question(source, len(bank), 0, 1, f'Fall verstehen · {i+1}',
            f"Ausgangsfall: LS {source['id']} · {source['title']}. Öffne bei Bedarf die vollständige Handlungssituation über „Fall und Materialien“.\n\nLeitfrage aus dem Ausgangspaket: {quiz['question']}",
            'Welche Fallangaben und fachlichen Schlussfolgerungen treffen zu?', pairs,
            next(o['feedback'] for o in quiz['options'] if o['value'] == quiz['correct']) + ' ' + t1,
            quiz['hint'], ['Handlungssituation', source['materials'][i % len(source['materials'])]['key']]))
    # One additional orientation question plus four distinct application questions.
    for level, indexes in [(1, [3]), (2, range(4))]:
        for i in indexes:
            topic, t1, t2, f1, f2 = topics[i]
            neighbor, nt1, nt2, nf1, nf2 = topics[(i+1) % 4]
            mat, excerpt = material_excerpt(source, i)
            pairs = [(1,t1,t2),(1,t2,t1),(0,f1,t1),(0,f2,t2),(1,nt1,nt2),(0,nf1,nt1)]
            scene = f"Originalmaterial: {mat['title']}\n\n{excerpt}\n\n" + (
                f'Übungsvariante: Für das Handlungsergebnis prüft ihr Aussagen zu „{topic}“ und „{neighbor}“. Eine erste Fassung vermischt belegte Angaben und weitergehende Schlüsse.'
                if level == 2 else f'Ordne die fachlichen Grundsätze zu „{topic}“ und „{neighbor}“ dem Fall zu.')
            bank.append(base_question(source, len(bank), 0, level, topic, scene,
                f'Welche Aussagen zu „{topic}“ und „{neighbor}“ sind fachlich tragfähig?', pairs,
                f'{t1} {t2} {nt1}',
                'Trenne belegte Information, mögliche Erklärung und zu weit gehende Behauptung. Nutze die Originalmaterialien.', [mat['key']]))
        for level_in_spec, c, title, variation, ask, pairs in COMPETENCE_ITEMS:
            if level_in_spec != level:
                continue
            i = (c + (1 if 'Eigenen' in title or 'Beteiligung' in title or 'Vergleich' in title or 'Export' in title else 0)) % 4
            topic = topics[i][0]
            mat, excerpt = material_excerpt(source, i)
            scene = f"Originalmaterial: {mat['title']}\n\n{excerpt}\n\nÜbungsvariante: " + variation.format(topic=topic)
            positives = [p[2] for p in pairs if p[0]]
            bank.append(base_question(source, len(bank), c, level, title, scene, ask, pairs,
                ' '.join(positives),
                f'Prüfe deinen Entscheidungsweg mit dieser Kompetenz: {source["competencies"][c]["statement"]}', [mat['key']]))
    assert len(bank) == 24
    bank.extend(story_bank(source, topics))
    return bank


ROLES = ['Belegweg', 'Beteiligungsweg', 'Rahmenweg']
LOGIC_MAP = [0, 1, 2, 0, 1, 2]


def story_bank(source, topics):
    product = re.search(r'„([^“]+)“', source['competencies'][0]['statement'])
    product = product[1] if product else source['title']
    topic = topics[0][0]
    # Six genuine, distinct actions. A/D, B/E, C/F each carry the same protected
    # strategic role; links assess coherent continuation, not isolated correctness.
    chapters = [
        (0, 'Einen Arbeitsweg wählen',
         f'Für „{product}“ braucht ihr eine begründete Entscheidung. Wählt einen Schwerpunkt für euren Arbeitsweg. Alle drei Perspektiven bleiben notwendig; der Schwerpunkt bestimmt, wie ihr eure Begründung aufbaut.',
         'Womit beginnst du den Entscheidungsweg?', [
             f'Du stellst die Fallbelege zu „{topic}“ gegenüber und leitest daraus eine erste Prüffrage ab.',
             'Du sammelst die dokumentierten Sichtweisen und klärst, welche Perspektive noch fehlt.',
             'Du klärst die dokumentierten Zuständigkeiten und begrenzenden Bedingungen vor der Planung.',
             'Du ordnest zwei Aussagen aus dem Material nach Beleg und Deutung und prüfst ihre Reichweite.',
             'Du stellst Fragen der Beteiligten nebeneinander und bestimmst einen Punkt für gemeinsame Klärung.',
             'Du listest vorhandene Mittel und noch offene Freigaben auf und markierst die Grenze eurer Entscheidung.']),
        (3, 'Die Empfehlung aufbauen',
         'Übungsvariante: Ihr sollt zwei Handlungsoptionen in einer knappen Vorlage vergleichen. Eine noch nicht belegte Annahme und eine fehlende Rückmeldung stehen im Entwurf.',
         'Wie baust du den Vergleich passend zu deinem bisherigen Schwerpunkt auf?', [
             'Du vergleichst die Optionen mit Fallbelegen und kennzeichnest die noch ungesicherte Annahme.',
             'Du vergleichst die Optionen aus den dokumentierten Sichtweisen und ergänzt die fehlende Rückfrage.',
             'Du vergleichst die Optionen nach Zuständigkeit und Aufwand und markierst die ungeklärte Bedingung.',
             'Du prüfst je Option eine tragende Aussage am Originalmaterial und ergänzt einen möglichen Gegenbeleg.',
             'Du erstellst je Option eine Rückmeldefrage für Beteiligte und hältst den offenen Einflusszeitpunkt fest.',
             'Du ordnest je Option die erforderliche Entscheidung einer zuständigen Person und einem realistischen Schritt zu.']),
        (0, 'Eine offene Information einarbeiten',
         f'Übungsvariante: Zur Frage „{topics[1][0]}“ liegt jetzt eine zusätzliche Rückfrage vor. Sie bestätigt eure Vermutung noch nicht. Ihr sollt eure vorläufige Empfehlung präzisieren.',
         'Wie arbeitest du die Rückfrage in deinen Weg ein?', [
             'Du prüfst, welche Aussage durch die Rückfrage offenbleibt, und ergänzt eine gezielte Materialprüfung.',
             'Du nutzt die Rückfrage für eine Klärung mit Beteiligten und benennst ihren Einfluss auf die Empfehlung.',
             'Du prüfst, ob die Rückfrage die Machbarkeit verändert, und hältst die nötige Zuständigkeitsklärung fest.',
             'Du kennzeichnest die Reichweite eurer bisherigen Belege und formulierst eine zusätzliche Beobachtungsfrage.',
             'Du vergleichst die Rückfrage mit den schon dokumentierten Sichtweisen und ergänzt einen fehlenden Gesprächspunkt.',
             'Du trennst den schon möglichen Schritt von der noch nicht freigegebenen Entscheidung und passt den Ablauf an.']),
        (4, 'Die digitale Begründung absichern',
         'Übungsvariante: Ein Gruppenmitglied ergänzt eine KI-Antwort im Entwurf. Die dafür genannte Quelle ist noch nicht überprüft. Eure Endfassung muss lesbar und quellenklar bleiben.',
         'Wie sicherst du die Endfassung in deinem bisherigen Arbeitsweg ab?', [
             'Du prüfst die Behauptung am Originalmaterial und korrigierst die Belegübersicht, falls sie dort nicht trägt.',
             'Du kennzeichnest die offene Aussage für das Gespräch und gibst erst nach Quellenprüfung eine begründete Rückmeldung.',
             'Du hältst fest, welcher Planungsschritt von der Quellenprüfung abhängt, und lässt ihn bis zur Klärung offen.',
             'Du trennst Zitat und eigene Deutung im Export und zeigst, welcher Beleg die Empfehlung tatsächlich trägt.',
             'Du machst die geprüften Informationen für Beteiligte lesbar und dokumentierst, welche Rückfrage unbeantwortet bleibt.',
             'Du kontrollierst die Quelle für die benötigte Entscheidung und ordnest ihre Prüfung dem verantwortlichen Schritt zu.']),
        (1, 'Unter Zeitdruck priorisieren',
         f'Übungsvariante: Für die Vorstellung von „{product}“ bleiben euch drei Minuten. Der Fallbezug und ein konkreter nächster Schritt müssen trotzdem erkennbar sein.',
         'Wie verdichtest du den bisher aufgebauten Weg?', [
             'Du behältst den stärksten Fallbeleg, seine Begrenzung und die daraus abgeleitete Empfehlung im Kurzbericht.',
             'Du behältst eine zentrale Sichtweise, die noch offene Rückfrage und den vereinbarten Rückmeldeschritt.',
             'Du behältst die zentrale Rahmenbedingung, die geklärte Zuständigkeit und den machbaren nächsten Schritt.',
             'Du zeigst einen kurzen Vergleich zweier Optionen und begründest die Auswahl mit dem entscheidenden Beleg.',
             'Du stellst den Einfluss eines Beteiligtenbeitrags auf die Entscheidung dar und erklärst den weiteren Umgang damit.',
             'Du zeigst einen knappen Ablauf mit benötigtem Mittel, verantwortlicher Person und überprüfbarem Ziel.']),
        (2, 'Die Endfassung empfehlen',
         f'Übungsvariante: Die Gruppe soll „{product}“ jetzt als vorläufige Empfehlung weitergeben. Die noch offenen Punkte müssen kenntlich bleiben.',
         'Welche Endfassung führt deinen bisherigen Arbeitsweg schlüssig zu Ende?', [
             'Du empfiehlst die belegorientierte Fassung mit Fallnachweisen, ihren Grenzen und einer konkreten weiteren Prüfung.',
             'Du empfiehlst die beteiligungsorientierte Fassung mit Sichtweisen, offenem Klärungspunkt und Rückmeldevereinbarung.',
             'Du empfiehlst die rahmenorientierte Fassung mit Zuständigkeiten, Bedingungen und einem realistischen nächsten Schritt.',
             'Du empfiehlst den begründeten Optionenvergleich, der die Auswahl am Material und an einem Gegenbeleg nachvollziehbar macht.',
             'Du empfiehlst den Gesprächsplan, der Beiträge zur Entscheidung zuordnet und die Rückmeldung an Beteiligte absichert.',
             'Du empfiehlst den Ablaufplan, der verantwortliche Entscheidungen, vorhandene Mittel und die spätere Überprüfung verbindet.']),
    ]
    result = []
    for i, (c, title, scene, ask, options) in enumerate(chapters):
        mat, excerpt = material_excerpt(source, i)
        consequence = [
            f'Variante {j+1}: Dein {ROLES[r]} führt mit dieser Entscheidung weiter. '
            + ['Die tragenden Aussagen bleiben am Material überprüfbar.',
               'Sichtweisen und Rückmeldungen bleiben in der Entscheidung erkennbar.',
               'Bedingungen und Zuständigkeiten bleiben im nächsten Schritt sichtbar.'][r]
            for j, r in enumerate(LOGIC_MAP)]
        q = {'id':24+i,'c':c,'l':3,'type':'story','storyIndex':i,'title':title,
             'scene': f"Ausgangsmaterial: {mat['title']}\n\n{excerpt}\n\n{scene}",
             'ask':ask,'options':options,'consequences':consequence,
             'logicMap':LOGIC_MAP,'logicRoles':[ROLES[r] for r in LOGIC_MAP],
             'why':'Alle angebotenen Handlungen können für sich fachlich sinnvoll sein. Die Rückmeldung bewertet, ob die Schwerpunkte deiner sechs Entscheidungen zusammenpassen.',
             'hint':'Beziehe dich auf deinen bisherigen Schwerpunkt und die neue Information.',
             'steps':'Vorherige Entscheidung ansehen → neue Bedingung prüfen → eine passende Handlung wählen.',
             'example':'Eine zweite Variante desselben Arbeitswegs kann deinen Schwerpunkt ebenso gut weiterführen wie die erste Variante.',
             'caseLabel':f"LS {source['id']} · {source['title']} · zusammenhängender Transfer",
             'criteria':'Wähle genau eine Handlung. Mehrere Gesamtwege sind möglich; ausgewertet wird die ganze Entscheidungskette.',
             'sourceRefs':[mat['key']]}
        if i:
            q['branchFrom'] = q['id']-1
            q['branchText'] = [f'Dein bisheriger Schwerpunkt: {ROLES[r]}. Prüfe, wie die neue Handlung daran anschließt.' for r in LOGIC_MAP]
        result.append(q)
    return result


def transfer_rules():
    links = [(0,1,1,.78),(0,2,1.1,.72),(1,3,1,.84),(2,4,1.3,.72),(3,4,1,.82),(4,5,1.8,.35)]
    return [{'id':f'r{i+1:02}','label':f'Kapitel {a+1} ↔ Kapitel {b+1}',
             'kind':'matrix','steps':[a,b],'weight':weight,
             'matrix':[[1 if a==b else cross for b in range(3)] for a in range(3)],
             'good':'Die spätere Entscheidung führt den zuvor gewählten Schwerpunkt nachvollziehbar weiter.',
             'issue':'Zwischen diesen Entscheidungen wechselt der Schwerpunkt; die Verbindung bleibt im gewählten Weg offen.',
             'next':'Prüfe, ob die neue Handlung denselben Schwerpunkt fortführt. Ein fachlich begründeter Wechsel müsste in einer vertieften Fallbesprechung erklärt werden.'}
            for i,(a,b,weight,cross) in enumerate(links)]


def generated_engine():
    engine = (BLUEPRINT / 'engine.js').read_text()
    old = "const n=this.plan(3).length,answers=Array.from({length:n},(_,i)=>Number(s.storyAnswers[i]));if(answers.some(x=>!Number.isInteger(x)||x<0||x>2))return null;"
    new = "const n=this.plan(3).length,choices=Array.from({length:n},(_,i)=>s.storyAnswers[i]);if(choices.some((x,i)=>!Number.isInteger(x)||x<0||x>=BANK[this.plan(3)[i]].options.length))return null;const answers=choices.map((a,i)=>BANK[this.plan(3)[i]].logicMap?.[a]??a);"
    assert old in engine
    engine = engine.replace(old,new).replace("const ways=['Prozessweg','Rollenweg','Systemweg'];", 'const ways='+J(ROLES)+';')
    engine = engine.replace('→ Unternehmen ${ways[answers[2]]}', '→ Präzisierung ${ways[answers[2]]}')
    engine = engine.replace('choice:q.options[a],consequence:q.consequences[a],role:q.logicRoles?.[a]',
                            'choice:q.options[choices[i]],consequence:q.consequences[choices[i]],role:q.logicRoles?.[choices[i]]')
    engine = engine.replace('Global Bike BFSdual LF01 PROTOTYP30', 'Sozialpädagogik · eigenständige Lernpfadübung')
    return engine


def generated_teacher():
    teacher = (BLUEPRINT / 'teacher.js').read_text()
    teacher = teacher.replace("const DRAFT_KEY='bbs1-scorm-editor-bfsdual-globalbike-lf01-v2'", "const DRAFT_KEY='bbs1-editor-'+PACKAGE.id+'-v1'")
    teacher = teacher.replace('Lernpfadübung · Duales System verstehen', '${E(PACKAGE.title)}')
    teacher = teacher.replace('z. B. Aufgabe 5 oder Berufsschule', 'z. B. Aufgabe 5 oder Fallanalyse')
    teacher = teacher.replace('Formuliere drei echte Entscheidungsalternativen.', 'Formuliere sechs echte Entscheidungsalternativen; je zwei führen denselben geschützten Arbeitsweg fort.')
    teacher = teacher.replace('q.options.length!==3', 'q.options.length!==6').replace('q.consequences.length!==3', 'q.consequences.length!==6').replace('q.logicRoles.length!==3', 'q.logicRoles.length!==6')
    teacher = teacher.replace('genau drei ausgefüllte', 'genau sechs ausgefüllte')
    # Strong option-length variation is a quality advisory, not a broken answer
    # key. Do not pad short, correct statements just to pass a numerical heuristic.
    teacher = teacher.replace("if(lengthTrap(q.options))e.push('Antwortlängen sind stark unterschiedlich – eine Option könnte auffallen')", '')
    teacher = teacher.replace("if(lengthTrap(q.options))e.push('Antwortlängen sind stark unterschiedlich – Lösung könnte erkennbar sein');", '')
    teacher = teacher.replace("else if(q.type==='single'||q.type==='multi'){", "else if(q.type==='single'||q.type==='multi'){if(q.options.length!==6)e.push('Genau sechs Antwortmöglichkeiten benötigt');")
    teacher = teacher.replace("e.push('Richtige Mehrfachauswahl fehlt')", "e.push('Richtige Mehrfachauswahl fehlt');if(q.type==='multi'&&Array.isArray(q.answer)&&(new Set(q.answer).size!==q.answer.length||q.answer.some(a=>!Number.isInteger(a)||a<0||a>=6)))e.push('Ungültiger Antwortschlüssel')")
    teacher = teacher.replace("if(!Array.isArray(q.logicRoles)||q.logicRoles.length!==6)e.push('Geschützte Entscheidungsrollen fehlen');", "if(!Array.isArray(q.logicRoles)||q.logicRoles.length!==6||JSON.stringify(q.logicMap)!=='[0,1,2,0,1,2]')e.push('Geschützte Entscheidungsrollen fehlen');")
    teacher = teacher.replace("el.textContent=errors.length?errors.join(' · '):'Aufgabe vollständig. Die Gesamtstruktur wird beim Export zusätzlich geprüft.';",
        "el.textContent=errors.length?errors.join(' · '):'Aufgabe vollständig. Die Gesamtstruktur wird beim Export zusätzlich geprüft.'+(lengthTrap(BANK[current].options)?' Hinweis: Antwortlängen prüfen; keine künstliche Verlängerung.':'');")
    teacher = teacher.replace("return 'const COMP='", "return 'const PACKAGE='+JSON.stringify(PACKAGE)+';\\nconst COMP='")
    teacher = teacher.replace("'assets/global-bike.svg',", "'source-data.js','source-reader.js','source-reader.css',")
    teacher = teacher.replace("a.download='01_Duales_System_verstehen_bearbeitet.zip'", "a.download=PACKAGE.id+'_bearbeitet_SCORM12.zip'")
    # Option-level explanations are refreshed through the editable overall
    # explanation rather than retaining stale detailed feedback after edits.
    teacher = teacher.replace("function mark(){changed.add(current);", "function mark(){if(BANK[current].optionFeedback)delete BANK[current].optionFeedback;changed.add(current);")
    return teacher


READER_JS = r"""(function(){
'use strict';
const e=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const dialog=document.createElement('dialog');dialog.id='sourceReader';
dialog.innerHTML='<div class="source-top"><h2>Fall und Materialien</h2><button type="button" id="sourceClose" aria-label="Materialansicht schließen">Schließen</button></div><label for="sourceSelect">Material auswählen</label><select id="sourceSelect"></select><article id="sourceText"></article>';
document.body.appendChild(dialog);
const materials=[{key:'Handlungssituation',title:'Handlungssituation',text:SOURCES.case},...SOURCES.materials];
const select=dialog.querySelector('select');select.innerHTML=materials.map((m,i)=>`<option value="${i}">${e(m.title)}</option>`).join('');
function show(){const m=materials[Number(select.value)];dialog.querySelector('article').innerHTML=`<h3>${e(m.title)}</h3>`+m.text.split(/\n\n+/).map(p=>`<p>${e(p)}</p>`).join('')+(m.links?.length?'<h4>Originalquellen aus dem Material</h4><ul>'+m.links.map(l=>`<li><a href="${e(l.url)}" target="_blank" rel="noopener noreferrer">${e(l.label)}</a></li>`).join('')+'</ul>':'');dialog.scrollTop=0;}
select.onchange=show;dialog.querySelector('#sourceClose').onclick=()=>dialog.close();
document.addEventListener('click',event=>{if(!event.target.closest('[data-open-sources]'))return;select.value='0';show();dialog.showModal();});
})();
"""
READER_CSS = """.chrome-sticky .header{grid-template-columns:minmax(0,1fr) 180px;gap:20px;padding:14px 20px}.chrome-sticky .titlewrap{min-width:0}.chrome-sticky .title{font-size:clamp(19px,2.3vw,25px);line-height:1.25;margin:0 0 5px}.chrome-sticky .school{width:180px}.chrome-sticky .school img{width:180px;max-width:100%;height:auto}.chrome-sticky .meta{font-size:11px;line-height:1.5}.source-actions{margin:12px 0}.source-actions button{font-size:.9rem}#sourceReader{width:min(900px,calc(100% - 24px));max-height:90vh;box-sizing:border-box;border:1px solid #9bd9ee;border-radius:16px;padding:20px;color:#20313e;background:#fff}#sourceReader::backdrop{background:rgba(16,42,61,.55)}.source-top{display:flex;align-items:center;justify-content:space-between;gap:12px;position:sticky;top:-20px;background:#fff;padding:10px 0}.source-top h2{margin:0;font-size:1.25rem}#sourceText{line-height:1.65;overflow-wrap:anywhere}#sourceSelect{width:100%;margin:8px 0;padding:10px}.option-explanation{margin:10px 0}.option-explanation ul{padding-left:20px}.option-explanation li{margin:10px 0}@media(max-width:680px){.chrome-sticky .header{grid-template-columns:minmax(0,1fr) 100px;gap:10px;padding:12px}.chrome-sticky .school,.chrome-sticky .school img{width:100px}.chrome-sticky .title{font-size:18px}.chrome-sticky .meta{font-size:10px}}@media(max-width:480px){#sourceReader{padding:12px}.source-top{top:-12px}}"""
READER_CSS += '.teacher-overlay .teacher-primary:hover{background:#0f2f55;color:#fff;border-color:#0f2f55}'


def generated_app():
    app = (BLUEPRINT / 'app.js').read_text()
    app = app.replace("'globalbike-bfsdual-01_duales_system_verstehen-v1'", "PACKAGE.id+'-learner-v1'")
    app = app.replace('Lernpfadübung | Duales System verstehen · Global Bike · BFS dual', '${esc(PACKAGE.title)} · Sozialpädagogik')
    app = app.replace('Lernpfadübung | Duales System verstehen', '${esc(PACKAGE.title)}')
    app = app.replace('Global-Bike-Fall', 'Fall der Sozialpädagogik')
    app = app.replace("a.download='01_Duales_System_verstehen_Lernbericht.html'", "a.download=PACKAGE.id+'_Lernbericht.html'")
    app = app.replace('Prüfe noch einmal: Betrieb, Schule, Unternehmen und deine Rolle.', 'Prüfe den Fallbezug und die fachliche Begründung deiner Empfehlung.')
    needle = '<form id="form">${inputHTML(q)}'
    assert needle in app
    app = app.replace(needle, '<div class="source-actions"><button class="secondary" type="button" data-open-sources>Fall und Materialien</button></div><form id="form">${inputHTML(q)}')
    needle = '<p><b>Lösung:</b> ${esc(correctText(q))}</p>'
    app = app.replace(needle, needle + '${q.optionFeedback?`<details class="option-explanation"><summary>Alle sechs Aussagen erklärt</summary><ul>${q.options.map((o,i)=>`<li><b>${q.answer.includes(i)?"Zutreffend":"Nicht zutreffend"}:</b> ${esc(o)}<br>${esc(q.optionFeedback[i])}</li>`).join("")}</ul></details>`:""}')
    return app


def write_manifest(folder, package):
    ims='http://www.imsproject.org/xsd/imscp_rootv1p1p2'
    adl='http://www.adlnet.org/xsd/adlcp_rootv1p2'
    ET.register_namespace('',ims);ET.register_namespace('adlcp',adl)
    root=ET.Element(f'{{{ims}}}manifest',identifier=package['id'],version='1.0')
    def node(parent,name,text=None,**attrs):
        child=ET.SubElement(parent,f'{{{ims}}}{name}',attrs)
        child.text=text
        return child
    meta=node(root,'metadata');node(meta,'schema','ADL SCORM');node(meta,'schemaversion','1.2')
    orgs=node(root,'organizations',default='ORG');org=node(orgs,'organization',identifier='ORG');node(org,'title',package['title'])
    item=node(org,'item',identifier='TRAINING',identifierref='RES');node(item,'title',package['title'])
    res=node(node(root,'resources'),'resource',identifier='RES',type='webcontent',href='index.html')
    res.set(f'{{{adl}}}scormtype','sco')
    for path in sorted(folder.rglob('*')):
        if path.is_file() and path.name!='imsmanifest.xml':
            node(res,'file',href=path.relative_to(folder).as_posix())
    ET.ElementTree(root).write(folder/'imsmanifest.xml',encoding='utf-8',xml_declaration=True)


def make_package(source, topics):
    id = 'SozPaed_Lernpfad_LS'+source['id'].replace('.', '_')
    folder = ROOT / ('LS'+source['id'].replace('.', '_'))
    folder.mkdir(exist_ok=True)
    (folder/'assets').mkdir(exist_ok=True)
    for filename in ['style.css','teacher-template.css','progress.js','teacher-config.js','jszip.min.js']:
        shutil.copyfile(BLUEPRINT/filename,folder/filename)
    for filename in ['bbs.svg','teacher-bbs1-aurich.svg']:
        shutil.copyfile(BLUEPRINT/'assets'/filename,folder/'assets'/filename)
    package = {'id':id,'ls':source['id'],'title':f"Lernpfadübung · LS {source['id']} · {source['title']}",
               'version':'1.0','source':source['provenance']['source']}
    bank = make_bank(source,topics)
    comp = [[c['label'],c['statement']] for c in source['competencies']]
    plan = {str(l):[q['id'] for q in bank if q['l']==l] for l in [1,2,3]}
    data = '\n'.join('const '+name+'='+J(value)+';' for name,value in [
        ('PACKAGE',package),('COMP',comp),('BANK',bank),('CORE_PLAN',plan),('TRANSFER_RULES',transfer_rules())])+'\n'
    (folder/'data.js').write_text(data)
    for name,content in [('engine.js',generated_engine()),('app.js',generated_app()),
                         ('teacher.js',generated_teacher()),('source-reader.js',READER_JS),('source-reader.css',READER_CSS)]:
        (folder/name).write_text(content)
    (folder/'source-data.js').write_text('const SOURCES='+J({'case':source['case'],'materials':source['materials'],'provenance':source['provenance']})+';\n')
    index = (BLUEPRINT/'index.html').read_text()
    index = index.replace('Lernpfadübung | Duales System verstehen',html.escape(package['title']))
    index = index.replace('BFS dual · Global Bike ·', 'Sozialpädagogik ·')
    index = index.replace('<div class="biocasa"><img src="assets/global-bike.svg" alt="Global Bike Inc."></div>', '')
    index = index.replace('</head>', '<link rel="stylesheet" href="source-reader.css"></head>')
    index = index.replace('<script src="data.js">', '<script src="source-data.js"></script><script src="data.js">')
    index = index.replace('</body>', '<script src="source-reader.js"></script></body>')
    (folder/'index.html').write_text(index)
    teacher_notes=f'''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lehrkraft-Hinweise</title><link rel="stylesheet" href="style.css"><body><main class="shell"><section class="card"><h1>{html.escape(package['title'])}</h1>
<p>Eigenständige Lernpfadübung zur zugehörigen Lernsituation, keine Ersetzung des Ausgangspakets. Quelle: {html.escape(source['provenance']['source'])}.</p>
<ul><li>12 Orientierung, 12 Anwendung, 6 zusammenhängende Transferentscheidungen.</li><li>Alle Aufgaben haben sechs eigenständige Antwortmöglichkeiten. Keine Cloze-, Kurzantwort-, Zuordnungs- oder Sortieraufgaben.</li><li>Orientierung und Anwendung: eine oder mehrere Antworten sind richtig. Vollständige Auswahl gibt volle Punkte; falsche zusätzliche Auswahl reduziert Teilpunkte wie in der Blaupause.</li><li>Stufenaufstieg ab 66 %; andernfalls Festigungsrunde. Hilfen und Kompetenznachweise werden gespeichert.</li><li>Transfer: sechs Einfachauswahl-Entscheidungen, je zwei Varianten für Beleg-, Beteiligungs- und Rahmenweg. Die geschützte Zuordnung [0,1,2,0,1,2] bewahrt die drei Rollen des Entscheidungsnetzes. Bewertet wird die Konsistenz der Schwerpunkte, kein isoliertes richtig/falsch und keine frei formulierte Begründung.</li><li>Die fünf Kompetenzbeschreibungen stammen aus der originalen Lernsituation. Eigene Übungsvarianten sind ausdrücklich gekennzeichnet.</li><li>Die vollständige Textfassung von Fall und Materialien ist in der Übung verfügbar. Abbildungen aus dem Ausgangspaket werden hier nicht benötigt und nicht mitgeliefert.</li></ul>
<h2>Lehrkräfte-Editor</h2><p>PIN und Stil stammen aus der Lernpfad-Blaupause. Aufgaben, Lösungen, Erklärungen und Hilfen bearbeiten; Entwurf speichern; aktuelle Fassung als neues SCORM exportieren. Entscheidungsrollen bleiben geschützt. Antwortlängen sind ein Qualitätshinweis; keine Antwort künstlich verlängern. Bei Änderungen werden optionenbezogene Erklärungen entfernt: die editierbare fachliche Gesamterklärung bleibt maßgeblich.</p>
<h2>Moodle</h2><p>Die einzelne ZIP-Datei als SCORM 1.2 hinzufügen. Jede Übung besitzt einen eigenen Paketbezeichner und Browserspeicher. Resume führt fort, ab-initio startet neu. GitHub aktualisiert Moodle nicht automatisch. Die Paketfassung ist lokal mit einer SCORM-API-Simulation geprüft; ein echter Moodle-/iPad-Test steht vor dem Unterrichtseinsatz noch aus.</p></section></main></body></html>'''
    (folder/'LEHRKRAFT-HINWEISE.html').write_text(teacher_notes)
    report=ROOT/'PRUEFBERICHT.md'
    (folder/'TESTPROTOKOLL.txt').write_text(report.read_text() if report.exists() else 'Prüfung noch ausstehend.\nSCORM 1.2, 30 Aufgaben, sechs Optionen, 12/12/6.\n')
    write_manifest(folder,package)
    return package,folder,bank


def archive(folder, destination):
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                # Fixed metadata makes rebuilds deterministic.
                info=zipfile.ZipInfo(path.relative_to(folder).as_posix(),(2026,10,8,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644 << 16
                z.writestr(info,path.read_bytes(),compresslevel=9)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--import-inventory');args=parser.parse_args()
    if args.import_inventory:import_sources(args.import_inventory)
    topics={}
    for line in (ROOT/'tools/fachliche_bausteine.txt').read_text().splitlines():
        if not line or line.startswith('#'):continue
        id,*parts=line.split('|');assert len(parts)==5,line
        topics.setdefault(id,[]).append(parts)
    sources=[json.loads(p.read_text()) for p in (ROOT/'quellen').glob('*.json')]
    sources.sort(key=lambda s:tuple(map(int,s['id'].split('.'))))
    assert len(sources)==30 and len(topics)==30
    downloads=ROOT/'Downloads';downloads.mkdir(exist_ok=True)
    entries=[]
    for source in sources:
        assert len(topics[source['id']])==4 and len(source['quiz'])==3
        package,folder,bank=make_package(source,topics[source['id']])
        for q in bank:
            assert len(q['options'])==6 and len(set(q['options']))==6
            assert q['type'] in ('multi','story')
            if q['type']=='multi':assert q['answer'] and all(0<=i<6 for i in q['answer'])
        zip_name=package['id']+'_SCORM12.zip'
        archive(folder,downloads/zip_name)
        entries.append({'ls':source['id'],'title':source['title'],'folder':folder.name,'zip':zip_name,'tasks':30})
    (ROOT/'bestand.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
    rows=''.join(f'<tr><td>LS {e["ls"]}</td><td>{html.escape(e["title"])}</td><td><a href="{e["folder"]}/index.html">Vorschau</a></td><td><a download href="Downloads/{e["zip"]}">SCORM-ZIP</a></td></tr>' for e in entries)
    (ROOT/'index.html').write_text(f'''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>30 Lernpfadübungen · Sozialpädagogik</title><style>body{{font:16px/1.5 'Segoe UI',sans-serif;margin:0;color:#173a63;background:#f6fafc}}main{{max-width:1000px;margin:auto;padding:24px}}h1{{border-bottom:5px solid #afca0b;padding-bottom:16px}}a{{color:#006a9d}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #d9e6eb}}.table{{overflow:auto}}.download{{display:inline-block;background:#173a63;color:white;border-radius:10px;padding:12px 18px}}</style><main><h1>30 Lernpfadübungen · Sozialpädagogik</h1><p>Je 30 Aufgaben · sechs Antwortmöglichkeiten · ohne Lückentexte · SCORM 1.2</p><p><a class="download" download href="Downloads/Sozialpaedagogik_30_Lernpfaduebungen_SCORM12.zip">Alle 30 Pakete herunterladen</a></p><p>Gesamt-ZIP entpacken; in Moodle jeweils die einzelne SCORM-ZIP verwenden. Vorschauen speichern nur in diesem Browser.</p><div class="table"><table><thead><tr><th>Situation</th><th>Lernpfadübung</th><th>Öffnen</th><th>Download</th></tr></thead><tbody>{rows}</tbody></table></div></main></html>''')
    readme='''# Sozialpädagogik · 30 Lernpfadübungen

Eigenständige SCORM-1.2-Übungen zu allen 30 Ausgangssituationen.
Je 12 Orientierung + 12 Anwendung + 6 verknüpfte Transferentscheidungen,
immer sechs Antwortmöglichkeiten, keine Cloze-Aufgaben.

Orientierung und Anwendung erlauben eine oder mehrere richtige Antworten.
Im Transfer wird pro Kapitel eine Handlung ausgewählt; das geschützte Netz
bewertet die ganze Entscheidungskette. Zwei Varianten je Schwerpunkt bewahren
die drei Entscheidungsrollen der Blaupause. Der 66-%-Aufstieg, Festigungsrunden,
Hilfen, Selbsteinschätzung und SCORM-Tracking bleiben erhalten.

**Download:** `Downloads/Sozialpaedagogik_30_Lernpfaduebungen_SCORM12.zip`.
Die Gesamt-ZIP entpacken und in Moodle die gewünschte einzelne ZIP auswählen.
Die Gesamt-ZIP selbst ist kein einzelnes SCORM-Paket.

**Vorschau:** `index.html` über einen Webserver öffnen; außerhalb von Moodle
steht ausdrücklich Browser-Speicherung. Lehrkräfte-Editor: Stil und PIN aus
der Lernpfad-Blaupause, Entwürfe je Übung getrennt, validierter SCORM-Export.

**Quellen:** `quellen/LS*.json` enthält nachvollziehbare Text-Snapshots der
hochgeladenen Lernsituationen und deren SHA-256-Herkunftsnachweise.
LS1.1 stammt aus der vorhandenen Sozialpädagogik-Vorlage. Fallfragen wurden
aus den Ausgangspaketen übernommen und um passende fachliche Aussagen ergänzt.
Weitere Fragen verwenden Falltexte und die fünf originalen Kompetenzen;
erfundene Veränderungen heißen ausdrücklich „Übungsvariante“.

**Erstellung:** `python Lernpfaduebungen/Sozialpaedagogik/tools/build.py`.
Fachliche Eingaben: `tools/fachliche_bausteine.txt`; Kompetenz- und Transferfragen
im Generator. Die Ausgangs-Lernsituationen werden nicht verändert.
Prüfungen: `tools/verify.py`, Ergebnisse in `PRUEFBERICHT.md`.

**Google Drive:** Der Upload ist gewünscht und autorisiert, aber in dieser Sitzung
steht kein Drive-Upload-Werkzeug zur Verfügung. Diese Dateien sind deshalb
zunächst hier und im Repository bereitgestellt; kein Drive-Upload wird behauptet.

'''
    readme+='| LS | Lernpfadübung | Paket |\n|---|---|---|\n'+''.join(f'| {e["ls"]} | {e["title"]} | [ZIP](Downloads/{e["zip"]}) |\n' for e in entries)
    (ROOT/'README.md').write_text(readme)
    with zipfile.ZipFile(downloads/'Sozialpaedagogik_30_Lernpfaduebungen_SCORM12.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for e in entries:z.write(downloads/e['zip'],e['zip'])
        z.writestr('BITTE_ZUERST_LESEN.txt','30 einzelne Lernpfadübungen · Sozialpädagogik · SCORM 1.2\nGesamtarchiv entpacken. In Moodle jeweils eine der 30 inneren ZIP-Dateien als SCORM-Paket verwenden.\nJede Übung: 30 Aufgaben, sechs Antwortmöglichkeiten, keine Lückentexte.\n')
    print(f'Built {len(entries)} SCORM packages; {sum(e["tasks"] for e in entries)} tasks. Total archive: {(downloads/"Sozialpaedagogik_30_Lernpfaduebungen_SCORM12.zip").stat().st_size:,} bytes.')


if __name__=='__main__':main()
