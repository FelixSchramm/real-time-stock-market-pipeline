"""Render price, return and risk tiles for approved portfolio stocks (#7)."""

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ci import FINANCE, NEUTRAL, german, save, use_ci
from matplotlib.patches import FancyBboxPatch
from returns import drawdown
from stocks import TICKER_COLORS, load_prices


def metrics(close):
    """Calculate returns and risk on observed daily adjusted closes.

    :param close: one stock's daily close Series
    :return: price, daily/period returns, annual log volatility, max drawdown
    """
    close = close.dropna()
    if len(close) < 3 or (close <= 0).any():
        raise ValueError("Mindestens drei positive Schlusskurse erforderlich.")
    return pd.Series(
        {
            "price": close.iloc[-1],
            "day": close.iloc[-1] / close.iloc[-2] - 1,
            "year": close.iloc[-1] / close.iloc[0] - 1,
            "volatility": np.log(close / close.shift()).std() * np.sqrt(252),
            "drawdown": drawdown(close).min() / 100,
        }
    )


def signed_return(value):
    """Format a signed return with both direction and sign.

    :param value: fractional return
    :return: directional German percentage
    """
    return f"{'▲ +' if value >= 0 else '▼ −'}{german(abs(value) * 100, 2)} %"


def plot(close, path):
    """Draw up to three KPI cards per row.

    :param close: daily price DataFrame in the approved ticker order
    :param path: output PNG path
    :return: None
    """
    use_ci()
    rows = math.ceil(len(close.columns) / 3)
    fig = plt.figure(figsize=(12, 1 + 3.6 * rows))
    fig.text(0.04, 0.94, "Aktien im Überblick", fontsize=17)
    fig.text(
        0.04,
        0.89,
        f"Bereinigte Kurse in USD · {close.index[0]:%d.%m.%Y}–{close.index[-1]:%d.%m.%Y}",
        color=NEUTRAL["ink_secondary"],
        fontsize=10,
    )
    for i, ticker in enumerate(close):
        values = metrics(close[ticker])
        ax = fig.add_axes(
            [
                0.035 + (i % 3) * 0.32,
                0.04 + (rows - 1 - i // 3) * 0.76 / rows,
                0.30,
                0.72 / rows,
            ]
        )
        ax.set_axis_off()
        ax.add_patch(
            FancyBboxPatch(
                (0, 0),
                1,
                1,
                boxstyle="round,pad=0,rounding_size=.035",
                transform=ax.transAxes,
                facecolor=NEUTRAL["surface"],
                edgecolor=NEUTRAL["gridline"],
            )
        )
        ax.text(0.07, 0.87, "●", color=TICKER_COLORS[ticker], fontsize=15)
        ax.text(0.17, 0.87, ticker, fontsize=15)
        ax.text(0.07, 0.69, f"{german(values['price'], 2)} USD", fontsize=23)
        for j, (label, key) in enumerate(
            [
                ("Letzter Tag", "day"),
                ("12 Monate", "year"),
                ("Volatilität p. a.", "volatility"),
                ("Max. Drawdown", "drawdown"),
            ]
        ):
            y = 0.50 - 0.11 * j
            directional = key in ("day", "year")
            value = values[key]
            text = (
                signed_return(value)
                if directional
                else german(value * 100, 1).replace("-", "−") + " %"
            )
            color = (
                FINANCE["up" if value >= 0 else "down"]
                if directional
                else NEUTRAL["ink"]
            )
            ax.text(0.07, y, label, color=NEUTRAL["ink_secondary"], fontsize=10)
            ax.text(0.93, y, text, ha="right", color=color, fontsize=10)
    save(fig, path)


if __name__ == "__main__":
    plot(load_prices(), "data_exploration/v3_dark/08_kpi_tiles.png")
