# V4 – Prüfung vom 02.11.2026

- Alle 29 Diagrammthemen wurden aus einem gemeinsamen Yahoo-Snapshot
  vom 01.11.2026 neu gerendert: 44 PNGs einschließlich der Vergleichsvarianten.
  `manifest.json` enthält keine Abruf- oder Renderfehler.
- Alle 21 Offline-Tests bestehen, darunter neun V4-Tests: vollständige Monate,
  fehlende Quartale, Hoch vor dem sichtbaren Zeitraum, durchschnittliches
  investiertes Kapital, Reverse-DCF-Rechnung, Optionsfilter, Achsenpräzision,
  Segmentabgleich und unveränderte Originalbilder.
- Black, Ruff und `git diff --check` bestehen für die Änderungen.
- Alle 29 Standardansichten wurden als Bilder geprüft. Endbeschriftungen,
  Zahlenpräzision und die Darstellung auf kleinen Bildschirmen wurden korrigiert.
- Chromium: Desktop mit 1440 × 1000 und Mobilansicht mit 390 × 844 Pixeln.
  Vorher/V4, EUR/USD, Kurs-/Gesamtrendite, Ereignismarker, Gruppennavigation
  und Analystenfilter funktionieren; keine JavaScript-Fehler. Diagramme
  bleiben mobil horizontal scrollbar, ohne die gesamte Seite zu verbreitern.
- Alle 67 Dateien der Ausgangsversion sind byteidentisch gesichert.
  Alle bisherigen Analyse- und Style-Dateien bleiben am ursprünglichen Ort.
- Segmentumsätze und operative Ergebnisse wurden mit Microsoft Annual Report
  2026, Note 18, abgeglichen. Die Summe 2026 beträgt 331.839 Mio. USD Umsatz
  und 155.237 Mio. USD operatives Ergebnis.

Prüfbefehle ab Repository-Wurzel:

```sh
python -m black --check data_exploration/v4/*.py tests/test_v4.py
python -m ruff check data_exploration/v4/*.py tests/test_v4.py
python -m unittest discover -s tests -v
python data_exploration/v4/generate.py
git diff --check
```

Ein frischer Abruf kann andere Zahlen liefern. Die HTML-Galerie nutzt lokale
PNG-Dateien und benötigt zum Betrachten weder Netzwerkzugriff noch API-Schlüssel.
