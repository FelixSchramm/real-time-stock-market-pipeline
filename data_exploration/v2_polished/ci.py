"""Apply the personal CI to Matplotlib, with helpers for a polished layout.

Compared to ``v1_basic/ci.py`` this adds: title and subtitle at the left
edge, a card behind the plot, German number and month formatting and
direct end labels. All values come from ``style/felix-schramm-ci.json``.

Set ``CI_MODE=dark`` to use the dark tokens; :func:`save` then writes the
PNG with a ``_dark`` suffix next to the light one.
"""

import json
import os
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

CI = json.loads(
    (Path(__file__).parents[2] / "style" / "felix-schramm-ci.json").read_text()
)
MODE = os.environ.get("CI_MODE", "light")
COLORS = [c["hex"] for c in CI["color"]["categorical"][MODE]]
NEUTRAL = CI["color"]["neutral"][MODE]
FINANCE = CI["color"]["finance"][MODE]
# Keep only installed fonts, Matplotlib warns once per missing family otherwise.
INSTALLED = {f.name for f in font_manager.fontManager.ttflist}
FONTS = [
    f for f in CI["typography"]["font_family"]["stack_matplotlib"] if f in INSTALLED
]
MONTHS = [
    "Jan",
    "Feb",
    "Mär",
    "Apr",
    "Mai",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Okt",
    "Nov",
    "Dez",
]
FIG_SIZE = (10, 5.6)
LEFT = 0.04  # left edge of title, subtitle and legend, in figure coordinates


def use_ci():
    """Set Matplotlib rcParams to the CI look (y-grid only, no frame).

    :return: None
    """
    plt.rcParams.update(
        {
            "font.family": FONTS,
            "font.size": 11,
            "axes.prop_cycle": cycler(color=COLORS),
            "axes.edgecolor": NEUTRAL["axis"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.axisbelow": True,
            "grid.color": NEUTRAL["gridline"],
            "xtick.color": NEUTRAL["ink_muted"],
            "ytick.color": NEUTRAL["ink_muted"],
            "xtick.major.size": 0,
            "xtick.major.pad": 8,
            "ytick.left": False,
            "figure.facecolor": NEUTRAL["page"],
            "axes.facecolor": NEUTRAL["surface"],
            "savefig.facecolor": NEUTRAL["page"],
            "text.color": NEUTRAL["ink"],
            "lines.linewidth": 2,
            "lines.solid_capstyle": "round",
            "legend.frameon": False,
        }
    )


def german(value, decimals=0):
    """Format a number the German way (thousands dot, decimal comma).

    :param value: number to format
    :param decimals: digits after the decimal comma
    :return: formatted string, e.g. ``"1.234,56"``
    """
    return (
        f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    )


def new_figure(title, subtitle, legend_row=False):
    """Create a figure with a card, a left-aligned title and a subtitle.

    :param title: chart title (what is shown)
    :param subtitle: unit and time range, replaces the axis titles
    :param legend_row: leave room for a legend row below the subtitle
    :return: tuple ``(fig, ax)``
    """
    use_ci()
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    fig.subplots_adjust(
        left=0.075, right=0.88, bottom=0.11, top=0.76 if legend_row else 0.81
    )
    card = FancyBboxPatch(
        (0.008, 0.012),
        0.984,
        0.976,
        boxstyle="round,pad=0,rounding_size=0.02",
        mutation_aspect=FIG_SIZE[0] / FIG_SIZE[1],
        transform=fig.transFigure,
        facecolor=NEUTRAL["surface"],
        edgecolor=NEUTRAL["gridline"],
        linewidth=0.8,
        zorder=-1,
    )
    fig.patches.append(card)
    fig.text(LEFT, 0.915, title, fontsize=15)
    fig.text(LEFT, 0.87, subtitle, fontsize=11, color=NEUTRAL["ink_secondary"])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: german(v)))
    return fig, ax


def legend_row(fig, handles):
    """Place the legend as one row below the subtitle.

    :param fig: figure from :func:`new_figure` with ``legend_row=True``
    :param handles: legend handles in display order
    :return: None
    """
    fig.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(LEFT - 0.008, 0.85),
        ncol=len(handles),
        fontsize=10,
        labelcolor=NEUTRAL["ink_secondary"],
        handlelength=1.6,
        columnspacing=1.6,
    )


def month_axis(ax):
    """Label the x-axis with German month names, the year only in January.

    :param ax: axes with a date x-axis
    :return: None
    """

    def label(x, _):
        day = mdates.num2date(x)
        return MONTHS[day.month - 1] + (f" {day:%y}" if day.month == 1 else "")

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(label))


def end_label(ax, x, y, text, color):
    """Mark the last value with a dot and write its label next to it.

    :param ax: axes to draw on
    :param x: x position of the last value
    :param y: y position of the last value
    :param text: label, e.g. ``"466,71 €"``
    :param color: series color of the dot
    :return: None
    """
    ax.scatter(
        [x],
        [y],
        s=40,
        color=color,
        edgecolors=NEUTRAL["surface"],
        linewidths=2,
        zorder=4,
    )
    ax.annotate(
        text,
        (x, y),
        xytext=(9, 0),
        textcoords="offset points",
        va="center",
        fontsize=11,
    )


def save(fig, path):
    """Save the figure, with a ``_dark`` suffix in dark mode, and close it.

    :param fig: figure to save
    :param path: output PNG path of the light version
    :return: None
    """
    if MODE == "dark":
        path = path.replace(".png", "_dark.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
