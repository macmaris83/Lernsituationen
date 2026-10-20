# BioCasa · BRC LG03 · Abschlussprüfung

Stand: 15. Oktober 2026, Paketfassung `2026-10-15.lg03.2`. Vorlage: `Reihen/BRC_LG01/LS06`, Commit `bcd1140e0a86287709a9709a20ac2ad618b23f6b`.

**Ergebnis: Inhalte, Originalbilder, Dateien und lokale Browserfunktionen bestanden.** Sämtliche Prüfungen der fertigen Fassung erfolgten ohne Ausnahme für fehlende Bilder oder PDF-Payloads.

## Inhalt, Bilder und Dateien

Prüfbefehl: `python tools/verify_lg03_content.py`. Ergebnis: PASS, Exit 0.

- Zwölf Lernsituationen, 80 UE, fünf alternative Lernwege je LS und sechs Phasen der vollständigen Handlung.
- Alle 360 Originalaufträge vollständig in HTML sowie den zugehörigen Phasen- und Gesamtheft-PDFs nachgewiesen. Reihenfolge, Minutenbudgets, Kriterien und operative Fortsetzungen erhalten.
- 86 nummerierte Originalmaterialien und 1.647 Originaltabellenzellen geprüft. Lehrkräfteanhänge vollständig und getrennt von Schülerunterlagen; Orientierung ohne redaktionelle Lehrkräftehinweise.
- 180 ursprüngliche Buchhinweise beim Auftrag. 41 Hinweise mit bloßen Seitenzahlen erhalten 105 belegte Stichwort-Ergänzungen aus 40 LS-/Seitenzuordnungen. Originalseiten bleiben erhalten; Bezeichnung „Lehrbuch“.
- Alle 24 Originalbilder aus den beiden gelieferten Archiven visuell zugeordnet und bytegenau über Import, Bildzuordnung, Paket und ZIP verglichen. Keine Ersatzbilder, Neubearbeitung oder Neukomprimierung der PNG-Dateien. Originalauflösungen: 1672 × 941 Pixel, LS02-Orientierung 1672 × 940 Pixel.
- In jedem Gesamtdruck sind beide Bildobjekte in Originalauflösung enthalten: Orientierung auf Seite 1, Handlungssituation auf Seite 3. Alle 24 PDF-Bildansichten zusätzlich visuell mit den Originalen verglichen; keine Vertauschungen oder motivischen Beschneidungen.
- 432 PDF-Dateien: je LS 30 Phasenfassungen, fünf Gesamtarbeitshefte und ein Gesamtdruck.
- Zwölf SCORM-Manifeste, zwölf bytegleiche Einzelarchive und drei unabhängig entpackbare Sammelarchive geprüft. LS01–04, LS05–08 und LS09–12 enthalten jeweils exakt vier vollständige Einzelpakete, insgesamt zwölf ohne Doppelungen oder Lücken. Alle Sammelarchive bleiben unter 100 MiB.
- Die Originalquelle und neun gemeinsame Runtime-JavaScript-Dateien entsprechen unverändert der Quelle bzw. freigegebenen LS06-Vorlage. Sämtliche Fortschrittsmetadaten und Inhaltssignaturen sind gegenüber der vorherigen LG03-Fassung unverändert.

Die 60 Einstiegskontrollen und die Gewichtungen im Kompetenznetz sind redaktionelle Ergänzungen für die vorhandene Vorlage. Sie werden nicht als Originalaufgaben bzw. vorgegebene RRL-Gewichte ausgegeben.

## Browser

Prüfer: `tools/verify_lg03_browser.py`, Chromium mit SCORM-1.2-API-Simulation. Die zwölf LS wurden in zwei parallelen Sechsergruppen ohne `--allow-missing-images` oder `--skip-pdf` geprüft. [Konsolidierter Bericht](BRC_LG03_Browserpruefung.json): **96 von 96 Prüfbereichen bestanden**.

| Prüfbereich | Umfang |
|---|---:|
| Aufgabenaktionen mit echten phasen- und lernwegbezogenen GoodNotes-PDF/Share-Payloads | 360 |
| Phasenübergänge mit Sperren oben, unten und bei Direktaufruf | 300 |
| Material-/Lernwegkombinationen mit Aufgabenrücksprung und URL-Kontext | 665 |
| Bildansichten: 24 Originalbilder bei 390 / 768 / 1024 Pixeln | 72 |

Bilder werden tatsächlich geladen und dekodiert. Geprüft sind natürliche Abmessungen, Zuordnung, Alternativtexte, unverändertes Seitenverhältnis, vollständige sichtbare Bildfläche und unveränderte Originalbytes im bearbeiteten SCORM-Export.

Geprüft wurden außerdem die vollständige Handlung, Quizrückmeldungen, manueller Aufgabenwechsel, blaue Fokuskarten, grüne Erledigt-Karten, Materialrücksprung bei gesperrtem sessionStorage, Lehrkräftefreigabe der Lernwegauswahl, gespeicherte Editoränderungen und echte konfigurierte SCORM-ZIP-Exporte. SCORM-Speicherung, Kompetenzberichte und Wiederaufnahme gespeicherter Aufgaben und Belege bestanden in der Simulation.

Breite Kostentabellen scrollen innerhalb des vorhandenen Materialrahmens. Zahlen bleiben ungeteilt, ohne Seitenüberlauf. Die lange Materialauswahl lässt sich vor dem Aufgabenfokus regulär einklappen.

Visuelle Beispiele: [Orientierung](BRC_LG03_Orientierung.png), [Handlungssituation](BRC_LG03_Handlungssituation.png), [Aufgabenfokus](BRC_LG03_Aufgabenfokus.png) und [Kostentabelle](BRC_LG03_Kostentabelle.png).

## Grenzen der Prüfung

Die unveränderte AIS-Einbettung und ihre Dialogfunktion wurden lokal geprüft; die Anmeldung am tatsächlichen Dienst war nicht Bestandteil der Prüfung. Ebenso sind die native Moodle-App und die tatsächliche Übergabe an die native GoodNotes-App nicht durch lokale Browser- und API-Simulationen bestätigt.

GitHub-Änderungen aktualisieren keine bereits in Moodle hochgeladenen SCORM-Pakete. Für den Unterricht ist die neue Paketfassung hochzuladen.
