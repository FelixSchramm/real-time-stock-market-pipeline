"""Shared, owner-approved stock selection for multi-stock comparisons.

Use this selection for indexed prices, monthly returns, drawdown and KPI
tiles. Additional symbols require checking the owner's current holdings;
demo data and watchlists do not establish portfolio membership.

Only market symbols and their stable CI colors belong here. Keep the private
source, quantities, cost bases and account information outside the repository.
"""

import yfinance as yf
from ci import COLORS

TICKERS = ("ORCL", "MSFT", "MCD")
TICKER_COLORS = dict(zip(TICKERS, COLORS[: len(TICKERS)], strict=True))


def load_prices(period="1y"):
    """Download adjusted closes for every approved stock, without threading.

    :param period: Yahoo lookback period
    :return: daily prices in the approved order, retaining missing observations
    """
    close = yf.download(
        TICKERS, period=period, auto_adjust=True, progress=False, threads=False
    )["Close"].reindex(columns=TICKERS)
    if close.empty or close.isna().all().any():
        raise ValueError("Mindestens eine Kursreihe fehlt.")
    return close
