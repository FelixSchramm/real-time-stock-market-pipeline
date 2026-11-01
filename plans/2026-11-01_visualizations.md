# Complete the chart work plan

The user requested all visualizations without a separate review. This overrides
the relay's reviewer step; no reviewer or automatic session relay is started.
Issue #21 (CI distribution) remains deferred. Use the approved ORCL/MSFT/9988.HK/SAP.DE
selection for the multi-stock charts. Include optional charts #18 and #19.

1. Integrate the prepared #4 comparison, then implement #5–#7 using v3_dark CI.
2. Implement #9–#19 as standalone scripts at the paths in their issues, sharing
   the existing dark CI. Keep financial units, event dates and snapshots explicit.
3. Generate every PNG from real Yahoo data. Check return, drawdown, volatility,
   earnings timing, TTM EPS and dividend-yield calculations with small known
   examples; run all scripts plus Black/Ruff and inspect generated charts.
4. Update the chart catalog and handover. Integrate completed charts into
   integration and finally main without requesting or posting a code review.

The repository currently contains data exploration, not a running Kafka/Spark/
PostgreSQL stack. This task completes that visualization work plan; it does not
claim that the planned streaming pipeline has been implemented.

Concurrent main update e5c53c6 is preserved: final four-stock selection,
correctly directed USD conversion and native calendars. The current owner
workflow supersedes the initial PR plan: publish checked changes directly
to main without further PRs or review, and display chart images in chat.
