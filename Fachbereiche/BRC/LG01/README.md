# BioCasa · BRC LG01 · Plug-and-Play-Reihe

Die Reihe setzt den bereitgestellten narrativen Reihenplan mit der zuletzt
freigegebenen Oberfläche und SCORM-Technik um. Sechs Lernsituationen umfassen
zusammen **80 Unterrichtsstunden**. Jede enthält **fünf alternative Lernwege**;
die Wege werden zeitlich nicht addiert.

| LS | Lernsituation | Umfang | SCORM-Paket |
|---|---|---:|---|
| 01 | Eine Geschäftsidee entwickeln | 12 UStd. | [Aktuelle ZIP](../../../Downloads/README.md) |
| 02 | Eine Unternehmensberatung besuchen | 8 UStd. | [Aktuelle ZIP](../../../Downloads/README.md) |
| 03 | Einen Business-Plan erstellen | 18 UStd. | [Aktuelle ZIP](../../../Downloads/README.md) |
| 04 | Bei Kapitalgebern pitchen | 12 UStd. | [Aktuelle ZIP](../../../Downloads/README.md) |
| 05 | Ein Unternehmen gründen | 14 UStd. | [Aktuelle ZIP](../../../Downloads/README.md) |
| 06 | Geschäfte abwickeln | 16 UStd. | [Aktuelle ZIP](../../../Downloads/README.md) |

[Aktuelle Paketübersicht](../../../Downloads/README.md): Pro Lernsituation wird
genau die im Master-Katalog eingetragene Version angeboten. In Moodle jede ZIP
als eigene SCORM-Aktivität hochladen.

## Lernweg und Unterricht

W1 ist stark geführt, W2 begleitet, W3 teiloffen, W4 selbstgesteuert mit
Checkpoints und W5 Löppt. Die Kennfarben folgen dem Reihenplan; Hausfarben und
Bedienelemente bleiben im freigegebenen BBS-Design. Die Lehrkraft wählt den Weg im
bestehenden Lehrkräftemodus. Für die Verteilung einen konfigurierten SCORM-Export
erstellen; die Schüleransicht zeigt keine alternativen Lernwege oder Wegauswahl.
Jedes Paket startet standardmäßig mit W1.

Die Handlungssituation und ihre fallbezogenen Kurzprüfungen führen in die
Aufgabenphasen. Die fünf Kurzprüfungen pro LS enthalten jeweils sechs
Antwortmöglichkeiten mit einer begründet richtigen Antwort. Anschließende
Phasen öffnen erst nach Abschluss der vorherigen Aufgaben. Der Fokus zeigt den
vollständigen Auftrag, Kompetenz, Uhr, Arbeitsform und KI-Hilfe. Erledigt markieren
und Weiter klicken sind zwei getrennte Handlungen. Materialwechsel erhält den
Bezug zur konkreten Aufgabe und zum Lernweg. Aus dem Material führt nur der
schwebende Button zur Aufgabe zurück; die Phasenübersicht bleibt unterhalb des
Materials erreichbar.

## Arbeitshefte, Druck und Bearbeitung

Jede der sechs Aufgabenphasen bietet ausschließlich ihre eigenen
GoodNotes-Arbeitsheftseiten im aktuellen Lernweg. Je Paket sind 30 Teil-Arbeitshefte
und fünf zusammengeführte Arbeitshefte enthalten. Der Schülerzugang bietet keine
vollständige GoodNotes-Datei in Orientierung oder Handlungssituation an.

Das PDF-Symbol steht ausschließlich unten rechts neben dem Lehrkräftezugang.
Die Gesamtdruck-PDF enthält Orientierung, Handlungssituation, die W1-Aufgaben und
sämtliche Materialien. Die vollständigen Arbeitshefte für W2–W5 liegen getrennt
im Paket. Die aktuelle Druckansicht berücksichtigt den ausgewählten Weg und
gespeicherte Seitenänderungen. Nach redaktionellen Änderungen die aktuelle
Druckansicht nutzen; die vorab erzeugten PDF-Arbeitshefte enthalten die
ursprüngliche Quellfassung. Die sichtbaren Aufgaben und der Akkordeon-Fokus werden
aus denselben gespeicherten Seiteninhalten erzeugt.

Aufgaben, Fallgeschichte, Materialtexte, Tabellen, Quellen und fachliche Sicherung
stammen vollständig aus dem [Reihenplan](quellen/Reihenplan.md).
Kompetenzen sind ohne fachliche Kürzung in die Ich-Perspektive übertragen.
Aufgabenzeiten sind zusätzliche Orientierungsvorschläge, deren Summe pro Weg
genau zum Phasenbudget passt, einschließlich halber Unterrichtsstunden.
Erwartungshorizont, Operatoren, Lehrkräftehinweise und Qualitätscheck stehen in
der Lehrkräftefassung. Die Hinweise zu KI-freien Arbeitsanteilen und erlaubtem
KI-Coaching bleiben im Quelltext erhalten; die KI-Hilfe stellt keine fertige
fachliche Lösung bereit und ersetzt keine amtliche Rechtsquelle.

## Technik und Prüfung

SCORM 1.2 startet über `scorm.html`. Jede LS hat eigene Lernstands- und
Kompetenzkennungen. Moodle-Abschluss, gespeicherte Aufgaben, Wiederaufnahme und
Kompetenzberichte verwenden die freigegebene Schnittstelle. Das Hintergrundbild
ist lokal enthalten und bleibt beim Scrollen stehen. Eine reine Zeitänderung
wird bei Aufgabensignaturen ausgeklammert.

Chromium- und SCORM-API-Prüfungen sind im
[Prüfbericht](../../../Pruefberichte/BRC_LG01_Reihe_Pruefung.md) dokumentiert.
Native Moodle-App, GoodNotes-Übergabe und die AIS-Anmeldung benötigen weiterhin
eine Prüfung im tatsächlichen Unterrichtssystem. GitHub-Änderungen aktualisieren
bereits hochgeladene Moodle-Pakete nicht automatisch.

## Aktuellen Master exportieren

Der aktuelle Arbeitsstand liegt unmittelbar in `LS01` bis `LS06`. Änderungen an
diesen Mastern bleiben beim normalen Export erhalten:

```bash
python tools/master.py export --all
```

Die Quellen unter `quellen/` dokumentieren die ursprüngliche Generierung. Eine
vollständige Neuerzeugung überschreibt die Master einschließlich Konfiguration
und erfolgt ausschließlich nach einer bewussten Entscheidung und Übernahme aller
zwischenzeitlichen Bearbeitungen in die Quellen bzw. den Generator:


```bash
python tools/build_brc_series.py --regenerate-masters
python tools/verify_brc_editorial.py
python tools/verify_brc_series.py --source Fachbereiche/BRC/LG01/quellen/Reihenplan.md
```

Benötigt werden Python 3, Pandoc, lxml, PyMuPDF, Playwright und Chromium unter
`/usr/bin/chromium`; Node prüft JavaScript. Die Erstellung nutzt die vorhandene
Cloud-Umgebung und startet ihren lokalen PDF-Prüfserver selbst.

## Überarbeitung mit den gelieferten Bildern

Je Lernsituation sind das zugehörige Orientierungs- und Handlungssituationsbild unverändert enthalten. Die Orientierung zeigt keinen Einordnungsblock und keine Lernwegübersicht; vier weitere Kompetenzen stehen neben dem Netz als 2×2-Raster. Prüfkriterien, Rückmeldung und Überarbeitung bilden gemeinsam einen einzigen Auftrag. Reflexionsfragen sind gemeinsam dargestellt, und die Symbole nennen die passende Arbeitsform pro Auftrag. Die sechs MC-Antworten stehen einzeln untereinander.

Die aktualisierten Pakete können alte Lernstände derselben sechs BioCasa-Pakete übernehmen. Eine zusammengefasste Aufgabe wird dabei nur als erledigt übernommen, wenn alle früheren Teile erledigt waren. Unvollständige Prüfblöcke bleiben offen. Die sechs LS-Kennungen und Kompetenzberichte bleiben dieselben. Bei Paketänderung in Moodle die bestehenden Einstellungen zum Speichern oder Zurücksetzen von Versuchen beachten.
