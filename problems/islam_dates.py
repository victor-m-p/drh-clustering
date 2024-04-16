import numpy as np
import pandas as pd

# find islamic entries
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

# we additionally need expert, editor
raw_data = pd.read_csv("../data/raw/data_dump.csv")
raw_data = raw_data[
    ["entry_id", "expert_id", "expert_name", "editor_id", "editor_name"]
].drop_duplicates()
islam_metadata = islam_metadata.merge(raw_data, on="entry_id", how="inner")
islam_problematic = islam_metadata.sort_values("year_from", ascending=True).head(20)

# write potentially problematic csv files
islam_problematic.to_csv("islam_metadata.csv", index=False)
