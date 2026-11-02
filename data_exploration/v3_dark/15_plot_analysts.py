"""Plot the current Microsoft analyst target and recommendation snapshot (#15)."""

import pandas as pd
import yfinance as yf
from ci import CI, COLORS, MODE, NEUTRAL, german, save
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from msft_data import figure

RATINGS = ["strongBuy", "buy", "hold", "sell", "strongSell"]
LABELS = ["Stark kaufen", "Kaufen", "Halten", "Verkaufen", "Stark verkaufen"]


def plot(targets, recommendations, path):
    """Draw the target range and monthly recommendation counts side by side.

    :param targets: current, low, high, mean and median target prices in USD
    :param recommendations: recommendation counts by relative month
    :param path: output PNG path
    :return: None
    """
    if any(
        pd.isna(targets.get(key))
        for key in ("current", "low", "high", "mean", "median")
    ):
        raise ValueError("Unvollständige Analystenkursziele.")
    if recommendations.empty:
        raise ValueError("Keine Analystenempfehlungen verfügbar.")
    recommendations = recommendations.copy()
    recommendations["month"] = (
        recommendations["period"].str.removesuffix("m").astype(int)
    )
    recommendations = recommendations.sort_values("month")
    fig, (left, right) = figure(
        "Microsoft (MSFT): Kursziele und Analystenempfehlungen",
        f"Momentaufnahme vom {pd.Timestamp.now():%d.%m.%Y} · USD · Empfehlungen: Anzahl je Monat",
        ncols=2,
        gridspec_kw={"width_ratios": [1, 1.1], "wspace": 0.23},
    )
    fig.subplots_adjust(right=0.96, top=0.73, bottom=0.16)
    left.grid(False)
    left.hlines(
        0.45,
        targets["low"],
        targets["high"],
        color=NEUTRAL["ink_secondary"],
        linewidth=6,
    )
    left.set_ylim(0, 1)
    left.set_yticks([])
    left.axvline(targets["current"], color=COLORS[1], linewidth=1.5)
    for key, y, marker, color in [
        ("median", 0.80, "D", COLORS[0]),
        ("mean", 0.65, "o", COLORS[2]),
    ]:
        value = targets[key]
        left.scatter(value, 0.45, marker=marker, color=color, s=65, zorder=3)
        left.annotate(
            f"{'Median' if key == 'median' else 'Mittelwert'} {german(value, 0)}",
            xy=(value, 0.45),
            xytext=(value, y),
            ha="center",
            fontsize=9,
            arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.8},
        )
    for key in ("low", "high"):
        left.text(targets[key], 0.36, german(targets[key]), ha="center", fontsize=9)
    left.text(
        targets["current"],
        0.12,
        f"Kurs\n{german(targets['current'], 2)}",
        ha="center",
        color=COLORS[1],
        fontsize=10,
    )
    left.set_xlabel("Kursziele in USD")
    left.margins(x=0.16)
    ramp = CI["color"]["diverging"][f"returns_{MODE}"]
    colors = [ramp[i] for i in (8, 6, 4, 2, 0)]
    baseline = pd.Series(0, index=recommendations.index)
    for name, color in zip(RATINGS, colors):
        right.bar(
            range(len(recommendations)),
            recommendations[name],
            bottom=baseline,
            color=color,
            edgecolor=NEUTRAL["surface"],
            linewidth=0.8,
        )
        baseline += recommendations[name]
    right.set_xticks(
        range(len(recommendations)),
        [
            "Aktuell" if m == 0 else f"vor {abs(m)} Mon."
            for m in recommendations["month"]
        ],
    )
    right.set_ylabel("Anzahl Empfehlungen")
    fig.legend(
        handles=[Patch(color=c, label=n) for c, n in zip(colors, LABELS)],
        loc="upper right",
        bbox_to_anchor=(0.965, 0.84),
        ncol=3,
        fontsize=9,
        labelcolor=NEUTRAL["ink_secondary"],
    )
    left.legend(
        handles=[
            Line2D(
                [],
                [],
                color=NEUTRAL["ink_secondary"],
                linewidth=5,
                label="Minimum–Maximum",
            )
        ],
        loc="upper left",
        fontsize=9,
    )
    save(fig, path)


if __name__ == "__main__":
    stock = yf.Ticker("MSFT")
    plot(
        stock.analyst_price_targets,
        stock.recommendations,
        "data_exploration/v3_dark/15_analysts.png",
    )
