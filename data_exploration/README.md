# Data Exploration

Ad-hoc exploration of the market data (price ticks, schemas, gaps, value
ranges) before it is built into the ingestion and streaming code.

Notebooks and scripts here are throwaway analysis, not production code.
Never commit API keys or raw data dumps; read credentials from environment
variables.

## Scripts

Run from the repo root. Numbering gives the order they were built in. Both
folders produce the same three plots from the same data:

- `v1_basic/`: first version, CI colors and font only.
- `v2_polished/`: title and subtitle at the left edge instead of axis titles,
  German month names and number format, a labeled dot on the last value,
  legend as one row above the plot, a card behind the chart.

| Script (in both folders) | Output |
|---|---|
| `01_plot_price_eur.py` | `01_price_eur.png`: MSFT price in EUR, year to date |
| `02_plot_price_earnings.py` | `02_price_earnings.png`: same price with quarterly EPS surprise markers |
| `03_plot_cashflow.py` | `03_cashflow.png`: operating cash flow, capex, free cash flow per quarter (USD) |

Example: `python data_exploration/v2_polished/01_plot_price_eur.py`

Each folder has its own `ci.py` (`use_ci()` and, in v2, the layout helpers);
the values come from `style/felix-schramm-ci.json`.

Requirements: `pip install yfinance matplotlib`
