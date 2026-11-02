# Identität und Nation · Version 1.8.4

Der fortlaufende SCORM-1.2-Master dieser Lernsituation liegt in `Lernpaket/`.
Die Jugendredaktion „Zeitstimmen“ entwickelt einen Podcast zu Identität, Nation
und Zugehörigkeit. Die sechs Aufgabenphasen enthalten jeweils zwei Aufgaben;
Materialien M1–M6 unterstützen die fachliche Arbeit.

Die aktuelle Schüler-ZIP wird über den Master-Katalog erzeugt:
`Downloads/GESCHICHTE-IDN/Identitaet_und_Nation_v1.8.4_SCORM12.zip`.
Sie wird als eigene SCORM-Aktivität in Moodle importiert. Bereits hochgeladene
Moodle-Kopien werden durch GitHub-Änderungen nicht automatisch ersetzt.

[Lehrkräftehinweise und Lösungen](Lehrkraft/Identitaet_und_Nation_Lehrkraft.pdf)
stehen separat außerhalb des Schüler-Masters. Ursprüngliche Eingabedateien
und frühere Exportfassungen gehören nicht in `Lernpaket/`.

Für weitere Änderungen diesen Master einschließlich `lesson-data.js` und der
zugehörigen HTML-Seiten fortführen und die vorhandenen Aufgaben-, Kompetenz-,
SCORM- und Speicherkennungen erhalten. Der normale Export ist
`python tools/master.py export --all`; keine älteren Inhaltsgeneratoren ausführen.

## Änderungen in 1.8.4

Die Orientierung ist gestrafft. Geschichte zeigt an den Aufgaben ausschließlich
Aufgabennummer, GoodNotes und Arbeitsform; die Arbeitsform bleibt im Editor
bearbeitbar. Die Kennzeichnungen Theorie, Praxistheorie und Praxis entfallen.
Der grüne Materialzugriff verwendet die kompakte BRC-Struktur.

Der Footer zeigt den laufenden XP-/Punktestand dieser Lernsituation als absolute
Summe von 0 bis 100: Aufgaben 25, Handlungssituationscheck 15 und Begriffscheck 60
Punkte. Die Anzeige wird aus dem gespeicherten Fortschritt berechnet; sie addiert
beim Wiederöffnen oder wiederholten Abschluss keine weiteren Punkte. „XP“
bezeichnet diesen Paketpunktestand. Eine externe XP-Plattform ist nicht angebunden.

Nach Erledigung von Orientierung, Aufgaben und Checks lässt sich das Lernpaket
abschließen. In Moodle bestätigt die SCORM-Speicherung den Abschluss; bei einem
Speicher- oder Abschlussfehler bleibt ein erneuter Versuch möglich. Eine lokale
Vorschau kennzeichnet ihren Abschluss als lokal. Die fachliche Podcastbewertung
bleibt Aufgabe der Lehrkraft.
