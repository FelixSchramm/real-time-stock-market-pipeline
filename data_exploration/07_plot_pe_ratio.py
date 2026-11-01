"""Plot historical Microsoft trailing price/earnings (#12).

Yahoo's reported EPS are adjusted EPS, so this differs from GAAP-based portal
ratios. Four successive reported quarters are summed (not averaged). Reports
arrive after close: an EPS value becomes effective on the next calendar day,
then on the next available trading session. No future EPS are backfilled.
"""

import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.lines import Line2D
from msft_data import figure, load_close, load_earnings
from v3_dark.ci import COLORS, NEUTRAL, end_label, german, legend_row, save


def trailing_pe(earnings, close):
    """Align four-quarter EPS to prices without after-close lookahead.

    :param earnings: reported EPS indexed by normalized report date
    :param close: unadjusted daily closes in USD
    :return: positive-EPS historical price/earnings Series
    """
    eps = earnings["Reported EPS"].sort_index()
    ttm = eps.rolling(4, min_periods=4).sum()
    # A missing quarter must not turn four non-consecutive reports into TTM EPS.
    consecutive = eps.index.to_series().diff().dt.days.between(60, 130)
    ttm = ttm.where(consecutive.rolling(3).sum().eq(3))
    ttm.index += pd.Timedelta(days=1)
    known = (
        ttm.reindex(ttm.index.union(close.index))
        .sort_index()
        .ffill()
        .reindex(close.index)
    )
    # Preserve an explicit gap until four consecutive reports are available again.
    valid = (
        ttm.notna()
        .astype(float)
        .reindex(ttm.index.union(close.index))
        .sort_index()
        .ffill()
        .reindex(close.index)
    )
    return close.div(known.where((known > 0) & valid.eq(1))).dropna()


def plot(pe, path):
    """Draw the P/E history and its median.

    :param pe: historical P/E values
    :param path: output PNG path
    :return: None
    """
    if pe.empty:
        raise ValueError("Keine vier aufeinanderfolgenden EPS-Berichte mit Kursdaten.")
    fig, ax = figure(
        "Microsoft (MSFT): Kurs-Gewinn-Verhältnis über die Zeit",
        "Unbereinigter USD-Kurs / Summe der letzten 4 gemeldeten Quartals-EPS · adjustierte EPS",
        legend_row=True,
    )
    ax.plot(pe.index, pe, color=COLORS[1])
    ax.axhline(pe.median(), color=NEUTRAL["ink_secondary"], linestyle=":")
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    legend_row(
        fig,
        [
            Line2D([], [], color=COLORS[1], label="KGV (TTM)"),
            Line2D(
                [],
                [],
                color=NEUTRAL["ink_secondary"],
                linestyle=":",
                label=f"Median {german(pe.median(), 1)}",
            ),
        ],
    )
    end_label(ax, pe.index[-1], pe.iloc[-1], german(pe.iloc[-1], 1), COLORS[1])
    save(fig, path)


if __name__ == "__main__":
    reports = load_earnings()
    plot(
        trailing_pe(reports, load_close(start=reports.index.min())),
        "data_exploration/07_pe_ratio.png",
    )
