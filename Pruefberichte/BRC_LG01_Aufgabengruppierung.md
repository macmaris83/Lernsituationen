# Prüfung der Aufgabengruppierung und Arbeitsformen – BioCasa LG01

Geprüft am 14.10.2026, ausschließlich lesend am Repository: `Quellen/BRC_LG01/Reihenplan.md` und `tools/build_brc_series.py`.

## Ergebnis mit höchster Priorität

Die sechs Phasen `Kontrollieren / Überprüfen` enthalten in ALLEN sechs Lernsituationen und ALLEN fünf Lernwegen genau einen zusammenhängenden Prüfauftrag: fremdes Ergebnis prüfen, Kriterien/Belege anwenden, Rückmeldung auswerten, eigene Fassung überarbeiten. Der komplette Inhalt nach Entfernen der reinen Metadaten gehört in EINE Aufgabenkarte.

Aktueller Fehler: `metadata_and_tasks()` behandelt jedes direkte `li` einer `ul` oder `ol` wie einen eigenen Arbeitsauftrag und jedes gewöhnliche `p` zusätzlich wie eine Aufgabe. Dadurch werden LS01 W1 „Tauschen“, neun Qualitätskriterien und „Geben … Überarbeiten“ zu elf Aufgaben. Die Kriterien sind keine isolierten Schülerhandlungen und dürfen weder eigene Erledigtfelder noch Minuten erhalten.

Robuste Umsetzung für diese bekannte Quelle: der Funktion den semantischen Phasenschlüssel übergeben. Bei `phase == 'bewerten'` den gesamten nach Metadaten verbleibenden HTML-Fragmentinhalt unverändert als genau eine Aufgabe zurückgeben. Das ist sicherer als generische Verberkennung und gilt ebenfalls für:

- W3 LS01: Die drei nummerierten Schritte Tauschen / Überprüfen / eigenes Kriterium und Überarbeiten bilden einen einzigen Prüfzyklus; Nummerierung innerhalb der Karte bewahren.
- W5: Bulletschritte Audit / Rückmeldungen / Änderungen bleiben gemeinsam innerhalb einer Karte.
- W2/W4: Auch zwei oder mehr Absätze gehören zum selben Prüfzyklus.
- LS04: Gremium prüft, Pitchteam übernimmt begründete vorläufige Entscheidung und überarbeitet maximal drei Folien – ein Auftrag mit zwei Rollen.

### Erwartete Prüfkriterien und Phasenzeiten

| LS | W1 Prüfkriterien in derselben Karte | Überprüfen-Minuten pro W1–W5 |
|---|---:|---:|
| LS01 Geschäftsidee | 9 | 45 |
| LS02 Beratung | 8 | 22,5 |
| LS03 Businessplan | 10 | 45 |
| LS04 Pitch | 10 | 45 |
| LS05 Gründung | 9 | 45 |
| LS06 Geschäfte | 12 | 90 |

Diese Zeiten sind die bereits festgelegten Phasenbudgets, keine neue Schätzung. Die zusammengefasste Aufgabe übernimmt das gesamte Budget. Gesamtsummen jeder Phase und jedes Lernwegs bleiben unverändert.

## Allgemeine Regeln für andere Phasen

1. Verschachtelte Listen stets beim Elternauftrag lassen. Die vorhandene DOM-Regel tut das grundsätzlich richtig.
2. Direkte nummerierte Arbeitsaufträge in Informieren, Planen und Entscheiden sind tatsächliche getrennte Aufgaben. Bewahren, außer die ausdrücklich bekannte Auditphase.
3. **Nicht jede Bulletliste ist eine Kriterienliste.** LS03 W2 Informieren enthält die drei echten fachlichen Arbeitspakete „Angebot und Markt“, „Marketing und Umsetzung“, „Kapital und Kapazität“. Diese dürfen drei eigene Aufgaben bleiben. Der vorhergehende Absatz enthält eine echte Einstiegshandlung („Halten Sie zunächst fest …“) und kann eine EA-Aufgabe bleiben. Der nachfolgende Expertengruppen-Kurzbericht ist eine reale Zwischensicherung.
4. Ein Einleitungsabsatz, der nur auf die folgende Liste verweist, ist kein separater Auftrag; mit der Liste verbinden (z. B. „Überprüfen Sie anhand folgender Fragen:“). Das wird für die Auditphasen von Regel oben vollständig abgedeckt.
5. Vorgaben zum Ergebnis, Mindeststandard, Pflichtkern, Format und KI-Bedingungen sind Bestandteil des jeweiligen Auftrags und keine eigenen Aufgaben. Bei W5 gehören „Mindestanforderung:“/„Mindeststandard:“ und „Sie muss …“ zum Erstellen des Produkts; bei Informieren gehört „Ihr fachlicher Pflichtkern:“/„Pflichtvergleich:“ zur Materialerschließung; „Ab dieser Phase dürfen … KI …“ zur Planung, nicht als abhakkbare KI-Nutzung.
6. **Checkpoint A/B** und **Verbindlicher Checkpoint 1/2** sind echte, explizit nachzuweisende Zwischenergebnisse. Können als eigene gemeinsame Aufgabe bleiben; keinen optionalen KI-Hinweis anstelle eines Checkpoints abhaken lassen.
7. `Handlungsergebnis:` an den ausführenden Auftrag anhängen. Nachfolgende Hinweise zum erlaubten KI-Einsatz ebenfalls dort lassen, statt neue GoodNotes-Aufgabe zu generieren.
8. Persönliche Reflexionsfragen sind echte Teilfragen und dürfen nicht verloren gehen. W1 LS01 beginnt mit „Nehmen Sie schriftlich zu den folgenden Fragen Stellung:“ – hier Einleitung an Frageblock binden, damit sie keine leere Extraaufgabe wird. Falls Reflexion in einer Karte gruppiert wird, alle nummerierten Fragen und ggf. anschließendem Austausch innerhalb dieser Karte erhalten. Das ist eine weitere semantische Vereinheitlichung, aber der Nutzerbeleg erzwingt primär die Audit-Gruppierung.
9. Text als HTML DOM behandeln und Tabellen/Listen/Absätze nicht per Satzzeichen zerlegen. Inhalt vollständig mit denselben Reihenfolgen erhalten, lediglich Kartengrenzen ändern.

## Arbeitsformen statt pauschalem „Lernteam“

Phasenmeta aus der Quelle vollständig erhalten. Pro Karte eine zum tatsächlichen Auftrag passende Arbeitsform ausweisen; Symbolauswahl nicht bloß über den Text „Einzelarbeit“ im gesamten Phasenmeta treffen. Die aktuelle Logik `single = pi == 5 or ('Einzelarbeit' in form and 'anschließend' not in form and 'Gruppen' not in form)` fällt bei fast allen Informierenphasen auf „Lernteam“ zurück.

Reihenfolge der Zuordnungsregeln:

1. Explizite karteneigene Angaben aus Text: einzeln/eigene Sichtung → Einzelarbeit; Expertengruppe → Expertengruppen; Stammgruppe → Stammgruppen; anderes Team/andere Gruppe/Peer/Audit → Partnergruppen bzw. passende Prüfgruppe; Gründerperspektiven → Gruppenarbeit mit Gründerrollen.
2. Phase `reflektieren`: Einzelarbeit als primäre Handlung, anschließenden Team-/Plenumsvergleich aus Originaltext sichtbar halten („Einzelarbeit → Teamaustausch“, falls vorhanden).
3. Phase `bewerten`: Partnergruppen; LS04 „Finanzierungsgremium / Pitchteam“, LS03 „Prüfgruppen“, LS05 „Rechtscheck / Partnergruppen“, LS06 „Auditgruppen“.
4. Gemeinsame Planung/Abwägung/Endprodukt: präzises Original (Vierergruppen, Stammgruppen, Gruppenarbeit mit Gründerrollen, Redaktion, Pitchteam).
5. Für W4/W5 selbstgesteuerte Arbeitsorganisation keine stillschweigende Festlegung sämtlicher Materialsichtung auf Gruppe: „Einzel-/Partnerarbeit“ bzw. „Arbeitsform selbst wählen“ für offene Erschließung; verpflichtendes gemeinsames Produkt/Entscheidung/Checkpoint trotzdem Gruppen-/Teamarbeit. Die Quelle erlaubt ausdrücklich selbst gewählte Einzel-, Partner- und Teamarbeit.

### Konkrete W1-Zuordnung Informieren

| LS | Aufgabe | Primäre Arbeitsform |
|---|---|---|
| LS01 | 1 Problem, 2 Gründer, 3 Kunden | Einzelarbeit, danach Ergebnisabgleich |
| LS01 | 4 Ziele, 5 Anspruchsgruppen, 6 Betriebsart, 7 Prozesse | Partnerarbeit / Vierergruppe für Begründungsvergleich; persönliche Erstbearbeitung möglich |
| LS01 | Zwischensicherung | Vierergruppe |
| LS02 | 1 Problem | Einzelarbeit |
| LS02 | 2 Kategorien, 3 Standort, 4 Lücken | Partnerarbeit / arbeitsteilige Vierergruppe |
| LS02 | 5 Quellenakte | Explizit arbeitsteilige Quellen-/Expertengruppe |
| LS02 | 6 Quellenprüfung | Partnerarbeit (gegenseitiger Belegcheck) |
| LS02 | 7 Übergang, Zwischensicherung | Vierergruppe |
| LS03 | 1 Problem | Einzelarbeit |
| LS03 | 2 Produkte, 3 Markt, 4 Wettbewerb, 5 Marketing, 6 Kapital, 7 Kapazität, 8 Widersprüche | Fachliche Expertengruppen; bei Rechnungen Partnercheck innerhalb der Expertise |
| LS03 | Kurzbericht / Übernahme | Expertengruppen → Stammgruppen |
| LS04 | 1 Finanzierungsproblem | Einzelarbeit |
| LS04 | 2 Formen, 3 Darlehen, 4 Kontokorrent, 5 Leasing, 6 Tragfähigkeit, 7 Mischungen | Fachliche Expertengruppen; Rechenaufgaben mit Partnercheck |
| LS04 | Fachinformation | Expertengruppen → Vierergruppe |
| LS05 | 1 Problem, 2 Interessen, 3 Verpflichtungen | Einzelarbeit → Ergebnisabgleich |
| LS05 | 4 Rechtsform | Explizite Rechtsform-Expertengruppen |
| LS05 | 5 alle Formen vergleichen | Explizite Stammgruppen |
| LS05 | 6 Haftungsfälle, 7 Chat-/Quellencheck | Partnerarbeit / Rechtsform-Expertengruppe |
| LS05 | 8 Schritte, Vergleichstabelle | Stammgruppen |
| LS06 | 1–5 Vertrag | Expertengruppe „Vertrag“ nach eigener Erstlektüre |
| LS06 | 6 Zahlung | Expertengruppe „Zahlung“, Partnercheck der Rechnung |
| LS06 | 7–9 Reklamation | Expertengruppe „Reklamation“ |
| LS06 | 10–11 Personal | Expertengruppe „Personal“ |
| LS06 | Prüfnotizen | Expertengruppen → Stammgruppen |

### W2/W3/W4/W5 Besonderheiten

- LS01/02 W2 haben einen expliziten einzeln zu lösenden Einstieg vor drei nummerierten Analysepaketen. Einstieg EA, Pakete arbeitsteilige Vierergruppen, Ergebnissicherung gemeinsame Gruppe.
- LS03 W2: eigene erste Sichtung EA; drei echte Fachpakete Expertengruppen; Kurzbericht zunächst Expertengruppe, Übernahme Stammgruppe.
- LS04 W2: erstes Finanzierungsproblem EA; Finanzierung und Belastbarkeit Expertengruppen; Fachinformationen Expertengruppen mit Austausch.
- LS05 W2: Quellenplan verlangt zunächst EA und anschließend gemeinsamem Rechtsformvergleich; taskbezogen Interessen/Risiken EA→Gruppenvergleich, Rechtsformen Vergleichsgruppe, Belastungsprobe Partner-/Quellencheck, Ergebnistabelle Vierergruppe.
- LS06 W2: vier Fachpakete jeweils Expertengruppe mit eigener Materialerstsichtung; gemeinsame Akte anschließend Stammgruppe.
- W3 kürzer formuliert, aber gleiche Fachlogik. Wo ausdrücklich einzeln/eigene Analyse/Persönliches: EA; sonst Partner-/Expertengruppe für Analysen und gemeinsame Gruppenarbeit für Synthese.
- W4 Informationsmaterial nennt selbst gewählte Einzel-, Partner- und Teamarbeit. Diese Wahl darf in der Karte erkennbar bleiben. Checkpoints sind gemeinsame Nachweise mit Lehrkraft; Planung und endgültige Unternehmensentscheidung Gründerteam, Materialrecherche davor selbstgewählt.
- W5: erster „KI-frei“-Einstieg/Inventar persönliche Erstlektüre EA; weitere Materialsichtung selbstgewählt oder gezielt Expertengruppe (LS06 ausdrücklich erlaubt); Pflichtkern beim Materialauftrag; Checkpoints Gründerteam; eigenes Reflexionslernen EA; Audit immer anderes Team.

## Sinnvolle Verifikationsfälle

- Alle 30 `bewerten`-Panels haben exakt eine `.assignment-frame`, keine extra Karte für Kriterien und Feedback; vollständige Originalpassage im Fokus.
- W1 Audit-Listenlängen 9/8/10/10/9/12 und anschließende Feedback-/Überarbeitungssätze erhalten.
- Alle Phasenbudgets pro LS/W summieren unverändert auf Ausgangsbudget.
- LS03 W2 Informieren: drei fachliche Bulletpakete getrennt erhalten (kein pauschales Verschlucken).
- LS02 W1 Aufgabe5: ihre vier verschachtelten Quellenfragen bleiben innerhalb einer einzigen Aufgabenkarte.
- LS05 W1 Aufgabe4/5 zeigen Expertengruppen bzw. Stammgruppen; LS06 Vertrag/Zahlung/Reklamation/Personal unterscheidbar.
- Persönliche Reflexion als Einzelarbeit und Audit als kooperativer Rollenwechsel erkennbar; keine durchgängig identischen „Lernteam“-Badges.
- Textnormalisierter Vergleich Ausgangsauftrag → erzeugte Karten über HTML-Textinhalte, damit Umgruppierung keine Satzverluste erzeugt.
