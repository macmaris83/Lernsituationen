# LG01 · Uhr, Gong, Lehrbuchlogo und bedienbare MC-Fragen

Lieferung **1.4**, geprüft am 16.10.2026. Ausgangspunkt ist die unveränderte
Aufgabenfassung 1.2 mit der Aufgabenform des GitHub-Masters
`8dd3853c69e1d33499037956c5fe3096fd2016f7`.

## Korrekturen

- Alle 628 Aufträge besitzen die vollständige Uhr aus der GitHub-Runtime:
  Countdown, Pause/Fortsetzen, Glockenschalter, Grün–Schwarz–Rot und Weiterarbeiten
  nach Ablauf. Der Glockenschalter steuert den kurzen dreifachen Gong.
- Die vorhandenen Phasenbudgets werden mit `build_brc_series.times()` für jeden
  Lernweg auf dessen Aufgaben verteilt. Summe und halbe Minuten entsprechen der
  Master-Methode; keine neuen Gesamtbudgets. Die ergänzten Zeiten sind Orientierung.
- Eine zweite Ursache lag in der Runtime: Die Ablaufmeldung wurde erzeugt, aber
  nicht angehängt. Sie wird jetzt auch sichtbar und als Status ausgegeben.
- Das vorhandene originale Lehrbuchlogo bleibt an allen 468 Buchverweisen direkt
  neben dem zugehörigen Text sichtbar. Bilddatei und Buchtexte sind unverändert.
- In SCORM-Review deaktivierte `situation.js` sämtliche Radios und Prüfbuttons.
  Die MC-Fragen können dort jetzt als lokale Übung bedient werden. Der gespeicherte
  Lernversuch bleibt schreibgeschützt. Im normalen Versuch werden Antworten wie
  zuvor gespeichert und für das Fortschreiten gewertet.

## Erhalt und Verifikation

- Aufgabenformulierungen, Operatoren, Nummern, Kennungen, Signaturen, Materialien,
  Quizfragen und korrekte Antworten erhalten. Die Fortschrittsdateien bleiben
  bytegleich. Alle 42 Original-PDFs und 180 Phasenhefte bleiben unverändert.
- 37 Python-Tests erfolgreich. Alle Zeitverteilungen ergeben exakt die vorhandenen
  Phasenbudgets. Die drei maßgeblichen Master-Stylesheets bleiben bytegleich.
- Alle 30 Kombinationen aus sechs Paketen und fünf Lernwegen haben eine bedienbare
  Uhr samt Pause/Fortsetzen und Glockenschalter. In jedem Paket zusätzlich voller
  Ablauf-, Farb- und Speichertest: pausierende Restzeit, Erhalt nach Neuladen,
  Grün–Schwarz–Rot, sichtbare Ablaufmeldung und Weiterarbeiten bei null.
  Glocke aus: keine Oszillatorstarts. Glocke an: sechs erfolgreiche native Starts
  mit positiven Lautstärkerampen. Keine JavaScript-Seitenfehler.
- Touch-Auswahl direkt auf dem Antworttext: alle sechs Pakete in lokaler Vorschau,
  normalem SCORM-Versuch, Browse und Review erfolgreich, insgesamt 24 Fälle.
  Falsches und richtiges Feedback, fünf richtige Antworten, Neuladen und
  authentifizierter Lehrkräftewechsel geprüft. Review schreibt dabei nichts ins LMS.
- Editoränderung an Auftrag und individueller Aufgabenzeit nach Neuladen im Fokus
  und im SCORM-Export sichtbar. Sauberer Export bewahrt alle Aufgabensignaturen.
  Direkter gesperrter Phasenaufruf bleibt gesperrt; ein vollständiger simulierter
  SCORM-Versuch meldet `completed`.

Die maschinenlesbaren Browserberichte liegen der Lieferung bei. Browserprüfungen
erfolgten lokal in Chromium mit Touch-Eingabe und SCORM-1.2-API-Simulation. Der
Audio-Test beobachtet native Web-Audio-Oszillatoren und positive Lautstärkerampen.
Ein physisches iPad, eine tatsächliche Moodle-Installation und die GoodNotes-App
wurden damit nicht getestet.
