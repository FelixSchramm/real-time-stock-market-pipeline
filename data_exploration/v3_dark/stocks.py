"""Shared, owner-approved stock selection for multi-stock comparisons.

Use this selection for indexed prices, monthly returns, drawdown and KPI
tiles. Additional symbols require checking the owner's current holdings;
demo data and watchlists do not establish portfolio membership.

Only market symbols and their stable CI colors belong here. Keep the private
source, quantities, cost bases and account information outside the repository.
"""

from ci import COLORS

TICKERS = ("ORCL", "MSFT", "MCD")
TICKER_COLORS = dict(zip(TICKERS, COLORS[: len(TICKERS)], strict=True))
