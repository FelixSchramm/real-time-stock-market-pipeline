"""Compare AAPL, MSFT and NVDA daily closes, indexed to 100.

Usage::

    python data_exploration/v3_dark/05_plot_indexed.py
"""

import yfinance as yf
from ci import (
    COLORS,
    NEUTRAL,
    end_label,
    german,
    legend_row,
    month_axis,
    new_figure,
    save,
)
from matplotlib.lines import Line2D

TICKERS = ["AAPL", "MSFT", "NVDA"]


def load_prices():
    """Download one year of adjusted closes on a common trading calendar.

    :return: complete daily closing prices in the fixed ticker order
    """
    close = yf.download(
        TICKERS,
        period="1y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )["Close"].reindex(columns=TICKERS)
    if close.empty or close.isna().all().any():
        raise ValueError("Mindestens eine Kursreihe fehlt; kein Vergleich möglich.")
    close = close.dropna()
    if len(close) < 2:
        raise ValueError("Zu wenige gemeinsame Handelstage für den Kursvergleich.")
    return close


def plot(close, path):
    """Draw indexed prices with end labels separated by at least 15 points.

    :param close: complete daily closes with at most four ticker columns
    :param path: output PNG path
    :return: None
    """
    if not 1 <= len(close.columns) <= 4:
        raise ValueError("Der Linienvergleich unterstützt höchstens vier Aktien.")
    indexed = close.div(close.iloc[0]).mul(100)
    fig, ax = new_figure(
        "Kursentwicklung, Basis 100",
        f"Tagesschlusskurs indexiert auf den {indexed.index[0]:%d.%m.%Y}",
        legend_row=True,
    )
    handles = []
    for i, ticker in enumerate(indexed):
        ax.plot(indexed.index, indexed[ticker], color=COLORS[i])
        handles.append(Line2D([], [], color=COLORS[i], label=ticker))
    ax.axhline(100, color=NEUTRAL["axis"], linewidth=1)
    month_axis(ax)
    legend_row(fig, handles)
    fig.canvas.draw()
    previous = float("inf")
    gap = 15 * fig.dpi / 72
    for ticker, value in indexed.iloc[-1].sort_values(ascending=False).items():
        actual = ax.transData.transform((0, value))[1]
        position = min(actual, previous - gap)
        end_label(
            ax,
            indexed.index[-1],
            value,
            f"{ticker} {german(value)}",
            COLORS[list(indexed.columns).index(ticker)],
            offset_y=(position - actual) * 72 / fig.dpi,
        )
        previous = position
    save(fig, path)


if __name__ == "__main__":
    plot(load_prices(), "data_exploration/v3_dark/05_indexed.png")
