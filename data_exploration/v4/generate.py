"""Regenerate all V4 PNGs and the comparison gallery from one dated snapshot.

Usage: python data_exploration/v4/generate.py [--refresh]
Raw Yahoo responses stay in .cache, which is excluded from Git.
"""

import argparse
import json

import business
import market
from data import ROOT, fetch


def main():
    """Render all charts, report real failures and write a reviewable gallery."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh", action="store_true", help="Fetch a new complete Yahoo snapshot"
    )
    args = parser.parse_args()
    bundle = fetch(args.refresh)
    if bundle.get("info", {}).get("financialCurrency") != "USD":
        raise ValueError(
            "Financial statement currency must be USD for these MSFT charts"
        )
    outputs = {}
    failures = {}
    tasks = {
        "03": lambda: business.cashflows(bundle, quarterly=True),
        "04": lambda: market.candles(bundle),
        "09": lambda: business.cashflows(bundle),
        "10": lambda: business.income(bundle),
        "11": lambda: market.reactions(bundle),
        "12": lambda: market.pe_history(bundle),
        "14": lambda: market.dividends(bundle),
        "15": lambda: market.analyst_snapshot(bundle),
        "16": lambda: market.target_actions(bundle),
        "17": lambda: market.insider_activity(bundle),
        "18": lambda: market.holders(bundle),
        "19": lambda: market.option_volatility(bundle),
        "20": lambda: business.balance_sheet(bundle),
        "21": lambda: business.returns_on_capital(bundle),
        "22": lambda: business.cash_quality(bundle),
        "23": lambda: business.capital_allocation(bundle),
        "24": lambda: business.per_share(bundle),
        "25": lambda: business.estimates(bundle),
        "26": lambda: business.valuation(bundle),
        "27": lambda: business.reverse_dcf(bundle),
        "28": lambda: business.segments(bundle),
        "29": lambda: business.cash_bridge(bundle),
    }
    for key, task in tasks.items():
        try:
            print("Rendering", key, flush=True)
            outputs[key] = task()
        except Exception as exc:  # noqa: BLE001
            failures[key] = f"{type(exc).__name__}: {exc}"
            print("FAILED", key, failures[key], flush=True)
    outputs.update(market.price_events(bundle))
    variants = {}
    for currency in ("EUR", "USD"):
        for total in (True, False):
            kind = "total" if total else "price"
            print("Rendering comparison", currency, kind, flush=True)
            variant = market.comparison(bundle, currency, total)
            variants[f"{currency}_{kind}"] = variant
            if currency == "EUR" and total:
                outputs.update(variant)
    metadata = {
        "retrieved_at": bundle["retrieved_at"],
        "yfinance_version": bundle["version"],
        "outputs": outputs,
        "variants": variants,
        "fetch_errors": bundle["errors"],
        "render_errors": failures,
        "baseline_commit": "71a8bbeaa147e84cd8ac2a1eb80e4b0af9fb0c42",
    }
    (ROOT / "manifest.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )
    if failures:
        raise RuntimeError(f"{len(failures)} plots failed; see manifest.json")
    from gallery import build

    build(bundle, metadata)
    print(f'{len(outputs)} chart themes rendered; gallery: {ROOT / "index.html"}')


if __name__ == "__main__":
    main()
