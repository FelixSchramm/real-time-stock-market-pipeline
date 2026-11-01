"""Small shared data and formatting helpers for the Microsoft chart epic.

Price/target/EPS charts use unadjusted USD closes. Total-return comparisons
explicitly request adjusted closes instead. Never fill absent fundamentals.
"""

import pandas as pd
import yfinance as yf
from v3_dark.ci import german, new_figure


def figure(title, subtitle, **panels):
    """Create a wider CI card for the Microsoft chart series.

    :param title: German chart title
    :param subtitle: units, period and data limitations
    :param panels: keyword arguments for the shared CI figure
    :return: figure and axes
    """
    fig, axes = new_figure(title, subtitle, **panels)
    fig.set_size_inches(12, 6.6)
    fig.subplots_adjust(left=0.10)
    return fig, axes


def daily_index(data):
    """Normalize market-local dates without shifting them to UTC.

    :param data: Series or DataFrame with a DatetimeIndex
    :return: sorted copy with timezone-naive normalized dates
    """
    data = data.copy()
    data.index = pd.to_datetime(data.index).tz_localize(None).normalize()
    return data.sort_index()


def load_close(period="5y", start=None):
    """Fetch unadjusted daily Microsoft closes in USD.

    :param period: Yahoo lookback period when start is absent
    :param start: optional inclusive start date
    :return: nonempty daily close Series
    """
    options = {"start": start} if start is not None else {"period": period}
    close = daily_index(yf.Ticker("MSFT").history(auto_adjust=False, **options))[
        "Close"
    ].dropna()
    if close.empty:
        raise ValueError("Keine MSFT-Schlusskurse verfügbar.")
    return close


def load_earnings():
    """Fetch unique reported quarterly EPS in report-date order.

    :return: earnings DataFrame, future and duplicate reports removed
    """
    earnings = yf.Ticker("MSFT").get_earnings_dates(limit=25)
    if earnings is None or earnings.empty:
        raise ValueError("Keine gemeldeten EPS verfügbar.")
    earnings = daily_index(earnings.dropna(subset=["Reported EPS"]))
    return earnings.loc[~earnings.index.duplicated(keep="last")]


def statement(data, rows):
    """Select complete reported periods and convert USD to billions.

    :param data: Yahoo statement with line items as rows
    :param rows: required line-item names
    :return: periods as rows, oldest first, in billion USD
    """
    missing = set(rows) - set(data.index)
    if missing:
        raise ValueError(f"Fehlende Positionen: {sorted(missing)}")
    result = data.loc[rows].dropna(axis=1).T.sort_index() / 1e9
    if result.empty:
        raise ValueError("Keine vollständigen Berichtsperioden verfügbar.")
    return result


def fiscal_label(date, annual=False):
    """Label Microsoft's June-ending fiscal year and optional quarter.

    :param date: fiscal period end
    :param annual: omit the quarter if true
    :return: two-line German fiscal label
    """
    year = date.year + (date.month > 6)
    quarter = (date.month - 7) % 12 // 3 + 1
    prefix = "" if annual else f"Q{quarter} "
    return f"{prefix}GJ{year % 100:02d}\n{date:%m/%Y}"


def percent(value, decimals=1):
    """Format percentage points with a real minus sign.

    :param value: percentage points
    :param decimals: number of fractional digits
    :return: German percentage text
    """
    return german(value, decimals).replace("-", "−") + " %"
