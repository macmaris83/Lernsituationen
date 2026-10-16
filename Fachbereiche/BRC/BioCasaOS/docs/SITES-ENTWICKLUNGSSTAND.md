> Übernommene Entwicklungsnotizen der Sites-Fassung 0.10.0 vom 16.10.2026.
> Aktueller Einstieg: [README](../README.md), verbindliche Projektregeln: [AGENTS](../AGENTS.md).
> Einzelne ältere Abschnitte beschreiben frühere Oberflächen; der letzte Stand ist in STATUS.md dokumentiert.

# BioCasa OS 0.10.0

Dependency-free educational accounting prototype, delivered both as a private
Sites web preview and a single-SCO SCORM 1.2 package for Moodle.

The authoritative teaching context is the supplied LG02 semester plan of
5 October 2026: nine situations, five learning pathways, own frozen pizza
production, opening date 1 October 2026. Opening balances and IKR account
numbers follow that plan. Teacher solutions are not included.

## Running and packaging

`dist/index.html` is the static entry point. All runtime assets are local classic
JavaScript/CSS; no build, API, CDN, external font or database is required.
`imsmanifest.xml` sits at the root of the SCORM ZIP. Tests: `npm test`.

The default OS demonstration ledger uses LS01 opening balances, the independent
LS02 G1–G8 basics window, and distinctly named additional OS-01–OS-07 examples.
It must never be treated as the canonical LS08 annual closing ledger. The
curriculum view distinguishes implemented functions from future modules.

Money is held in integer cents. Stock changes and finance lines are validated
atomically; corrections append reversals. Read-only SCORM review sessions never
write over the original attempt. SCORM state is compacted and LZW compressed;
limits are checked before mutations. There are no raw scores or network calls.

Actual Moodle installation, mobile webview and visual browser verification
remain to be performed in the school environment. Automated tests cover the
accounting model, state serialization and a simulated SCORM API.

The booking composer fixes debit accounts above the `an` divider and credit
accounts below it. Every row has one amount input and an immutable side.
Multiple rows can be added on both sides. Display ordering never mutates
stored journal records, so existing SCORM attempts and reversals remain valid.

## Learning progression and the supplied Moodle packages

`inventory-cases.js` supplies five independently checked inventory cases: the
LS01/M6 flour case, a source-linked document inventory check and three distinct
OS practice cases. All five are required before the inventory stage. The
prerequisite chain is inventory → inventar → balance sheet → balance accounts
→ income accounts → input/output VAT → further postings → returns → accruals.
Receipt work is embedded, not a separate counted step. Later accounting topics
have compact, checked, independent practice cases in `later-lessons.js`; they do
not add entries to the canonical OS ledger.

The early inventar assignment uses vehicle, furniture, bank and debt. Accounts
160, 260 and 290 are muted, not queried; their 185,110 EUR is a given supplement
to the 667,390 EUR foundation assets. The full 852,500 EUR balance remains intact.
Old flour answers remain one of five proofs; legacy journal and other evidence
survive updates. Warehouse and controlling use the same ledger as before.

The supplied `BioCasa_LG02_Moodle_Lernpakete.zip` contains nine independent
SCORM activities. Their learner-facing titles, material references and required
work inform `curriculum.js`. None of their solution/teacher HTML, PDFs or runtimes
are redistributed. They retain separate activity progress; no cross-activity
SCORM progress synchronization is implied. Source teaching windows stay separate
from the OS demonstration ledger, especially the LS01/M6 flour exercise and the
canonical LS08/09 closing data.

`tutorials.js` maps every seeded business event to its account changes. Context
comes before account arrows, then a checked interpretation. This progress is
separate from the nine learning steps. Drafts are validated by `drafts.js` and do not
count as checked evidence. Autosave captures raw partial forms after 700 ms and
before page/visibility changes; exports include the current inputs even when
the SCORM capacity rejects a further save. Import previews show date and progress
before explicit replacement. Moodle student names are displayed from the API,
not copied into exported state. Legacy compact v1 exports remain readable.

`KURZSTART.txt` includes setup, an iPad mini guide and a school acceptance test.
The automated UI tests run templates/events in a Node VM; they do not substitute
for visual browser testing or a real Moodle/iPad integration test.

## Company branding

Always use the original BioCasa company logo from `/BRC/BioCasa(3).svg`,
retained unchanged at `dist/assets/biocasa-logo.svg`. The shared app header
shows it on every view, including narrow tablet layouts and printed reports.
The SCORM manifest includes it as a local asset. Do not replace it with a
text monogram or a recreated logo in later updates.

## Teacher preview and release policy

The private Site includes `preview.html` with `teacher-preview.js`: all topics
are selectable without synthesizing correct learner answers. Progress stays
actual; local storage has its own preview context, and this page never connects
to an LMS API. Switching off preview applies learner prerequisites to that
separate state. No Moodle teacher-role detection is claimed. These teacher
files are excluded from the learner SCORM manifest and ZIP.

The header offers “Ansicht wählen”: Lernen or Lehrkräftemodus. On the private
Site, changing the mode saves unfinished inputs and switches between the
learner and teacher pages with separate storage. From Moodle, the teacher
choice opens the private hosted preview in a new tab; it does not unlock or
replace the current learner attempt. The company banner uses BioCasa GmbH,
so the product name appears only once in the top header.

`teacher.html` creates a configured Moodle ZIP (using a small ZIP32 writer).
`course-config.js` sets inventar access to automatic, held, or a Europe/Berlin
release time. The five proofs remain necessary in all modes. This is an
instructional package setting; it uses the device clock and is not an LMS
security boundary. It is not imported from a student's state. To change an
existing class activity, the teacher replaces its package file in Moodle;
there is no remote Moodle settings mutation.

Original white BBS 1 Aurich branding appears discreetly on the dark footer,
paired with the fictional-company notice. Both logos remain unmodified.

## Inventar, Bilanz und Erklärhilfen (0.4)

`didactics.js` enthält die gemeinsamen Positionsmodelle, Kontenentscheidungen,
optionalen Erklärschritte, fiktiven Übungsbelege und vier unabhängige Bilanzsimulationen.
Das Inventar wird in Staffelform erstellt; jede Position wird wertgleich in die
Kontenform der Bilanz übernommen. Fortgeschrittene Positionen bleiben vorgegeben
und grau. Lernnachweise speichern nur die Zuordnungen, keine zweite Saldenliste.

Neue Formulare prüfen mit `schema: "2"` sämtliche Zuordnungen beziehungsweise
Kontenentscheidungen. Vorhandene geprüfte Lernstände behalten ihren Fortschritt.
Bereits bestätigte Antworten werden nicht nochmals als identische Entwürfe gespeichert.
Abweichende und unfertige Eingaben werden wortgetreu wiederhergestellt.
Erkläranimationen, Entwürfe und Bilanzsimulationen erzeugen keine Journalbuchungen
und lösen keine Lernschritte. Die neuen Verständnischecks speichern eigene Nachweise. Die optionale Wiedergabe pausiert beim Schließen, Navigieren
oder Hintergrundwechsel und berücksichtigt reduzierte Bewegung.

Die neun fiktiven Belege übernehmen ausschließlich die Belegmetadaten.
Vor dem Buchen wird die eigene Kontierung gegen den gewählten Beleg geprüft.
Ein aktiver Beleg kann nicht zweimal über die Belegauswahl gebucht werden;
eine vollständige Stornierung gibt ihn erneut frei. Freie Buchungen prüfen
weiterhin nur technische Buchbarkeit und müssen fachlich abgeglichen werden.

Automatisierte Prüfungen umfassen die Dokumentmodelle, alle Kontenentscheidungen,
Bilanztypen, tatsächliche Formularabgaben, Belegprüfung, Wiederaufnahme und SCORM.
Visuelle Browser-, iPad- und Schul-Moodle-Tests sind in dieser Umgebung nicht erfolgt.

## Rollencenter und animierte kleine Bilanz (0.5)

BioCasa OS verwendet eine dunkle Kopfzeile, Rollencenter, flache Aktionsleisten,
Aktivitätskacheln, Listen und die Suche nach Seiten/Aktionen (Alt+Q). Die
Oberfläche trägt ausschließlich den Namen BioCasa OS. Originale BioCasa-/Schullogos bleiben erhalten.

`dynamics.css` ist lokal und tabletgerecht. Gesperrte Lernschritte bleiben auch
über Suche/Aktionsleisten gesperrt. Die Lehrkräftevorschau darf sie auswählen.
Die kleine Bilanz zeigt nur betroffene Werte; volle Bilanzsummen sind als solche
beschriftet. Auch unfertige, eigene Eingaben erzeugen eine ungeprüfte Vorschau.
`flow-player.js` animiert einen Betrag vom Soll-/Habenkonto zur Bilanzposition,
mit Pause, Fortsetzen, Wiederholen und einzelnem Weitergehen. Vollständige Entwürfe und der Ergebnisdialog starten nach 500 ms automatisch.
Unveränderte input/change-Ereignisse erhalten denselben DOM-Stand und den Check.
Reduzierte Bewegung verwendet zeitgesteuerte Hervorhebungen ohne Flugbewegung.
Bei fehlender Web Animations API bewegt ein CSS-Fallback den Betrag.
Navigation, fachlich geänderte Eingaben und Hintergrund brechen Flüge ab; eine
Größenänderung (auch iPad-Tastatur) berechnet den laufenden Pfeil neu.

`booking-checks.js` unterbricht vor dem zweiten Zahlenweg: Die ersten drei
unterschiedlichen, vollständig geprüften Buchungen pro Thema erfordern vier
Single-Choice-Antworten, jeweils eine Frage im Blick. Themen: Bestandskonten,
Erfolgskonten, Steuer, weitere Buchungen, Retouren und Abgrenzung. Übungsfälle und
eigene Belegbuchungen verwenden dieselbe Regel; Wiederholen zählt nicht doppelt.
Falsche Antworten geben Regelhinweise, keine Eintragung einer Musterlösung. Bei
vorgegebenen Fällen muss auch der eingegebene Buchungssatz zum Fall passen.
Freie Belege bleiben fachlich selbst zu beurteilen. Neue Themen starten ihren
eigenen Dreierzyklus. Geänderte Eingaben eines geprüften Falls erfordern einen
neuen Check. Nur die getrennte Lehrkräftevorschau bietet einen Überspringen-Knopf.

Maximal 18 kompakte Check-Nachweise werden unter `q` im bestehenden v1-Format
gespeichert. Sie verändern weder Journal noch neun Lernschritte oder Bewertung.
Bestehende Stände ohne `q` bleiben lesbar. SCORM-Kapazitätsprüfung bleibt wirksam.
Die Vorschau-Infrastruktur war nicht verfügbar; automatisierte Modell-/UI-Ereignis-
und Ablaufprüfungen ersetzen keine visuelle iPad-/Moodle-Abnahme.

## Austauschbare Schuljahresdaten und Buchverweise (0.6)

Die bisherige Lernfolge und Navigation bleiben erhalten. `data-defaults.js`
belegt unveränderlich die Ausgangsdaten aus LG02 (5. Oktober 2026).
`data-config.js` wählt die Datenbasis eines konkreten Pakets; `dataset.js` prüft
sie und versieht die rechnerischen Daten mit einer reproduzierbaren Kennung.
Klasse 11 startet mit 852.500 EUR Vermögen, 490.000 EUR Schulden und 362.500 EUR
Eigenkapital. Ergänzende OS-Werte sind mit Rechenwegen gekennzeichnet.
Die Datenansicht im Schülerbereich zeigt Schuljahr, Quelle und Annahmen.

`teacher.html` bietet JSON-Vorlage, Upload, geprüfte Auswahlvorschau, Falljahr,
Lehrkräftevorschau und Paketexport mit den gewählten Daten plus Inventarfreigabe.
Der Upload ist eine Datenkonfiguration, keine MD-Interpretation und kein Upload
ausführbarer Dateien. Er enthält Eurobeträge (höchstens zwei Dezimalstellen),
Eröffnungswerte im bestehenden Kontenplan, drei Roh-/Hilfsstoffartikel, die
bestehenden Demobelege, Inventurparameter, Pizzasimulation, eigene Übungsbelege,
Herkunftstexte und Lehrbuchfundstellen. Die Grundstruktur der ersten 15 Belege
bleibt erhalten; Werte können angepasst und weitere Belege ergänzt werden.
Die Lehrkraft muss geänderte Herkunfts- und Rechenwegtexte fachlich mitpflegen.

Die Prüfung kontrolliert Eröffnungsbilanz, Soll/Haben, Datumsbereich, feste
Artikelbewertung, Zuordnung von Mengen zu Finanzbuchungen und verfügbare Mittel.
Inventurfragen zu Bank/Darlehen, Inventar, Bilanz, Journal und Kennzahlen greifen
auf dieselbe gewählte Basis zu. Methodenübungen bleiben als solche unabhängig.
Drei zusätzliche auswählbare Belege: Büromaterial 5×17 EUR; Wartung 4×125 EUR
mit 95 EUR Steuer; Flyer 300×0,40 EUR mit 22,80 EUR Steuer. Sie werden erst bei
eigener Verbuchung Teil des gemeinsamen Journals.

Der SCORM-/JSON-Stand speichert nur die Datenkennung `h`, keine zweite Datenbasis.
Andere Finanzdaten/Schuljahre werden bei Wiederaufnahme geschützt abgewiesen.
Ein neues Schuljahr erhält eine eigene Aktivität oder einen neuen Versuch.
Die unveränderte MD-Basis nimmt bisherige v1-Stände ohne Kennung wieder auf.
Reine Änderungen von Buchverweisen oder Inventarfreigabe ändern die Finanzbasis
nicht. Eine Lehrkräfte-Datenvorschau nutzt einen getrennten lokalen Stand; der
Schülerstart ignoriert diese lokale Auswahl und verwendet stets die Paketdaten.

Buchverweise werden thematisch aufklappbar angezeigt. Seitenangaben stammen
aus dem in der MD belegten Stichwortregister (u. a. 196–204, 211–227, 242–253,
255–267, 269–297, 302–312 und 322–334). Buchtitel und Auflage sind dort nicht
belegt und werden nicht erfunden. Für Retouren wird fehlende eigene Paginierung
offen benannt. Die Lehrkraft kann die Fundstellen im Jahresdatensatz anpassen.

## Fokusmodus beim Buchen (0.7)

Das Buchungsblatt öffnet im nativen modalen Dialog innerhalb derselben
Moodle-Aktivität. Die Buchungsmaske erhält den größten Bereich; der übrige
Arbeitsbereich ist durch den Dialog nicht bedienbar und über dessen Backdrop
unscharf. Es existiert immer nur ein Buchungsformular. Esc oder „Fokus verlassen“
sichern den aktuellen Entwurf und führen zur normalen Arbeitsansicht zurück.
Bilanz und GuV sind anfangs gemeinsam sichtbar, T-Konten lassen sich hinzuschalten.
Die GuV erklärt bei reinen Bestandsbuchungen ausdrücklich die fehlende Erfolgswirkung. Alle Fenster
verwenden denselben ungeprüften Entwurf und dieselben gebuchten Anfangswerte;
Fensterwechsel buchen nichts und erzeugen keine Lernnachweise. Pfeilanimationen
und die bisherigen Verständnischecks bleiben im Bilanzfenster erhalten.

Die Kontenauswahl verwendet ab 0.8 ein anklickbares Kontenblatt statt Selects.
Kontonummern bleiben unveränderte Formularwerte; die Bezeichnungen folgen den
bereitgestellten IKR-Lehrbuchseiten. Konkrete Inventargegenstände bleiben im
Inventar und in der betrieblichen Beschreibung, nicht in der Kontenauswahl.

Automatisierte Ereignisprüfungen decken Fokuswechsel, Esc, Formular-Eindeutigkeit,
bewusste Fensterwahl und Entwurfswiederaufnahme ab. Der visuelle iPad-/Moodle-Test
steht weiter aus.

## Kontenblatt, Eröffnung und Saldierung (0.8)

`accounts.js` hält den IKR-Auszug nach den Screenshots 10.50.50, 10.51.11 und
10.51.50 vom 16.10.2026 und das gemeinsame T-Kontenmodell. Die fachlichen
Kontonummern, bestehenden Kontenindizes, Eröffnungswerte und Datenkennungen
bleiben unverändert. Der Auswahlknopf öffnet ein Kontenblatt mit Aktiva,
Passiva, Aufwendungen und Erträgen. Die Zielzeile steht im Dialogkopf; ein Klick
übernimmt ausschließlich die Nummer in dieselbe Formularzeile. Lernschranken,
begrenzte Antwortauswahlen und die Materialführung über Lager bleiben erhalten.
Suche und Abbrechen ändern keine Buchungen oder Lernnachweise.

Die neue Bestandskonteneinheit nutzt Schema 4: Alle grundlegenden Konten mit
Anfangsbestand werden selbst aus der bestätigten Bilanz eröffnet; 160/260/290
bleiben vorgegebene spätere Ergänzungen. Das Konto ist in der Eröffnungsübung
zunächst leer. Erst eigene Eingaben erzeugen dort AB-Zeilen. Nach der geprüften
Eröffnung werden dieselben Eröffnungswerte im gemeinsamen Journal fortgeführt.
Der unabhängig gekennzeichnete Übungsabschluss führt Einzahlung und Tilgung
zusammen. Beide Salden und ihre Abschlussseiten müssen selbst eingegeben sein,
bevor die Einheit Erfolgskonten öffnet. Vorhandene Schema-1/2/3-Nachweise bleiben
gültig; neue Aufgaben verlangen Schema 4 mit Gegenkonto und Gegenbuchungsseite.

Bestandskonten zeigen AB auf der sachlich richtigen Seite (auch AB 0),
Erfolgskonten keinen AB. Nur beim geprüften Abschluss sperrt eine Buchhalternase
die freien Zeilen der kürzeren Seite nach Eintrag des Saldos; bei gleicher
Zeilenzahl entfällt sie.
Soll und Haben stehen in einer gemeinsamen Tabelle, einschließlich einer
gemeinsamen Summenzeile auf gleicher Höhe. Der geprüfte
Abschluss ergänzt den Saldo auf der kleineren Seite und zeigt gleiche Summen
mit Doppelstrich. Der Lernende entscheidet in jeder Einheit selbst über Betrag,
Abschlussseite, Gegenkonto und Gegenbuchungsseite. Erst vier passende Angaben
tragen den Abschluss und die orange markierte Gegenbuchung ein. Der Rechner
kann das selbst berechnete Ergebnis nach Bestätigung in das gewählte Feld schreiben.
Entwurfszeilen bleiben als solche erkennbar; der Abschluss betrifft den gebuchten
Stand. Das SBK (801) bzw. die GuV (802) zeigt in einem zweiten T-Konto die
Gegenbuchungen der bisher geprüften Einzelabschlüsse. Diese didaktische
Abschlussansicht führt keine zweite laufende Finanzbuchung aus und verändert
die fortgeführten Auswertungswerte nicht. Ein vollständiger Jahresabschluss mit
GuV-Übertrag ins Eigenkapital ist weiterhin ein eigener Ausbauschritt.
Die Nachweise liegen getrennt im Stand (`c`); neue Buchungen verlangen den
Abschluss betroffener Konten erneut. Alte Vierer-Nachweise bleiben lesbar, neue
Sechser-Nachweise enthalten zusätzlich Gegenkonto und Gegenbuchungsseite.

Kontenabschluss-Regeln abgeglichen mit Europa-Lehrmittel, Leseprobe 76762-3,
S. 10–11: https://www.europa-lehrmittel.de/leseprobe/76762-3.pdf.
Automatisierte Prüfungen decken selbst entschiedene Saldierung, Gegenbuchungen, Eröffnungsseiten,
Korrekturbuchungen, SCORM-Wiederaufnahme, Speichergrenzen und Kontenblatt-Auswahl
ab. Visuelle Browser-/iPad-/Moodle-Prüfung bleibt offen.

Die Lernweg-Auswahl und W1–W5-Kennzeichnungen entfallen im OS. Die neun
Lernschritte, Moodle-Zuordnung und optional aufklappbaren Hilfen bleiben
erhalten. Alte gespeicherte `level`-Werte werden weiterhin gelesen, steuern
aber keine sichtbare Auswahl und verändern keine fachlichen Anforderungen.

T-Kontenzeilen (0.10.0): EBK ersetzt die bisherige AB-Beschriftung. Gegenkonten
werden vollständig mit IKR-Nummer und Titel angezeigt; bei zusammengesetzten
Buchungen werden sämtliche gegenüberliegenden Konten aufgeführt, ohne den
Zeilenbetrag zu vervielfachen. Buchungsdatum und Ursprung kommen aus dem Journal,
Entwurfsdaten direkt aus der Maske. Nur Startbuchungen (`seed`) und übernommene
Eröffnungsbestände sind grau; eigene Buchungen werden nicht wegen ihres Datums
als vorgegeben markiert. Die Kontoansicht ordnet Buchungen chronologisch.

Ein nativer Mouseover-Text und eine per Touch/Tastatur aufklappbare Zeile zeigen
den betrieblichen Hintergrund und die Belegreferenz. Das Aufklappen ist eine
reine Ansicht. Finanzwerte, Belege, Lernerfolg und bestehende Abschlussnachweise
bleiben unverändert; deren bisherige Signaturen werden weiterhin verwendet.

Bilanzwirkung und Buchungssatz (0.10.0): Die kleine Bilanz und die Darstellung nach
einer Buchung zeigen stets die Gruppen Anlagevermögen, Umlaufvermögen, Eigenkapital
und Fremdkapital. Gruppenüberschriften sind grau. Betroffene Konten stehen mit
IKR-Nummer, Titel und signiertem Veränderungsbetrag nebeneinander, soweit der
Platz reicht. Vorher-/Nachher-Werte entfallen. ARA und PRA bleiben bei Bedarf
eigene Abgrenzungspositionen; sie werden nicht als Vorrat oder Schuld umsortiert.
Animationen behalten ihre Kontenziele und Verständnischecks.

Die Buchungssatzdarstellung nutzt eine Tabelle: Konten links, Soll-/Habenbeträge
in zwei rechten Spalten. Sollkonten stehen zuerst; weitere Konten derselben
Seite werden mit „und“ verbunden. Ein zusätzliches „an“ entfällt in der Tabelle. Jeder Betrag
erscheint nur auf seiner Seite. Buchungsmaske, Beträge und Speicherdaten sind
durch diese Darstellungsänderung unverändert.

## Anpassbare Arbeitsansicht (0.9)

Zwei angedockte Bereiche zeigen Buchung und Veränderungen. Seiten können getauscht
werden; auf schmalen Bildschirmen ändert dies die vertikale Reihenfolge. Ein
Pointer-/Touch-Trenner und ein nativer Range-Regler ändern den Buchungsanteil
zwischen 35 und 65 Prozent. Pfeiltasten, Home/End und ein Reset ergänzen die
Bedienung. Pointer-Abbruch, Esc während des Ziehens, Fokusverlust und ein erneuter
Render brechen die laufende Größenänderung ab. Es werden keine Formulare geklont
oder beim Umordnen neu eingesetzt.

Bilanz/GuV stehen standardmäßig nebeneinander, sofern Platz vorhanden ist; sie
können bewusst umgeordnet, gestapelt oder geschlossen werden. T-Konten bleiben
optional. Die GuV ist auch ohne Erfolgswirkung verfügbar. Die Tabelle lässt
das zusätzliche „an“ weg; die Soll-/Haben-Spalten bestimmen die Zuordnung.

Optionale Entwurfsdaten `focus: [Breite, Seite, Stapelung, GuV-zuerst, Fenstermaske]`
speichern die Ansicht mit fünf streng validierten kleinen Ganzzahlen. Standardwerte
werden nicht zusätzlich gespeichert. Alte Stände brauchen keine Migration.
Änderungen betreffen nur Darstellung und Entwürfe, keine Buchungen oder Nachweise.
Die größte bestehende Moodle-Wiederaufnahmeprüfung enthält auch angepasste Ansichten.


Rechenhilfe (0.10.0): Ein kleiner ±-Knopf am Betragsfeld öffnet den Rechner im
selben Formular. Der Zielname bleibt sichtbar. Runde Touch-Tasten (mindestens
44 px), dunkle Anzeige und orange Plus-/Minus-/Gleich-Tasten; keine weiteren
Rechenarten. Der Rechner arbeitet ausschließlich mit den selbst eingegebenen
Zahlen in ganzen Cent. Erst nach „=“ ist „Ergebnis übernehmen“ freigegeben.
Dieser Klick schreibt nur in das zuvor gewählte, noch verbundene Eingabefeld
und löst dessen normale input/change-Ereignisse aus. Er prüft keine Aufgabe,
erzeugt keine Buchung und wählt keine Kontenseite. Rechner und Zielzuordnung
bleiben flüchtige Bedienzustände; übernommene Aufgabeneingaben werden regulär
gesichert. Große Summen und Fehler haben eine kontrollierte Rückmeldung.
