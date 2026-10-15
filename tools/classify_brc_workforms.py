#!/usr/bin/env python3
"""Assign an intentional work form to the actual grouped BioCasa assignments.

This mapping describes cooperation for a whole real assignment, never splitting
checklists/reflection into additional completion items. It preserves source intent:
individual entry, expert exchange, joint decisions, independent external feedback,
and personal reflection. Open ways use explicit recommendations, not extra rules.
"""
import json
import argparse
from collections import Counter
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'Fachbereiche/BRC/LG01/quellen/Arbeitsformen.json');args=parser.parse_args()
INPUT=args.input
OUTPUT=args.output

IND = ('individual', 'Einzelarbeit')
PAIR = ('pair', 'Partnerarbeit')
GROUP = ('group', 'Vierergruppe')
STAMM = ('group', 'Stammgruppe')
EXPERT = ('expert-group', 'Expertengruppe')
PEERS = ('partner-groups', 'Partnergruppen')

# Every information task of the guided ways is reviewed explicitly against source.
INFO = {
 (1,1): [
  (*IND, 'Eigene Problemdiagnose sichert den persönlichen Einstieg vor dem Gruppenaustausch.'),
  (*PAIR, 'Zwei Lernende vergleichen und belegen die Gründerprofile; anschließend fließen die Befunde in die gemeinsame Diagnose.'),
  (*PAIR, 'Kundenbedürfnisse lassen sich zu zweit auswerten und auf Materialbezug gegenprüfen.'),
  (*PAIR, 'Die Zuordnung der Ziele wird im Partnerabgleich fachlich überprüft.'),
  (*GROUP, 'Die vier Interessenperspektiven werden gemeinsam mit Beiträgen und Zielkonflikten abgestimmt.'),
  (*PAIR, 'Betriebsarten und Begründungen werden zu zweit gegenübergestellt und gegengeprüft.'),
  (*GROUP, 'Die Prozesskette verbindet Beiträge zu Einkauf, Produktion, Vertrieb und Zahlung in der Vierergruppe.'),
  (*GROUP, 'Die zweiminütige Problemdiagnose ist eine gemeinsame Sicherung der vier Gruppenmitglieder.'),
 ],
 (1,2): [
  (*IND, 'Die Quelle verlangt zunächst eine persönliche Analyse; die folgenden Pakete werden anschließend abgestimmt.'),
  (*PAIR, 'Gründerprofile und Kundenimpulse können zu zweit ausgewertet und danach in die Vierergruppe eingebracht werden.'),
  (*GROUP, 'Ziele und Stakeholderkonflikte erfordern den gemeinsamen Abgleich mehrerer Perspektiven.'),
  (*PAIR, 'Die Betriebsart und der Prozessvergleich werden im Tandem fachlich gegengeprüft.'),
  (*GROUP, 'Die Problemdiagnose bündelt alle Analysepakete; Strukturhilfen bleiben wählbar.'),
 ],
 (2,1): [
  (*IND, 'Die eigene Diagnose des Entscheidungsproblems und seiner Risiken geht dem Gruppenaustausch voraus.'),
  (*PAIR, 'Voraussetzungen und begründete Mehrfachzuordnungen werden zu zweit abgeglichen.'),
  (*PAIR, 'Standortfragen und Belege werden im Tandem auf Vollständigkeit überprüft.'),
  (*GROUP, 'Kompetenzlücken und Verantwortungen der vier Gründerpersonen werden gemeinsam abgeglichen.'),
  (*GROUP, 'Die Quellenakte wird innerhalb der Vierergruppe arbeitsteilig erschlossen und danach zusammengeführt.'),
  (*PAIR, 'Die drei ungeprüften Quellen werden zu zweit anhand derselben Qualitätsmerkmale gegengeprüft.'),
  (*IND, 'Jede Person erklärt selbst den Zusammenhang von Gründungsfahrplan und Businessplan.'),
  (*GROUP, 'Die gemeinsame Übersicht führt die arbeitsteiligen Ergebnisse mit offiziellen Quellen zusammen.'),
 ],
 (2,2): [
  (*IND, 'Der Einstieg ist in der Quelle ausdrücklich als persönliche Problemanalyse angelegt.'),
  (*PAIR, 'Standortfragen und Zuordnungen werden materialgestützt im Tandem abgeglichen.'),
  (*GROUP, 'Verantwortung und Kompetenzlücken betreffen die vier Gründerrollen und werden gemeinsam bestimmt.'),
  (*GROUP, 'Die Quellenakte wird aufgeteilt; alle vier Beiträge werden im gemeinsamen Ergebnis gesichert.'),
  (*GROUP, 'Die Übersicht und Quellenprüfung sichern die gemeinsame Arbeit; angebotene Hilfen bleiben optional.'),
 ],
 (3,1): [
  (*IND, 'Zunächst wird das Unternehmensproblem eigenständig verstanden, bevor Expertisen verteilt werden.'),
  ('expert-group', 'Expertengruppe · Produkt', 'Die Produktexpertise erschließt alle fünf Konzepte für die spätere Stammgruppe.'),
  ('expert-group', 'Expertengruppe · Markt', 'Die Marktexpertise wertet Kundendaten und Absatzannahmen nachvollziehbar aus.'),
  ('expert-group', 'Expertengruppe · Markt', 'Die Wettbewerbsanalyse ergänzt die Marktexpertise und wird später materialgestützt erklärt.'),
  ('expert-group', 'Expertengruppe · Marketing', 'Die Marketingexpertise prüft die vier Instrumente und ihre Abhängigkeiten.'),
  ('expert-group', 'Expertengruppe · Kapital', 'Die Kapitalexpertise erstellt nachvollziehbare Berechnungen für das gesamte Team.'),
  ('expert-group', 'Expertengruppe · Kapazität', 'Die Kapazitätsexpertise prüft Mengen, Kapazität und Überschuss für die Stammgruppe.'),
  (*STAMM, 'Widerspruchsnotizen verbinden alle Fachkapitel und werden gemeinsam in der Stammgruppe geklärt.'),
  ('expert-group', 'Expertengruppe → Stammgruppe', 'Der Kurzbericht wird in der Expertise vorbereitet und nur nachvollziehbar in die Stammgruppe übernommen.'),
 ],
 (3,2): [
  (*IND, 'Die eigene Sichtung des Bankfähigkeitsproblems ist in der Quelle vor dem Expertenaustausch vorgesehen.'),
  ('expert-group', 'Expertengruppe · Angebot/Markt', 'Das begleitete Fachpaket verbindet Produkt, Kundschaft und Wettbewerb.'),
  ('expert-group', 'Expertengruppe · Marketing', 'Das Fachpaket prüft Marketing und Folgen für Umsetzung und Lieferfähigkeit.'),
  ('expert-group', 'Expertengruppe · Kapital', 'Das Fachpaket verbindet Kapital-, Kapazitätsrechnung und Widerspruchsanalyse.'),
  ('expert-group', 'Expertengruppe → Stammgruppe', 'Jede Expertise erläutert ihren Kurzbericht; die Stammgruppe prüft Nachvollziehbarkeit.'),
 ],
 (4,1): [
  (*IND, 'Die Finanzierungsproblemdiagnose beginnt eigenständig mit Kapitalbedarf, Eigenmitteln und Lücke.'),
  ('expert-group', 'Expertengruppen · Finanzierung', 'Die Finanzierungsformen werden in den vorgesehenen Fachgruppen parallel erschlossen.'),
  ('expert-group', 'Expertengruppe · Darlehen', 'Die Darlehensexpertise erklärt den vollständigen Rechenweg.'),
  ('expert-group', 'Expertengruppe · Kontokorrent', 'Die Kontokorrentexpertise klärt Kosten und verbleibende Rückzahlungsverpflichtung.'),
  ('expert-group', 'Expertengruppe · Leasing', 'Die Leasingexpertise vergleicht Gesamtbetrag, Kaufpreis und Aussagegrenzen.'),
  ('expert-group', 'Expertengruppe · Tragfähigkeit', 'Die Tragfähigkeitsexpertise prüft Plan- und Stressszenario nachvollziehbar.'),
  (*GROUP, 'Der Vergleich der Finanzierungsmixe führt die unterschiedlichen Fachbeiträge zusammen.'),
  ('expert-group', 'Expertengruppe · Fachinformation', 'Jede Expertise vermittelt ihren Fachbeitrag mit sichtbaren Rechenwegen.'),
 ],
 (4,2): [
  (*IND, 'Die eigene Sichtung beginnt mit dem Zusammenhang zwischen Kapitalbedarf, Eigenmitteln und Lücke.'),
  ('expert-group', 'Expertengruppen · Finanzierung', 'Darlehen, Kontokorrent und Leasing werden in den angekündigten Expertisen geprüft.'),
  ('expert-group', 'Expertengruppe · Tragfähigkeit', 'Die Tragfähigkeitsexpertise führt Plan-/Stressrechnung und Vergleich der Kombinationen zusammen.'),
  ('expert-group', 'Expertengruppe · Fachinformation', 'Die fünfminütige Fachinformation sichert nachvollziehbare Rechnungen für alle.'),
 ],
 (5,1): [
  (*IND, 'Der persönliche Einstieg identifiziert Entscheidungsproblem und benötigte Auskünfte.'),
  (*PAIR, 'Gründerinteressen, Beiträge und Rechte werden zu zweit materialgestützt abgeglichen.'),
  (*PAIR, 'Wirtschaftliche Haftungsfolgen der Verpflichtungen werden im Tandem überprüft.'),
  ('expert-group', 'Expertengruppe · Rechtsform', 'Die Quelle verlangt ausdrücklich die arbeitsteilige Erschließung je einer Rechtsform.'),
  (*STAMM, 'Die vier Rechtsformexpertisen werden anhand gemeinsamer Merkmale in der Stammgruppe verglichen.'),
  (*PAIR, 'Die konkreten Haftungsfälle werden anhand derselben Rechtsgrundlagen gegenseitig geprüft.'),
  (*PAIR, 'Gesetzesbelege und korrigierte Chat-Aussagen werden im Partnercheck kontrolliert.'),
  (*GROUP, 'Die formalen Gründungsschritte werden gemeinsam in eine belastbare Folge gebracht.'),
  (*STAMM, 'Die quellenbelegte Vergleichstabelle sichert die Ergebnisse aller Expertisen.'),
 ],
 (5,2): [
  ('individual', 'Einzelarbeit → Vierergruppe', 'Die Quelle sieht Einzelarbeit vor; eigene Interessen- und Risikobefunde werden anschließend in der Vierergruppe abgeglichen.'),
  (*GROUP, 'W2 fordert einen gemeinsamen Rechtsformvergleich; keine verpflichtenden neuen Expertengruppen.'),
  (*PAIR, 'Haftungsfälle und Chatbehauptungen werden zu zweit mit Quellen geprüft und anschließend zurückgemeldet.'),
  (*GROUP, 'Alle vier Mitglieder sichern die Vergleichstabelle und erläutern Geschäftsführung versus Vertretung.'),
 ],
 (6,1): [
  (*IND, 'Jede Person erschließt zuerst die Dokumentenkette und ihre rechtliche Funktion.'),
  ('expert-group', 'Expertengruppe · Vertrag', 'Die Vertragsexpertise prüft den Zeitpunkt und Inhalt des Vertragsschlusses.'),
  ('expert-group', 'Expertengruppe · Vertrag', 'Die Vertragsexpertise hält die endgültig geltenden Vertragsinhalte fest.'),
  ('expert-group', 'Expertengruppe · Vertrag', 'Die Vertragsexpertise überprüft sämtliche Wirksamkeitsvoraussetzungen.'),
  ('expert-group', 'Expertengruppe · Vertrag', 'Die Vertragsexpertise verbindet Hauptpflichten mit betrieblichen Folgen.'),
  ('expert-group', 'Expertengruppe · Zahlung', 'Die Zahlungsexpertise vergleicht die vier Optionen mit nachvollziehbaren Rechnungen.'),
  ('expert-group', 'Expertengruppe · Reklamation', 'Die Reklamationsexpertise bestimmt Mangelart, Menge und Wert.'),
  ('expert-group', 'Expertengruppe · Reklamation', 'Die Reklamationsexpertise prüft Rüge und Käuferrechte mit Rechtsbelegen.'),
  ('expert-group', 'Expertengruppe · Reklamation', 'Die Reklamationsexpertise grenzt gesicherte Ursachen und geeignete Reaktionen ab.'),
  ('expert-group', 'Expertengruppe · Personal', 'Die Personalexpertise vergleicht Stunden, Kosten und Wirkungen der Beschäftigungsformen.'),
  ('expert-group', 'Expertengruppe · Personal', 'Die Personalexpertise prüft den Arbeitsvertragsentwurf anhand der angegebenen Quellen.'),
  ('expert-group', 'Expertengruppe → Stammgruppe', 'Jede Expertise übergibt eine belegte Prüfnotiz und erläutert deren Folgerung für BioCasa.'),
 ],
 (6,2): [
  ('expert-group', 'Einzelarbeit → Expertengruppe', 'Die vier Expertisen sind ausdrücklich vorgesehen; vor dem Austausch wird die Dokumentenkette eigenständig gesichtet.'),
  ('expert-group', 'Expertengruppe · Zahlung', 'Die Zahlungsexpertise rechnet und vergleicht für beide Unternehmensperspektiven.'),
  ('expert-group', 'Expertengruppe · Reklamation', 'Die Reklamationsexpertise prüft Mangel, Rüge, Rechte und Lösungsmöglichkeiten.'),
  ('expert-group', 'Expertengruppe · Personal', 'Die Personalexpertise prüft Beschäftigungsoptionen und Arbeitsvertrag mit Quellen.'),
  ('expert-group', 'Expertengruppe → Stammgruppe', 'Die Expertise übergibt ihre Prüfnotiz; alle Befunde werden vor der Übernahme zusammengeführt.'),
 ],
}

PLAN_W1 = {
 1: [(GROUP, 'Arbeitsplanung'),(PAIR, 'Kriterienentwurf'),(PAIR, 'Zielformulierung'),(PAIR, 'Zielbeziehungen')],
 2: [(GROUP, 'Maßnahmenfolge'),(GROUP, 'Gründerrollen'),(PAIR, 'Erledigungsnachweise'),(GROUP, 'Beratungskriterien')],
 3: [(STAMM, 'Redaktionsplanung'),(PAIR, 'Kapitelabhängigkeiten'),(STAMM, 'Entscheidungskriterien'),(STAMM, 'Dokumentationsregeln')],
 4: [(GROUP, 'Finanzierungskriterien'),(GROUP, 'Pitchrollen'),(PAIR, 'Visualisierung'),(PAIR, 'Rückfragen')],
 5: [(GROUP, 'Kriterien und Gewichte'),(GROUP, 'Entscheidungsablauf'),(GROUP, 'Grenzbedingungen'),(GROUP, 'Beteiligungsmodelle')],
 6: [(STAMM, 'Auftragsplanung'),(PAIR, 'Kundeninformation'),(PAIR, 'Zahlungskriterien'),(PAIR, 'Personalkriterien'),(STAMM, 'Gründerrollen')],
}


def result(kind, label, reason, recommendation=False):
    if recommendation:
        label += ' (Empfehlung)'
        reason += ' Die konkrete Sozialform, Arbeitsteilung und Gruppengröße bleiben im Rahmen des ursprünglichen Auftrags selbst wählbar.'
    return {'kind': kind, 'label': label, 'reason': reason}


def classify(t):
    ls, phase, mode, n, text = t['ls'], t['phase'], t['mode'], t['number'], t['text']
    meta = t['meta'].get('Arbeitsform','')
    open_way = mode in (3,4,5)
    # A whole reflective activity remains personal even when followed by exchange.
    if phase == 'reflektieren':
        return result(*IND, 'Persönliche Urteile, eigene Lernentwicklung und der nächste Lernschritt werden individuell dokumentiert; die vorgesehene anschließende Runde bleibt erhalten.', mode in (3,5))
    # The checklist and revision form one externally checked assignment.
    if phase == 'bewerten':
        if ls == 4:
            return result('partner-groups', 'Finanzierungsgremium ↔ Pitchteam', 'Ein anderes Team prüft als Finanzierungsgremium; das Pitchteam verarbeitet dessen fachliches Feedback. Selbst organisierte Prüf- und Feedbackgestaltung bleiben erhalten.')
        label = {1:'Partnergruppen · Peer-Check',2:'Partnergruppen · Plancheck',3:'Prüfgruppen · Konsistenzcheck',5:'Partnergruppen · Rechtscheck',6:'Auditgruppe ↔ Erstellergruppe'}[ls]
        if mode==5 and ls==1:
            return result('partner-groups', 'Partnergruppen', 'Peer-Feedback ist eine passende Orientierung; laut Ausgangsauftrag bleiben eigener Kriteriencheck, Probe-Termin oder deren Kombination wählbar.', True)
        return result('partner-groups', label, 'Eine unabhängige Gegengruppe prüft das vollständige Produkt; die Erstellergruppe entscheidet begründet über Feedback und überarbeitet anschließend.')
    if phase == 'informieren':
        if (ls,mode) in INFO:
            sequence=INFO[(ls,mode)]
            assert 1 <= n <= len(sequence), (t['key'],len(sequence))
            return result(*sequence[n-1])
        # Open paths: recommend an own entry, cooperative expertise and joint synthesis.
        if n==1:
            return result(*IND, 'Der eigene Erstzugang zur Ausgangslage sichert ein persönliches Problemverständnis, bevor Untersuchung und Kooperation organisiert werden.', True)
        if any(s in text for s in ('Checkpoint A:', 'Meilenstein 1:')):
            return result('group', 'Gruppenarbeit', 'Der gemeinsame Zwischenstand wird erklärt und auf Nachvollziehbarkeit geprüft.', True)
        if mode==3 and ls==1 and n==3:
            return result('group','Gruppenarbeit','Die Materialaufteilung und Ergebnissicherung erfordern gemeinsame Absprachen.', True)
        if mode==3 and ls==1 and n==2:
            return result('group','Gruppenarbeit','Die fachlichen Pflichtbereiche werden gemeinsam auf belastbare Aussagen geprüft.', True)
        if ls in (3,4,5,6):
            if ls==3 and mode==3 and n==3:
                return result(*PAIR, 'Daten und Annahmen können im Tandem systematisch gegengeprüft werden.', True)
            if ls==5 and mode==3 and n==3:
                return result(*PAIR, 'Kritische Rechtsbehauptungen werden anhand der Quellen gegenseitig überprüft.', True)
            if ls==6 and mode==3 and n==3:
                return result(*PAIR, 'Quellenbezüge und Rechenwege werden wechselseitig auf Nachvollziehbarkeit geprüft.', True)
            return result('expert-group','Expertengruppen','Die umfangreichen Fachbereiche lassen sich arbeitsteilig erschließen; Ergebnisse müssen anschließend gemeinsam verstanden und gesichert werden.', True)
        if ls==2 and ('Quellen' in text or 'Quellenqualität' in text or mode==3 and n==3):
            return result(*PAIR,'Ein Partnercheck unterstützt die Prüfung von Zuständigkeit, Aktualität und Verbindlichkeit.', True)
        return result('group','Gruppenarbeit','Die Analyse verbindet mehrere betriebliche Perspektiven und wird zu einem gemeinsamen Ergebnis zusammengeführt.', True)
    if phase=='planen':
        if mode==1:
            form,subject=PLAN_W1[ls][n-1]
            return result(form[0],form[1], f'{subject} wird passend zur Aufgabe im Tandem vorbereitet oder gemeinsam koordiniert; Partnerentwürfe werden in der Vierer-/Stammgruppe abgestimmt.')
        if mode==2:
            if ls==1 and n==3:
                return result(*PAIR, 'Zielvorschläge und ihre Beziehungen werden zu zweit vorbereitet und anschließend im Team abgestimmt.')
            if ls==6 and n==2:
                return result(*PAIR, 'Kundeninformation und interne Prüfung werden im Tandem abgegrenzt und danach gemeinsam freigegeben.')
            return result('group','Stammgruppe' if ls==3 else 'Vierergruppe','Arbeitsfolge, Kriterien und Verantwortlichkeiten werden gemeinsam abgestimmt; die angebotenen Strukturhilfen bleiben wählbar.')
        if 'Checkpoint B:' in text:
            return result('group','Gruppenarbeit','Die gemeinsame Planfreigabe verlangt übereinstimmende Zuständigkeiten, Termine und Qualitätsstandards.', mode in (3,5))
        if mode==3 and ((ls==1 and n in (2,3)) or (ls==3 and n==2) or (ls==4 and n in (3,4)) or (ls==6 and n==2)):
            return result(*PAIR,'Entwürfe und fachliche Abhängigkeiten können im Tandem vorbereitet und danach gemeinsam vereinbart werden.', True)
        return result('group','Gruppenarbeit','Das Team legt Arbeitsplan, Rollen, Kriterien und interne Freigaben eigenverantwortlich fest.', True)
    if phase=='entscheiden':
        if ls==1:
            label='Gründerrollen · Entscheidungsrunde'
        elif ls==3:
            label='Stammgruppe · Geschäftsführung'
        elif ls==4:
            label='Vierergruppe · Finanzierung'
        elif ls==5:
            label='Gründerrollen · Rechtsformwahl'
        elif ls==6:
            label='Stammgruppe · Fallentscheidung'
        else:
            label='Vierergruppe · Beratungswahl'
        if 'Verbindlicher Checkpoint' in text:
            return result('group','Gruppe · Checkpoint mit Lehrkraft','Die Gruppe stellt der Lehrkraft Entscheidung, Belege und Alternativen vor; die unternehmerische Wahl bleibt bei den Lernenden.')
        if mode in (3,5):
            label='Gruppenarbeit'
        return result('group',label,'Unternehmerische Auswahl, Gründerinteressen und Folgen müssen gemeinsam begründet und verantwortet werden; die einzelnen Perspektiven bleiben sichtbar.', mode in (3,5))
    if phase=='durchfuehren':
        if 'Verbindlicher Checkpoint' in text:
            return result('group','Gruppe · Checkpoint mit Lehrkraft','Der vollständige gemeinsame Entwurf wird der Lehrkraft vorgestellt; die Gruppe hält Rückmeldungen und notwendige Korrekturen fest.')
        if ls==4:
            return result('group','Pitchteam · Vier Sprechrollen' if mode in (1,2,4) else 'Pitchteam','Die Präsentation ist eine gemeinsame Leistung; alle Teammitglieder tragen vor und bleiben fachlich auskunftsfähig. Die vorgesehene Rolle des Finanzierungsgremiums bleibt erhalten.')
        if ls==6 and mode==2 and n==2:
            return result('pair','Partnerarbeit · Kundenmail','Ein Tandem verfasst und prüft die Kundenmail; vor der Zusammenführung in die Auftragsakte gibt die Gruppe deren Zusagen frei.')
        if ls==3 and mode==2 and n==2:
            return result('pair','Partnerarbeit · Redaktion','Eine wechselseitige Redaktionsprüfung sichert Zahl-, Quellen- und Textkonsistenz vor der gemeinsamen Freigabe.')
        if mode in (3,4,5):
            return result('group','Gruppenarbeit','Die Produktteile werden eigenverantwortlich erarbeitet, gegenseitig geprüft und zu einem gemeinsamen adressatengerechten Ergebnis verbunden.', True)
        return result('group','Stammgruppe · Redaktion' if ls==3 else 'Vierergruppe · Zusammenführung','Die vereinbarten Teilbeiträge werden arbeitsteilig umgesetzt, geprüft und gemeinsam zu einem konsistenten Handlungsergebnis verbunden.')
    raise ValueError(t['key'])


def main():
    tasks=json.loads(INPUT.read_text())
    mapped={t['key']:classify(t) for t in tasks}
    assert len(mapped)==len(tasks)==440
    assert all(v['kind'] in {'individual','pair','group','expert-group','partner-groups','plenum'} and v['label'] and v['reason'] for v in mapped.values())
    assert all(mapped[t['key']]['kind']=='individual' for t in tasks if t['phase']=='reflektieren')
    assert all(mapped[t['key']]['kind']=='partner-groups' for t in tasks if t['phase']=='bewerten')
    OUTPUT.write_text(json.dumps(mapped,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'tasks':len(mapped),'kinds':dict(Counter(v['kind'] for v in mapped.values())),'recommendations':sum('(Empfehlung)' in v['label'] for v in mapped.values())},ensure_ascii=False))

if __name__=='__main__':main()
