# Data Exploration

Ad-hoc exploration of the market data (price ticks, schemas, gaps, value
ranges) before it is built into the ingestion and streaming code.

Notebooks and scripts here are throwaway analysis, not production code.
Never commit API keys or raw data dumps; read credentials from environment
variables.

## Scripts

Run from the repo root. Numbering gives the order they were built in. All
folders produce the same plots from the same data:

- `v1_basic/`: first version, CI colors and font only.
- `v2_polished/`: title and subtitle at the left edge instead of axis titles,
  German month names and number format, a labeled dot on the last value,
  legend as one row above the plot, a card behind the chart.
- `v3_dark/`: same as v2, permanently in the CI default mode (`meta.default_mode`
  in the JSON, currently dark). Plain file names, no switch needed.

| Script (in every folder) | Output |
|---|---|
| `01_plot_price_eur.py` | `01_price_eur.png`: MSFT price in EUR, year to date |
| `02_plot_price_earnings.py` | `02_price_earnings.png`: same price with quarterly EPS surprise markers |
| `03_plot_cashflow.py` | `03_cashflow.png`: operating cash flow, capex, free cash flow per quarter (USD) |
| `04_plot_candles.py` | `04_candles.png`: MSFT daily candles of the last 60 trading days with SMA 20/50 and a volume panel |

Example: `python data_exploration/v3_dark/01_plot_price_eur.py`

Dark mode in v2: `CI_MODE=dark python data_exploration/v2_polished/01_plot_price_eur.py`
writes `01_price_eur_dark.png` next to the light version.

Each folder has its own `ci.py` (`use_ci()` and, from v2 on, the layout helpers);
the values come from `style/felix-schramm-ci.json`.

Requirements: `pip install yfinance matplotlib`

## Additional dark-mode comparisons

| Script | Output | Content |
|---|---|---|
| `v3_dark/05_plot_indexed.py` | `v3_dark/05_indexed.png` | ORCL, MSFT, MCD adjusted closes over one year, indexed to 100 at their first common close |

Run from the repository root, e.g.
`python data_exploration/v3_dark/05_plot_indexed.py`. The comparison uses a
common trading calendar and stops if any requested price series is missing.

Charts comparing three or more stocks use only stocks from the owner's
actual portfolio. The shared approved selection is in `v3_dark/stocks.py`:
Oracle (`ORCL`, slot 1), Microsoft (`MSFT`, slot 2), McDonald's (`MCD`, slot 3).
All three trade in USD. The indexed chart and HTML preview use this selection
and keep each stock's color fixed. The upcoming monthly-return, drawdown and
KPI-tile scripts must reuse it as well.
Check the private portfolio source before adding or replacing a symbol;
watchlist entries and synthetic demo positions are not holdings. Do not
commit spreadsheet identifiers, quantities, weights or cost bases.
