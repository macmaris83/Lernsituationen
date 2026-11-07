# Materialvorlagen

Wiederverwendbare HTML-Hüllen für vorhandene Unterrichtsmaterialien. Maßgeblich sind die `AGENTS.md` im Repository und in diesem Ordner. Dieser Abgleich ergänzt Dokumentformate und Formatproben; er erzeugt keine fertigen Lernsituationen oder SCORM-Pakete.

## Dateien und Auswahl

| Datei | Passende Dokumentart |
|---|---|
| `acrobat.html` | Formale Unterlagen, Berichte, einzelne Lieferangebote und Rechtsunterlagen |
| `outlook.html` | Tatsächlich als E-Mail vorliegende Nachrichten |
| `onenote.html` | Interne Notizen, Gesprächsvermerke, Kontaktlisten und Arbeitsblätter |
| `teams.html` | Tatsächlich als Chat oder kollaborative Abstimmung vorliegende Inhalte |
| `sap.html` | Als Geschäftsbeleg oder ERP-Auszug vorliegende Buchführungsunterlagen |
| `excel.html` | Tabellenblätter, Kostenvergleiche und tabellarische Modelldaten |
| `assets/material-views.css` | Gemeinsame Bildschirm- und Druckgestaltung |

Die App-Rahmen sind statische Gestaltung. Sichtbare Menünamen führen keine echten App-Funktionen aus: Es gibt weder Versand, Chat, Anmeldung, Buchung oder Dateispeicherung noch Tabellenkalkulation und Export.

Die Dokumentart folgt der Quelle. Eine vorhandene Gesprächsnotiz bleibt eine Notiz; daraus entstehen keine erfundene E-Mail, Teams-Unterhaltung, Bankunterlage oder SAP-Buchung. Ein Tabellenblatt behauptet keine Herkunft aus einer realen Anwendung. Fiktionshinweise und offene Angaben bleiben sichtbar. Unbekannte Kopffelder werden als Platzhalter erhalten, nicht ergänzt.

## Einsetzen vorhandener Inhalte

Originalformulierungen, Zahlen, Tabellen, Einheiten und Einschränkungen unverändert in `article.paper` übernehmen. Den Dokumenttitel in Seitentitel und Dateileiste eintragen; CSS mitliefern und relative Pfade an den Zielort anpassen. Die Hülle ergänzt keine fachlichen Erklärungen, Lösungen oder Aufgaben. Theorie wird aus dem Lehrbuch erarbeitet; Lehrbuchverweise bleiben einzeln bei den Aufgaben und werden nicht zu Materialdokumenten.

Bei einer späteren Einbettung bleiben Materialzugriff, Aufgabenrücksprung und Phasenfreischaltung der bestehenden Lernsituation erhalten. Diese Navigation gehört nicht in die eigenständigen Formatproben.

## Zuordnung für ReNo, Lernfeld 7

Die Matrix beschreibt geeignete Hüllen. Sie verlangt keine Neuerzeugung vorhandener Lernendenprodukte.

| LS | M1 und vorhandene Ergebnisse | Weitere Unterlagen und geeignete Hülle |
|---|---|---|
| 1 | Vorliegende Modellkanzlei und Gründungsanlass weiterverwenden | M2 Kontaktübersicht und Ausstattungsliste: `onenote.html` |
| 2 | Fallkartenset aus LS 1 weiterverwenden | M2 Bestands- und Auslastungsnotiz: `onenote.html` |
| 3 | Entscheidungsmail und Ressourcenmatrix aus LS 2 weiterverwenden | M2 interne Kostengegenüberstellung: `excel.html`; Annahmen und erläuternde Texte erhalten |
| 4 | Kalkulationsblatt und Aufbauentscheidung aus LS 3 weiterverwenden | M2 Gesprächsnotiz: `onenote.html`, keine nachträglich erzeugte Unterhaltung |
| 5 | Aufbauunterlagen aus LS 1–4 weiterverwenden | M2 einzelne Lieferangebote: `acrobat.html`; interne Notiz: `onenote.html`; getrennte Modellrechnung: `excel.html`. M3 Besprechungsvermerk: `onenote.html`, bestehende Modellvorstellungen unverändert verwenden |
| 6 | Aufbauunterlagen aus LS 1–5 weiterverwenden | M2 interne Vorgangsliste: `onenote.html`; kein Kontoauszug oder ERP-Beleg. Leistungszeitpunkte, Fälligkeiten und Finanzierungsangaben erhalten |
| 7 | Digitale Aufbauakte aus LS 1–6 weiterverwenden | M2 Planungsanhang und M3 Szenarien: `excel.html` mit vollständigen Erläuterungen; Simulation, Datenlücken und Randnotizen sichtbar lassen |

## Formatproben

`tests/index.html` bündelt vier Proben für unterschiedliche Layoutanforderungen:

| Probe | Inhalt und Prüfzweck |
|---|---|
| `tests/notiz.html` | LS 4: Gesprächsnotiz mit Metadaten und längeren Äußerungen |
| `tests/angebot.html` | LS 5: ausschließlich Einzelangebot B mit Originaldaten; unbekannte Kopffelder bleiben Platzhalter |
| `tests/kosten.html` | LS 3: breite Kostentabelle mit Formeln, Beträgen und längeren Zelltexten |
| `tests/modelldaten.html` | LS 7: Modelldaten, Szenariotabellen und erläuternde Randnotizen |

Die Proben prüfen die Darstellung vorhandener Inhalte. Sie bilden weder vollständige Materialsammlungen noch die Lernsituationsnavigation ab.

## CSS-Konventionen

| Klasse | Verwendung |
|---|---|
| `.document-meta` | Metadaten als `dl` mit zusammengehörigen `dt`-/`dd`-Paaren |
| `.long-prose` | Längere Fließtexte mit deutscher Silbentrennung; `lang="de"` beibehalten |
| `.numeric` | Reine Zahlenwerte rechtsbündig; nicht auf Formeln oder erklärende Zelltexte anwenden |
| `.wrap-value` | Optionaler Umbruch langer Werte, etwa in Metadaten |
| `.table-wrap` | Horizontal verschiebbarer Tabellencontainer mit `tabindex="0"`, `role="region"` und sprechendem `aria-label` |
| `table.table-wrap-text` | Gleichmäßige Spalten mit umbrechendem Text |
| `table.table-wide` | Mindestbreite für lesbare Tabellenspalten im Scrollcontainer; entfällt im Druck |
| `.table-scroll-hint` | Hinweis auf Verschieben und Tastaturbedienung bei schmalen Ansichten |
| `.sheet-start` | Beginnt im Druck ein neues Tabellenblatt; am Bildschirm bleibt der Lesefluss erhalten |

Die Proben enthalten an einzelnen langen Wörtern optionale Trennstellen (`&shy;`/`wbr`), damit Druckumbrüche auch ohne deutsches Silbentrennungswörterbuch verständlich bleiben. Wortlaut und Zahlen werden dadurch nicht geändert.

## Prüfverfahren

Vom Repository-Verzeichnis aus ausführen:

```sh
node Materialvorlagen/tests/check-layout.mjs
```

Voraussetzung ist das lokal verfügbare Node-Paket `playwright` mit installiertem Chromium. Der Prüflauf lädt keine Abhängigkeiten nach. Ein vorhandener Browserpfad kann über `CHROMIUM_EXECUTABLE` angegeben werden; `MATERIAL_QA_OUTPUT` bestimmt optional den Ausgabeordner. Screenshots und PDFs gehören ausschließlich in ein temporäres Ausgabeverzeichnis, nicht in den Vorlagenbestand.

Vorgesehen sind Prüfungen auf Desktop-, Tablet- und Mobilbreite sowie im Druck: vollständige Inhalte und Metadaten, lesbare Umbrüche, keine abgeschnittenen Werte, keine überbreite Gesamtseite, zugängliche breite Tabellen und sinnvolle Seitenumbrüche. App-Rahmen dürfen den Druckinhalt nicht verdecken. Originaldaten, Fiktionshinweise und Platzhalter sind mit der Quelle abzugleichen.

Diese Dokumentation beschreibt das Prüfverfahren. Sie bestätigt keinen bestandenen Prüflauf; tatsächliche Ergebnisse sind anhand des ausgeführten Tests und der erzeugten Ansichten festzuhalten.
