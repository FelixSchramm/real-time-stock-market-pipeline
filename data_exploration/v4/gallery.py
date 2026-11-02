"""Build a local, mobile-readable before/after gallery and GitHub image catalog."""

import html
import json

import pandas as pd
from data import ROOT, dates
from theme import number

# Each legacy theme has a preserved counterpart; new business views are marked as new.
CATALOG = {
    "01": (
        "Kurs ohne Ereignisse",
        "v3_dark/01_price_eur.png",
        "Explizit unbereinigter EUR-Kurs; zusammen mit 02 als ein-/ausblendbare Ansicht.",
    ),
    "02": (
        "Kurs und Quartalsergebnisse",
        "v3_dark/02_price_earnings.png",
        "EPS über/unter Schätzung statt missverständlichem EPS-Wachstum; Zeitpunkt nach Börsenschluss.",
    ),
    "03": (
        "Cashflow je Quartal",
        "v3_dark/03_cashflow.png",
        "Quartalswerte plus rollierende Zwölfmonatssumme; keine Überbrückung fehlender Quartale.",
    ),
    "04": (
        "Kerzen und Volumen",
        "v3_dark/04_candles.png",
        "Öffnung/Schluss korrekt erklärt, eigenes Volumenpanel und eindeutiger Zeitraum.",
    ),
    "05": (
        "Aktienvergleich",
        "v3_dark/05_indexed.png",
        "Einheitliche Währung, Renditeart und Start-/Endtage; Verbindungslinien zu Endlabels.",
    ),
    "06": (
        "Monatsrenditen",
        "v3_dark/06_monthly_returns.png",
        "Sichtbare Farbskala, Währung und Renditedefinition; ausschließlich vollständige Monate.",
    ),
    "07": (
        "Drawdown",
        "v3_dark/07_drawdown.png",
        "Hoch aus zehnjähriger Vorgeschichte; kein künstlicher Neustart am linken Bildrand.",
    ),
    "08": (
        "Rendite und Kursrisiko",
        "v3_dark/08_kpi_tiles.png",
        "2×2-Anordnung, vergleichbare Zeiträume und Zeit unter dem Hoch; nominalen Aktienkurs entfernt.",
    ),
    "09": (
        "Cashflow und Investitionen",
        "04_cashflow_annual.png",
        "Cashflow-Gleichung, Capex-Intensität, FCF-Marge und Vorjahresveränderung.",
    ),
    "10": (
        "Wachstum und Margen",
        "05_income.png",
        "Jahres- und Quartalsansicht, Bruttomarge sowie Umsatzwachstum gegenüber Vorjahr.",
    ),
    "11": (
        "Reaktion auf Quartalszahlen",
        "06_earnings_reaction.png",
        "Marktbereinigte Reaktion neben Aktienrendite; Korrelation als Beschreibung, nicht Prognose.",
    ),
    "12": (
        "Historisches KGV",
        "07_pe_ratio.png",
        "Gewinnbasis und Look-ahead-Grenzen erklärt; Median ausdrücklich kein fairer Wert.",
    ),
    "13": (
        "Marktvergleich",
        "08_benchmark.png",
        "Gleicher Zeitraum wie Aktienvergleich; Wahl der Renditeart und zusätzliche Renditedifferenz.",
    ),
    "14": (
        "Dividende und Deckung",
        "09_dividends.png",
        "Dezimalachse repariert; Gewinn- und FCF-Ausschüttungsquote ergänzt.",
    ),
    "15": (
        "Analysten-Konsens",
        "10_analysts.png",
        "Median-Abstand zum Kurs, Zielspanne und Rating-Anteile mit Anzahl.",
    ),
    "16": (
        "Kurszieländerungen",
        "11_price_targets.png",
        "Letzte zwölf Änderungen als Vorher/Nachher-Paare; vollständige filterbare Meldungstabelle.",
    ),
    "17": (
        "Insideraktivität",
        "12_insiders.png",
        "Monatliche Summen und einzelne Meldungen; unbekannte Werte und Schenkungen bleiben getrennt.",
    ),
    "18": (
        "Institutionelle Eigentümer",
        "13_holders.png",
        "Beteiligungsanteil, relative Bestandsänderung und Meldedatum in getrennten Spalten.",
    ),
    "19": (
        "Optionsvolatilität",
        "14_implied_vol.png",
        "Strengere Liquiditätsfilter, Bid/Ask-Prüfung und einzelne Quotes statt suggerierter glatter Kurven.",
    ),
    "20": (
        "Bilanz und Zinsdeckung",
        None,
        "Neu: Liquidität, Schulden, Finanzierungsleasing und Zinsdeckung.",
    ),
    "21": (
        "Kapitalrendite",
        None,
        "Neu: ROIC mit durchschnittlichem Kapital und dokumentierter Steuer-/Goodwill-Behandlung.",
    ),
    "22": (
        "Gewinnqualität",
        None,
        "Neu: Gewinn versus Cashflow, Working Capital und aktienbasierte Vergütung.",
    ),
    "23": (
        "Kapitalverwendung",
        None,
        "Neu: Rückkäufe, Dividenden und Akquisitionen gegenüber FCF; Finanzierung separat.",
    ),
    "24": (
        "Entwicklung je Aktie",
        None,
        "Neu: verwässerte Aktienzahl, Gewinn- versus EPS-Wachstum und FCF je Aktie.",
    ),
    "25": (
        "Schätzungen und Revisionen",
        None,
        "Neu: Gewinn-/Umsatzspannen, Analystenzahl und EPS-Revisionen für identische Zielperioden.",
    ),
    "26": (
        "Bewertungsmultiplikatoren",
        None,
        "Neu: historische und aktuelle Portal-Bewertungen mit klaren Gewinnbasen.",
    ),
    "27": (
        "Reverse DCF",
        None,
        "Neu: Welche Cashflow-Wachstumsrate setzt der heutige Preis unter verschiedenen Renditeannahmen voraus?",
    ),
    "28": (
        "Geschäftsmodell und Segmente",
        None,
        "Neu: Umsatz und operatives Ergebnis aus Microsoft Annual Report 2026, Note 18.",
    ),
    "29": (
        "Cashflow-Überleitung",
        None,
        "Neu: Wasserfall vom operativen Cashflow über Cash-Capex zum FCF.",
    ),
}
GROUPS = [
    (
        "geschaeft",
        "Geschäftsmodell und Ertragskraft",
        ["28", "10", "09", "29", "03", "22"],
    ),
    (
        "kapital",
        "Kapitalrendite, Management und Bilanz",
        ["21", "23", "24", "20", "14"],
    ),
    ("bewertung", "Erwartungen und Bewertung", ["25", "12", "26", "27"]),
    (
        "markt",
        "Ergänzung: Kurs und Markt",
        ["02", "05", "08", "13", "07", "06", "11", "04"],
    ),
    (
        "kontext",
        "Ergänzung: Analysten, Eigentümer und Optionen",
        ["15", "16", "17", "18", "19"],
    ),
]


def table(columns, rows, table_id=""):
    """Render an escaped, scrollable data table.

    :param columns: column labels
    :param rows: display strings
    :param table_id: optional DOM identifier
    :return: HTML fragment
    """
    head = "".join(f'<th scope="col">{html.escape(str(c))}</th>' for c in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>"
        for row in rows
    )
    return f'<div class="scroll" tabindex="0" role="region" aria-label="Datentabelle"><table id="{table_id}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def detail_tables(bundle):
    """Provide analyst filters and contextual insider details.

    :param bundle: source snapshot
    :return: chart-number to HTML mapping
    """
    actions = dates(bundle["actions"])
    end = bundle["prices"]["MSFT"].index[-1]
    actions = actions.loc[
        (actions.index.year == end.year) & (actions.currentPriceTarget > 0)
    ].sort_index(ascending=False)
    rows = [
        [
            d.strftime("%d.%m.%Y"),
            r.Firm,
            number(r.priorPriceTarget, 0),
            number(r.currentPriceTarget, 0),
            str(r.priceTargetAction),
        ]
        for d, r in actions.iterrows()
    ]
    firms = sorted(actions.Firm.dropna().unique())
    options = "".join(f"<option>{html.escape(f)}</option>" for f in firms)
    targets = (
        f'<details><summary>Alle {len(rows)} verfügbaren Meldungen im laufenden Jahr</summary><label>Analyst <select id="firm"><option value="">Alle</option>{options}</select></label>'
        + table(
            ["Datum", "Analyst", "Vorher USD", "Nachher USD", "Meldung"],
            rows,
            "target-table",
        )
        + "</details>"
    )
    trades = bundle["insiders"].copy()
    trades["date"] = pd.to_datetime(trades["Start Date"]).dt.tz_localize(None)
    trades = trades.loc[
        trades.date.between(end - pd.DateOffset(years=1), end)
    ].sort_values("date", ascending=False)
    rows = [
        [
            r.date.strftime("%d.%m.%Y"),
            r.Insider,
            r.Position,
            str(r.Text),
            number(r.Shares, 0),
            number(r.Value / 1e6, 2) if r.Value > 0 else "Wert fehlt / null",
        ]
        for _, r in trades.iterrows()
    ]
    insider = (
        f"<details><summary>Alle {len(rows)} gemeldeten Insidertransaktionen im Zeitraum</summary>"
        + table(
            ["Datum", "Person", "Funktion", "Transaktion", "Aktien", "Wert Mio. USD"],
            rows,
        )
        + "</details>"
    )
    return {"16": targets, "17": insider}


def build(bundle, manifest):
    """Write a standalone local gallery and a repository-native image comparison.

    :param bundle: fetched data for supplemental display tables
    :param manifest: chart paths and provenance
    :return: None
    """
    extras = detail_tables(bundle)
    sections = []
    markdown = [
        "# V4 – Unternehmensanalyse und Vorher-/Nachher-Vergleich\n",
        "Alle bisherigen Dateien bleiben erhalten. `baseline/` enthält zusätzlich eine byteidentische Kopie der ursprünglichen 67 Analyse- und Style-Dateien.\n",
        "[Interaktive Vergleichsgalerie](index.html) · [Geschäftsmodell und Quellen](research.md) · [Methodik](METHODS.md)\n",
        "**Galerie lokal öffnen:** Repository herunterladen/klonen und `data_exploration/v4/index.html` im Browser öffnen. GitHub zeigt HTML als Quelltext; die PNG-Vergleiche unten funktionieren direkt auf GitHub.\n",
        f'Datenabruf: **{manifest["retrieved_at"]}**. 29 Diagrammthemen, davon 19 überarbeitet und 10 ergänzt. 44 PNGs einschließlich EUR/USD- und Renditevarianten. Kein Live-Dashboard.\n',
        "## Reproduzieren\n\n```sh\npython -m pip install -r data_exploration/v4/requirements.txt\npython data_exploration/v4/generate.py --refresh\npython -m unittest discover -s tests -v\n```\n",
        "Ohne `--refresh` wird ein vorhandener lokaler Snapshot wiederverwendet. `.cache/` wird nicht committet. Die Segmenttabelle ist separat aus dem Geschäftsbericht belegt und wird nicht von Yahoo aktualisiert.\n",
    ]
    for group_id, title, keys in GROUPS:
        cards = []
        markdown.append(f"## {title}\n\n| Thema | Vorher | V4 |\n|---|---|---|\n")
        for key in keys:
            name, before, change = CATALOG[key]
            after = manifest["outputs"][key]
            previous = "baseline/data_exploration/" + before if before else None
            before_html = (
                f'<figure class="before"><figcaption>Vorher · unveränderte Definition und Zeitraum</figcaption><div class="scroll" tabindex="0" role="region" aria-label="Vorher: {html.escape(name)}"><a href="{previous}"><img loading="lazy" src="{previous}" alt="Vorher: {html.escape(name)}"></a></div></figure>'
                if previous
                else '<div class="before new">Neue Analyse – in der Ausgangsversion nicht vorhanden.</div>'
            )
            toggle = (
                '<label class="event-control"><input type="checkbox" id="events" checked> Quartalsergebnisse einblenden</label>'
                if key == "02"
                else ""
            )
            cards.append(
                f'<article id="chart-{key}"><h3>{html.escape(name)}</h3><p>{html.escape(change)}</p>{toggle}<div class="pair">{before_html}<figure><figcaption>V4</figcaption><div class="scroll" tabindex="0" role="region" aria-label="V4: {html.escape(name)}"><a class="chart-link" data-key="{key}" href="{after}"><img class="chart" data-key="{key}" loading="lazy" src="{after}" alt="V4: {html.escape(name)}"></a></div></figure></div>{extras.get(key,"")}</article>'
            )
            old = f"[![Vorher]({previous})]({previous})" if previous else "Neu"
            markdown.append(
                f"| **{name}**<br>{change} | {old} | [![V4]({after})]({after}) |\n"
            )
        inner = "".join(cards)
        if group_id in ("markt", "kontext"):
            sections.append(
                f'<details class="group" id="{group_id}"><summary>{html.escape(title)}</summary>{inner}</details>'
            )
        else:
            sections.append(
                f'<section id="{group_id}"><h2>{html.escape(title)}</h2>{inner}</section>'
            )
    markdown.append(
        "\n## Weitere Ansichten\n\n[Kurs ohne Ereignisse](charts/01_price_eur.png) · [Originale Galerie](baseline/data_exploration/README.md) · [Originale HTML-Vorschau](baseline/style/ci-preview.html)\n"
    )
    (ROOT / "README.md").write_text("".join(markdown))
    template = (ROOT / "gallery-template.html").read_text()
    replacements = {
        "@@SECTIONS@@": "".join(sections),
        "@@DATE@@": html.escape(manifest["retrieved_at"]),
        "@@VARIANTS@@": json.dumps(manifest["variants"]),
        "@@OUTPUTS@@": json.dumps(manifest["outputs"]),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    (ROOT / "index.html").write_text(template)
