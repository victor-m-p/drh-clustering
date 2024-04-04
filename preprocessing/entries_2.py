import pandas as pd
from functions_answers import mode_feature_by_entry

# load data
data_raw = pd.read_csv("../data/dump/raw_data.csv")
data_subset = pd.read_csv("../data/preprocessed/answers_subset.csv")

# only take the entries from data_subset
unique_entries = data_subset[["entry_id"]].drop_duplicates()
data_raw = data_raw.merge(unique_entries, on="entry_id", how="inner")

# get most common date range for each entry
mode_timespan = mode_feature_by_entry(data_raw, "entry_id", ["year_from", "year_to"])

# save
mode_timespan.to_csv("../data/preprocessed/entry_timespan.csv", index=False)
