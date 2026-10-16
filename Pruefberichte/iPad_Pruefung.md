# iPad-Layoutprüfung · 16. Oktober 2026

Ergebnis: **PASS in 14 SCORM-Kontexten**: sechs LG01-Master, zwei freigegebene Vorlagen und sechs aktualisierte Upload-Pakete in Version 1.6. Geprüft wurden insgesamt 280 Touch-Seitenansichten und 14 Maus-Monitoransichten.

Die Touch-Prüfungen verwenden die tatsächlich ausgelieferten SCORM-Iframes, mit 768×1024, 820×1180, 1024×768, 1180×820 und 507×768 Pixeln (Hochformat, Querformat und Split View). Die unveränderte Monitoransicht wurde bei 1440×900 Pixeln und feinem Mauszeiger geprüft.

## Belegte Korrekturen

- Die vorher 26 Pixel hohe Zeile „Orientierung gelesen“ hat jetzt mindestens 44×44 Pixel Berührungsfläche. Das Markieren wurde in allen 14 SCORM-Kontexten per Touch ausgeführt.
- Materiallinks (vorher 32 Pixel), Materialauswahl (34/38 Pixel), Pause und Signalton (36 Pixel) sowie die Aufgaben-Fußleiste (34–39 Pixel) erreichen auf Touch-Geräten mindestens 44×44 Pixel.
- Die acht Phasen unter den Materialien sind ab 960 Pixeln in einer Zeile angeordnet; Hochformat und Split View nutzen vier Spalten in zwei Zeilen. Alle acht Stationen sind vollständig sichtbar. Zuvor lagen bei 768 Pixeln nur 676 Pixel für 810 Pixel Inhalt vor, sodass die letzten Phasen seitlich verborgen waren.
- Geöffnete Materiallisten scrollen bei Bedarf vertikal und bleiben auf 32 Prozent der sichtbaren Höhe begrenzt. Die Auswahl benötigt keinen seitlichen Bildlauf.
- Formularfelder verwenden auf Touch-Geräten mindestens 16 Pixel Schrift. Das vermeidet den durch kleinere Formularschrift ausgelösten Safari-Fokuszoom.

## Bestandsschutz

Keine globale Überbreite in den geprüften Ansichten. Fachkompetenz und vollständiger Uhrbereich bleiben ab Tabletbreite nebeneinander; in Split View stehen sie lesbar untereinander. Rechner und Aufgabenrücksprung überdecken einander nicht. Das vorhandene Maus-Monitorlayout bleibt unverändert. Die spezielle Touch-Steuerung des Rechner-Draggriffs bleibt erhalten. Das additive Stylesheet verändert keine Aufgaben, Lehrbuchverweise, Inhalte, Speicherkennungen oder Fortschrittssignaturen.

## Reproduktion

```sh
python tools/check_ipad_layout.py --all --delivery work/delivery-v1.6/preview --report work/ipad-audit/iPad_14_Pruefung.json
```

Detaillierte Ergebnisse: [iPad_Pruefung.json](iPad_Pruefung.json).

Die Prüfung erfolgte mit Chromium-Toucheingaben und lokalen SCORM-Iframes. Ein physisches iPad, Safari und die tatsächliche Moodle-App wurden damit nicht getestet.
