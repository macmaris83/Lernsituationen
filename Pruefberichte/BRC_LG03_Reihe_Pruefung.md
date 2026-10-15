# BioCasa · BRC LG03 · Prüfung des Entwurfs

Stand: 15. Oktober 2026. Vorlage: `Reihen/BRC_LG01/LS06`, Commit `bcd1140e0a86287709a9709a20ac2ad618b23f6b`.

**Ergebnis: Inhalte, Dateien und lokale Browserfunktionen bestanden. Bildvollständigkeit ausdrücklich nicht bestätigt.** Die 24 bereitgestellten Originalbilder konnten wegen der Transfergrenze von 32 MiB für das hochgeladene ZIP nicht importiert werden. Es wurden keine Ersatzbilder verwendet. Vor Abschluss sind Bildimport, Neubau einschließlich PDFs und erneute Prüfung ohne Ausnahmeflags erforderlich.

## Inhalt und Dateien

Prüfbefehl: `python tools/verify_lg03_content.py --skip-image-check`. Ergebnis: PASS, Exit 0; Bilder SKIP.

- Zwölf Lernsituationen, 80 UE, fünf alternative Lernwege je LS und sechs Phasen der vollständigen Handlung.
- Alle 360 Originalaufträge vollständig in HTML sowie den zugehörigen Phasen- und Gesamtheft-PDFs nachgewiesen. Reihenfolge, Minutenbudgets, Kriterien und operative Fortsetzungen erhalten.
- 86 nummerierte Originalmaterialien und 1.647 Originaltabellenzellen geprüft. Lehrkräfteanhänge vollständig und getrennt von Schülerunterlagen; Orientierung ohne redaktionelle Lehrkräftehinweise.
- 180 ursprüngliche Buchhinweise beim Auftrag. 41 Hinweise mit bloßen Seitenzahlen erhalten 105 belegte Stichwort-Ergänzungen aus 40 LS-/Seitenzuordnungen. Originalseiten bleiben erhalten; Bezeichnung „Lehrbuch“.
- 432 PDF-Dateien: je LS 30 Phasenfassungen, fünf Gesamtarbeitshefte und ein Gesamtdruck.
- Zwölf SCORM-Manifeste mit Dateien im ZIP-Wurzelverzeichnis sowie zwölf bytegleiche Einzelarchive und das Sammelarchiv geprüft.
- Die Runtime-JavaScript-Dateien entsprechen der freigegebenen LS06-Vorlage. Für LG03 werden die vorhandenen, durch die Lehrkraft steuerbaren Lernweg-Auswahlfelder wieder eingeblendet.

Die 60 Einstiegskontrollen und die Gewichtungen im Kompetenznetz sind redaktionelle Ergänzungen für die vorhandene Vorlage. Sie werden nicht als Originalaufgaben bzw. vorgegebene RRL-Gewichte ausgegeben.

## Browser

Prüfer: `tools/verify_lg03_browser.py`, Chromium mit SCORM-1.2-API-Simulation, Ausnahmeflag `--allow-missing-images`. [Konsolidierter Bericht](BRC_LG03_Browserpruefung.json): **96 von 96 Prüfbereichen bestanden**.

| Prüfbereich | Umfang |
|---|---:|
| Aufgabenaktionen mit echten phasen- und lernwegbezogenen GoodNotes-PDF/Share-Payloads | 360 |
| Zusätzliche Aufgabenprüfung nach Buchstichwort-Ergänzungen, LS05–09 | 150 |
| Phasenübergänge mit Sperren oben, unten und bei Direktaufruf | 300 |
| Material-/Lernwegkombinationen mit Aufgabenrücksprung und URL-Kontext | 665 |
| Ansichtsbreiten in Pixeln, alle zwölf LS | 390 / 768 / 1024 |

Geprüft wurden außerdem die vollständige Handlung, Quizrückmeldungen, manueller Aufgabenwechsel, blaue Fokuskarten, grüne Erledigt-Karten, Materialrücksprung bei gesperrtem sessionStorage, Lehrkräftefreigabe der Lernwegauswahl, gespeicherte Editoränderungen und echte konfigurierte SCORM-ZIP-Exporte. SCORM-Speicherung, Kompetenzberichte und Wiederaufnahme gespeicherter Aufgaben und Belege bestanden in der Simulation.

Breite Kostentabellen scrollen innerhalb des vorhandenen Materialrahmens. Zahlen bleiben ungeteilt, ohne Seitenüberlauf. Die lange Materialauswahl lässt sich vor dem Aufgabenfokus regulär einklappen.

## Grenzen und Fertigstellung

Die unveränderte AIS-Einbettung und ihre Dialogfunktion wurden lokal geprüft; die Anmeldung am tatsächlichen Dienst war nicht Bestandteil der Prüfung. Ebenso sind die native Moodle-App und die tatsächliche Übergabe an die native GoodNotes-App nicht durch lokale Browser- und API-Simulationen bestätigt.

Nach Eingang der Originalbilder:

1. Mit `tools/import_lg03_images.py` importieren und Zuordnung aller 24 Originale prüfen.
2. Ohne `--allow-missing-images` neu bauen.
3. Inhaltsprüfung ohne `--skip-image-check` und Browserprüfung ohne `--allow-missing-images` ausführen; Bildansichten prüfen.
4. Entwurfskennzeichnung entfernen und aktualisierte Pakete bereitstellen.

GitHub-Änderungen aktualisieren keine bereits in Moodle hochgeladenen SCORM-Pakete.
