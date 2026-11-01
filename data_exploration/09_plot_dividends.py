"""Plot Microsoft dividend per share and trailing twelve-month yield (#14).

Yield uses actual dividends in (date minus one calendar year, date], divided
by the unadjusted USD close. It is a trailing yield, not a forward estimate.
"""

import pandas as pd
import yfinance as yf
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.ticker import FuncFormatter
from msft_data import daily_index, figure, load_close, percent
from v3_dark.ci import COLORS, end_label, german, save


def dividend_yield(dividends, close):
    """Calculate calendar-year trailing dividend yield, including leap years.

    :param dividends: complete dividend history indexed by ex-dividend date
    :param close: unadjusted daily USD closes
    :return: trailing dividend yield in percent
    """
    cumulative = dividends.groupby(level=0).sum().sort_index().cumsum()
    end = cumulative.reindex(close.index, method="ffill").fillna(0)
    before = cumulative.reindex(
        close.index - pd.DateOffset(years=1), method="ffill"
    ).fillna(0)
    before.index = close.index
    return (end - before).div(close).mul(100)


def plot(dividends, close, path):
    """Draw quarterly payouts above daily trailing dividend yield.

    :param dividends: full historical dividend Series
    :param close: daily USD closes over the displayed five-year period
    :param path: output PNG path
    :return: None
    """
    if dividends.empty:
        raise ValueError("Keine Dividendenhistorie verfügbar.")
    payout = (
        dividends.reindex(dividends.index.union(close.index))
        .sort_index()
        .ffill()
        .reindex(close.index)
    )
    annual_yield = dividend_yield(dividends, close)
    fig, (top, bottom) = figure(
        "Microsoft (MSFT): Dividende je Aktie und Dividendenrendite",
        "Oben: Quartalsdividende in USD am Ex-Tag · unten: Ausschüttungen der letzten 12 Monate / Kurs",
        nrows=2,
        sharex=True,
        gridspec_kw={"height_ratios": [1, 1], "hspace": 0.18},
    )
    top.step(payout.index, payout, where="post", color=COLORS[1])
    top.set_ylabel("USD je Aktie")
    bottom.plot(annual_yield.index, annual_yield, color=COLORS[0])
    bottom.yaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v)))
    bottom.set_ylabel("Rendite (TTM)")
    bottom.xaxis.set_major_locator(YearLocator())
    bottom.xaxis.set_major_formatter(DateFormatter("%Y"))
    end_label(
        top,
        payout.index[-1],
        payout.iloc[-1],
        f"{german(payout.iloc[-1], 2)} USD",
        COLORS[1],
    )
    end_label(
        bottom,
        annual_yield.index[-1],
        annual_yield.iloc[-1],
        percent(annual_yield.iloc[-1], 2),
        COLORS[0],
    )
    save(fig, path)


if __name__ == "__main__":
    plot(
        daily_index(yf.Ticker("MSFT").dividends),
        load_close(),
        "data_exploration/09_dividends.png",
    )
