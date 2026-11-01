"""Apply the personal CI (font, colors, chart style) to Matplotlib.

All values come from ``style/felix-schramm-ci.json`` so plots, dashboards and
application documents share one source.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib import font_manager

CI = json.loads(
    (Path(__file__).parents[1] / "style" / "felix-schramm-ci.json").read_text()
)
COLORS = [c["hex"] for c in CI["color"]["categorical"]["light"]]
NEUTRAL = CI["color"]["neutral"]["light"]
FINANCE = CI["color"]["finance"]["light"]
# Keep only installed fonts, Matplotlib warns once per missing family otherwise.
INSTALLED = {f.name for f in font_manager.fontManager.ttflist}
FONTS = [
    f for f in CI["typography"]["font_family"]["stack_matplotlib"] if f in INSTALLED
]


def use_ci():
    """Set Matplotlib rcParams to the CI look (left title, y-grid, no frame).

    :return: None
    """
    plt.rcParams.update(
        {
            "font.family": FONTS,
            "axes.prop_cycle": cycler(color=COLORS),
            "axes.titlelocation": "left",
            "axes.titlesize": 13,
            "axes.titlepad": 14,
            "axes.labelcolor": NEUTRAL["ink_secondary"],
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
            "ytick.left": False,
            "figure.facecolor": NEUTRAL["surface"],
            "axes.facecolor": NEUTRAL["surface"],
            "savefig.facecolor": NEUTRAL["surface"],
            "text.color": NEUTRAL["ink"],
            "lines.linewidth": 2,
            "legend.frameon": False,
        }
    )
