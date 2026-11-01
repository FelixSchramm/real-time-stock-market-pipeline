"""Plot the price development of stocks from Yahoo Finance on a time axis.

Prices are indexed to 100 at the start of the period so that stocks with
different price levels (e.g. AAPL vs. MSFT) share one y-axis.

Usage::

    python data_exploration/plot_prices.py AAPL MSFT --period 1y
"""

import argparse

import matplotlib.pyplot as plt
import yfinance as yf

# Categorical colors in fixed order (blue, orange), light-surface variants.
COLORS = ["#2a78d6", "#eb6834"]


def load_indexed_close(symbols, period):
    """Download daily closing prices and index them to 100 at the first day.

    :param symbols: ticker symbols, e.g. ``["AAPL", "MSFT"]``
    :param period: yfinance period string, e.g. ``"1y"``
    :return: DataFrame with one column per symbol, starting at 100
    """
    close = yf.download(symbols, period=period, interval="1d", progress=False)["Close"]
    return close / close.iloc[0] * 100


def plot(indexed, period, path):
    """Draw one line per symbol with end labels and save the figure.

    :param indexed: DataFrame from :func:`load_indexed_close`
    :param period: period string, used in the title
    :param path: output PNG path
    :return: None
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    for color, symbol in zip(COLORS, indexed.columns):
        ax.plot(indexed.index, indexed[symbol], color=color, linewidth=2, label=symbol)
        ax.annotate(
            f"{symbol} {indexed[symbol].iloc[-1]:.0f}",
            (indexed.index[-1], indexed[symbol].iloc[-1]),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
        )
    ax.axhline(100, color="gray", linewidth=1, alpha=0.5)
    ax.set_title(f"Kursentwicklung, Basis 100 ({period})")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Schlusskurs, Start = 100")
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main():
    """Parse arguments, download the data and save the plot.

    :return: None
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("symbols", nargs="*", default=["AAPL", "MSFT"])
    parser.add_argument("--period", default="1y")
    parser.add_argument("--out", default="data_exploration/prices.png")
    args = parser.parse_args()
    plot(load_indexed_close(args.symbols, args.period), args.period, args.out)


if __name__ == "__main__":
    main()
