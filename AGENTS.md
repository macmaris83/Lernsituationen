# Verbindlicher Standard für Lernsituationen

Die vom Nutzer freigegebene Gestaltung in `Vorlagen/Lernsituation_tradiert` und
`Vorlagen/Lernsituation_fuenf_Lernwege` ist der Standard für zukünftige Änderungen und neue
Lernsituationen. Beide Vorlagen auf `main` enthalten die Umsetzung. Der Nutzer
kann diesen Standard jederzeit ausdrücklich ändern.

## Ein fortlaufender Master je Lernsituation

- `master-katalog.json` ist das verbindliche Verzeichnis der aktuellen Master. Vor
  jeder Bearbeitung den aktuellen Branch-Stand synchronisieren und den Master über
  seinen Katalogeintrag finden; alte ZIPs oder Prototypen nicht als Ausgangspunkt nehmen.
- Die vorhandenen Master unter `Fachbereiche/` und `Vorlagen/` fortlaufend bearbeiten.
  Keine parallelen Ordner mit Namen wie `neu`, `final`, `Aktualisiert` oder Versionssuffixen
  anlegen. Weitere Fachbereiche wie ReNo und Geschichte nutzen dieselben Vorlagentypen.
- Sichtbare Paketversionen haben zwei Zahlen, z. B. `1.2`, `1.5` oder `2.1`. Die aktuelle
  Version wird je Master im Katalog gepflegt; pro Master ist nur eine aktuelle ZIP
  im Downloadbestand vorgesehen. Frühere Stände bleiben durch Git nachvollziehbar.
- `python tools/master.py export --all` exportiert den tatsächlichen aktuellen Master.
  Der normale Export führt keine alten Inhaltsgeneratoren aus und setzt keine
  Lehrkräftekonfiguration oder redaktionellen Anpassungen zurück.
- Die ursprünglichen Generatorquellen bleiben für eine bewusst angeforderte
  Neuerzeugung erhalten. Die Generatoren benötigen dafür `--regenerate-masters`.
  Vorher sämtliche zwischenzeitlichen Master- und Editoränderungen in diese Eingaben
  übernehmen und den Unterschied prüfen; eine Neuerzeugung kann sie sonst überschreiben.
- Inhalte in `lesson-data.js` und den zugehörigen HTML-Seiten gemeinsam aktualisieren,
  soweit die vorhandene Runtime beide verwendet. Browserentwürfe vor der Weiterarbeit
  in den passenden Master übernehmen; sie ändern den GitHub-Master nicht automatisch.
- Interne SCORM-, Aufgaben-, Kompetenz- und Speicherkennungen bleiben trotz neuer
  Ordner oder Paketversion erhalten. Eine sichtbare Versionsnummer ist kein Anlass,
  bestehende Lernstände zurückzusetzen.
- `Downloads/README.md` und `Downloads/aktuell.json` verweisen auf den aktuellen Export
  aus dem Katalog. Aktualität nicht aus lexikografischer Dateisortierung, Zeitstempeln
  oder dem Wort „Aktualisiert“ ableiten. Vor Veröffentlichung den aktuellen Master
  mit dem Export vergleichen und die notwendigen Funktionsprüfungen durchführen.

## Getrennte Vorlagentypen

`Vorlagen/Lernpfaduebung/` und `Fachbereiche/Sozialpaedagogik/Lernpfaduebungen/`
gehören zum eigenständigen Vorlagentyp Lernpfadübung. Die nachfolgenden Regeln für
Lernsituationen gelten nicht automatisch für Lernpfadübungen. Für diese gelten
die gesonderten Vorgaben in den dortigen `AGENTS.md`-Dateien.

## Aufgaben und Fokus

- Originale Aufgabenstellungen vollständig anzeigen; keine Textkürzung oder zusätzliche Aufgabenüberschrift. Operatoren bleiben fett. Zusammenhängende Prüfaufträge mit Kriterienliste, Rückmeldung und Überarbeitung bilden eine einzige Aufgabe; Kriterien und optionale KI-Hinweise nicht als eigene Erledigt-Karten behandeln. Reflexionsfragen gemeinsam mit ihrer Einleitung darstellen. Arbeitsformen pro Auftrag differenzieren: Einzelarbeit, Partnerarbeit, Expertengruppe, Gruppenarbeit und externe Prüfgruppen statt pauschalem „Lernteam“. Bei offenen Arbeitsweisen Empfehlungen kennzeichnen.
- Kompetenzbeschreibungen konsequent aus der Ich-Perspektive formulieren und gemeinsame Lernsituationsdaten verwenden. In der Orientierung ein kompaktes Kompetenzprofil zeigen: Netz links (beim Businessplan ca. 25 Prozent kleiner, höchstens 420 Pixel breit), rechts die vier weiteren Kompetenzen mit ihren vollständigen Ich-Beschreibungen in einem 2×2-Raster (auf schmalen Smartphones lesbar untereinander). Die Fachkompetenz mit Beschreibung steht als vorrangige Kompetenz oberhalb des Netzes, ohne doppelte Karte in der rechten Liste. Auf kleinen Bildschirmen lesbar untereinander anordnen. Die vollständigen Ich-Beschreibungen bleiben in den Daten und im Aufgabenfokus erhalten.
- Für längere Fließtexte Blocksatz und automatische deutsche Silbentrennung verwenden (`lang="de"`, `hyphens:auto`); kurze Texte, Aufgabenstellungen, Tabellen und Bedienelemente linksbündig lassen. Unterschiede der Silbentrennung zwischen Browsern berücksichtigen.
- Geschlossene Aufgabenkarten nach tatsächlicher Text- und Symbolhöhe bemessen. Keine feste Mindesthöhe mit großer Leerfläche unter dem Lehrbuchbezug.
- In allen sechs Aufgabenphasen (Informieren, Planen, Entscheiden, Durchführen, Bewerten, Reflektieren) öffnet ein Klick auf die Aufgabenkarte ein Akkordeon auf derselben Seite. Andere Aufgaben und die übergeordnete Navigation werden im Fokus ausgeblendet; der Materialzugriff bleibt verfügbar.
- Die Karte gleitend erweitern und nach oben scrollen; reduzierte Bewegung respektieren. Der offene Rahmen ist hellblau/blau.
- Nummer, GoodNotes-Logo und vorhandene Theorie-/Sozialform-Symbole stehen oberhalb des Auftrags. Die geöffnete Kopfzeile enthält keine Links und klappt durch Klick, Enter oder Leertaste nicht zu. Die Rückkehr erfolgt über die Schaltfläche unten links.
- Nach dem Öffnen keinen orangefarbenen Fokusrahmen um die Kopfzeile anzeigen. Den Tastatur-/Screenreader-Fokus in den Aufgabenbereich setzen; der Aufgabenrahmen bleibt blau. Bedienelemente behalten eine sichtbare Tastaturfokusmarkierung.
- Im Fokus stehen die einzelnen Arbeitsaufträge in eigenen Absätzen. Zusammengehörende Operatorenteile wie „Arbeiten … heraus“ nicht auseinanderreißen.
- Fachkompetenz aus den aktuellen Lernsituationsdaten ausformulieren, mit kleinem kontrastreichem Kompetenznetz. Keine ausklappbare Kompetenzdarstellung.
- Auf Tabletbreite Fachkompetenz links und vollständiger Uhrbereich rechts auf gleicher Höhe; dadurch beginnt der Arbeitsauftrag weiter oben. Auf schmalen Bildschirmen lesbar untereinander anordnen.
- Vorhandene Zeitangaben der Aufgabe als Grundlage des Countdowns nutzen. Uhr, Countdown, Pause und Glockenschalter gehören zusammen. Darunter: „Die Zeit ist eine Orientierung. Du kannst pausieren und nach Ablauf weiterarbeiten.“ Grün über Schwarz zu Rot; nach Ablauf weiterarbeiten erlauben, Fortsetzen ausblenden, optional kurzer Ton. Kein Zurücksetzen und keine erfundenen Zeitangaben.
- Fußleiste: links „Phasenübersicht“, mittig „Aufgabe erledigt“, rechts „Zur nächsten Aufgabe“. Abhaken schaltet nur den rechten Button frei; niemals automatisch wechseln. Bei der letzten Aufgabe führt der rechte Button zurück zur Phasenübersicht.
- Erledigte Karten in der Übersicht vollständig hellgrün hinterlegen (`#f3f8e7`, wie Materialzugriff), mit Haken oben rechts. Kein zusätzlicher Haken links oder unter der Sozialform; keine grüne Aufgabenummer.
- Keinen zusätzlichen Bereich „Arbeitsheft und Abgabe“ mit GoodNotes-Teilen oder Abgabe-Erklärung im Aufgabenfokus ergänzen.

## Materialien und KI-Hilfe

- In der Orientierung (`index.html`) keinen Materialzugriff und keinen Ersatz dafür anzeigen. Auf den übrigen Phasenseiten genau ein hellgrünes Material-Akkordeon „Materialzugriff“ und derselbe Materialzugriff oben auf jeder Materialseite. M-Nummern und vollständige Bezeichnungen anzeigen; geöffnete Links bei Bedarf in weitere Zeilen umbrechen. Kein horizontales Scrollen voraussetzen, damit alle Materialien auch mit der Maus erreichbar sind. Geschlossen bleibt die Auswahl ein schmaler Streifen. Keine doppelte Materialauswahl in einer weiteren Leiste.
- Auf jeder Materialseite muss eine kompakte Phasenübersicht Zugang zu allen acht Stationen der vollständigen Handlung bieten, unterhalb des Materials und unterhalb von „Kurz prüfen“. Keine separate Weiter-Schaltfläche unter dem Material: die Phasenübersicht reicht aus. Die bestehenden Phasensperren gelten auch für diese Materialnavigation und dürfen nicht umgangen werden. Keinen zusätzlichen Button „Zurück zu Informieren“/zur Ausgangsphase anzeigen: Der Rücksprung gilt der konkreten Aufgabe; Phasen sind über die Phasenübersicht erreichbar.
- Die Materialnavigation bleibt kompakt: keine große Kopf-/Fußnavigation und keine GoodNotes-Teilen-Funktion. Genau eine hellgrüne Leiste zum Wechseln zwischen den vorhandenen Materialien; die zusätzliche Phasenwahl und den schwebenden Aufgabenrücksprung blau gestalten. Diese Vorgabe ersetzt das frühere Verbot der Phasenwahl auf Materialseiten und gilt für zukünftige Lernsituationen und SCORM-Paketaktualisierungen.
- Ein schwebender Button unten rechts führt aus dem Material zur zuletzt geöffneten Aufgabe zurück; Phase, Aufgabe und Lernweg erhalten.
- Im kompakten Materialkopf weder das PDF-Symbol noch einen zusätzlichen Aufgabenrücksprung anbieten. Die schwebende Schaltfläche außerhalb des begrenzten Inhaltsrahmens direkt unter `body` anlegen und bei Änderungen des sichtbaren Viewports (WebView/Zoom/Tastatur) nachführen. Den validierten Aufgabenbezug in lokalen Materiallinks mitführen und beim Materialwechsel erhalten; nicht allein auf `sessionStorage` vertrauen. Ohne gültigen Aufgabenbezug die Schaltfläche sichtbar, aber deaktiviert lassen, statt auf eine beliebige Phase zu verweisen. Das Materialfenster soll den Bildschirm dominieren; zusätzliche große Titel-/Beschreibungsblöcke auf Materialseiten ausblenden, Inhalte für Druck und Editor erhalten.
- Prüffragen in der Handlungssituation: Die gesamte Zeile hellblau für offen/noch nicht richtig gelöst und hellgrün für richtig gelöst färben; keine Haken in diesen Zeilen und kein Orange. Textliche Rückmeldung und zugänglichen Status beibehalten.
- Eine kompakte lila KI-Hilfe: AIS.chat-Logo als direkt eingebettetes SVG im Button „KI-Hilfe öffnen“. Kein langer Erklärungstext neben der Aufgabe, keine drei Hilfestufen und keine alten Punkteabzüge.
- Chat im eingebetteten Dialog auf derselben Seite öffnen; nicht automatisch Safari oder ein neues Browserfenster öffnen. Dialogtitel: „KI-Hilfe · Löppt-Pilot“, ausdrücklich mit ö und zwei p. Kurzer Hinweis im Dialog: „Hilfe zur Selbsthilfe · Deine Lösung erarbeitest du selbst.“
- Den freigegebenen AIS-Link aus der vorhandenen Runtime verwenden. Ob AIS Einbettung, Anmeldung und das gewünschte Coaching erlaubt, muss am tatsächlichen Dienst/in der Moodle-App geprüft werden; keine ungetestete Garantie geben. Der Hinweis in der Vorlage ersetzt keine Konfiguration des KI-Gesprächspartners.

## Editor, Freischaltung und SCORM

- Den GoodNotes-Import-Button einschließlich seiner gerahmten Leiste in jeder Aufgabenphase direkt unterhalb der Arbeitsform platzieren, für jeden Lernweg passend. Kein zusätzlicher Import-Button oberhalb des Materialzugriffs.
- GoodNotes-Import ausschließlich in den sechs Aufgabenphasen anbieten und nur die zur aktuellen Phase und zum aktuellen Lernweg gehörenden Arbeitsheftseiten importieren. Kein vollständiges Arbeitsheft vorab für Lernende anbieten. In Orientierung und Handlungssituation fehlen Import-Button und die dadurch leere Leiste samt Rahmen vollständig. Der separate PDF-Button ist ausdrücklich davon zu unterscheiden: Er öffnet das gesamte Dokument zum Ausdrucken, auch für Lernende und unabhängig vom aktuellen Phasenfortschritt. Links ein kleines Acrobat/PDF-Symbol, Beschriftung „Gesamtdokument als PDF“, keine Beschriftung „PDF dieser Phase“. Das Adobe/PDF-Symbol ausschließlich unten rechts in der Fußleiste neben dem Lehrkräftemodus anbieten. Diese kompakte Fußleiste bleibt auch im Aufgabenfokus und auf Materialseiten erreichbar; keine zusätzlichen PDF-Symbole im Materialkopf oder Aufgabenfooter. Lehrkräfte-Exporte bleiben verfügbar.
- Handlungssituation und deren Titelbereich mit derselben leichten Kartenumrahmung wie Orientierung und die übrigen Phasen darstellen.
- Das Akkordeon aus dem aktuellen Aufgabeninhalt erzeugen, nachdem gespeicherte Editor-Änderungen angewendet wurden. Keine unabhängig gepflegte Kopie der Aufgabenstellung einführen.
- Editor-Änderungen sollen nach Speichern und Neuladen in Übersicht und Fokus sowie im neuen SCORM-Export erscheinen. Geänderte Zeitangaben und vorhandene Symbole mit übernehmen.
- Nachfolgende Lernphasen erst freischalten, wenn alle erforderlichen Aufgaben vorheriger Phasen im gewählten Lernweg als erledigt markiert sind. Sowohl obere Navigation, untere Weiter-Schaltfläche als auch direkte Seitenaufrufe müssen die Sperre beachten; gesperrte Links sichtbar kennzeichnen.
- Bestehende SCORM-Schnittstelle, Lernstandsstruktur, Aufgaben-IDs und Kompetenzberichte bewahren. Reine Designänderungen dürfen die vorhandenen Inhalts-Signaturen nicht neu erzeugen. Bei inhaltlich bearbeiteten Exporten wird die Fortschrittsmetadatenstruktur durch den bestehenden Exporter neu berechnet.
- Exportierte ZIPs enthalten `imsmanifest.xml` direkt im ZIP-Wurzelverzeichnis und alle darin aufgeführten Dateien. Der Export muss aktuelle HTML-, CSS- und JS-Dateien verwenden, nicht einen veralteten eingebetteten Paketbestand.
- Bereits hochgeladene Moodle-Pakete werden durch GitHub-Änderungen nicht automatisch aktualisiert; dafür ist eine neue Paketfassung erforderlich.

## Verifikation

Bei Verhaltensänderungen im Browser prüfen: Aufgaben vollständig, Teilaufträge als
Absätze, offener Kopf ohne Einklappaktion, manuelles Weiter, grüne Erledigt-Karten,
Materialwechsel und Rücksprung mit korrektem Lernweg, Phasenwahl und schwebenden Aufgabenrücksprung
auf allen Materialseiten einschließlich Phasensperren, gemeinsame Höhe von
Fachkompetenz/Uhr auf Tabletbreite und keine Überbreite auf schmalen Displays.
Freischaltung oben/unten und direkten gesperrten Aufruf prüfen. Bei Änderungen am
Editor/Export gespeicherte Bearbeitung bis zum Export prüfen; bei Änderungen am
Fortschritt die SCORM-Speicherung und Kompetenzberichte mitprüfen. Tatsächliche
Moodle-/AIS-Prüfungen von lokalen Browser- und API-Simulationen unterscheiden.

## Glas-Optik und Hintergrund

Leicht transparente Flächen mit weichen Schatten, hellen Kanten und moderatem `backdrop-filter`/`-webkit-backdrop-filter` nutzen. Lesbarkeit und eindeutige Statusfarben erhalten; erledigte Aufgaben bleiben klar hellgrün. Für ein freigegebenes Hintergrundbild eine feste, dekorative Ebene über die gesamte Bildschirmfläche mit proportionalem `cover` verwenden, damit das Motiv beim Scrollen stehen bleibt und freie Flächen bei verschiedenen Zoom-/Fenstergrößen füllt. Das exakt bereitgestellte Motiv verwenden; keine Ersatzgrafik als Original ausgeben. Hintergrund im Druck ausblenden.

## Fundus für Dokumentoberflächen

Für Materialien aller Lerngebiete den wiederverwendbaren Fundus `Materialvorlagen/` und dessen `AGENTS.md` nutzen. Dokumenttyp passend auswählen: Outlook für E-Mails, OneNote für Notizen, Teams für Chats, SAP für Geschäftsbelege und Acrobat für PDF-Unterlagen. Nicht pauschal Acrobat für alle Materialien verwenden. Der Fundus ändert keine Fachinhalte und keine bestehende Navigation.

## Schüleransicht der BioCasa-Reihe

In allen sechs Paketen unter `Fachbereiche/BRC/LG01` entfällt der Einordnungsblock in der Orientierung. Keine Übersicht der fünf alternativen Lernwege, keine Lernweg-Badges oder Auswahl durch Schüler anzeigen; die Auswahl bleibt im Lehrkräftemodus. Zugeordnete Originalbilder erscheinen in Orientierung und Handlungssituation und werden nicht neu erzeugt oder beschnitten. MC-Antwortmöglichkeiten stehen einzeln untereinander. Bei Zusammenfassung alter Aufgaben die vorhandenen Fortschrittskennungen bewahren: eine neue Gruppenaufgabe gilt erst als erledigt, wenn sämtliche alten Teilaufgaben erledigt waren. Kompetenzberichte und eine bereits gelesene Orientierung erhalten; Quelle und Migrationsmetadaten enthalten keine personenbezogenen Lernstände.



## BioCasa OS als eigenständiges Lernunternehmen

`Fachbereiche/BRC/BioCasaOS` ist das bestehende Rechnungswesen-Lernunternehmen, keine neu zu erzeugende Lernsituation oder Lernweg-Oberfläche. Die konkreten Produkt- und Prüfregeln stehen in der dortigen `AGENTS.md`. Vorlagenmechaniken wie acht Phasen, Lernwege oder Kompetenzradar werden nicht automatisch in dieses ERP-Werkzeug übernommen. Die zentralen Regeln für einen Master, stabile Kennungen, Versionen und aktuelle Exporte gelten weiter. Der Katalog-Master liegt in `BioCasaOS/dist`; `manifestOnly: true` beschränkt seine Schüler-ZIP auf das Manifest und dessen deklarierte Dateien.
