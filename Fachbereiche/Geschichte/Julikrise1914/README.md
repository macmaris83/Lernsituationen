# Julikrise 1914 · Vom Mythos zum Krieg · Version 1.8.3

Sechs eigenständige SCORM-1.2-Master: Deutsches Reich, Frankreich, Großbritannien, Österreich-Ungarn, Russland und Presse. Die internen Lernstandskennungen bleiben erhalten.

Die sechs offenen Phasenaufträge dienen der Strategieplanung, dem Spiel, dem historischen Vergleich und der Erklärung von Unterschieden. Für die Presse sind mindestens zwei veröffentlichte Zeitungsausgaben verbindlich; der AIS-Spielberater darf unterstützen.

Das Lernvideo startet über eine kompakte Vorschau. Videofragen, Wiederaufnahme, Überspringen und Nacharbeits-Hinweise sind integriert. Historische Flaggen stehen bei den Länderrollen. Die kleine Fußzeilen-Version wird aus der Paketversion des jeweiligen Masters gelesen.

## Verwendung

Aktuelle ZIPs stehen unter `Downloads/` über den Master-Katalog bereit. In Moodle jede Rolle als eigene SCORM-Aktivität für das passende Team bereitstellen. Lehrkräfte-Material und die Gesamtübersicht gehören nicht in die Schüleraktivitäten.

`python tools/master.py export --all` exportiert den aktuellen Quellstand. Keine früheren Inhaltsgeneratoren ausführen. Die vorhandenen Aufgaben-, Quiz-, Video- und Begriffsprüfungen behalten ihre Kennungen.

Lösungen, Spielleitung und Originalmaterialien stehen separat unter `Lehrkraft/`; der ergänzte Presse-Rollenauftrag unter `Presse/`.
