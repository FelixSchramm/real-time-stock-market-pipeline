"""Plot reported Microsoft annual cash flows in billion USD (#9)."""

import yfinance as yf
from matplotlib.patches import Patch
from msft_data import figure, fiscal_label, statement
from v3_dark.ci import COLORS, german, legend_row, save

SERIES = ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"]
LABELS = ["Operativer Cashflow", "Capex (Investitionen)", "Free Cashflow"]


def load_cashflow():
    """Load only complete annual statement periods.

    :return: cash flows in billion USD with capex as positive expenditure
    """
    data = statement(yf.Ticker("MSFT").cashflow, SERIES)
    data["Capital Expenditure"] = data["Capital Expenditure"].abs()
    return data


def plot(data, path):
    """Draw grouped annual cash-flow bars and label free cash flow.

    :param data: annual cash flows in billion USD
    :param path: output PNG path
    :return: None
    """
    fig, ax = figure(
        "Microsoft (MSFT): Cashflow und Investitionen pro Geschäftsjahr",
        "Mrd. USD · Geschäftsjahresende im Juni · nur vollständige Berichte",
        legend_row=True,
    )
    fig.subplots_adjust(right=0.96)
    for i, name in enumerate(SERIES):
        bars = ax.bar(
            [x + (i - 1) * 0.26 for x in range(len(data))],
            data[name],
            width=0.24,
            color=COLORS[i],
        )
        if name == "Free Cash Flow":
            ax.bar_label(bars, labels=[german(v, 1) for v in data[name]], padding=5)
    ax.set_xticks(range(len(data)), [fiscal_label(d, annual=True) for d in data.index])
    legend_row(fig, [Patch(color=c, label=n) for c, n in zip(COLORS, LABELS)])
    save(fig, path)


if __name__ == "__main__":
    plot(load_cashflow(), "data_exploration/04_cashflow_annual.png")
