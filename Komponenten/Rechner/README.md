# BBS-Rechner

Verschiebbarer Grundrechner für Lernsituationen und ihre SCORM-Pakete. Abgerundete, leicht transparente Oberfläche in BBS-Blau, Dunkelblau und Grün. Enthalten sind +, −, ×, ÷, Prozent, Dezimalkomma, Vorzeichenwechsel und AC.

Der Rechner öffnet sich auf Wunsch über einen kleinen Button in Aufgabenphasen und Materialien. Am Kopf lässt er sich mit Touch oder Maus verschieben; alternativ dienen dort die Pfeiltasten zum Verschieben. Auf kleinen Materialseiten bleibt der Öffner als beschriftetes Symbol zugänglich, ohne den Aufgabenrücksprung zu überdecken. Bei wenig Höhe scrollt nur die Rechnerfläche; der Schließen-Knopf bleibt erreichbar. Die Orientierung und der Druck enthalten keinen zusätzlichen Rechner.

Rechnung, Position und Offen/Geschlossen-Zustand bleiben innerhalb des Lernpakets während der Browsersitzung auch beim Materialwechsel erhalten. Die Komponente arbeitet vollständig mit lokalen Paketdateien. Sie verändert weder Aufgabenhaken noch Quizantworten oder Moodle-Bewertungen und wird nicht als persönlicher Rechenstand exportiert.

## Prozent und Bedienung

- `200 + 10 % =` ergibt `220`.
- `200 − 15 % =` ergibt `170`.
- `200 × 10 % =` ergibt `20`.
- `10 %` ergibt `0,1`.

Punkt vor Strich wird berücksichtigt. Ergebnisse werden mit bis zu 14 signifikanten Stellen angezeigt; damit erscheint beispielsweise `0,1 + 0,2` als `0,3`. Division durch null zeigt einen Fehler; die nächste Ziffer oder AC beginnt eine neue Eingabe.

Bei Fokus im Rechner sind Ziffern, Komma/Punkt, Grundrechenarten, Prozent, Enter, Backspace und Delete bedienbar. Escape schließt den Rechner. Er ist nicht modal; die übrige Aufgabe bleibt bedienbar. Die Bildschirmtasten funktionieren ohne eingeblendete Systemtastatur.

## Einbau und Prüfung

`python tools/install_calculator.py PAKETORDNER …` kopiert die drei lokalen Dateien, ergänzt die vorhandenen HTML-Hüllen und die Manifest-Dateiliste. Unterrichtsinhalte, Konfigurationen und Fortschrittsmetadaten werden nicht verändert. Die Installationsfunktion wird auch bei der Aufbereitung des gelieferten LG01-Paketsets verwendet.

Rechenlogik: `node tools/test_calculator.cjs`. Touch- und SCORM-Prüfung: `python tools/check_calculator.py --delivery work/delivery-v1.5/preview`. Geprüft werden echte Touch-Ereignisse im SCORM-Iframe, Materialwechsel, gespeicherte Position/Rechnung, Tastatur, kleine Displays, Druckausschluss und unveränderter bewerteter Lernstand.

Die Tests verwenden Chromium mit Touch-Eingabe. Sie ersetzen keine Prüfung auf einem physischen iPad oder in der tatsächlichen Moodle-App.
