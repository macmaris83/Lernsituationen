# Eigenständige Lernpfadübungen

Diese Dateien sind Lernpfadübungen, keine Lernsituationen. Die Regeln für
Aufgabenphasen und Akkordeons der Lernsituationen gelten hier nicht automatisch.
Der Nutzer hat das hochgeladene Paket
`01_Duales_System_verstehen_SCORM12_ResetResume_FIX (1).zip` ausdrücklich als
Mechanik-Blaupause für zukünftige Lernpfadübungen festgelegt.

## Blaupause

`Duales_System_verstehen` ist die Ausgangsvorlage. Ihre Mechanik ist getrennt von
`Lernsituation_tradiert` und `Lernsituation_fuenf_Lernwege` weiterzuführen:

- Drei Stufen: Orientierung, Anwendung und Transfer; in diesem Paket 12 + 12 + 6 Aufgaben.
- Lernende schätzen ihre fünf Kompetenzbereiche vor und nach dem Lernweg ein.
- Aufstieg nach Orientierung und Anwendung ab 66 Prozent; andernfalls Festigungsrunde.
- Antwortprüfung, Teilpunkte, Hilfestufen und deren Erfassung unverändert übernehmen.
- Transfer als zusammenhängende Entscheidungskette auswerten, nicht als isolierte richtig/falsch-Antworten. Entscheidungsrollen und Verknüpfungen schützen.
- SCORM 1.2: ursprüngliche Interaktionen, Kompetenzziele, Punktwerte, Resume, neue Versuche und Speicherung erhalten. `resume` setzt den gespeicherten Versuch fort; `ab-initio` übernimmt keinen alten Lernstand. Keine Fortschrittslogik aus Lernsituationen einbauen.
- Lehrkräfte-PIN, Fehlversuchsperre, Entwurfsspeicherung, Aufgaben- und Lösungsauswahl, Validierung und SCORM-Export erhalten.
- Für neue eigenständige Übungen IDs und Browserspeicherschlüssel passend zur neuen Übung vergeben; nicht die Speicherstände einer anderen Übung wiederverwenden. Beim bestehenden Paket diese Werte nicht wegen Designänderungen ändern.

## Verbindlicher Aufgabenstandard (aktuelle Nutzerpräzisierung)

Für die gewünschten 30 Lernpfadübungen bedeutet „immer sechs“ ausdrücklich
**sechs Antwortmöglichkeiten je MC-Aufgabe**, nicht sechs Aufgaben insgesamt oder
je Stufe. Die Zahl der Aufgaben nicht aufgrund dieser Formulierung ändern.

- Keine Cloze-/Lückentext-Aufgaben verwenden. Vorhandene Aufgaben dieser Art in fachlich passende Multiple-Choice-Aufgaben umarbeiten.
- MC-Aufgaben als echte Mehrfachauswahl mit sechs eigenständigen Antwortmöglichkeiten erstellen. Eine oder mehrere Antworten können richtig sein; diese Möglichkeit in der Aufgabenanweisung klar benennen.
- Aufgabe, Antwortschlüssel und Feedback fachlich aus der zugehörigen Lernsituation ableiten. Plausible Fehlvorstellungen als Distraktoren einsetzen; keine künstlich verlängerten Antworttexte oder offensichtlich absurde Alternativen.
- Keine Lückentexte als MC tarnen. Kompetenz und Anforderungsniveau der ursprünglichen Aufgabe erhalten.
- Jede Aufgabe auf sechs verschiedene Optionen, gültige Antwortindizes, Übereinstimmung von Schlüssel und Erklärung sowie funktionierende Auswertung prüfen.
- Den bestehenden Lehrkräfte-Stil verwenden. Lernpfadübungen bleiben getrennt von Lernsituationen.
- Die 30 fertigen SCORM-ZIPs sollen auf ausdrücklichen Nutzerwunsch in dessen Google Drive abgelegt werden. Dies ist eine autorisierte Zielaktion, sobald Quelldaten, Drive-Verbindung und Zielordner verfügbar sind. Keine Upload-Erfolge ohne Bestätigung des Werkzeugs behaupten.
- Zur fachlichen Erstellung alle 30 Ausgangssituationen verwenden. Fehlende Inhalte nicht aus bloßen Titeln erfinden. Ein unzugängliches Sammelpaket oder fehlender Drive-Zugriff muss konkret benannt werden.

Diese Vorgabe ist für die gewünschte Überarbeitung/Neuerstellung anzuwenden;
der bisherige Ausgangsstand `Duales_System_verstehen` bleibt eine nachvollziehbare
Mechanik-Blaupause. Bestehende geschützte Transferrollen nicht unbegründet verändern,
um lediglich die Anzahl der Optionen zu erhöhen.

## Gestaltung des Lehrkräfte-Modus

Die Form von `Lernsituation_tradiert/lehrkraft.html` und dessen `assets/styles.css`
ist das Gestaltungsvorbild, nicht dessen Lernmechanik. Aktuelle Umsetzung:
`Duales_System_verstehen/teacher-template.css` und das Präsentations-Markup in
`teacher.js`.

BBS-Kopfbereich (#2aa7d7, grüne Unterkante #afca0b), maximal 1000 px breiter Rahmen,
Avenir/Segoe UI, helle gerahmte Karten, dunkelblaue Hauptschaltflächen (#173a63),
gleiche Eingabefelder und gelber Tastaturfokus. Aufgabenwahl und Editor als
aufeinanderfolgende Karten statt separater Vollbild-Seitenleiste. Auf Tablets und
schmalen Bildschirmen müssen sämtliche Eingaben und die letzten Aktionen erreichbar
bleiben. Styles nur auf den Lehrkräfte-Modus begrenzen; Lerneransicht nicht
unbeabsichtigt verändern.

Neue Paketdateien müssen sowohl im SCORM-Manifest als auch in der Dateiliste des
Lehrkräfte-Exports enthalten sein. ZIP enthält `imsmanifest.xml` im Wurzelverzeichnis.

## Prüfungen

Bei reinen Formatänderungen unveränderte Daten, Engine, Kompetenzdarstellung und
Lern-/SCORM-Funktionen gegen die Ausgangsvorlage prüfen. PIN-Prüfung, Bearbeitung,
Transferrollen, Export einschließlich neuer Styles, Scrollen am iPad-Bildschirmmaß,
Resume und frischen Versuch testen. Lokale Browser- und SCORM-API-Simulationen nicht
als tatsächlichen Moodle-/iPad-Test ausgeben.
