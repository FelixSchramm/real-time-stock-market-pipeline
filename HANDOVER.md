# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-11-01 (work plan: chart issues #3-#7 added)
**Chain status:** not started (kickoff pending, see below)

## Kickoff checklist (to be done by the user or a setup session)

The protocol is set up in theory only. Before the first worker session can
start:

1. Create the work plan as GitHub issues (self-contained, one issue = one
   PR) and list their processing order under "Work plan" below.
2. Create the integration branch `integration` from `main` and push it
   (it must contain these protocol files).
3. Create the fallback routine (claude-code-remote `create_trigger`,
   cron `0 6,18 * * *`, `create_new_session_on_fire: true`) with the
   fallback prompt from CLAUDE.md, section "Prompt templates".
4. Start the first worker session with the "Reviewer → worker" template
   for the first issue.

## Work plan

1. #3 — feat: candlestick chart with volume panel (v3_dark/04)
2. #4 — feat: indexed price comparison of several stocks (v3_dark/05)
3. #5 — feat: monthly returns heatmap (v3_dark/06)
4. #6 — feat: drawdown chart of several stocks (v3_dark/07)
5. #7 — feat: KPI tiles per stock (v3_dark/08)

Context: chart ideas from the CI preview page (`style/ci-preview.html`), to
be built in Matplotlib in `data_exploration/v3_dark/` with its `ci.py`.

## Done

- (nothing yet — protocol files added on 2026-09-28)

## In progress

- Issue #3 (candles) implemented on branch `issue-03-candles` at the user's
  direct request, in all three folders (`v1_basic`, `v2_polished`,
  `v3_dark`), not only v3 as the issue says. No PR yet (the integration
  branch does not exist; kickoff pending). `new_figure` in v2/v3 `ci.py` now
  passes extra keywords to `plt.subplots` (needed for stacked panels).
  The user changed the ticker from AAPL (issue text) to MSFT.

## Next step

- Complete the kickoff checklist above.

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
