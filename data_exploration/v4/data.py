"""Fetch one coherent Yahoo snapshot; cache raw responses locally, never in Git."""

import pickle
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
TICKERS = ("ORCL", "MSFT", "9988.HK", "SAP.DE")
NAMES = {
    "ORCL": "Oracle",
    "MSFT": "Microsoft",
    "9988.HK": "Alibaba HK",
    "SAP.DE": "SAP",
}
SYMBOLS = (*TICKERS, "EURUSD=X", "USDHKD=X", "^GSPC", "^NDX", "SPY", "QQQ")


def dates(frame):
    """Normalize market-local dates without changing their calendar day.

    :param frame: market Series or DataFrame
    :return: sorted copy with naive dates
    """
    frame = frame.copy()
    frame.index = pd.to_datetime(frame.index).tz_localize(None).normalize()
    return frame.sort_index()


def fetch(refresh=False):
    """Fetch required prices and optional business/event resources once.

    :param refresh: replace the local cached snapshot
    :return: dictionary of data, timestamps and resource errors
    """
    cache = ROOT / ".cache" / "snapshot.pkl"
    if cache.exists() and not refresh:
        return pickle.loads(cache.read_bytes())
    now = pd.Timestamp.now(tz="UTC")
    raw = yf.download(
        list(SYMBOLS),
        period="10y",
        auto_adjust=False,
        group_by="ticker",
        threads=False,
        progress=False,
    )
    bundle = {
        "retrieved_at": now.isoformat(),
        "version": yf.__version__,
        "prices": {},
        "errors": {},
    }
    for symbol in SYMBOLS:
        frame = dates(raw[symbol]).dropna(subset=["Close"])
        if frame.empty:
            raise ValueError(f"Required price series missing: {symbol}")
        bundle["prices"][symbol] = frame
    stock = yf.Ticker("MSFT")
    calls = {
        "income": lambda: stock.income_stmt,
        "quarter_income": lambda: stock.quarterly_income_stmt,
        "balance": lambda: stock.balance_sheet,
        "cash": lambda: stock.cashflow,
        "quarter_cash": lambda: stock.quarterly_cashflow,
        "earnings": lambda: stock.get_earnings_dates(limit=48),
        "dividends": lambda: stock.dividends,
        "targets": lambda: stock.analyst_price_targets,
        "recommendations": lambda: stock.recommendations,
        "actions": lambda: stock.upgrades_downgrades,
        "insiders": lambda: stock.insider_transactions,
        "holders": lambda: stock.institutional_holders,
        "major": lambda: stock.major_holders,
        "info": lambda: stock.info,
        "estimates": lambda: stock.earnings_estimate,
        "revenue_estimates": lambda: stock.revenue_estimate,
        "eps_trend": lambda: stock.eps_trend,
        "eps_revisions": lambda: stock.eps_revisions,
        "valuation": lambda: stock.get_valuation_measures(periods=None),
        "filings": lambda: stock.sec_filings,
    }
    for name, function in calls.items():
        print(f"Fetching {name}", flush=True)
        try:
            value = function()
            if value is None or len(value) == 0:
                raise ValueError("Yahoo returned no data")
            bundle[name] = value
        except Exception as exc:  # noqa: BLE001
            bundle["errors"][name] = f"{type(exc).__name__}: {exc}"
    try:
        expiries = list(stock.options)
        available = [
            d
            for d in expiries
            if (pd.Timestamp(d) - now.tz_localize(None).normalize()).days >= 7
        ]
        chains = {}
        for horizon in (7, 30, 90):
            if not available:
                break
            expiry = min(
                available,
                key=lambda d: abs(
                    (pd.Timestamp(d) - now.tz_localize(None)).days - horizon
                ),
            )
            available.remove(expiry)
            chains[expiry] = stock.option_chain(expiry).calls
        bundle["options"] = chains
    except Exception as exc:  # noqa: BLE001
        bundle["errors"]["options"] = f"{type(exc).__name__}: {exc}"
    cache.parent.mkdir(exist_ok=True)
    cache.write_bytes(pickle.dumps(bundle))
    return bundle


def statement(bundle, name, columns):
    """Select statement rows, keeping unavailable items as missing.

    :param bundle: fetched snapshot
    :param name: statement resource name
    :param columns: requested Yahoo line items
    :return: chronological amounts in original USD units
    """
    return bundle[name].reindex(columns).T.sort_index().dropna(how="all")


def prices(bundle, symbols=TICKERS, currency="EUR", total=True):
    """Convert price or adjusted-close series into one display currency.

    FX gaps are filled only from prior observations, for at most seven days.
    Listing calendars stay native. Adjusted closes approximate gross total return.

    :param bundle: fetched snapshot
    :param symbols: requested listings/benchmarks
    :param currency: EUR or USD
    :param total: use adjusted closes if true
    :return: outer-aligned daily prices
    """
    raw = bundle["prices"]
    result = {}
    for symbol in symbols:
        series = raw[symbol]["Adj Close" if total else "Close"].dropna().copy()
        eurusd = raw["EURUSD=X"]["Close"].reindex(
            series.index, method="ffill", tolerance=pd.Timedelta(days=7)
        )
        if symbol == "9988.HK":
            fx = raw["USDHKD=X"]["Close"].reindex(
                series.index, method="ffill", tolerance=pd.Timedelta(days=7)
            )
            series = series / fx
        elif symbol == "SAP.DE":
            series = series * eurusd
        if currency == "EUR":
            series = series / eurusd
        result[symbol] = series
    return pd.concat(result, axis=1)
