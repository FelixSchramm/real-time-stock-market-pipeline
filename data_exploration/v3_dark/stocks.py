"""Shared, owner-approved stock selection for multi-stock comparisons.

Use this selection for indexed prices, monthly returns, drawdown and KPI
tiles. Additional symbols require checking the owner's current holdings;
demo data and watchlists do not establish portfolio membership.

Only market symbols and their stable CI colors belong here. Keep the private
source, quantities, cost bases and account information outside the repository.
"""

import yfinance as yf
from ci import COLORS

TICKERS = ("ORCL", "MSFT", "9988.HK", "SAP.DE")
TICKER_COLORS = dict(zip(TICKERS, COLORS[: len(TICKERS)], strict=True))


def load_history(period="1y"):
    """Load adjusted stock OHLC in USD, retaining each listing's trading days.

    Alibaba uses its Hong Kong ordinary share, SAP its Xetra share. USD/HKD
    quotes HKD per USD, so divide HKD prices; EUR/USD quotes USD per EUR, so
    multiply EUR prices. Only FX gaps are forward-filled, never stock prices.
    Volume stays in shares. Missing stock or FX data stops the comparison.

    :param period: yfinance history period, e.g. ``1y`` or ``13mo``
    :return: mapping from approved symbols to USD OHLC and share volume
    """
    raw = yf.download(
        [*TICKERS, "USDHKD=X", "EURUSD=X"],
        period=period,
        interval="1d",
        auto_adjust=True,
        group_by="ticker",
        progress=False,
        threads=False,
    )
    fx = {}
    for symbol in ("USDHKD=X", "EURUSD=X"):
        rate = raw[symbol]["Close"]
        if rate.dropna().empty or (rate.dropna() <= 0).any():
            raise ValueError("Gültiger FX-Kurs für die USD-Umrechnung fehlt.")
        fx[symbol] = rate.ffill()
    prices = ["Open", "High", "Low", "Close"]
    history = {}
    for ticker in TICKERS:
        frame = raw[ticker][[*prices, "Volume"]].copy()
        if ticker == "9988.HK":
            frame[prices] = frame[prices].div(fx["USDHKD=X"], axis=0)
        elif ticker == "SAP.DE":
            frame[prices] = frame[prices].mul(fx["EURUSD=X"], axis=0)
        frame = frame.dropna(subset=prices)
        if len(frame) < 2 or (frame[prices] <= 0).any().any():
            raise ValueError("Mindestens eine gültige Aktienkursreihe fehlt.")
        history[ticker] = frame
    return history
