# BFS dual · PDF-Export

`python tools/bfs_pdf_export/build.py` erstellt die Druckansicht, die A4-Arbeitsblätter und die Gesamtdokumente aus den HTML-Mastern für Global Bike in LF 1 bis 3 und dem Board-Paket für LS 6.9. Der Generator benötigt Python mit lxml, Playwright und PyMuPDF sowie Chromium. Bei Bedarf gibt `BFS_CHROMIUM` den Pfad zum Browser an.

In `pdf-document.css` steht das gemeinsame Drucklayout. Die PDFs unter `pdf/` sind die Laufzeitdateien und werden über das jeweilige SCORM-Manifest mit ausgeliefert. Nach Änderungen an den Fachinhalten oder am Layout die PDFs neu erstellen, die Version der betroffenen Pakete erhöhen und mit `tools/master.py` exportieren. Für LS 6.9 erneuert das Skript das eigenständige Board-ZIP direkt.

`python tools/bfs_pdf_export/check.py` prüft die Export-Schaltflächen, alle Lernweg-PDFs und den A4-Druck der einzelnen Seiten in Chromium.
