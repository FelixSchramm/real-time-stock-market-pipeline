"""Plot the last twelve complete months of adjusted stock returns (#5)."""

import numpy as np
import pandas as pd
from ci import CI, MODE, MONTHS, NEUTRAL, german, new_figure, save
from matplotlib.colors import BoundaryNorm, ListedColormap, to_rgb
from stocks import load_prices

THRESHOLDS = [-10, -5, -2, -0.5, 0.5, 2, 5, 10]


def monthly_returns(close, today=None):
    """Calculate complete monthly returns without filling missing prices.

    :param close: daily adjusted prices, one column per stock
    :param today: optional reference date for reproducible checks
    :return: up to twelve complete months of returns in percent
    """
    current_month = pd.Timestamp(today or pd.Timestamp.now()).to_period("M").start_time
    monthly = close.resample("ME").last()
    monthly = monthly.loc[monthly.index < current_month]
    return monthly.pct_change(fill_method=None).iloc[1:].tail(12).mul(100)


def text_color(background):
    """Choose the CI ink with the higher WCAG contrast against a cell.

    :param background: cell background color
    :return: light or dark CI ink color
    """

    def luminance(color):
        """Return relative sRGB luminance.

        :param color: Matplotlib color specification
        :return: relative luminance between zero and one
        """
        rgb = np.array(to_rgb(color))
        linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
        return linear @ [0.2126, 0.7152, 0.0722]

    cell = luminance(background)
    inks = [CI["color"]["neutral"][m]["ink"] for m in ("light", "dark")]
    return max(
        inks,
        key=lambda ink: (max(cell, luminance(ink)) + 0.05)
        / (min(cell, luminance(ink)) + 0.05),
    )


def plot(returns, path):
    """Draw a discrete nine-bin heatmap with signed labels.

    :param returns: monthly returns in percent, stocks in columns
    :param path: output PNG path
    :return: None
    """
    if returns.empty:
        raise ValueError("Keine vollständigen Monate verfügbar.")
    colors = CI["color"]["diverging"][f"returns_{MODE}"]
    fig, ax = new_figure(
        "Monatsrenditen",
        "Bereinigter Schlusskurs gegenüber Vormonatsende in % · nur volle Monate",
    )
    fig.set_size_inches(12, max(4.5, 2.5 + 0.4 * len(returns.columns)))
    fig.subplots_adjust(left=0.08, right=0.96, bottom=0.22, top=0.78)
    values = returns.T.to_numpy()
    bins = np.digitize(values, THRESHOLDS)
    ax.grid(False)
    ax.pcolormesh(
        np.ma.masked_invalid(values),
        cmap=ListedColormap(colors),
        norm=BoundaryNorm([-np.inf, *THRESHOLDS, np.inf], 9),
        edgecolors=NEUTRAL["surface"],
        linewidth=2 * 72 / 150,
    )
    for row, column in np.ndindex(values.shape):
        value = values[row, column]
        label = (
            "–"
            if not np.isfinite(value)
            else f"{'+' if value >= 0 else '−'}{german(abs(value), 1)}"
        )
        ink = (
            NEUTRAL["ink_muted"]
            if not np.isfinite(value)
            else text_color(colors[bins[row, column]])
        )
        ax.text(
            column + 0.5,
            row + 0.5,
            label,
            ha="center",
            va="center",
            color=ink,
            fontsize=10,
        )
    ax.set_yticks(np.arange(len(returns.columns)) + 0.5, returns.columns)
    ax.invert_yaxis()
    labels = [
        MONTHS[d.month - 1] + (f"\n{d:%Y}" if i == 0 or d.month == 1 else "")
        for i, d in enumerate(returns.index)
    ]
    ax.set_xticks(np.arange(len(returns)) + 0.5, labels)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(
        0.04,
        0.07,
        "Farbstufen: < −10 | −10 | −5 | −2 | −0,5 bis +0,5 | +2 | +5 | +10 | ≥ +10 %",
        fontsize=9,
        color=NEUTRAL["ink_secondary"],
    )
    save(fig, path)


if __name__ == "__main__":
    plot(
        monthly_returns(load_prices("13mo")),
        "data_exploration/v3_dark/06_monthly_returns.png",
    )
