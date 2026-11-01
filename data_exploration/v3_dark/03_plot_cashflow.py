"""Plot quarterly operating cash flow, capex and free cash flow of MSFT (dark).

Same plot as ``v2_polished/03_plot_cashflow.py``: billion USD as reported by
Microsoft, quarters without data are dropped.

Usage::

    python data_exploration/v3_dark/03_plot_cashflow.py
"""

import yfinance as yf
from ci import COLORS, german, legend_row, new_figure, save
from matplotlib.patches import Patch

# CI categorical colors in fixed order (forest, blue, orchid).
SERIES = [
    ("Operating Cash Flow", "Operativer Cashflow", COLORS[0]),
    ("Capital Expenditure", "Capex (Investitionen)", COLORS[1]),
    ("Free Cash Flow", "Free Cashflow", COLORS[2]),
]


def load_cashflow():
    """Load the quarterly cash flow figures of MSFT in billion USD.

    :return: DataFrame indexed by quarter end (oldest first), capex positive
    """
    rows = [name for name, _, _ in SERIES]
    cashflow = yf.Ticker("MSFT").quarterly_cashflow.loc[rows].dropna(axis=1)
    cashflow = cashflow.T.sort_index() / 1e9
    # Capex is reported as an outflow (negative); plot its size next to the rest.
    cashflow["Capital Expenditure"] = cashflow["Capital Expenditure"].abs()
    return cashflow


def fiscal_label(quarter_end):
    """Label a quarter end with Microsoft's fiscal quarter (year ends in June).

    :param quarter_end: last day of the quarter (pandas Timestamp)
    :return: two-line label, e.g. ``"Q1 GJ26\\n09/2025"``
    """
    fiscal_year = quarter_end.year + (quarter_end.month > 6)
    fiscal_quarter = (quarter_end.month - 7) % 12 // 3 + 1
    return f"Q{fiscal_quarter} GJ{fiscal_year % 100}\n{quarter_end:%m/%Y}"


def plot(cashflow, path):
    """Draw grouped bars per quarter and label the free cash flow bars.

    :param cashflow: DataFrame from :func:`load_cashflow`
    :param path: output PNG path
    :return: None
    """
    fig, ax = new_figure(
        "Microsoft (MSFT): Cashflow und Investitionen",
        "Mrd. USD je Fiskalquartal, das Geschäftsjahr endet im Juni",
        legend_row=True,
    )
    # Bars need no room for end labels on the right.
    fig.subplots_adjust(right=0.96)
    width = 0.24
    positions = range(len(cashflow))
    for i, (name, _, color) in enumerate(SERIES):
        x = [p + (i - 1) * (width + 0.02) for p in positions]
        bars = ax.bar(x, cashflow[name], width=width, color=color)
        if name == "Free Cash Flow":
            ax.bar_label(bars, labels=[german(v, 1) for v in cashflow[name]], padding=4)
    ax.set_xticks(list(positions))
    ax.set_xticklabels([fiscal_label(d) for d in cashflow.index])
    legend_row(fig, [Patch(color=color, label=label) for _, label, color in SERIES])
    save(fig, path)


if __name__ == "__main__":
    data = load_cashflow()
    plot(data, "data_exploration/v3_dark/03_cashflow.png")
    print(data.round(1))
