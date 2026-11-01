# Glossary: Microsoft data exploration plots and yfinance functions

Overview of all plots of the MSFT data exploration (`data_exploration/`) and
the `yfinance` functions each plot uses. The epic is #8; open plots link to
their issue. The `Quality` column is empty on purpose and is filled in during
review.

`t = yf.Ticker("MSFT")`. All data comes from `yfinance`, no API key needed.

## Plots

| Plot | Script and output | Content | Status | yfinance functions | Quality |
|---|---|---|---|---|---|
| 01 | `01_plot_price_eur.py`, `01_price_eur.png` | MSFT closing price in EUR, year to date | done | `yf.download(["MSFT", "EURUSD=X"], period="ytd", interval="1d")` | |
| 02 | `02_plot_price_earnings.py`, `02_price_earnings.png` | Price in EUR with quarterly EPS surprise markers | done | `t.get_earnings_dates(limit=12)`, price from plot 01 | |
| 03 | `03_plot_cashflow.py`, `03_cashflow.png` | Quarterly operating cash flow, capex, free cash flow (USD, fiscal quarters) | done | `t.quarterly_cashflow` | |
| 04 | `04_plot_cashflow_annual.py` | Annual cash flow by fiscal year | open, #9 | `t.cashflow` | |
| 05 | `05_plot_income.py` | Quarterly revenue, net income, margins | open, #10 | `t.quarterly_income_stmt` | |
| 06 | `06_plot_earnings_reaction.py` | EPS surprise vs price change on the next trading day | open, #11 | `t.get_earnings_dates(limit=25)`, `t.history(...)` | |
| 07 | `07_plot_pe_ratio.py` | P/E ratio over time | open, #12 | `t.get_earnings_dates(limit=25)`, `t.history(...)` | |
| 08 | `08_plot_benchmark.py` | MSFT vs S&P 500 and Nasdaq-100, plus drawdown | open, #13 | `yf.download(["MSFT", "^GSPC", "^NDX"], ...)` | |
| 09 | `09_plot_dividends.py` | Dividend per share and dividend yield | open, #14 | `t.dividends`, `t.history(...)` | |
| 10 | `10_plot_analysts.py` | Analyst price targets and recommendations | open, #15 | `t.analyst_price_targets`, `t.recommendations` | |
| 11 | `11_plot_price_targets.py` | Price target development over time | open, #16 | `t.upgrades_downgrades` | |
| 12 | `12_plot_insiders.py` | Insider transactions on the price line | open, #17 | `t.insider_transactions` | |
| 13 | `13_plot_holders.py` | Largest institutional holders (optional) | open, #18 | `t.institutional_holders`, `t.major_holders` | |
| 14 | `14_plot_implied_vol.py` | Implied volatility by strike (optional) | open, #19 | `t.options`, `t.option_chain(expiry)` | |

## Functions

| Function | Returns | Used in plots |
|---|---|---|
| `yf.download(tickers, period, interval)` | Price history of one or more tickers as a DataFrame (`Close` etc.); `EURUSD=X` is the USD per EUR exchange rate | 01, 02, 08 |
| `t.history(period, interval)` | Daily OHLCV price history of one ticker | 06, 07, 09 |
| `t.get_earnings_dates(limit)` | Report dates (after US market close) with `EPS Estimate`, `Reported EPS`, `Surprise(%)`; `limit` sets how many quarters | 02, 06, 07 |
| `t.quarterly_cashflow` | Cash flow statement per quarter, rows e.g. `Operating Cash Flow`, `Capital Expenditure`, `Free Cash Flow`; about 5 quarters | 03 |
| `t.cashflow` | Same rows per fiscal year (ends 30 June); about 4 years | 04 |
| `t.quarterly_income_stmt` | Income statement per quarter (revenue, net income, operating income) | 05 |
| `t.dividends` | Series of dividends per share by ex-dividend date | 09 |
| `t.analyst_price_targets` | Dict with `current`, `low`, `high`, `mean`, `median` (snapshot) | 10 |
| `t.recommendations` | Count of Strong Buy to Strong Sell ratings per month (snapshot) | 10 |
| `t.upgrades_downgrades` | Analyst actions with firm, grade change and price target change | 11 |
| `t.insider_transactions` | Insider sales, purchases and gifts with shares, value and date | 12 |
| `t.institutional_holders` | Ten largest institutional holders with share and change (snapshot) | 13 |
| `t.major_holders` | Overall share held by insiders and institutions (snapshot) | 13 |
| `t.options`, `t.option_chain(expiry)` | Option expiry dates; calls and puts per expiry with strike and implied volatility | 14 |

Functions for plots 04 to 14 are taken from the issues and from a test call of
the datasets; column names marked "check first" in the issues are not yet
verified.
