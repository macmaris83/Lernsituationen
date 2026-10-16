# Gesamtdruck auf A4 · 16. Oktober 2026

Die sechs BioCasa-LG01-Lieferpakete 1.7, die sechs Katalog-Master 1.4 und beide
Vorlagen 1.4 verwenden dieselbe Druckkomponente. Die vollständige Druckansicht
enthält Orientierung, Handlungssituation, sechs Aufgabenphasen des gewählten
Lernwegs und alle Materialien. Sie öffnet die Inhaltsdetails und übernimmt
gespeicherte Schülerangaben sowie Editoränderungen im bestehenden SCORM-Kontext.

A4 hochkant, weißer Seitenhintergrund, 14 mm oberer, 12 mm seitlicher und 15 mm
unterer Rand. Die Inhaltsbilder, Tabellen, Dokumentfarben und Vektornetze bleiben
erhalten. Das Kompetenzprofil entspricht der Lernansicht. Die Fußleiste zeigt
einen Drucker und ein Zahnrad am Editor; die Touch-Flächen bleiben mindestens
44 × 44 Pixel groß.

[30 Browser-Druckfälle mit 995 Einzelprüfungen](Gesamtdruck_A4_Pruefung.json)
bestanden. Lernwege 1 und 5 (tradiert nur 1), volle Aufträge, Materialabsätze und
Tabellenzellen, lange gespeicherte Texte, Auswahlantworten, Kompetenzbelege,
verzögerte Bilder und Schriften, unveränderter bewerteter Lernstand und tatsächliche
Drucknavigation im SCORM-Iframe sind geprüft. Drei zusätzliche Fälle sichern das
endgültige Kompetenzraster; die Reihenfolge der Prüfstadien steht im JSON.

[Alle 14 final erzeugten Standard-PDFs](Gesamtdruck_A4_PDFs.json) haben A4-Format,
keine leeren Seiten und keinen Text außerhalb des Blatts. Die ergänzende Prüfung
der letzten Umbruchregel steht im [Nachtest](../Lieferungen/BioCasa_LG01/Default_PDF_Nachpruefung.json).
Die [Lieferprüfung](../Lieferungen/BioCasa_LG01/Lieferpruefung.json) bestätigt alle
sechs finalen Archive, unveränderte Originalinhalte und geschützte Kennungen sowie
aktuelle Druckdateien in den tatsächlich bearbeiteten Lehrkräfteexporten.
`tools/master.py check --archives` bestätigt alle 40 Katalogpakete.

Geprüft wurde lokal in Chromium mit Touch- und SCORM-1.2-Simulation und erzeugten
PDFs. Der Systemdruck auf einem physischen iPad, eine tatsächliche Moodle-Instanz
und ein Papierausdruck waren nicht Bestandteil dieser Prüfung.

Die aktuelle Implementierung und Wiederverwendung beschreibt
[Komponenten/Druckansicht](../Komponenten/Druckansicht/README.md).
