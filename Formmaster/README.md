# Gemeinsamer Formmaster 1.8.8

Dieser Ordner ist die verbindliche Quelle für die gemeinsame Gestaltung der
Lernsituationen. Grundlage ist die Gestaltung von **Identität und Nation 1.8.8**
am in [`manifest.json`](manifest.json) dokumentierten Commit. Die Dateien unter
`assets/` werden hier gepflegt und durch `tools/form_master.py` in die bestehenden
Lernsituationen übernommen. Die Dateien in den einzelnen Paketen sind die daraus
erzeugten, lokal ausführbaren Kopien.

Die gemeinsame Quelle umfasst aktuell **20 Lernsituationen und beide
Lernsituationsvorlagen**. Maßgeblich ist der `master-katalog.json`: Alle Einträge
mit `typ: "Lernsituation"` sowie `VORLAGE-TRADIERT` und
`VORLAGE-FUENF-LERNWEGE` werden automatisch berücksichtigt. Eine später neu
registrierte Lernsituation gehört damit ebenfalls zum Geltungsbereich und muss
die vorhandenen Schnittstellen der LS-Vorlagen verwenden. Die eigenständigen
Lernpfadübungen und BioCasa OS verwenden andere Oberflächen und sind nicht Teil
dieses Formmasters.

## Gestaltung zentral ändern

1. Die zuständige Datei in `Formmaster/assets/` bearbeiten. Allgemeine Änderungen
   an Farben, Schrift, Abständen, Karten, Navigation, Materialzugriff,
   Punkteanzeige und Abschlussdarstellung gehören in diese gemeinsame Quelle.
2. Bei einem neuen freigegebenen Formstand `version` in `manifest.json` erhöhen.
   Die Herkunft unter `reference` beschreibt weiterhin die ursprüngliche Basis.
3. Den Formmaster synchronisieren, die Prüfungen durchführen und die aktuellen
   Pakete exportieren:

   ```bash
   python tools/form_master.py sync
   python tools/form_master.py check
   python -m unittest discover -s tools -p 'test_form_master.py'
   node tools/test_form185.cjs
   python tools/master.py export --all
   python tools/master.py check --archives
   ```

   Änderungen an Darstellung und Bedienung zusätzlich mit der vorhandenen
   Browserintegration prüfen, insbesondere auf schmalen Bildschirmen, im
   Aufgabenfokus und in der Lehrkräfteansicht. `test_form185.cjs` bleibt trotz
   seines historischen Namens die Regression für Abschluss, Wiederaufnahme und
   unveränderte Fortschrittskennungen.

4. Gemeinsame Quelle, synchronisierte Pakete, Katalog und aktuelle Exporte
   gemeinsam in Git übernehmen. Der Workflow
   [`Aktuelle SCORM-Pakete`](../.github/workflows/current-scorm.yml) übernimmt die
   Synchronisierung und den Export auch nach Änderungen auf GitHub. Die
   Konsistenzprüfung erkennt Änderungen an erzeugten Dateien, die nicht aus dem
   Formmaster stammen.

`sync` ist wiederholbar: Ohne Änderung an der Quelle oder an einem Ziel entstehen
keine weiteren Änderungen. `check` schreibt keine Dateien und meldet, wenn
Quelle und Paketkopien auseinanderlaufen. Fachinhalte werden beim Synchronisieren
nicht aus früheren Generatorständen neu erzeugt.

## Gemeinsame Quelle und vorhandene Varianten

[`manifest.json`](manifest.json) beschreibt die erlaubten Übernahmen:

| Regel | Bedeutung |
| --- | --- |
| `files` | Gemeinsame CSS- und Oberflächenmodule mit ihrem Zielpfad im Paket. |
| `existingOnly` | Ein optionales Modul wird nur dort aktualisiert, wo es bereits vorhanden ist. |
| `append` | Zentral gepflegte Ergänzungen für bestehendes Vorlagen-Markup. |
| `override` | Eine ausdrücklich dokumentierte Variante, derzeit das Drucklayout der tradierten Vorlage. |
| `regions` | Nur der abgegrenzte Abschnitt für die Punkteanzeige in vorhandenen Fortschrittsdateien wird ersetzt. Die vorangehende Berechnung und Speicherung bleiben erhalten. |

Die Regeln unter `compat/` erhalten vorhandene Editor-Steuerelemente,
Aufgabensymbole und die Druckausgabe der Vorlagen. Sie sind ebenfalls Teil der
zentralen Quelle und werden nicht separat in einzelnen Lernsituationen gepflegt.
Inhaltsspezifische Gestaltung, etwa die Darstellung eines konkreten historischen
Dokuments, kann außerhalb der gemeinsamen Module bestehen bleiben. Ein neuer
allgemeiner Gestaltungswunsch wird zuerst darauf geprüft, ob er in den Formmaster
gehört; so entsteht keine weitere unabhängige Kopie der gemeinsamen Oberfläche.

Ein neues Modul nur in diesen Ordner zu legen, bindet es noch nicht in HTML ein.
Für neue Komponenten müssen Manifestregel, HTML-Verweise, vorhandene
Runtime-Schnittstellen und gegebenenfalls die Dateiliste im `imsmanifest.xml`
gemeinsam ergänzt und geprüft werden. Auch eine neue Struktur der Aufgaben- oder
Materialseiten braucht eine passende Integration; ein CSS-Update allein erzeugt
kein fehlendes Markup. Bestehende lokale Bilder und Schriften bleiben im jeweiligen
Paket, damit relative CSS-Verweise und die Offline-Nutzung funktionieren.

## Inhalte und Lernstände erhalten

Die fachlichen Master unter `Fachbereiche/` und `Vorlagen/` bleiben bestehen.
Aufgabentexte, Materialien, Bilder, Kompetenzbeschreibungen und
Lernsituationskonfiguration werden dort weiterentwickelt. Der Formmaster ersetzt
keine Inhalte, keine Bewertungen und keine komplette Runtime durch die von
Identität und Nation.

Bestehende SCORM-, Aufgaben-, Kompetenz- und Speicherkennungen sowie die
Fortschrittssignaturen bleiben maßgeblich. Die gemeinsame Punkteanzeige verwendet
das Bewertungsbudget des jeweiligen Pakets; ein Paket ohne Fachbegriffscheck
erhält durch die neue Gestaltung keinen zusätzlichen Check oder zusätzliche
Punkte.

## Formversion und Paketversion

**Formversion 1.8.8** bezeichnet die gemeinsame Gestaltungsbasis. Die Paketversion
kennzeichnet die konkrete exportierte Fassung einer Lernsituation und kann höher
sein. Ein bereits veröffentlichtes Paket darf nicht unter derselben Version mit
anderen Dateien überschrieben werden. Wenn die Synchronisierung seinen Inhalt
ändert, erhöht das Werkzeug die Paketversion bei Bedarf und führt die Formversion
separat im Katalog und in den Paketmetadaten mit. Beide Angaben lösen keinen
Lernstands-Reset aus.

Der Quellfingerabdruck `formSourceSha256` verbindet die Pakete zusätzlich mit den
genauen zentralen Dateien. Gleiche Versionsbeschriftungen allein gelten damit
nicht als Nachweis für gleiche Gestaltung.

## Moodle folgt separat

Diese Automatik aktualisiert die Master und die bereitgestellten SCORM-ZIPs in
GitHub. Bereits in Moodle importierte Pakete ändern sich dadurch noch nicht.
Die spätere Moodle-Anbindung muss die neuen Pakete übernehmen; sie ist kein
Bestandteil dieses Schritts. Die ZIPs enthalten weiterhin die benötigten lokalen
Dateien und setzen keinen extern geladenen CSS-Dienst voraus.

## Kompakte Phasenübersicht

Die Überschrift „Phasenübersicht“ und die Akkuanzeige teilen sich die oberste
Zeile der Navigation. Die acht Stationen folgen unmittelbar darunter. Auf schmalen
Displays verkleinert sich nur die Akkuanzeige innerhalb dieser Kopfzeile; die
Beschriftungen und die vorhandene Phasennavigation bleiben lesbar.
