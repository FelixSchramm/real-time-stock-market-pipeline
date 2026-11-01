"""Plot quarterly operating cash flow, capex and free cash flow of MSFT.

Values are in billion USD, as reported by Microsoft (no currency conversion).
yfinance only provides the last few quarters, quarters without data are
dropped.

Usage::

    python data_exploration/03_plot_cashflow.py
"""

import matplotlib.pyplot as plt
import yfinance as yf
from ci import COLORS, use_ci

# CI categorical colors in fixed order (forest, blue, copper).
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
    use_ci()
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.27
    positions = range(len(cashflow))
    for i, (name, label, color) in enumerate(SERIES):
        x = [p + (i - 1) * width for p in positions]
        bars = ax.bar(x, cashflow[name], width=width * 0.9, color=color, label=label)
        if name == "Free Cash Flow":
            ax.bar_label(bars, fmt="%.1f", padding=3)
    ax.set_xticks(list(positions))
    ax.set_xticklabels([fiscal_label(d) for d in cashflow.index])
    ax.set_title("Microsoft (MSFT): Cashflow und Investitionen pro Quartal")
    ax.set_xlabel("Fiskalquartal (Geschäftsjahr endet im Juni) und Quartalsende")
    ax.set_ylabel("Mrd. USD")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


if __name__ == "__main__":
    data = load_cashflow()
    plot(data, "data_exploration/03_cashflow.png")
    print(data.round(1))
