# Prüf- und Übergabestand

Stand der Übernahme: **16.10.2026**, Paketversion **0.10** (Sites-Quellfassung **0.10.0**).

## Vorhanden

- Bestehende Oberfläche, Firmen-/Schullogo, neun gesperrt fortschreitende Lernschritte und auswählbare getrennte Lehrkräftevorschau.
- Fünf Inventurfälle, Inventar in Staffelform und Übertragung in die Bilanz in Kontenform; graue fortgeschrittene Anfangspositionen.
- Gemeinsamer Finanz-/Lagerdatenkranz, schuljahresbezogener geprüfter Datenupload, Herkunft und Lehrbuchverweise.
- Fiktive Belege, Kontenblatt, feste Soll-/Habenzeilen, anpassbare Fokusansicht mit Bilanz/GuV und optionalen T-Konten.
- Automatischer Zahlenweg mit Pause/Wiederholung; Verständnischeck vor Pfeil 2 bei den ersten drei unterschiedlichen Fällen eines Themas; Sonderweg für reduzierte Bewegung.
- EBK-Eröffnung, datierte Gegenkonten mit Touch-Hintergrund; geprüfter Abschluss mit selbst gewähltem Betrag/Seiten/Gegenkonto, orange verbundenen Zeilen, korrekter Buchhalternase und gemeinsamer Summenzeile.
- Touch-Rechner mit +/− und bestätigter Übernahme des eigenen Ergebnisses ins gewählte Betragsfeld.
- Persönlicher SCORM-1.2-Stand, Autosave, Wiederaufnahme, Review-Schutz, JSON-Sicherung und iPad-Kurzanleitung.

## Prüfungen

Die GitHub-Übernahme wurde lokal geprüft: **140 Node-Tests, 20 zentrale Exporttests und 4 Projekt-/Versionstests erfolgreich**. Die Schüler-ZIP wurde mit allen 27 Manifestdateien bytegenau verglichen; die 23 bestehenden JavaScript-Dateien blieben unverändert. Die Node-UI-Tests verwenden eine VM mit simulierten DOM-/Ereignisobjekten; die SCORM-Tests eine simulierte LMS-API.

**Offen bleiben reale Abnahmen:** visuelle Browserdarstellung und Pfeilbewegung, tatsächliche Touch-/iPad-Tastaturbedienung, Moodle-App/Webview, Speichern/Wiederaufnahme in der Schulinstallation und Gerätewechsel. Ein erfolgreicher automatisierter Test bestätigt diese Abnahmen nicht. Die Browser-Prüfumgebung war beim letzten Versuch nicht verfügbar.

Der bestehende GitHub-Workflow „Aktuelle SCORM-Pakete“ prüft den gesamten Katalog und seine Exportwerkzeug-Tests und erzeugt die aktuellen ZIPs. Der ergänzende Workflow „BioCasa OS prüfen“ führt die OS-Tests und den eigenen Paketvergleich aus. Den tatsächlichen Laufstatus immer in GitHub prüfen; diese Beschreibung behauptet keinen noch nicht erfolgten CI-Erfolg.

## Grenzen und offene fachliche Ausbauschritte

- Der Kontenabschluss ist eine **didaktische Abschlussansicht** mit Gegenbuchungen auf 801 SBK bzw. 802 GuV. Er ist kein vollständiger Jahresabschluss mit endgültigem GuV-Übertrag ins Eigenkapital. Laufende Auswertungswerte werden nicht durch eine zweite Abschlussbuchung verdoppelt oder nullgesetzt.
- Das Demo-Journal enthält LS02-Grundfälle und gekennzeichnete OS-Ergänzungen. Es ist nicht die eigene Jahresabschluss-Saldenliste von LS08/09.
- Spätere Themen haben eigene geprüfte Übungsfenster; deren Lösungen werden nicht automatisch ins kanonische Demo-Journal gebucht.
- SCORM 1.2 hat höchstens 4096 Zeichen für den komprimierten Stand; das Modell begrenzt zusätzliche Buchungen auf 60 und lehnt zu große Änderungen vor Übernahme ab.
- Keine gemeinsame Klassenfirma, zentrale Benutzerverwaltung oder automatische Moodle-Rollenerkennung. Der Lehrkräftemodus ist eine getrennte private Vorschau; Freigabekonfiguration im Paket ersetzt keine LMS-Zugriffssicherheit.
- Aus dem Moodle-Schülerpaket öffnet die Lehrkräfteauswahl die bestehende private Website. Deren Berechtigung ist gesondert erforderlich.
- Original-MD, originale Moodle-Reihenpakete und Lehrbuchscans sind nicht in diesem Codeimport enthalten. Bei quellenabhängigen Änderungen Originalgrundlage prüfen; keine Fundstellen erfinden.

Diese Liste ist eine ehrliche Bestandsaufnahme, **kein selbständiger Entwicklungsauftrag**. Nur konkret beauftragte Änderungen umsetzen und im selben Arbeitsgang nach GitHub übernehmen.

## Herkunft und Veröffentlichung

Die Quellkopie stammt aus dem Sites-Commit `495531b14dc777ef7b84d3b65aa5829217bdf83e`, zuletzt veröffentlicht am 16.10.2026 um 11:49 UTC. Die erste GitHub-Übernahme ändert keine fachliche Laufzeitlogik. Angepasst wurden die sichtbare zweistellige Paketversion und Projekt-/Exportanweisungen; Manifest-/Aufgaben-/Speicherkennungen bleiben erhalten. Herkunft und Dateiprüfsummen stehen in `docs/HERKUNFT.json`.

Die bestehende private Site bleibt unter ihrer bisherigen Adresse bestehen. Der Repository-Push ist kein Site-Deployment und ersetzt keine installierte Moodle-ZIP. Neue Veröffentlichungen sollen aus diesem einen GitHub-Master entstehen.

