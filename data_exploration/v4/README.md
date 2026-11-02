# V4 – Unternehmensanalyse und Vorher-/Nachher-Vergleich
Die Ausgangsversion bleibt in `baseline/` als byteidentische Kopie der ursprünglichen 67 Analyse- und Style-Dateien erhalten. Live-Charts verwenden die aktuelle CI-Farbskala.
[Interaktive Vergleichsgalerie](index.html) · [Geschäftsmodell und Quellen](research.md) · [Methodik](METHODS.md)
**Galerie lokal öffnen:** Repository herunterladen/klonen und `data_exploration/v4/index.html` im Browser öffnen. GitHub zeigt HTML als Quelltext; die PNG-Vergleiche unten funktionieren direkt auf GitHub.
Datenabruf: **2026-11-02T10:09:16.887914+00:00**. 29 Diagrammthemen, davon 19 überarbeitet und 10 ergänzt. 44 PNGs einschließlich EUR/USD- und Renditevarianten. Kein Live-Dashboard.
Wertefarbskala: CI **1.3.0** · Rot → Grau → Grün, definiert in `../../style/felix-schramm-ci.json`.
## Reproduzieren

```sh
python -m pip install -r data_exploration/v4/requirements.txt
python data_exploration/v4/generate.py --refresh
python -m unittest discover -s tests -v
```
Ohne `--refresh` wird ein vorhandener lokaler Snapshot wiederverwendet. `.cache/` wird nicht committet. Die Segmenttabelle ist separat aus dem Geschäftsbericht belegt und wird nicht von Yahoo aktualisiert.
## Geschäftsmodell und Ertragskraft

| Thema | Vorher | V4 |
|---|---|---|
| **Geschäftsmodell und Segmente**<br>Neu: Umsatz und operatives Ergebnis aus Microsoft Annual Report 2026, Note 18. | Neu | [![V4](charts/28_segments.png)](charts/28_segments.png) |
| **Wachstum und Margen**<br>Jahres- und Quartalsansicht, Bruttomarge sowie Umsatzwachstum gegenüber Vorjahr. | [![Vorher](baseline/data_exploration/05_income.png)](baseline/data_exploration/05_income.png) | [![V4](charts/10_income.png)](charts/10_income.png) |
| **Cashflow und Investitionen**<br>Cashflow-Gleichung, Capex-Intensität, FCF-Marge und Vorjahresveränderung. | [![Vorher](baseline/data_exploration/04_cashflow_annual.png)](baseline/data_exploration/04_cashflow_annual.png) | [![V4](charts/09_cashflow_annual.png)](charts/09_cashflow_annual.png) |
| **Cashflow-Überleitung**<br>Neu: Wasserfall vom operativen Cashflow über Cash-Capex zum FCF. | Neu | [![V4](charts/29_cash_bridge.png)](charts/29_cash_bridge.png) |
| **Cashflow je Quartal**<br>Quartalswerte plus rollierende Zwölfmonatssumme; keine Überbrückung fehlender Quartale. | [![Vorher](baseline/data_exploration/v3_dark/03_cashflow.png)](baseline/data_exploration/v3_dark/03_cashflow.png) | [![V4](charts/03_cashflow_quarterly.png)](charts/03_cashflow_quarterly.png) |
| **Gewinnqualität**<br>Neu: Gewinn versus Cashflow, Working Capital und aktienbasierte Vergütung. | Neu | [![V4](charts/22_cash_quality.png)](charts/22_cash_quality.png) |
## Kapitalrendite, Management und Bilanz

| Thema | Vorher | V4 |
|---|---|---|
| **Kapitalrendite**<br>Neu: ROIC mit durchschnittlichem Kapital und dokumentierter Steuer-/Goodwill-Behandlung. | Neu | [![V4](charts/21_roic.png)](charts/21_roic.png) |
| **Kapitalverwendung**<br>Neu: Rückkäufe, Dividenden und Akquisitionen gegenüber FCF; Finanzierung separat. | Neu | [![V4](charts/23_capital_allocation.png)](charts/23_capital_allocation.png) |
| **Entwicklung je Aktie**<br>Neu: verwässerte Aktienzahl, Gewinn- versus EPS-Wachstum und FCF je Aktie. | Neu | [![V4](charts/24_per_share.png)](charts/24_per_share.png) |
| **Bilanz und Zinsdeckung**<br>Neu: Liquidität, Schulden, Finanzierungsleasing und Zinsdeckung. | Neu | [![V4](charts/20_balance_sheet.png)](charts/20_balance_sheet.png) |
| **Dividende und Deckung**<br>Dezimalachse repariert; Gewinn- und FCF-Ausschüttungsquote ergänzt. | [![Vorher](baseline/data_exploration/09_dividends.png)](baseline/data_exploration/09_dividends.png) | [![V4](charts/14_dividends.png)](charts/14_dividends.png) |
## Erwartungen und Bewertung

| Thema | Vorher | V4 |
|---|---|---|
| **Schätzungen und Revisionen**<br>Neu: Gewinn-/Umsatzspannen, Analystenzahl und EPS-Revisionen für identische Zielperioden. | Neu | [![V4](charts/25_estimates.png)](charts/25_estimates.png) |
| **Historisches KGV**<br>Gewinnbasis und Look-ahead-Grenzen erklärt; Median ausdrücklich kein fairer Wert. | [![Vorher](baseline/data_exploration/07_pe_ratio.png)](baseline/data_exploration/07_pe_ratio.png) | [![V4](charts/12_pe_ratio.png)](charts/12_pe_ratio.png) |
| **Bewertungsmultiplikatoren**<br>Neu: historische und aktuelle Portal-Bewertungen mit klaren Gewinnbasen. | Neu | [![V4](charts/26_valuation.png)](charts/26_valuation.png) |
| **Reverse DCF**<br>Neu: Welche Cashflow-Wachstumsrate setzt der heutige Preis unter verschiedenen Renditeannahmen voraus? | Neu | [![V4](charts/27_reverse_dcf.png)](charts/27_reverse_dcf.png) |
## Ergänzung: Kurs und Markt

| Thema | Vorher | V4 |
|---|---|---|
| **Kurs und Quartalsergebnisse**<br>EPS über/unter Schätzung statt missverständlichem EPS-Wachstum; Zeitpunkt nach Börsenschluss. | [![Vorher](baseline/data_exploration/v3_dark/02_price_earnings.png)](baseline/data_exploration/v3_dark/02_price_earnings.png) | [![V4](charts/02_price_events.png)](charts/02_price_events.png) |
| **Aktienvergleich**<br>Einheitliche Währung, Renditeart und Start-/Endtage; Verbindungslinien zu Endlabels. | [![Vorher](baseline/data_exploration/v3_dark/05_indexed.png)](baseline/data_exploration/v3_dark/05_indexed.png) | [![V4](charts/05_indexed_EUR_total.png)](charts/05_indexed_EUR_total.png) |
| **Rendite und Kursrisiko**<br>2×2-Anordnung, vergleichbare Zeiträume und Zeit unter dem Hoch; nominalen Aktienkurs entfernt. | [![Vorher](baseline/data_exploration/v3_dark/08_kpi_tiles.png)](baseline/data_exploration/v3_dark/08_kpi_tiles.png) | [![V4](charts/08_kpis_EUR_total.png)](charts/08_kpis_EUR_total.png) |
| **Marktvergleich**<br>Gleicher Zeitraum wie Aktienvergleich; Wahl der Renditeart und zusätzliche Renditedifferenz. | [![Vorher](baseline/data_exploration/08_benchmark.png)](baseline/data_exploration/08_benchmark.png) | [![V4](charts/13_benchmark_EUR_total.png)](charts/13_benchmark_EUR_total.png) |
| **Drawdown**<br>Hoch aus zehnjähriger Vorgeschichte; kein künstlicher Neustart am linken Bildrand. | [![Vorher](baseline/data_exploration/v3_dark/07_drawdown.png)](baseline/data_exploration/v3_dark/07_drawdown.png) | [![V4](charts/07_drawdown_EUR_total.png)](charts/07_drawdown_EUR_total.png) |
| **Monatsrenditen**<br>Sichtbare Farbskala, Währung und Renditedefinition; ausschließlich vollständige Monate. | [![Vorher](baseline/data_exploration/v3_dark/06_monthly_returns.png)](baseline/data_exploration/v3_dark/06_monthly_returns.png) | [![V4](charts/06_monthly_returns_EUR_total.png)](charts/06_monthly_returns_EUR_total.png) |
| **Reaktion auf Quartalszahlen**<br>Marktbereinigte Reaktion neben Aktienrendite; Korrelation als Beschreibung, nicht Prognose. | [![Vorher](baseline/data_exploration/06_earnings_reaction.png)](baseline/data_exploration/06_earnings_reaction.png) | [![V4](charts/11_earnings_reaction.png)](charts/11_earnings_reaction.png) |
| **Kerzen und Volumen**<br>Öffnung/Schluss korrekt erklärt, eigenes Volumenpanel und eindeutiger Zeitraum. | [![Vorher](baseline/data_exploration/v3_dark/04_candles.png)](baseline/data_exploration/v3_dark/04_candles.png) | [![V4](charts/04_candles.png)](charts/04_candles.png) |
## Ergänzung: Analysten, Eigentümer und Optionen

| Thema | Vorher | V4 |
|---|---|---|
| **Analysten-Konsens**<br>Median-Abstand zum Kurs, Zielspanne und Rating-Anteile mit Anzahl. | [![Vorher](baseline/data_exploration/10_analysts.png)](baseline/data_exploration/10_analysts.png) | [![V4](charts/15_analysts.png)](charts/15_analysts.png) |
| **Kurszieländerungen**<br>Letzte zwölf Änderungen als Vorher/Nachher-Paare; vollständige filterbare Meldungstabelle. | [![Vorher](baseline/data_exploration/11_price_targets.png)](baseline/data_exploration/11_price_targets.png) | [![V4](charts/16_price_targets.png)](charts/16_price_targets.png) |
| **Insideraktivität**<br>Monatliche Summen und einzelne Meldungen; unbekannte Werte und Schenkungen bleiben getrennt. | [![Vorher](baseline/data_exploration/12_insiders.png)](baseline/data_exploration/12_insiders.png) | [![V4](charts/17_insiders.png)](charts/17_insiders.png) |
| **Institutionelle Eigentümer**<br>Beteiligungsanteil, relative Bestandsänderung und Meldedatum in getrennten Spalten. | [![Vorher](baseline/data_exploration/13_holders.png)](baseline/data_exploration/13_holders.png) | [![V4](charts/18_holders.png)](charts/18_holders.png) |
| **Optionsvolatilität**<br>Strengere Liquiditätsfilter, Bid/Ask-Prüfung und einzelne Quotes statt suggerierter glatter Kurven. | [![Vorher](baseline/data_exploration/14_implied_vol.png)](baseline/data_exploration/14_implied_vol.png) | [![V4](charts/19_implied_vol.png)](charts/19_implied_vol.png) |

## Weitere Ansichten

[Kurs ohne Ereignisse](charts/01_price_eur.png) · [Originale Galerie](baseline/data_exploration/README.md) · [Originale HTML-Vorschau](baseline/style/ci-preview.html)
