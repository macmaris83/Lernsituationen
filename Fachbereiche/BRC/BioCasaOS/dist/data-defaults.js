/* Kanonische MD-Ausgangsdaten 2026/27. Erlaubt die sichere Zuordnung älterer Stände. */
globalThis.BioCasaDefaultData={
 "format": "BioCasaDataset",
 "version": 1,
 "label": "BioCasa · LG02 · Einstieg Klasse 11",
 "schoolYear": "2026/27",
 "caseYear": 2026,
 "grade": 11,
 "source": {
  "title": "LG02 Gesamtreihe · Bearbeitungsstand 5. Oktober 2026",
  "reference": "LS01 M2 / LS02 M1–M2",
  "bookEdition": "Bereitgestellte BRC-Lehrbuchausgabe · Stichwortregister",
  "bookSource": "Lehrbuchfundstellen aus der Markdown-Gesamtreihe; Buchtitel und Auflage sind dort nicht belegt."
 },
 "openingBalances": {
  "160": 15000,
  "260": 108110,
  "280": 160390,
  "290": 62000,
  "300": 50000,
  "310": 312500,
  "425": 490000,
  "057": 148000,
  "073": 185000,
  "076": 20000,
  "082": 4000,
  "084": 68000,
  "085": 42000,
  "086": 24000,
  "087": 16000
 },
 "products": [
  {
   "id": "BC-R01",
   "cost": 4,
   "opening": 0,
   "minimum": 400
  },
  {
   "id": "BC-V01",
   "cost": 0.5,
   "opening": 0,
   "minimum": 500
  },
  {
   "id": "BC-R02",
   "cost": 7.5,
   "opening": 0,
   "minimum": 100
  }
 ],
 "demoEntries": [
  {
   "date": "2026-10-02",
   "text": "LS02 G1 · Rohstoffe auf Ziel · ohne Steuer",
   "reference": "G1 / ER-01",
   "lines": [
    [
     "200",
     8000,
     0
    ],
    [
     "440",
     0,
     8000
    ]
   ],
   "movement": {
    "productId": "BC-R01",
    "qty": 2000,
    "kind": "purchase",
    "net": 8000,
    "vat": 0
   },
   "origin": "md"
  },
  {
   "date": "2026-10-03",
   "text": "LS02 G2 · Büromöbel per Bank",
   "reference": "G2 / ER-02 + BA-01",
   "lines": [
    [
     "087",
     1200,
     0
    ],
    [
     "280",
     0,
     1200
    ]
   ],
   "movement": null,
   "origin": "md"
  },
  {
   "date": "2026-10-04",
   "text": "LS02 G3 · Bargeld vom Bankkonto abgehoben",
   "reference": "G3 / BA-02 + KB-01",
   "lines": [
    [
     "288",
     2000,
     0
    ],
    [
     "280",
     0,
     2000
    ]
   ],
   "movement": null,
   "origin": "md"
  },
  {
   "date": "2026-10-05",
   "text": "LS02 G4 · Teilzahlung an Lieferanten",
   "reference": "G4 / BA-03",
   "lines": [
    [
     "440",
     3000,
     0
    ],
    [
     "280",
     0,
     3000
    ]
   ],
   "movement": null,
   "origin": "md"
  },
  {
   "date": "2026-10-06",
   "text": "LS02 G5 · Lieferantenschuld durch Darlehen abgelöst",
   "reference": "G5 / V-01",
   "lines": [
    [
     "440",
     2000,
     0
    ],
    [
     "425",
     0,
     2000
    ]
   ],
   "movement": null,
   "origin": "md"
  },
  {
   "date": "2026-10-07",
   "text": "LS02 G6 · Küche durch zusätzliches Darlehen finanziert",
   "reference": "G6 / ER-03 + D-01",
   "lines": [
    [
     "085",
     4500,
     0
    ],
    [
     "425",
     0,
     4500
    ]
   ],
   "movement": null,
   "origin": "md"
  },
  {
   "date": "2026-10-08",
   "text": "LS02 G7 · freiwillige Sondertilgung im Übungsfenster",
   "reference": "G7 / BA-04",
   "lines": [
    [
     "425",
     5000,
     0
    ],
    [
     "280",
     0,
     5000
    ]
   ],
   "movement": null,
   "origin": "md"
  },
  {
   "date": "2026-10-09",
   "text": "LS02 G8 · Verpackungsvorrat per Bank · ohne Steuer",
   "reference": "G8 / ER-04 + BA-05",
   "lines": [
    [
     "202",
     1000,
     0
    ],
    [
     "280",
     0,
     1000
    ]
   ],
   "movement": {
    "productId": "BC-V01",
    "qty": 2000,
    "kind": "purchase",
    "net": 1000,
    "vat": 0
   },
   "origin": "md"
  },
  {
   "date": "2026-11-10",
   "text": "OS-Übung · Rohstoffentnahme für verkaufte Pizza-Charge",
   "reference": "OS-01",
   "lines": [
    [
     "600",
     4000,
     0
    ],
    [
     "200",
     0,
     4000
    ]
   ],
   "movement": {
    "productId": "BC-R01",
    "qty": -1000,
    "kind": "consumption",
    "net": 0,
    "vat": 0
   },
   "origin": "practice"
  },
  {
   "date": "2026-11-15",
   "text": "OS-Übung · eigene Bio-Pizzen verkauft · 7 % USt",
   "reference": "OS-02",
   "lines": [
    [
     "280",
     26750,
     0
    ],
    [
     "5000",
     0,
     25000
    ],
    [
     "480",
     0,
     1750
    ]
   ],
   "movement": null,
   "origin": "practice"
  },
  {
   "date": "2026-11-18",
   "text": "OS-Übung · Hallenmiete",
   "reference": "OS-03",
   "lines": [
    [
     "670",
     8900,
     0
    ],
    [
     "280",
     0,
     8900
    ]
   ],
   "movement": null,
   "origin": "practice"
  },
  {
   "date": "2026-11-21",
   "text": "OS-Übung · Gehälter, vereinfacht",
   "reference": "OS-04",
   "lines": [
    [
     "630",
     5000,
     0
    ],
    [
     "280",
     0,
     5000
    ]
   ],
   "movement": null,
   "origin": "practice"
  },
  {
   "date": "2026-11-25",
   "text": "OS-Übung · Energiekosten · 19 % Vorsteuer",
   "reference": "OS-05",
   "lines": [
    [
     "605",
     600,
     0
    ],
    [
     "260",
     114,
     0
    ],
    [
     "280",
     0,
     714
    ]
   ],
   "movement": null,
   "origin": "practice"
  },
  {
   "date": "2026-12-30",
   "text": "OS-Übung · lineare Abschreibung Siegeleinheit",
   "reference": "OS-06",
   "lines": [
    [
     "652",
     1000,
     0
    ],
    [
     "076",
     0,
     1000
    ]
   ],
   "movement": null,
   "origin": "practice"
  },
  {
   "date": "2026-12-31",
   "text": "OS-Übung · Zinsaufwand",
   "reference": "OS-07",
   "lines": [
    [
     "751",
     200,
     0
    ],
    [
     "280",
     0,
     200
    ]
   ],
   "movement": null,
   "origin": "practice"
  }
 ],
 "practiceInventory": {
  "flour": {
   "bags": 38,
   "perBag": 25,
   "openBag": 12.5,
   "foreignBags": 2,
   "price": 2,
   "list": 975
  },
  "pizza": {
   "boxes": 7,
   "perBox": 12,
   "singles": 6,
   "price": 3
  },
  "cutoff": {
   "count": 300,
   "incoming": 80,
   "outgoing": 45,
   "price": 2
  },
  "permanent": {
   "count": 480,
   "incoming": 1200,
   "outgoing": 950
  }
 },
 "pizzaSimulation": [
  {
   "id": "P1",
   "name": "Nordlicht Margherita",
   "price": 4.35,
   "cost": 2.2
  },
  {
   "id": "P2",
   "name": "Küstengarten Gemüse",
   "price": 4.35,
   "cost": 2.4
  },
  {
   "id": "P3",
   "name": "Landküche Dinkel-Pilz",
   "price": 4.35,
   "cost": 2.6
  }
 ],
 "receipts": [
  {
   "id": "deposit",
   "min": 4,
   "reference": "OS-BE-01",
   "date": "2026-12-31",
   "kind": "Einzahlungsbeleg",
   "partner": "BioCasa GmbH · Kasse / Geschäftskonto",
   "title": "Bargeld auf das Geschäftskonto eingezahlt",
   "text": "Christian nimmt 200 € aus der Barkasse und zahlt sie auf das Geschäftskonto ein. Kassen- und Banknachweis bestätigen beide Bewegungen.",
   "lines": [
    [
     "Bargeldeinzahlung",
     200
    ]
   ],
   "total": 200,
   "netModel": true,
   "entryText": "Übungsbeleg · Bargeldeinzahlung auf Bank",
   "posting": [
    [
     "280",
     200,
     0
    ],
    [
     "288",
     0,
     200
    ]
   ]
  },
  {
   "id": "furniture",
   "min": 4,
   "reference": "OS-BE-02",
   "date": "2026-12-31",
   "kind": "Kaufbeleg mit Zahlungsnachweis",
   "partner": "KüstenKontor Büroausstattung · fiktiver Lieferant",
   "title": "Büromöbel für BioCasa",
   "text": "Neue Büromöbel werden geliefert und sofort per Bank bezahlt. Sie werden längerfristig im Betrieb genutzt.",
   "lines": [
    [
     "Büromöbel · bestätigter Positionswert",
     1200
    ]
   ],
   "total": 1200,
   "netModel": true,
   "entryText": "Übungsbeleg · Büromöbel per Bank",
   "posting": [
    [
     "087",
     1200,
     0
    ],
    [
     "280",
     0,
     1200
    ]
   ]
  },
  {
   "id": "rent",
   "min": 4,
   "reference": "OS-BE-03",
   "date": "2026-12-31",
   "kind": "Mietabrechnung mit Banknachweis",
   "partner": "Schirumer Gewerbehof · fiktiver Vermieter",
   "title": "Hallenmiete für Dezember",
   "text": "Die Nutzung der Halle betrifft vollständig den laufenden Dezember. BioCasa hat den Betrag per Bank überwiesen.",
   "lines": [
    [
     "Hallenmiete Dezember",
     1000
    ]
   ],
   "total": 1000,
   "netModel": true,
   "entryText": "Übungsbeleg · laufende Hallenmiete",
   "posting": [
    [
     "670",
     1000,
     0
    ],
    [
     "280",
     0,
     1000
    ]
   ]
  },
  {
   "id": "sale",
   "min": 4,
   "reference": "OS-BE-04",
   "date": "2026-12-31",
   "kind": "Ausgangsbeleg · Lieferung auf Ziel",
   "partner": "Frischemarkt Nord · fiktiver Kunde",
   "title": "Eigene Bio-Pizzen geliefert",
   "text": "Die Lieferung eigener Erzeugnisse an den Einzelhändler ist bestätigt. Der Kunde bezahlt später. Dieser Beleg betrachtet nur die Ausgangsrechnung; eine Bestandsentnahme ist separat zu erfassen.",
   "lines": [
    [
     "Eigene Bio-Pizzen · Lieferwert",
     600
    ]
   ],
   "total": 600,
   "netModel": true,
   "entryText": "Übungsbeleg · eigene Erzeugnisse auf Ziel",
   "posting": [
    [
     "240",
     600,
     0
    ],
    [
     "5000",
     0,
     600
    ]
   ]
  },
  {
   "id": "truck",
   "min": 5,
   "reference": "OS-BE-05",
   "date": "2026-12-31",
   "kind": "Eingangsrechnung mit Banknachweis",
   "partner": "KüstenMobil Nutzfahrzeuge · fiktiver Lieferant",
   "title": "Kühltransporter gekauft und bezahlt",
   "text": "BioCasa übernimmt einen Kühltransporter. Die Rechnung wurde vollständig über die Bank beglichen. Die ausgewiesene Vorsteuer ist im Übungsfall vollständig abzugsfähig.",
   "lines": [
    [
     "Kühltransporter · netto",
     40000
    ],
    [
     "Umsatzsteuer laut Eingangsrechnung · 19 %",
     7600
    ]
   ],
   "total": 47600,
   "entryText": "Übungsbeleg · Kühltransporter mit Vorsteuer",
   "posting": [
    [
     "084",
     40000,
     0
    ],
    [
     "260",
     7600,
     0
    ],
    [
     "280",
     0,
     47600
    ]
   ]
  },
  {
   "id": "energy",
   "min": 5,
   "reference": "OS-BE-06",
   "date": "2026-12-31",
   "kind": "Eingangsrechnung mit Banknachweis",
   "partner": "Nordstrom Gewerbe · fiktiver Versorger",
   "title": "Energie für die Produktion",
   "text": "Die berechnete Energie wurde im laufenden Monat verbraucht. BioCasa bezahlt die Rechnung per Bank. Die Vorsteuer ist im Übungsfall vollständig abzugsfähig.",
   "lines": [
    [
     "Energieverbrauch · netto",
     600
    ],
    [
     "Umsatzsteuer laut Eingangsrechnung · 19 %",
     114
    ]
   ],
   "total": 714,
   "entryText": "Übungsbeleg · laufender Energieverbrauch",
   "posting": [
    [
     "605",
     600,
     0
    ],
    [
     "260",
     114,
     0
    ],
    [
     "280",
     0,
     714
    ]
   ]
  },
  {
   "id": "office",
   "min": 4,
   "reference": "OS-BE-07",
   "date": "2026-12-31",
   "kind": "Kassenbeleg · Grundlagenmodell",
   "partner": "Bürobedarf Küste · fiktiver Lieferant",
   "title": "Büromaterial für den laufenden Betrieb",
   "text": "Julia kauft fünf Pakete Büropapier für jeweils 17 € und bezahlt bar. Der Verbrauch gehört in die laufende Periode. Im Grundlagenmodell bleibt Umsatzsteuer ausgeblendet.",
   "lines": [
    [
     "5 Pakete × 17 €",
     85
    ]
   ],
   "total": 85,
   "netModel": true,
   "posting": [
    [
     "680",
     85,
     0
    ],
    [
     "288",
     0,
     85
    ]
   ]
  },
  {
   "id": "maintenance",
   "min": 5,
   "reference": "OS-BE-08",
   "date": "2026-12-31",
   "kind": "Eingangsrechnung mit Banknachweis",
   "partner": "Service Küste · fiktiver Wartungsbetrieb",
   "title": "Wartung vorhandener Geräte",
   "text": "Eine vorhandene Anlage wird vier Stunden zu je 125 € netto gewartet. Die Rechnung nennt für diesen Übungsfall 19 % Steuer; der Vorsteuerabzug wird vorausgesetzt. BioCasa überweist sofort.",
   "lines": [
    [
     "4 Stunden × 125 € netto",
     500
    ],
    [
     "19 % Vorsteuer",
     95
    ]
   ],
   "total": 595,
   "posting": [
    [
     "616",
     500,
     0
    ],
    [
     "260",
     95,
     0
    ],
    [
     "280",
     0,
     595
    ]
   ]
  },
  {
   "id": "advertising",
   "min": 5,
   "reference": "OS-BE-09",
   "date": "2026-12-31",
   "kind": "Eingangsrechnung mit Banknachweis",
   "partner": "Küstenwerbung · fiktive Druckerei",
   "title": "Flyer für die Bio-Pizzen",
   "text": "Julia erhält 300 Flyer zu je 0,40 € netto für eine Aktion im laufenden Monat. Im Übungsfall werden 19 % Steuer angesetzt; der Vorsteuerabzug wird vorausgesetzt. BioCasa bezahlt per Bank.",
   "lines": [
    [
     "300 Flyer × 0,40 € netto",
     120
    ],
    [
     "19 % Vorsteuer",
     22.8
    ]
   ],
   "total": 142.8,
   "posting": [
    [
     "687",
     120,
     0
    ],
    [
     "260",
     22.8,
     0
    ],
    [
     "280",
     0,
     142.8
    ]
   ]
  }
 ],
 "bookReferences": {
  "inventory": [
   {
    "topic": "Inventur und Bestandskontrolle",
    "pages": "196–197, 200, 204",
    "prompt": "Unterscheide Aufnahmeart und Organisation. Begründe, welchen Nachweis der konkrete Bestand benötigt."
   }
  ],
  "inventar": [
   {
    "topic": "Inventar, Vermögen und Schulden",
    "pages": "197–199, 233",
    "prompt": "Ordne die aufgenommenen Positionen und erkläre den Weg zum Reinvermögen."
   }
  ],
  "balance": [
   {
    "topic": "Bilanz in Kontenform",
    "pages": "201–203",
    "prompt": "Vergleiche Mittelverwendung links mit Mittelherkunft rechts."
   },
   {
    "topic": "Bilanzveränderungen",
    "pages": "206–208",
    "prompt": "Verfolge die betroffenen Positionen und prüfe die Bilanzsumme."
   }
  ],
  "accounts": [
   {
    "topic": "Aktive und passive Bestandskonten",
    "pages": "211–217",
    "prompt": "Leite Soll und Haben aus Kontoart und Veränderung ab."
   },
   {
    "topic": "Buchungssatz und Kontierung",
    "pages": "221–222, 227",
    "prompt": "Formuliere zuerst Sollkonten, dann „an“ und die Habenkonten."
   }
  ],
  "income": [
   {
    "topic": "Erfolgskonten, Aufwand und Ertrag",
    "pages": "242–245",
    "prompt": "Trenne Leistung, Zahlung und Erfolgswirkung."
   },
   {
    "topic": "GuV und Erfolgsermittlung",
    "pages": "249, 251, 253",
    "prompt": "Erkläre den Weg vom Erfolgskonto über die GuV zum Eigenkapital."
   }
  ],
  "tax": [
   {
    "topic": "Umsatzsteuerprinzip und Vorsteuer",
    "pages": "255–259",
    "prompt": "Verfolge Einkauf und Verkauf entlang der Wertschöpfungskette."
   },
   {
    "topic": "Zahllast und Vorsteuerüberhang",
    "pages": "266–267",
    "prompt": "Unterscheide Steuerschuld und Erstattungsanspruch."
   }
  ],
  "further": [
   {
    "topic": "Abschreibung und Anlagen",
    "pages": "269–280, 283, 285",
    "prompt": "Erkläre, warum Nutzung Aufwand verursacht, ohne eine neue Zahlung auszulösen."
   },
   {
    "topic": "Eigene Erzeugnisse",
    "pages": "292, 294, 297",
    "prompt": "Trenne Produktion, vorhandene Bestände und Verkauf."
   }
  ],
  "returns": [],
  "accrual": [
   {
    "topic": "Aktive und passive Rechnungsabgrenzung",
    "pages": "302–303",
    "prompt": "Vergleiche Zahlungstag, Leistungszeitraum und Jahresgrenze."
   },
   {
    "topic": "Weitere Abgrenzungsarten",
    "pages": "305–307, 312",
    "prompt": "Unterscheide spätere Zahlung von ungewisser Verpflichtung."
   }
  ],
  "stock": [
   {
    "topic": "Bestände eigener Erzeugnisse · Anschluss aus LG02",
    "pages": "292, 294, 297",
    "prompt": "Prüfe den Zusammenhang von Mengen, Bewertung und Bestandsänderung. Lagerkennzahlen werden im 12. Jahrgang vertieft."
   }
  ],
  "control": [
   {
    "topic": "Jahresabschluss und Kennzahlen · Anschluss aus LG02",
    "pages": "322–328, 331, 333–334",
    "prompt": "Prüfe Bezugsgrößen und Grenzen, bevor du eine betriebliche Entscheidung begründest."
   }
  ]
 },
 "assumptions": [
  {
   "origin": "md",
   "title": "Eröffnung und Finanzierung",
   "basis": "LS01 M2 / LS02 M1: Vermögen 852.500 €, Schulden 490.000 €, Eigenkapital 362.500 €. Davon 50.000 € Stammkapital und 312.500 € Kapitalrücklage."
  },
  {
   "origin": "md",
   "title": "Grundlagenfenster G1–G8",
   "basis": "Beträge und Konten aus LS02. Die Zuordnung auf den 2.–9. Oktober ist eine zusätzliche OS-Datierungsannahme."
  },
  {
   "origin": "practice",
   "title": "Rohstoff- und Verpackungsmengen",
   "basis": "G1: 2.000 kg × 4 € = 8.000 €. G8: 2.000 Verpackungssets × 0,50 € = 1.000 €. Die Mengen und Einstandspreise ergänzen die vorgegebenen Buchungswerte. OS-01: 1.000 kg × 4 € = 4.000 € Verbrauch."
  },
  {
   "origin": "practice",
   "title": "Zusätzlicher Umsatz und laufende Kosten",
   "basis": "OS-02: eigener Mischauftrag mit 5.000 Pizzen × 5 € = 25.000 € netto; Übungssteuer 7 % = 1.750 €. OS-03 bis OS-07 sind zusätzliche Modellbelege und bilden kein vollständiges Geschäftsjahr oder den Abschluss aus LS08."
  },
  {
   "origin": "practice",
   "title": "Nachvollziehbare Belegerweiterungen",
   "basis": "OS-BE-07: 5 × 17 € = 85 € Büromaterial. OS-BE-08: 4 × 125 € = 500 € Wartung, 95 € Steuer. OS-BE-09: 300 × 0,40 € = 120 € Werbung, 22,80 € Steuer. Sie werden erst bei eigener Verbuchung Teil des Journals."
  },
  {
   "origin": "practice",
   "title": "Einprodukt-Simulation als freiwillige Vertiefung",
   "basis": "4,35 € Verkaufspreis aus der MD (52.200 € / 12.000 Pizzen). Variable Stückkosten 2,20 / 2,40 / 2,60 € sind offen ausgewiesene Modellannahmen: Zutaten und Verarbeitung 1,70 / 1,90 / 2,10 € plus 0,50 € Verpackung. Keine aus dem Journal abgeleitete vollständige Herstellungskostenrechnung."
  }
 ]
};
