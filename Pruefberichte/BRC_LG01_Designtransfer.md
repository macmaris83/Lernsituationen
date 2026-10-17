# LG01 · GitHub-Design bei unveränderten Originalinhalten

Geprüft am 16.10.2026. Grundlage: das ausdrücklich hochgeladene `BioCasa_LG01_Moodle_Lernpakete.zip`.
Designquelle: aktueller GitHub-Katalogstand `8dd3853c69e1d33499037956c5fe3096fd2016f7`. Die Lieferung trägt die Anzeigenummer **1.1**.

Die Paketkennungen der gelieferten Fassung (`LG01-LS01` bis `LG01-LS06`) unterscheiden sich von den gepflegten Reihenmastern. Der Designtransfer erzeugt deshalb eine Lieferung aus dem Upload und ersetzt keine fachlich neueren Master.

| Paket | Unveränderte Inhaltsseiten | Unveränderte Aufgabenkennungen/-signaturen | Fokusprüfungen |
|---|---:|---:|---:|
| LG01-LS01 | 20 | 88 | 30 |
| LG01-LS02 | 18 | 88 | 30 |
| LG01-LS03 | 19 | 83 | 30 |
| LG01-LS04 | 20 | 85 | 30 |
| LG01-LS05 | 19 | 86 | 30 |
| LG01-LS06 | 20 | 93 | 30 |

Alle 116 Inhaltsseiten bleiben zeichengetreu erhalten. `lesson-data.js`, `progress-meta.js`, Konfiguration, Medienzuordnung und sämtliche 42 Original-PDFs sind bytegleich mit dem Upload. Zusätzliche GoodNotes-Importe je Phase bestehen aus unveränderten Originalseiten. Die vollständigen Prüfwerte stehen im maschinenlesbaren Lieferbericht.

## Lokale Funktionsprüfungen

- 180 Kombinationen aus sechs Aufgabenphasen, fünf Lernwegen und sechs Paketen: vollständige Aufgaben im Fokus, manuelles Abhaken und getrenntes Weitergehen.
- Alle sechs Pakete: Materialwechsel und Rücksprung zur konkreten Aufgabe im gewählten Lernweg; kein Überlauf bei 1024 und 390 Pixeln.
- LS01: direkter Aufruf einer gesperrten Folgephase bleibt gesperrt.
- Lehrkräfteexport ohne Bearbeitung: Inhaltsdaten und Aufgaben-Signaturen bleiben erhalten; aktuelle Runtime und 30 phasenbezogene GoodNotes-Dateien sind enthalten; keine alte eingebettete Paketkopie.
- Gespeicherte Editoränderung erscheint nach Neuladen in Übersicht/Fokus und im exportierten HTML sowie den exportierten Inhaltsdaten. Die Prüfung verändert keine Datei der Lieferung.
- Lokale SCORM-1.2-API-Simulation: Initialisierung, Speicherung in `cmi.suspend_data`, Commit und Abschlussstatus `completed` erfolgreich.
- 19 Python-Regressionstests erfolgreich, einschließlich Inhaltserhalt, stabilen Kennungen, Manifest-Dateiliste und bestehendem Exportwerkzeug.

Chromium-Prüfungen im lokalen Browser und SCORM-API-Simulation. Native Moodle-App, AIS-Anmeldung und die tatsächliche GoodNotes-Übergabe wurden damit nicht verifiziert.
