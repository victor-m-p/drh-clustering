import numpy as np
import pandas as pd

# islam

# christianity

#
# find christian entries
entry_tags = pd.read_csv("../data/raw/entry_tags.csv")
entry_tags_lvl2 = entry_tags[entry_tags["level"] == 2]
entry_tags_lvl2.groupby("entry_tag").size().reset_index(name="count").sort_values(
    "count", ascending=False
).head(20)

"Islamic Traditions"
entry_tags_lvl2[entry_tags_lvl2["entry_tag"] == "Abrahamic"]

entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
x = entry_metadata.merge(entry_tags_lvl2, on="entry_id", how="inner")
x[x["entry_tag"] == "Christianity"]["poll"].unique()
x[x["entry_tag"] == "Christian Traditions"]["poll"].unique()

entry_tags[entry_tags["entrytag_id"] == 1570]

# find out what we match with "Christ":
christian_tags = [
    18,  # Christian Traditions
    905,  # Abrahamic
    915,  # Evangelicalism
    971,  # Methodism
    1032,  # Protestantism
    996,  # Roman Catholic
    999,  # Catholic
    1031,  # Pentecostal
    1570,  # Christianity
]
christian_string = "Christian"

# find christian entries
christian_entries = (
    entry_tags[
        (entry_tags["entrytag_id"].isin(entrytag_id))
        | (entry_tags["parent_tag_id"].isin(entrytag_id))
        | (entry_tags["entry_tag"].str.contains(entry_string_match))
    ]["entry_id"]
    .unique()
    .tolist()
)

# find non-christian entries
non_christian_entries = (
    entry_tags[~entry_tags["entry_id"].isin(christian_entries)]["entry_id"]
    .unique()
    .tolist()
)
