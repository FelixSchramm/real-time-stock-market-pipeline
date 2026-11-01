"""Plot the year-to-date MSFT price in euro with quarterly earnings (dark).

Same plot as ``v2_polished/02_plot_price_earnings.py``: one marker per reported
quarter, triangle up if the reported EPS beat the estimate, triangle down if
it missed. The price series is reused from ``01_plot_price_eur.py``.

Usage::

    python data_exploration/v3_dark/02_plot_price_earnings.py
"""

import importlib

import pandas as pd
import yfinance as yf
from ci import (
    COLORS,
    FINANCE,
    NEUTRAL,
    end_label,
    german,
    legend_row,
    month_axis,
    new_figure,
    save,
)
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
    """Draw the price line with one labeled earnings marker per quarter.

    :param price_eur: Series from ``load_msft_eur``
    :param earnings: DataFrame from :func:`load_earnings`
    :param path: output PNG path
    :return: None
    """
    fig, ax = new_figure(
        "Microsoft (MSFT) und Quartalszahlen",
        "Tagesschlusskurs in EUR seit Jahresbeginn, "
        "Marker: Gewinn je Aktie (EPS) gegenüber der Analystenerwartung",
        legend_row=True,
    )
    ax.plot(price_eur.index, price_eur, color=COLOR)
    for date, row in earnings.iterrows():
        beat = row["Surprise(%)"] >= 0
        y = price_eur.asof(date)
        ax.scatter(
            date,
            y,
            marker="^" if beat else "v",
            color=BEAT if beat else MISS,
            s=110,
            zorder=3,
            edgecolors=NEUTRAL["surface"],
            linewidths=1.5,
        )
        sign = "+" if beat else "−"
        ax.annotate(
            f"EPS {sign}{german(abs(row['Surprise(%)']), 1)} %",
            (date, y),
            xytext=(0, 16 if beat else -22),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            # A surface-colored box keeps the label readable where it meets the line.
            bbox={"boxstyle": "round,pad=0.25", "fc": NEUTRAL["surface"], "ec": "none"},
        )
    end_label(
        ax,
        price_eur.index[-1],
        price_eur.iloc[-1],
        f"{german(price_eur.iloc[-1], 2)} €",
        COLOR,
    )
    # Proxy handles: the legend lists both outcomes even if one never occurred.
    legend_row(
        fig,
        [
            Line2D([], [], color=COLOR, linewidth=2, label="MSFT in EUR"),
            Line2D(
                [], [], color=BEAT, marker="^", linestyle="", label="über Erwartung"
            ),
            Line2D(
                [], [], color=MISS, marker="v", linestyle="", label="unter Erwartung"
            ),
        ],
    )
    month_axis(ax)
    save(fig, path)


if __name__ == "__main__":
    price = load_msft_eur()
    plot(
        price,
        load_earnings(price.index[0]),
        "data_exploration/v3_dark/02_price_earnings.png",
    )
