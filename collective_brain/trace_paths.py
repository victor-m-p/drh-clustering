import numpy as np
import pandas as pd

spatiotemporal_overlap = pd.read_csv("data/spatiotemporal_overlap.csv")

# 1. entries only in "from" (i.e., starting points)
entries_from = spatiotemporal_overlap["entry_id_from"].unique()
entries_to = spatiotemporal_overlap["entry_id_to"].unique()
entries_only_from = np.setdiff1d(entries_from, entries_to)
len(entries_only_from)

# check these out
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
entry_metadata = entry_metadata[
    ["entry_id", "entry_name", "year_from", "year_to", "poll"]
]
entry_metadata[entry_metadata["entry_id"].isin(entries_only_from)]

# problems with this:
# 1. some are weird: "contemporary" West African Vodun (from -1960).
# 2. some we know have contact: The Mosque Cluster at Gedi.
# 3. unless the data is clean the inference will not be clean.

# solutions
# 1. ways of plausibly establishing contact (e.g., language phylogeny, trade routes, entry tags, wikipedia scrape, etc.)
# 2. this also applies to across continent if we want to include recent data.
# 3. this becomes incredibly complex but could be really interesting.

# really want to create a function to find all paths
# and then potentially to map them out.
