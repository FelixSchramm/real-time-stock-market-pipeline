# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-11-01 (issue #4 implemented, PR #22 review pending)
**Chain status:** interactive implementation; automatic relay not started

## Kickoff checklist (to be done by the user or a setup session)

The integration branch now exists, initialized from `main` at
`5fa9e62b345418eb1b65d5ca0715a63187c97502`. Issue #4 was implemented in an
interactive Codex session. No fallback routine was created and no external
Claude session was started. The Claude-specific remote-session tools are
not available in this session; the automatic relay remains inactive.

Original relay setup checklist:

1. Create the work plan as GitHub issues (self-contained, one issue = one
   PR) and list their processing order under "Work plan" below.
2. Integration branch created and pushed (done).
3. Create the fallback routine (claude-code-remote `create_trigger`,
   cron `0 6,18 * * *`, `create_new_session_on_fire: true`) with the
   fallback prompt from CLAUDE.md, section "Prompt templates".
4. Start the first worker session with the "Reviewer → worker" template
   for the first issue.

## Work plan

1. #4 — feat: indexed price comparison of several stocks (v3_dark/05)
2. #5 — feat: monthly returns heatmap (v3_dark/06)
3. #6 — feat: drawdown chart of several stocks (v3_dark/07)
4. #7 — feat: KPI tiles per stock (v3_dark/08)
5. #9 — MSFT annual cash flow
6. #10 — MSFT quarterly income and margins
7. #11 — MSFT earnings reaction
8. #13 — MSFT benchmark and drawdown
9. #12 — MSFT historical P/E
10. #14 — MSFT dividends and yield
11. #15 — MSFT analyst targets and recommendations
12. #16 — MSFT price target development
13. #17 — MSFT insider transactions
14. #18 — MSFT institutional holders (optional)
15. #19 — MSFT implied volatility (optional)

#8 tracks the MSFT chart epic. #21 (CI distribution) stays open and is
deferred at the user's explicit request on 2026-11-01; do not implement it
as part of this chart work.

Context: chart ideas from the CI preview page (`style/ci-preview.html`), to
be built in Matplotlib in `data_exploration/v3_dark/` with its `ci.py`.

## Done

- #3 candlestick chart with volume panel: `04_plot_candles.py` in all three
  folders (`v1_basic`, `v2_polished`, `v3_dark`), at the user's request for
  MSFT instead of AAPL. Merged directly into `main` at the user's request
  (no integration branch yet). `new_figure` in v2/v3 `ci.py` now passes
  extra keywords to `plt.subplots` (stacked panels); reuse it for #4-#7.

## In progress

- #4: implemented on `issue-4-indexed`, commit `50a3d94`.
  PR [#22](https://github.com/FelixSchramm/real-time-stock-market-pipeline/pull/22)
  targets `integration`; state: **review pending**, not merged.
- Real yfinance data used (31.10.2025–30.10.2026); PNG generated and visually
  inspected. Synthetic checks verified the shared base 100, exact indexed
  values, >=15 pt end-label spacing, series-count limit and missing-series
  rejection. Black, Ruff and whitespace checks passed.

## Next step

- Review PR #22 following the reviewer protocol. After a merge into
  `integration`, close #4 manually, archive this handover and proceed to #5.
- The remaining chart issues are specified sufficiently for implementation;
  no product clarification is pending. #21 is deliberately deferred.

## Open questions / decisions taken

- External services (market data API, broker, database) and their
  credentials may not be available in a cloud session. Implement and
  document the code path anyway and record here which steps still need a
  local run for verification.

## Known pitfalls

- Never force-push `integration`.
- Issue PRs target the integration branch, not `main` — GitHub's `Closes #N`
  auto-close does not fire there; the reviewer closes issues manually after
  the merge.
- Every issue PR is merged only by a reviewer session (see CLAUDE.md,
  "Reviewer session"); always record the open PR number and its state
  (review pending / findings open / merged) here.
- Never commit API keys or credentials; use environment variables.
- Parallel yfinance downloads hit a SQLite cache lock in this fresh
  environment. The new script uses `threads=False`; no requested ticker is
  silently omitted. yfinance 1.7.0 with pandas 3.1.0 emits upstream pandas
  deprecation warnings; the chart still renders successfully.
