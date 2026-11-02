"""V4 market views: comparable returns, explicit events and contextual snapshots."""

import numpy as np
import pandas as pd
from calculations import dividend_yield, drawdown, monthly_returns, valid_calls
from data import NAMES, TICKERS, dates, prices, statement
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.ticker import FuncFormatter
from theme import (
    COLORS,
    DOWN,
    GRID,
    INK,
    MUTED,
    TICKER_COLORS,
    UP,
    VALUE_COLORS,
    VALUE_MISSING,
    VALUE_TEXT,
    bars,
    figure,
    finish,
    lines,
    number,
    percent,
    time_axis,
)


def window(bundle):
    """Return common comparison endpoints from a full year of observed prices."""
    common = prices(bundle).dropna()
    end = common.index[-1]
    start = common.index[common.index.searchsorted(end - pd.DateOffset(years=1))]
    return start, end


def comparison(bundle, currency="EUR", total=True):
    """Render five comparable portfolio/benchmark views for one setting.

    :param bundle: fetched snapshot
    :param currency: common display currency
    :param total: adjusted-close return or price-only return
    :return: output paths keyed by chart number
    """
    start, end = window(bundle)
    history = prices(bundle, currency=currency, total=total)
    recent = history.loc[start:end]
    common = recent.dropna()
    kind = "total" if total else "price"
    suffix = f"_{currency}_{kind}"
    label = (
        "Gesamtrendite-Näherung aus bereinigten Kursen"
        if total
        else "Kursrendite ohne Dividenden"
    )
    subtitle = f"{currency} · {start:%d.%m.%Y}–{end:%d.%m.%Y} · {label}"
    note = (
        "Gemeinsame Start-/Endtage; eigene Börsenkalender dazwischen. FX zum jeweiligen Tageskurs, nicht synchronen Handelszeitpunkt. "
        "Bereinigte Kurse enthalten keine persönlichen Steuern oder Gebühren."
    )
    outputs = {}
    indexed = common / common.iloc[0] * 100
    fig, (ax,) = figure("Was wurde aus 100? Deine Aktien im Vergleich", subtitle)
    lines(ax, indexed, TICKER_COLORS, direct=True)
    ax.axhline(100, color=MUTED, lw=0.8)
    ax.set_ylabel("Startwert = 100")
    outputs["05"] = finish(fig, "05_indexed" + suffix, bundle, note)

    returns = monthly_returns(history.loc[:end], bundle["retrieved_at"])
    # All live return heatmaps share the CI's red/grey/green value scale.
    cmap = ListedColormap(VALUE_COLORS)
    cmap.set_bad(VALUE_MISSING)
    bounds = [-100, -10, -5, -2, -0.5, 0.5, 2, 5, 10, 1000]
    fig, (ax,) = figure(
        "Welche Monate haben die Rendite geprägt?",
        f"{currency} · letzte 12 vollständige Monate · {label}",
        height=6.2,
    )
    fig.subplots_adjust(right=0.95, bottom=0.29)
    values = returns.T.to_numpy(dtype=float)
    mesh = ax.imshow(
        np.ma.masked_invalid(values),
        cmap=cmap,
        norm=BoundaryNorm(bounds, 9),
        aspect="auto",
    )
    for (r, c), value in np.ndenumerate(values):
        ax.text(
            c,
            r,
            (
                number(value)
                if not np.isfinite(value)
                else ("+" if value > 0 else "") + number(value)
            ),
            ha="center",
            va="center",
            color=VALUE_TEXT,
            fontsize=10,
        )
    ax.set_yticks(range(4), [NAMES[t] for t in TICKERS])
    ax.set_xticks(range(len(returns)), [d.strftime("%m/%y") for d in returns.index])
    ax.grid(False)
    cb = fig.colorbar(
        mesh,
        ax=ax,
        orientation="horizontal",
        fraction=0.09,
        pad=0.20,
        ticks=[-10, -5, -2, 0, 2, 5, 10],
        spacing="uniform",
        extend="both",
    )
    cb.set_label("Monatsrendite (%) · Randklassen ≤ −10 / ≥ +10", fontsize=9)
    cb.ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _: ("+" if value > 0 else "") + number(value, 0))
    )
    outputs["06"] = finish(
        fig,
        "06_monthly_returns" + suffix,
        bundle,
        "Rot: negativ · Grau: nahe null · Grün: positiv. Kräftigere Farbe: größerer Ausschlag. Vorzeichen bleiben sichtbar; fehlende Kurse werden nicht aufgefüllt.",
    )

    dd = drawdown(history).loc[start:end]
    fig, (ax,) = figure(
        "Kursrisiko: Verlust und Zeit unter dem bisherigen Hoch", subtitle
    )
    lines(ax, dd, TICKER_COLORS, pct=True, direct=True)
    ax.axhline(0, color=MUTED, lw=0.8)
    outputs["07"] = finish(
        fig,
        "07_drawdown" + suffix,
        bundle,
        "Hoch wird aus der gesamten geladenen 10-Jahres-Historie berechnet, nicht am linken Bildrand zurückgesetzt. Kein Maß für Bilanz- oder Insolvenzrisiko.",
    )

    fig, axes = figure(
        "Rendite und Kursrisiko auf einen Blick", subtitle, rows=2, cols=2, height=8.6
    )
    fig.subplots_adjust(left=0.06, right=0.94, hspace=0.35)
    for ax, ticker in zip(axes, TICKERS):
        ax.set_axis_off()
        full = history[ticker].dropna().loc[:end]
        series = recent[ticker].dropna()
        daily = np.log(series / series.shift()).dropna()
        peak_date = full.idxmax()
        elapsed = (end - peak_date).days if full.iloc[-1] < full.max() else 0
        maximum = drawdown(series).min()
        rows = [
            ("Zeitraum-Rendite", percent((series.iloc[-1] / series.iloc[0] - 1) * 100)),
            (
                "Letzter Handelstag",
                percent(series.pct_change(fill_method=None).iloc[-1] * 100),
            ),
            ("Volatilität p. a.", percent(daily.std() * np.sqrt(252) * 100)),
            ("Max. Verlust im Zeitraum", percent(maximum)),
            ("Seit letztem 10J-Hoch", f"{elapsed} Kalendertage"),
        ]
        ax.text(
            0,
            0.97,
            f"{NAMES[ticker]}  ·  {ticker}",
            fontsize=13,
            weight="bold",
            color=TICKER_COLORS[ticker],
            transform=ax.transAxes,
        )
        for i, (key, value) in enumerate(rows):
            ax.text(
                0,
                0.73 - i * 0.15,
                key,
                color=MUTED,
                transform=ax.transAxes,
                fontsize=10,
            )
            ax.text(
                1,
                0.73 - i * 0.15,
                value,
                ha="right",
                transform=ax.transAxes,
                fontsize=11,
            )
    outputs["08"] = finish(
        fig,
        "08_kpis" + suffix,
        bundle,
        "Volatilität: Standardabweichung täglicher Log-Renditen × √252. Zeitraum-Drawdown startet am gemeinsamen Anfang; Hoch-Abstand nutzt 10 Jahre.",
    )

    symbols = ("MSFT", "SPY", "QQQ") if total else ("MSFT", "^GSPC", "^NDX")
    names = {
        "MSFT": "MSFT",
        "SPY": "SPY",
        "QQQ": "QQQ",
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq-100",
    }
    bench = (
        prices(bundle, symbols, currency, total)
        .loc[start:end]
        .dropna()
        .rename(columns=names)
    )
    indexed = bench / bench.iloc[0] * 100
    fig, (top, bottom) = figure(
        "Wie schneidet Microsoft gegenüber dem Markt ab?",
        subtitle,
        rows=2,
        height=8.0,
        sharex=True,
    )
    benchmark_colors = {
        "MSFT": COLORS[1],
        "SPY": COLORS[0],
        "QQQ": COLORS[2],
        "S&P 500": COLORS[0],
        "Nasdaq-100": COLORS[2],
    }
    lines(top, indexed, benchmark_colors, direct=True)
    excess = pd.DataFrame(
        {
            n: (bench["MSFT"] / bench["MSFT"].iloc[0] - bench[n] / bench[n].iloc[0])
            * 100
            for n in bench.columns[1:]
        }
    )
    lines(bottom, excess, benchmark_colors, pct=True)
    bottom.axhline(0, color=MUTED, lw=0.8)
    bottom.set_ylabel("Renditedifferenz (Prozentpunkte)")
    outputs["13"] = finish(
        fig,
        "13_benchmark" + suffix,
        bundle,
        "Bei Gesamtrendite dienen SPY/QQQ als investierbare Index-Näherungen inklusive Ausschüttungen; Tracking und Fondskosten weichen vom Index ab. "
        "Gleiche Start-/Endtage; Umrechnung zum jeweiligen Tageskurs.",
    )
    return outputs


def price_events(bundle):
    """Render raw EUR price and its optional earnings-event overlay."""
    close = prices(bundle, ("MSFT",), "EUR", False)["MSFT"].dropna()
    close = close.loc[str(close.index[-1].year) :]
    earnings = (
        bundle["earnings"].dropna(subset=["Reported EPS", "EPS Estimate"]).sort_index()
    )
    outputs = {}
    for events in (False, True):
        fig, (ax,) = figure(
            (
                "Microsoft: Kurs und veröffentlichte Quartalsergebnisse"
                if events
                else "Microsoft: Kurs in Euro"
            ),
            f"EUR · unbereinigter Schlusskurs mit Tages-FX · {close.index[0]:%d.%m.%Y}–{close.index[-1]:%d.%m.%Y}",
        )
        lines(ax, close.to_frame("MSFT"), {"MSFT": COLORS[1]}, direct=True)
        if events:
            for timestamp, row in earnings.iterrows():
                date = timestamp.tz_localize(None).normalize()
                if (
                    date < close.index[0]
                    or date > close.index[-1]
                    or row["EPS Estimate"] == 0
                ):
                    continue
                surprise = (row["Reported EPS"] / row["EPS Estimate"] - 1) * 100
                y = close.asof(date)
                ax.scatter(
                    date,
                    y,
                    marker="^" if surprise >= 0 else "v",
                    color=UP if surprise >= 0 else DOWN,
                    s=65,
                    zorder=4,
                )
                ax.annotate(
                    f"{number(abs(surprise))} % "
                    + ("über" if surprise >= 0 else "unter")
                    + " Schätzung",
                    (date, y),
                    xytext=(0, 22),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    bbox={"facecolor": "#161A17", "edgecolor": "none", "pad": 3},
                )
            ax.margins(y=0.2)
        key = "02" if events else "01"
        outputs[key] = finish(
            fig,
            key + "_price_events" if events else key + "_price_eur",
            bundle,
            (
                "Ereignismarker: Veröffentlichung nach Börsenschluss, noch vor der Folgetagsreaktion. EPS-Abweichung ist kein Gewinnwachstum."
                if events
                else "Preisansicht ohne Dividenden. Die Vergleichsansichten bieten unabhängig davon EUR/USD und Kurs-/Gesamtrendite."
            ),
        )
    return outputs


def candles(bundle):
    """Render price candles with a separately scaled, labeled volume panel."""
    full = bundle["prices"]["MSFT"]
    data = full[["Open", "High", "Low", "Close", "Volume"]].copy()
    data["SMA20"] = data["Close"].rolling(20).mean()
    data["SMA50"] = data["Close"].rolling(50).mean()
    data = data.tail(60)
    fig, (ax, vol) = figure(
        "Microsoft: Tagesverlauf und Handelsvolumen",
        f"USD · unbereinigte OHLC · {data.index[0]:%d.%m.%Y}–{data.index[-1]:%d.%m.%Y}",
        rows=2,
        height=8.0,
        sharex=True,
    )
    x = np.arange(len(data))
    up = data.Close >= data.Open
    colors = np.where(up, UP, DOWN)
    ax.vlines(x, data.Low, data.High, color=colors, lw=1)
    ax.bar(
        x,
        data.Close - data.Open,
        bottom=data.Open,
        color=np.where(up, "#161A17", DOWN),
        edgecolor=colors,
        width=0.6,
    )
    for i, col in enumerate(["SMA20", "SMA50"]):
        ax.plot(x, data[col], color=COLORS[1 + i], label=col, lw=1.4)
    ax.legend(ncol=2)
    ax.set_ylabel("USD")
    vol.bar(x, data.Volume / 1e6, color="#839387")
    vol.set_ylabel("Volumen (Mio. Aktien)")
    ticks = np.linspace(0, len(data) - 1, 6, dtype=int)
    vol.set_xticks(ticks, [data.index[i].strftime("%d.%m.%y") for i in ticks])
    return finish(
        fig,
        "04_candles",
        bundle,
        "Hohl/grün: Schluss ≥ Eröffnung. Gefüllt/kupfer: Schluss < Eröffnung. Das ist nicht die Veränderung gegenüber dem Vortag. SMA vor dem Ausschnitt berechnet.",
    )


def reactions(bundle):
    """Compare EPS surprises with raw and market-relative next-session returns."""
    close = prices(bundle, ("MSFT", "SPY"), "USD", True).dropna()
    rows = []
    for timestamp, row in (
        bundle["earnings"].dropna(subset=["Reported EPS", "EPS Estimate"]).iterrows()
    ):
        date = timestamp.tz_localize(None).normalize()
        p = close.index.searchsorted(date)
        if p >= len(close) - 1 or close.index[p] != date or row["EPS Estimate"] <= 0:
            continue
        # Microsoft announces at/after the US close; before-open reports use the prior close.
        before_open = timestamp.hour < 9 or (
            timestamp.hour == 9 and timestamp.minute < 30
        )
        base, after = (p - 1, p) if before_open else (p, p + 1)
        if base < 0:
            continue
        returns = (close.iloc[after] / close.iloc[base] - 1) * 100
        rows.append(
            {
                "date": date,
                "surprise": (row["Reported EPS"] / row["EPS Estimate"] - 1) * 100,
                "raw": returns["MSFT"],
                "relative": returns["MSFT"] - returns["SPY"],
            }
        )
    frame = pd.DataFrame(rows).set_index("date").sort_index()
    fig, axes = figure(
        "Erwartungen schlagen ist nicht gleich Kursanstieg",
        f"{len(frame)} Quartale · USD-Renditen · Reaktion über die erste Sitzung nach Veröffentlichung",
        cols=2,
    )
    for ax, col, title in zip(
        axes, ["raw", "relative"], ["Microsoft-Rendite", "Abzüglich SPY-Rendite"]
    ):
        for positive in (True, False):
            mask = frame[col].ge(0) == positive
            ax.scatter(
                frame.loc[mask, "surprise"],
                frame.loc[mask, col],
                edgecolor=UP if positive else DOWN,
                facecolor=UP if positive else "none",
                s=45,
            )
        ax.axhline(0, color=MUTED, lw=0.7)
        ax.axvline(0, color=MUTED, lw=0.7)
        ax.set_title(
            f"{title} · r = {number(frame.surprise.corr(frame[col]),2)}", fontsize=10
        )
        ax.set_xlabel("EPS über/unter Schätzung (%)")
        ax.set_ylabel(
            "Rendite (%)" if col == "raw" else "Renditedifferenz (Prozentpunkte)"
        )
    return finish(
        fig,
        "11_earnings_reaction",
        bundle,
        "Deskriptiver Zusammenhang, keine Prognoseregel. Umsatz, Guidance und andere Nachrichten fehlen als Erklärungsvariablen. Bereinigte Renditen vermeiden Dividendenverzerrungen.",
    )


def pe_history(bundle):
    """Align reported EPS to the next session and retain explicit missing gaps."""
    eps = dates(bundle["earnings"].dropna(subset=["Reported EPS"]))["Reported EPS"]
    eps = eps.loc[~eps.index.duplicated()]
    ttm = eps.rolling(4, min_periods=4).sum()
    consecutive = (
        eps.index.to_series().diff().dt.days.between(60, 130).rolling(3).sum().eq(3)
    )
    ttm = ttm.where(consecutive)
    ttm.index += pd.Timedelta(days=1)
    close = bundle["prices"]["MSFT"].Close
    known = (
        ttm.reindex(ttm.index.union(close.index))
        .sort_index()
        .ffill()
        .reindex(close.index)
    )
    valid = (
        ttm.notna()
        .astype(float)
        .reindex(ttm.index.union(close.index))
        .sort_index()
        .ffill()
        .reindex(close.index)
        .eq(1)
    )
    ratio = close / known.where((known > 0) & valid)
    ratio = ratio.loc[ratio.first_valid_index() :]
    fig, (ax,) = figure(
        "Microsoft: Was kostet ein Dollar berichteter Gewinn?",
        "KGV = USD-Kurs / vier zuletzt veröffentlichte Quartals-EPS · Yahoo-Earnings-Basis",
    )
    lines(ax, ratio.to_frame("KGV"), {"KGV": COLORS[1]}, direct=True)
    median = ratio.median()
    ax.axhline(
        median, color=MUTED, ls=":", label=f"Historischer Median {number(median)}"
    )
    ax.legend(loc="upper left")
    return finish(
        fig,
        "12_pe_ratio",
        bundle,
        "Median ist kein fairer Wert. Earnings-EPS können von GAAP-Diluted-EPS abweichen; nicht ungeprüft mit Portal-KGV gleichsetzen. Nachbörsliche Gewinne erst ab Folgetag verwendet.",
    )


def dividends(bundle):
    """Show dividend growth alongside earnings and FCF payout coverage."""
    payouts = dates(bundle["dividends"])
    close = bundle["prices"]["MSFT"].Close.tail(1260)
    payout = (
        payouts.reindex(payouts.index.union(close.index))
        .sort_index()
        .ffill()
        .reindex(close.index)
    )
    cash = statement(bundle, "cash", ["Cash Dividends Paid", "Free Cash Flow"])
    income = statement(bundle, "income", ["Net Income"])
    coverage = pd.DataFrame(
        {
            "vom Gewinn": cash["Cash Dividends Paid"].abs()
            / income["Net Income"]
            * 100,
            "vom FCF": cash["Cash Dividends Paid"].abs() / cash["Free Cash Flow"] * 100,
        }
    ).dropna(how="all")
    fig, axes = figure(
        "Microsoft: Wächst die Dividende nachhaltig?",
        "USD je Aktie am Ex-Tag · tatsächliche TTM-Rendite · jährliche Ausschüttungsquoten",
        rows=3,
        height=10.5,
    )
    axes[0].step(payout.index, payout, where="post", color=COLORS[1])
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x, 2)))
    axes[0].set_ylabel("USD / Quartal")
    time_axis(axes[0])
    lines(
        axes[1],
        dividend_yield(payouts, close).to_frame("Rendite TTM"),
        pct=True,
        direct=True,
    )
    lines(axes[2], coverage, pct=True)
    axes[2].set_ylabel("Ausschüttungsquote")
    return finish(
        fig,
        "14_dividends",
        bundle,
        "TTM-Rendite nutzt ein Kalenderjahr; verschobene Ex-Tage können kurzzeitig drei/fünf Zahlungen einschließen. Quoten nutzen Gesamtdividenden, nicht die Quartalsrate × 4.",
    )


def analyst_snapshot(bundle):
    """Render target dispersion and recommendation proportions compactly."""
    targets = bundle["targets"]
    rec = bundle["recommendations"].copy()
    rec["m"] = rec.period.str.removesuffix("m").astype(int)
    rec = rec.sort_values("m")
    fig, (left, right) = figure(
        "Analysten: Welche Erwartungen sind im Umlauf?",
        "USD · aktuelle Zielspanne ist kein Konfidenzintervall · Ratings als Anteile",
        cols=2,
        height=6.8,
    )
    left.hlines(0.5, targets["low"], targets["high"], color=MUTED, lw=4)
    left.scatter([targets["median"]], [0.5], color=COLORS[0], s=70, zorder=3)
    left.axvline(targets["current"], color=COLORS[1], lw=1.5)
    for key, y in [("low", 0.35), ("high", 0.35), ("median", 0.67), ("current", 0.15)]:
        label = {
            "low": "Minimum",
            "high": "Maximum",
            "median": "Median",
            "current": "Kurs",
        }[key]
        left.text(
            targets[key],
            y,
            f"{label}\n{number(targets[key],0)}",
            ha="center",
            fontsize=9,
        )
    left.set_ylim(0, 1)
    left.set_yticks([])
    left.set_xlabel("USD")
    upside = (targets["median"] / targets["current"] - 1) * 100
    left.set_title(f"Median {percent(upside)} über aktuellem Kurs", fontsize=10)
    columns = ["strongBuy", "buy", "hold", "sell", "strongSell"]
    labels = ["Stark kaufen", "Kaufen", "Halten", "Verkaufen", "Stark verkaufen"]
    totals = rec[columns].sum(axis=1)
    bottom = np.zeros(len(rec))
    for key, label, color in zip(
        columns, labels, [COLORS[0], "#456F4D", "#879387", "#AD735B", DOWN]
    ):
        value = rec[key] / totals * 100
        right.bar(range(len(rec)), value, bottom=bottom, color=color, label=label)
        bottom += value.to_numpy()
    right.set_xticks(
        range(len(rec)),
        [
            ("Aktuell" if m == 0 else f"vor {abs(m)} Mon.") + f"\nn={n}"
            for m, n in zip(rec.m, totals)
        ],
    )
    right.set_ylim(0, 100)
    right.yaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v)))
    right.legend(loc="upper center", bbox_to_anchor=(0.5, 1.20), ncol=3, fontsize=8)
    return finish(
        fig,
        "15_analysts",
        bundle,
        "Kursziele sind Meinungen, keine eigene Unternehmensbewertung. Rating-Anzahl entspricht nicht zwingend der Anzahl von Kurszielschätzungen; Zielhorizonte können variieren.",
    )


def target_actions(bundle):
    """Show latest analyst revisions, avoiding a dense cloud of targets."""
    actions = dates(bundle["actions"])
    data = (
        actions.loc[(actions.currentPriceTarget > 0) & (actions.priorPriceTarget > 0)]
        .tail(12)
        .copy()
    )
    fig, (ax,) = figure(
        "Was haben Analysten zuletzt an ihren Kurszielen geändert?",
        "Letzte 12 Meldungen mit altem und neuem Ziel · USD · keine Konsenshistorie",
        height=8,
    )
    fig.subplots_adjust(left=0.30, right=0.88)
    for i, (_, row) in enumerate(data.iterrows()):
        old, new = row["priorPriceTarget"], row["currentPriceTarget"]
        color = UP if new >= old else DOWN
        ax.plot([old, new], [i, i], color=color, lw=3)
        ax.scatter(old, i, color=MUTED, s=25)
        ax.scatter(new, i, color=color, s=45)
        ax.annotate(
            f"{number(old,0)} → {number(new,0)}",
            (max(old, new), i),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
        )
    ax.set_yticks(
        range(len(data)),
        [f"{d:%d.%m.%y} · {str(f)[:25]}" for d, f in zip(data.index, data.Firm)],
    )
    ax.invert_yaxis()
    ax.set_xlabel("Kursziel in USD")
    ax.grid(False, axis="y")
    ax.grid(True, axis="x")
    ax.margins(x=0.2)
    return finish(
        fig,
        "16_price_targets",
        bundle,
        "Grauer Punkt: vorheriges Ziel. Farbiger Punkt: neues Ziel. In der Galerie sind alle verfügbaren Meldungen nach Analyst filterbar.",
    )


def insider_activity(bundle):
    """Summarize purchases and sales separately from gifts and unknown values."""
    data = bundle["insiders"].copy()
    data["date"] = (
        pd.to_datetime(data["Start Date"]).dt.tz_localize(None).dt.normalize()
    )
    end = bundle["prices"]["MSFT"].index[-1]
    data = data.loc[data.date.between(end - pd.DateOffset(years=1), end)]
    text = data.Text.fillna("")
    data["kind"] = np.where(
        text.str.startswith("Sale"),
        "Verkäufe",
        np.where(text.str.startswith("Purchase"), "Käufe", "Sonstige"),
    )
    known = data.loc[(data.Value > 0) & data.kind.isin(["Verkäufe", "Käufe"])]
    table = (
        known.pivot_table(index="date", columns="kind", values="Value", aggfunc="sum")
        .resample("ME")
        .sum(min_count=1)
        .fillna(0)
        / 1e6
    )
    fig, (ax,) = figure(
        "Insider: Käufe und Verkäufe im zeitlichen Kontext",
        f"Microsoft · gemeldete Transaktionen bis {end:%d.%m.%Y} · Mio. USD",
        height=7,
    )
    bars(ax, table, labels=[d.strftime("%m/%y") for d in table.index])
    return finish(
        fig,
        "17_insiders",
        bundle,
        f"{(data.Value.fillna(0)<=0).sum()} Meldungen ohne positiven Wert separat in der Tabelle. Keine Aussage über Verkaufspläne, Steuern oder Restbeteiligung; Verkäufe allein sind kein Negativsignal.",
    )


def holders(bundle):
    """Keep ownership percentages and reported changes in separate columns."""
    data = (
        bundle["holders"].dropna(subset=["Holder", "pctHeld"]).nlargest(10, "pctHeld")
    )
    fig, (ax,) = figure(
        "Wer hält Microsoft? Gemeldete institutionelle Bestände",
        "Anteil am Unternehmen und relative Bestandsänderung sind unterschiedliche Größen",
        height=7.8,
    )
    ax.set_axis_off()
    rows = [
        [
            str(row.Holder),
            percent(row.pctHeld * 100),
            ("+" if row.pctChange >= 0 else "") + percent(row.pctChange * 100),
            pd.Timestamp(row["Date Reported"]).strftime("%d.%m.%Y"),
        ]
        for _, row in data.iterrows()
    ]
    table = ax.table(
        cellText=rows,
        colLabels=["Institution", "Anteil", "Bestandsänderung", "Meldestichtag"],
        colWidths=[0.49, 0.13, 0.20, 0.18],
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 2)
    for (r, c), cell in table.get_celld().items():
        cell.set_facecolor("#263029" if r == 0 else "#161A17")
        cell.set_edgecolor(GRID)
        cell.get_text().set_color(INK)
    return finish(
        fig,
        "18_holders",
        bundle,
        "Bestandsänderung gegenüber dem Vorbericht, keine Prozentpunkte am Unternehmen. Institutionen können Indexfonds sein. Meldestichtag ist nicht Abrufdatum.",
    )


def option_volatility(bundle):
    """Plot only reasonably liquid, recent call quotes, with visible exclusions."""
    now = pd.Timestamp(bundle["retrieved_at"])
    spot = bundle["prices"]["MSFT"].Close.iloc[-1]
    fig, (ax,) = figure(
        "Optionen: Wie teuer ist erwartete Kursschwankung?",
        f"Microsoft Calls · USD · Schlusskurs {number(spot,2)} · IV annualisiert",
    )
    counts = []
    total = 0
    for color, (expiry, raw) in zip(COLORS, bundle["options"].items()):
        valid = valid_calls(raw, spot, now)
        total += len(valid)
        days = (pd.Timestamp(expiry) - now.tz_localize(None).normalize()).days
        counts.append(f"{days} Tage: {len(valid)}/{len(raw)}")
        # Scatter avoids falsely implying smooth or executable interpolation across missing strikes.
        ax.scatter(
            valid.strike / spot,
            valid.impliedVolatility * 100,
            color=color,
            s=25,
            label=f"{expiry} · {days} Tage",
        )
    if total == 0:
        ax.text(
            0.5,
            0.5,
            "Keine Quotes erfüllen die Qualitätsfilter",
            transform=ax.transAxes,
            ha="center",
        )
    ax.axvline(1, color=MUTED, ls=":")
    ax.set_xlabel("Strike / letzter Aktienkurs (1,0 = am Geld)")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: number(v, 2)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: percent(v)))
    ax.legend()
    return finish(
        fig,
        "19_implied_vol",
        bundle,
        "Bid > 0; Ask ≥ Bid; Spread/Mitte ≤ 20 %; OI ≥ 10; letzter Trade ≤ 3 Tage. Verbleibend: "
        + ", ".join(counts)
        + ". Trade-Alter garantiert keine aktuelle Quote.",
    )
