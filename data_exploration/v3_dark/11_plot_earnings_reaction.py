"""Relate EPS surprise to next-session price reaction (#11).

Microsoft reports after market close. Reaction uses the report day's close
and the strictly next trading day's close, never the previous trading day.
"""

import pandas as pd
from ci import FINANCE, NEUTRAL, legend_row, save
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from msft_data import figure, load_close, load_earnings, percent


def reactions(earnings, close):
    """Pair reported EPS surprises with the next-session close return.

    :param earnings: normalized report dates, estimates and reported EPS
    :param close: unadjusted daily USD closes
    :return: complete report observations with surprise and reaction in percent
    """
    rows = []
    for date, event in earnings.iterrows():
        position = close.index.searchsorted(date)
        if position >= len(close) - 1 or close.index[position] != date:
            continue
        estimate = event["EPS Estimate"]
        if pd.isna(estimate) or estimate == 0:
            continue
        rows.append(
            {
                "date": date,
                "surprise": (event["Reported EPS"] / estimate - 1) * 100,
                "reaction": (close.iloc[position + 1] / close.iloc[position] - 1) * 100,
            }
        )
    return (
        pd.DataFrame(rows).set_index("date")
        if rows
        else pd.DataFrame(columns=["surprise", "reaction"])
    )


def plot(data, path):
    """Draw filled gains, hollow losses and the three largest reactions.

    :param data: surprise and reaction observations
    :param path: output PNG path
    :return: None
    """
    if data.empty:
        raise ValueError("Keine vollständigen EPS-/Kursreaktionspaare verfügbar.")
    corr = data["surprise"].corr(data["reaction"])
    fig, ax = figure(
        "Microsoft (MSFT): EPS-Überraschung und Kursreaktion am Folgetag",
        f"{len(data)} Quartale · unbereinigte USD-Kurse · Korrelation {corr:.2f}".replace(
            ".", ","
        ),
        legend_row=True,
    )
    fig.subplots_adjust(right=0.96, bottom=0.15)
    for gain in (True, False):
        subset = data.loc[(data["reaction"] >= 0) == gain]
        color = FINANCE["up" if gain else "down"]
        ax.scatter(
            subset["surprise"],
            subset["reaction"],
            s=85,
            facecolors=color if gain else "none",
            edgecolors=color,
            linewidths=1.7,
        )
    for date in data["reaction"].abs().nlargest(3).index:
        row = data.loc[date]
        ax.annotate(
            f"{date:%m/%Y}",
            (row["surprise"], row["reaction"]),
            xytext=(7, 9),
            textcoords="offset points",
            fontsize=9,
        )
    ax.axhline(0, color=NEUTRAL["axis"], linewidth=1)
    ax.axvline(0, color=NEUTRAL["axis"], linewidth=1)
    ax.set_xlabel("EPS-Überraschung gegenüber Schätzung")
    ax.set_ylabel("Kursänderung am nächsten Handelstag")
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(FuncFormatter(lambda v, _: percent(v)))
    legend_row(
        fig,
        [
            Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                color=FINANCE["up"],
                label="Kurs gestiegen",
            ),
            Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                markerfacecolor="none",
                color=FINANCE["down"],
                label="Kurs gefallen",
            ),
        ],
    )
    save(fig, path)


if __name__ == "__main__":
    earnings = load_earnings()
    plot(
        reactions(earnings, load_close(start=earnings.index.min())),
        "data_exploration/v3_dark/11_earnings_reaction.png",
    )
