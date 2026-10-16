# BioCasa LG01 · Paketset 1.5 · Abschlussprüfung

Geprüft am 16. Oktober 2026. Grundlage sind die sechs ausdrücklich bereitgestellten SCORM-Pakete 1.4. Die [Quellenprüfsummen](Quellen_Pruefsummen.json) dokumentieren diese Eingaben. Referenz der Oberfläche ist der Katalogstand `8dd3853`; die vor der Veröffentlichung synchronisierte Hauptversion `614736e` enthält identische LG01-Master und Vorlagen.

## Ergebnis und Inhaltserhalt

Alle Prüfungen bestanden. Die [unabhängige Lieferprüfung](Lieferpruefung.json) vergleicht sämtliche Aufgabenphasen, Materialien, Quellen- und Quiztexte, Lehrbuchverweise, Konfigurationen und Fortschrittsdateien mit den hochgeladenen Paketen.

| LS | Vollständige Einzelaufgaben | Lehrbuchverweise |
|---|---:|---:|
| 01 | 102 | 76 |
| 02 | 100 | 74 |
| 03 | 104 | 78 |
| 04 | 104 | 77 |
| 05 | 103 | 76 |
| 06 | 115 | 87 |
| Gesamt | 628 | 468 |

Alle Inhaltsseiten außer der gezielt überarbeiteten Orientierung bleiben im Datenbestand zeichengetreu erhalten. Die vollständigen Fortschrittsdateien, Paketkonfigurationen, 222 ursprünglichen PDF-Dateien, ursprünglichen Bilddateien und GoodNotes-Payloads sind bytegleich. Die 180 Phasen-PDF-Payloads stimmen mit der jeweils richtigen PDF-Datei überein.

Die Orientierung enthält keinen Materialzugriff. Ihre ursprünglichen Relevanztexte und Kurzprüfungen bleiben erhalten; die 30 Kompetenzbeschreibungen werden fachlich vollständig in die Ich-Perspektive übertragen und im kompakten Vorlagenraster dargestellt. Die zwölf aktuellen Originalbilder aus den Katalog-Mastern sind zusätzlich unverändert übernommen und in Orientierung und Handlungssituation zugeordnet.

Die Darstellungsänderung der Orientierung erhält deren bestehende Signatur ausschließlich für die genau bekannte neue Darstellung. Der Prüfer rekonstruiert sämtliche Aufgaben-, Quiz- und Orientierungssignaturen aus den aktuellen Daten. Echte spätere Inhaltsänderungen erzeugen weiterhin neue Signaturen. Ein Editor-Export mit einer gezielt bearbeiteten Aufgabe änderte in jedem Paket genau deren Aufgabensignatur; die gelesene Orientierung blieb erhalten.

## Browser, Druck und Export

- [180 Kombinationen](Browser_Pruefung.json) aus sechs Paketen, sechs Aufgabenphasen und fünf Lernwegen: vollständiger Fokus, aktuelle Metadaten, manuelles Weitergehen, sofortiger Farbwechsel und Speicherung nach Neuladen bestanden.
- [30 Uhrkombinationen](Uhren_Pruefung.json) mit Countdown, Pause/Fortsetzen und Gong. Je Paket zusätzlich Ablaufmeldung, Grün–Schwarz–Rot, Fortsetzen nach Neuladen, Stummschaltung und native Web-Audio-Ausgabe geprüft.
- [24 Touch-Fälle](MC_Pruefung.json): alle sechs Pakete in lokaler Vorschau, normalem SCORM-Versuch, Browse und Review. Auswahl auf dem Antworttext, Feedback und Wiederaufnahme bestanden; Review verändert den gespeicherten Lernversuch nicht.
- 36 neue Bildansichten bei 390, 768 und 1024 Pixeln: richtige Datei, tatsächliches Laden, volle Bildfläche, Originalseitenverhältnis und kein Seitenüberlauf.
- 124 Material-/Lernwegaufrufe: Materialwechsel, kompakte Phasenübersicht und Rücksprung zur exakt zugehörigen Aufgabe erhalten.
- Zwölf tatsächliche GoodNotes-Share-Payloads im Browser gegen den SHA-256-Wert der zugehörigen Phasen-PDF verglichen.
- Sechs tatsächliche bearbeitete SCORM-ZIPs aus dem Lehrkräfteeditor geprüft: Bearbeitung in HTML und Inhaltsdaten, Originalbilder, aktuelle Runtime und richtige Fortschrittsmetadaten enthalten. Persönliche Teststände werden nicht ausgeliefert.
- Sechs neue A4-Gesamtdokumente enthalten die aktuellen Ich-Kompetenzen, beide unbeschnittenen Originalbilder in voller Auflösung und alle 428 ursprünglichen Tabellenzellen. Die Original-PDFs bleiben zusätzlich erhalten.
- Alle Einzelarchive: CRC, Manifest im ZIP-Wurzelverzeichnis, unveränderte SCORM-Kennungen und Startressourcen, vollständige Dateiliste und bytegleicher aktueller Paketbestand geprüft.

Ein vorhandener Bedienfehler der Fassung 1.4 wurde behoben: Die Lernwegauswahl in der Lehrkräfteansicht entfernt bei einer bewussten Neuwahl den vorherigen Aufgabenrücksprung aus der Adresse. Dadurch setzt die alte Aufgabe den gerade gewählten Weg nicht wieder zurück. Der Wechsel nach einem echten Materialrücksprung ist in allen sechs Paketen geprüft.

Die drei maßgeblichen Stylesheets sowie Druck- und Materialgestaltung entsprechen bytegleich den aktuellen Katalog-Mastern. Die Aufgabenform, Nummerierung, Uhr und Lehrkräftefunktionen der gelieferten Fassung bleiben erhalten.

## Reproduzieren und Prüfgrenzen

Der zusätzliche BBS-Rechner ist in allen sechs Lieferpaketen, den sechs Katalog-Mastern der BRC-LG01-Reihe und beiden Lernsituationsvorlagen enthalten. Die acht Katalogexporte tragen Version 1.2; das eigenständige hochgeladene Paketset bleibt die Lieferung 1.5 mit seinen ursprünglichen Kennungen. Alle 40 Katalogarchive bestanden die zentrale Vollständigkeits- und Inhaltsgleichheitsprüfung.

Rechnerprüfung: sieben unabhängige Rechenlogik-Tests und [14 tatsächliche SCORM-Iframe-Prüfungen](Rechner_Pruefung.json) bestanden. Geprüft sind die vier Grundrechenarten, Punkt-vor-Strich, Dezimalkomma, Prozent einschließlich Aufschlag/Rabatt, Fehlerbehandlung, echtes Touch-Verschieben ohne Seitenscrollen, erhaltene Rechnung/Position beim Materialwechsel, Tastatur, kleine Ansichten bis 667 × 320 Pixel, Schließen und Druckausschluss. Das Rechnen selbst verändert den bewerteten Lernstand nicht. Die sechs zusätzlichen Lehrkräfteexporte enthalten alle Rechnerdateien. Die 180 Fokusprüfungen wurden mit eingebautem Rechner erneut bestanden.

Die Erstellung erfolgt mit `tools/refresh_lg01_upload.py INPUT OUTPUT`; INPUT enthält die sechs entpackten Originalordner LS01–LS06. Der Generator verändert die eigenständige Lieferung, nicht die fachlich andere Katalogreihe. Anschließend `tools/verify_lg01_upload.py INPUT OUTPUT` ausführen. Weitere Browserprüfer: `tools/check_task_card_form.mjs`, `tools/check_task_clocks.mjs` und `tools/check_situation_mc.mjs` mit dem erzeugten `preview`-Ordner. Benötigt werden lxml, PyMuPDF, Playwright und Chromium. Die aktuelle Quelle der 30 Ich-Formulierungen und deren ursprüngliche Fassung sind in [Inhaltspruefung.json](Inhaltspruefung.json) dokumentiert.

Die Funktionsprüfungen liefen lokal in Chromium, einschließlich Touch-Eingabe und SCORM-1.2-API-Simulation. Eine tatsächliche Moodle-Installation, AIS-Anmeldung, ein physisches iPad und die Übergabe an die native GoodNotes-App waren nicht Bestandteil der Prüfung. Bereits importierte Moodle-Pakete benötigen dort ausdrücklich die neue Paketfassung.
