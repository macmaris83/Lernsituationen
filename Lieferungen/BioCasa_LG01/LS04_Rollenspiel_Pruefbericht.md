# LS04 · Bei Business Angels pitchen · Version 1.8

Überarbeitet und geprüft am 19. Oktober 2026. Grundlage ist das zuletzt
bereitgestellte LS04-Paket 1.7. Die reguläre Katalogfassung ist parallel auf 1.5
aktualisiert. Beide behalten ihre unterschiedlichen Speicherkennungen
`LG01-LS04` beziehungsweise `BRC-LG01-LS04`.

## Ablauf und persönliche Beteiligung

Die bereits bestehenden Drei- bis Viererteams bleiben zusammen. Ein Schülerteam
präsentiert BioCasa, das andere spielt die Business Angels. Anschließend wechseln
die Teams die Rollen. Jede einzelne Person übernimmt beide Rollen aktiv:

- eigener Sprechanteil im Gruppenpitch und eine beantwortete fachliche Rückfrage;
- in der anderen Runde mindestens eine eigene Frage als Business Angel und ein
  konkreter Beobachtungsbeleg für die Peerbeurteilung.

M6 dokumentiert diese Beiträge pro Gruppenmitglied. Der Pitch dauert wie bisher
höchstens acht Minuten, die Fragerunde fünf Minuten. Zwei Lehrkräfte beobachten
und beurteilen mit demselben Kriterienraster wie die Schülergegengruppe. Sie
beziehen deren begründete Peerbeurteilung ein. Eine gespielte Investitionszusage
ist keine Note; eine neue verbindliche Notengewichtung wird nicht vorgegeben.

Alle fünf Lernwege führen zu denselben Produkten: Gruppenpitch, Finanzierungsanlage,
Rollen-/Beitragsübersicht, ausgefüllter Peerbogen und persönliche Reflexion.
Unterstützung und Selbstständigkeit unterscheiden sich weiterhin.

## Fachliche Überarbeitung

Darlehen, Leasing und Factoring bereiten die konkrete Beteiligungsanfrage vor.
Business Angels werden als Beteiligungskapital sowie mögliche Erfahrung,
Beratung und Netzwerkunterstützung behandelt. Factoring setzt geeignete bestehende
Forderungen voraus und wird nicht als Geldquelle vor dem ersten Verkauf eingeplant.
Die Leasingwirkung wird nicht als zusätzlicher Geldzufluss gezählt.

Die bisherigen BioCasa-Grunddaten bleiben erhalten. Eine mögliche Kombination
ist Leasing, 400.000 Euro Darlehen und eine noch zu verhandelnde Beteiligung von
90.000 Euro. Eine andere begründete Lösung ist möglich. Die Anfrage muss Betrag,
Mittelverwendung, Meilensteine und gewünschte Unterstützung benennen.

Handlungssituation, Kompetenzbeschreibungen, Aufgaben aller Lernwege,
Rollenkarten, Vergleichsakte, Bewertungsbogen, Kurzprüfungen und Lehrkräftehinweise
sind abgestimmt. Darlehens- und Leasingkonditionen bleiben als fachliche Grundlagen
erhalten. Die Lehrbuchhinweise verwenden belegbare Fundstellen: Finanzierung
S. 350, Darlehen S. 391 und Leasing S. 398–399. Für Factoring und Business Angels
wurde keine unbelegte Seitenzahl ergänzt.

## Prüfung

- [Browser- und Lernstandsintegrität](LS04_Pruefberichte/Browser_Lernstand_Integritaet_Pruefung.json):
  Native DOM-Metadaten stimmen mit beiden Paketen überein. Alle 174 bestehenden
  Aufgabenkennungen und Zeitwerte, Konfigurationen, Manifest-/Startkennungen und
  32 Bilddateien sind erhalten. Alte Kompetenzbelege, Feedback und nächste
  Lernschritte bleiben erhalten. Inhaltlich geänderte Aufträge, Orientierung und
  Kurztest erfordern erneute Bearbeitung; passende unveränderte Aufgabenstände
  werden übernommen, auch bei übersprungenen Versionen.
- [26 SCORM-Fälle](LS04_Pruefberichte/SCORM_Pruefung.json): passende, fremde,
  beschädigte und nicht passende Schema-Lernstände in Normal-, Vorschau- und
  Review-Situationen geprüft. Die bekannte Orientierungssperre tritt nicht wieder auf.
- [Zehn Druckfälle mit 340 Einzelprüfungen](LS04_Pruefberichte/Druck_Pruefung.json):
  beide Paketfamilien in allen fünf Lernwegen, vollständige Aufträge und Materialien,
  aktuelle Eingaben, offene Details, weiße A4-Seiten, erhaltene Bilder und Diagramme,
  keine leeren Seiten und kein Text außerhalb des Druckbereichs.
- [iPad-/SCORM-Prüfung](LS04_Pruefberichte/iPad_Pruefung.json):
  Querformat, Hochformat, Split View und Monitoransicht; Touch-Flächen und Überlauf geprüft.
- Alle 60 neu erzeugten Phasen-PDFs sind A4 und stimmen exakt mit ihren eingebetteten
  GoodNotes-Daten überein. Auch die fünf Gesamtarbeitshefte und ihre Daten sind aktuell.
  Die Lehrbuchbilder sind in Originalauflösung eingebettet, keine defekten Bildsymbole.
- [Tatsächlicher Editor-, Material- und GoodNotes-Test](LS04_Pruefberichte/Editor_Material_GoodNotes_Pruefung.json):
  Bilder und Materialrücksprünge, lernwegabhängige Phasenfreigabe sowie ein tatsächlich
  bearbeitetes SCORM-Paket mit aktuellen Laufzeit- und Druckdateien geprüft.
- ZIP-Wurzelmanifest, Dateiliste, CRC, Inhaltsgleichheit mit dem aktuellen Master
  und Sammelarchiv geprüft. `tools/master.py check --archives` prüft zusätzlich den Katalog.

Die sechs Einzelpakete enthalten weiterhin insgesamt 628 Aufgaben. Nur LS04
wurde fachlich geändert; die fünf anderen Lieferpakete bleiben bytegleich in 1.7.
Die 1.8-Sammeldatei LS04–LS06 enthält entsprechend LS04 1.8 und LS05/LS06 1.7.
Der vorherige [Prüfbericht 1.7](Pruefbericht_1.7.md) bleibt als historischer Nachweis erhalten.

Die Prüfung lief in Chromium mit Touch- und SCORM-1.2-Simulation. Eine echte
Moodle-Installation, ein physisches iPad und die native GoodNotes-App wurden nicht
verwendet. Die vorbereitete Einzel-PDF zeigt Lernweg 1 ohne persönliche Testdaten;
die Druckfunktion im Paket übernimmt den aktuellen Lernweg und gespeicherte Eingaben.

Die fortlaufende Katalogquelle liegt in
`Fachbereiche/BRC/LG01/quellen/Reihenplan.md` und
`LS04_Rollenspiel_Materialien.json`. `tools/revise_ls04_roleplay.py` überträgt die
Überarbeitung gezielt auf die beiden bestehenden Paketidentitäten, ohne eine
vollständige Neuerzeugung anderer Lernsituationen.
