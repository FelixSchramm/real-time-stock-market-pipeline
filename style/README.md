# CI color categories

The source of the live design tokens is [felix-schramm-ci.json](felix-schramm-ci.json).
[ci-preview.html](ci-preview.html) is a standalone preview with an embedded copy.

| Category | JSON path | Purpose |
|---|---|---|
| Categorical | `color.categorical` | Identify stocks or other unrelated series |
| Sequential | `color.sequential` | Encode increasing amounts, such as volume |
| Diverging | `color.diverging` | Encode negative → neutral → positive values |
| Finance directions | `color.finance` | Up/down markers, candles and indicators |

## Diverging value scale

CI 1.3.0 uses the owner's selected red → grey → green scale, matching
[stock_treemap](https://github.com/FelixSchramm/stock_treemap/blob/main/src/portfolio_dashboard/treemap.py):

- Negative: **#B3261E**
- Neutral: **#5F6368**
- Positive: **#188038**

`returns_light` and `returns_dark` contain nine interpolated steps, ordered
from negative to positive. Both modes use these same treemap fills. The
`label` token supplies white text; `missing` distinguishes unavailable values
from zero. Every numeric cell retains its value and sign.

Return bins stay at −10, −5, −2, −0.5, +0.5, +2, +5 and +10 percent. The
middle bin spans −0.5 to +0.5 percent. Legend ticks also retain explicit
minus/plus signs (zero is unsigned). Value changes affect saturation, not
stock identity. V3/V4 read these value tokens; the frozen V4 baseline keeps
its original colors for the before/after comparison.
