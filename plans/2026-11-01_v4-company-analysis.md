# V4 comparison and company analysis

User authorized a new V4 directory, preservation of all prior versions, real-data
plots and a direct push to main. References: original visualization epic #8.

1. Freeze the existing data_exploration and style files in v4/baseline.
2. Build a separate V4 renderer with explicit currency, adjustment and time
   conventions, source dates, readable scales and market-data quality checks.
3. Regenerate all 19 chart themes; add balance sheet, ROIC, cash conversion,
   capital allocation, per-share economics, estimate revisions, valuation and
   reverse-DCF scenarios. Source qualitative facts; never invent segment data.
4. Provide an HTML before/after gallery and a linked Markdown catalog. Separate
   business analysis from supplemental market/ownership/options charts. Preserve
   the approved stock selection and every existing chart outside V4.
5. Run offline financial tests, all real-data renderers, Black/Ruff and browser
   checks (desktop/mobile), inspect plots, then publish checked commits to main; push immediately after each commit.

Raw API responses/cache remain local and untracked. The gallery contains public
chart outputs and provenance only. No portfolio quantities, weights or costs.
