# Plot polish: v1 and v2 side by side

Goal: keep the current plots as `data_exploration/v1_basic/` and add
`data_exploration/v2_polished/` with the same three plots in Matplotlib,
styled like the CI preview page (`style/ci-preview.html`).

1. Move scripts, PNGs and `ci.py` into `v1_basic/`, fix output paths and the
   JSON path → verify: v1 scripts run and write their PNGs.
2. `v2_polished/ci.py`: rcParams plus helpers for title/subtitle, card,
   German numbers and months, end label, legend row → verify: black, ruff.
3. Port the three plots to v2 (same loaders, new `plot()`) → verify: scripts
   run, PNGs checked visually.
4. Update `data_exploration/README.md` → verify: paths in README match.

Not in scope: interactivity (needs Plotly), rounded bar ends.
