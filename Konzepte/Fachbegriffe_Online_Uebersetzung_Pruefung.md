# Prüfung: Online-Übersetzung ausgewählter Fachbegriffe

Stand: 14. Oktober 2026. Auftrag: zunächst nur prüfen, noch nicht in Lernpakete einbauen.

## Zielbild

Der deutsche Fachtext bleibt vollständig erhalten. Nach Sprachwahl erscheint nur hinter ausgewählten Fachbegriffen eine Übersetzung in Klammern. Satzbau, Artikel, Arbeitsaufträge und Antworten werden nicht vollständig übersetzt. Beispiel: **Kapitalbedarf (الاحتياج إلى رأس المال)**. Die arabische Formulierung hier illustriert nur die Darstellung; sie ist kein in diesem Test erzeugtes oder fachlich freigegebenes API-Ergebnis.

Eine kuratierte Begriffsliste pro Lernsituation bestimmt, welche Wörter automatisch ergänzt werden. Die automatische Anzeige und Übersetzung sind von der fachlichen Auswahl der Begriffe zu unterscheiden. Bekannte Wortformen können derselben Begriffskennung zugeordnet werden. Ohne Sprachauswahl bleibt Deutsch die Ausgangsansicht. Eine Übersetzung möglichst nur beim ersten Auftreten je Aufgaben-/Materialabschnitt ergänzen, damit der deutsche Text im Vordergrund bleibt.

## Technisch geeigneter Kandidat: LibreTranslate

Anhand des offiziellen Quellcodes und der Herstellerinformationen geprüft:

- `POST /translate` akzeptiert `q` als einzelnen Text oder Liste, `source`, `target` und `format: text`; die Antwort enthält `translatedText`. Daher müssen nur die ausgewählten Begriffe übertragen werden, nicht ganze Aufgabenstellungen oder Schülerlösungen.
- `GET /languages` liefert die auf der konkreten Instanz verfügbaren Sprachen und Zielsprachen. Die Auswahl im Lernpaket sollte daraus abgeleitet werden, statt unbestätigte Sprachen anzubieten.
- Der Server setzt CORS-Header (`Access-Control-Allow-Origin: *`). Das erlaubt grundsätzlich Anfragen aus anderen Web-Oberflächen, einschließlich eines App-WebViews, ohne Öffnen der Übersetzungswebsite. Anfragen ohne Cross-Site-Cookies verwenden; tatsächliche App-/Server-Konfiguration separat prüfen.
- API-Schlüsselpflicht, Zeichenlimits, Anfragelimits und Sperren sind konfigurierbar. Quellcode enthält Fehlerpfade unter anderem für 403 und 429. Ein öffentlicher Server ist daher nicht automatisch kostenlos oder für eine ganze Klasse unbegrenzt nutzbar.
- LibreTranslate verwendet Argos Translate. Der offizielle Modellindex enthält Deutsch → Englisch und Englisch → Arabisch; in der geprüften Indexfassung kein direktes Deutsch → Arabisch-Modell. Argos unterstützt zusammengesetzte Übersetzungen über Zwischensprachen. Arabisch ist technisch erreichbar, wenn die passende Instanz diese Modelle/Zielpaare bereitstellt. Fachwortqualität eines solchen Sprachweges ist noch praktisch zu prüfen.

**Empfehlung:** LibreTranslate für einen ersten technischen Versuch mit einer verlässlich betriebenen Instanz. Vor dauerhaftem Schuleinsatz Übersetzungsqualität mit typischen Fachbegriffen der Businessplan- und Sozialpädagogik-Lernsituationen prüfen. Eine authentifizierte kommerzielle Übersetzungs-API wie Azure Translator bleibt eine Alternative; deren offizielle REST-Beispiele verlangen Dienstzugang, Endpunkt und Schlüssel. Hier wurde kein Qualitätsvergleich durchgeführt.

## Einbindung in das Lernpaket

Die Oberfläche fragt die Übersetzungs-API ab und ergänzt die Antwort als normalen Text im bestehenden HTML. Kein Übersetzungs-iFrame und kein automatischer Aufruf von Safari oder einer externen Website sind nötig. Sprachwechsel tauscht nur die Übersetzungszusätze aus; die deutschen Originalwörter bleiben bestehen. Arabische Zusätze erhalten eine eigene Sprach-/Schreibrichtungskennzeichnung, etwa mit `bdi`, damit deutsche Klammern und Satzzeichen korrekt bleiben.

Die Umsetzung muss folgende Punkte berücksichtigen:

1. Nur freigegebene Begriffe senden; bei mehrdeutigen Begriffen wie „Absatz“ den Fachkontext in der Begriffsliste festlegen und Ergebnisse prüfen.
2. Ergebnisse je Begriff und Sprache zwischenspeichern; bei mehreren Klassen nach Möglichkeit einen gemeinsamen Cache nutzen, um wiederholte Anfragen zu reduzieren.
3. Falls der Dienst einen geheimen API-Schlüssel benötigt, diesen nicht in einem öffentlichen GitHub-Repository oder SCORM-ZIP speichern. Dafür wäre ein kleiner serverseitiger Vermittler oder eine passend verwaltete schulische Instanz nötig. Studierende sollen keine eigenen Dienstkonten benötigen.
4. Bei Zeitüberschreitung, Offlinebetrieb oder erreichtem Anfragelimit bleibt der deutsche Text nutzbar; die Übersetzungsfunktion darf Aufgaben, Timer und Freischaltung nicht blockieren.
5. Übersetzungszusätze als Darstellung behandeln: keine Änderung der deutschen Aufgabeninhalte, Aufgaben-IDs, SCORM-Signaturen oder Erledigt-Markierungen. Lehrkräfte-Editor und Export dürfen keine zufällig geladenen Übersetzungszusätze als neuen Originaltext übernehmen.
6. Die Auswahl konkret benennen, etwa „Arabisch“. „Syrisch“ ist als gewünschte Sprache zunächst zu präzisieren; die konkrete Instanz entscheidet auch über weitere verfügbare Sprachen.

## Umfang der Prüfung und offene Schritte

Geprüft wurden aktuelle offizielle Projektinformationen und API-/Modell-Implementierungen. Es wurde **keine** Übersetzungsfunktion eingebaut, kein Dienst bereitgestellt und kein kostenpflichtiger Zugang angelegt. Es wurden keine Unterrichtstexte oder Schülerdaten an einen Übersetzungsdienst gesendet.

Noch nicht geprüft: Live-Antworten eines ausgewählten Übersetzungsservers, Fachwortqualität, tatsächliche Klassenlast, Verhalten in der installierten Moodle-App sowie Datenschutz-/Betriebsbedingungen einer gewählten Instanz. Die geprüfte CORS-Implementierung ist eine technische Voraussetzung, keine Garantie für jede Moodle-App-/Server-Konfiguration.

Für einen späteren Test wären unter anderem „Kapitalbedarf“, „Distribution“, „Absatzmenge“, „Marktsegment“, „Vorannahme“, „Alltagstheorie“ und „Feinfühligkeit“ sinnvoll. Mehrdeutige Fachwörter verdienen besondere Prüfung. Eine hohe Lernwirksamkeit lässt sich nicht allein aus einer verfügbaren Übersetzungs-API ableiten; die Darstellung soll das Verstehen und den deutschen Wortschatzerwerb unterstützen.

## Geprüfte Quellen

- [LibreTranslate – offizielles Projekt](https://github.com/LibreTranslate/LibreTranslate/blob/main/README.md)
- [LibreTranslate – API, Sprachliste, CORS, Zugang und Limits](https://github.com/LibreTranslate/LibreTranslate/blob/main/libretranslate/app.py)
- [Argos Translate – offizieller Modellindex](https://github.com/argosopentech/argospm-index/blob/main/index.json)
- [Argos Translate – Übersetzung über Zwischensprachen](https://github.com/argosopentech/argos-translate/blob/master/argostranslate/translate.py)
- [Azure – offizielle REST-API-Beispiele und Zugangsvoraussetzungen](https://github.com/Azure-Samples/Cognitive-Services-REST-API-Samples/blob/master/README.md)
