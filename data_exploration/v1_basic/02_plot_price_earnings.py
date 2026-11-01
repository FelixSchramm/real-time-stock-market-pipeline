"""Plot the year-to-date MSFT price in euro with quarterly earnings dates.

Each reported quarter is a marker on the price line: green triangle up if the
reported EPS beat the analyst estimate, red triangle down if it missed. The
label shows the surprise in percent. The price series is reused from
``01_plot_price_eur.py``.

Usage::

    python data_exploration/02_plot_price_earnings.py
"""

import importlib

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from ci import COLORS, FINANCE, NEUTRAL, use_ci
from matplotlib.lines import Line2D

# Module names starting with a digit cannot be used in an import statement.
load_msft_eur = importlib.import_module("01_plot_price_eur").load_msft_eur

COLOR = COLORS[1]
BEAT = FINANCE["up"]
MISS = FINANCE["down"]


def load_earnings(start):
    """Load reported quarterly earnings of MSFT since ``start``.

    :param start: first day to keep (pandas Timestamp, timezone-naive)
    :return: DataFrame indexed by report date with the column ``Surprise(%)``
    """
    earnings = (
        yf.Ticker("MSFT").get_earnings_dates(limit=12).dropna(subset=["Reported EPS"])
    )
    # Reports come after market close with a timezone; match the price index.
    earnings.index = pd.to_datetime(earnings.index.date)
    return earnings[earnings.index >= start]


def plot(price_eur, earnings, path):
    """Draw the price line with one earnings marker per reported quarter.

    :param price_eur: Series from ``load_msft_eur``
    :param earnings: DataFrame from :func:`load_earnings`
    :param path: output PNG path
    :return: None
    """
    use_ci()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(price_eur.index, price_eur, color=COLOR, linewidth=2)
    for date, row in earnings.iterrows():
        beat = row["Surprise(%)"] >= 0
        y = price_eur.asof(date)
        ax.scatter(
            date,
            y,
            marker="^" if beat else "v",
            color=BEAT if beat else MISS,
            s=90,
            zorder=3,
            edgecolors=NEUTRAL["surface"],
        )
        ax.annotate(
            f"EPS {row['Surprise(%)']:+.1f} %",
            (date, y),
            xytext=(0, 14 if beat else -20),
            textcoords="offset points",
            ha="center",
        )
    # Proxy handles: the legend lists both outcomes even if one never occurred.
    handles = [
        Line2D([], [], color=COLOR, linewidth=2, label="MSFT Schlusskurs in EUR"),
        Line2D(
            [], [], color=BEAT, marker="^", linestyle="", label="EPS über Erwartung"
        ),
        Line2D(
            [], [], color=MISS, marker="v", linestyle="", label="EPS unter Erwartung"
        ),
    ]
    ax.legend(handles=handles, frameon=False, loc="upper left")
    ax.set_title("Microsoft (MSFT) in Euro mit Quartalszahlen (EPS-Überraschung)")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Schlusskurs in EUR")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


if __name__ == "__main__":
    price = load_msft_eur()
    plot(price, load_earnings(price.index[0]), "data_exploration/02_price_earnings.png")
