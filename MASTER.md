# Ein Master pro Lernsituation

## Verbindlicher Arbeitsstand

`master-katalog.json` ordnet jede feste Paketkennung genau einem entpackten Master zu.
Die Dateien in diesem Master sind der aktuelle Arbeitsstand. Entwürfe auf einem
Arbeitsbranch werden nach Prüfung in denselben Master auf `main` übernommen.
Keine zusätzlichen Ordner namens „neu“, „final“, „v2“ oder „aktualisiert“ anlegen.

Die bestehenden BRC-Master liegen direkt unter `Fachbereiche/BRC/LG01/LS01` bis `LS06`.
Ihre redaktionellen Quellen liegen gemeinsam unter `Fachbereiche/BRC/LG01/quellen`.
Diese Reihenquelle muss bei fachlichen Änderungen mitgepflegt werden. Die
Sozialpädagogik-Lernpfadübungen haben ihre eigenen Quellen und Generatoren.

## Bearbeiten und exportieren

Der normale Weg ist: aktuellen Master öffnen → bearbeiten → prüfen → Anzeigenummer
erhöhen → `tools/master.py export` ausführen. Dabei werden aktuelle HTML-, CSS-, JS-,
Bild- und PDF-Dateien gepackt. Es wird kein älteres ZIP als Ausgangspunkt verwendet.

Bei Lernsituationen werden Aufgaben-/Materialinhalte in `lesson-data.js` und den
betroffenen HTML-Seiten zusammenhängend gepflegt; der vorhandene Editor/Exporter kann
dafür verwendet werden. Fortschrittsmetadaten nach bestehenden Regeln aktualisieren.
Browser-Entwürfe sind erst dann Teil des GitHub-Masters, wenn die exportierten Änderungen
in dessen Dateien übernommen und geprüft wurden. Im Browser gespeicherte Entwürfe sind
kein Ersatz für den Repository-Stand.

Der Paketexport erhält Manifest-, Aufgaben-, Lernstands- und Kompetenzkennungen.
Eine neue Anzeigenummer darf diese Kennungen nicht automatisch ändern.

## Versionsnummer und aktuelle Downloads

- Zwei oder drei Zahlen verwenden: `1.0`, `1.2`, `1.8.2` oder `2.0`.
- Pro freigegebener inhaltlicher oder technischer Änderung am Paket die Nummer erhöhen.
- `set-version` lehnt kleinere und gleiche Nummern ab und vergleicht Zahlen numerisch.
- Beispiel: `Downloads/BRC-LG01-LS03/BRC_LG01_LS03_v1.2_SCORM12.zip`.
- Im jeweiligen Ausgabeordner liegt genau eine ZIP; alte ZIPs verschwinden aus dem
  aktuellen Dateibaum, bleiben aber über Git erreichbar.
- `Downloads/README.md` ist der stabile Einstieg; `Downloads/aktuell.json` enthält die
  aktuelle Zuordnung sowie SHA-256-Prüfsummen von Masterbestand und ZIP.
- Für sämtliche Pakete: `python tools/master.py export --all`.
- Vor automatischer Weiterverwendung: `python tools/master.py check --archives`.

Es gibt keine automatisch ausgewählte „höchste“ ZIP und keine zusätzliche `latest.zip`-
Kopie. Das verhindert veraltete Parallelstände. Sammelarchive sind keine eigenen Master;
bei Bedarf können die aktuellen Einzelpakete gemeinsam heruntergeladen werden.

## Generatoren und gemeinsame Vorlagen

Die drei Vorlagentypen werden jeweils in ihrem bestehenden Master unter `Vorlagen/`
weiterentwickelt. Neue Lernsituationen entstehen aus dem aktuellen passenden Typ;
eine neue Lernsituation erhält dabei eigene Kennungen. Für bestehende Lernsituationen
werden gemeinsame technische Verbesserungen gezielt übernommen und geprüft.
Der normale Paketexport überschreibt keine fachlichen Inhalte mit einer Vorlage.

Die bisherigen Generatoren bleiben für eine ausdrücklich gewünschte vollständige
Neuerzeugung erhalten. Sie sind mit `--regenerate-masters` abgesichert, weil sie aus
Quellen und Vorlage ganze Master überschreiben können, einschließlich Konfiguration.
Eine Neuerzeugung deshalb in einem separaten Arbeitsstand durchführen, mit den
gepflegten Mastern vergleichen und erst nach Prüfung übernehmen. Danach den zentralen
Export ausführen. Das ist kein erforderlicher Schritt bei gewöhnlichen Überarbeitungen.

## Neues Fach / neue Lernsituation

1. Fachbereich anlegen, beispielsweise `Fachbereiche/ReNo/LF01/LS01` oder
   `Fachbereiche/Geschichte/<Unterrichtseinheit>/LS01`. Bestehende fachliche Gliederung
   verwenden; keine Themen oder Lernfelder aus bloßen Platzhaltern erfinden.
2. Aktuelle freigegebene Vorlage übernehmen, Inhalte ergänzen und eigene stabile
   SCORM-/Lernstandskennungen vergeben. Lernsituation und Lernpfadübung getrennt führen.
3. Einen Eintrag mit eindeutiger `id`, `master`, `archiveStem`, `title`, `bereich`,
   `typ` und `version` in `master-katalog.json` hinzufügen. Neue Anzeigenummer: `1.0`.
4. Fachliche und funktionale Prüfungen durchführen, exportieren und ZIP prüfen.
   Künftig immer diesen Master weiterbearbeiten.

## Einordnung der bisherigen LS03-Dateien

Die bisherige reguläre BioCasa-LS03 ist die Lernsituation der sechsteiligen Reihe
(`BRC-LG01-LS03`, sieben Materialien). Die bisher „Aktualisiert“ genannte ZIP war ein
älterer Export der separaten Fünf-Lernwege-Vorlage (`LG01-LS03`, zehn Materialien).
Beide Identitäten bleiben erhalten und werden eindeutig im Katalog getrennt geführt.
Die Sozialpädagogik-Vorlage LS1.1 ist ebenfalls von der Lernpfadübung LS1.1 getrennt.



## BioCasa OS

Das bestehende Lernunternehmen wird unter `Fachbereiche/BRC/BioCasaOS` fortgeführt; Katalogkennung `BRC-BIOCASA-OS`. Quellcode und Tests liegen in diesem Projekt, der Laufzeit-Master in `dist`. `manifestOnly: true` nimmt ausschließlich `imsmanifest.xml` und die dort genannten Laufzeitdateien in die Schüler-ZIP auf. Lehrkräftevorschau und Paketkonfiguration bleiben Quellcode, gehören jedoch nicht ins Moodle-Schülerpaket. Andere Master behalten ihren vollständigen Export.

Für dieses bereits bestehende Projekt wird die Sites-Version `0.10.0` als sichtbare Paketversion `0.10` übernommen; `package.json` behält die passende SemVer `0.10.0`. Weitere Versionswechsel erfolgen gemeinsam für Katalog, Oberfläche und npm über `python3 Fachbereiche/BRC/BioCasaOS/scripts/project.py version X.Y`. Anschließend normal exportieren und prüfen. Siehe Projekt-README und STATUS.md.
