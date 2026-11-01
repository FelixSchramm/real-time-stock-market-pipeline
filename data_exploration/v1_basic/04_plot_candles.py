"""Plot daily AAPL candles with a volume panel and two moving averages.

Price and volume sit in two stacked panels with a shared x-axis instead of
on two y-axes. Rising days are hollow, falling days filled, so the direction
stays readable without color. The x-axis is the trading-day index, so
weekends and holidays leave no gaps.

Usage::

    python data_exploration/v1_basic/04_plot_candles.py
"""

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from ci import COLORS, FINANCE, NEUTRAL, use_ci
from matplotlib.lines import Line2D

DAYS = 60
SMA_COLORS = {20: COLORS[1], 50: COLORS[6]}


def load_candles():
    """Download one year of daily AAPL candles and keep the last ``DAYS``.

    :return: DataFrame with ``Open``, ``High``, ``Low``, ``Close``, ``Volume``
        and the moving averages ``SMA 20`` and ``SMA 50``
    """
    ohlc = yf.Ticker("AAPL").history(period="1y", interval="1d")
    # Average over the full year before slicing, so both lines start at the left edge.
    for window in SMA_COLORS:
        ohlc[f"SMA {window}"] = ohlc["Close"].rolling(window).mean()
    return ohlc.tail(DAYS)


def plot(ohlc, path):
    """Draw candles and moving averages on top, volume bars below.

    :param ohlc: DataFrame from :func:`load_candles`
    :param path: output PNG path
    :return: None
    """
    use_ci()
    fig, (ax, ax_vol) = plt.subplots(
        2, 1, figsize=(10, 5.6), sharex=True, gridspec_kw={"height_ratios": [4, 1]}
    )
    x = np.arange(len(ohlc))
    up = (ohlc["Close"] >= ohlc["Open"]).to_numpy()
    edge = np.where(up, FINANCE["up"], FINANCE["down"])
    ax.vlines(x, ohlc["Low"], ohlc["High"], color=edge, linewidth=1)
    # Bodies above the wicks, so a hollow body hides the wick inside it.
    ax.bar(
        x,
        ohlc["Close"] - ohlc["Open"],
        bottom=ohlc["Open"],
        width=0.6,
        color=np.where(up, NEUTRAL["surface"], FINANCE["down"]),
        edgecolor=edge,
        linewidth=1,
        zorder=3,
    )
    for window, color in SMA_COLORS.items():
        ax.plot(
            x,
            ohlc[f"SMA {window}"],
            color=color,
            linewidth=1.5,
            label=f"Durchschnitt {window} Tage",
        )
    ax_vol.bar(x, ohlc["Volume"] / 1e6, width=0.7, color=FINANCE["volume"])
    starts = np.flatnonzero(np.diff(ohlc.index.month)) + 1
    ax_vol.set_xticks(starts, ohlc.index[starts].strftime("%m/%Y"))

    # Proxy handles: the candle bodies have no single color for the legend.
    handles = [
        Line2D(
            [],
            [],
            marker="s",
            linestyle="",
            markerfacecolor=NEUTRAL["surface"],
            markeredgecolor=FINANCE["up"],
            label="steigt",
        ),
        Line2D([], [], marker="s", linestyle="", color=FINANCE["down"], label="fällt"),
    ]
    ax.legend(handles=handles + ax.get_legend_handles_labels()[0], loc="upper left")
    ax.set_title(f"AAPL: Tageskerzen und Volumen, letzte {DAYS} Handelstage")
    ax.set_ylabel("Kurs in USD")
    ax_vol.set_ylabel("Volumen in Mio.")
    ax_vol.set_xlabel("Datum")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


if __name__ == "__main__":
    plot(load_candles(), "data_exploration/v1_basic/04_candles.png")
