# Prüf- und Übergabestand

Aktueller Stand: **17.10.2026**, Paketversion **0.13**. Ursprung: Sites-Fassung **0.10.0**.

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

Touch-Regeln sehen 48 × 48 CSS-Pixel für Schaltflächen auf Touch-Geräten vor; die spätere Prüfung in 0.12 fand noch ältere, spezifischere Ausnahmen. Daher ist 48 Pixel keine durchgängige Zusicherung für alle Bedienelemente. Formfelder bleiben beschriftet; bereits in Tabellen erkennbare doppelte Feldtitel sind für Hilfstechnologien weiter vorhanden. Keine neue Buchungs-, Freigabe- oder Speicherlogik. Buchungsmodell, Datenbasis, Fortschrittskennungen und SCORM-Schnittstelle bleiben erhalten; geändert sind didaktische Beschriftungen.

Die Versionspflege wurde für diese Veröffentlichung so korrigiert, dass ein Versionswechsel keine Datumsangabe wie 30.10. verändert; der bestehende Versionstest prüft das zusätzlich. Visuelle Browser-/iPad-/Moodle-Abnahme bleibt offen.


## Versionsübergreifende Wiederaufnahme

Ein synthetischer Stand wurde mit dem unveränderten Sites-Quellcommit der Fassung 0.10 erzeugt und unter 0.11 wieder aufgenommen. Der Test erhält neun Lernnachweise, Journal und Salden, einen unfertigen Buchungssatz, Inventur-/Lernantworten und die angepasste Fokusansicht. Lesen schreibt den alten Stand nicht um; erneutes Speichern enthält denselben vollständigen Inhalt. Der Test ist erfolgreich und bleibt als dauerhafte Updateprüfung erhalten. Die Anzeigenummer wird nicht als neue Speicherkennung verwendet. Für künftige Änderungen am Speicher-/Datenformat verlangt AGENTS.md eine geprüfte Migration. Ein anderer Datenkranz wird weiterhin geschützt erkannt. Reales Moodle: dieselbe Aktivität und denselben Versuch fortsetzen; echte Paketupdate-Abnahme bleibt offen.


## Oberfläche 0.12 · verschiebbarer Rechner und sichtbare JSON-Sicherung

Auf Nutzerauftrag öffnet ± den Rechner als kleines Dialog-Flyover oberhalb der Formulare, auch über dem Buchungsfokus und beim Kontenabschluss. Die Kopfzeile lässt sich per Touch/Maus ziehen oder mit Pfeiltasten bewegen; die Position wird auf den sichtbaren Viewport begrenzt, einschließlich Fenster-/Bildschirmtastaturänderungen. Schließen, Esc und Antippen daneben übernehmen keinen Betrag. Erst = und „Ergebnis übernehmen“ schreiben das selbst errechnete Ergebnis ins gewählte Feld. Keine neue Kontenwahl, Buchungs- oder Lernfortschrittslogik.

Auch ohne Bearbeitung erzeugt „Sicherung“ dieselbe bisherige JSON-Struktur. Ein kleiner Dialog zeigt Dateiname, Datum und Lernstand mit echtem Downloadlink. Unterstützte Dateifreigabe bietet zusätzlich „Teilen“; Abbruch/Fehler lassen den Download verfügbar. Der Blob-Link wird nicht mehr nach 1,5 Sekunden entfernt. Der Text bestätigt nur Anforderung oder Übergabe, niemals eine vom Betriebssystem unbestätigte Speicherung. Ob der vorher beobachtete ausbleibende Download durch die konkrete WebView blockiert wurde, ist nicht nachgewiesen.

Touch-Abgleich: Apple nennt als allgemeine Hit-Region 44 × 44 pt (https://developer.apple.com/design/human-interface-guidelines/buttons). Das Web-Ziel 44 × 44 CSS-Pixel ist in WCAG 2.2 SC 2.5.5, Level AAA, beschrieben. Beide Einheiten sind nicht pauschal gleichzusetzen. Im Code gelten für Import in der Befehlsleiste und nun auch in der Seitenleiste mindestens 48 × 48 CSS-Pixel bei any-pointer:coarse. Rechnertasten mindestens 52 Pixel hoch, Schließen/Griff mindestens 48 × 48; die Übernahmetaste wurde von 44 auf 52 Pixel angehoben.

Weitere ältere CSS-Ausnahmen sind dokumentiert, nicht in diesem begrenzten Auftrag umgestaltet: Fokusfenster-Schließen teilweise 38 Pixel hoch, Fokus verlassen und T-Konten-Aufklappzeilen teilweise 44 Pixel. Die Hauptfläche des Verschiebeteilers ist 36 Pixel breit; alternativ steht der Breitenregler bereit. Reale Größen und Treffbarkeit müssen in der Schul-Moodle-App geprüft werden.

Prüfung: 146 Node-Tests, darunter Flyover/Bestätigung, Touch-Ziehen und Tastatur, Begrenzung nach Verkleinern, JSON ohne Bearbeitung, Import unfertiger Eingaben/Nachweise, identische Dateifreigabe und Abbruch. Der alte 0.10-Moodle-Stand bleibt mit Buchungen und neun Nachweisen les-/speicherbar. Vier Projekt-/Versionstests und der bytegenaue Schüler-ZIP-Vergleich gehören zum Release. Visuelle Browser-, iPad- und echte Moodle-Abnahme bleiben offen.


Die anschließend angeforderte Steuerdarstellung übernimmt die Staffelung und Rechnungs-/Pfeillogik der Nutzervorlage `image(20261016-132116).png` als HTML/CSS. Lebensmittelbegriffe ersetzen die Möbelkette: Bauernhöfe → Zutatenhersteller → BioCasa GmbH → Einzelhandel → Privatkundschaft. Grünabstufungen, Original-Firmenzeichen und dunkelgrüne Hervorhebung kennzeichnen BioCasa als Industrieunternehmen. Auf schmalen Bildschirmen stehen dieselben Rechnungen lesbar untereinander. Eintritts-/Pfeilanimation beim Aufklappen respektiert reduzierte Bewegung.

Neutrales OS-Erklärbeispiel: Netto 100/300/700/800 €, einheitlich 7 %, Umsatzsteuer 7/21/49/56 €, Rechnungsbeträge 107/321/749/856 €. Zahllasten 7/14/28/7 € ergeben zusammen die 56 € Steuerlast der privaten Endkundschaft. BioCasa: 480 Umsatzsteuer 49 € minus 260 Vorsteuer 21 € ergibt 28 €. Voller Vorsteuerabzug, 0 € Vorsteuer auf der ersten Stufe und keine weiteren Eingangsrechnungen sind ausdrücklich Modellannahmen. Die vier vorhandenen Hilfeschritte erklären dieselben Beispielwerte; keine Aufgabenlösungen oder Buchhaltungsdaten geändert. Die Grafik liegt ausschließlich in der zunächst geschlossenen Steuerhilfe.

Release-Quelle der bestehenden privaten Site: `fcc6944d204953785486539b574f7b13fd5d2e57` (0.12). GitHub-Master und Site-Laufzeit wurden vor Veröffentlichung bytegleich abgeglichen.


## Oberfläche 0.13 · persönliches Menü, LS-Kacheln und Kontexthinweise

Auf Nutzerauftrag führt der Knopf oben links zu Name und persönlichen Einstellungen. Der von Moodle bereitgestellte Name wird nur angezeigt, nicht neu in die Moodle-Identität geschrieben oder als Profilname exportiert. Ohne Moodle-Namen ist ein Anzeigename mit bis zu 60 Zeichen möglich. Im Buchungsfokus öffnet auch das Firmenzeichen links das persönliche Menü. Der laufende Formular-DOM wird beim Einstellungswechsel nicht neu aufgebaut.

Voreinstellung „Weniger“: Beschriftungen wiederkehrender Nebenaktionen sind durch ihre vorhandenen Symbole ersetzt, mit mindestens 48 Pixel großen Aktionsflächen, zugänglichen Namen und abrufbaren Hinweisen. Aufgaben, Buchungsfragen, Kontenbezeichnungen, Fehlermeldungen und Speicherstatus bleiben erhalten. „Standard“ zeigt kurze Hinweise; „Mehr“ ergänzt längere Kontexthinweise per Mouseover oder Tastaturfokus. Hilfesymbole öffnen dieselben Hinweise per Touch als kleines schließbares Flyover. Hilfebereiche werden nie automatisch geöffnet. Die Hinweise lösen und buchen nichts.

Oben stehen fünf Kernbereiche; Lager/Controlling sind im aufklappbaren Arbeitsbereichsmenü weiterhin mit Jahrgang 12/13 erreichbar und beachten dieselben Sperren. Ist einer davon geöffnet, erscheint er zusätzlich oben. Die zusätzliche Befehlsleiste enthält nur Neue Buchung und Journal; redundantes Speichern, Bilanz und Suchen entfallen dort. Speichern, Datenbasis, iPad-Hilfe und Dateifunktionen bleiben im Menü; Import und Sicherung bleiben als kurze Aktionen beim Übungsstand. Menügruppen sind zunächst geschlossen.

Farbschemata: BioCasa (bisherige Oberfläche), Blau (Flächen/Primäraktionen), Kontrast (dunklere Schrift und deutlichere Grenzen). Keine pauschale Zusicherung einer gesamten WCAG-Konformität; bestehende fachliche Statusfarben und Logos bleiben erhalten. Die Einstellungen gelten auch im Buchungsfokus und in Hinweisen.

Rückwärtskompatible optionale Erweiterung von `drafts.preferences`: Anzeigename, Hilfeumfang und Farbschema. Die bisherige Lernstandsversion 1, Speicherkennung und Aufgabennachweise bleiben unverändert. Fehlende Einstellungen werden nur zur Anzeige mit kompakten Vorgaben ergänzt und nicht still in alte Stände hineingeschrieben. Die 0.10-Testdatei bleibt unverändert; ihre neun Nachweise, Buchungen und unfertigen Eingaben sind weiter les-/speicherbar. Unbekannte/überlange Einstellungswerte weisen den Import ab, ohne den aktiven Stand zu ersetzen.

Prüfung: 156 Node-Tests erfolgreich. Neue Prüfungen: Moodle-Name/Maskierung/kein Identitätsschreiben; kompakte Voreinstellung; Einstellungswechsel ohne Eingabeverlust; lokale Wiederaufnahme und JSON-Import; sichere Mouseover-/Touch-Hinweise; unveränderte Pflichtinhalte; Abweisung ungültiger Einstellungen. Der vollständige simulierte Moodle-Durchlauf mit neun Nachweisen und sechs Belegen enthält jetzt zusätzlich Namen, Hilfeumfang, Farbschema und Fokuslayout und passt weiter in 4096 Zeichen. Die alte 0.10-Wiederaufnahmeprüfung bleibt unverändert erfolgreich. Reale Browser-/iPad-/Moodle-Abnahme bleibt offen; Browsersteuerung ist in dieser Sitzung nicht verfügbar.


Startseite und Lernaufträge stellen die neun bestehenden Lernsituationen als große Kacheln dar. Nummer und Kurztitel, thematisches Symbol und OS-Status erleichtern die Orientierung. Auftrag und originale Materialbezeichnungen bleiben über ein separates 48-Pixel-Infosymbol verfügbar. Die Lernschrittleiste und die bisherige Finanzübersicht sind zunächst eingeklappt, die lange doppelte Auftragsliste entfällt. Beim Öffnen einer Übung steht diese allein mit Rückkehr zur Kachelübersicht; unfertige Antworten bleiben gespeichert. Ein wiederaufgenommener Auftragsstand öffnet weiterhin seine angefangene Übung.

Zuordnung: LS01 enthält Inventur/Inventar/Bilanz, LS02 Bestandskonten und anschließend das Journal, LS03 Erfolgskonten, LS04 Steuer, LS05/06 das vorhandene gemeinsame Fenster weiterer Buchungen, LS07 Abgrenzung. Retouren bleiben ein erforderlicher OS-Zwischenschritt und sind zusätzlich in der Lernschrittübersicht erreichbar. Die getrennte LS08-Abschlussakte ist weiterhin nicht umgesetzt: ihre Kachel öffnet die Materialinformation „In Vorbereitung“. LS09 führt zum optionalen Controlling am aktuellen OS-Stand (Jg. 13), nicht zu importierten bestätigten LS09-Abschlussdaten. Geprüft-Status bezeichnet ausschließlich die OS-Übung. Keine Moodle-Abschlüsse fingiert.

Vier zusätzliche Ereignistests prüfen Kachelzuordnung, Sperren bei direkten Aktionsaufrufen, Lehrkraft-/Retouren-Voraussetzungen, Rückkehr und Wiederaufnahme unfertiger Antworten mit Einstellungen sowie freie Lehrkräfteauswahl ohne Lernnachweis. Sichtbare Nummern, stabile Aufgabenkennungen, Speicherformat und Buchungsdaten wurden dadurch nicht verändert. Visuelle Browser-/iPad-Abnahme bleibt offen.

Release-Quelle der bestehenden privaten Site: `13f5a49518906e376a4658c57066b98f6fa07469` (0.13); Veröffentlichung erfolgreich. Der GitHub-Master und die veröffentlichte Site-Laufzeit sind bytegleich abgeglichen. Die neue Schüler-ZIP enthält alle 27 Manifestdateien aus diesem Master. Eine in Moodle installierte ältere ZIP muss separat in derselben Aktivität ersetzt werden.
