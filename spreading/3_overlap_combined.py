"""
2024-06-13 vmp checked and rerun.
"""

import pandas as pd

spatial_overlap = pd.read_csv("data/spatial_overlap.csv")
temporal_overlap = pd.read_csv("data/temporal_overlap.csv")

# merge spatiotemporal overlaps
## rename spatial overlap columns (direction does not matter here)
df_overlap = spatial_overlap.merge(
    temporal_overlap, on=["entry_id_from", "entry_id_to"], how="inner"
).sort_values("overlap_start")

# save
df_overlap.to_csv("data/spatiotemporal_overlap.csv", index=False)
