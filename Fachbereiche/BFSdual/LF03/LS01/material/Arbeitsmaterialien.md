# M1 · Gemeinsame fachliche Grundlagen: Die optimale Bestellmenge im vereinfachten Modell

### 1. Worum geht es?

Ein Unternehmen muss entscheiden, wie viele Stück eines Artikels es mit einer Bestellung beschaffen soll. Bei kleinen Bestellmengen muss häufig bestellt werden. Dadurch entstehen höhere Bestellkosten. Bei großen Bestellmengen wird seltener bestellt, dafür liegt mehr Ware im Lager und es entstehen höhere Lagerhaltungskosten.

Die optimale Bestellmenge ist im vereinfachten Modell die Bestellmenge, bei der die Summe aus Bestellkosten und Lagerhaltungskosten möglichst gering ist.

### 2. Wichtige Begriffe

- **Jahresbedarf (D):** Gesamtmenge, die innerhalb eines Jahres benötigt wird.
- **Bestellkosten (K):** Kosten, die durch die Durchführung einer Bestellung entstehen.
- **Lagerhaltungskosten (H):** Kosten, die durch die Lagerung einer Einheit für ein Jahr entstehen.
- **Bestellmenge (Q):** Menge, die mit einer einzelnen Bestellung beschafft wird.
- **Durchschnittlicher Lagerbestand:** Im vereinfachten Modell ohne Sicherheitsbestand die Hälfte der Bestellmenge.

### 3. Formel

\[
Q_{opt} = \sqrt{\frac{2 \cdot D \cdot K}{H}}
\]

Dabei gilt:

- \(Q_{opt}\) = optimale Bestellmenge
- \(D\) = Jahresbedarf
- \(K\) = Bestellkosten je Bestellung
- \(H\) = Lagerhaltungskosten je Stück und Jahr

### 4. Beispielrechnung

Für einen Artikel gelten folgende **frei erfundene Übungsdaten**:

- Jahresbedarf: 500 Stück
- Bestellkosten je Bestellung: 20 €
- Lagerhaltungskosten je Stück und Jahr: 2 €

Einsetzen in die Formel:

\[
Q_{opt} = \sqrt{\frac{2 \cdot 500 \cdot 20}{2}}
= \sqrt{10000}
= 100
\]

Die optimale Bestellmenge beträgt im vereinfachten Modell **100 Stück**.

### 5. Weitere Berechnungen

**Anzahl der Bestellungen pro Jahr:**

\[
500 : 100 = 5
\]

Es werden rechnerisch fünf Bestellungen pro Jahr benötigt.

**Jährliche Bestellkosten:**

\[
5 \cdot 20\,€ = 100\,€
\]

**Durchschnittlicher Lagerbestand ohne Sicherheitsbestand:**

\[
100 : 2 = 50 \text{ Stück}
\]

**Jährliche Lagerhaltungskosten:**

\[
50 \cdot 2\,€ = 100\,€
\]

**Summe aus Bestell- und Lagerhaltungskosten:**

\[
100\,€ + 100\,€ = 200\,€
\]

### 6. Vergleich verschiedener Bestellmengen

| Bestellmenge | Bestellungen pro Jahr | Bestellkosten pro Jahr | Durchschnittlicher Lagerbestand | Lagerhaltungskosten pro Jahr | Gesamtkosten |
|---:|---:|---:|---:|---:|---:|
| 50 Stück | 10 | 200 € | 25 Stück | 50 € | 250 € |
| 100 Stück | 5 | 100 € | 50 Stück | 100 € | 200 € |
| 200 Stück | 2,5 | 50 € | 100 Stück | 200 € | 250 € |

Im Beispiel sind die Gesamtkosten bei einer Bestellmenge von 100 Stück am niedrigsten.

### 7. Übungsaufgabe

Für einen anderen Artikel gelten folgende **frei erfundene Übungsdaten**:

- Jahresbedarf: 800 Stück
- Bestellkosten je Bestellung: 18 €
- Lagerhaltungskosten je Stück und Jahr: 2 €

Berechnen Sie die optimale Bestellmenge. Notieren Sie Ihren Rechenweg und erläutern Sie, was das Ergebnis bedeutet.

---

# M2 · Bestellzeitpunktverfahren und Bestellrhythmusverfahren

### 1. Bestellpunktverfahren

Beim Bestellpunktverfahren wird der Lagerbestand laufend überwacht. Sobald der festgelegte Meldebestand erreicht wird, wird eine Bestellung ausgelöst.

Der Meldebestand berücksichtigt:

- den Bedarf während der Lieferzeit,
- den Sicherheitsbestand.

**Vereinfachte Formel:**

\[
Meldebestand = Tagesverbrauch \cdot Lieferzeit + Sicherheitsbestand
\]

**Beispiel mit fiktiven Übungsdaten:**

- Tagesverbrauch: 10 Stück
- Lieferzeit: 5 Tage
- Sicherheitsbestand: 20 Stück

\[
10 \cdot 5 + 20 = 70
\]

Der Meldebestand beträgt 70 Stück. Sobald der Lagerbestand diesen Wert erreicht, wird eine Bestellung ausgelöst.

### 2. Bestellrhythmusverfahren

Beim Bestellrhythmusverfahren wird der Lagerbestand in festgelegten Zeitabständen überprüft, beispielsweise alle zehn Tage. Zu diesen Zeitpunkten wird ermittelt, welche Menge bestellt werden muss.

Die Bestellmenge kann unterschiedlich groß sein, weil sie vom aktuellen Lagerbestand abhängt.

**Vereinfachte Berechnung des Zielbestands:**

\[
Zielbestand = Tagesverbrauch \cdot (Überprüfungszeitraum + Lieferzeit) + Sicherheitsbestand
\]

**Beispiel mit fiktiven Übungsdaten:**

- Tagesverbrauch: 10 Stück
- Überprüfungszeitraum: 10 Tage
- Lieferzeit: 5 Tage
- Sicherheitsbestand: 20 Stück

\[
10 \cdot (10 + 5) + 20 = 170
\]

Der Zielbestand beträgt 170 Stück.

Bei einem aktuellen Lagerbestand von 60 Stück und ohne offene Bestellungen ergibt sich:

\[
170 - 60 = 110
\]

Es müssen 110 Stück bestellt werden.

### 3. Die Verfahren im Vergleich

| Merkmal | Bestellpunktverfahren | Bestellrhythmusverfahren |
|---|---|---|
| Überprüfung | laufend | in festgelegten Zeitabständen |
| Auslöser | Erreichen des Meldebestands | festgelegter Überprüfungszeitpunkt |
| Bestellmenge | abhängig von der gewählten Regelung | abhängig vom aktuellen Bestand |
| Besonderheit | reagiert auf Bestandsveränderungen | regelmäßige Überprüfung |

### 4. Übungsaufgabe

Für einen Artikel gelten folgende **fiktive Übungsdaten**:

- Tagesverbrauch: 8 Stück
- Lieferzeit: 6 Tage
- Sicherheitsbestand: 25 Stück
- Überprüfungszeitraum: 8 Tage
- aktueller Lagerbestand: 45 Stück
- offene Bestellungen: keine

1. Berechnen Sie den Meldebestand.
2. Berechnen Sie den Zielbestand im Bestellrhythmusverfahren.
3. Berechnen Sie die Bestellmenge bei der nächsten Überprüfung.
4. Erklären Sie den Unterschied zwischen Bestellpunkt- und Bestellrhythmusverfahren.

---

# M3 · Just-in-time

### 1. Was bedeutet Just-in-time?

Just-in-time bedeutet, dass Waren möglichst bedarfsgerecht und zeitnah zum benötigten Zeitpunkt angeliefert werden. Ziel ist es, unnötig hohe Lagerbestände zu vermeiden.

Die Ware wird möglichst so angeliefert, dass sie für den vorgesehenen betrieblichen Ablauf zur Verfügung steht, ohne lange im Lager zu liegen.

### 2. Voraussetzungen

Damit Just-in-time funktionieren kann, sind unter anderem erforderlich:

- zuverlässige Lieferanten,
- eine gute Bedarfs- und Absatzplanung,
- kurze und verlässliche Wiederbeschaffungszeiten,
- abgestimmte Kommunikation zwischen den Beteiligten,
- zuverlässige Transport- und Logistikabläufe.

### 3. Chancen und Risiken

| Chancen | Risiken |
|---|---|
| geringere Lagerbestände | stärkere Abhängigkeit von Lieferanten |
| geringere Lagerhaltungskosten | Lieferverzögerungen können Abläufe gefährden |
| weniger Kapitalbindung im Lager | geringe Reserven bei unerwartetem Mehrbedarf |
| bedarfsgerechte Warenbereitstellung | hohe Anforderungen an Planung und Abstimmung |

### 4. Arbeitsaufträge

1. Erklären Sie das Just-in-time-Prinzip mit eigenen Worten.
2. Nennen Sie mindestens drei Voraussetzungen für eine zuverlässige Just-in-time-Beschaffung.
3. Erläutern Sie zwei Chancen und zwei Risiken.
4. Beurteilen Sie, unter welchen Bedingungen Just-in-time für Global Bike Deutschland GmbH sinnvoll sein könnte. Begründen Sie Ihre Einschätzung anhand der genannten Voraussetzungen und Risiken.

---

# M4 · Entscheidungshilfe: Beschaffungsverfahren vergleichen

### 1. Welche Frage beantwortet welches Verfahren?

| Begriff / Verfahren | Zentrale Frage |
|---|---|
| Optimale Bestellmenge | Wie viel soll bestellt werden? |
| Bestellpunktverfahren | Bei welchem Lagerbestand soll bestellt werden? |
| Bestellrhythmusverfahren | Zu welchen festgelegten Zeitpunkten wird der Bestand überprüft und bestellt? |
| Just-in-time | Wann soll die Ware möglichst angeliefert werden? |

Die Verfahren betrachten unterschiedliche Aspekte der Beschaffung. Sie können deshalb nicht einfach als identische Alternativen behandelt werden.

### 2. Mögliche Entscheidungskriterien

Bei einer Beschaffungsentscheidung können unter anderem folgende Kriterien berücksichtigt werden:

- Höhe der Bestellkosten,
- Höhe der Lagerhaltungskosten,
- Höhe und Schwankung des Bedarfs,
- Lieferzeit,
- Zuverlässigkeit der Lieferungen,
- Sicherheitsbestand und Versorgungssicherheit,
- Planbarkeit des Bedarfs,
- verfügbare Lagerkapazitäten.

### 3. Vergleichsmatrix

| Kriterium | Optimale Bestellmenge | Bestellpunktverfahren | Bestellrhythmusverfahren | Just-in-time |
|---|---|---|---|---|
| Bestellmenge | rechnerisch auf Kosten ausgerichtet | abhängig von der Bestellregelung | abhängig vom aktuellen Bestand | bedarfsgerecht |
| Bestellzeitpunkt | nicht im Mittelpunkt | bei Erreichen des Meldebestands | zu festgelegten Überprüfungszeitpunkten | möglichst nah am Bedarf |
| Lagerbestand | Abwägung von Bestell- und Lagerkosten | Sicherheitsbestand kann berücksichtigt werden | Zielbestand kann festgelegt werden | möglichst gering |
| Zentrale Voraussetzung | geeignete Kostendaten | laufende Bestandsüberwachung | regelmäßige Bestandsprüfung | zuverlässige Lieferkette |

### 4. Arbeitsaufträge

1. Erläutern Sie, welche Frage jedes Verfahren beantwortet.
2. Vergleichen Sie die Verfahren anhand von mindestens vier Kriterien.
3. Arbeiten Sie heraus, welche Informationen für eine fundierte Beschaffungsentscheidung noch benötigt werden.
4. Formulieren Sie eine begründete Empfehlung für Global Bike Deutschland GmbH. Machen Sie deutlich, auf welche Kriterien Sie Ihre Empfehlung stützen.

---

# M5 · Auswahl und Begründung des Lernpakets

Sie haben drei Lernpakete zur Auswahl. Alle drei Lernpakete bearbeiten dieselbe Fachkompetenz und enthalten dieselben fachlichen Anforderungen. Sie unterscheiden sich im Zugang und in der Form des Handlungsergebnisses.

- **Lernpaket A:** Beschaffungsleitfaden für den Einkauf – schriftlich, analytisch und strukturiert.
- **Lernpaket B:** Entscheidungsplakat – visuell, übersichtlich und kreativ.
- **Lernpaket C:** Entscheidungsvorlage für die Geschäftsleitung – zusammenhängend, abwägend und entscheidungsorientiert.

### Arbeitsauftrag

1. Entscheiden Sie sich für eines der drei Lernpakete.
2. Begründen Sie Ihre Auswahl.
3. Erläutern Sie, welcher Zugang Ihnen bei der Bearbeitung hilft.
4. Beschreiben Sie, wie Sie in Ihrem Handlungsergebnis zeigen werden, dass Sie die fachlichen Anforderungen erfüllen.

**Wichtig:** Alle Lernpakete sind gleichwertig. Die fachlichen Anforderungen und die Bewertungskriterien sind für alle Lernpakete gleich.

---

# M6 · Gemeinsame Bewertungskriterien für alle Lernpakete

Unabhängig davon, welches Lernpaket gewählt wurde, werden dieselben fachlichen Kriterien angewendet.

| Kriterium | Erwartung |
|---|---|
| Optimale Bestellmenge | Begriff und Ziel werden korrekt erklärt. Die Formel wird richtig verwendet und eine Berechnung wird nachvollziehbar dargestellt. |
| Bestellpunktverfahren | Das Verfahren wird erklärt. Der Meldebestand und seine Bedeutung werden richtig dargestellt. |
| Bestellrhythmusverfahren | Das Verfahren wird erklärt und vom Bestellpunktverfahren abgegrenzt. |
| Just-in-time | Das Prinzip wird erklärt. Voraussetzungen, Chancen und Risiken werden berücksichtigt. |
| Vergleich | Die Verfahren werden anhand geeigneter Kriterien gegenübergestellt. |
| Empfehlung | Eine nachvollziehbare und fachlich begründete Empfehlung wird formuliert. |
| Verständlichkeit | Das Handlungsergebnis ist klar strukturiert und fachlich verständlich. |

Die Darstellungsform wird nicht als Ersatz für fachliche Qualität bewertet. Gestaltung und Übersichtlichkeit werden berücksichtigt, soweit sie das Verständnis und die Nutzung des Ergebnisses unterstützen.

---

# M8 · Übungsaufgaben zur Beschaffungsplanung

**Hinweis:** Die folgenden Aufgaben dienen dem Üben und Festigen. Jede Aufgabe enthält sechs Antwortmöglichkeiten. Es ist jeweils genau eine Antwort richtig.

### Aufgabe 1 – Jahresbedarf

Was beschreibt der Jahresbedarf?

- A: Die Menge, die täglich verbraucht wird.
- B: Die Gesamtmenge, die innerhalb eines Jahres benötigt wird.
- C: Die Menge einer einzelnen Bestellung.
- D: Die Menge, die durchschnittlich auf Lager liegt.
- E: Die Menge, die während der Lieferzeit eintrifft.
- F: Die Menge, die als Sicherheitsbestand vorgesehen ist.



### Aufgabe 2 – Bestellkosten

Welche Kosten gehören zu den Bestellkosten?

- A: Kosten für die Bearbeitung einer Bestellung.
- B: Kosten für die Lagerfläche.
- C: Kosten für die Lagerung über ein Jahr.
- D: Kosten für die Kapitalbindung im Lager.
- E: Kosten für die Durchführung eines Bestellvorgangs.
- F: Kosten für die Versicherung des Lagerbestands.



### Aufgabe 3 – Lagerhaltungskosten

Welche Kosten sind typische Lagerhaltungskosten?

- A: Kosten für das Auslösen einer Bestellung.
- B: Kosten für die Bearbeitung einer Bestellung.
- C: Kosten für Lagerfläche und Lagerbetrieb.
- D: Kosten für die Erstellung einer Bestellung.
- E: Kosten für die Kapitalbindung im Lager.
- F: Kosten für die Prüfung einer Bestellung.



### Aufgabe 4 – Optimale Bestellmenge

Was ist das Ziel der Berechnung der optimalen Bestellmenge im vereinfachten Modell?

- A: Den Jahresbedarf zu erhöhen.
- B: Den Lagerbestand möglichst groß zu halten.
- C: Die Anzahl der Lieferanten zu reduzieren.
- D: Die Summe aus Bestell- und Lagerhaltungskosten möglichst gering zu halten.
- E: Die Lieferzeit zu verkürzen.
- F: Den Sicherheitsbestand auf null zu setzen.



### Aufgabe 5 – Berechnung der optimalen Bestellmenge

Gegeben sind: Jahresbedarf 500 Stück, Bestellkosten 20 € je Bestellung und Lagerhaltungskosten 2 € je Stück und Jahr. Wie hoch ist die optimale Bestellmenge?

- A: 25 Stück
- B: 50 Stück
- C: 75 Stück
- D: 100 Stück
- E: 150 Stück
- F: 200 Stück



### Aufgabe 6 – Durchschnittlicher Lagerbestand

Die Bestellmenge beträgt 100 Stück. Wie hoch ist der durchschnittliche Lagerbestand im vereinfachten Modell ohne Sicherheitsbestand?

- A: 10 Stück
- B: 25 Stück
- C: 50 Stück
- D: 75 Stück
- E: 100 Stück
- F: 200 Stück



### Aufgabe 7 – Meldebestand

Was bedeutet Meldebestand?

- A: Die Menge, die jährlich bestellt wird.
- B: Der Lagerbestand, bei dessen Erreichen eine Bestellung ausgelöst wird.
- C: Die Menge, die ein Lieferant maximal liefern kann.
- D: Der durchschnittliche Lagerbestand.
- E: Die Menge, die am Jahresende übrig bleibt.
- F: Die Bestellmenge je Bestellung.



### Aufgabe 8 – Berechnung des Meldebestands

Tagesverbrauch 10 Stück, Lieferzeit 5 Tage, Sicherheitsbestand 20 Stück. Wie hoch ist der Meldebestand?

- A: 20 Stück
- B: 50 Stück
- C: 60 Stück
- D: 70 Stück
- E: 80 Stück
- F: 100 Stück



### Aufgabe 9 – Bestellpunktverfahren

Was kennzeichnet das Bestellpunktverfahren?

- A: Die Bestellung erfolgt immer am Monatsanfang.
- B: Der Bestand wird laufend überwacht; beim Erreichen des Meldebestands wird bestellt.
- C: Die Bestellung erfolgt ausschließlich nach einem festen Kalender.
- D: Die Ware wird grundsätzlich ohne Lagerung angeliefert.
- E: Der Bestand wird nur einmal jährlich geprüft.
- F: Die Bestellmenge entspricht immer dem Jahresbedarf.



### Aufgabe 10 – Bestellrhythmusverfahren

Was kennzeichnet das Bestellrhythmusverfahren?

- A: Die Bestellung wird ausschließlich bei Erreichen des Meldebestands ausgelöst.
- B: Der Lagerbestand wird nicht überprüft.
- C: Die Überprüfung erfolgt in festgelegten Zeitabständen.
- D: Die Bestellmenge ist immer gleich.
- E: Die Lieferung erfolgt ohne vorherige Bestellung.
- F: Der Bestellzeitpunkt hängt ausschließlich vom Tagesverbrauch ab.



### Aufgabe 11 – Zielbestand

Was beschreibt der Zielbestand im vereinfachten Bestellrhythmusverfahren?

- A: Die Menge, die ein Lieferant auf Lager hat.
- B: Die Menge, die im Vorjahr verbraucht wurde.
- C: Den angestrebten Bestand, auf den bei einer Überprüfung aufgefüllt werden soll.
- D: Die Menge, die täglich bestellt wird.
- E: Die maximale Lagerkapazität.
- F: Die Anzahl der Bestellungen pro Jahr.



### Aufgabe 12 – Bestellmenge im Bestellrhythmusverfahren

Der Zielbestand beträgt 170 Stück. Im Lager befinden sich 60 Stück. Es gibt keine offenen Bestellungen. Wie hoch ist die Bestellmenge?

- A: 60 Stück
- B: 100 Stück
- C: 110 Stück
- D: 120 Stück
- E: 170 Stück
- F: 230 Stück



### Aufgabe 13 – Lieferzeit

Was bezeichnet die Lieferzeit?

- A: Den Zeitraum zwischen zwei Bestandsüberprüfungen.
- B: Den Zeitraum zwischen dem Auslösen einer Bestellung und dem Eintreffen der Ware.
- C: Den Zeitraum, in dem die Ware im Lager bleibt.
- D: Den Zeitraum zwischen zwei Geschäftsjahren.
- E: Den Zeitraum für die jährliche Inventur.
- F: Den Zeitraum zwischen zwei Kundenbestellungen.



### Aufgabe 14 – Just-in-time

Was ist das zentrale Ziel von Just-in-time?

- A: Möglichst große Lagerbestände aufzubauen.
- B: Möglichst frühzeitig und unabhängig vom Bedarf zu bestellen.
- C: Waren möglichst bedarfsgerecht und zeitnah bereitzustellen.
- D: Lieferanten vollständig zu ersetzen.
- E: Die Bedarfsplanung überflüssig zu machen.
- F: Bestellungen grundsätzlich nur einmal im Jahr auszulösen.



### Aufgabe 15 – Voraussetzungen für Just-in-time

Welche Voraussetzung ist für Just-in-time besonders wichtig?

- A: Möglichst große Sicherheitsbestände.
- B: Unregelmäßige Lieferungen.
- C: Fehlende Abstimmung mit Lieferanten.
- D: Zuverlässige Lieferungen und gute Planung.
- E: Möglichst lange Lagerzeiten.
- F: Verzicht auf Bedarfsplanung.

---

# M9 · Wissens-Check: Beschaffungsstrategien

Für Aufgaben mit Mehrfachauswahl müssen alle passenden Antworten ausgewählt werden.

### Aufgabe 1 – Optimale Bestellmenge

**Wählen Sie alle richtigen Aussagen aus.**

Welche Aussagen zur optimalen Bestellmenge im vereinfachten Modell treffen zu?

- A: Sie berücksichtigt Bestellkosten und Lagerhaltungskosten.
- B: Sie führt grundsätzlich zur größtmöglichen Bestellmenge.
- C: Sie zielt darauf, die Summe aus Bestell- und Lagerhaltungskosten zu minimieren.
- D: Sie hängt ausschließlich vom Einkaufspreis der Ware ab.
- E: Eine Veränderung der Bestellkosten kann die optimale Bestellmenge beeinflussen.
- F: Sie ist unabhängig vom Jahresbedarf.



### Aufgabe 2 – Berechnung der optimalen Bestellmenge

**Wählen Sie eine richtige Antwort aus.**

Für einen Artikel gelten folgende fiktive Daten:

- Jahresbedarf: 500 Stück
- Bestellkosten je Bestellung: 20 €
- Lagerhaltungskosten je Stück und Jahr: 2 €

Wie hoch ist die optimale Bestellmenge nach der vereinfachten Formel?

- A: 25 Stück
- B: 50 Stück
- C: 75 Stück
- D: 100 Stück
- E: 125 Stück
- F: 200 Stück



### Aufgabe 3 – Kosten bei optimaler Bestellmenge

**Wählen Sie alle richtigen Aussagen aus.**

Bei einer Bestellmenge von 100 Stück und den Daten aus Aufgabe 2: Welche Aussagen treffen zu?

- A: Es werden rechnerisch fünf Bestellungen pro Jahr benötigt.
- B: Die jährlichen Bestellkosten betragen 100 €.
- C: Der durchschnittliche Lagerbestand beträgt 100 Stück.
- D: Die jährlichen Lagerhaltungskosten betragen 100 €.
- E: Die Summe aus jährlichen Bestell- und Lagerhaltungskosten beträgt 200 €.
- F: Die jährlichen Bestellkosten betragen 200 €.



### Aufgabe 4 – Bestellpunktverfahren

**Wählen Sie alle richtigen Aussagen aus.**

Welche Aussagen beschreiben das Bestellpunktverfahren zutreffend?

- A: Der Lagerbestand wird laufend überwacht.
- B: Eine Bestellung wird ausgelöst, sobald der Meldebestand erreicht ist.
- C: Die Bestellung erfolgt grundsätzlich an einem festen Kalendertag.
- D: Der Bestellzeitpunkt hängt von der Bestandsentwicklung ab.
- E: Der Meldebestand berücksichtigt den Bedarf während der Lieferzeit und den Sicherheitsbestand.
- F: Die Bestellmenge muss bei jeder Bestellung gleich groß sein.



### Aufgabe 5 – Berechnung des Meldebestands

**Wählen Sie eine richtige Antwort aus.**

Für einen Artikel gelten folgende fiktive Daten:

- Tagesverbrauch: 10 Stück
- Lieferzeit: 5 Tage
- Sicherheitsbestand: 20 Stück

Wie hoch ist der Meldebestand?

- A: 20 Stück
- B: 50 Stück
- C: 60 Stück
- D: 70 Stück
- E: 80 Stück
- F: 100 Stück



### Aufgabe 6 – Bestellrhythmusverfahren

**Wählen Sie alle richtigen Aussagen aus.**

Welche Aussagen zum Bestellrhythmusverfahren sind richtig?

- A: Der Lagerbestand wird in festgelegten Zeitabständen überprüft.
- B: Die Bestellmenge kann bei jeder Überprüfung unterschiedlich ausfallen.
- C: Der Bestellzeitpunkt wird ausschließlich durch das Erreichen des Meldebestands bestimmt.
- D: Die Überprüfung kann beispielsweise alle zehn Tage erfolgen.
- E: Das Verfahren setzt eine laufende tägliche Bestandskontrolle voraus.
- F: Der Bestellzeitpunkt orientiert sich am festgelegten Überprüfungsrhythmus.



### Aufgabe 7 – Bestellmenge im Bestellrhythmusverfahren

**Wählen Sie eine richtige Antwort aus.**

Für einen Artikel gelten folgende fiktive Daten:

- Tagesverbrauch: 10 Stück
- Überprüfungszeitraum: 10 Tage
- Lieferzeit: 5 Tage
- Sicherheitsbestand: 20 Stück
- Aktueller Lagerbestand: 60 Stück
- Offene Bestellungen: keine

Der Zielbestand wird mit folgender vereinfachter Berechnung ermittelt:

(Tagesverbrauch × (Überprüfungszeitraum + Lieferzeit)) + Sicherheitsbestand

Wie viele Stück müssen bestellt werden?

- A: 60 Stück
- B: 100 Stück
- C: 110 Stück
- D: 150 Stück
- E: 170 Stück
- F: 190 Stück



### Aufgabe 8 – Vergleich der Bestellverfahren

**Wählen Sie alle richtigen Zuordnungen aus.**

Welche Zuordnungen sind fachlich richtig?

- A: Bestellpunktverfahren – Bestellung bei Erreichen des Meldebestands
- B: Bestellrhythmusverfahren – Bestellung zu festgelegten Überprüfungszeitpunkten
- C: Bestellpunktverfahren – Bestellung ausschließlich in festen Zeitabständen
- D: Bestellrhythmusverfahren – Bestellmenge kann je Überprüfung variieren
- E: Bestellpunktverfahren – laufende Überwachung des Lagerbestands
- F: Bestellrhythmusverfahren – Bestellung immer bei Erreichen eines festen Meldebestands



### Aufgabe 9 – Just-in-time

**Wählen Sie alle richtigen Aussagen aus.**

Welche Aussagen beschreiben das Just-in-time-Prinzip zutreffend?

- A: Materialien werden möglichst bedarfsgerecht und zeitnah angeliefert.
- B: Große Lagerbestände sind das zentrale Ziel des Verfahrens.
- C: Eine zuverlässige Lieferkette ist eine wichtige Voraussetzung.
- D: Verzögerungen bei Lieferungen können die betriebliche Versorgung gefährden.
- E: Eine gute Abstimmung zwischen Bedarf und Lieferung ist wichtig.
- F: Das Verfahren macht eine Planung des Materialbedarfs überflüssig.



### Aufgabe 10 – Auswahl einer Beschaffungsstrategie

**Wählen Sie alle relevanten Entscheidungskriterien aus.**

Welche Faktoren sollten bei der Auswahl einer geeigneten Beschaffungsstrategie berücksichtigt werden?

- A: Höhe der Bestellkosten
- B: Höhe der Lagerhaltungskosten
- C: Zuverlässigkeit der Lieferungen
- D: Vorhandene Lagerkapazitäten
- E: Planbarkeit und Schwankungen des Materialbedarfs
- F: Farbe der Verpackung als alleiniger Entscheidungsfaktor

---

# M10 · Fachbegriffsfragen: Zentrale Begriffe der Beschaffungsplanung

### Aufgabe 1 – Jahresbedarf

**Wählen Sie eine richtige Antwort aus.**

Was versteht man unter dem Jahresbedarf?

- A: Die Menge eines Artikels, die täglich benötigt wird.
- B: Die Gesamtmenge eines Artikels, die innerhalb eines Jahres benötigt wird.
- C: Die Menge, die bei einer einzelnen Bestellung geliefert wird.
- D: Die Menge, die dauerhaft im Lager liegt.
- E: Die Menge, die während der Lieferzeit verbraucht wird.
- F: Die Menge, die als Sicherheitsbestand zurückgehalten wird.



### Aufgabe 2 – Bestellkosten

**Wählen Sie alle richtigen Aussagen aus.**

Was zählt zu den Bestellkosten?

- A: Kosten für die Bearbeitung einer Bestellung.
- B: Kosten für die Erstellung und Prüfung von Bestellunterlagen.
- C: Kosten für die Lagerung der Ware über einen längeren Zeitraum.
- D: Kosten, die bei jeder Bestellung unabhängig von der Bestellmenge entstehen können.
- E: Kosten für die Bereitstellung von Lagerfläche.
- F: Kosten für die Bearbeitung des Bestellvorgangs.



### Aufgabe 3 – Lagerhaltungskosten

**Wählen Sie alle richtigen Aussagen aus.**

Was versteht man unter Lagerhaltungskosten?

- A: Kosten für die Lagerung von Waren.
- B: Kosten für gebundenes Kapital im Lagerbestand.
- C: Kosten, die ausschließlich beim Auslösen einer Bestellung entstehen.
- D: Kosten für Lagerflächen und Lagerbetrieb.
- E: Kosten, die durch die Aufbewahrung von Waren entstehen können.
- F: Kosten für die Berechnung der optimalen Bestellmenge.



### Aufgabe 4 – Optimale Bestellmenge

**Wählen Sie eine richtige Antwort aus.**

Was beschreibt die optimale Bestellmenge?

- A: Die größtmögliche Menge, die ein Lager aufnehmen kann.
- B: Die Menge, die immer unabhängig vom Bedarf bestellt wird.
- C: Die Bestellmenge, bei der im vereinfachten Modell die Summe aus Bestell- und Lagerhaltungskosten möglichst gering ist.
- D: Die Menge, die täglich verbraucht wird.
- E: Die Menge, die mindestens als Sicherheitsbestand vorhanden sein muss.
- F: Die Menge, die ein Lieferant grundsätzlich liefern kann.



### Aufgabe 5 – Sicherheitsbestand

**Wählen Sie eine richtige Antwort aus.**

Welche Bedeutung hat der Sicherheitsbestand?

- A: Er gibt die Menge an, die bei jeder Bestellung zusätzlich bestellt werden muss.
- B: Er dient als Reserve, um Unsicherheiten oder Verzögerungen abzufangen.
- C: Er bezeichnet die gesamte Jahresbedarfsmenge.
- D: Er entspricht immer der optimalen Bestellmenge.
- E: Er gibt die maximale Lagerkapazität an.
- F: Er bezeichnet die Menge, die bereits beim Lieferanten bestellt wurde.



### Aufgabe 6 – Lieferzeit

**Wählen Sie eine richtige Antwort aus.**

Was bedeutet Lieferzeit im Beschaffungsprozess?

- A: Der Zeitraum zwischen zwei Lagerinventuren.
- B: Der Zeitraum zwischen dem Verbrauch zweier Artikel.
- C: Der Zeitraum zwischen dem Auslösen einer Bestellung und dem Eintreffen der Ware.
- D: Der Zeitraum, in dem eine Ware im Lager bleibt.
- E: Der Zeitraum für die Berechnung der Lagerhaltungskosten.
- F: Der Zeitraum zwischen zwei Geschäftsjahren.



### Aufgabe 7 – Meldebestand

**Wählen Sie eine richtige Antwort aus.**

Was bezeichnet der Meldebestand?

- A: Den Bestand, bei dem eine Bestellung ausgelöst werden soll.
- B: Den Bestand, der am Jahresende übrig bleibt.
- C: Die Menge, die bei jeder Bestellung geliefert wird.
- D: Den durchschnittlichen Lagerbestand.
- E: Die maximale Lagermenge.
- F: Die Menge, die ein Lieferant auf Vorrat hält.



### Aufgabe 8 – Bestellpunktverfahren

**Wählen Sie eine richtige Antwort aus.**

Was kennzeichnet das Bestellpunktverfahren?

- A: Es wird ausschließlich einmal im Monat bestellt.
- B: Der Lagerbestand wird laufend überwacht und bei Erreichen des Meldebestands wird bestellt.
- C: Die Bestellung erfolgt immer am gleichen Wochentag.
- D: Die Bestellmenge wird grundsätzlich täglich verändert.
- E: Die Ware wird grundsätzlich ohne Lagerung geliefert.
- F: Der Lagerbestand wird nur am Jahresende überprüft.



### Aufgabe 9 – Bestellrhythmusverfahren

**Wählen Sie eine richtige Antwort aus.**

Was kennzeichnet das Bestellrhythmusverfahren?

- A: Eine Bestellung wird ausschließlich bei Erreichen des Meldebestands ausgelöst.
- B: Der Lagerbestand wird überhaupt nicht überprüft.
- C: Die Bestellung erfolgt in festgelegten Zeitabständen; die Bestellmenge kann variieren.
- D: Die Lieferzeit bestimmt allein den Bestellzeitpunkt.
- E: Es wird immer die gleiche Menge bestellt.
- F: Die Ware wird grundsätzlich direkt an den Kunden geliefert.



### Aufgabe 10 – Just-in-time

**Wählen Sie eine richtige Antwort aus.**

Was bedeutet Just-in-time?

- A: Waren werden möglichst frühzeitig und in großen Mengen eingelagert.
- B: Waren werden möglichst bedarfsgerecht und zeitnah zum benötigten Zeitpunkt geliefert.
- C: Waren werden ausschließlich einmal jährlich bestellt.
- D: Waren werden ohne vorherige Bedarfsplanung beschafft.
- E: Waren werden grundsätzlich erst nach dem Verkauf bestellt.
- F: Waren werden unabhängig vom tatsächlichen Bedarf geliefert.



### Aufgabe 11 – Durchschnittlicher Lagerbestand

**Wählen Sie eine richtige Antwort aus.**

Was beschreibt der durchschnittliche Lagerbestand im vereinfachten Modell ohne Sicherheitsbestand?

- A: Die gesamte Menge aller Bestellungen eines Jahres.
- B: Die Hälfte der Bestellmenge.
- C: Die Menge, die während der Lieferzeit verbraucht wird.
- D: Die größte Menge, die im Lager vorhanden ist.
- E: Die Menge, die am Jahresende vorhanden ist.
- F: Die Menge, die bei jeder Bestellung zusätzlich geliefert wird.



### Aufgabe 12 – Zielbestand

**Wählen Sie eine richtige Antwort aus.**

Was beschreibt der Zielbestand im vereinfachten Bestellrhythmusverfahren?

- A: Die Menge, die im Lager mindestens immer vorhanden sein muss.
- B: Die Menge, die ein Lieferant maximal liefern darf.
- C: Den angestrebten Lagerbestand, auf den bei einer Überprüfung aufgefüllt werden soll.
- D: Die Menge, die im vergangenen Jahr verbraucht wurde.
- E: Die Menge, die bei einer Bestellung grundsätzlich nicht überschritten werden darf.
- F: Den durchschnittlichen Verbrauch pro Tag.