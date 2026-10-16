# Prüf- und Übergabestand

Aktueller Stand: **16.10.2026**, Paketversion **0.11**. Ursprung: Sites-Fassung **0.10.0**.

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

Der erste GitHub-OS-Lauf fand einen übernommenen, fest codierten Scratch-Pfad in einem Paket-Writer-Test. Dessen unnötige Dateiausgabe wurde entfernt; dieselben ZIP-/CRC-Prüfungen arbeiten im Speicher. Die Anwendung und Schüler-ZIP ändern sich dadurch nicht. Der zentrale SCORM-Workflow hat beim Import bereits alle Katalog-Master und aktuellen Archive erfolgreich geprüft.

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



## Oberfläche 0.11 · weniger Text, klare Zeichen

Auf Nutzerauftrag wurden ausschließlich Darstellung und Bedienbeschriftungen vereinfacht. 17 gerenderte Ansichten/Varianten enthalten anfangs 4.669 statt 6.699 sichtbare Wörter (**30,3 % weniger**). Geschlossene Details, versteckte Schritte, dekorative Zeichen und nicht gewählte Auswahloptionen zählen nicht mit. Dies misst Vorlagen, keine echte Bildschirmhöhe; Kontenplan und Geschäftsdaten wurden nicht verkürzt. Kurze Texte, beseitigte Doppelbeschriftungen und aufklappbare Hilfe/Reihenübersicht tragen gemeinsam zur Reduktion bei.

Dieselben Piktogramme kennzeichnen Navigation, Überschriften und Lernschritte. Grün: Bestände; Blau: Finanzen; Violett: Lernaufträge. Spätere Bereiche bleiben grau. Das Original-BioCasa-Logo kennzeichnet zusätzliche Übungsfälle. Farbe ergänzt Zeichen und Beschriftung. Speichern, Sicherung, Import und Prüfen haben einheitliche Symbole und kurze Namen. Weiter bleibt eine bewusst ausgelöste Aktion.

Touch-Regeln setzen mindestens 48 × 48 CSS-Pixel für Schaltflächen auf Touch-Geräten; Antwortzeilen und Aufklappbereiche sind ebenfalls groß antippbar. Formfelder bleiben beschriftet; bereits in Tabellen erkennbare doppelte Feldtitel sind für Hilfstechnologien weiter vorhanden. Keine neue Buchungs-, Freigabe- oder Speicherlogik. Buchungsmodell, Datenbasis, Fortschrittskennungen und SCORM-Schnittstelle bleiben erhalten; geändert sind didaktische Beschriftungen.

Die Versionspflege wurde für diese Veröffentlichung so korrigiert, dass ein Versionswechsel keine Datumsangabe wie 30.10. verändert; der bestehende Versionstest prüft das zusätzlich. Visuelle Browser-/iPad-/Moodle-Abnahme bleibt offen.


## Versionsübergreifende Wiederaufnahme

Ein synthetischer Stand wurde mit dem unveränderten Sites-Quellcommit der Fassung 0.10 erzeugt und unter 0.11 wieder aufgenommen. Der Test erhält neun Lernnachweise, Journal und Salden, einen unfertigen Buchungssatz, Inventur-/Lernantworten und die angepasste Fokusansicht. Lesen schreibt den alten Stand nicht um; erneutes Speichern enthält denselben vollständigen Inhalt. Der Test ist erfolgreich und bleibt als dauerhafte Updateprüfung erhalten. Die Anzeigenummer wird nicht als neue Speicherkennung verwendet. Für künftige Änderungen am Speicher-/Datenformat verlangt AGENTS.md eine geprüfte Migration. Ein anderer Datenkranz wird weiterhin geschützt erkannt. Reales Moodle: dieselbe Aktivität und denselben Versuch fortsetzen; echte Paketupdate-Abnahme bleibt offen.
