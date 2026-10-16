# LG01 · Aufgabenform und Farben des aktuellen GitHub-Masters

Geprüft am 16.10.2026. Lieferung **1.3** aus der gelieferten Fassung 1.2.
Referenz: `main`, Commit `8dd3853c69e1d33499037956c5fe3096fd2016f7`, der zu Beginn
der Bearbeitung weiterhin aktuelle Standard im Master-Katalog.

## Gefundene Ursache und Änderung

Die Dateien `styles.css`, `phases.css` und `lg01.css` waren bereits bytegleich
mit GitHub. Den gelieferten Karten fehlte jedoch die aufgabenbezogene
Arbeitsform. Die komplette Phasenarbeitsform wurde dadurch als unformatierter
Fallback in der schmalen Symbolspalte dargestellt.

Alle 628 Karten verwenden jetzt die vorgesehene `assignment-social`-Struktur:
320 Zuordnungen stimmen mit dem vollständigen Masterauftrag überein, 198 sind
eindeutige Teilaufträge eines Masterauftrags. 105 zusätzliche Aufträge erhalten
ihre Arbeitsform aus den Originalanweisungen. Fünf offene Aufträge verweisen
kompakt auf ihren Phasenplan; deren ursprüngliche Wahlfreiheit bleibt erhalten.

Die Quellenbudgets sind ausdrücklich als Phasenbudgets gekennzeichnet.
Sie erzeugen keine neuen individuellen Aufgabendauern. Anzeige und Fokus lesen
die aktuelle Phasenangabe nach gespeicherten Editoränderungen.

## Erhalt und Prüfung

- Aufgabenwortlaut einschließlich Operatoren, Links und Buchverweisen erhalten.
  Materialien, Orientierung, Handlungssituation und Erwartungshorizont unverändert.
- Alle Aufgabenkennungen, fortlaufenden Nummern, Signaturen und Migrationsregeln
  erhalten; `progress-meta.js` in sämtlichen Paketen bytegleich mit Fassung 1.2.
- Alle Original- und GoodNotes-PDFs unverändert; Konfiguration und Medienzuordnung
  ebenfalls bytegleich. Aktuelle Dateiliste im SCORM-Manifest vorhanden.
- Alle drei maßgeblichen Stylesheets in allen sechs Paketen bytegleich mit dem
  GitHub-Master. Der Lehrbuchbezug wird beibehalten, auch wo die aktuelle
  BRC-Masterkarte keinen Buchverweis enthält.
- 35 Python-Tests erfolgreich, darunter Inhaltserhalt, eindeutige Zuordnung,
  Wahlfreiheit, wiederholbare Anwendung sowie Erhalt echter Aufgabendauern.
- Alle 180 Kombinationen aus sechs Paketen, sechs Aufgabenphasen und fünf
  Lernwegen im Browser geprüft: Symbolleiste, keine lange Phasenarbeitsform in
  der Symbolspalte, Fokus auf derselben Seite, manuelles Abhaken und Weitergehen.
- Inhaltssignaturen aller 628 Aufgaben im Browser neu berechnet und gegen die
  unveränderten gelieferten Metadaten verglichen: vollständig identisch.
- Fachkompetenz und Zeitbudget auf Tabletbreite nebeneinander, auf Smartphone-
  breite untereinander; kein horizontaler Überlauf.
- Farbprüfung: blauer Rahmen bei offener Aufgabe, vollständiges Hellgrün nach
  Erledigung, Erhalt nach Neuladen und Rückkehr zu Blau beim Entfernen des Hakens.
- Lokale Lernvorschau sowie simulierte normale SCORM- und Browse-Versuche
  bedienbar; Review bleibt in der Lernendenansicht schreibgeschützt.
- Editoränderung an Auftrag und Phasenzeit nach Neuladen im Fokus sichtbar und
  im SCORM-Export vorhanden. Aktuelle Runtime und zusätzliche CSS-Datei sind
  Bestandteil des Exports. Abgeschlossener simulierter Versuch erreicht `completed`.

Die Funktionsprüfungen erfolgten in Chromium mit lokaler SCORM-1.2-API-Simulation.
Ein tatsächlicher Test auf einem iPad, in Moodle und in der GoodNotes-App ist
damit nicht belegt.
