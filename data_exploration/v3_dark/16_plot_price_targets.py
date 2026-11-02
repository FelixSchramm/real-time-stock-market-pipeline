"""Plot all available year-to-date Microsoft analyst target actions (#16).

No historical consensus is implied: every marker is an individual firm's
published target. Missing or zero targets are excluded, never forward-filled.
"""

import yfinance as yf
from ci import COLORS, NEUTRAL, legend_row, month_axis, save
from matplotlib.lines import Line2D
from msft_data import daily_index, figure, load_close

ACTIONS = [
    ("Raises", "^", "Kursziel erhöht", COLORS[0]),
    ("Lowers", "v", "Kursziel gesenkt", COLORS[2]),
    ("Other", "o", "Bestätigt / sonstige", NEUTRAL["ink_secondary"]),
]


def prepare_actions(actions, close):
    """Keep positive targets in the displayed price period.

    :param actions: analyst action DataFrame indexed by timestamp
    :param close: daily closes defining the displayed date window
    :return: normalized target actions with a shape category
    """
    actions = daily_index(actions).copy()
    actions = actions.loc[
        actions.index.to_series().between(close.index[0], close.index[-1])
        & (actions["currentPriceTarget"] > 0)
    ]
    actions["kind"] = actions["priceTargetAction"].where(
        actions["priceTargetAction"].isin(["Raises", "Lowers"]), "Other"
    )
    return actions


def plot(actions, close, path):
    """Draw prices and dated target-action markers with shape-based direction.

    :param actions: filtered year-to-date analyst targets
    :param close: daily unadjusted USD closes
    :param path: output PNG path
    :return: None
    """
    if actions.empty:
        raise ValueError("Keine datierten Kursziele im Kurszeitraum verfügbar.")
    fig, ax = figure(
        "Microsoft (MSFT): Kursziele der Analysten über die Zeit",
        f"USD seit Jahresbeginn · {len(actions)} Einzelmeldungen · keine Konsenshistorie",
        legend_row=True,
    )
    fig.subplots_adjust(right=0.96)
    ax.plot(close.index, close, color=COLORS[1])
    handles = [Line2D([], [], color=COLORS[1], label="MSFT Schlusskurs")]
    for key, marker, label, color in ACTIONS:
        subset = actions.loc[actions["kind"] == key]
        ax.scatter(
            subset.index,
            subset["currentPriceTarget"],
            marker=marker,
            color=color,
            edgecolor=NEUTRAL["surface"],
            linewidth=0.4,
            alpha=0.75,
            s=35,
            zorder=3,
        )
        handles.append(
            Line2D([], [], marker=marker, linestyle="", color=color, label=label)
        )
    legend_row(fig, handles)
    month_axis(ax)
    save(fig, path)


if __name__ == "__main__":
    prices = load_close("ytd")
    plot(
        prepare_actions(yf.Ticker("MSFT").upgrades_downgrades, prices),
        prices,
        "data_exploration/v3_dark/16_price_targets.png",
    )
