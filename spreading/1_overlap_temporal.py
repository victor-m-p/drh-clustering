"""
2024-06-13 vmp checked and rerun.
"""

# find temporal overlaps;
import pandas as pd
from fun import find_temporal_overlaps

# load
entry_metadata = pd.read_csv("../data/raw/entry_data.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to"]]

# find temporal overlaps (from, to)
temporal_overlap = find_temporal_overlaps(entry_metadata)

# save
temporal_overlap.to_csv("data/temporal_overlap.csv", index=False)
