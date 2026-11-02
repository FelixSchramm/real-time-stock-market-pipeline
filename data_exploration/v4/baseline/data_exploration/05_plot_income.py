"""Plot Microsoft quarterly income and calculated profit margins (#10)."""

import yfinance as yf
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter
from msft_data import figure, fiscal_label, percent, statement
from v3_dark.ci import COLORS, end_labels, legend_row, save

ROWS = ["Total Revenue", "Net Income", "Operating Income"]


def margins(income):
    """Calculate net and operating margins using revenue as denominator.

    :param income: complete quarterly statement values in a common unit
    :return: margin DataFrame in percent
    """
    return (
        income[["Net Income", "Operating Income"]]
        .div(income["Total Revenue"], axis=0)
        .mul(100)
        .rename(
            columns={"Net Income": "Nettomarge", "Operating Income": "Operative Marge"}
        )
    )


def plot(income, path):
    """Draw income bars and a separate margin panel without twin axes.

    :param income: quarterly amounts in billion USD
    :param path: output PNG path
    :return: None
    """
    fig, (top, bottom) = figure(
        "Microsoft (MSFT): Umsatz, Gewinn und Margen pro Quartal",
        "Oben: Mrd. USD · unten: % vom Umsatz · Geschäftsjahresende im Juni",
        legend_row=True,
        nrows=2,
        sharex=True,
        gridspec_kw={"height_ratios": [3, 2], "hspace": 0.18},
    )
    for i, name in enumerate(ROWS[:2]):
        top.bar(
            [x + (i - 0.5) * 0.30 for x in range(len(income))],
            income[name],
            width=0.28,
            color=COLORS[i],
        )
    values = margins(income)
    values.index = range(len(values))
    colors = dict(zip(values.columns, COLORS[1:3]))
    for name in values:
        bottom.plot(
            values.index, values[name], color=colors[name], marker="o", markersize=4
        )
    bottom.yaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v, 0)))
    bottom.set_xticks(range(len(income)), [fiscal_label(d) for d in income.index])
    # Extra room is needed for direct labels outside the last bar group.
    fig.subplots_adjust(right=0.77)
    handles = [
        Patch(color=COLORS[0], label="Umsatz"),
        Patch(color=COLORS[1], label="Nettogewinn"),
    ]
    handles += [Line2D([], [], color=colors[n], label=n) for n in values]
    legend_row(fig, handles)
    end_labels(bottom, values, colors, percent)
    save(fig, path)


if __name__ == "__main__":
    plot(
        statement(yf.Ticker("MSFT").quarterly_income_stmt, ROWS),
        "data_exploration/05_income.png",
    )
