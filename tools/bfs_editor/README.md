# BFS dual · Editor, Checks und XP

Die SCORM-Pakete haben den Lehrkrafteditor in `lehrkraft.html`. Der Zugang verwendet dieselbe lokale PIN wie die BRC-Referenz. Die Seite kann Texte, eingebundene Verweise, Bilder, Fachbegriffs- und Fallfragen sowie Moodle-Aktivitäten konfigurieren. Ein berechtigter Zugriff auf den Moodle-Kurs wird durch Moodle verwaltet. Die lokale PIN sperrt nur die Editoroberfläche.

`editor-settings.js` bindet die Paketkonfiguration ein. Lokale Entwürfe erscheinen in der Vorschau. Die SCORM-Datei der Lerngruppe erhält die Änderungen beim Export. Die bearbeitete Druckansicht übernimmt den Entwurf. Die gelieferten, vorab erzeugten PDFs werden in der Autorenversion mit `tools/bfs_pdf_export/build.py` neu exportiert.

`build.py` und `answers.json` dokumentieren die erstmalige Übernahme der Editor- und Prüffunktionen. In den bestehenden Paketen bleiben die ursprünglichen Aufgaben- und SCORM-Kennungen erhalten. Die XP-Anzeige nutzt die Symbolik und Balkendarstellung des gemeinsamen Formmasters.
