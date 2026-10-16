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
