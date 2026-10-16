# BioCasa OS: verbindliche Projektregeln

## Auftrag und Synchronisation

- Diesen bestehenden Master fortführen: `Fachbereiche/BRC/BioCasaOS`. Kein Neubau, keine zusätzlichen final-/v2-Ordner.
- Repository: `macmaris83/Lernsituationen`; Katalogkennung: `BRC-BIOCASA-OS`; Laufzeitmaster: `Fachbereiche/BRC/BioCasaOS/dist`.
- **Nach jeder konkret vom Nutzer beauftragten Änderung genau diese Änderung samt notwendigen Tests, Dokumentation und Exporten im selben Arbeitsgang in dieses Repository übernehmen.** Der Nutzer hat diese Aktualisierung ausdrücklich beauftragt; nicht bei jedem normalen Commit erneut fragen.
- Keine selbständigen Funktionsausbauten, Aufräumaktionen an fremden Mastern oder zeitgesteuerten Entwicklungsaufträge. Offene Punkte in STATUS.md sind keine Erlaubnis, sie eigenständig umzusetzen.
- Vor Bearbeitung aktuellen Branch/Stand und lokale Änderungen prüfen. Andere Änderungen erhalten, nur auftragsbezogene Dateien committen. Kein Force-Push, kein Reset fremder Arbeit, keine ungeprüfte Konfliktauflösung.
- Committext nennt konkrete Änderung und relevante Prüfung. Erfolgreiche GitHub-Übernahme belegen; bei fehlendem GitHub-Zugriff klar sagen, dass noch kein Sync erfolgt ist.
- Website-Veröffentlichung und Ersetzen einer Moodle-Aktivität sind eigene Aktionen. Ein GitHub-Push veröffentlicht die bestehende Site nicht automatisch. Keine neue Site oder neue Identität anlegen, um einen Sync zu simulieren.

## Produkt und Unterricht

- Dieses ERP-Lernunternehmen ist keine gewöhnliche Lernsituation-Vorlage. Keine Lernweg-Auswahl, Phasenoberfläche, Kompetenzradar oder allgemeine Vorlagenmechanik einbauen. Die übergeordneten Regeln zu Master, Versionen und Kennungen gelten weiter.
- Name ausschließlich BioCasa OS; Dynamics-nahe Arbeitsoberfläche mit BioCasa-Farben. Original-BioCasa-Logo erhalten; weißes BBS-1-Aurich-Logo klein im dunklen Fuß.
- Primäres Ziel: Nutzung innerhalb von Moodle auf dem Schul-iPad. Keine externe API, CDN, Anmeldung oder Safari-Wechsel für das normale Schülerarbeiten voraussetzen.
- Reihenfolge: Inventur → Inventar → Bilanz → Bestandskonten → Erfolgskonten → Vor-/Umsatzsteuer → weitere Buchungen → Retouren → zeitliche Erfolgsabgrenzung (ARA/PRA).
- Fünf korrekt geprüfte Inventurfälle vor Inventar. Zusätzliche Lehrkraft-Freigabe/Termin respektieren. Lehrkräftevorschau darf Voraussetzungen umgehen, erzeugt aber keine Lernernachweise und schreibt nie in die Schüler-LMS-Sitzung.
- Lager (12. Jahrgang) und Controlling (13. Jahrgang) optisch zurücknehmen; freiwillige Vertiefung verwendet denselben Finanzdatenkranz.
- Betriebswirtschaftlichen Vorgang vor den Konten zeigen. Herkunft aus LS/Material oder zusätzliche hellgrüne OS-Übung kenntlich machen. Lehrbuchverweise nur mit belegter Fundstelle.
- Hilfen sind optional aufklappbar; sie erklären Zusammenhänge und lösen keine Aufgabe. Die Lernenden entscheiden Konto, Kontoart, Mehrung/Minderung und Soll/Haben selbst.

## Buchungs- und Darstellungsregeln

- Geld in ganzen Cent; Fachmodell und Lagerbewegungen atomar prüfen. Korrekturen über Gegenbuchungen, kein stilles Überschreiben des Journals.
- Inventar in Staffelform; Bilanz in Kontenform: Aktiva links, Passiva rechts. Vorsteuer, sonstige Finanzanlagen und ARA anfangs grau als spätere Ergänzungen erhalten.
- Fokusansicht: Buchungsmaske im Mittelpunkt; standardmäßig Buchung links, Veränderungen rechts mit Bilanz und GuV. Hintergrund unscharf/inaktiv. Seiten, Breite und Berichtsanordnung bleiben anpassbar; kein dupliziertes Formular.
- Kontenblatt statt Dropdown: anklickbare geordnete Konten, Nummer und fette kanonische Kontenbezeichnung; keine Inventarobjekte als Kontenname. Sollzeilen vor Habenzeilen. Buchungssatz als Tabelle mit Soll-/Habenbetragsspalten; kein zusätzliches „an“ in dieser Tabelle.
- Bilanzwirkung mit grauen Gruppen Anlage-/Umlaufvermögen, Eigen-/Fremdkapital und betroffenen Konten mit signiertem Betrag. Keine Vorher-/Nachher-Spalten in diesem Ausschnitt.
- Zahlenweg automatisch nach ausgeglichenem Entwurf bzw. bestätigter Buchung. Unveränderte input/change/blur-Ereignisse dürfen ihn nicht neu starten. Versteckte Miniaturen nicht als Pfeilziel verwenden. Pause, Wiederholung, Einzelschritte und reduzierte Bewegung erhalten.
- Bei den ersten drei unterschiedlichen Buchungen jedes Themas vor Pfeil 2 vier Single-Choice-Fragen: beteiligte Konten; Bilanzseite; Zu-/Abnahme; Soll-/Habenbuchung. Erst richtige Antworten setzen fort. Kein Buchungseintrag durch den Check.
- Bestandskonten erhalten EBK-Eröffnung auf der richtigen Seite; in der Eröffnungsaufgabe erst nach eigener Entscheidung. Erfolgskonten ohne Anfangsbestand.
- T-Konten: Gegenkontonummer/-bezeichnung plus fachliches Buchungsdatum; übernommene Anfangs-/Startbuchungen grau. Hintergrund per Mouseover und Touch aufklappbar.
- Beim Abschluss in **jeder Einheit** Betrag, Abschlussseite, Gegenkonto und Gegenbuchungsseite vom Lernenden entscheiden lassen. Das ist die spätere Nutzerpräzisierung und ersetzt frühere Wünsche nach automatischer Saldierung ab Erfolgskonten.
- Erst nach korrekter Prüfung orange Saldodifferenz und beide verbundenen Abschlusszeilen zeigen. Bestandskonto gegen 801 SBK, Erfolgskonto gegen 802 GuV; bei Nullsaldo keine erfundene Gegenbuchung.
- Buchhalternase nur beim geschlossenen Konto auf der kürzeren Seite nach Eintrag des Saldos. Bei gleicher Zeilenzahl keine Nase. Beide Summen in derselben gemeinsamen Tabellenzeile, mit Doppelstrich.
- Aktuell didaktische Abschlussansicht: Gegenbuchungen nicht nochmals ins laufende Journal schreiben oder Auswertungswerte nullen. Vollständiger Jahresabschluss ist nicht implementiert.
- Rechner: klein, am Betragsfeld, Touch-Tasten, dunkle Anzeige, orange +/−/=; nur Addition/Subtraktion. Nach = übernimmt erst ausdrückliche Bestätigung das eigene Ergebnis in das gewählte noch verbundene Feld. Keine Kontenwahl, Lösung oder Buchung automatisieren.

## Daten und Lernstände

- Gemeinsame Datenbasis; MD-Ausgangswerte Jg. 11: 852.500 EUR Vermögen, 490.000 EUR Darlehen, 362.500 EUR Eigenkapital, Eröffnung 01.10.2026. Ergänzungen und ihre Herleitung sind als OS-Annahmen kenntlich.
- LS01/M6-Inventurfall und LS08/09-Abschlussdaten nicht unbemerkt zum Demo-Journal addieren. Das Demo-Journal ist kein kanonischer Jahresabschluss.
- Schuljahres-/Datenupload validieren; inkompatible Stände nicht vermischen. Keine neuen Datenkennungen nur wegen einer Anzeigenummer.
- SCORM 1.2: persönliche Wiederaufnahme im selben Versuch, Autosave, kein Raw Score, Read-only/Review respektieren. 4096-Zeichen-Grenze vor Mutationen prüfen; JSON-Sicherung erhalten.
- Manifest-, SCO-, Aufgaben-, Konten-, Speicher- und Fortschrittskennungen stabil halten. Alte Nachweis-/Lernstandsschemata lesbar lassen. Keine realen Schülerdaten ins Repository übernehmen.
- Neue Anzeigenummern dürfen niemals vorhandene Stände zurücksetzen oder neue Speicherplätze erzwingen. Bei einer Änderung des Daten-/Speicherformats vor Veröffentlichung eine geprüfte Migration für alte Stände vorsehen; unbekannte Stände erhalten und verständlich melden, nicht still neu beginnen.
- `tests/fixtures/upgrade-0.10.json` ist ein synthetischer, mit der echten 0.10-Laufzeit erzeugter Ausgangsstand. Der Wiederaufnahmetest muss bei Updates Buchungen, Nachweise und unfertige Eingaben erhalten. Diese alte Testdatei nicht durch einen neu erzeugten aktuellen Stand ersetzen.

## Prüfen und ausliefern

1. `npm --prefix Fachbereiche/BRC/BioCasaOS test`
2. `python3 -m unittest discover -s tools -p 'test_master.py'`
3. Bei Laufzeitänderung neue zweistellige Paketversion gemeinsam setzen: `python3 Fachbereiche/BRC/BioCasaOS/scripts/project.py version X.Y`. npm-SemVer lautet entsprechend X.Y.0.
4. `python3 tools/master.py export --id BRC-BIOCASA-OS`, danach `python3 tools/master.py check --archives` im vollständigen Repository.
5. `python3 Fachbereiche/BRC/BioCasaOS/scripts/project.py check --archive`

`dist` ist hier gepflegter Quellcode. Es darf nicht wegen des allgemeinen Root-Gitignore gelöscht oder durch einen Build ersetzt werden. `manifestOnly: true` exportiert nur die im SCORM-Manifest genannten Schülerdateien. Lehrkräfte-/Konfigurationsdateien bleiben außerhalb der Schüler-ZIP.

VM-Vorlagen-/Ereignistests und simulierte SCORM-API sind keine Browser-, iPad- oder echte Moodle-Abnahme. Den tatsächlichen Prüfstand und Grenzen in STATUS.md nennen. Fehlende Original-MD/Lehrbuchquellen nicht erfinden.

