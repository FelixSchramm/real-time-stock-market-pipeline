# Data Exploration

Ad-hoc exploration of the market data (price ticks, schemas, gaps, value
ranges) before it is built into the ingestion and streaming code.

Notebooks and scripts here are throwaway analysis, not production code.
Never commit API keys or raw data dumps; read credentials from environment
variables.

## Scripts

Run from the repo root. Numbering gives the order they were built in.

| Script | Output |
|---|---|
| `01_plot_price_eur.py` | `01_price_eur.png`: MSFT price in EUR, year to date |
| `02_plot_price_earnings.py` | `02_price_earnings.png`: same price with quarterly EPS surprise markers |
| `03_plot_cashflow.py` | `03_cashflow.png`: operating cash flow, capex, free cash flow per quarter (USD) |

All plots use the personal CI via `ci.py` (`use_ci()`), values in
`style/felix-schramm-ci.json`.

Requirements: `pip install yfinance matplotlib`
