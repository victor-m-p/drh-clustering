# find temporal overlaps;
import pandas as pd
import numpy as np
from fun import find_temporal_overlaps

# load
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to"]]

# find temporal overlaps (from, to)
temporal_overlap = find_temporal_overlaps(entry_metadata)

# save
temporal_overlap.to_csv("data/temporal_overlap.csv", index=False)
