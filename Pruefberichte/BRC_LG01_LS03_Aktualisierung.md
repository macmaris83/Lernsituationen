# Businessplan LG01–LS03: aktualisiertes SCORM-Paket

Stand: 9. Oktober 2026. Grundlage: hochgeladenes `BRC_LG01_LS03_SCORM (1).zip`.

## Inhalt und Zeiten

Originale Aufgabenstellungen, Materialien, PDFs, GoodNotes-Dateien, Konfiguration und Fachkompetenzen bleiben unverändert. Auf ausdrücklichen Nutzerwunsch wurden ausschließlich Orientierungszeiten für die 83 Aufgaben ergänzt, nach Umfang und Anspruch verteilt. Die Zeiten ergeben in allen fünf alternativen Lernwegen exakt die jeweilige Phasenzeit. Die Lernwege werden nicht addiert.

| Phase | Minuten je Lernweg |
| --- | ---: |
| Informieren | 270 |
| Planen | 135 |
| Entscheiden | 135 |
| Durchführen | 180 |
| Bewerten | 45 |
| Reflektieren | 45 |
| Gesamt | **810** |

Die einzelnen Zuordnungen stehen in [businessplan_aufgabenzeiten.json](../tools/businessplan_aufgabenzeiten.json).

## Materialnavigation – Ergänzung vom 9. Oktober 2026

Auf allen zehn Materialseiten gibt es zusätzlich eine kompakte blaue Phasenübersicht mit allen acht Stationen der vollständigen Handlung. Unter dem Material führen „Zurück“ zur Ausgangsphase und „Weiter“ zur folgenden Phase. Die Ausgangsphase wird aus der zuletzt geöffneten Aufgabe übernommen; ohne vorherige Aufgabe gilt Informieren als Ausgangspunkt. Der schwebende Rücksprung zur konkreten Aufgabe und die einzige hellgrüne Materialleiste bleiben bestehen. Gesperrte Phasen bleiben auch von Materialseiten aus gesperrt. Die große Stationsübersicht und GoodNotes-Teilen bleiben dort ausgeblendet.

## Technik und Oberfläche

Der freigegebene Lernsituationsstandard wurde übernommen: Aufgabenakkordeon, vollständige Arbeitsaufträge, gemeinsame Kopfzeile für Fachkompetenz und Uhr, manuelles Weiter nach Erledigt-Markierung, hellgrüne erledigte Karten, Materialleiste mit Rücksprung zur Aufgabe, AIS-Hilfe im Dialog sowie Phasenfreischaltung. Lehrkräfte-Änderungen erscheinen auch im Fokus und im neuen Export. Countdown-Zeiten bleiben beim Materialwechsel erhalten.

Originale SCORM-Schnittstelle und Codec, Aufgaben-IDs, Aufgaben-Signaturen, Fortschrittsmetadaten und Kompetenzberichtstruktur bleiben erhalten. Die hinzugefügten Zeitangaben werden vor der Signaturberechnung entfernt, sodass eine reine Zeitänderung vorhandene Erledigt-Markierungen nicht ungültig macht.

## Durchgeführte Prüfungen

- Redaktioneller Vergleich: Nach Entfernen der ergänzten Zeitspannen entsprechen die Lernsituationsdaten exakt dem Original. Materialien, PDFs, Medien, Konfiguration und SCORM-Dateien wurden zusätzlich auf Bytegleichheit geprüft.
- Alle 83 Aufgaben in sämtlichen sechs Phasen und fünf Lernwegen im Browser geprüft: vollständiger Text, Timer, Kopfzeile ohne Einklapp-Link, manuelles Weiter, Erledigt-Markierung, Materialzugriff und Layout.
- Alle 30 Kombinationen aus Phase und Lernweg: Zeitsummen und Originalsignaturen geprüft.
- 25 Phasenübergänge: Sperren in Navigation und bei direktem Seitenaufruf geprüft.
- Timer: Grün/Schwarz/Rot, Pause/Fortsetzen, Ablauf und Tonsignal geprüft. Materialwechsel M2 → M3 → ursprüngliche Aufgabe mit erhaltener Restzeit geprüft.
- Lehrkräfte-Editor: PIN-Prüfung, gespeicherte Zeitänderungen, Anzeige im Akkordeon und tatsächlicher ZIP-Export mit aktuellen Assets und unveränderten Fortschrittssignaturen geprüft.
- SCORM-API-Simulation: Commit, Kompetenzberichte, ursprüngliche Aufgabenkennungen und Wiederaufnahme geprüft.
- Ansichten bei 1024 × 768, 768 × 1024 und 390 × 844 Pixeln geprüft.
- Neue Materialnavigation: alle zehn Materialien in allen fünf Lernwegen, Phasensperren, kontextabhängige Zurück-/Weiter-Ziele und tatsächliche Wechsel zu Phasen geprüft.
- Fertige ZIP: fehlerfrei entpackbar, Manifest direkt im Wurzelverzeichnis, alle referenzierten Dateien vorhanden, alle Dateiinhalte identisch mit dem geprüften Arbeitsverzeichnis.

Die Prüfungen erfolgten lokal mit Chromium und einer SCORM-API-Simulation. Tatsächlicher Moodle-Betrieb, iPad-Tonverhalten und AIS-Einbettung/Anmeldung müssen im jeweiligen Zielsystem geprüft werden. Der AIS-Dialog wurde mit einer simulierten Antwort geprüft.

## Dateien und Reproduktion

- [Fertiges SCORM-ZIP](../Downloads/BRC_LG01_LS03_Aktualisiert_SCORM.zip)
- [Aufgabenfokus als Screenshot](BRC_LG01_LS03_Aufgabenfokus.png)
- Aufbau: `python tools/prepare_businessplan_scorm.py ORIGINAL.zip AUSGABEORDNER`
- Prüfung: `python tools/verify_businessplan_scorm.py ORIGINAL.zip AUSGABEORDNER`
- Voraussetzungen für die Prüfung: Python 3, Node.js, Python-Paket Playwright, Chromium unter `/usr/bin/chromium`. Die Prüfung startet ihren HTTP-Server selbst und beendet ihn anschließend.

ZIP-SHA256: `0cc2d0b30fb14c48eaf85c0104390478845a47abe5e6438a2de7ae53a8fb90af`
