"""Plot Microsoft call-option implied volatility by strike (#19).

Calls only, within +/-20% of the last close. Exclude no-open-interest rows,
nonfinite/near-zero IV (<=1%) and trades older than seven calendar days.
This is a quoted snapshot, not an independently estimated volatility curve;
weekend and stale quotes can still limit its interpretation.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from ci import COLORS, NEUTRAL, german, legend_row, save
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from msft_data import figure, load_close, percent


def select_expiries(expiries, today):
    """Choose distinct expiries about 7, 30 and 90 days away.

    :param expiries: available ISO expiry strings
    :param today: reference calendar date
    :return: three ISO expiry strings in horizon order
    """
    available = sorted(
        d for d in expiries if (pd.Timestamp(d) - pd.Timestamp(today)).days >= 7
    )
    if len(available) < 3:
        raise ValueError("Weniger als drei geeignete Optionsverfälle verfügbar.")
    selected = []
    for horizon in (7, 30, 90):
        date = min(
            available,
            key=lambda d: abs((pd.Timestamp(d) - pd.Timestamp(today)).days - horizon),
        )
        selected.append(date)
        available.remove(date)
    return selected


def valid_calls(calls, spot, now):
    """Remove unusable or stale calls from the strike window.

    :param calls: Yahoo call-chain table
    :param spot: current underlying close in USD
    :param now: timezone-aware snapshot timestamp
    :return: sorted calls suitable for the plotted snapshot
    """
    recent = pd.to_datetime(calls["lastTradeDate"], utc=True)
    valid = (
        (calls["openInterest"] > 0)
        & np.isfinite(calls["impliedVolatility"])
        & (calls["impliedVolatility"] > 0.01)
        & calls["strike"].between(spot * 0.8, spot * 1.2)
        & recent.between(now - pd.Timedelta(days=7), now)
    )
    return calls.loc[valid].sort_values("strike")


def plot(chains, spot, now, path):
    """Draw one available IV curve per selected expiry.

    :param chains: mapping from ISO expiry to filtered call table
    :param spot: last underlying USD close
    :param now: snapshot timestamp
    :param path: output PNG path
    :return: None
    """
    if not any(len(c) >= 2 for c in chains.values()):
        raise ValueError(
            "Keine belastbaren Optionsketten nach Aktualitätsfilter verfügbar."
        )
    fig, ax = figure(
        "Microsoft (MSFT): Implizite Volatilität nach Strike",
        f"Calls · Snapshot {now:%d.%m.%Y} · Open Interest > 0 · letzte Transaktion ≤ 7 Tage alt",
        legend_row=True,
    )
    fig.subplots_adjust(right=0.96, bottom=0.16)
    handles = []
    for color, (expiry, calls) in zip(COLORS, chains.items()):
        ax.plot(
            calls["strike"],
            calls["impliedVolatility"] * 100,
            color=color,
            marker="o",
            markersize=3,
        )
        label = f"{pd.Timestamp(expiry):%d.%m.%Y}" + (
            " (zu wenige Werte)" if len(calls) < 2 else ""
        )
        handles.append(
            Line2D([], [], color=color, marker="o", markersize=4, label=label)
        )
    ax.axvline(spot, color=NEUTRAL["ink_secondary"], linestyle=":", linewidth=1.5)
    handles.append(
        Line2D(
            [],
            [],
            color=NEUTRAL["ink_secondary"],
            linestyle=":",
            label=f"Letzter Kurs {german(spot, 2)} USD",
        )
    )
    ax.set_xlabel("Strike in USD")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v, 0)))
    ax.set_xlim(spot * 0.8, spot * 1.2)
    legend_row(fig, handles)
    fig.text(
        0.04,
        0.05,
        "Nur verfügbare Quotes · keine Glättung · außerhalb der Handelszeit können Kurse veraltet sein",
        color=NEUTRAL["ink_secondary"],
        fontsize=9,
    )
    save(fig, path)


if __name__ == "__main__":
    stock = yf.Ticker("MSFT")
    snapshot = pd.Timestamp.now(tz="UTC")
    spot = load_close("1d").iloc[-1]
    expiries = select_expiries(stock.options, snapshot.tz_localize(None).normalize())
    chains = {
        d: valid_calls(stock.option_chain(d).calls, spot, snapshot) for d in expiries
    }
    plot(chains, spot, snapshot, "data_exploration/v3_dark/19_implied_vol.png")
