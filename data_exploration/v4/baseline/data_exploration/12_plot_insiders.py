"""Plot reported Microsoft insider transactions over the last year (#17).

Markers use the close on or immediately before the transaction date, not the
execution price. Positive marker areas are proportional to reported USD value;
zero/unknown-value events get a small outlined marker and no implied value.
"""

import pandas as pd
import yfinance as yf
from matplotlib.lines import Line2D
from msft_data import figure, load_close
from v3_dark.ci import COLORS, NEUTRAL, german, legend_row, month_axis, save

KINDS = [
    ("Sale", "v", "Verkauf", COLORS[2]),
    ("Purchase", "^", "Kauf", COLORS[0]),
    ("Other", "o", "Schenkung / sonstige", NEUTRAL["ink_secondary"]),
]


def prepare_transactions(transactions, close):
    """Classify actual transaction text and align event dates to prior closes.

    :param transactions: Yahoo insider transaction table
    :param close: unadjusted daily closes for the last year
    :return: filtered transaction table including marker price and type
    """
    data = transactions.copy()
    data["date"] = (
        pd.to_datetime(data["Start Date"]).dt.tz_localize(None).dt.normalize()
    )
    data = data.loc[data["date"].between(close.index[0], close.index[-1])].copy()
    text = data["Text"].fillna("")
    data["kind"] = "Other"
    for key in ("Sale", "Purchase"):
        data.loc[text.str.startswith(key), "kind"] = key
    data["price"] = [close.asof(date) for date in data["date"]]
    return data


def plot(data, close, path):
    """Draw transactions, their value legend and three large-event labels.

    :param data: dated and classified insider transactions
    :param close: daily USD closes
    :param path: output PNG path
    :return: None
    """
    if data.empty:
        raise ValueError("Keine Insidertransaktionen im Kurszeitraum verfügbar.")
    fig, ax = figure(
        "Microsoft (MSFT): Insider-Transaktionen",
        "USD · Marker am Tagesschlusskurs · Fläche ∝ gemeldetem Wert · Umriss: Wert fehlt / null",
        legend_row=True,
    )
    fig.subplots_adjust(right=0.96)
    ax.plot(close.index, close, color=COLORS[1])
    maximum = data["Value"].max()
    handles = [Line2D([], [], color=COLORS[1], label="MSFT Schlusskurs")]
    for key, marker, label, color in KINDS:
        subset = data.loc[data["kind"] == key]
        positive = subset.loc[subset["Value"] > 0]
        unknown = subset.loc[~(subset["Value"] > 0)]
        ax.scatter(
            positive["date"],
            positive["price"],
            s=positive["Value"] / maximum * 500,
            marker=marker,
            color=color,
            edgecolors=NEUTRAL["surface"],
            linewidth=0.6,
            alpha=0.85,
            zorder=3,
        )
        ax.scatter(
            unknown["date"],
            unknown["price"],
            s=30,
            marker=marker,
            facecolors="none",
            edgecolors=color,
            linewidth=1,
            zorder=3,
        )
        handles.append(
            Line2D([], [], color=color, marker=marker, linestyle="", label=label)
        )
    for i, (_, row) in enumerate(
        data.loc[data["Value"] > 0].nlargest(3, "Value").iterrows()
    ):
        ax.annotate(
            f"{row['Insider']}\n{german(row['Value'] / 1e6, 1)} Mio. USD",
            (row["date"], row["price"]),
            xytext=(0, 28 + 23 * i),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            arrowprops={"arrowstyle": "-", "color": NEUTRAL["ink_muted"]},
            bbox={"facecolor": NEUTRAL["surface"], "edgecolor": "none", "pad": 2},
        )
    ax.margins(y=0.25)
    legend_row(fig, handles)
    month_axis(ax)
    save(fig, path)


if __name__ == "__main__":
    prices = load_close("1y")
    plot(
        prepare_transactions(yf.Ticker("MSFT").insider_transactions, prices),
        prices,
        "data_exploration/12_insiders.png",
    )
