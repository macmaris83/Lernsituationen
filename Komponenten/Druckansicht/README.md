# A4-Gesamtdokument

Die Komponente gestaltet ausschließlich `druckansicht.html`. Die bestehenden
Kapitel aus `D.printOrder`, lokale Editoränderungen, fachliche Bilder, SVGs,
Dokumentoberflächen und der ausgewählte Lernweg bleiben erhalten. Der dekorative
Campus- und Glashintergrund entfällt bereits in der Bildschirmvorschau.

`print.css` wird als `assets/print-layout.css` hinter allen anderen Stylesheets
eingebunden. `print.js` wird als `assets/print-layout.js` am Ende von `body` nach
Runtime und `lg01.js` geladen. Installation:

```sh
python tools/install_print_layout.py Pfad/zum/Master
```

Der bestehende Druckbutton verwendet nach der Integration:

```js
document.querySelectorAll('[data-print]').forEach(button => {
  button.addEventListener('click', () => window.SOZ_PRINT.print());
});
```

Einen vorhandenen `window.print()`-Klickhandler dabei ersetzen, damit nicht ein
zweiter Druckdialog zu früh startet. Der Installer aktualisiert die entsprechenden
Runtime-Bindungen und ergänzt Drucker- und Zahnrad-Symbole. Lernsituationsdaten,
Konfigurationen und Fortschrittskennungen bleiben unverändert.

`SOZ_PRINT.prepare()` öffnet sämtliche Inhaltsdetails nach der Wiederherstellung,
gibt verzögert gezeigene Materialien frei, erhält die Lernwegfilter und erzeugt
unbegrenzte Druckdarstellungen für Textfelder und Auswahllisten. Die Originale
bleiben im DOM erhalten. Der Druck schreibt keine Lernstände; das Öffnen der
Druckdetails überschreibt keine gespeicherten Akkordeonpräferenzen.

`await SOZ_PRINT.ready()` wartet auf Schriften, Bilddekodierung und zwei
Layoutzyklen. Danach steht `body.dataset.printReady` auf `true`.
`await SOZ_PRINT.print()` wartet ebenfalls und öffnet danach den Browserdruck.
`beforeprint` bereitet auch den Druck über das Browsermenü erneut vor.

Das Papierformat ist A4 hochkant mit 14 mm oben, 12 mm seitlich und 15 mm unten.
Karten und Dokumentleisten behalten ihre Farben, Originalbilder werden weder
beschnitten noch durch neue Motive ersetzt. Tabellen umbrechen Text und erhalten
wiederholte Kopfzeilen; lange Inhalte sind nicht scrollbegrenzt. Das native
Druckmenü, Druckerauswahl und PDF-Speichern gehören zum jeweiligen Browser bzw.
iPadOS. Eine Prüfung mit Browser-PDF ersetzt keinen physischen iPad-Drucktest.
