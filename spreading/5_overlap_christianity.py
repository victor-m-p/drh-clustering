import numpy as np
import pandas as pd

# let us flag which entries have been in contact (direct, indirect)
# with christianity
spatiotemporal_data = pd.read_csv("data/spatiotemporal_overlap.csv")

# add christianity
entry_data_subset = pd.read_csv("data/entry_data_subset.csv")
entry_data_subset = entry_data_subset[["entry_id", "christian_tradition"]]

entry_data_subset = entry_data_subset.rename(
    columns={
        "entry_id": "entry_id_from",
        "christian_tradition": "christian_tradition_from",
    }
)
spatiotemporal_data = spatiotemporal_data.merge(
    entry_data_subset, on="entry_id_from", how="inner"
)

entry_data_subset = entry_data_subset.rename(
    columns={
        "entry_id_from": "entry_id_to",
        "christian_tradition_from": "christian_tradition_to",
    }
)
spatiotemporal_data = spatiotemporal_data.merge(
    entry_data_subset, on="entry_id_to", how="inner"
)
spatiotemporal_data.to_csv("data/overlap_christianity.csv", index=False)
