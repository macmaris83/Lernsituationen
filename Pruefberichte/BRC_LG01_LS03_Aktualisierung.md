# Businessplan LG01–LS03: aktualisiertes SCORM-Paket

Stand: 14. Oktober 2026. Grundlage: hochgeladenes `BRC_LG01_LS03_SCORM (1).zip`.

## Inhalt und Zeiten

Originale Aufgabenstellungen, Materialien, Quellen, PDFs und Konfiguration bleiben erhalten. Die zwei ausdrücklich freigegebenen redaktionellen Änderungen sind die Orientierungszeiten für alle 83 Aufgaben und die fünf Kompetenzbeschreibungen in der Ich-Perspektive. Die vollständigen Ich-Kompetenzen bleiben in den gemeinsamen Daten und im Aufgabenfokus erhalten. Die Orientierung zeigt nun ein kompaktes Kompetenzprofil mit den fünf Kompetenznamen rechts neben dem verkleinerten Netz. Die Zeiten ergeben in allen fünf alternativen Lernwegen exakt die jeweilige Phasenzeit; die Lernwege werden nicht addiert.

| Phase | Minuten je Lernweg |
| --- | ---: |
| Informieren | 270 |
| Planen | 135 |
| Entscheiden | 135 |
| Durchführen | 180 |
| Bewerten | 45 |
| Reflektieren | 45 |
| Gesamt | **810** |

Einzelzeiten: [businessplan_aufgabenzeiten.json](../tools/businessplan_aufgabenzeiten.json). Kompetenzformulierungen: [businessplan_kompetenzen.json](../tools/businessplan_kompetenzen.json).

## Finale Oberfläche und Navigation

Das Kompetenzprofil der Orientierung wurde neu angeordnet: Netz links, beim Businessplan von 560 auf höchstens 420 Pixel (25 Prozent kleiner), rechts die vier weiteren Kompetenznamen mit ihren vollständigen Ich-Beschreibungen. Die Fachkompetenz steht oberhalb als vorrangige Kompetenz samt Beschreibung; sie wird rechts nicht doppelt dargestellt. Auf kleinen Bildschirmen stehen Netz und Beschreibungen untereinander. Die gemeinsamen Kompetenzdaten und die vollständigen Aussagen im Aufgabenfokus bleiben erhalten. Die bestehende Orientierung-Abschlussmarkierung bleibt nach Neuladen erhalten; Metadaten und SCORM-Signaturen sind unverändert.

- Auf allen Materialseiten nur ein kompakter hellgrüner Materialzugriff als Akkordeon. M-Nummern und vollständige Bezeichnungen bleiben lesbar; die Auswahl bricht in mehrere Zeilen um, ohne horizontales Scrollen vorauszusetzen. Dasselbe gilt für die übrigen Phasenseiten. In der Orientierung ist der Materialzugriff ersatzlos entfernt.
- Das Materialfenster dominiert den Bildschirm. Zusätzliche große Titelblöcke sind in der Materialansicht ausgeblendet, im Editor/Druck bleiben die Inhalte erhalten. Die kompakte blaue Phasenübersicht steht unter dem Material und unter „Kurz prüfen“.
- „Zurück zur Aufgabe“ steht im schmalen Materialkopf und schwebend unten rechts. Die schwebende Schaltfläche sitzt direkt unter `body`, außerhalb des begrenzten Inhaltsrahmens. Der validierte Aufgabenbezug wird in lokalen Materiallinks mitgeführt; fehlender Sitzungsspeicher entfernt die Navigation nicht mehr. Materialwechsel erhält Aufgabe und Lernweg. Ohne gültigen Aufgabenbezug bleibt der Rücksprung sichtbar, aber deaktiviert; kein beliebiger Rücksprung zu Informieren.
- Geschlossene Aufgabenkarten folgen der tatsächlichen Text-/Symbolhöhe. Die feste Mindesthöhe von 185 Pixeln ist entfernt. Die kurze erste Businessplan-Karte benötigt bei 1024 Pixeln Breite rund 113 statt rund 205 Pixel.
- Arbeitsaufträge bleiben vollständig, im offenen Akkordeon als Absätze. Der Aufgabenrahmen ist blau, erledigte Karten hellgrün. Kein orangefarbener Rahmen um den geöffneten Kopf; Tastaturfokus landet im Aufgabenbereich. Manuelles Weiter erst nach Erledigt-Markierung.
- Prüffragen der Handlungssituation: komplette Zeile hellblau bei offen/falsch und hellgrün bei richtig gelöst, ohne Haken. Rückmeldung und zugänglicher Status bleiben erhalten. Handlungssituation und Titelbereich haben die gleiche leichte Kartenumrahmung wie die übrigen Phasen.
- Lange Fließtexte erhalten Blocksatz und automatische deutsche Silbentrennung; kurze Texte, Arbeitsaufträge, Tabellen und Bedienelemente bleiben linksbündig. Tatsächliche Trennung hängt von Browser und Sprachwörterbuch ab.

## Phasenbezogener GoodNotes-Import

30 zusätzliche Teil-Arbeitshefte: sechs Phasen × fünf Lernwege. Die jeweiligen Original-PDF-Seiten werden übernommen, ohne Aufgaben umzuschreiben. Jeder Import bietet nur die aktuelle Phase und den aktuellen Lernweg. Der Import-Button einschließlich seiner gerahmten Leiste steht in allen sechs Aufgabenphasen unmittelbar unter der Arbeitsform, passend zum gewählten Lernweg. Orientierung und Handlungssituation zeigen weder Import-Button noch leere Import-Leiste. Der separate PDF-/Druck-Button öffnet ausdrücklich das gesamte Dokument, unabhängig von der aktuellen Phase. Ein kleines rotes Acrobat/PDF-Symbol steht links neben „Gesamtdokument als PDF“. Der Gesamtzugriff bleibt auf Materialseiten und im Aufgabenfokus als kompakter Symbolbutton erreichbar. Der Businessplan verwendet die vorhandene vollständige PDF-Datei; Sozialpädagogik die vollständige Druckansicht mit dem bisherigen PDF-Druckmechanismus. Lehrkräfte können weiterhin exportieren. Originale PDF-Dateien bleiben als Quelldateien im Archiv erhalten.

Die Sozialpädagogik-Vorlage und das Paket LS 1.1 enthalten dieselbe technische Oberflächenanpassung, mit sechs Teil-Arbeitsheften für den einen Lernweg. Die vorhandenen Ich-Kompetenzen dort bleiben erhalten.

## Glas-Optik und Hintergrund

Transparente Flächen, weiche Schatten, helle Kanten und moderate Hintergrundunschärfe (`backdrop-filter` und WebKit-Variante) sind wieder deutlicher eingesetzt. Erledigte Aufgaben behalten ihre eindeutige hellgrüne Statusfarbe, Dokumentseiten ihre lesbare Papierfläche. Eine feste dekorative Ebene füllt die gesamte Bildschirmfläche und wird beim Drucken ausgeblendet. Sie zeigt das unverändert übernommene Originalmotiv proportional skaliert mit `cover` und bleibt beim Scrollen stehen.

Das als ZIP nachgereichte BBS-Hintergrundmotiv liegt jetzt als lokale PNG-Datei in beiden Paketen vor und ist in beiden Manifesten aufgeführt. Es benötigt keinen externen Bildabruf.

## Online-Übersetzung: nur geprüft

Die Übersetzungsfunktion ist nicht eingebaut. Der Nutzer hat ausdrücklich zunächst die Prüfung einer Online-Lösung gewählt. Die Ergebnisse und Grenzen der Quellenprüfung stehen in [Fachbegriffe_Online_Uebersetzung_Pruefung.md](../Konzepte/Fachbegriffe_Online_Uebersetzung_Pruefung.md).

## SCORM und Editor

Originale SCORM-Schnittstelle und Codec, Aufgaben-IDs, Aufgaben-Signaturen, Fortschrittsmetadaten und Kompetenzberichtstruktur bleiben erhalten. Ergänzte Zeitspannen werden vor der Aufgabensignaturberechnung entfernt. Bei der Orientierung wird ausschließlich die freigegebene, inhaltlich gleichwertige Ich-Umformulierung vor der Signaturberechnung normalisiert, sodass bisheriges „Orientierung gelesen“ erhalten bleibt. Andere Inhaltsänderungen bleiben signaturwirksam. Lehrkräfte-Änderungen erscheinen im Aufgabenfokus und im neuen ZIP-Export. Timer-Zeiten bleiben beim Materialwechsel erhalten.

Die neuen Teil-Arbeitshefte und deren lokalen Share-Skripte sind im Manifest enthalten. Das Manifest liegt direkt im ZIP-Wurzelverzeichnis.

## Verifikation

- Redaktioneller Vergleich mit dem Upload: nach Rücknahme ausschließlich der freigegebenen Zeitspannen und Ich-Kompetenzen identische Lernsituationsdaten. Originalmedien/PDFs, Konfiguration, SCORM-Dateien und Fortschrittsmetadaten auf Bytegleichheit geprüft.
- Alle 83 Aufgaben in sechs Phasen und fünf Lernwegen im Browser: vollständige Texte, korrekte Timer, gleicher Kompetenz-/Uhrbereich, Kopf ohne Einklapp-Link/orangen Fokusrahmen, manuelles Weiter, Abschlussmarkierung und Layout.
- Alle 30 Phasen-/Lernweg-Zeitsummen und neu berechnete Metadaten mit Originalaufgaben- und Orientierungssignaturen geprüft.
- 25 Phasenübergänge: Sperren in Navigation und bei direktem Seitenaufruf.
- Alle zehn Materialien in allen fünf Lernwegen: Materialwechsel, genaue Aufgabenrückkehr, erhaltene Restzeit, kompakte Auswahl, Phasenübersicht unter dem Material. Zusätzlich mit blockiertem oder bei jedem Seitenaufruf geleertem Sitzungsspeicher geprüft. Ungültige Aufgabenreferenzen führen zu keinem beliebigen Ziel.
- Prüffragen: offen/falsch blau, nach richtiger Prüfung grün, ohne Haken; Wiederaufnahme nach Neuladen.
- Alle 30 tatsächlichen GoodNotes-Share-Aufrufe mit Dateiobjekten geprüft: Phase, Lernweg, Dateiname und PDF-Größe stimmen. Sechs entsprechende Share-Aufrufe in Sozialpädagogik LS 1.1 geprüft. Die PDF-Teilseiten wurden textlich mit den entsprechenden Originalseiten verglichen.
- Lehrkräfte-Editor: PIN-Prüfung, gespeicherte Zeitänderungen, Akkordeon und tatsächlicher ZIP-Export mit aktuellen Assets und unveränderten Fortschrittssignaturen.
- SCORM-API-Simulation: Commit, Kompetenzberichte, ursprüngliche Aufgabenkennungen und Wiederaufnahme.
- Ansichten bei 1024 × 768, 768 × 1024 und 390 × 844 Pixeln: kein seitlicher Seiten-/Materialscroll, kompakte Karten, sichtbarer Rücksprung, unverdeckte Materialien.
- GoodNotes-Position: gerahmter Import direkt nach dem Arbeitsform-/Arbeitszeitbereich in allen sechs Phasen und fünf Businessplan-Lernwegen sowie den sechs Sozialpädagogik-Phasen geprüft.
- Orientierung-Kompetenzprofil: Netz höchstens 420 Pixel, rechts vier weitere Kompetenzen mit vollständigen Ich-Beschreibungen, vorrangige Fachkompetenz mit Beschreibung oberhalb ohne doppelte rechte Karte, responsive Ansichten 1024/768/390 Pixel und gespeicherte Orientierung-Markierung nach Neuladen geprüft.
- Orientierung: kein Materialzugriff, kein Ersatz und keine leere Material-/Import-Leiste; in beiden Paketen im Browser geprüft.
- Gesamt-PDF: getrennt vom phasenweisen GoodNotes-Import, Symbol und Gesamtziel in Übersicht, Materialkopf und Aufgabenfokus geprüft.
- Glasflächen und feste Hintergrundebene bei 2000/1024/390 Pixeln, Hintergrundgröße über die ganze Bildschirmbreite, unveränderter Ursprung beim Scrollen und ausgeblendeter Druckhintergrund geprüft. Das vom Nutzer als ZIP gelieferte Originalfoto ist unverändert als lokale PNG-Datei eingebunden; Auslieferung im Browser, proportionaler bildschirmfüllender Hintergrund und Scrollverhalten wurden geprüft.
- Lange Texte: CSS-Blocksatz/automatische Silbentrennung und deutsches Dokument geprüft. Aufgaben bleiben linksbündig; Handlungssituationsrahmen konsistent; keine Import-Leiste in Orientierung/Handlungssituation.
- Fertige ZIPs: fehlerfrei entpackbar, alle Manifest-Dateien vorhanden, Archivinhalt identisch mit den jeweils geprüften Ausgabeordnern.

Prüfungen lokal mit Chromium und einer SCORM-API-Simulation. Der echte Moodle-App-Betrieb, native GoodNotes-Übergabe/iPad-Ton und AIS-Einbettung/Anmeldung wurden hier nicht geprüft. AIS und Web Share wurden im Browser simuliert. Die Moodle-Pakete müssen ersetzt werden; GitHub aktualisiert vorhandene Moodle-Kopien nicht automatisch.

## Dateien und Reproduktion

- [Businessplan-SCORM-ZIP](../Downloads/BRC_LG01_LS03_Aktualisiert_SCORM.zip)
- [Sozialpädagogik LS 1.1 SCORM-ZIP](../Downloads/Sozialpaedagogik_LS1_1_SCORM.zip)
- [Kompakte Aufgabenübersicht](BRC_LG01_LS03_Kompakte_Karten.png)
- [Materialansicht](BRC_LG01_LS03_Materialansicht.png)
- Aufbau: `python tools/prepare_businessplan_scorm.py ORIGINAL.zip AUSGABEORDNER`
- Vollständige Businessplan-Prüfung: `python tools/verify_businessplan_scorm.py ORIGINAL.zip AUSGABEORDNER`
- Material-/Viewport-Prüfung: `python tools/verify_material_layout.py AUSGABEORDNER`
- Orientierung-Prüfung: `python tools/verify_orientation_layout.py AUSGABEORDNER`
- Glas-/Gesamtdokument-Prüfung: `python tools/verify_visual_shell.py AUSGABEORDNER`
- Phase-Import-/Typografie-Prüfung: `python tools/verify_phase_imports.py AUSGABEORDNER`
- Voraussetzungen: Python 3, PyMuPDF, Node.js, Python-Paket Playwright, Chromium unter `/usr/bin/chromium`. Die Prüfungen starten und beenden ihren lokalen HTTP-Server selbst.

## Archiv-Prüfsummen

- `BRC_LG01_LS03_Aktualisiert_SCORM.zip` · SHA256 `6cc772a2bc2b6e20d3a5718bea8b28b2d57231380e97c549205eef7ac894a65e`
- `Sozialpaedagogik_LS1_1_SCORM.zip` · SHA256 `b4f26e3c70be770acd80d69e824349d815157a913d1fe58beb0425646e649866`

## Nachtrag: Kompetenzbeschreibungen und Originalhintergrund

Die am 14.10.2026 nachgereichte ZIP enthält das Originalmotiv „Frosted-Glass Campus in Pastelltönen.png“. Beide Vorlagen und SCORM-Ausgaben enthalten es bytegleich als `assets/bbs1-campus-background.png`, einschließlich Manifest-Eintrag. Die feste Hintergrundebene verwendet das Foto lokal, ohne Internetabruf. Die vier weiteren Kompetenzbeschreibungen bleiben neben dem Netz sichtbar; die Fachkompetenz steht als vorrangige Kompetenz oberhalb. Gemeinsame Daten, Editor-Inhalte und vorhandene Fortschrittssignaturen bleiben erhalten. Orientierung und Glas-/Hintergrundprüfung haben für beide Pakete bestanden; die Businessplan-Erstellung aus dem Originalarchiv mit neuer Grafik wurde ebenfalls ausgeführt.
