# Consolidate the V3 chart files

1. Move the eleven Microsoft chart scripts and their PNGs from the
   `data_exploration/` root into `v3_dark/`, numbered 09–19 after the existing
   01–08. Move `msft_data.py` beside its consumers.
2. Update sibling imports, output paths, test module names and the live chart
   catalog. Keep V1/V2, V4 and its immutable baseline files unchanged.
3. Check every V3 script's imports and output path, verify the PNG moves are
   byte-identical, and run the offline suite plus Black/Ruff. Adapt the V4
   baseline integrity test to locate the renamed originals.
4. Commit the complete reorganization and immediately push directly to main,
   without a PR or review, as requested. No market-data refresh is needed.
