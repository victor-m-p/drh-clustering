import numpy as np
import pandas as pd

# islam

# christianity

# find christian entries
entry_tags = pd.read_csv("../data/raw/entry_tags.csv")
entry_string_match = "Islam"

# find christian entries
islam_entries = (
    entry_tags[entry_tags["entry_tag"].str.contains(entry_string_match)]["entry_id"]
    .unique()
    .tolist()
)

entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
entry_metadata = entry_metadata[["entry_id", "entry_name", "year_from", "year_to"]]
islam_metadata = entry_metadata[entry_metadata["entry_id"].isin(islam_entries)]
islam_metadata.sort_values("year_from").head(20)


# find non-christian entries
non_christian_entries = (
    entry_tags[~entry_tags["entry_id"].isin(christian_entries)]["entry_id"]
    .unique()
    .tolist()
)
