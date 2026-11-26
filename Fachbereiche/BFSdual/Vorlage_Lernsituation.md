# BFSdual · LF [Nummer] · LS [Nummer] · [Titel der Lernsituation]

**Bildungsgang:** BFS dual  
**Profil und Halbjahr:** [eintragen]  
**Lernfeld:** [Nummer und vollständige Bezeichnung]  
**Lernsituation:** [Nummer und handlungsorientierter Titel]  
**Zeit:** [Anzahl] UStd.  
**Unterrichtlicher Bezug:** [Kompetenz oder Inhaltsbezug aus der Planung]  
**Formgrundlage:** [Gemeinsamer Formmaster 1.8.8](../../Formmaster/README.md)  
**SCORM-Referenz für Aufbau und Kompetenznetz:** `BRC_LG01_LS04_v1.8.15_SCORM12.zip`

Diese Vorlage gilt für **alle Lernfelder der BFSdual**. Nutzt die acht Stationen und den Fachbegriffscheck. Füllt die Platzhalter für den aktuellen Fall aus. Jede LS enthält ihre eigenen Aufgaben und Materialien. Auch ein neues Team kann sie von Anfang bis Ende bearbeiten. Wenn vorherige Entscheidungen für den Fall wichtig sind, legt sie als Material bei.

## Aufgabenzeiten und Gong

Verteilt die Zeit vor dem Export auf die einzelnen Aufgaben. Gebt auch dem Einstieg, jeder Lesefrage, dem Fachbegriffscheck, der Wahl, dem Peer-Feedback, dem Pitch und der letzten Moodle-Aufgabe eine Zeit. Große Produkte lassen sich in Arbeitsstücke mit eigenem Ergebnis teilen. Zählt bei A, B und C nur den gewählten Arbeitsweg. Gebt allen drei Wegen gleich viel Zeit. Die Summe der Minuten muss der geplanten Zahl an Unterrichtsstunden entsprechen. Eine Unterrichtsstunde umfasst hier 45 Minuten.

Im Markdown steht direkt am jeweiligen Auftrag eine maschinenlesbare Zeitmarke. Ersetzt die Werte in diesem Muster. Der sichtbare Text und der Zahlenwert müssen übereinstimmen. Jede Kennung ist innerhalb der LS eindeutig und bleibt bei späteren Bearbeitungen erhalten.

```html
<span class="assignment-time" data-task-id="BFSDUAL-LF06-LS01-T01" data-task-minutes="29">29 Minuten</span>
```

In den sechs Aufgabenphasen wandern `data-task-id` und `data-task-minutes` auf die zugehörige `.assignment-frame`. Die sichtbare Zeit bleibt als `.assignment-time` am Auftrag. Die sechs Aufgabenphasen nutzen den Aufgabenfokus des gemeinsamen Formmasters. Die Zeit startet beim Öffnen der Aufgabe. Pause und Tonschalter bleiben bedienbar. Bei null bleiben die Arbeit und das manuelle Weiter möglich. Für Orientierung, Handlungssituation samt Lesefragen und die eigenständige Checkseite liegt [der BFSdual-Zusatztimer](assets/zusatzzeiten.js) bereit. Kopiert diese Datei samt Manifest-Eintrag nach `assets/zusatzzeiten.js` und bindet sie dort mit `<script defer src="assets/zusatzzeiten.js"></script>` ein. Auf diesen drei Seiten bleiben die Attribute am Span. Hier startet jede Person die gewünschte Uhr selbst. Der Fachcheck erhält seine Zeitmarke auf der Checkseite. Ein Quiz mit zehn zusammengehörigen Karten verwendet einen Timer für den ganzen Check. Beim Wechsel von Informieren zum Quiz läuft nur dieser eine Timer. Die freie Wahl zwischen drei Paketen startet keinen zusätzlichen Countdown.

## Orientierung

### Warum wir das lernen

[Schreibt zwei bis vier kurze Sätze an die Lernenden. Beginnt mit einem Erlebnis aus ihrem Alltag oder Praktikum. Greift einen Ort, einen Gegenstand oder eine Frage aus dem Fall auf. Zeigt am Schluss, was die Lernenden im Fall tun und wofür ihnen das hilft.]

### Kompetenzprofil und Kompetenznetz

**Vorrangige Fachkompetenz · [1–6] von 6**

Ich kann [eine konkrete Aufgabe lösen]. Ich zeige das, indem ich [sichtbares Ergebnis oder fachlichen Beleg nennen].

[Wenn die LS mehrere eigenständige fachliche Schwerpunkte hat, nennt sie hier einzeln als konkrete Ich-Formulierungen.]

Die Zahlen von **1 bis 6** zeigen, wie stark ihr die jeweilige Kompetenz in dieser LS übt. Die Werte gelten für alle drei Lernpakete. [Legt die Werte anhand der Aufgaben und des Handlungsprodukts fest.]

| Wert | Wie stark wird die Kompetenz angesteuert? |
| ---: | --- |
| 1 | Ihr braucht sie kurz in einer Aufgabe. |
| 2 | Ihr übt sie in einem Teil einer Aufgabe. |
| 3 | Ihr nutzt sie an mehreren Stellen. |
| 4 | Ihr übt sie gezielt in mehreren Phasen. |
| 5 | Ihr braucht sie für euer Handlungsprodukt oder für die Prüfung des Ergebnisses. |
| 6 | Ihr übt sie von der Vorbereitung bis zur Auswertung. |

| Kompetenz | Wie stark? (1–6) | Das übe ich in dieser LS | Woran merkt ihr das? |
| --- | ---: | --- | --- |
| Personalkompetenz | [1–6] | Ich [plane, prüfe oder begründe mein Vorgehen]. | [Beobachtbare Handlung] |
| Sozialkompetenz | [1–6] | Ich [stimme mich ab, höre zu oder nutze Rückmeldungen]. | [Beobachtbare Handlung] |
| Methodenkompetenz | [1–6] | Ich [erschließe, vergleiche oder strukturiere Informationen]. | [Beobachtbare Handlung] |
| Medienkompetenz | [1–6] | Ich [nutze oder gestalte Medien passend zur Aufgabe]. | [Beobachtbare Handlung] |

## Handlungssituation

[Erzählt eine kurze Szene aus dem Betrieb. Wer ist dabei? Was wollen die Beteiligten jeweils und wo entsteht das Problem? Bei Global Bike nutzt ihr nach Möglichkeit Namen und Aufgaben aus dem Organigramm. Macht deutlich, was die Lernenden entscheiden sollen und wer das Ergebnis braucht. Legt die nötigen Unterlagen bei.]

### Kurz prüfen · Handlungssituation

Stellt nach der Szene **drei bis sechs Fragen zum Text**. Der Text enthält alle Antworten. Gebt zu jeder Frage eine aufklappbare Hilfe. Sie kann auf einen Absatz zeigen oder einen Satzanfang anbieten. Die Lernenden schreiben die Antwort selbst. Passt die Fragen an den Fall an.

**1. Wer kommt im Fall vor? Welche Aufgabe hat diese Person?**

<details>
<summary>Hilfe</summary>

Lest den ersten Absatz. Sucht den Namen und die Aufgabe der Person.

</details>

**2. Was wollen die Beteiligten? Wo liegt das Problem?**

<details>
<summary>Hilfe</summary>

Lest, was die Personen sagen. Beginnt mit „[Name] möchte … Für [Name] ist wichtig, dass … Das Problem ist …“.

</details>

**3. Welche Vorgabe muss das Team beachten?**

<details>
<summary>Hilfe</summary>

Sucht nach einer Uhrzeit, einem Datum, einem Maß oder einer Anweisung. Schreibt auf, woran sich das Team halten muss.

</details>

**4. Was soll das Team entscheiden oder vorbereiten?**

<details>
<summary>Hilfe</summary>

Lest am Ende der Szene nach, was die Person vom Team braucht. Beginnt mit „Das Team soll …, damit …“.

</details>

## Informieren

**Sucht** in [M-Nummer und Titel] die Angaben zu [fachliche Frage]. **Notiert** [Angaben und Belege, die ihr später braucht].

**Fachbuchverweis.** [Später ergänzen]

## Fachbegriffscheck

Der eigene Check folgt **nach Informieren und vor Planen**. Er umfasst je LS **mindestens 10 und höchstens 20 unterschiedliche Fachbegriffe** und ist für alle drei Lernpakete gleich. Die Lernenden ordnen jedem Begriff die zutreffende Erklärung zu. Die Rückmeldung erklärt den Begriff am aktuellen Fall. Offene Begriffe können anschließend gezielt nachgearbeitet werden.

**Fachbuchverweis.** [Später ergänzen]

| Karten-ID | Fachbegriff | Zutreffende Erklärung | Falsche Erklärung 1 | Falsche Erklärung 2 | Rückmeldung mit Fall- und Materialbezug |
| --- | --- | --- | --- | --- | --- |
| `[LS-ID]-B01` | [Begriff] | [Kurze, fachlich genaue Erklärung] | [Naheliegende Verwechslung] | [Plausible zweite Verwechslung] | [Beispiel und M-Nummer] |

Füllt eine Zeile pro Fachbegriff aus. Wählt Begriffe, die für das Verständnis oder die Bearbeitung der LS gebraucht werden. Stellt die Erklärungen bei **Informieren** im Begriffsblatt und zum Nachschlagen im LS-Glossar bereit. Zeigt die drei Antwortmöglichkeiten im Check gemischt und die Rückmeldung nach der Antwort an. Die Spalte „Zutreffende Erklärung“ dient in der Markdown-Quelle als Lösungsschlüssel. Plant den Check in das Zeitbudget der LS ein.

## Planen

**Skizziert** eure Ideen. Haltet mit Stichworten oder einer Zeichnung fest, wie ihr vorgehen könnt. **Notiert**, welche Vorgaben ihr beachten müsst und woran ihr eine passende Lösung erkennt.

**Fachbuchverweis.** [Später ergänzen]

## Entscheiden

### Lernpaket wählen

**Wählt** einen der drei Arbeitswege. Überlegt, welcher Weg euch bei der Entscheidung am besten hilft. **Haltet** beim Arbeiten ein Zwischenergebnis und einen Beleg für den Pitch fest. Ein Beleg kann zum Beispiel eine Zahl, ein Maß oder eine Kundenstimme sein.

**Gemeinsames Fachziel und Handlungsprodukt.** [Benennt die konkrete vorrangige Fachkompetenz der LS. Sagt, welche Entscheidung die Lernenden treffen oder prüfen, welche Belege sie dabei sichern und welches gemeinsame Handlungsprodukt entsteht. Für alle drei Pakete gelten dieselben Aufgabenanforderungen, Fallvorgaben und Bewertungskriterien.]

| Lernpaket | Lernzugänge | So arbeitet ihr | Euer Zwischenergebnis | Wählt dieses Paket, wenn … |
| --- | --- | --- | --- | --- |
| **A · [Tätigkeit benennen]** | [Zum Beispiel lesen, skizzieren und vergleichen] | [Nennt den Plan, die Grafik oder die Übersicht. Beschreibt, was die Lernenden darin markieren, vergleichen oder entwerfen.] | [Nennt die konkrete Skizze, Zuordnung oder Beobachtung, die ins gemeinsame Ergebnis eingeht.] | [Erklärt, welchen Unterschied oder Zusammenhang ihr mit diesem Zugang leichter erkennen könnt.] |
| **B · [Tätigkeit benennen]** | [Zum Beispiel zuhören, nachfragen und aushandeln] | [Nennt die Aufnahme oder den Vorlesetext. Beschreibt, was die Lernenden beim Zuhören, Nachfragen oder im Gespräch herausarbeiten und wie sie Angaben absichern.] | [Nennt die konkrete Aussage, Vereinbarung oder Begründung, die die Lernenden schriftlich für das gemeinsame Ergebnis festhalten.] | [Erklärt, welches Interesse, welche Unklarheit oder welche Begründung im Gespräch deutlicher wird.] |
| **C · [Tätigkeit benennen]** | [Zum Beispiel legen, umbauen und praktisch erproben] | [Nennt die Karten, Gegenstände oder Modelle. Beschreibt, was die Lernenden legen, umbauen oder erproben.] | [Nennt die konkrete Beobachtung oder erprobte Lösung, die die Lernenden für das gemeinsame Ergebnis sichern.] | [Erklärt, welche Anordnung oder Handlungsfolge ihr durch Ausprobieren leichter überprüfen könnt.] |

[Verwendet in jeder LS dieselbe Reihenfolge und dieselben Spalten. Paket A nutzt vor allem Darstellungen und Vergleiche, Paket B Zuhören und Austausch, Paket C praktisches Erproben. Benennt die Pakete nach der konkreten Tätigkeit. Nennt unter „Lernzugänge“, was die Lernenden auf diesem Weg tatsächlich tun. Gemeinsame Tätigkeiten wie das Lesen von Belegen, das schriftliche Begründen oder das Rechnen stehen beim gemeinsamen Auftrag, wenn sie für alle Wege erforderlich sind. Stellt für jedes Paket die Materialien bereit und plant die Bearbeitung in derselben Unterrichtszeit.]

**Fachbuchverweis.** [Später ergänzen]

### Fachliche Entscheidung

**Entscheidet** euch für eine Lösung oder einen Arbeitsweg. **Begründet** eure Wahl mit [konkreten Belegen aus den Materialien].

**Fachbuchverweis.** [Später ergänzen]

## Durchführen

**Erstellt** [gemeinsames Handlungsprodukt] für [Person oder Betrieb]. Nutzt euer Lernpaket. **Haltet** eure Entscheidung in [Dokumentationsform] fest.

**Fachbuchverweis.** [Später ergänzen]

## Bewerten

**Prüft** euer [Handlungsprodukt] mit den Fragen unter der Aufgabe. **Verbessert** eine Stelle, wenn das nötig ist.

**Fachbuchverweis.** [Später ergänzen]

**Bewertet** eine andere Arbeit in Moodle unter [Peer-Feedback]({{MOODLE_PEER_FEEDBACK_URL}}).

1. **Ladet euer Handlungsprodukt hoch.** Bei Teamarbeit reicht jede Person eine Kopie im eigenen Konto ein. Wählt einen Titel und einen Dateinamen ohne eure Namen. Entfernt eure Namen aus der Arbeit und aus den Dateieigenschaften.
2. **Schaut euch die zugeteilte Arbeit an.** Moodle lost aus, welche Arbeit ihr bekommt. Ihr seht die Arbeit ohne Namen.
3. **Gebt Rückmeldung.** Nutzt [fachliche Prüffragen]. Nennt eine Stelle, die gut gelungen ist. Schreibt, was die Person verbessern kann. Die Person sieht bei eurer Antwort euren Klarnamen.
4. **Lest** die empfangene Rückmeldung nach der Freigabe. Verbessert eine Stelle oder erklärt, warum ihr bei eurer Lösung bleibt.

**Fachbuchverweis.** [Später ergänzen]

## Reflektieren

**Notiert** einzeln, welcher Beleg euch bei der Entscheidung am meisten geholfen hat. **Erklärt**, was ihr beim nächsten Mal genauso oder anders machen würdet. Schätzt euer eigenes Können zur Fachkompetenz auf der Skala von 1 bis 4 ein. Zeigt eine passende Stelle in eurem Produkt. 1 bedeutet „mit Hilfe bei jedem Schritt“, 2 „mit einzelnen Tipps“, 3 „selbstständig lösen und begründen“ und 4 „auch in einem neuen Fall“.

**Fachbuchverweis.** [Später ergänzen]

**Abschlusspitch.**

**Pitcht** euer Lernpaket. Ein Pitch ist eine kurze Vorstellung. Nutzt euer Handlungsprodukt und eure Unterlagen. Ihr habt für den Kurzpitch etwa zwei Minuten. Wenn noch Zeit ist, beantwortet eine Rückfrage.

1. **Ergebnis zeigen.** Zeigt euer Handlungsprodukt. Sagt, was ihr entschieden habt.
2. **Entscheidung belegen.** Zeigt einen Beleg aus dem Fall. Erklärt, wie er eure Entscheidung stützt.
3. **Arbeitsweg begründen.** Sagt, warum ihr euer Lernpaket gewählt habt. Zeigt ein Zwischenergebnis. Erklärt, wie es euch bei der Entscheidung geholfen hat.

**Das könnt ihr zeigen.** [Nennt eine Stelle im gemeinsamen Handlungsprodukt und einen Fallbeleg, die Lernende aus jedem der drei Pakete im Pitch zeigen können.]

<details>
<summary>Sprachhilfe für den Pitch</summary>

- „Unser Ergebnis ist … Wir schlagen vor, dass …“
- „Unser Beleg ist … Er zeigt, dass …“
- „Wir haben Paket … gewählt. Beim Arbeiten hat uns … geholfen.“

</details>

**Fachbuchverweis.** [Später ergänzen]

**Füllt** zum Schluss [Feedback]({{MOODLE_FEEDBACK_URL}}) in Moodle aus.

**Fachbuchverweis.** [Später ergänzen]

## Handlungsprodukt und Kriterien

**Produkt:** [konkretes Ergebnis, Umfang und Adressat]  
**Fachliche Nachweise:** [beobachtbare Bestandteile, Belege und Begründung]  
**Kriterien:** [Qualitätsmaßstäbe, anhand derer alle drei Paketvarianten geprüft werden]

## Materialien

**M1 bis Mxx** sind Platzhalter für die Belege und Materialien der jeweiligen LS. Wählt Anzahl, Reihenfolge und Materialarten nach dem Fall. Geeignet sind zum Beispiel E-Mails, Geschäftsbelege, Produktdatenblätter, Pläne, Fotos, Audios oder Arbeitshilfen. Fügt die Unterlagen ein oder verlinkt sie aus dem Materialordner. Ein Vorlesetext ist ein nutzbares Hörangebot zu zweit. Versprecht eine Audiodatei nur, wenn sie mitgeliefert wird. Nennt in jedem Arbeitsauftrag die M-Nummer, die dort gebraucht wird.

| Kennung | Titel und Materialart | Inhalt, Datei oder Link |
| --- | --- | --- |
| **M1** | [Titel und Art des Belegs oder Materials] | [Inhalt einfügen oder Datei verlinken] |
| **M2** | [Titel und Art des Belegs oder Materials] | [Inhalt einfügen oder Datei verlinken] |
| **… bis Mxx** | [Weitere Belege und Materialien nach Bedarf] | [Inhalt einfügen oder Datei verlinken] |

## Redaktionshinweise für das Vorlagenset

- **Lernbedeutsamkeit.** Prüft, ob das Alltagsbeispiel und der Fall dieselbe konkrete Frage aufwerfen. Der Einstieg nennt den Fall oder einen seiner Schauplätze und führt in den fachlichen Auftrag. In LF 06 steht die Kundschaft zum Beispiel vor zwei Pumpen und braucht eine verständliche Angabe zum Ventil. Auf der Aktionsfläche entscheiden die Lernenden, wo die Kundschaft diese Angabe findet.
- **LS-Glossar.** Erstellt für jede LS eine eigene [Nachschlageseite](Vorlage_LS_Glossar.md). Prüft alle Begriffe aus dem Fachbegriffscheck und verlinkt sie im Material, wo sie im Fall sinnvoll gebraucht werden. Verlinkt dort auch weitere Begriffe, deren Erklärung bei der Bearbeitung hilft. Die Zahl der Links richtet sich nach dem Material. Setzt den Link direkt an den Fachbegriff im Satz oder in der Tabelle. In einer eigenständigen MD verlinkt M2 z. B. `[Absatzmenge](#absatzmenge)` auf den Glossareintrag derselben Datei. Erklärt die Begriffe in einfacher Sprache und ergänzt je ein kurzes Beispiel aus dem Fall. Das Begriffsblatt für die Vorbereitung auf den Fachbegriffscheck bleibt bei „Informieren“ verfügbar.
- **Gemeinsamer Einstieg.** Orientierung, Handlungssituation, Informieren und Planen verwenden gemeinsame Fachaufträge und Fallunterlagen. Die Lernpaketwahl erscheint zu Beginn von **Entscheiden**. Die fachliche Entscheidung folgt auf Basis des gewählten Zugangs.
- **Gleichwertige Zugänge.** A, B und C haben dieselbe Fachkompetenz, dieselbe fachliche Datengrundlage, dasselbe Handlungsprodukt, dieselben Bewertungskriterien und denselben Zeitrahmen. Die Pakete verändern die Arbeitsweise. Alle erhalten Zugriff auf genaue Zahlen, Maße und fachliche Belege. Sprachfassungen und Modelle enthalten die Informationen, die zur Bearbeitung tatsächlich nötig sind.
- **Regionale Betriebe.** Wenn ihr reale Betriebe verwendet, verlinkt deren Websites und übernehmt passende belegbare Angaben zum Standort oder Angebot. Kennzeichnet die erfundene Zusammenarbeit, Fallbelege, Flächen und Geschäftsdaten als Unterrichtsfall.
- **Abschlusspitch.** Legt für A, B und C dieselben Anforderungen fest. Plant den Kurzpitch in der vorgesehenen Unterrichtszeit ein. Findet ein gemeinsamer Pitch am Ende des Lernfelds statt, kann jede abgeschlossene LS dafür gewählt und mit ihrem Handlungsprodukt, einem Zwischenergebnis und einem Fallbeleg vorgestellt werden. Das Material der gewählten LS reicht für den Pitch aus. Eine Folienpräsentation ist freiwillig.
- **Eigenständiger Fall.** Jede Lernsituation enthält eine vollständige Ausgangslage, eigene erreichbare Materialien, eine fachliche Entscheidung und ein abschließendes Handlungsprodukt. Ergebnisse innerhalb der LS werden weiterverwendet. Der Start einer anderen LS erfolgt mit den dort bereitgestellten Fallunterlagen.
- **Sprache.** Schreibt in direkter Ansprache und in kurzen Sätzen. Nennt pro Satz möglichst eine Handlung. Nutzt Fachbegriffe dort, wo sie fachlich gebraucht werden. Erklärt sie beim ersten Auftreten oder verlinkt das Glossar. Bietet zusätzliche Sprachhilfen zum Aufklappen an, etwa Wörter, Suchhinweise und Satzanfänge. Die Hilfen erleichtern das Lesen und Formulieren. Fachziele und Bewertungskriterien gelten für alle Lernenden.
- **Aufträge.** Beginnt mit einem klaren Arbeitsverb in Fettdruck. Nennt die M-Nummer und das erwartete Ergebnis direkt im Auftrag. Teilt längere Aufträge in kurze Schritte. Setzt den Fachbuchplatzhalter unter die Aufgabe.
- **Kompetenznetz im SCORM-Paket.** Verwendet den Wert aus dem Block „Vorrangige Fachkompetenz“ für die erste Achse. Die vier weiteren Achsen folgen der Tabellenreihenfolge. Beschriftet die sechs Skalenringe von **1 innen bis 6 außen** und zeigt die fünf Werte auch als Text. Übertragt die fünf Werte je LS in `competencies[].weight`. Die separate Selbsteinschätzung in Reflektieren folgt der SCORM-Skala **1–4** vom Arbeiten mit enger Hilfe bis zur selbstständigen, begründeten Anwendung im Transfer und kann mit einem Arbeitsbeleg ergänzt werden.
- **Fachbegriffscheck im SCORM-Paket.** Verlinkt nach Informieren **„Begriffe prüfen“** auf `begriffstraining.html`. Übernehmt je LS alle 10 bis 20 Karten mit stabiler ID, Definition, Antwortalternativen und Rückmeldung. Prüft die Kartenzahl vor dem Export und hinterlegt den Check in der Navigation, den Fortschrittsdaten und dem Paketmanifest. Die Auswertung öffnet den Weg zu Planen und zeigt gezielte Nacharbeit zu unsicheren Begriffen an. Der Kurzcheck zur Handlungssituation bleibt ein eigener Schritt.
- **LS-Glossar im SCORM-Paket.** Nehmt die eigene Seite `ls-glossar.html` in das Paketmanifest auf und blendet sie aus Phasenübersicht und Materialmenü aus. Übertragt die Links an den Fachbegriffen in die jeweiligen Materialseiten und verwendet die passende Sprungmarke, etwa `ls-glossar.html#absatzmenge`. Der Link steht bereit, sobald das betreffende Material zugänglich ist. Beim Öffnen zeigt die Seite den ausgewählten Begriff. **„Zurück zum Material“** führt zur verlinkten Stelle zurück. Die Nutzung ist freiwillig und kann unabhängig vom Fachbegriffscheck erfolgen.
- **Paketansicht bei einer digitalen Umsetzung.** Zeigt in Entscheiden drei gleich gestaltete Wahlkarten mit Zugang, Tätigkeit und Ergebnis. Bis einschließlich Planen funktionieren Navigation, Materialzugriff und Wiederaufnahme bei offener Paketwahl. Für Durchführen ist eine Auswahl erforderlich. Speichert Aufgabenstand, Fachbegriffscheck und Auswahl je LS und prüft die Wiederaufnahme vor und nach der Wahl. Der Abschluss berücksichtigt die gemeinsamen Aufgaben und den gewählten Lernweg.

### Übergabe an den HTML-Export

- Erzeugt pro LS einen eigenen Satz von Seiten. Die acht Stationen reichen von Orientierung bis Reflektieren. Dazu kommen der eigenständige Fachbegriffscheck, die tatsächlich aufgeführten Materialien und das LS-Glossar. Den Produktauftrag mit Kriterien zeigt ihr bei Durchführen und Bewerten. Die Lösungsspalten der Karten und Lehrkräftenschlüssel werden ausschließlich bei der Erzeugung bzw. in der Lehrkräftefassung verwendet. Gebt die freien Leseantworten sinngemäß frei. Eine automatische Prüfung auf exakte Zeichenfolgen wäre für diese Aufgaben ungeeignet.
- Gebt dem Glossar stabile Abschnitts-IDs. Beim Export ersetzt ihr den Markdown-Link im Fachbegriff durch einen HTML-Link mit derselben Sprungmarke. Wenn die Quelle ein Glossar im selben Dokument enthält, nehmt genau den als LS-Glossar ausgezeichneten Abschnitt für die Zusatzseite. Merkt euch die konkrete Textstelle und den Materialnamen für den Rücksprung. Zeigt Wahlmöglichkeiten als lesbare Karten und breite Ausfülltabellen mit klaren Zeilen- und Spaltenüberschriften.
- Setzt unbefüllte Fachbuchfelder als neutralen Text. Fehlt die echte URL einer Moodle-Aktivität, zeigt eine verständliche Information ohne anklickbaren Platzhalter. Die Unterrichtsfassung erhält für beide Aktivitäten je LS ihre eigene Kurs-URL. Aufgabenzeit und Gong werden an der einzelnen Aufgabe geprüft. Ein Lehrkräftenschlüssel erscheint weder im Lernendenmenü noch im öffentlichen Lösungs-HTML eines Lernendenpakets.

## Moodle-Einrichtung für die Lehrkraft

1. Legt je LS eine **Gegenseitige Beurteilung** mit dem Namen **Peer-Feedback** an. Übernehmt die gemeinsamen fachlichen Kriterien der LS in den Bewertungsbogen. Die Einreichenden verwenden neutrale Abgabetitel und Dateinamen sowie Dateien ohne Namen oder identifizierende Dateieigenschaften.
2. Wählt nach der Einreichung **Einreichungen zuordnen → Zufällige Zuordnung**. Plant eine Rückmeldung je Person und je Einreichung ein. Bei einem gemeinsamen Teamprodukt reicht jede Person eine Kopie im eigenen Konto ein. Lost einen Auftrag pro Person aus. Deaktiviert die Selbstbeurteilung und kontrolliert, ob jede Arbeit eine Rückmeldung erhält. Erwischt jemand die Arbeit aus dem eigenen Team, lost ihr unter den übrigen passenden Einreichungen erneut und kontrolliert die Verteilung. Plant die Zuteilung, das Schließen der Aktivität und die Rückgabe in der Bewertungszeit ein. Schließt die Aktivität nach der Auswertung, damit die Einreichenden ihre Rückmeldungen einsehen können. [MoodleDocs zur gegenseitigen Beurteilung](https://docs.moodle.org/401/de/Gegenseitige_Beurteilung_nutzen)
3. Setzt in den **Rechten der Aktivität** für **Teilnehmer/in** die beiden Berechtigungen wie unten angegeben. Prüft mit Teilnehmendenrechten die Ansicht der zugeteilten Einreichung und die Ansicht des empfangenen Peer-Feedbacks. Verwendet in der Aktivität die zugeteilten, anonym dargestellten Arbeiten.
4. Legt für den Abschluss eine Moodle-Aktivität vom Typ **Feedback** an. Ersetzt `{{MOODLE_PEER_FEEDBACK_URL}}` und `{{MOODLE_FEEDBACK_URL}}` durch die tatsächlichen Direktlinks der jeweiligen LS. Der Feedback-Link bildet die **letzte Aufgabe in „Reflektieren“**. [MoodleDocs zur Feedback-Aktivität](https://docs.moodle.org/401/en/Feedback_activity)

| Berechtigung für Teilnehmer/in | Einstellung | Anzeige für Lernende |
| --- | --- | --- |
| `mod/workshop:viewauthornames` | **Verhindern** | Zugewiesene Einreichung ohne Autorennamen. |
| `mod/workshop:viewreviewernames` | **Erlauben** | Klarname der beurteilenden Person beim erhaltenen Peer-Feedback. |

[MoodleDocs zu Autorennamen](https://docs.moodle.org/401/en/Capabilities/mod/workshop:viewauthornames) · [MoodleDocs zu Beurteilernamen](https://docs.moodle.org/401/en/Capabilities/mod/workshop:viewreviewernames)

[Ausgearbeitetes Reihenbeispiel für LF 06](LF06/BFSdual_LF06_Vorlagenset.md) · [Technisches Referenzbeispiel für den Fachbegriffscheck](../Geschichte/IdentitaetUndNation/Lernpaket/begriffstraining.html)
