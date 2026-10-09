# Verbindlicher Standard für Lernsituationen

Die vom Nutzer freigegebene Gestaltung in `Lernsituation_tradiert` und
`Lernsituation_fuenf_Lernwege` ist der Standard für zukünftige Änderungen und neue
Lernsituationen. Beide Vorlagen auf `main` enthalten die Umsetzung. Der Nutzer
kann diesen Standard jederzeit ausdrücklich ändern.

## Getrennte Vorlagentypen

`Lernpfaduebungen/` ist ein eigener Vorlagentyp. Die nachfolgenden Regeln für
Lernsituationen gelten nicht automatisch für Lernpfadübungen. Für diese gelten
die gesonderten Vorgaben in `Lernpfaduebungen/AGENTS.md`.

## Aufgaben und Fokus

- Originale Aufgabenstellungen vollständig anzeigen; keine Textkürzung oder zusätzliche Aufgabenüberschrift. Operatoren bleiben fett.
- In allen sechs Aufgabenphasen (Informieren, Planen, Entscheiden, Durchführen, Bewerten, Reflektieren) öffnet ein Klick auf die Aufgabenkarte ein Akkordeon auf derselben Seite. Andere Aufgaben und die übergeordnete Navigation werden im Fokus ausgeblendet; der Materialzugriff bleibt verfügbar.
- Die Karte gleitend erweitern und nach oben scrollen; reduzierte Bewegung respektieren. Der offene Rahmen ist hellblau/blau.
- Nummer, GoodNotes-Logo und vorhandene Theorie-/Sozialform-Symbole stehen oberhalb des Auftrags. Die geöffnete Kopfzeile enthält keine Links und klappt durch Klick, Enter oder Leertaste nicht zu. Die Rückkehr erfolgt über die Schaltfläche unten links.
- Im Fokus stehen die einzelnen Arbeitsaufträge in eigenen Absätzen. Zusammengehörende Operatorenteile wie „Arbeiten … heraus“ nicht auseinanderreißen.
- Fachkompetenz aus den aktuellen Lernsituationsdaten ausformulieren, mit kleinem kontrastreichem Kompetenznetz. Keine ausklappbare Kompetenzdarstellung.
- Auf Tabletbreite Fachkompetenz links und vollständiger Uhrbereich rechts auf gleicher Höhe; dadurch beginnt der Arbeitsauftrag weiter oben. Auf schmalen Bildschirmen lesbar untereinander anordnen.
- Vorhandene Zeitangaben der Aufgabe als Grundlage des Countdowns nutzen. Uhr, Countdown, Pause und Glockenschalter gehören zusammen. Darunter: „Die Zeit ist eine Orientierung. Du kannst pausieren und nach Ablauf weiterarbeiten.“ Grün über Schwarz zu Rot; nach Ablauf weiterarbeiten erlauben, Fortsetzen ausblenden, optional kurzer Ton. Kein Zurücksetzen und keine erfundenen Zeitangaben.
- Fußleiste: links „Phasenübersicht“, mittig „Aufgabe erledigt“, rechts „Zur nächsten Aufgabe“. Abhaken schaltet nur den rechten Button frei; niemals automatisch wechseln. Bei der letzten Aufgabe führt der rechte Button zurück zur Phasenübersicht.
- Erledigte Karten in der Übersicht vollständig hellgrün hinterlegen (`#f3f8e7`, wie Materialzugriff), mit Haken oben rechts. Kein zusätzlicher Haken links oder unter der Sozialform; keine grüne Aufgabenummer.
- Keinen zusätzlichen Bereich „Arbeitsheft und Abgabe“ mit GoodNotes-Teilen oder Abgabe-Erklärung im Aufgabenfokus ergänzen.

## Materialien und KI-Hilfe

- Genau ein hellgrünes Material-Akkordeon pro Phasenseite. Materiallinks in einer horizontalen Zeile; auf schmalen Displays horizontal scrollbar. Keine doppelte Materialauswahl in einer weiteren Leiste.
- Auf jeder Materialseite muss eine kompakte Phasenübersicht Zugang zu allen acht Stationen der vollständigen Handlung bieten. Zusätzlich müssen „Zurück“ zur Ausgangsphase und „Weiter“ zur folgenden Phase angeboten werden; die Ausgangsphase aus der zuletzt geöffneten Aufgabe übernehmen. Ohne vorherige Aufgabe Informieren als Ausgangspunkt nutzen. In der letzten Phase entfällt „Weiter“. Die bestehenden Phasensperren gelten auch für diese Materialnavigation und dürfen nicht umgangen werden.
- Die Materialnavigation bleibt kompakt: keine große Kopf-/Fußnavigation und keine GoodNotes-Teilen-Funktion. Genau eine hellgrüne Leiste zum Wechseln zwischen den vorhandenen Materialien; die zusätzliche Phasenwahl und Zurück-/Weiter-Schaltflächen blau gestalten. Diese Vorgabe ersetzt das frühere Verbot der Phasenwahl auf Materialseiten und gilt für zukünftige Lernsituationen und SCORM-Paketaktualisierungen.
- Ein schwebender Button unten rechts führt aus dem Material zur zuletzt geöffneten Aufgabe zurück; Phase, Aufgabe und Lernweg erhalten.
- Eine kompakte lila KI-Hilfe: AIS.chat-Logo als direkt eingebettetes SVG im Button „KI-Hilfe öffnen“. Kein langer Erklärungstext neben der Aufgabe, keine drei Hilfestufen und keine alten Punkteabzüge.
- Chat im eingebetteten Dialog auf derselben Seite öffnen; nicht automatisch Safari oder ein neues Browserfenster öffnen. Dialogtitel: „KI-Hilfe · Löppt-Pilot“, ausdrücklich mit ö und zwei p. Kurzer Hinweis im Dialog: „Hilfe zur Selbsthilfe · Deine Lösung erarbeitest du selbst.“
- Den freigegebenen AIS-Link aus der vorhandenen Runtime verwenden. Ob AIS Einbettung, Anmeldung und das gewünschte Coaching erlaubt, muss am tatsächlichen Dienst/in der Moodle-App geprüft werden; keine ungetestete Garantie geben. Der Hinweis in der Vorlage ersetzt keine Konfiguration des KI-Gesprächspartners.

## Editor, Freischaltung und SCORM

- Das Akkordeon aus dem aktuellen Aufgabeninhalt erzeugen, nachdem gespeicherte Editor-Änderungen angewendet wurden. Keine unabhängig gepflegte Kopie der Aufgabenstellung einführen.
- Editor-Änderungen sollen nach Speichern und Neuladen in Übersicht und Fokus sowie im neuen SCORM-Export erscheinen. Geänderte Zeitangaben und vorhandene Symbole mit übernehmen.
- Nachfolgende Lernphasen erst freischalten, wenn alle erforderlichen Aufgaben vorheriger Phasen im gewählten Lernweg als erledigt markiert sind. Sowohl obere Navigation, untere Weiter-Schaltfläche als auch direkte Seitenaufrufe müssen die Sperre beachten; gesperrte Links sichtbar kennzeichnen.
- Bestehende SCORM-Schnittstelle, Lernstandsstruktur, Aufgaben-IDs und Kompetenzberichte bewahren. Reine Designänderungen dürfen die vorhandenen Inhalts-Signaturen nicht neu erzeugen. Bei inhaltlich bearbeiteten Exporten wird die Fortschrittsmetadatenstruktur durch den bestehenden Exporter neu berechnet.
- Exportierte ZIPs enthalten `imsmanifest.xml` direkt im ZIP-Wurzelverzeichnis und alle darin aufgeführten Dateien. Der Export muss aktuelle HTML-, CSS- und JS-Dateien verwenden, nicht einen veralteten eingebetteten Paketbestand.
- Bereits hochgeladene Moodle-Pakete werden durch GitHub-Änderungen nicht automatisch aktualisiert; dafür ist eine neue Paketfassung erforderlich.

## Verifikation

Bei Verhaltensänderungen im Browser prüfen: Aufgaben vollständig, Teilaufträge als
Absätze, offener Kopf ohne Einklappaktion, manuelles Weiter, grüne Erledigt-Karten,
Materialwechsel und Rücksprung mit korrektem Lernweg, Phasenwahl und Zurück/Weiter
auf allen Materialseiten einschließlich Phasensperren, gemeinsame Höhe von
Fachkompetenz/Uhr auf Tabletbreite und keine Überbreite auf schmalen Displays.
Freischaltung oben/unten und direkten gesperrten Aufruf prüfen. Bei Änderungen am
Editor/Export gespeicherte Bearbeitung bis zum Export prüfen; bei Änderungen am
Fortschritt die SCORM-Speicherung und Kompetenzberichte mitprüfen. Tatsächliche
Moodle-/AIS-Prüfungen von lokalen Browser- und API-Simulationen unterscheiden.
