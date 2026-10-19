# iPad zuerst

Die Hauptansicht ist das iPad im Querformat. Ab 960 Pixeln stehen die acht Materialphasen in einer Zeile; bei schmaleren Ansichten in zwei Zeilen. Die Ergänzung erhält das freigegebene Design und verbessert die Bedienung auf Geräten mit Touch-Eingabe. Wichtige Bedienelemente erhalten mindestens 44 Pixel Höhe. Die Phasenwahl auf Materialseiten zeigt alle acht Stationen auch im Hochformat und in Split View. Geöffnete Materiallisten scrollen bei wenig Platz vertikal; das Dokument bleibt erreichbar. Textfelder verwenden mindestens 16 Pixel Schrift, um automatisches Vergrößern beim Fokussieren in Safari zu vermeiden.

Das Stylesheet greift über `any-pointer: coarse`. Monitore mit reiner Mausbedienung behalten ihr bisheriges Layout. Bildschirmzoom bleibt möglich, die Druckgestaltung bleibt unverändert.

Einbau: `python tools/install_ipad_layout.py PAKETORDNER …`. Die lokale CSS-Datei wird im SCORM-Manifest und in den bestehenden HTML-Hüllen ergänzt; Inhaltsdaten, Arbeitsaufträge, Speicherkennungen und Fortschrittsmetadaten werden nicht verändert.

Prüfung: `python tools/check_ipad_layout.py --all --delivery work/delivery-v1.6/preview`. Die Prüfung läuft innerhalb der SCORM-Iframes bei 768 × 1024, 820 × 1180, 1024 × 768, 1180 × 820 und 507 × 768 Pixeln sowie auf einem Mausmonitor mit 1440 × 900 Pixeln. Das sind Chromium-Browserprüfungen mit Touch-Eingabe; ein physisches iPad, Safari und die tatsächliche Moodle-App wurden nicht getestet.
