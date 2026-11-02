"""Check financial arithmetic and event timing offline with known examples.

Run: ``python -m unittest discover -s tests -v``. No network or API keys needed.
"""

import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data_exploration" / "v3_dark"
sys.path.insert(0, str(ROOT))
monthly = importlib.import_module("06_plot_monthly_returns")
kpi = importlib.import_module("08_plot_kpi_tiles")
returns = importlib.import_module("returns")
stocks = importlib.import_module("stocks")
income = importlib.import_module("10_plot_income")
reaction = importlib.import_module("11_plot_earnings_reaction")
pe = importlib.import_module("12_plot_pe_ratio")
dividends = importlib.import_module("14_plot_dividends")
targets = importlib.import_module("16_plot_price_targets")
insiders = importlib.import_module("17_plot_insiders")
options = importlib.import_module("19_plot_implied_vol")
data = importlib.import_module("msft_data")


class FinancialCalculations(unittest.TestCase):
    """Protect against month-boundary, lookahead and unit mistakes."""

    def test_native_calendars_preserve_foreign_market_highs(self):
        """Do not remove foreign sessions when calculating drawdown or risk."""
        dates = pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-06"])
        history = {
            t: pd.DataFrame({"Close": [100.0, 110.0]}, index=dates[[0, 2]])
            for t in stocks.TICKERS
        }
        history["9988.HK"] = pd.DataFrame({"Close": [100.0, 200.0, 110.0]}, index=dates)
        with patch.object(stocks, "load_history", return_value=history) as loader:
            close = stocks.load_prices("13mo")
        loader.assert_called_once_with("13mo")
        self.assertTrue(pd.isna(close.loc[dates[1], "MSFT"]))
        self.assertAlmostEqual(returns.drawdown(close)["9988.HK"].iloc[-1], -45.0)
        self.assertAlmostEqual(kpi.metrics(close["9988.HK"])["drawdown"], -0.45)
        self.assertEqual(tuple(close.columns), ("ORCL", "MSFT", "9988.HK", "SAP.DE"))

    def test_complete_months_and_missing_prices(self):
        """Exclude the running month and never fill a missing monthly price."""
        close = pd.DataFrame(
            {"MSFT": [100.0, 110.0, np.nan, 121.0, 999.0]},
            index=pd.to_datetime(
                ["2025-12-31", "2026-01-30", "2026-02-27", "2026-03-31", "2026-04-01"]
            ),
        )
        result = monthly.monthly_returns(close, "2026-04-15")
        self.assertEqual(result.index[-1], pd.Timestamp("2026-03-31"))
        self.assertAlmostEqual(result.iloc[0, 0], 10.0)
        self.assertTrue(result.iloc[1:].isna().all().all())

    def test_twelve_complete_months(self):
        """Retain twelve changes from thirteen complete month-end prices."""
        close = pd.DataFrame(
            {"MSFT": np.arange(100.0, 114.0)},
            index=pd.date_range("2025-01-31", periods=14, freq="ME"),
        )
        result = monthly.monthly_returns(close, "2026-02-15")
        self.assertEqual(len(result), 12)
        self.assertEqual(result.index[-1], pd.Timestamp("2026-01-31"))

    def test_drawdown_and_kpis(self):
        """Compare return/risk figures with hand-computable daily prices."""
        close = pd.Series([100.0, 120.0, 90.0, 99.0])
        np.testing.assert_allclose(returns.drawdown(close), [0, 0, -25, -17.5])
        result = kpi.metrics(close)
        self.assertAlmostEqual(result["day"], 0.1)
        self.assertAlmostEqual(result["year"], -0.01)
        self.assertAlmostEqual(result["drawdown"], -0.25)
        expected = np.std(np.log([1.2, 0.75, 1.1]), ddof=1) * np.sqrt(252)
        self.assertAlmostEqual(result["volatility"], expected)
        self.assertIn("▼ −", kpi.signed_return(-0.01))
        with self.assertRaises(ValueError):
            kpi.metrics(pd.Series([1.0, 0.0, 2.0]))

    def test_fiscal_year_and_margins(self):
        """Microsoft's September quarter belongs to the following fiscal year."""
        self.assertEqual(
            data.fiscal_label(pd.Timestamp("2026-09-30")), "Q1 GJ27\n09/2026"
        )
        self.assertEqual(
            data.fiscal_label(pd.Timestamp("2026-06-30"), True), "GJ26\n06/2026"
        )
        result = income.margins(
            pd.DataFrame(
                {
                    "Total Revenue": [100.0],
                    "Net Income": [30.0],
                    "Operating Income": [40.0],
                }
            )
        )
        np.testing.assert_allclose(result.iloc[0], [30, 40])

    def test_local_dates_are_preserved(self):
        """Discard timezone offsets without moving a late report into tomorrow."""
        original = pd.Series(
            [1], index=pd.DatetimeIndex(["2026-01-30 23:00"], tz="America/New_York")
        )
        self.assertEqual(
            data.daily_index(original).index[0], pd.Timestamp("2026-01-30")
        )

    def test_next_trading_day_reaction(self):
        """A Friday after-close report affects Monday, not Friday's return."""
        earnings = pd.DataFrame(
            {"EPS Estimate": [2.0], "Reported EPS": [2.2]},
            index=pd.to_datetime(["2026-01-30"]),
        )
        close = pd.Series(
            [50.0, 100.0, 90.0],
            index=pd.to_datetime(["2026-01-29", "2026-01-30", "2026-02-02"]),
        )
        result = reaction.reactions(earnings, close)
        self.assertAlmostEqual(result.iloc[0]["surprise"], 10)
        self.assertAlmostEqual(result.iloc[0]["reaction"], -10)
        self.assertTrue(reaction.reactions(earnings, close.iloc[:-1]).empty)

    def test_ttm_eps_has_no_same_day_lookahead(self):
        """Fourth-quarter EPS become available on the next trading session."""
        dates = pd.to_datetime(["2025-04-30", "2025-07-30", "2025-10-29", "2026-01-30"])
        earnings = pd.DataFrame({"Reported EPS": [1.0, 2.0, 3.0, 4.0]}, index=dates)
        close = pd.Series(
            [100.0, 110.0], index=pd.to_datetime(["2026-01-30", "2026-02-02"])
        )
        result = pe.trailing_pe(earnings, close)
        self.assertEqual(list(result.index), [pd.Timestamp("2026-02-02")])
        self.assertAlmostEqual(result.iloc[0], 11.0)

    def test_missing_quarter_does_not_make_ttm(self):
        """Four reports spanning a missing fiscal quarter are not TTM EPS."""
        dates = pd.to_datetime(["2025-01-30", "2025-04-30", "2025-10-29", "2026-01-30"])
        earnings = pd.DataFrame({"Reported EPS": [1.0, 2.0, 3.0, 4.0]}, index=dates)
        close = pd.Series([100.0], index=pd.to_datetime(["2026-02-02"]))
        self.assertTrue(pe.trailing_pe(earnings, close).empty)

    def test_dividend_window_uses_calendar_year(self):
        """Exclude the exact year-old payment, including across a leap year."""
        payments = pd.Series(
            [1.0, 2.0, 3.0],
            index=pd.to_datetime(["2023-03-01", "2024-02-29", "2024-03-01"]),
        )
        close = pd.Series([100.0], index=pd.to_datetime(["2024-03-01"]))
        self.assertAlmostEqual(dividends.dividend_yield(payments, close).iloc[0], 5.0)

    def test_actions_and_insider_types(self):
        """Exclude zero targets and infer insider type from populated text."""
        close = pd.Series(
            [100.0, 110.0], index=pd.to_datetime(["2026-01-02", "2026-01-05"])
        )
        actions = pd.DataFrame(
            {
                "currentPriceTarget": [0.0, 120.0],
                "priceTargetAction": ["Raises", "Lowers"],
            },
            index=close.index,
        )
        self.assertEqual(
            targets.prepare_actions(actions, close)["kind"].tolist(), ["Lowers"]
        )
        transactions = pd.DataFrame(
            {
                "Start Date": ["2026-01-03", "2026-01-05"],
                "Text": ["Sale at price 100", "Stock Gift"],
                "Transaction": ["", ""],
            }
        )
        result = insiders.prepare_transactions(transactions, close)
        self.assertEqual(result["kind"].tolist(), ["Sale", "Other"])
        self.assertEqual(result["price"].tolist(), [100.0, 110.0])

    def test_option_expiries_and_stale_quotes(self):
        """Select distinct horizons and reject zero IV, stale trades and no OI."""
        now = pd.Timestamp("2026-11-01", tz="UTC")
        chosen = options.select_expiries(
            ["2026-11-02", "2026-11-09", "2026-12-04", "2027-01-15"],
            now.tz_localize(None),
        )
        self.assertEqual(chosen, ["2026-11-09", "2026-12-04", "2027-01-15"])
        calls = pd.DataFrame(
            {
                "strike": [100.0] * 4,
                "openInterest": [10, 10, 0, 10],
                "impliedVolatility": [0.2, 0.00001, 0.2, 0.2],
                "lastTradeDate": [now - pd.Timedelta(days=d) for d in [2, 2, 2, 20]],
            }
        )
        self.assertEqual(list(options.valid_calls(calls, 100.0, now).index), [0])


if __name__ == "__main__":
    unittest.main()
