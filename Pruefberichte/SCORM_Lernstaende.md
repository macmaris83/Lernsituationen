# SCORM-Lernstände bei Paketupdates

Die sichtbare Paketversion ist unabhängig von der festen Lernstandskennung. Bei Updates bleiben Paket-, Aufgaben- und Kompetenzkennungen erhalten. Der zentrale Export prüft die feste Identität gegen die vorherige ZIP und stoppt vor dem Ersetzen, wenn versehentlich andere Kennungen oder Startdateien verwendet werden. Originalpakete und ihre Fortschrittsmetadaten werden bei der Aufbereitung zusätzlich direkt verglichen.

Ein passender gespeicherter Moodle-Lernstand wird übernommen: Aufgabenhaken, gelesene Orientierung, Quizantworten, Kompetenzbelege, Feedback und nächster Lernschritt. Reine Designänderungen setzen diese Angaben nicht zurück. Fachlich bearbeitete Aufgaben werden weiterhin über ihre Inhaltssignaturen erkannt.

## Behobene Sperre

Die bisherige Runtime setzte das gesamte Paket auf schreibgeschützt, sobald Moodle einen Lernstand mit anderer Kennung oder anderem Datenformat lieferte. Dadurch blieb „Orientierung gelesen“ unabhängig von den Eintragungen deaktiviert. Selbst die Lernvorschau wurde durch diese Prüfung blockiert.

Die Lernvorschau liest jetzt keine bewerteten Moodle-Speicherdaten und hat einen eigenen beschreibbaren lokalen Stand. Im normalen Versuch wird ein passender Stand weiterhin in Moodle gespeichert. Bei einem tatsächlich fremden, inkompatiblen oder nicht lesbaren Altstand bleibt dieser in Moodle unverändert. Das Paket ermöglicht dann getrenntes lokales Weiterarbeiten, statt die Bedienung zu sperren. Eine klare Meldung erklärt die lokale Speicherung und dass in Moodle ein neuer Versuch nötig ist. Dieser lokale Ersatzstand wird zusätzlich nach Schülerkennung getrennt; er ersetzt keine Moodle-Speicherung. Der Review-Modus bleibt schreibgeschützt.

## Nachweis

[188 Browserfälle](SCORM_Lernstand_Pruefung.json) bestanden: 182 Regressionen in beiden Lernsituationsvorlagen und zwölf LG01-Paketen sowie sechs tatsächliche komprimierte SCORM-Updates von Original 1.4 auf 1.6. In diesen sechs Updates bleiben sämtliche 628 Aufgabenstände, 30 Quizantworten, 30 Kompetenzbelege und sechs bereits gelesenen Orientierungen erhalten, ebenso Feedback, nächster Lernschritt und Berichtindex. Weiteres Schreiben und erneutes Laden sind geprüft.

Die Konfliktfälle prüfen ausdrücklich unveränderte Moodle-Daten und null Schreib-/Commit-Aufrufe. Lokale Vorschau, Wiederaufnahme, Schülerwechsel und schreibgeschütztes Review sind enthalten. Vor der Korrektur scheiterten 24 von 39 gezielten Baseline-Fällen.

Reproduzieren: `python tools/check_scorm_resume.py --all --delivery work/delivery-v1.6/preview --upgrade-from work/input-v1.4`. Die Exportsicherung ist zusätzlich durch 27 Tests von `tools/test_master.py` geprüft.

Die Browserprüfungen verwenden Chromium und eine SCORM-1.2-API-Simulation. Der tatsächliche Moodle-Server und die Moodle-App waren nicht Bestandteil dieser lokalen Prüfung. Bereits hochgeladene Moodle-Aktivitäten benötigen die neue ZIP-Fassung.
