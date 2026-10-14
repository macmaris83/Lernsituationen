# BRC LG01 · Prüfung der Plug-and-Play-Reihe

Stand: 14.10.2026. Grundlage ist der vom Nutzer bereitgestellte narrative Reihenplan; Oberfläche und SCORM-Technik stammen aus der zuletzt freigegebenen Vorlage (Ausgangscommit `712a120`). Die neue Fassung verwendet die zwölf separat gelieferten Originalbilder und die freigegebene kompakte Schüleransicht.

## Umfang

| LS | Titel | UStd. | Minuten | Aufgabenkarten |
|---|---|---:|---:|---:|
| LS01 | Eine Geschäftsidee entwickeln | 12 | 540 | 72 |
| LS02 | Eine Unternehmensberatung besuchen | 8 | 360 | 75 |
| LS03 | Einen Business-Plan erstellen | 18 | 810 | 73 |
| LS04 | Bei Kapitalgebern pitchen | 12 | 540 | 70 |
| LS05 | Ein Unternehmen gründen | 14 | 630 | 72 |
| LS06 | Geschäfte abwickeln | 16 | 720 | 78 |
| Gesamt | BioCasa-Gründungsgeschichte | **80** | **3.600** | **440** |

Fünf alternative Wege je LS ergeben 30 Lernwege und 180 Phasenblöcke; die Alternativen werden zeitlich nicht addiert. Alle nummerierten und unnummerierten Arbeitsaufträge bleiben vollständig enthalten. Zusammenhängende Prüfkriterien, Peer-Feedback und Überarbeitung bilden gemeinsam eine Aufgabe; sämtliche Reflexionsfragen stehen mit ihrer Einleitung in einer Aufgabe. Kontrollieren/Überprüfen (`bewerten.html`) und Reflektieren enthalten deshalb je Lernweg genau einen vollständigen Auftrag. Einzelne Kriterien und optionale KI-Hinweise erzeugen keine zusätzlichen Erledigt-Karten. 34 Originalmaterialien, sechs fachsystematische Sicherungen und sechs KI-Hinweise sind enthalten.

## Inhalt und Oberfläche

- Sämtliche Aufgaben und Originalmaterialien werden nach dem Rendern gegen den Quellplan verglichen; kein Auftrags- oder Materialtext wird gekürzt.
- Die 30 Kompetenzbeschreibungen und sechs vorrangigen Kompetenzen sind in vollständige Ich-Aussagen übertragen; Gewichtungen bleiben erhalten. In der Orientierung steht die vorrangige Kompetenz oberhalb, das Netz links und die vier weiteren Ich-Beschreibungen rechts in einem 2×2-Raster. Auf schmalen Smartphones stehen die Kompetenzkarten untereinander.
- Die Schülerorientierung enthält keinen Einordnungsblock, keine Lernwegübersicht, keine Lernweg-Badges und keine Auswahl zwischen W1–W5. Die Lehrkraft wählt und exportiert den vorgesehenen Weg im bestehenden Lehrkräftemodus; die fünf Varianten bleiben vollständig vorhanden.
- 30 ergänzende fallbezogene Einstiegskontrollen mit je sechs Antwortmöglichkeiten wurden unabhängig gegen Fallgeschichte, Materialien und Erwartungshorizonte gegengeprüft. Genau eine Option je Frage ist begründet richtig. Die sechs Antwortmöglichkeiten erscheinen einzeln untereinander.
- Arbeitsformen sind pro Auftrag zugeordnet: Einzelarbeit, Partnerarbeit, Gruppenarbeit, Expertengruppe und externe Partner-Prüfgruppen, statt einer pauschalen Lernteam-Angabe. Bei offenen Wegen sind Vorschläge als Empfehlungen erkennbar. Die Arbeitsform wird in jeder Karte genau einmal mit passendem Symbol angezeigt.
- Je LS sind 30 phasenbezogene GoodNotes-PDFs und fünf zusammengeführte Arbeitshefte erstellt, insgesamt 180 Teil-Arbeitshefte und 30 Gesamt-Arbeitshefte. Schülerimport bietet nur die aktuelle Phase/den aktuellen Lernweg an; in Orientierung und Handlungssituation gibt es keinen Import.
- Aufgabenzeiten sind zusätzliche Orientierungsvorschläge. Sie summieren sich in jedem Weg exakt zu den Originalphasenbudgets; Dezimal-Minuten und halbe Unterrichtsstunden werden ohne Rundungsverlust in Sekunden verarbeitet.
- Die aktuelle Glas-Optik, das unveränderte lokale Hintergrundmotiv, die lila AIS-Hilfe mit Löppt-Pilot und die separate Gesamt-PDF-Fußleiste neben Lehrkraft bleiben erhalten.
- Materialseiten verwenden die Dokumentansicht der Vorlage, einen kompakten Materialzugriff, die Phasenübersicht darunter und ausschließlich den schwebenden Aufgabenrücksprung. Kein Rücksprung/PDF oben und kein zusätzlicher Weiter-Button.
- Im Fokus sind weitere Karten verborgen. Mehrere Operatoraufträge stehen untereinander in Absätzen. Erledigt markieren und Weiter klicken bleiben getrennte Handlungen. Die verbleibende Zeit wird bei Materialbesuchen erhalten; reine Zeit-UI gehört nicht zur Aufgabensignatur.

## Originalbilder, Editor und Lernstände

Je LS sind das zugehörige Orientierungs- und Handlungssituationsbild aus der gelieferten Bildsammlung lokal enthalten: **zwölf unveränderte PNG-Dateien**, ohne Neuerzeugung, Neukodierung oder Beschnitt. Zuordnung, Alternativtexte und Ursprungsdateinamen stehen in `Quellen/BRC_LG01/Bildzuordnung.json`. Bytevergleich und SHA256 bestätigen dieselben Dateien in Quelle, Paket und Lehrkräfteexport; die Medienzuordnung verweist auf diese Originale.

Der Lehrkräfte-Editor verwendet denselben Seiteninhalt wie der Aufgabenfokus. Gespeicherte Änderungen erscheinen nach Neuladen in Übersicht und Fokus. Der tatsächliche SCORM-ZIP-Export enthält aktuelle Dateien, neu berechnete Inhaltsmetadaten, beide zugeordneten Originalbilder und die aktuelle Medienzuordnung. Vorgefertigte PDF-Dateien bleiben die ursprüngliche Quellfassung; für gespeicherte Editoränderungen ist die aktuelle Druckansicht zu verwenden.

Die sechs LS-Kennungen und 30 Kompetenz-/Berichtskennungen bleiben gegenüber der vorherigen BioCasa-Reihenfassung erhalten und sind zwischen den LS unabhängig. Vorhandene Aufgabenkennungen werden bei Zusammenfassung konservativ migriert: Eine neue Gruppenaufgabe gilt erst als erledigt, wenn **sämtliche** alten Teilaufgaben mit ihrer gültigen Inhaltskennzeichnung erledigt waren. Eine nur teilweise bearbeitete Prüfung bleibt offen. Alte Aufgabenrücksprünge werden einer passenden neuen Gruppenaufgabe zugeordnet. Bereits gelesene Orientierung und Kompetenzberichte bleiben bei gültiger Migration erhalten; fremde LS-Kennungen werden nicht übernommen. Ein später im Lehrkräfte-Editor geänderter Orientierungstext verlangt erneut eine Lesebestätigung: Der alte Lesestatus wird nur für den unveränderten Zieltext dieser Layoutüberarbeitung übernommen. Aufgabenmarkierungen und Kompetenzberichte bleiben dabei unabhängig erhalten. Die Migrationsmetadaten enthalten Inhaltskennungen, keine personenbezogenen Lernstände.

### SHA256 der zwölf Originalbilder

| LS | Verwendung | Originaldatei im Paket | SHA256 |
|---|---|---|---|
| LS01 | Orientierung | `biocasa-ls01-orientation.png` | `2ffe7dc03588163338c1e1168655f58ef6f89492ec86a95e0b2943c9952a8fc8` |
| LS01 | Handlungssituation | `biocasa-ls01-situation.png` | `c6686349bf2ee6a2769ee1b9b79534172e0cc3bd9c7dd1526d7c57168471f860` |
| LS02 | Orientierung | `biocasa-ls02-orientation.png` | `383855fb1c4598087f1605517816fb273823691ab0e86954cbbb924bf04988c1` |
| LS02 | Handlungssituation | `biocasa-ls02-situation.png` | `dfd69676dc3fc3249c6792f518a4571d433011ae3afb2431de14e05512ddd89f` |
| LS03 | Orientierung | `biocasa-ls03-orientation.png` | `0fb4cec24cece9769e05fc83efcfcded504a836540dda66cdda0ff5dd3f28bcb` |
| LS03 | Handlungssituation | `biocasa-ls03-situation.png` | `ccbe6add46edcde8170f1c4267f445f24fafbf73399236bfb9ec6abbb74dd11c` |
| LS04 | Orientierung | `biocasa-ls04-orientation.png` | `42262cc0614c70e2cc4e9dc8e8f06a6fd8c6cc0a1f74095057f64df5b1be18d6` |
| LS04 | Handlungssituation | `biocasa-ls04-situation.png` | `410b4960d668244e95fa5d64266b1adb9602caf53001deeef57c6891c51858d6` |
| LS05 | Orientierung | `biocasa-ls05-orientation.png` | `8a97ca6c4c2931756808ff8cf769f0b745dc87f8aaec533938b04c2c167cc8e2` |
| LS05 | Handlungssituation | `biocasa-ls05-situation.png` | `218fb279ba9f6909b3861d970e1acd4fee9d46251cabf630fd0b3929cb1412fe` |
| LS06 | Orientierung | `biocasa-ls06-orientation.png` | `99ed7cce1b0062eb5d08645ac52a17edd17fbef5ae8227078903208e40443494` |
| LS06 | Handlungssituation | `biocasa-ls06-situation.png` | `8705f0724f2c475578f719814cf7d6834fe80551e26d0c1d82f02997dad7edbc` |

## Validierung

Der vollständige Quellenvergleich `tools/verify_brc_editorial.py` ist für alle sechs LS bestanden. Die vollständige Matrixprüfung ist für alle **440 Aufgabenkarten** in **30 Lernwegen/180 Phasen** bestanden. Sie prüft vollständige Aufträge, Operatorabsätze, genau eine passende Sozialformanzeige, exakte Phasenzeit-Summen, Countdown, getrenntes Erledigt/Weiter, ausgeblendete weitere Karten und eindeutige Statusfarben. Für alle Bewerten-/Reflektieren-Blöcke wird die gemeinsame Darstellung als jeweils ein vollständiger Auftrag geprüft.

Die statische Artefaktprüfung kontrolliert die sechs unabhängigen LS und 30 Kompetenzkennungen, alle Manifestdateien, die zwölf Originalbilder einschließlich SHA256/Medienzuordnung, die differenzierten Arbeitsformen sowie die vollständigen GoodNotes-Dateien. Die Matrixprüfung enthält alle 180 tatsächlichen Phase-PDF-Übergaben über Web-Share-Mocks.

**Abschließender Teststatus:** Alle sechs Pakete und das Gesamtarchiv sind bestanden. Die vollständige 440-Aufgaben-Matrix, sämtliche ergänzenden Browserprüfungen und die zusätzlichen Migrationsläufe endeten ohne Fehler. Nach der letzten Zielhash-Absicherung wurden Artefakte und Migration für alle sechs LS erneut geprüft; LS01 zusätzlich mit einer tatsächlichen Orientierungstextänderung im Lehrkräfte-Editor und anschließendem ZIP-Export.

Die ergänzenden Browserprüfungen umfassen alle Materialseiten in allen fünf Wegen, gesperrte Vorgängerphasen bei Navigation und direktem Aufruf, verweigerten Sitzungsspeicher, den korrekten Aufgabenrücksprung, Phasenwahl, Flyover-Anklickbarkeit und einen simuliert verkleinerten sichtbaren WebView-Viewport. Responsive Prüfungen decken Orientierung, Aufgabenfokus und Materialien ab, insbesondere das 2×2-Kompetenzraster ab Tabletbreite und die einzelne Spalte auf schmalen Smartphones. Die MC-Prüfung kontrolliert die sechs einzelnen Antwortzeilen, richtige/falsche Rückmeldung, Statusfarbe und Wiederaufnahme.

Die SCORM- und Migrationsprüfung kontrolliert API-Speicherung, unabhängige Kompetenzberichte, vollständige Wiederaufnahme sowie die Übernahme vollständig und teilweise bearbeiteter alter Prüfaufgaben in allen fünf Wegen. Der Editor-Test prüft gespeicherte Auftragsänderungen in Übersicht/Fokus, den tatsächlichen ZIP-Export einschließlich Originalbilder und eine unveränderte Aufgabensignatur bei reiner Zeit-UI-Änderung. Timerprüfungen umfassen Restzeit nach Materialwechsel, Grün/Schwarz/Rot, Pause, Ablauf, optionalen Ton und Stummschalter; der KI-Dialog öffnet auf derselben Seite.

Die Prüfungen verwenden Chromium, SCORM-API-Mocks, Web-Share-Mocks und einen lokalen AIS-Dialog-Mock. Die **native Moodle-App**, native GoodNotes-Übergabe, reale AIS-Einbettung/Anmeldung und Ton auf dem iPad sind damit nicht tatsächlich geprüft. Der schwebende Aufgabenrücksprung wurde im Browser mit simuliertem WebView-Viewport geprüft; seine native Appanzeige benötigt weiterhin einen Test in Moodle. GitHub-Änderungen aktualisieren bereits hochgeladene Moodle-Pakete nicht automatisch.

## Artefakte und Reproduktion

Sechs Einzel-ZIPs enthalten `imsmanifest.xml` direkt im Archivwurzelverzeichnis. Das [Gesamtarchiv](../Downloads/BRC_LG01_PlugAndPlay_Gesamtreihe_SCORM.zip) enthält diese sechs ZIPs und eine kurze Anleitung; es muss vor dem Upload einzelner Moodle-Aktivitäten entpackt werden. Die ältere einzelne Businessplan- und Sozialpädagogik-Ausgabe bleiben davon getrennt.

- `python tools/build_brc_series.py`
- `python tools/verify_brc_editorial.py`
- `python tools/verify_brc_series.py --source Quellen/BRC_LG01/Reihenplan.md`

Anleitung und Einzelpakete: [Reihe](../Reihen/BRC_LG01/README.md).

## Sichtprüfung

- [Kompetenzprofil](BRC_LG01_Reihe_Kompetenzen.png)
- [Aufgabenfokus](BRC_LG01_Reihe_Aufgabenfokus.png)
- [Materialansicht](BRC_LG01_Reihe_Material.png)
- [Geliefertes Orientierungsbild](BRC_LG01_Reihe_Orientierungsbild.png)
- [Antwortmöglichkeiten untereinander](BRC_LG01_Reihe_MC_Antworten.png)
- [Vollständiger gemeinsamer Prüfauftrag](BRC_LG01_Reihe_Pruefliste.png)

## SHA256 der finalen Archive

- `BRC_LG01_LS01_SCORM.zip` · `e9d8afae0db93f4e332f35d4b224278ed3c19ead7b0466b39af93b6b91339451`
- `BRC_LG01_LS02_SCORM.zip` · `b49d3618be74e6854e33b18173d1f88e31d0497a8ef1f081a9fca5e8ffa12a81`
- `BRC_LG01_LS03_SCORM.zip` · `adde2f9fa374ba81f74b5f05effdb5bcbbc90abf28b2112ab62c84859e941da5`
- `BRC_LG01_LS04_SCORM.zip` · `4420dd2cff1e0268277a63823219f7c457cbca16bfad7716f8192b9fd63bb8e0`
- `BRC_LG01_LS05_SCORM.zip` · `24468205d2c2a7544c3dc98b2b63752c1167c7e4e2032796591839b89f0d483d`
- `BRC_LG01_LS06_SCORM.zip` · `63718097525671dd4fa9166bb600d39e4c7db91c62b701436cfdf2472ba8e7b2`
- `BRC_LG01_PlugAndPlay_Gesamtreihe_SCORM.zip` · `7dd8ba4230a1597150c3bdc33c59bf56104f7d8b853fea9600f934695632e3fb`
