"""Plot daily AAPL candles with a volume panel and two moving averages (polished).

Price and volume sit in two stacked panels with a shared x-axis instead of
on two y-axes. Rising days are hollow, falling days filled, so the direction
stays readable without color. The x-axis is the trading-day index, so
weekends and holidays leave no gaps.

Usage::

    python data_exploration/v2_polished/04_plot_candles.py
"""

import numpy as np
import yfinance as yf
from ci import COLORS, FINANCE, MONTHS, NEUTRAL, german, legend_row, new_figure, save
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MaxNLocator

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


def box(face, edge, label):
    """Build a square legend handle, hollow if face and edge differ.

    :param face: fill color
    :param edge: edge color
    :param label: legend text
    :return: Line2D proxy handle
    """
    return Line2D(
        [],
        [],
        marker="s",
        markersize=9,
        linestyle="",
        markerfacecolor=face,
        markeredgecolor=edge,
        label=label,
    )


def plot(ohlc, path):
    """Draw candles and moving averages on top, volume bars below.

    :param ohlc: DataFrame from :func:`load_candles`
    :param path: output PNG path
    :return: None
    """
    fig, (ax, ax_vol) = new_figure(
        "AAPL: Tageskerzen und Volumen",
        f"Letzte {DAYS} Handelstage in USD, "
        "gleitende Durchschnitte über 20 und 50 Tage",
        legend_row=True,
        nrows=2,
        sharex=True,
        gridspec_kw={"height_ratios": [4, 1], "hspace": 0.08},
    )
    # Wider left margin than the default: the volume ticks read "50 Mio.".
    fig.subplots_adjust(left=0.09)
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
        ax.plot(x, ohlc[f"SMA {window}"], color=color, linewidth=1.5)
    ax.spines["bottom"].set_visible(False)

    ax_vol.bar(x, ohlc["Volume"], width=0.7, color=FINANCE["volume"])
    ax_vol.yaxis.set_major_locator(MaxNLocator(2))
    ax_vol.yaxis.set_major_formatter(
        FuncFormatter(lambda v, _: f"{german(v / 1e6)} Mio.")
    )
    months = ohlc.index.month
    starts = np.flatnonzero(np.diff(months)) + 1
    ax_vol.set_xticks(starts, [MONTHS[months[i] - 1] for i in starts])
    ax_vol.set_xlim(-1, len(ohlc))

    legend_row(
        fig,
        [
            box(NEUTRAL["surface"], FINANCE["up"], "steigt"),
            box(FINANCE["down"], FINANCE["down"], "fällt"),
            Line2D([], [], color=SMA_COLORS[20], linewidth=1.5, label="Ø 20 Tage"),
            Line2D([], [], color=SMA_COLORS[50], linewidth=1.5, label="Ø 50 Tage"),
            box(FINANCE["volume"], FINANCE["volume"], "Volumen"),
        ],
    )
    save(fig, path)


if __name__ == "__main__":
    plot(load_candles(), "data_exploration/v2_polished/04_candles.png")
