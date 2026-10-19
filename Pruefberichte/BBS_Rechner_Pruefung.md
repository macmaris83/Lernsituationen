# BBS-Rechner · SCORM- und Touch-Prüfung

Geprüft am 16. Oktober 2026. [Komponente und Bedienung](../Komponenten/Rechner/README.md).

Der Rechner ist in den sechs BRC-LG01-Katalogmastern, beiden Lernsituationsvorlagen und allen sechs ausdrücklich hochgeladenen LG01-Paketen enthalten. Die Katalogexporte tragen Version 1.3; die eigenständige Lieferung trägt Version 1.6. In den acht Katalogmastern bleiben Inhaltsdaten, Konfigurationen und Fortschrittsmetadaten bytegleich.

Sieben Rechenlogik-Tests bestanden: Grundrechenarten, Punkt-vor-Strich, Dezimalkomma, Rundungsdarstellung, Prozent mit Aufschlag/Rabatt, Vorzeichen, AC, Korrektur, wiederholtes Gleich, Division durch null, Wiederaufnahme und Prüfung gespeicherter Daten. Befehl: `node tools/test_calculator.cjs`.

[14 Browserprüfungen innerhalb echter SCORM-Iframes](BBS_Rechner_Pruefung.json) bestanden. Der Rechner startet geschlossen, berechnet über Touch-Tasten, lässt sich mit echten Touch-Ereignissen verschieben und scrollt dabei nicht die Aufgabe. Rechenstand, ausstehende Operation und Position bleiben nach dem Materialwechsel erhalten. Geprüft sind außerdem Tastatureingabe, Pfeiltasten-Verschieben, Escape, kleine Ansichten bis 667 × 320 Pixel, der freie Aufgabenrücksprung auf schmalen Materialseiten und der Druckausschluss. Ein Vergleich des vollständigen bewerteten Lernstands vor und nach dem Rechnen bestätigt dessen Unverändertheit.

Die 180 Fokusprüfungen des hochgeladenen LG01-Paketsets sind mit Rechner erneut bestanden. Sechs tatsächlich erzeugte Lehrkräfteexporte enthalten die aktuellen Rechnerdateien. Die zentrale Prüfung `python tools/master.py check --archives` bestätigt alle 40 registrierten Masterarchive einschließlich der acht neu exportierten Fassungen.

Die Komponente benötigt keine externe Internetverbindung. Rechnung und Position stehen ausschließlich im lokalen Sitzungsspeicher des Lernpakets und werden nicht an Moodle-Bewertungen übergeben oder als persönliche Eingaben exportiert.

Die Tests liefen in Chromium mit Touch-Eingabe. Ein physisches iPad und die tatsächliche Moodle-App wurden damit nicht getestet.
