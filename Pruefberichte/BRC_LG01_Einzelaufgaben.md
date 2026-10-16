# LG01 · Einzelaufgaben, Fortschritt und Lehrkräfteansicht

Geprüft am 16.10.2026. Lieferung **1.2**, aufgebaut auf der inhaltserhaltenden
Lieferung 1.1 mit der GitHub-Oberfläche aus `8dd3853c69e1d33499037956c5fe3096fd2016f7`.
Die fachlich abweichenden Katalog-Master werden durch diesen Upload-Transfer
nicht ersetzt. Dieser Bericht ergänzt den unveränderten Bericht zur Lieferung 1.1.

| Paket | Alte IDs erhalten | Einzelkarten jetzt | Aufgaben in Weg 1 | GoodNotes-Phasenhefte |
|---|---:|---:|---:|---:|
| LS01 | 88 | 102 | 26 | 30 |
| LS02 | 88 | 100 | 26 | 30 |
| LS03 | 83 | 104 | 28 | 30 |
| LS04 | 85 | 104 | 27 | 30 |
| LS05 | 86 | 103 | 29 | 30 |
| LS06 | 93 | 115 | 34 | 30 |

59 Bündel eigenständiger Aufträge getrennt; zusammenhängende Kriterien und
Prüf-/Überarbeitungsaufträge bleiben verbunden. Insgesamt 628 Karten mit
fortlaufender Nummerierung je Lernweg über sechs Phasen. Alle ursprünglichen
523 Aufgabenkennungen bleiben vorhanden. Neue Teile haben stabile Unterkennungen;
Migration übernimmt nur signaturgültige alte Erledigungen.

## Inhalt und Paketbestand

- Zeichenprüfung sämtlicher Originalaufträge gegen die zusammengeführten Teile,
  ohne bloße HTML-Blockabstände und ohne wiederholte identische Einleitungen.
- Sämtliche Materialien, sonstigen Inhaltsseiten, Medienzuordnungen und Bilder
  unverändert. Alle 42 Original-PDFs bytegleich.
- HTML-Aufgabenbereiche und Inhaltsdaten stimmen überein; SCORM-Kennungen und
  Kompetenz-, Orientierungs- und Quiz-Signaturen erhalten.
- Alle 180 GoodNotes-Phasenhefte enthalten die aktuellen Einzelaufgaben mit den
  fortlaufenden Nummern; PDF-Text gegen die vollständigen Aufgaben geprüft.
  Eingebettete GoodNotes-Dateien entsprechen den jeweiligen PDF-Bytes.
- Manifest im ZIP-Wurzelverzeichnis; vollständige Dateiliste und alle Verweise
  geprüft. Neue Lehrkräfte-Dateien im Manifest und im Editor-Export enthalten.

## Lokaler Browser und SCORM-Simulation

- Alle 170 Aufgaben des Lernwegs 1 in allen sechs Paketen tatsächlich über die
  Oberfläche geöffnet und abgehakt. „Weiter“ wird freigegeben; Abhaken wechselt
  nicht automatisch. Folgephasen werden erst nach vollständiger Bearbeitung frei.
  Alle sechs simulierten SCORM-Versuche erreichen `completed` mit Suspend-Daten.
- Nach PIN-Anmeldung Lehrkräftebutton, alle 180 Phase/Lernweg-Kombinationen,
  Original-Quizlösungen und Erwartungshorizont sowie Rückkehr geprüft.
  Lehrkräftentests verändern den Lernversuch nicht und schreiben im Review-Test
  keine LMS-Daten. Button vor Anmeldung verborgen; Zugang unten rechts „Editor“.
- Lokale Vorschau und Moodle-`browse`: Orientierung, Quiz und Aufgabenhaken
  bedienbar. Moodle-`review` bleibt in der Lernendenansicht schreibgeschützt.
- In allen sechs Paketen: Export erhält Aufgaben-Signaturen und Nummerierung;
  abgeschlossene alte Bündel werden übernommen, neue Teilhaken bleiben einzeln.
- Materialrücksprung für neu getrennte Aufgaben mit Unterkennung und korrektem
  Lernweg; Layout bei 1024 und 390 Pixeln ohne horizontalen Überlauf geprüft.
- Materialauswahl mit mehr als zwei Zeilen startet eingeklappt und bleibt im
  geöffneten Zustand nicht am Bildschirmrand haften; beim Aufgabenöffnen klappt
  sie wieder zu. In allen sechs Paketen auf Tablet- und Smartphonebreite geprüft.
- Gespeicherte Editoränderung nach Neuladen in Übersicht und Fokus sowie im
  SCORM-Export vorhanden; Signaturen unveränderter Aufgaben bleiben stabil.
- 24 Python-Regressionstests bestanden.
- Alle 39 Katalog-Master mit dem bestehenden Prüfwerkzeug geprüft.

Die Prüfungen verwenden Chromium und eine lokale SCORM-1.2-API-Simulation.
Ein tatsächlicher Import in Moodle, die native Moodle-App und die Übergabe an
die GoodNotes-App sind dadurch nicht verifiziert.
