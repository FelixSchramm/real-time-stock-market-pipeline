"""Compare Microsoft price return with two USD price indices (#13).

Unadjusted closes compare prices consistently: no dividend reinvestment and
no currency conversion. The drawdown is relative to the high since year start.
"""

import yfinance as yf
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from msft_data import figure, percent
from v3_dark.ci import COLORS, NEUTRAL, end_labels, legend_row, month_axis, save
from v3_dark.returns import drawdown

NAMES = {"MSFT": "MSFT", "^GSPC": "S&P 500", "^NDX": "Nasdaq-100"}
PALETTE = dict(zip(NAMES.values(), [COLORS[1], COLORS[0], COLORS[2]]))


def load_prices():
    """Load common year-to-date closes for MSFT and both indices.

    :return: complete prices in fixed display order
    """
    close = yf.download(
        list(NAMES), period="ytd", auto_adjust=False, threads=False, progress=False
    )["Close"]
    close = close.reindex(columns=NAMES).rename(columns=NAMES)
    if close.empty or close.isna().all().any():
        raise ValueError("MSFT oder ein Vergleichsindex fehlt.")
    close = close.dropna()
    if len(close) < 2:
        raise ValueError("Zu wenige gemeinsame Handelstage.")
    return close


def plot(close, path):
    """Draw indexed closes and a separate Microsoft drawdown panel.

    :param close: daily closes on common trading dates
    :param path: output PNG path
    :return: None
    """
    indexed = close.div(close.iloc[0]).mul(100)
    dd = drawdown(close["MSFT"])
    fig, (top, bottom) = figure(
        "Microsoft (MSFT) gegen S&P 500 und Nasdaq-100 seit Jahresbeginn",
        f"Basis 100 am {close.index[0]:%d.%m.%Y} · USD / Indexpunkte · ohne FX und Dividenden",
        legend_row=True,
        nrows=2,
        sharex=True,
        gridspec_kw={"height_ratios": [3, 2], "hspace": 0.18},
    )
    fig.subplots_adjust(right=0.80)
    for name in indexed:
        top.plot(indexed.index, indexed[name], color=PALETTE[name])
    top.axhline(100, color=NEUTRAL["axis"], linewidth=1)
    bottom.plot(dd.index, dd, color=COLORS[1])
    bottom.fill_between(dd.index, dd, 0, color=COLORS[1], alpha=0.15)
    bottom.axhline(0, color=NEUTRAL["axis"], linewidth=1)
    bottom.set_ylabel("MSFT Drawdown")
    bottom.yaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v, 0)))
    month_axis(bottom)
    legend_row(fig, [Line2D([], [], color=PALETTE[n], label=n) for n in indexed])
    end_labels(top, indexed, PALETTE)
    save(fig, path)


if __name__ == "__main__":
    plot(load_prices(), "data_exploration/08_benchmark.png")
