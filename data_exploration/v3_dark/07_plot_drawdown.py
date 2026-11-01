"""Plot drawdown from the running high within the last year (#6)."""

from ci import NEUTRAL, end_labels, german, legend_row, month_axis, new_figure, save
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from returns import drawdown
from stocks import TICKER_COLORS, TICKERS, load_prices


def percent(value):
    """Format a German percentage with a true minus sign.

    :param value: percentage points
    :return: formatted percentage
    """
    return german(value, 1).replace("-", "−") + " %"


def plot(close, path):
    """Draw at most four approved stocks with separated end labels.

    :param close: daily USD prices retaining each stock's native trading dates
    :param path: output PNG path
    :return: None
    """
    if not 1 <= len(close.columns) <= 4 or any(t not in TICKERS for t in close):
        raise ValueError("Höchstens vier Aktien aus der freigegebenen Auswahl nutzen.")
    values = drawdown(close)
    if values.empty:
        raise ValueError("Keine gemeinsamen Handelstage verfügbar.")
    fig, ax = new_figure(
        "Drawdown",
        "Abstand zum bisherigen Höchststand im gezeigten Jahr in %",
        legend_row=True,
    )
    for name in values:
        series = values[name].dropna()
        ax.plot(series.index, series, color=TICKER_COLORS[name])
    ax.axhline(0, color=NEUTRAL["axis"], linewidth=1)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v)))
    month_axis(ax)
    legend_row(fig, [Line2D([], [], color=TICKER_COLORS[t], label=t) for t in values])
    end_labels(ax, values, TICKER_COLORS, percent)
    save(fig, path)


if __name__ == "__main__":
    plot(load_prices(), "data_exploration/v3_dark/07_drawdown.png")
