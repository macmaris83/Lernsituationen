# Eigenständige Flashcards-Vorlage

Diese Vorlage ist eine Flashcards-Übung mit dem Erscheinungsbild der freigegebenen GitHub-Lernsituationen: Schulkopf, Farben, Schrift, Seitenrahmen, Themenübersicht, Karten, Schaltflächen, Lehrkraftbereich und Fußleiste. Sie enthält eigene Flashcards-Funktionen und keine Lernphasen einer Lernsituation. Die 30 BioCasa-Karten dienen als vorhandene Beispielübung.

## Verwenden

Das ZIP als „Lernpaket (SCORM)“ in Moodle hochladen. `imsmanifest.xml` liegt direkt im ZIP-Hauptverzeichnis. Alle Dateien zusammen behalten; die Gestaltung und Programmlogik sind in `index.html` enthalten, die Logos liegen daneben.

Für die lokale Prüfung aus diesem Ordner `python3 -m http.server 8000` ausführen und `index.html` im Browser über den lokalen Server laden.

Die drei Trainingsrichtungen, Themenwahl, Kartenwendung, Sicher-/Unsicher-Stapel, Wiederholung, SCORM-1.2-Anbindung und Druckausgabe stammen aus der bereitgestellten Flashcards-Übung. Die SCORM-Anbindung wurde lokal simuliert; ein Test im tatsächlichen Moodle steht aus.

## Karten bearbeiten

„Lehrkraft“ öffnet die PIN-Anmeldung. Die vorhandene PIN der gelieferten Übung ist unverändert. Im Editor lassen sich Begriff, Erklärung und Beispiel jeder Karte anpassen.

1. Änderungen in den Feldern vornehmen und mit „Änderungen übernehmen“ testen.
2. „Bearbeitete index.html herunterladen“ wählen.
3. Im entpackten Paket die bisherige `index.html` durch die heruntergeladene Datei ersetzen; die übrigen Dateien beibehalten.
4. Den Ordnerinhalt erneut zippen, sodass `imsmanifest.xml` direkt auf oberster ZIP-Ebene liegt. Das neue Paket in Moodle hochladen.

Der Export beginnt wieder in der Lernansicht. Persönliche Kartenstapel werden beim Übernehmen der Änderungen zurückgesetzt. Änderungen werden wie in der Ausgangsübung erst durch den HTML-Export dauerhaft in einer neuen Paketfassung festgehalten.

## Als eigene Vorlage weiterverwenden

Den gesamten Ordner für eine neue Flashcards-Übung kopieren. Die Kartendaten sind im Array `const groups` in `index.html` zusammengefasst; Begriffe, Erklärungen und Beispiele lassen sich auch im Lehrkraftbereich bearbeiten. Für ein anderes Thema außerdem Seitentitel, sichtbaren Übungstitel, Themenbezeichnungen, Kontextbeschriftungen und die Titel/Kennung in `imsmanifest.xml` passend ändern. Die Gestaltung bleibt dabei gleich.

## Geprüft

- Alle 30 Kartentexte entsprechen der hochgeladenen Ausgangsübung.
- Trainingsrichtungen, Themenwechsel, Kartenwendung per Maus/Tastatur, Sicher-/Unsicher-Stapel und Wiederholung funktionieren.
- Ein vollständiger Durchgang meldet den Abschluss an eine lokale SCORM-1.2-Simulation.
- PIN-Anmeldung, Rückkehr ohne Anmeldung, Bearbeitung und erneutes Öffnen der exportierten HTML-Datei funktionieren.
- Tablet- und Smartphonebreiten (768 und 390 Pixel): alle Karten ohne Überbreite oder abgeschnittene Antworten.
- Druckansicht enthält 30 Vorder-/Rückseitenpaare; Manifest und Paketdateien sind vollständig.
