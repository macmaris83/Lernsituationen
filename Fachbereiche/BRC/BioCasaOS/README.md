# BioCasa OS · Rechnungswesen

Dies ist der fortzuführende Quellcode des bestehenden BioCasa OS. Das Lernunternehmen bildet Inventur, Inventar, Bilanz und Buchführung für Jahrgang 11 ab. Lager (Jg. 12) und Controlling (Jg. 13) greifen auf denselben Datenkranz zu. Die Oberfläche orientiert sich an Dynamics; der Produktname bleibt **BioCasa OS**.

**Paketversion: 0.19.** Übernommen aus der Sites-Fassung 0.10.0 vom 16.10.2026; npm verwendet zur zweistelligen Paketnummer die entsprechende SemVer X.Y.0. Aufgaben-, Manifest- und Speicherkennungen wurden beim Umzug nicht geändert.

Die neun Lernsituationen stehen mit vollständigen Originaltiteln einmal direkt am Header. Das Profil oben links enthält Import, Export und persönliche Einstellungen. Ab der zweiten Lernsituation stehen direkt darunter Neue Buchung und Journal; in Inventur, Inventar und der Bilanzaufgabe bleiben beide ausgeblendet. Arbeitsbereiche, Fallstand und Sicherungsdetails sind im Profil erreichbar; der Speicherstatus bleibt als Symbol im Kopf. Ein Rollencenter und ein eigener Bereich für Lernaufträge entfallen; bestehende OS-Buchungschecks und Zwischenstände bleiben erhalten.

## In Codex fortsetzen

In Codex das Repository `macmaris83/Lernsituationen` auswählen und im bestehenden Projekt arbeiten:

> Arbeite in Fachbereiche/BRC/BioCasaOS. Lies zuerst die dortige AGENTS.md und STATUS.md. Setze ausschließlich meine konkret beauftragte Änderung um, prüfe sie und übernimm sie mit nachvollziehbarem Commit in dasselbe Repository. Erhalte bestehende Daten, Lernstände und Paketkennungen.

Jede beauftragte Änderung wird im selben Arbeitsgang in diesem Repository aktualisiert. Es gibt keinen Auftrag für selbständige Weiterentwicklung, regelmäßige Hintergrundänderungen oder zusätzliche Funktionen. Änderungen an anderen Mastern bedürfen eines entsprechenden Auftrags. Notwendige Tests, Dokumentation und Paketexporte gehören zur jeweiligen Änderung.

## Starten und prüfen

Voraussetzungen: Node.js 22 und Python 3.11 oder neuer. Keine npm-Pakete installieren; die Anwendung hat keine externen Laufzeitabhängigkeiten.

Vom Repository-Stamm aus:

```bash
npm --prefix Fachbereiche/BRC/BioCasaOS test
python3 -m unittest discover -s tools -p 'test_master.py'
python3 Fachbereiche/BRC/BioCasaOS/scripts/project.py check --archive
python3 -m http.server 8000 --directory Fachbereiche/BRC/BioCasaOS/dist
```

Danach lokal `http://localhost:8000/index.html` öffnen. `preview.html` bietet die getrennte Lehrkräftevorschau, `teacher.html` die Daten-/Freigabekonfiguration. Ein lokaler Start bestätigt keine Moodle- oder iPad-Kompatibilität.

## Projektstruktur

| Pfad | Zweck |
|---|---|
| `dist/` | Direkt ausführbarer HTML-/CSS-/JS-Master, keine generierten Builddateien |
| `dist/imsmanifest.xml` | Verbindliche Dateiliste der Schüler-ZIP, ein SCORM-1.2-Lernobjekt |
| `dist/data-defaults.js`, `dataset.js` | Ausgangsdaten und geprüfter Schuljahresupload |
| `dist/engine.js`, `accounts.js` | Gemeinsames Buchungsmodell und T-Konten |
| `dist/flow-player.js`, `booking-checks.js` | Zahlenwege und vorgeschaltete Verständnisfragen |
| `dist/storage.js` | Persönlicher Stand, SCORM-Wiederaufnahme und Kapazitätsprüfung |
| `tests/` | Modell-, Ereignis-/Vorlagentests und simulierte SCORM-API |
| `STATUS.md` | Übernommene Funktionen, Prüfstand und konkrete offene Punkte |
| `docs/ANFORDERUNGEN.md` | Fachliche und didaktische Entscheidungen aus dem Auftrag |
| `docs/HERKUNFT.json` | Herkunft des übernommenen Sites-Commits und Dateiprüfsummen |

## Versionieren und Moodle-Paket erzeugen

Bei einer Änderung der Schüler-Laufzeit zuerst die passende neue Paketversion setzen, zum Beispiel:

```bash
python3 Fachbereiche/BRC/BioCasaOS/scripts/project.py version 0.13
npm --prefix Fachbereiche/BRC/BioCasaOS test
python3 tools/master.py export --id BRC-BIOCASA-OS
python3 tools/master.py check --archives
python3 Fachbereiche/BRC/BioCasaOS/scripts/project.py check --archive
```

Der Versionsbefehl hält Katalog, sichtbare Oberfläche, Kurzstart und npm-Version zusammen. Reine Projekt-/Dokumentationsänderungen benötigen keine künstliche Laufzeitversion. Es gibt genau eine aktuelle ZIP unter `Downloads/BRC-BIOCASA-OS/`; Einstieg: [Downloadübersicht](../../../Downloads/README.md). Der zentrale Export liest die gepflegten Dateien. Kein altes ZIP als Quellcode verwenden.

`manifestOnly: true` schließt die Lehrkräftedateien `preview.html`, `teacher-preview.js`, `teacher.html`, `teacher.js` und `package-writer.js` aus der Schüler-ZIP aus. `imsmanifest.xml` liegt direkt in deren Wurzel. Künftig benötigte Schülerdateien immer im Manifest ergänzen.

## GitHub, Website und Moodle

GitHub ist der fortzuführende Code-Master. Ein Commit ist keine Veröffentlichung auf der [bestehenden privaten Website](https://biocasa-rechnungswesen.macmaris.chatgpt.site). Diese behält ihre bisherige Identität; eine gewünschte Web-Veröffentlichung verwendet den geprüften `dist`-Stand desselben Projekts. Moodle verwendet die konkret hochgeladene ZIP. Änderungen in GitHub ersetzen keine bereits installierte Moodle-Datei.

Der bisherige Chatverlauf und ursprüngliche MD-/Lehrbuchmaterialien werden nicht automatisch Teil einer Codex-Umgebung. Die Anforderungen und Herkunft sind hier zusammengefasst; Lehrbuchscans und Original-Lernpakete sind in diesem Codeimport nicht enthalten. Fehlende Originalquellen dürfen nicht durch erfundene Seitenangaben ersetzt werden.

Ältere technische Notizen: [übernommener Sites-Entwicklungsstand](docs/SITES-ENTWICKLUNGSSTAND.md). Bei abweichenden älteren Beschreibungen gelten AGENTS.md, Anforderungen und aktueller Code.

