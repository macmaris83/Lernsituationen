# M1 · Grundlagen der Lagerhaltung

## 1.1 Warum werden Waren gelagert?

Lagerhaltung sorgt dafür, dass Waren und Materialien zum benötigten Zeitpunkt verfügbar sind. Sie kann Schwankungen zwischen Beschaffung, Produktion und Absatz ausgleichen. Gleichzeitig verursacht Lagerhaltung Kosten und bindet Kapital.

Mögliche Aufgaben der Lagerhaltung:
- Sicherstellung der Liefer- und Produktionsfähigkeit
- Ausgleich unterschiedlicher Zeitpunkte von Beschaffung und Bedarf
- Bereitstellung von Waren für Versand und Verkauf
- Schutz und geordnete Verwaltung der Bestände

Zu den möglichen Kosten gehören beispielsweise Raum- und Flächenkosten, Personal, technische Ausstattung, Energie, Versicherung, Verwaltung und Kapitalbindung.

## 1.2 Eigenlagerung

Bei der Eigenlagerung organisiert das Unternehmen die Lagerhaltung selbst. Das Lager kann sich in eigenen oder angemieteten Räumen befinden. Das Unternehmen trägt die Verantwortung für Organisation, Bestandsführung und Abläufe.

**Mögliche Vorteile**
- unmittelbare Kontrolle über Bestände und Abläufe
- direkter Zugriff auf die Waren
- Prozesse können an die eigenen Anforderungen angepasst werden
- enge Abstimmung mit anderen Unternehmensbereichen

**Mögliche Nachteile**
- Kosten für Räume, Ausstattung und Personal
- eigener organisatorischer und administrativer Aufwand
- Verantwortung für Lagerprozesse und Bestandsführung
- Kapazitäten können bei schwankendem Bedarf ungenutzt bleiben oder knapp werden

## 1.3 Fremdlagerung

Bei der Fremdlagerung übernimmt ein externer Dienstleister Lageraufgaben. Je nach Vereinbarung können dazu auch Wareneingang, Bestandsverwaltung, Kommissionierung oder Versand gehören.

**Mögliche Vorteile**
- keine oder geringere eigene Investitionen in Lagerflächen und Ausstattung
- Nutzung externer Kapazitäten und Fachkenntnisse
- mögliche Flexibilität bei wechselndem Lagerbedarf
- Entlastung eigener Mitarbeitender von bestimmten Lageraufgaben

**Mögliche Nachteile**
- Abhängigkeit vom Dienstleister
- weniger unmittelbare Kontrolle über Lagerabläufe
- Kosten für vereinbarte Dienstleistungen
- zusätzlicher Abstimmungs- und Kommunikationsbedarf

## 1.4 Vergleichskriterien

Vergleichen Sie Eigen- und Fremdlagerung beispielsweise anhand folgender Kriterien:

- Kosten und Kapitalbindung
- Kontrolle und Zugriff auf Bestände
- Flexibilität bei schwankendem Bedarf
- organisatorischer Aufwand
- Qualität und Zuverlässigkeit der Abläufe
- Abhängigkeit von externen Dienstleistern
- Abstimmung mit Versand und Kundenaufträgen

**Arbeitsauftrag:** Erstellen Sie einen Kriterienvergleich. Leiten Sie daraus ab, welche Aspekte für die Lagerhaltung der Global Bike Deutschland GmbH besonders bedeutsam sind.

---

# M2 · Grundlagen der ABC-Analyse

## 2.1 Zweck

Die ABC-Analyse ordnet Artikel nach ihrer wirtschaftlichen Bedeutung. Als Grundlage dient in dieser Lernsituation der Verbrauchswert.

**Verbrauchswert = Jahresverbrauch × Stückpreis**

Die Artikel werden nach ihrem Verbrauchswert absteigend sortiert. Anschließend wird berechnet, welchen Anteil jeder Artikel am gesamten Verbrauchswert hat und wie sich die Anteile kumulieren.

## 2.2 Typische Einteilung

Als häufig verwendete Orientierungswerte gelten:

- **A-Güter:** hoher Anteil am gesamten Verbrauchswert
- **B-Güter:** mittlerer Anteil
- **C-Güter:** geringer Anteil

Eine häufig genutzte grobe Orientierung für die Verteilung des Verbrauchswertes ist etwa 80 % für A-Güter, 15 % für B-Güter und 5 % für C-Güter. Diese Werte sind keine allgemeingültigen Naturgesetze. Maßgeblich sind die im Unterricht bzw. in der Datengrundlage festgelegten Klassengrenzen.

## 2.3 Arbeitsschritte

1. Verbrauchswert jedes Artikels berechnen.
2. Gesamtverbrauchswert aller Artikel berechnen.
3. Artikel nach Verbrauchswert absteigend sortieren.
4. Prozentualen Anteil jedes Artikels am Gesamtverbrauchswert berechnen.
5. Prozentanteile kumulieren.
6. Artikel anhand der vorgegebenen Klassengrenzen in A, B und C einteilen.

**Arbeitsauftrag:** Erläutern Sie, warum eine ABC-Analyse eine gezieltere Steuerung von Lagerbeständen ermöglichen kann. Benennen Sie auch eine Grenze der Analyse.

---

# M3 · Excel-Arbeitsgrundlage zur ABC-Analyse

## 3.1 Tabellenaufbau

Legen Sie in Excel eine Tabelle mit folgenden Spalten an:

| Spalte | Inhalt |
|---|---|
| A | Materialnummer |
| B | Artikelbezeichnung |
| C | Jahresverbrauch |
| D | Stückpreis |
| E | Verbrauchswert |
| F | Anteil am Gesamtverbrauchswert |
| G | Kumulierte Prozentwerte |
| H | ABC-Klasse |

Die [Excel-Arbeitsdatei ABC_Arbeitsdatei.xlsx](ABC_Arbeitsdatei.xlsx) enthält die fünf Übungsdatensätze aus M8. Die Artikel-IDs A bis E sind reine Übungskennungen. Die Tabelle nutzt die Zeilen 2 bis 6.

## 3.2 Formeln

Für die fünf Datensätze in den Zeilen 2 bis 6:

**Verbrauchswert in E2**
```excel
=C2*D2
```

**Gesamtverbrauchswert**
```excel
=SUMME(E2:E6)
```

**Prozentualer Anteil in F2**
```excel
=E2/SUMME($E$2:$E$6)
```

Formatieren Sie die Spalte F als Prozentwert.

Sortieren Sie anschließend die gesamte Tabelle nach Spalte E absteigend. Achten Sie darauf, dass alle Spalten gemeinsam sortiert werden und die Datensätze vollständig zusammenbleiben.

**Kumulierter Prozentwert in G2**
```excel
=F2
```

**Kumulierter Prozentwert ab G3**
```excel
=G2+F3
```

Übernehmen Sie die Formel für die weiteren Zeilen. Die kumulierten Prozentwerte zeigen, wie viel Prozent des gesamten Verbrauchswertes bis zum jeweiligen Artikel erreicht sind.

## 3.3 ABC-Klasse

Verwenden Sie für jeden Artikel den kumulierten Endwert seiner Zeile. A reicht bis einschließlich 80 %, B über 80 % bis einschließlich 95 %, C über 95 %. Dokumentieren Sie, welche Grenzwerte verwendet wurden. Runden Sie erst für die Darstellung; für die kumulierte Berechnung sollten möglichst die ungerundeten Werte verwendet werden.

**Arbeitsauftrag:** Erstellen Sie eine vollständige, sortierte ABC-Auswertung. Prüfen Sie, ob der letzte kumulierte Prozentwert – abgesehen von Rundungsabweichungen – 100 % ergibt.

---

# M4 · Auswertung und Maßnahmen

## 4.1 Ergebnisse interpretieren

Die ABC-Klasse zeigt die Bedeutung eines Artikels gemessen am Verbrauchswert. Sie legt jedoch nicht allein fest, wie ein Artikel gelagert oder beschafft werden sollte.

Berücksichtigen Sie bei Ihrer Bewertung zusätzlich:
- Häufigkeit und Schwankung des Bedarfs
- Folgen eines Fehlbestands
- Lieferzeit und Zuverlässigkeit des Lieferanten
- Wiederbeschaffungsmöglichkeiten
- Aufwand der Bestandskontrolle
- Bedeutung des Artikels für Kundenaufträge und Lieferfähigkeit

## 4.2 Mögliche Maßnahmen

**A-Güter**
- intensive und regelmäßige Bestandskontrolle
- genaue Bedarfsermittlung und Überwachung
- engere Abstimmung mit Einkauf und Lieferanten
- sorgfältige Festlegung von Bestellmengen und Sicherheitsbeständen

**B-Güter**
- regelmäßige, aber weniger intensive Bestandskontrolle
- bedarfsgerechte Bestellplanung
- Überprüfung der Bestände in angemessenen Abständen

**C-Güter**
- vereinfachte Bestandskontrolle
- wirtschaftliche Bündelung von Bestellungen prüfen
- Verwaltungsaufwand möglichst gering halten
- Verfügbarkeit dennoch sicherstellen, wenn Fehlbestände betriebliche Folgen haben

Diese Maßnahmen sind mögliche Ansätze und müssen anhand der betrieblichen Situation begründet werden. Eine C-Klassifizierung bedeutet nicht automatisch, dass ein Artikel unwichtig oder entbehrlich ist.

## 4.3 Verbindung zur Lagerhaltungsentscheidung

Prüfen Sie, ob Eigen- oder Fremdlagerung für bestimmte Artikelgruppen oder Lageraufgaben Vorteile bieten könnte. Berücksichtigen Sie dabei Kosten, Zugriff, Kontrolle, Flexibilität, Dienstleisterabhängigkeit und die Bedeutung der Artikel.

Für die Region Nordwest (Ostfriesland) werden Markt- und Vertriebsentscheidungen vorbereitet. Die operative Lagerung und Warenbewegung verbleibt an den bestehenden Global-Bike-Standorten, insbesondere am Distributions- und Versandzentrum Hamburg. Die Region Nordwest ist kein Lagerstandort und kein SAP-Objekt.

**Arbeitsauftrag:** Entwickeln Sie aus Ihrer ABC-Auswertung konkrete, differenzierte Maßnahmen. Begründen Sie diese unter Einbeziehung der zusätzlichen betrieblichen Kriterien.

---

# M5 · Die wählbaren Lernpakete

Wählen Sie ein Lernpaket. Alle drei Pakete:
- bearbeiten dieselbe Fachkompetenz,
- nutzen dieselbe Datengrundlage,
- enthalten eine vollständige ABC-Analyse in Excel,
- vergleichen Eigen- und Fremdlagerung,
- leiten Maßnahmen für A-, B- und C-Güter ab.

Die Pakete unterscheiden sich in der betrieblichen Funktion und im Adressaten des Handlungsergebnisses. Sie sind gleichwertig.

## Lernpaket A – Arbeitsanweisung für die Lagersteuerung

**Adressat:** Ali Gül, Leitung Lager und Logistik

**Handlungsergebnis:** Eine praxisorientierte Arbeitsanweisung für Mitarbeitende in Lager und Logistik.

Die Arbeitsanweisung soll:
- die Ergebnisse der ABC-Analyse übersichtlich darstellen,
- die Bedeutung der A-, B- und C-Güter erläutern,
- konkrete Regeln zur Kontrolle und Steuerung der jeweiligen Artikelgruppen enthalten,
- geeignete Maßnahmen für die Lagerpraxis formulieren,
- den Vergleich von Eigen- und Fremdlagerung auf die betrieblichen Abläufe beziehen.

**Leitfrage:** Wie sollen Mitarbeitende in Lager und Logistik die unterschiedlichen Artikelgruppen künftig steuern?

## Lernpaket B – Lagerhaltungskonzept für die Geschäftsleitung

**Adressat:** Peter Schwarz und Hans-Werner Schoor

**Handlungsergebnis:** Ein Konzept zur zukünftigen Organisation der Lagerhaltung.

Das Konzept soll:
- die Ergebnisse der ABC-Analyse vollständig auswerten,
- die wirtschaftliche Bedeutung der Artikelgruppen darstellen,
- Eigen- und Fremdlagerung anhand betrieblicher Kriterien vergleichen,
- geeignete Lagerstrategien für A-, B- und C-Güter entwickeln,
- organisatorische Anforderungen und mögliche Auswirkungen benennen.

**Leitfrage:** Wie sollte die Lagerhaltung der Global Bike Deutschland GmbH grundsätzlich organisiert und gesteuert werden?

## Lernpaket C – Entscheidungsvorlage zur Optimierung der Lagerhaltung

**Adressat:** Peter Schwarz und Hans-Werner Schoor

**Handlungsergebnis:** Eine begründete Entscheidungsvorlage zur Optimierung der Lagerhaltung.

Die Entscheidungsvorlage soll:
- die vollständige ABC-Analyse als Zahlen- und Entscheidungsgrundlage enthalten,
- die wirtschaftliche Bedeutung der Artikelgruppen bewerten,
- Eigen- und Fremdlagerung systematisch gegenüberstellen,
- konkrete, differenzierte Maßnahmen für A-, B- und C-Güter vorschlagen,
- eine begründete Empfehlung für die zukünftige Lagerhaltung formulieren.

**Leitfrage:** Welche konkrete Entscheidung zur Optimierung der Lagerhaltung sollte die Geschäftsleitung treffen und warum?

---

# M6 · Fachbegriffsfragen

Bearbeiten Sie die Fragen schriftlich in eigenen Worten. Nutzen Sie die Materialien und die bereitgestellten Daten.

1. Was versteht man unter Lagerhaltung?
2. Was bedeutet Eigenlagerung?
3. Was bedeutet Fremdlagerung?
4. Nennen Sie mögliche Kosten der Lagerhaltung.
5. Was ist der Verbrauchswert eines Artikels und wie wird er berechnet?
6. Welches Ziel verfolgt die ABC-Analyse?
7. Wodurch unterscheiden sich A-, B- und C-Güter?
8. Was bedeutet „kumulierte Prozentwerte“?
9. Warum werden die Artikel vor der Berechnung der kumulierten Prozentwerte absteigend sortiert?
10. Warum reicht die ABC-Klasse allein nicht aus, um eine Lagerentscheidung zu treffen?
11. Welche Kriterien können bei der Entscheidung zwischen Eigen- und Fremdlagerung eine Rolle spielen?
12. Warum ist die Lieferfähigkeit für die Markt- und Kundenentwicklung in der Region Nordwest bedeutsam?

**Zusatzauftrag:** Formulieren Sie drei fachlich richtige Aussagen, in denen Sie mehrere der oben genannten Begriffe sinnvoll miteinander verbinden.

---

# M7 · Wissens-Check

Wähle je Frage eine passende Antwort.


Was kennzeichnet die Eigenlagerung?

- Die Lagerung erfolgt ausschließlich beim Kunden.
- Die Artikel werden ohne Bedarfsermittlung gelagert.
- Die Waren werden grundsätzlich nicht bestandsgeführt.
- Das Unternehmen organisiert und verantwortet die Lagerhaltung selbst.
- Ein externer Dienstleister übernimmt sämtliche Lageraufgaben.
- Die Lagerkosten entfallen vollständig.


Welcher Vorteil kann mit Fremdlagerung verbunden sein?

- Es entstehen grundsätzlich keine Dienstleistungskosten.
- Eigene Lagerkapazitäten und bestimmte organisatorische Aufgaben können entlastet werden.
- Das Unternehmen hat immer uneingeschränkte Kontrolle über alle Abläufe.
- Die Abhängigkeit von externen Partnern entfällt.
- Eine Abstimmung mit dem Dienstleister ist nicht erforderlich.
- Die Lieferzeiten sind immer kürzer.


Wie wird der Verbrauchswert eines Artikels berechnet?

- Stückpreis geteilt durch Lagerbestand.
- Jahresverbrauch geteilt durch Stückpreis.
- Jahresverbrauch plus Stückpreis.
- Stückpreis minus Jahresverbrauch.
- Jahresverbrauch mal Stückpreis.
- Lagerbestand mal Lieferzeit.


Was ist das zentrale Ziel der ABC-Analyse?

- Die Verkaufspreise automatisch festzulegen.
- Die Lagerfläche ohne weitere Daten zu vergrößern.
- Die Lieferanten ausschließlich nach Entfernung zu sortieren.
- Die Lagerdauer aller Artikel zu vereinheitlichen.
- Artikel nach ihrer wirtschaftlichen Bedeutung anhand eines gewählten Kriteriums zu ordnen.
- Alle Artikel aus dem Sortiment zu entfernen, die selten benötigt werden.


Welche Aussage trifft typischerweise auf A-Güter zu?

- Sie haben einen hohen Anteil am gesamten Verbrauchswert.
- Sie haben immer den höchsten mengenmäßigen Verbrauch.
- Sie müssen immer fremdgelagert werden.
- Sie verursachen grundsätzlich keine Lagerkosten.
- Sie werden grundsätzlich nie benötigt.
- Sie haben immer den niedrigsten Stückpreis.


Wie werden die Artikel für die übliche ABC-Auswertung sortiert?

- Absteigend nach Verbrauchswert.
- Aufsteigend nach Stückpreis.
- Aufsteigend nach Artikelbezeichnung.
- Absteigend nach Materialnummer.
- Nach Lagerplatz.
- Nach Lieferantenname.


Was zeigen kumulierte Prozentwerte?

- Die Anzahl der Lieferanten.
- Den bis zu einer Tabellenzeile aufaddierten Anteil am Gesamtverbrauchswert.
- Die durchschnittliche Lieferzeit.
- Den prozentualen Anteil der Lagerfläche.
- Die Anzahl der Kundenaufträge.
- Den prozentualen Anteil der Personalkosten.


Welche Maßnahme kann für C-Güter sinnvoll sein?

- Ein Verzicht auf jede Bestandsführung.
- Für jeden Artikel eine tägliche Einzelprüfung ohne Anlass.
- Eine automatische Einstufung als unwichtig.
- Eine grundsätzlich ausschließliche Fremdlagerung.
- Eine vereinfachte Bestandskontrolle, sofern die betriebliche Bedeutung dies zulässt.
- Eine vollständige Abschaffung aller C-Güter.


Warum reicht die ABC-Klasse allein nicht für eine Lagerentscheidung aus?

- Die ABC-Analyse enthält grundsätzlich keine Zahlen.
- Die ABC-Analyse berücksichtigt automatisch alle Lieferantenrisiken.
- Weitere Faktoren wie Fehlbestandsfolgen, Lieferzeit und Lieferzuverlässigkeit sind ebenfalls relevant.
- Die ABC-Analyse kann nur für Kunden eingesetzt werden.
- Die ABC-Klasse gibt immer den optimalen Lagerort vor.
- Die ABC-Analyse ersetzt jede betriebliche Entscheidung.


Welche Aussage zur Region Nordwest (Ostfriesland) trifft im Modell zu?

- Sie ist ein neu eingerichteter Lagerstandort im ERP-System.
- Sie ist ein Markt-, Vertriebs- und Entscheidungsraum; die operative Logistik läuft über bestehende Standorte, insbesondere Hamburg.
- Dort müssen neue SAP-Stammdaten angelegt werden.
- Dort werden grundsätzlich alle Waren gelagert.
- Sie ersetzt den Distributionsstandort Hamburg.
- Sie ist ein neuer Produktionsstandort.

---

# M8 · Übungsaufgaben

Bearbeite die Rechenaufgaben und notiere bei jeder Rechnung die Einheit. Bei Auswahlfragen wählst du eine Antwort.

## Datengrundlage für die Rechenübungen

| Artikel | Jahresverbrauch | Stückpreis |
|---|---:|---:|
| Artikel A | 120 | 45 € |
| Artikel B | 80 | 25 € |
| Artikel C | 300 | 32 € |
| Artikel D | 50 | 20 € |
| Artikel E | 90 | 30 € |

Den Gesamtverbrauchswert ermitteln Sie aus allen fünf Zeilen.

Für die Prozent- und Kumulationsaufgaben gilt: Rechnen Sie möglichst mit ungerundeten Werten und runden Sie erst das Endergebnis auf zwei Nachkommastellen.

## Multiple Choice

**Aufgabe 1:** Was ist ein typisches Merkmal der Eigenlagerung?


Was ist ein typisches Merkmal der Eigenlagerung?

- Ein externer Dienstleister übernimmt die gesamte Lagerorganisation.
- Die Lagerhaltung verursacht keine Kosten.
- Das Unternehmen organisiert die Lagerhaltung selbst.
- Die Waren werden nicht kontrolliert.



**Aufgabe 2:** Welcher Aspekt kann ein Vorteil der Fremdlagerung sein?


Welcher Aspekt kann ein Vorteil der Fremdlagerung sein?

- Die Kontrolle über alle Abläufe ist immer größer.
- Eigene Lagerkapazitäten können entlastet werden.
- Eine Abstimmung mit dem Dienstleister ist nie nötig.
- Es entstehen grundsätzlich keine Kosten.



**Aufgabe 3:** Welche Aussage beschreibt A-Güter typischerweise?


Welche Aussage beschreibt A-Güter typischerweise?

- Sie werden grundsätzlich selten benötigt.
- Sie haben einen hohen Anteil am gesamten Verbrauchswert.
- Sie sind grundsätzlich unwichtig.
- Sie haben immer den geringsten Verbrauchswert.



**Aufgabe 4:** Welche Maßnahme passt typischerweise zu A-Gütern?


Welche Maßnahme passt typischerweise zu A-Gütern?

- Eine intensive und regelmäßige Bestandskontrolle.
- Ein vollständiger Verzicht auf Bestandskontrolle.
- Eine automatische Abschaffung der Artikel.
- Eine zufällige Bestellung ohne Bedarfsermittlung.



## Numerische Eingaben

**Aufgabe 5:** Berechnen Sie den Verbrauchswert von Artikel A.


**Eingabe**  ___________________________________



**Aufgabe 6:** Wie hoch ist der Gesamtverbrauchswert aller fünf Artikel?


**Eingabe**  ___________________________________



**Aufgabe 7:** Artikel A hat einen Verbrauchswert von 5.400 €. Wie hoch ist sein Anteil am Gesamtverbrauchswert von 20.700 €? Geben Sie den Prozentwert ohne Prozentzeichen ein und runden Sie auf zwei Nachkommastellen.


**Eingabe**  ___________________________________



**Aufgabe 8:** Artikel C hat einen Verbrauchswert von 9.600 € und Artikel A von 5.400 €. Wie hoch ist der kumulierte Anteil nach diesen beiden Artikeln? Berechnen Sie mit ungerundeten Prozentwerten und runden Sie das Endergebnis auf zwei Nachkommastellen.


**Eingabe**  ___________________________________



**Aufgabe 9:** Berechnen Sie den Verbrauchswert von Artikel B.


**Eingabe**  ___________________________________



**Aufgabe 10:** Artikel E hat einen Verbrauchswert von 2.700 €. Wie hoch ist sein Anteil am Gesamtverbrauchswert von 20.700 €? Geben Sie den Prozentwert ohne Prozentzeichen ein und runden Sie auf zwei Nachkommastellen.


**Eingabe**  ___________________________________



## Multiple Choice zur ABC-Einordnung

Für diese Aufgaben gelten die kumulierten Werte der Übungsdatengrundlage und die in der Aufgabe verwendete vereinfachte Einteilung: A bis einschließlich 80 %, B bis einschließlich 95 %, C darüber.


Der kumulierte Anteil beträgt 72,46 %. Welcher Klasse wird der Artikel zugeordnet?

- C
- B
- Keine Zuordnung möglich
- A




Der kumulierte Anteil beträgt 85,51 %. Welcher Klasse wird der Artikel zugeordnet?

- Keine Zuordnung möglich
- C
- A
- B




Der kumulierte Anteil beträgt 95,17 %. Welcher Klasse wird der Artikel zugeordnet?

- B
- C
- Keine Zuordnung möglich
- A