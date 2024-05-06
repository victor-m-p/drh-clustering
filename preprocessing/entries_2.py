import pandas as pd
from helper_functions import mode_feature_by_entry

# load data
data_raw = pd.read_csv("../data/raw/raw_data.csv")
data_subset = pd.read_csv("../data/preprocessed/answers_subset.csv")

# only take the entries from data_subset
unique_entries = data_subset[["entry_id"]].drop_duplicates()
data_raw = data_raw.merge(unique_entries, on="entry_id", how="inner")

# get most common date range for each entry
mode_timespan = mode_feature_by_entry(data_raw, "entry_id", ["year_from", "year_to"])

# keep poll (might filter out texts)
data_subset = data_subset[["entry_id", "poll"]].drop_duplicates()
entry_metadata = mode_timespan.merge(data_subset, on="entry_id", how="inner")

# add entry name
data_raw = data_raw[["entry_id", "entry_name"]].drop_duplicates()
entry_metadata = entry_metadata.merge(data_raw, on="entry_id", how="inner")

# fix dates for some (islamic) entries
# we would need a spreadsheet of corrected dates here.

# sanity check and save
assert len(entry_metadata) == entry_metadata["entry_id"].nunique()
entry_metadata.to_csv("../data/preprocessed/entry_metadata.csv", index=False)
