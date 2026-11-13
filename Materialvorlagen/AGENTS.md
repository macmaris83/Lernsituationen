# Wiederverwendbare Dokumentvorlagen

Dieser Fundus gilt für alle Lerngebiete. Die Dateien sind Gestaltungshüllen mit Platzhaltern, keine LG03-Fachmaterialien. Bei neuen oder überarbeiteten Materialien die Oberfläche nach Dokumentart auswählen; nicht pauschal alle Materialien als Acrobat-PDF darstellen.

- `acrobat.html`: formale PDF-Berichte, Angebote und Rechtsunterlagen.
- `outlook.html`: E-Mails, Anfragen und interne Nachrichten.
- `onenote.html`: Notizen, Methodenkarten und Arbeitsblätter.
- `teams.html`: Chats, Besprechungen und kollaborative Abstimmungen.
- `sap.html`: Buchführungsdaten, Kostenübersichten und Geschäftsbelege.

Originalinhalte einschließlich Zahlen, Tabellen und Formulierungen unverändert in `article.paper` einsetzen; Dokumenttitel in Titel und Dateileiste übernehmen. Die Vorlagen enthalten keine Exportfunktion und keine Unterrichtsnavigation. Beim Einbetten in eine Lernsituation deren bestehenden Materialzugriff, Aufgabenrücksprung und Phasenfreischaltung erhalten. `assets/material-views.css` mitliefern. Weitere Dokumenttypen können später ergänzt werden.

Die realistischen App-Rahmen verwenden `data-material-surface="v2"`: passende Kopfzeile, Register, dezente Seitenleiste und Dokumentfläche. Rahmenbestandteile bleiben dekorativ; keine funktionslosen Schaltflächen, erfundenen Nachrichtenstände oder Geschäftsdaten ergänzen. Auf schmalen Bildschirmen die Seitenleiste ausblenden, im Druck nur den Dokumentinhalt zeigen. Historische Rollenkarten behalten eine passende Dokumentform.

`Formmaster/assets/material-views.css` ist die gemeinsame Gestaltungsquelle; die identische Kopie in diesem Fundus wird zusammen mit ihr gepflegt und geprüft. In Lernsituationen ergänzt `Formmaster/assets/material-access.js` die Hülle um das unveränderte vorhandene `article.paper`. Die fünf eigenständig nutzbaren HTML-Vorlagen enthalten denselben Rahmen bereits statisch.

