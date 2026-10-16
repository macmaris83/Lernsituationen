# GitHub-Oberfläche auf vorhandene SCORM-Pakete übertragen

`tools/transfer_scorm_design.py` übernimmt die freigegebene Oberfläche des im
Master-Katalog genannten BRC-Pakets auf ein ausdrücklich bereitgestelltes SCORM.
Es verarbeitet auch ein Sammel-ZIP mit den sechs LG01-Paketen. Die Ausgabe bleibt
außerhalb des Repositorys: Ein solcher Designtransfer ersetzt keinen gepflegten
Master und legt keinen parallelen Master an.

Der tatsächliche Transfer benötigt wie die vorhandene Arbeitsheftaufbereitung
PyMuPDF. Die Regressionstests des Transferwerkzeugs verwenden nur die Standardbibliothek.

```bash
python tools/transfer_scorm_design.py \
  /workspace/upload/BioCasa_LG01_Moodle_Lernpakete.zip \
  /workspace/delivery/lg01 \
  --version 1.1
```

Die Oberfläche stammt jeweils aus dem passenden aktuellen Katalog-Master. Dazu
gehören Aufgabenfokus, Materialrücksprung, kompakter Materialzugriff, Navigation,
Lehrkräfteeditor, Export und gemeinsame Gestaltung. Es wird kein eigenes
Flipbook-Design eingeführt.

Die Inhaltsbereiche sämtlicher HTML-Seiten bleiben zeichengetreu erhalten.
`lesson-data.js`, `progress-meta.js`, Konfiguration, Medienzuordnung und sämtliche
Original-PDFs bleiben bytegleich. Damit bleiben auch Paket-, Aufgaben- und
Kompetenzkennungen sowie bestehende Aufgabensignaturen erhalten. Kompetenzen,
Aufträge, Materialtexte, Buchverweise und Zeitvorgaben werden nicht umformuliert.
Der Fokus nutzt vorhandene aufgabenspezifische Zeitangaben; fehlen diese im
Original, werden keine Zeiten erfunden. Phasenbezogene GoodNotes-Dateien enthalten
unveränderte Seiten der gelieferten Originalarbeitshefte.

Veraltete eingebettete Paketkopien (`package-data.js`) werden entfernt. Der
Lehrkräfteexport liest die tatsächlich aktuellen Dateien aus dem Manifest. Das
Manifest behält seine SCORM-Kennungen, erhält aber eine aktuelle Dateiliste.
Die Anzeigenummer der Lieferung verändert keine Lernstandskennung.

Die Ausgabe enthält sechs einzeln importierbare ZIPs, ein Sammelarchiv und einen
Prüfbericht mit Quellen-, Inhalts-, Fortschritts- und Designprüfsummen. Das
Sammelarchiv zuerst entpacken; in Moodle die Einzelpakete hochladen. Bereits
importierte Moodle-Pakete müssen dort ausdrücklich ersetzt werden.

Vor Verteilung zusätzlich Aufgabenfokus in allen Phasen/Lernwegen, Materialwechsel
und Rücksprung, Phasensperren, Tablet-/Smartphonebreite sowie den Lehrkräfteexport
im Browser prüfen. Ein lokaler SCORM-API-Test ersetzt keine Prüfung in Moodle
oder der nativen Moodle-App.

## Einzelaufgaben und Lehrkräfteansicht in Lieferung 1.2

Nach dem unveränderten Designtransfer trennt der ausdrücklich angeforderte zweite
Schritt eigenständige Arbeitsaufträge in einzelne Karten. Kriterien, Checkpoints,
optionale Hilfen und zusammengehörende Prüfaufträge bleiben bei ihrer Aufgabe.
Die Nummerierung läuft pro Lernweg über alle sechs Aufgabenphasen weiter.
Text, fett markierte Operatoren, Buchbezüge, Materialien und Bilder bleiben
erhalten; erforderliche Einleitungen werden in den getrennten Karten wiederholt.

```bash
python -m pip install lxml reportlab PyMuPDF
python tools/individualize_scorm_tasks.py \
  /workspace/delivery/lg01/BioCasa_LG01_Moodle_Lernpakete_v1.1.zip \
  /workspace/delivery/lg01-einzelaufgaben \
  --version 1.2
```

Die vorhandenen Aufgaben-IDs bleiben erhalten; weitere Teile erhalten stabile
Unterkennungen. Signaturgeprüfte Migrationsregeln übernehmen erledigte alte
Bündel auf ihre Teile. Das Abhaken nur eines neuen Teils erledigt keine weiteren
Teile. Sichtbare Nummern sind von den Speicherkennungen getrennt und werden
auch im Editor-Export fortlaufend berechnet.

Der Zugang unten rechts heißt **Editor**. Nach der bestehenden PIN-Anmeldung
öffnet **Lehrkräfteansicht starten** einen getrennten Teststand mit direktem
Zugang zu sämtlichen Phasen und fünf Lernwegen. **Lösungen anzeigen** öffnet
die richtigen Original-Quizantworten samt Rückmeldung und den vorhandenen
Erwartungshorizont. **Lernendenansicht** beendet diese Ansicht. Der Teststand
schreibt weder Aufgabenhaken noch Kompetenzangaben in den Moodle-Lernversuch.

Der Moodle-Modus `browse` ist eine bedienbare lokale Lernvorschau ohne
Moodle-Schreibzugriffe. `review` bleibt für Lernende schreibgeschützt; die
angemeldete Lehrkräfteansicht kann unabhängig davon verwendet werden.

Die 180 abgeleiteten GoodNotes-Phasenhefte werden aus den aktuellen Einzelkarten
mit denselben Nummern und unveränderten Aufgabentexten erzeugt. Die 42 gelieferten
Original-PDFs bleiben bytegleich erhalten. Der PDF-Zugang öffnet die aktuelle
Druckansicht. Persönliche Test- und Lernstände werden nicht exportiert.

Prüfergebnisse der Lieferung 1.2: `Pruefberichte/BRC_LG01_Einzelaufgaben.md`.
