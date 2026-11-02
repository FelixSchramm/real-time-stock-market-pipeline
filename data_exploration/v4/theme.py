"""Readable, self-contained V4 plotting helpers; all outputs stay inside V4."""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, MaxNLocator

ROOT = Path(__file__).resolve().parent
COLORS = ["#75B77B", "#73A8EB", "#D89ABF", "#DDA270", "#75C8C6", "#B5A1E5"]
INK, MUTED, BG, GRID = "#EDEFEA", "#BCC4BC", "#161A17", "#333C35"
UP, DOWN = "#75B77B", "#F3A184"
TICKER_COLORS = dict(zip(("ORCL", "MSFT", "9988.HK", "SAP.DE"), COLORS))


def number(value, digits=1):
    """Format finite numbers in German notation; missing values stay explicit.

    :param value: numeric scalar
    :param digits: decimal places
    :return: formatted text
    """
    if not np.isfinite(value):
        return "k. A."
    return (
        f"{value:,.{digits}f}".replace(",", "_")
        .replace(".", ",")
        .replace("_", ".")
        .replace("-", "−")
    )


def axis_number(value, ax):
    """Choose sufficient precision to distinguish neighboring tick labels.

    :param value: tick value
    :param ax: axes providing the locator ticks
    :return: German-formatted number
    """
    ticks = ax.get_yticks()
    step = min(np.diff(ticks)) if len(ticks) > 1 else 1
    digits = next(
        (
            d
            for d in range(5)
            if round(step, d) > 0 and np.isclose(round(step, d), step)
        ),
        4,
    )
    return number(value, digits)


def percent(value):
    """Format percentage points with one decimal place."""
    return number(value) + " %"


def figure(title, subtitle, rows=1, cols=1, height=7.2, sharex=False):
    """Create chart panels with room for title, explanation and provenance.

    :param title: analytical chart title
    :param subtitle: units and methodology
    :param rows: panel rows
    :param cols: panel columns
    :param height: figure height in inches
    :param sharex: share horizontal axes
    :return: figure and flat array of axes
    """
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "text.color": INK,
            "axes.labelcolor": MUTED,
            "axes.edgecolor": GRID,
            "axes.facecolor": BG,
            "figure.facecolor": BG,
            "savefig.facecolor": BG,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.alpha": 0.6,
            "lines.linewidth": 2,
            "legend.frameon": False,
            "legend.fontsize": 9,
        }
    )
    fig, axes = plt.subplots(
        rows, cols, figsize=(12.6, height), sharex=sharex, squeeze=False
    )
    fig.subplots_adjust(
        left=0.09, right=0.88, top=0.78, bottom=0.19, hspace=0.55, wspace=0.35
    )
    fig.text(0.055, 0.94, title, fontsize=17, weight="bold", va="top")
    fig.text(
        0.055,
        0.885,
        "\n".join(textwrap.wrap(subtitle, 140)),
        fontsize=10,
        color=MUTED,
        va="top",
    )
    for ax in axes.flat:
        ax.grid(False, axis="x")
        ax.tick_params(length=0, labelsize=9)
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda x, _, axis=ax: axis_number(x, axis))
        )
    return fig, axes.ravel()


def finish(fig, name, bundle, note="", source="Yahoo Finance / yfinance"):
    """Save a chart with dated provenance and close its figure.

    :param fig: Matplotlib figure
    :param name: output name without extension
    :param bundle: snapshot metadata
    :param note: interpretation caveat or chart-specific finding
    :param source: source label
    :return: relative PNG path
    """
    retrieved = pd.Timestamp(bundle["retrieved_at"]).strftime("%d.%m.%Y %H:%M UTC")
    fig.text(
        0.055,
        0.105,
        "\n".join(textwrap.wrap(note, 151)),
        fontsize=9,
        color=MUTED,
        va="top",
    )
    fig.text(
        0.055, 0.025, f"{source} · Abruf {retrieved} · V4", fontsize=8, color=MUTED
    )
    target = ROOT / "charts" / (name + ".png")
    target.parent.mkdir(exist_ok=True)
    fig.savefig(target, dpi=145)
    plt.close(fig)
    return str(target.relative_to(ROOT))


def time_axis(ax):
    """Use compact date labels which include the calendar year."""
    locator = mdates.AutoDateLocator(minticks=4, maxticks=7)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))


def end_labels(ax, frame, colors, formatter=number):
    """Attach separated end labels with leaders to their actual data points.

    :param ax: plot axes
    :param frame: dated series as columns
    :param colors: series color dictionary
    :param formatter: numeric label formatter
    :return: None
    """
    ax.figure.canvas.draw()
    previous = float("inf")
    for name in (
        frame.apply(lambda s: s.dropna().iloc[-1]).sort_values(ascending=False).index
    ):
        series = frame[name].dropna()
        y = series.iloc[-1]
        display_y = ax.transData.transform((0, y))[1]
        placed = min(display_y, previous - 18 * ax.figure.dpi / 72)
        ax.plot(series.index[-1], y, "o", color=colors[name], markersize=4)
        ax.annotate(
            f"{name} {formatter(y)}",
            (series.index[-1], y),
            xytext=(10, (placed - display_y) * 72 / ax.figure.dpi),
            textcoords="offset points",
            color=colors[name],
            fontsize=9,
            va="center",
            arrowprops={"arrowstyle": "-", "color": colors[name], "lw": 0.7},
            annotation_clip=False,
        )
        previous = placed


def lines(ax, frame, colors=None, pct=False, direct=False):
    """Draw dated lines without bridging missing observations.

    :param ax: plot axes
    :param frame: dated series as columns
    :param colors: optional stable color mapping
    :param pct: format y axis as percentages
    :param direct: label last values
    :return: None
    """
    colors = colors or dict(zip(frame.columns, COLORS))
    for name in frame:
        ax.plot(
            frame.index,
            frame[name],
            label=name,
            color=colors[name],
            marker="o" if len(frame) < 12 else None,
            markersize=4,
        )
    if pct:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: percent(x)))
    if len(frame) <= 12:
        ax.set_xticks(frame.index, [d.strftime("%m/%Y") for d in frame.index])
    else:
        time_axis(ax)
    if direct:
        end_labels(ax, frame, colors, percent if pct else number)
    else:
        ax.legend(loc="best", ncol=min(3, len(frame.columns)))


def fiscal_labels(index):
    """Label actual fiscal period ends, avoiding ambiguous calendar quarters.

    :param index: Microsoft period ends
    :return: labels with fiscal year and month/year
    """
    return [f"GJ {d.year + (d.month > 6)}\n{d:%m/%Y}" for d in index]


def bars(ax, frame, labels=None, stacked=False):
    """Draw fiscal-period bars with a zero baseline and missingness retained.

    :param ax: plot axes
    :param frame: chronological period data
    :param labels: optional x tick labels
    :param stacked: stack components if true
    :return: None
    """
    x = np.arange(len(frame))
    base = np.zeros(len(frame))
    width = 0.8 / len(frame.columns)
    for i, name in enumerate(frame):
        values = frame[name].to_numpy(dtype=float)
        offset = 0 if stacked else (i - (len(frame.columns) - 1) / 2) * width
        ax.bar(
            x + offset,
            values,
            bottom=base if stacked else None,
            width=0.65 if stacked else width * 0.92,
            color=COLORS[i % len(COLORS)],
            label=name,
        )
        if stacked:
            base += values
    ax.axhline(0, color=MUTED, linewidth=0.7)
    ax.set_xticks(x, labels or fiscal_labels(frame.index))
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0, 1.16),
        ncol=min(4, len(frame.columns)),
        fontsize=8,
    )
