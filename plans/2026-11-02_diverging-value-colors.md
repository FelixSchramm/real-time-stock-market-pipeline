# Align numeric value colors with the stock treemap

The owner selected red → grey → green, matching
`FelixSchramm/stock_treemap/src/portfolio_dashboard/treemap.py`.
The category is a diverging color scale, stored under `color.diverging`.

1. Use the treemap's anchors: negative #B3261E, neutral #5F6368, positive
   #188038. Interpolate nine bins and retain the existing symmetric return
   thresholds. Keep signed values and high-contrast labels.
2. Update the main CI JSON, its standalone HTML preview, and V3/V4 consumers.
   V4 must read the same value tokens rather than its own orange/green ramp.
3. Regenerate affected V3 charts and V4's coherent snapshot/gallery. Preserve
   the immutable V4 baseline. Record the new retrieval date for live outputs.
4. Check shared-token consistency and label contrast, inspect the rendered
   heatmaps, run existing offline tests and required format/lint checks.
5. Commit and immediately publish directly to main without a PR or review.
