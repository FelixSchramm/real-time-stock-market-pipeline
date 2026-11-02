"""Business economics, balance-sheet quality and transparent valuation scenarios."""

import numpy as np
import pandas as pd
from calculations import equity_value, implied_growth, roic, trailing_four
from data import ROOT, statement
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from theme import (
    COLORS,
    DOWN,
    INK,
    MUTED,
    VALUE_COLORS,
    VALUE_TEXT,
    bars,
    figure,
    finish,
    lines,
    number,
    percent,
)

CF = ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"]
CF_NAMES = dict(zip(CF, ["Operativer CF", "Capex (Abfluss)", "Free Cashflow"]))


def cashflows(bundle, quarterly=False):
    """Show operating cash generation, cash investment and residual cash flow.

    :param bundle: fetched snapshot
    :param quarterly: quarterly/TTM instead of annual/intensity view
    :return: PNG path
    """
    data = statement(bundle, "quarter_cash" if quarterly else "cash", CF).dropna()
    data["Capital Expenditure"] = data["Capital Expenditure"].abs()
    # Validate vendor FCF rather than silently displaying incompatible line items.
    if not np.allclose(
        data["Operating Cash Flow"] - data["Capital Expenditure"],
        data["Free Cash Flow"],
        rtol=0.002,
        atol=1e6,
    ):
        raise ValueError("Reported FCF does not reconcile to CFO minus cash capex")
    fig, (top, bottom) = figure(
        "Microsoft: Wie viel vom Cashflow bleibt übrig?",
        "Mrd. USD · operativer Cashflow − Cash-Capex = Free Cashflow · Geschäftsjahresende Juni",
        rows=2,
        height=8.5,
    )
    bars(top, data.rename(columns=CF_NAMES) / 1e9)
    if quarterly:
        rolling = trailing_four(data).dropna()
        lines(bottom, rolling.rename(columns=CF_NAMES) / 1e9)
        bottom.set_ylabel("TTM · Mrd. USD")
        note = "Oben: einzelne Quartale. Unten: vier lückenlos aufeinanderfolgende Quartale. Keine langfristige Aussage aus fünf Quartalen; saisonale Effekte beachten."
        name = "03_cashflow_quarterly"
    else:
        revenue = statement(bundle, "income", ["Total Revenue"])["Total Revenue"]
        intensity = pd.DataFrame(
            {
                "Capex / Umsatz": data["Capital Expenditure"] / revenue * 100,
                "FCF / Umsatz": data["Free Cash Flow"] / revenue * 100,
            }
        ).dropna(how="all")
        lines(bottom, intensity, pct=True)
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        change = (latest["Free Cash Flow"] / previous["Free Cash Flow"] - 1) * 100
        note = f'Letzter Jahres-FCF: {number(latest["Free Cash Flow"]/1e9)} Mrd. USD ({percent(change)} zum Vorjahr). Cash-Capex trennt Erhaltungs- und Wachstumsinvestitionen nicht; Leasing separat prüfen.'
        name = "09_cashflow_annual"
    return finish(fig, name, bundle, note)


def income(bundle):
    """Render growth and profitability, separating annual and quarterly context."""
    columns = ["Total Revenue", "Net Income", "Operating Income", "Gross Profit"]
    annual = statement(bundle, "income", columns).dropna()
    quarter = statement(bundle, "quarter_income", columns).dropna()
    fig, axes = figure(
        "Microsoft: Wachstum, Margen und der Unterschied zum Vorjahr",
        "Mrd. USD und Prozent · Jahreszahlen links, Quartalsvergleich rechts · keine vermischten Perioden",
        rows=2,
        cols=2,
        height=9.4,
    )
    bars(
        axes[0],
        annual[["Total Revenue", "Net Income"]].rename(
            columns={"Total Revenue": "Umsatz", "Net Income": "Gewinn"}
        )
        / 1e9,
    )
    growth = annual["Total Revenue"].pct_change(fill_method=None) * 100
    axes[0].set_ylabel("Mrd. USD")
    for i, value in enumerate(growth):
        if np.isfinite(value):
            axes[0].text(
                i,
                annual["Total Revenue"].iloc[i] / 1e9 + 5,
                ("+" if value > 0 else "") + percent(value),
                ha="center",
                fontsize=8,
            )
    axes[0].margins(y=0.18)
    bars(
        axes[1],
        quarter[["Total Revenue", "Net Income"]].rename(
            columns={"Total Revenue": "Umsatz", "Net Income": "Gewinn"}
        )
        / 1e9,
    )
    for ax, frame in [(axes[2], annual), (axes[3], quarter)]:
        margins = (
            frame[["Gross Profit", "Operating Income", "Net Income"]].div(
                frame["Total Revenue"], axis=0
            )
            * 100
        )
        margins = margins.rename(
            columns={
                "Gross Profit": "Brutto",
                "Operating Income": "Operativ",
                "Net Income": "Netto",
            }
        )
        lines(ax, margins, pct=True)
    latest = quarter.iloc[-1]
    prior = quarter.reindex([quarter.index[-1] - pd.DateOffset(years=1)]).iloc[0]
    yoy = (latest["Total Revenue"] / prior["Total Revenue"] - 1) * 100
    return finish(
        fig,
        "10_income",
        bundle,
        f"Letztes Quartal: Umsatz {percent(yoy)} gegenüber Vorjahresquartal. Nettomargen enthalten Steuern und nichtoperative Effekte; die Ursachen müssen im Geschäftsbericht geprüft werden.",
    )


def balance_sheet(bundle):
    """Compare debt, liquid resources and coverage with consistent definitions."""
    data = statement(
        bundle,
        "balance",
        [
            "Total Debt",
            "Cash Cash Equivalents And Short Term Investments",
            "Capital Lease Obligations",
        ],
    ).dropna(subset=["Total Debt", "Cash Cash Equivalents And Short Term Investments"])
    inc = statement(bundle, "income", ["Operating Income", "Interest Expense"])
    coverage = inc["Operating Income"] / inc["Interest Expense"].where(
        inc["Interest Expense"] > 0
    )
    fig, (top, bottom) = figure(
        "Microsoft: Wie belastbar ist die Bilanz?",
        "Mrd. USD · Schulden versus Cash und kurzfristige Anlagen · Zinsdeckung separat",
        rows=2,
        height=8.5,
    )
    values = (
        data[["Total Debt", "Cash Cash Equivalents And Short Term Investments"]].rename(
            columns={
                "Total Debt": "Gesamtschulden (Yahoo)",
                "Cash Cash Equivalents And Short Term Investments": "Cash + kurzfristige Anlagen",
            }
        )
        / 1e9
    )
    bars(top, values)
    lines(bottom, coverage.to_frame("Operatives Ergebnis / Zinsaufwand"))
    bottom.set_ylabel("Zinsdeckung (×)")
    net = (
        data["Total Debt"] - data["Cash Cash Equivalents And Short Term Investments"]
    ).iloc[-1] / 1e9
    leases = data["Capital Lease Obligations"].iloc[-1] / 1e9
    return finish(
        fig,
        "20_balance_sheet",
        bundle,
        f"Letzter Nettofinanzschulden-Proxy: {number(net)} Mrd. USD. Separat gemeldete Finanzierungsleasing-Verpflichtungen: {number(leases)} Mrd. USD; nicht nochmals addiert. Fälligkeiten und Covenants fehlen.",
    )


def returns_on_capital(bundle):
    """Show transparently calculated ROIC alongside investment intensity."""
    inc = statement(
        bundle,
        "income",
        [
            "Operating Income",
            "Tax Provision",
            "Pretax Income",
            "Total Revenue",
            "Research And Development",
        ],
    )
    cap = statement(bundle, "balance", ["Invested Capital"])["Invested Capital"]
    values = roic(inc, cap)
    cf = statement(bundle, "cash", ["Capital Expenditure"])
    fig, (top, bottom) = figure(
        "Microsoft: Welche Rendite erzielt eingesetztes Kapital?",
        "ROIC = operativer Gewinn nach berichteten Steuern / durchschnittliches investiertes Kapital",
        rows=2,
        height=8.4,
    )
    lines(top, values.dropna().to_frame("ROIC"), pct=True, direct=True)
    ratios = pd.DataFrame(
        {
            "Cash-Capex / Umsatz": cf["Capital Expenditure"].abs()
            / inc["Total Revenue"]
            * 100,
            "F&E / Umsatz": inc["Research And Development"]
            / inc["Total Revenue"]
            * 100,
        }
    ).dropna(how="all")
    lines(bottom, ratios, pct=True)
    return finish(
        fig,
        "21_roic",
        bundle,
        "Yahoo Invested Capital inkl. Goodwill; Durchschnitt aus Jahresanfang/-ende. Effektivsteuer aus Tax Provision/Pretax Income. Keine F&E-Aktivierung, keine universelle Gut/Schlecht-Schwelle.",
    )


def cash_quality(bundle):
    """Separate cash conversion from stock compensation and working capital."""
    cf = statement(
        bundle,
        "cash",
        [
            "Operating Cash Flow",
            "Free Cash Flow",
            "Stock Based Compensation",
            "Change In Working Capital",
        ],
    )
    inc = statement(bundle, "income", ["Net Income", "Total Revenue"])
    amount = (
        pd.DataFrame(
            {
                "Nettogewinn": inc["Net Income"],
                "Operativer CF": cf["Operating Cash Flow"],
                "FCF": cf["Free Cash Flow"],
            }
        ).dropna()
        / 1e9
    )
    fig, (top, bottom) = figure(
        "Wie viel vom ausgewiesenen Gewinn wird zu Cash?",
        "Jahreswerte · Mrd. USD oben · Cashflow-Treiber in % vom Umsatz unten",
        rows=2,
        height=8.5,
    )
    bars(top, amount)
    ratios = pd.DataFrame(
        {
            "Aktienvergütung / Umsatz": cf["Stock Based Compensation"]
            / inc["Total Revenue"]
            * 100,
            "Working-Capital-Cash-Effekt / Umsatz": cf["Change In Working Capital"]
            / inc["Total Revenue"]
            * 100,
        }
    ).dropna(how="all")
    lines(bottom, ratios, pct=True)
    bottom.axhline(0, color=MUTED, lw=0.7)
    return finish(
        fig,
        "22_cash_quality",
        bundle,
        "Aktienvergütung erhöht als nichtzahlungswirksamer Aufwand den operativen Cashflow, hat aber wirtschaftliche Kosten. Sie wird hier gezeigt, nicht pauschal doppelt von Gewinn und FCF abgezogen.",
    )


def capital_allocation(bundle):
    """Compare discretionary uses with FCF and show debt funding separately."""
    cf = statement(
        bundle,
        "cash",
        [
            "Free Cash Flow",
            "Repurchase Of Capital Stock",
            "Cash Dividends Paid",
            "Purchase Of Business",
            "Issuance Of Debt",
            "Repayment Of Debt",
        ],
    )
    uses = (
        cf[
            [
                "Repurchase Of Capital Stock",
                "Cash Dividends Paid",
                "Purchase Of Business",
            ]
        ]
        .abs()
        .rename(
            columns={
                "Repurchase Of Capital Stock": "Rückkäufe",
                "Cash Dividends Paid": "Dividenden",
                "Purchase Of Business": "Unternehmenskäufe",
            }
        )
        / 1e9
    )
    fig, (top, bottom) = figure(
        "Wofür setzt Microsoft das verfügbare Kapital ein?",
        "Mrd. USD je Geschäftsjahr · FCF bereits nach Cash-Capex · Finanzierung separat",
        rows=2,
        height=8.6,
    )
    bars(top, uses, stacked=True)
    top.plot(
        range(len(cf)),
        cf["Free Cash Flow"] / 1e9,
        color=INK,
        marker="o",
        label="FCF nach Capex",
    )
    top.legend(loc="upper left", bbox_to_anchor=(0, 1.18), ncol=4, fontsize=8)
    bars(
        bottom,
        cf[["Issuance Of Debt", "Repayment Of Debt"]]
        .abs()
        .rename(
            columns={
                "Issuance Of Debt": "Schuldenaufnahme",
                "Repayment Of Debt": "Tilgung",
            }
        )
        / 1e9,
    )
    return finish(
        fig,
        "23_capital_allocation",
        bundle,
        "Bruttozahlungen; keine vollständige Cashflow-Überleitung. Verwendungen über FCF können aus vorhandener Liquidität, Verkäufen oder Finanzierung stammen. Rückkäufe gemeinsam mit Verwässerung beurteilen.",
    )


def per_share(bundle):
    """Show diluted share count and shareholder-level earnings/cash economics."""
    inc = statement(
        bundle, "income", ["Diluted Average Shares", "Net Income", "Diluted EPS"]
    ).dropna()
    cf = statement(bundle, "cash", ["Free Cash Flow"])
    fcf_per_share = cf["Free Cash Flow"] / inc["Diluted Average Shares"]
    indexed = (
        inc[["Net Income", "Diluted EPS"]].div(
            inc[["Net Income", "Diluted EPS"]].iloc[0]
        )
        * 100
    )
    indexed = indexed.rename(
        columns={"Net Income": "Nettogewinn", "Diluted EPS": "Verwässertes EPS"}
    )
    fig, axes = figure(
        "Wächst auch der Wert je Aktie?",
        "Verwässerte durchschnittliche Aktienanzahl · Gewinnwachstum · USD je verwässerter Aktie",
        rows=3,
        height=10.4,
    )
    lines(
        axes[0],
        (inc["Diluted Average Shares"] / 1e6).to_frame("Aktien (Mio.)"),
        direct=True,
    )
    lines(axes[1], indexed)
    axes[1].set_ylabel("Erstes Jahr = 100")
    lines(
        axes[2],
        pd.DataFrame(
            {"Diluted EPS": inc["Diluted EPS"], "FCF je Aktie": fcf_per_share}
        ).dropna(how="all"),
    )
    return finish(
        fig,
        "24_per_share",
        bundle,
        "Periodendurchschnittliche verwässerte Aktien, keine Stichtags-Aktienzahl. FCF je Aktie ist ein eigener Proxy. Rückkäufe können Aktienvergütung kompensieren, ohne die Aktienanzahl stark zu senken.",
    )


def estimates(bundle):
    """Show forward ranges and changes to the same fiscal-period EPS estimate."""
    eps = bundle["estimates"].loc[["0y", "+1y"]]
    rev = bundle["revenue_estimates"].loc[["0y", "+1y"]]
    trend = bundle["eps_trend"].loc[["0y", "+1y"]]
    now = pd.Timestamp(bundle["retrieved_at"]).tz_localize(None)
    current_fy = now.year + (now.month > 6)
    labels = [f"GJ {current_fy}", f"GJ {current_fy+1}"]
    fig, axes = figure(
        "Welche Erwartungen steigen oder fallen?",
        "Konsens-Schätzungen für zwei Geschäftsjahre · Spannen sind keine Wahrscheinlichkeitsintervalle",
        rows=2,
        cols=2,
        height=9,
    )
    for ax, frame, scale, title in [
        (axes[0], eps, 1, "EPS · USD"),
        (axes[1], rev, 1e9, "Umsatz · Mrd. USD"),
    ]:
        for i, (_, row) in enumerate(frame.iterrows()):
            avg = row["avg"] / scale
            low = row["low"] / scale
            high = row["high"] / scale
            ax.vlines(i, low, high, color=COLORS[i], lw=4)
            ax.scatter(i, avg, color=COLORS[i], s=55, zorder=3)
            ax.annotate(
                f"{number(avg)}\nn={int(row.numberOfAnalysts)}",
                (i, high),
                xytext=(0, 9),
                textcoords="offset points",
                ha="center",
                fontsize=9,
            )
        ax.set_xticks([0, 1], labels)
        ax.set_xlim(-0.5, 1.5)
        ax.margins(y=0.35)
        ax.set_title(title, fontsize=10)
    fields = ["90daysAgo", "60daysAgo", "30daysAgo", "7daysAgo", "current"]
    for i, (period, row) in enumerate(trend.iterrows()):
        values = row.reindex(fields).astype(float)
        axes[2].plot(
            [-90, -60, -30, -7, 0],
            values.to_numpy(),
            color=COLORS[i],
            marker="o",
            label=labels[i],
        )
    axes[2].set_xticks([-90, -60, -30, -7, 0])
    axes[2].set_xlabel("Tage vor aktuellem Snapshot")
    axes[2].set_ylabel("EPS-Schätzung (USD)")
    axes[2].legend()
    revisions = bundle["eps_revisions"].reindex(["0y", "+1y"])
    x = np.arange(2)
    axes[3].bar(
        x - 0.18, revisions.upLast30days, width=0.35, color=COLORS[0], label="Angehoben"
    )
    axes[3].bar(
        x + 0.18, revisions.downLast30days, width=0.35, color=DOWN, label="Gesenkt"
    )
    axes[3].set_xticks(x, labels)
    axes[3].set_title("Revisionen in den letzten 30 Tagen", fontsize=10)
    axes[3].legend()
    return finish(
        fig,
        "25_estimates",
        bundle,
        "Rückblicke stammen aus dem aktuellen Yahoo-Snapshot, nicht aus einer selbst archivierten täglichen Historie. Geschäftsjahr Juni; Prognosen können sich ändern. Keine Mischung mit bereits berichteten Jahreswerten.",
    )


def valuation(bundle):
    """Compare provider multiples through time without interpreting median as value."""
    source = bundle["valuation"]
    names = ["Trailing P/E", "Forward P/E", "Enterprise Value/EBITDA"]
    fig, axes = figure(
        "Bewertung: Gewinnbasis und Zeitraum machen einen Unterschied",
        "Yahoo-Bewertungskennzahlen · historische Stichtage plus aktueller Snapshot · Vielfache",
        rows=3,
        height=10.2,
    )
    for ax, name in zip(axes, names):
        row = source.loc[name]
        history = row.drop(labels="Current")
        history.index = pd.to_datetime(history.index)
        history = history.sort_index()
        series = pd.concat(
            [
                history,
                pd.Series(
                    [row["Current"]],
                    index=[
                        pd.Timestamp(bundle["retrieved_at"])
                        .tz_localize(None)
                        .normalize()
                    ],
                ),
            ]
        )
        lines(
            ax,
            series.to_frame(
                {
                    "Trailing P/E": "KGV TTM",
                    "Forward P/E": "KGV Forward",
                    "Enterprise Value/EBITDA": "EV/EBITDA",
                }[name]
            ),
            direct=True,
        )
        ax.set_ylabel("×")
    return finish(
        fig,
        "26_valuation",
        bundle,
        "Portal-KGV kann vom rekonstruierten Earnings-KGV abweichen. Forward P/E enthält Analystenschätzungen. EV/EBITDA berücksichtigt keine Cash-Investitionen; deshalb immer zusammen mit Capex und FCF lesen.",
    )


def reverse_dcf(bundle):
    """Show implied cash-flow growth and sensitivity, not a single fair-price target."""
    cf = statement(bundle, "cash", ["Free Cash Flow"]).dropna()
    fcf = cf["Free Cash Flow"].iloc[-1]
    info = bundle["info"]
    market_cap = info["marketCap"]
    shares = info["sharesOutstanding"]
    spot = bundle["prices"]["MSFT"].Close.iloc[-1]
    # Market capitalization, price and share count must describe compatible snapshots.
    if abs(market_cap / (shares * spot) - 1) > 0.05:
        raise ValueError(
            "Price, shares and market capitalization do not reconcile within 5%"
        )
    rates = np.array([0.08, 0.09, 0.10, 0.11, 0.12])
    growths = np.array([0, 0.05, 0.10, 0.15, 0.20, 0.25])
    value = np.array(
        [[equity_value(fcf, g, r) / shares for g in growths] for r in rates]
    )
    required = np.array([implied_growth(fcf, market_cap, r) * 100 for r in rates])
    fig, (left, right) = figure(
        "Welche Cashflow-Erwartung steckt im aktuellen Preis?",
        f"FCF-Basis GJ {cf.index[-1].year}: {number(fcf/1e9)} Mrd. USD · 10 Jahre Wachstum, danach 2,5 % · konstante Aktienanzahl",
        cols=2,
        height=7.6,
    )
    fig.subplots_adjust(right=0.94, wspace=0.42)
    ratio = (value / spot - 1) * 100
    limit = max(1, np.nanmax(np.abs(ratio)))
    left.imshow(
        ratio,
        cmap=LinearSegmentedColormap.from_list("ci_diverging", VALUE_COLORS),
        norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit),
        aspect="auto",
    )
    for (r, c), v in np.ndenumerate(value):
        left.text(
            c,
            r,
            number(v, 0),
            ha="center",
            va="center",
            fontsize=9,
            color=VALUE_TEXT,
        )
    left.set_xticks(
        range(len(growths)), [percent(g * 100) for g in growths], rotation=30
    )
    left.set_yticks(range(len(rates)), [percent(r * 100) for r in rates])
    left.grid(False)
    left.set_xlabel("FCF-Wachstum p. a.")
    left.set_ylabel("Geforderte Eigenkapitalrendite")
    left.set_title(f"Szenariowert USD/Aktie · Kurs {number(spot,2)}", fontsize=10)
    right.plot(rates * 100, required, color=COLORS[1], marker="o")
    for r, g in zip(rates, required):
        right.annotate(
            percent(g),
            (r * 100, g),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )
    right.set_xlabel("Geforderte Eigenkapitalrendite (%)")
    right.set_ylabel("Impliziertes FCF-Wachstum p. a. (%)")
    right.margins(y=0.25)
    return finish(
        fig,
        "27_reverse_dcf",
        bundle,
        "Modellannahmen, keine Prognose: CFO−Cash-Capex als vereinfachter Eigenkapital-CF-Proxy, kein Owner Earnings. Kein zusätzlicher Netto-Schuldenabzug. Keine neue Verschuldung/Verwässerung modelliert; Endwert sehr sensitiv.",
    )


def segments(bundle):
    """Render sourced segment economics without inventing unavailable Azure revenue."""
    data = pd.read_csv(ROOT / "segments.csv")
    revenue = (
        data.pivot(index="year", columns="segment", values="revenue_million_usd") / 1000
    )
    operating = (
        data.pivot(
            index="year", columns="segment", values="operating_income_million_usd"
        )
        / 1000
    )
    order = [
        "Productivity & Business Processes",
        "Intelligent Cloud",
        "More Personal Computing",
    ]
    revenue = revenue[order]
    operating = operating[order]
    fig, (top, bottom) = figure(
        "Microsoft: Welche Geschäfte tragen Umsatz und Ergebnis?",
        "Berichtete Segmente · Mrd. USD · GJ 2024–2026 · identische Abgrenzung aus Bericht 2026",
        rows=2,
        height=8.8,
    )
    short = {
        "Productivity & Business Processes": "Produktivität & Geschäftsprozesse",
        "Intelligent Cloud": "Intelligent Cloud",
        "More Personal Computing": "Personal Computing",
    }
    revenue = revenue.rename(columns=short)
    operating = operating.rename(columns=short)
    bars(top, revenue, labels=[f"GJ {y}" for y in revenue.index], stacked=True)
    top.set_ylabel("Umsatz (Mrd. USD)")
    bars(bottom, operating, labels=[f"GJ {y}" for y in operating.index], stacked=True)
    bottom.set_ylabel("Operatives Ergebnis (Mrd. USD)")
    return finish(
        fig,
        "28_segments",
        bundle,
        "Azure ist Teil von Intelligent Cloud, kein separat ausgewiesener Umsatz. Microsoft Cloud überschneidet mehrere Segmente und wird nicht addiert. Wettbewerbshypothesen und Quellen: research.md.",
        source="Microsoft Annual Report 2026 · Note 18",
    )


def cash_bridge(bundle):
    """Explain the latest annual operating-cash-flow to free-cash-flow bridge."""
    cf = statement(bundle, "cash", CF).dropna().iloc[-1] / 1e9
    cfo = cf["Operating Cash Flow"]
    capex = abs(cf["Capital Expenditure"])
    fcf = cf["Free Cash Flow"]
    fig, (ax,) = figure(
        "Vom operativen Cashflow zum verfügbaren Free Cashflow",
        "Letztes vollständiges Geschäftsjahr · Mrd. USD · Cash-Capex als Mittelabfluss",
    )
    ax.bar(
        [0, 1, 2],
        [cfo, capex, fcf],
        bottom=[0, fcf, 0],
        color=[COLORS[0], DOWN, COLORS[2]],
        width=0.6,
    )
    ax.plot([0.3, 0.7], [cfo, cfo], color=MUTED, ls=":")
    ax.plot([1.3, 1.7], [fcf, fcf], color=MUTED, ls=":")
    for i, y, label in [
        (0, cfo, number(cfo)),
        (1, cfo, "−" + number(capex)),
        (2, fcf, number(fcf)),
    ]:
        ax.annotate(
            label,
            (i, y),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=13,
        )
    ax.set_xticks([0, 1, 2], ["Operativer Cashflow", "Cash-Capex", "Free Cashflow"])
    ax.margins(y=0.2)
    return finish(
        fig,
        "29_cash_bridge",
        bundle,
        "FCF steht vor Dividenden und Rückkäufen. Die Grafik erklärt Zahlungsströme; sie beweist weder die Rentabilität der Investitionen noch die Höhe nachhaltiger Owner Earnings.",
    )
