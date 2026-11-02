# HANDOVER

**Last updated:** 2026-11-02
**Chain status:** CI 1.3.0 red/grey/green value scale applied; relay inactive

## Session instructions

The user requested all pending visualizations, including final integration,
without a review. This overrides the reviewer/relay steps in `CLAUDE.md` for
this work. No reviewer, successor session or fallback routine was created.
The current owner workflow is direct checked writes to main, without PRs or
review, with chart images shown in chat. The automatic relay remains inactive. #21 (CI distribution) remains deferred.

## Diverging value colors (CI 1.3.0)

The owner selected the red/grey/green treemap scale, not the suggested
orange/blue alternative. Value colors use the treemap anchors #B3261E,
#5F6368 and #188038 under `color.diverging`. Nine return bins retain their
existing thresholds. White text and explicit minus/plus signs appear in
numeric cells and the monthly-return colorbar (zero is unsigned).

The main CI JSON, standalone HTML preview, V3 heatmap/analyst PNG and V4
value consumers are updated. V4 now reads these value tokens instead of
hard-coded ramps. The reverse-DCF value heatmap uses the same diverging
colors. Other CI color categories keep their previous tokens.

V4 was regenerated coherently: all 29 themes / 44 PNGs use the Yahoo snapshot
from 2026-11-02 10:09 UTC, with no fetch or render errors. `manifest.json`
records CI version 1.3.0. The archived 67-file baseline remains unchanged;
tests pin the two baseline PNG hashes whose live V3 counterparts were
intentionally recolored, and still compare all other original PNGs. All 21
offline tests pass. Legend signs were checked on the rendered colorbar; the
minimum white-text contrast is 5.02:1 across all nine value fills. Black,
Ruff, preview JavaScript syntax and token/preview consistency checks pass.

## V3 file layout

The eleven Microsoft scripts and their existing PNGs now live in
`data_exploration/v3_dark/`, numbered 09–19 after the original 01–08.
`msft_data.py` moved beside the scripts. Imports, PNG output paths, test module
names and the live chart catalog follow the new layout. V4 and its immutable
baseline retain their historical files and paths; the baseline integrity test
locates the renamed originals and still compares their bytes.

Verification: all 21 offline tests pass, including the byte-for-byte baseline
comparison. All 19 V3 scripts import successfully; their numbering, PNG output
paths and README links are checked. Black, Ruff and whitespace checks pass.
No chart data or PNG contents were regenerated during this reorganization.

## V4 company-analysis comparison

The owner requested the full visualization critique implemented in a new V4
folder, preserving all earlier versions, and an immediate main push after
each commit. The baseline was published first in `c3bdc71`: 67 byte-identical
analysis/style files in `data_exploration/v4/baseline/` plus the work plan.

V4 is self-contained in `data_exploration/v4/`: 29 chart themes, 44 rendered
PNGs, a GitHub before/after catalog and a local HTML comparison gallery.
New business views cover segments, balance sheet, ROIC, cash quality, capital
allocation, per-share economics, estimate revisions and reverse DCF.
Five market comparisons support EUR/USD and price/total-return variants.
The original chart calculations, PNG bytes and style files were preserved.
The later V3 reorganization above changes only live file paths and imports.

The snapshot was fetched on 2026-11-01 at 22:50 UTC with yfinance 1.7.0;
latest market session is 2026-10-30. Segment figures are independently
sourced from Microsoft Annual Report 2026, Note 18, with a committed CSV.
Raw Yahoo cache files are ignored. The approved stock selection is unchanged.

Validation: all 21 offline tests pass; Black and Ruff pass. All 29 themes
rendered without fetch/render errors. PNGs were visually inspected and the
local gallery checked in Chromium at desktop/mobile sizes, including all
controls and zero JavaScript errors. See `data_exploration/v4/VALIDATION.md`.

Open `data_exploration/v4/README.md` on GitHub for the image comparisons, or
open `data_exploration/v4/index.html` locally for interactive controls.
Regenerate with `python data_exploration/v4/generate.py --refresh`.
Definitions and limitations are in V4 `METHODS.md` and `research.md`:
Yahoo history is limited, ROIC is an explicit proxy, cash Capex does not split
maintenance/growth investment, and the reverse DCF is an equity FCF scenario.
Competitive advantages remain research hypotheses, not an automated score.

## Earlier completed chart work

- #4: prepared indexed comparison integrated via PR #22 without a separate
  review, as requested. The approved ORCL/MSFT/9988.HK/SAP.DE selection is preserved.
- #5: twelve complete months of adjusted returns, nine discrete color bins,
  signed cell labels and contrast-aware text (`v3_dark/06`).
- #6: one-year drawdown with separated direct end labels (`v3_dark/07`).
- #7: price, daily/year return, annual log volatility and max-drawdown tiles
  using the approved stock selection (`v3_dark/08`).
- #9–#19: all eleven Microsoft epic charts, including optional institutional
  holders and implied volatility. Scripts and generated PNGs are now in
  `data_exploration/v3_dark/`, numbered 09–19 in the consolidated series.
- #8: epic implementation complete. The chart catalog documents each script,
  units, event timing and snapshot limitations, with a complete PNG gallery.
- Shared CI, end-label spacing, drawdown arithmetic and a small Microsoft
  data helper are reused. No new dashboard, streaming infrastructure, API
  credentials or portfolio-private data were introduced.

## Earlier verification

- All 15 additional scripts (the indexed comparison plus 14 new charts)
  ran successfully with real Yahoo/yfinance data on 2026-11-01.
- Generated PNGs inspected; dark-theme axis-label contrast corrected.
- 12 offline tests pass: complete months/missing prices, drawdown and manual
  KPI arithmetic, fiscal years/margins, local dates, next-session earnings
  reaction, no after-close EPS lookahead, missing quarters, calendar-year
  dividend windows, analyst/insider classification, stale option filtering, native foreign-market trading calendars.
- Black, Ruff and whitespace checks pass for changed Python code.
- Run `python -m unittest discover -s tests -v` from the repository root.

## Earlier publication

Initial chart commits were integrated through PR #23 without a review.
Concurrent main commit `e5c53c6` supplied the final four-stock selection, USD
conversion and direct-main workflow. It is preserved in full. The new charts
use its `load_history` helper and native calendars; foreign-market highs are
not discarded for drawdown or risk. PR #24 was closed without merging.
The combined, checked result is published directly to main, without further
PRs or review, as required by the latest owner instructions in CLAUDE.md.
Show the resulting chart images in chat. The disabled relay stays inactive.

## Next step

V4 is ready for the owner to compare with the preserved baseline. No further
automatic implementation, review or relay session is scheduled.
#21 stays open and is deliberately not part of this delivery. The Kafka,
Spark and PostgreSQL stack in the main README is still a target design; these
charts are standalone data exploration, not a running streaming dashboard.

## Earlier data limitations (baseline)

- Prices and snapshots reflect the last available market session; the run
  date is a Sunday. Options are filtered by open interest, plausible positive
  IV and last trade within seven days, but are still quoted snapshots.
- Institutional holdings carry filing dates, not live ownership estimates.
- Historical P/E uses adjusted reported EPS and may differ from GAAP portals.
- Yahoo fundamentals and event history have limited coverage. Missing required
  data stops a script; no synthetic data is used in committed PNGs.
- Never force-push `integration`, commit secrets or replace approved stock
  symbols without checking the owner's portfolio instruction.
