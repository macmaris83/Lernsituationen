# Lernsituationen · aktuelle Master

Hier werden dieselben Master fortlaufend weiterentwickelt. Jeder Master hat einen festen
Ordner, eine sichtbare Versionsnummer wie **1.2** und genau **eine aktuelle SCORM-ZIP**.
Frühere Fassungen bleiben in der Git-Historie nachvollziehbar.

**[Aktuelle Pakete herunterladen →](Downloads/README.md)**

| Bereich | Arbeitsstand |
|---|---|
| BRC · BioCasa LG01 | [Sechs Lernsituationen](Fachbereiche/BRC/LG01/) |
| Sozialpädagogik | [30 Lernpfadübungen](Fachbereiche/Sozialpaedagogik/Lernpfaduebungen/) |
| ReNo | [Bereich für künftige Lernsituationen](Fachbereiche/ReNo/) |
| Geschichte | [Bereich für künftige Lernsituationen](Fachbereiche/Geschichte/) |
| Gemeinsame Vorlagen | [Tradiert](Vorlagen/Lernsituation_tradiert/) · [Fünf Lernwege](Vorlagen/Lernsituation_fuenf_Lernwege/) · [Lernpfadübung](Vorlagen/Lernpfaduebung/) |
| Materialoberflächen | [Materialvorlagen](Materialvorlagen/) |

## Mit Codex weiterarbeiten

1. Den aktuellen Stand von `main` holen. In einem sauberen Checkout: `git pull --ff-only`.
   Lokale Änderungen zuerst erhalten und abstimmen; niemals durch Reset verwerfen.
2. In [master-katalog.json](master-katalog.json) den Eintrag anhand der festen Kennung
   auswählen. Dort steht der einzige verbindliche Masterpfad.
3. Diesen Master bearbeiten, seine Kennungen und Lernstände erhalten und die
   fachlichen/UI-Prüfungen aus `AGENTS.md` durchführen.
4. Die sichtbare Version erhöhen, aus dem aktuellen Master exportieren und prüfen:

```bash
python tools/master.py set-version BRC-LG01-LS03 1.1
python tools/master.py export --id BRC-LG01-LS03
python tools/master.py check --archives
```

`1.1` ist ein Beispiel für den ersten Schritt nach dem hier eingeführten Stand `1.0`.
Die folgenden Änderungen verwenden `1.2`, `1.3` usw. Bei grundlegenden Änderungen
kann die erste Zahl erhöht werden, etwa auf `2.0`. Die SCORM-Version bleibt davon
unabhängig **1.2**. Ordner und Aufgaben-/Speicherkennungen erhalten keinen Versionszusatz.

Der Export liest die aktuellen Dateien aus dem Master. Bei Änderungen unter derselben
bereits exportierten Versionsnummer stoppt er mit einem Hinweis. Nach erfolgreichem
Export wird die vorherige ZIP im Ausgabeordner ersetzt. Die Downloadübersicht folgt
dem Katalog; sie wählt keine Datei anhand von Datum, Dateiname oder alphabetischer Sortierung.

Nach Änderungen auf `main` prüft und aktualisiert der Workflow
„Aktuelle SCORM-Pakete“ die Downloads. Erst der erfolgreiche Lauf bestätigt den
aktuellen Export. Automatische Nutzer prüfen zusätzlich `master.py check --archives`.

## Arbeitsweise und neue Fächer

Die freigegebene Gestaltung, Bedienung, vollständige Handlung, Materialzugriff,
Lehrkräftemodus und SCORM-Technik gelten weiter. Lernpfadübungen behalten ihre
eigenständige Mechanik. Weitere Fachbereiche erhalten denselben Aufbau; ihre Inhalte
und fachliche Gliederung bleiben eigenständig.

Details: [Master bearbeiten und erweitern](MASTER.md).

Die sichtbaren Nummern starten bei dieser organisatorischen Umstellung mit `1.0`.
Das setzt weder fachliche Inhalte noch SCORM-Lernstände zurück. Bereits hochgeladene
Moodle-Pakete müssen weiterhin durch einen neuen Import ersetzt werden.
