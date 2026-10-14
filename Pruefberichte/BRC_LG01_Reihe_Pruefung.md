# BRC LG01 · Prüfung der neu aufgebauten Plug-and-Play-Reihe

Stand: 14.10.2026. Grundlage ist der vom Nutzer bereitgestellte narrative Reihenplan; Oberfläche und SCORM-Technik stammen aus der zuletzt freigegebenen Vorlage (Ausgangscommit `712a120`).

## Umfang

| LS | Titel | UStd. | Minuten | Aufgabenkarten |
|---|---|---:|---:|---:|
| LS01 | Eine Geschäftsidee entwickeln | 12 | 540 | 97 |
| LS02 | Eine Unternehmensberatung besuchen | 8 | 360 | 94 |
| LS03 | Einen Business-Plan erstellen | 18 | 810 | 94 |
| LS04 | Bei Kapitalgebern pitchen | 12 | 540 | 93 |
| LS05 | Ein Unternehmen gründen | 14 | 630 | 93 |
| LS06 | Geschäfte abwickeln | 16 | 720 | 102 |

Die Aufgabenkarten bilden die nummerierten Arbeitsaufträge sowie die vollständig enthaltenen unnummerierten Aufträge, Prüfkriterien und Checkpoints ab. Fünf alternative Wege je LS ergeben 30 Lernwege und 180 Phasenblöcke; die Alternativen werden zeitlich nicht addiert. 34 originale Materialien, sechs fachsystematische Sicherungen und sechs KI-Hinweise sind enthalten.

## Inhalt und Technik

- Sämtliche Aufgaben und Originalmaterialien wurden nach dem Rendern gegen den Quellplan verglichen; kein Auftrags- oder Materialtext gekürzt.
- Die 30 Kompetenzbeschreibungen und sechs vorrangigen Kompetenzen sind in vollständige Ich-Aussagen übertragen; Gewichtungen bleiben erhalten.
- 30 ergänzende fallbezogene Einstiegskontrollen mit je sechs Antwortmöglichkeiten wurden unabhängig gegen Fallgeschichte, Materialien und Erwartungshorizonte gegengeprüft. Genau eine Option je Frage ist begründet richtig.
- Je LS sind 30 phasenbezogene GoodNotes-PDFs und fünf zusammengeführte Arbeitshefte erstellt, insgesamt 180 Teil-Arbeitshefte und 30 Gesamt-Arbeitshefte. Schülerimport bietet nur die aktuelle Phase/den aktuellen Lernweg an.
- Aufgabenzeiten sind zusätzliche Orientierungsvorschläge. Sie summieren sich in jedem Weg exakt zu den Originalphasenbudgets; Dezimal-Minuten und halbe Unterrichtsstunden werden ohne Rundungsverlust in Sekunden verarbeitet.
- Orientierung: vorrangige Kompetenz oberhalb, Netz links, vier weitere Ich-Beschreibungen rechts. Kein Material-/GoodNotes-Zugriff in Orientierung; kein Import in der Handlungssituation.
- Aktuelle Glas-Optik, unverändertes lokales Hintergrundmotiv, lila AIS-Hilfe mit Löppt-Pilot und separate Gesamt-PDF-Fußleiste neben Lehrkraft.
- Materialseiten verwenden die Dokumentansicht der Vorlage, einen kompakten Materialzugriff, die Phasenübersicht darunter und ausschließlich den schwebenden Aufgabenrücksprung. Kein Rücksprung/PDF oben und kein zusätzlicher Weiter-Button.
- Im Fokus sind weitere Karten zuverlässig verborgen. Tight Markdown-Listen sind in Absatzmarkup überführt, sodass mehrere Operatoraufträge untereinander stehen. Die Arbeitsform wird einmal angezeigt.
- Verbleibende Zeit wird bei Materialbesuchen mit dem bewährten Timer-Speicher erhalten. Zeit-UI ist von Aufgabensignaturen ausgenommen.
- Lehrkräfte-Editor verwendet denselben Seiteninhalt wie der Fokus. SCORM-ZIP-Export enthält aktuelle Dateien und neu berechnete Inhaltsmetadaten. Vorgefertigte PDF-Dateien bleiben die ursprüngliche Quellfassung; aktualisierte Druckansicht für Editoränderungen verwenden.
- Sechs unabhängige LS-Kennungen und 30 unterschiedliche Kompetenz-/Berichtskennungen verhindern Verwechslungen zwischen den neuen Paketen.

## Validierung

Der vollständige Quellenvergleich `tools/verify_brc_editorial.py` ist für alle sechs LS bestanden. Die vollständige Matrixprüfung ist für alle **573 Aufgabenkarten** in 30 Lernwegen/180 Phasen bestanden (285 Karten in LS01–03, 288 in LS04–06). Dazu gehören vollständige Aufträge, Operatorabsätze, genau eine Sozialformanzeige, exakte Phasenzeit-Summen, Countdown, getrenntes Erledigt/Weiter, ausgeblendete weitere Karten und eindeutige Statusfarben.

Alle 180 tatsächlichen Phase-PDF-Übergaben wurden mit Web-Share-Mocks geprüft. Die 150 möglichen Übergänge zwischen Aufgabenphasen wurden bei noch offener Vorgängeraufgabe sowohl in der Navigation als auch beim direkten Aufruf gesperrt. Alle Materialien wurden in allen fünf Wegen sowie zusätzlich bei 1024/768/390 Pixeln geprüft, einschließlich verweigertem Sitzungsspeicher, korrektem Aufgabenrücksprung, Phasenwahl, Flyover-Anklickbarkeit und simuliert verkleinertem sichtbarem WebView-Viewport.

SCORM-API-Speicherung, unabhängige Kompetenzberichte und Wiederaufnahme einschließlich abgeschlossenem Lernweg sind in allen sechs Paketen bestanden. Der repräsentative LS01-Editor-Test prüfte gespeicherte Auftragsänderung in Übersicht/Fokus, tatsächlichen ZIP-Export und unveränderte Aufgabensignatur bei einer reinen Zeit-UI-Änderung. Zusätzlich wurden Timer-Restzeit nach M1 → M2 → Aufgabe, Farben Grün/Schwarz/Rot, Pause, Ablauf, optionaler Ton, Stummschalter und KI-Dialog auf derselben Seite geprüft.

Ein später korrigierter Grammatikfehler betraf ausschließlich eine falsche Antwortoption in LS04; fachlicher Inhalt und richtige Antwort blieben gleich. Nach der Korrektur wurden alle Archive/Metadaten und die LS04-Navigation, Materialien, SCORM-/Editor-/Timer-Prüfungen erneut kontrolliert.

Die Prüfungen verwenden Chromium, SCORM-API-Mocks, Web-Share-Mocks und einen lokalen AIS-Dialog-Mock. Native Moodle-App, native GoodNotes-Übergabe, reale AIS-Einbettung/Anmeldung und Ton auf dem iPad wurden nicht als tatsächlich geprüfte Appfunktionen ausgegeben.

## Artefakte und Reproduktion

Sechs Einzel-ZIPs enthalten `imsmanifest.xml` direkt im Archivwurzelverzeichnis. Das [Gesamtarchiv](../Downloads/BRC_LG01_PlugAndPlay_Gesamtreihe_SCORM.zip) enthält diese sechs ZIPs und eine kurze Anleitung; es muss vor dem Upload einzelner Moodle-Aktivitäten entpackt werden. Die alte einzelne Businessplan- und Sozialpädagogik-Ausgabe sind getrennt davon.

- `python tools/build_brc_series.py`
- `python tools/verify_brc_editorial.py`
- `python tools/verify_brc_series.py --source Quellen/BRC_LG01/Reihenplan.md`

Anleitung und Einzelpakete: [Reihe](../Reihen/BRC_LG01/README.md).

## Sichtprüfung

- [Kompetenzprofil](BRC_LG01_Reihe_Kompetenzen.png)
- [Aufgabenfokus](BRC_LG01_Reihe_Aufgabenfokus.png)
- [Materialansicht](BRC_LG01_Reihe_Material.png)

## SHA256

- `BRC_LG01_LS01_SCORM.zip` · `606168f571bc965268c6705266eeacdd33d28ad270bab2fd8e8001fe9c86e822`
- `BRC_LG01_LS02_SCORM.zip` · `b543ec5996510850cbfdd8be1346d7ae41e7894004fb79f76e0f1acae68c4aa4`
- `BRC_LG01_LS03_SCORM.zip` · `7560b38b00da79761844c8a8d97b976ecffde7755a8445ce8ec9cd3f64523dba`
- `BRC_LG01_LS04_SCORM.zip` · `d0269b00b87c256fd97936fb034bbfb1f899678feb88f2399c15f378d4156c67`
- `BRC_LG01_LS05_SCORM.zip` · `1fddf7615b49a65f2f962601e4f747b5be821dc5572a3a9aa5ca5bc13e847cef`
- `BRC_LG01_LS06_SCORM.zip` · `9df7418867f5cd0753c7cad1a90d564b4b8c2b87ff8f8d9fa96cfdef97315422`
- `BRC_LG01_PlugAndPlay_Gesamtreihe_SCORM.zip` · `37102ec26220006cdb39a333d1c25f5f2b0c6347ed98c9179260d9132576f3d6`
