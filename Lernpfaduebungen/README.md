# Lernpfadübungen

Eigenständiger Vorlagentyp, getrennt von den Lernsituationen.

## Duales System verstehen

Die Mechanik stammt aus dem freigegebenen Upload
`01_Duales_System_verstehen_SCORM12_ResetResume_FIX (1).zip`.
Diese Vorlage dient als Blaupause für weitere Lernpfadübungen.

Der Lehrkräfte-Modus übernimmt die Gestaltung der Lernsituationsvorlage:
BBS-Kopfbereich, Schrift, Karten, Eingabefelder, Schaltflächen und einspaltige
Aufgabenwahl/Bearbeitung. Die Anzeige heißt jetzt Lernpfadübung. Das eigentliche
Lernmodell bleibt erhalten: 30 Aufgaben (12/12/6), 66-Prozent-Aufstieg,
Festigungsrunden, drei Hilfestufen, zusammenhängende Transferbewertung,
Selbsteinschätzungen und SCORM 1.2 mit Reset/Resume.

Die neue Gestaltung ist in `teacher-template.css` gekapselt. Im Lehrkräfte-Export
wird diese Datei mitgenommen. Änderungen an Aufgaben und Antworten können wie bisher
im Lehrkräfte-Modus vorgenommen und als neues Paket exportiert werden.

Zur lokalen Entwicklung genügt ein statischer Webserver, zum Beispiel
`python -m http.server 8000 --directory Lernpfaduebungen/Duales_System_verstehen`.
Der PIN ist derselbe wie im hochgeladenen Ausgangspaket.

## Bestehende Besonderheit der Ausgangsvorlage

Die Originaldatei `teacher.js` ruft `validateCurrent()` auf, definiert diese Funktion
aber nicht. Die fehlende Anzeige-Funktion wurde ergänzt, damit Auswahl, Bearbeitung
und Zurücksetzen im Lehrkräfte-Modus ohne JavaScript-Abbruch funktionieren. Die
vorhandenen Validierungsregeln wurden nicht geändert.

Die Gesamtprüfung verlangt mindestens zwei Orientierungsaufgaben je Kompetenz,
der Original-Aufgabenbestand enthält jedoch nur eine zur Personalkompetenz. Deshalb
stoppt der Lehrkräfte-Export dieser unveränderten Aufgabenverteilung mit einem
entsprechenden Hinweis. Das bereitgestellte SCORM-ZIP ist vollständig und kann in
Moodle eingesetzt werden. Aufgaben oder Exportregeln wurden nicht stillschweigend
verändert; diese inhaltliche Entscheidung bleibt offen.

Geprüft: unveränderte Bewertungsengine und Lernmechanik, PIN, Aufgabenbearbeitung,
Erreichbarkeit der letzten Editor-Aktionen auf drei Bildschirmgrößen, SCORM-Resume
und frischer Versuch mit einer simulierten SCORM-API. Der Export einschließlich der
neuen Style-/Logo-Dateien wurde zusätzlich mit einer gültigen Aufgabenverteilung
als reinem Testdatensatz geprüft. Kein Test in einem tatsächlichen Moodle-Kurs oder
auf einem physischen iPad.
