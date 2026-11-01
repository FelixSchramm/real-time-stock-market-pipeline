"""Plot Microsoft's largest reported institutional holders (#18).

This is a filing snapshot, not live ownership. The filing date range and
retrieval date are explicit; holding changes refer to the previous report.
"""

import pandas as pd
import yfinance as yf
from matplotlib.ticker import FuncFormatter
from msft_data import figure, percent
from v3_dark.ci import COLORS, NEUTRAL, save


def plot(holders, major, path):
    """Draw ten sorted institutional holdings and their reported changes.

    :param holders: table including Holder, pctHeld, pctChange, Date Reported
    :param major: Yahoo major-holder table indexed by Breakdown
    :param path: output PNG path
    :return: None
    """
    data = holders.dropna(subset=["Holder", "pctHeld"]).nlargest(10, "pctHeld")
    if data.empty:
        raise ValueError("Keine gemeldeten institutionellen Beteiligungen verfügbar.")
    dates = pd.to_datetime(data["Date Reported"])
    total = major.loc["institutionsPercentHeld", "Value"]
    fig, ax = figure(
        "Microsoft (MSFT): Größte institutionelle Anteilseigner",
        f"Meldungen {dates.min():%d.%m.%Y}–{dates.max():%d.%m.%Y} · Institutionen insgesamt {percent(total * 100)}",
    )
    fig.subplots_adjust(left=0.30, right=0.78, bottom=0.16)
    values = data["pctHeld"] * 100
    ax.barh(range(len(data)), values, color=COLORS[1], height=0.63)
    ax.set_yticks(range(len(data)), data["Holder"], fontsize=9)
    ax.invert_yaxis()
    ax.grid(False, axis="y")
    ax.grid(True, axis="x")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v)))
    for i, (_, row) in enumerate(data.iterrows()):
        change = row["pctChange"]
        suffix = (
            "k. A."
            if pd.isna(change)
            else f"{'+' if change >= 0 else '−'}{percent(abs(change) * 100)}"
        )
        ax.annotate(
            f"{percent(row['pctHeld'] * 100)}   ({suffix})",
            (row["pctHeld"] * 100, i),
            xytext=(7, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
        )
    fig.text(
        0.04,
        0.06,
        f"Abruf {pd.Timestamp.now():%d.%m.%Y} · Klammern: Bestandsänderung zum Vorbericht · Meldungen können Monate zurückliegen",
        fontsize=9,
        color=NEUTRAL["ink_secondary"],
    )
    save(fig, path)


if __name__ == "__main__":
    stock = yf.Ticker("MSFT")
    plot(
        stock.institutional_holders,
        stock.major_holders,
        "data_exploration/13_holders.png",
    )
