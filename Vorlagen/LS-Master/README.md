# LS-Master im BRC-Design

Diese Vorlage für neue Lernsituationen verwendet das Layout von **BRC LG01 LS03 – Einen Business-Plan erstellen**, Paketstand **1.8.10** und Formstand **1.8.8**. Die BRC-Beispielinhalte zeigen die acht Phasen, den Aufgabenfokus, die Materialseiten, den Editor und die Druckansicht.

- **Vorschau:** `scorm.html` aus dem exportierten Paket lokal über einen HTTP-Server öffnen.
- **Neue Lernsituation:** Eine Arbeitskopie im passenden Fachbereich anlegen, eine eigene stabile Paketkennung vergeben und Inhalte im Editor oder in `lesson-data.js` und den zugehörigen HTML-Seiten austauschen. Fortschrittsmetadaten für neue Inhalte über den Editor-Export neu erzeugen.
- **Gemeinsame Gestaltung:** Änderungen an CSS und den gemeinsamen Bedienkomponenten in [Formmaster](../../Formmaster/README.md) pflegen. `python tools/form_master.py sync` übernimmt sie in den LS-Master.
- **SCORM-Export:** `python tools/master.py export --id LS-MASTER` und `python tools/master.py check --archives`. Die aktuelle Datei steht im [Downloadkatalog](../../Downloads/README.md).

Der LS-Master hat die Paketkennung `LS-MASTER`. Bei der Anlage wurden die Stylesheets einschließlich ihrer Ladefolge aus [BRC LG01 LS03](https://github.com/macmaris83/Lernsituationen/tree/e078eb9698954cad17b22f090c212597996fa05b/Fachbereiche/BRC/LG01/LS03) übernommen.
