# V4 – Prüfung vom 02.11.2026

- Alle 29 Diagrammthemen wurden aus dem gemeinsamen Yahoo-Snapshot vom
  02.11.2026, 10:09 UTC neu gerendert: 44 PNGs inklusive Vergleichsvarianten.
  `manifest.json` enthält keine Abruf- oder Renderfehler und nennt CI 1.3.0.
- Die divergierende Wertefarbskala nutzt die Treemap-Anker #B3261E (negativ),
  #5F6368 (null) und #188038 (positiv) aus der zentralen CI JSON.
- Alle vier Monatsrenditevarianten zeigen die Skalenbeschriftung
  −10, −5, −2, 0, +2, +5, +10. Die tatsächlich gerenderten Tick-Texte wurden
  geprüft. Numerische Zellen behalten ebenfalls ihre Vorzeichen.
- Weiße Zellschrift erreicht auf allen neun Farbstufen mindestens 5,02:1
  Kontrast. Auch die interpolierte Reverse-DCF-Skala wurde auf mindestens
  4,5:1 geprüft. Fehlende Werte haben eine eigene Füllfarbe.
- Die zentrale JSON, die eingebettete JSON und die drei CSS-Modi der
  eigenständigen CI-Vorschau stimmen überein. Andere Farbgruppen bleiben gleich.
- Alle 21 Offline-Tests bestehen. Die zwei absichtlich neu gefärbten V3-PNGs
  haben unveränderte Originale in der Baseline; deren SHA-256 ist fest geprüft.
  Alle übrigen ursprünglichen PNGs stimmen weiterhin mit der Baseline überein.
- Alle 67 Dateien unter `baseline/` bleiben unverändert. V3-Monatsrenditen und
  V3-Analysten wurden mit der neuen Wertefarbskala neu erzeugt.
- V3-/V4-Heatmaps wurden visuell geprüft. Die Inline-JavaScript-Syntax der
  CI-Vorschau wurde mit `node --check` geprüft. Black, Ruff und Whitespace-
  Prüfung sind erfolgreich.

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
Die Segmentauswertung bleibt die separat belegte Quelle aus dem Geschäftsbericht.
