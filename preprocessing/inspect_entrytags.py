"""
vmp 2026-11-02

First look at the religious tags (entity_tags.csv) for group entries, as they are (no repairs).
Run cell by cell from inside preprocessing/ (after curate_covariates.py).
"""

# data: group entries in our sample, and their tags in the religious tree
import pandas as pd

sample = pd.read_csv("../data/preprocessed/entry_covariates.csv")
groups = sample.loc[sample["poll_name"].str.contains("Group"), "entry_id"]

tags = pd.read_csv("../data/sccsrv3/entity_tags.csv")
tags = tags[tags["entry_id"].isin(groups)]
religious = tags[tags["entrytag_path"].str.startswith("Religious Group[", na=False)]
religious = religious[religious["entrytag_name"] != "Religious Group"]  # the root itself
print(len(groups), "group entries;", religious["entry_id"].nunique(), "with a religious tag")

# (1) tags carried by at least 10 group entries (as the entry's own tag)
n_entries = religious.groupby(["entrytag_id", "entrytag_name"])["entry_id"].nunique().sort_values(ascending=False)
common = n_entries[n_entries >= 10]
print(len(common), "tags with >= 10 group entries")
print(common.head(10))

# group entries with at least one of these tags
common_ids = common.index.get_level_values("entrytag_id")
matched = religious.loc[religious["entrytag_id"].isin(common_ids), "entry_id"].unique()
print(len(matched), "of", len(groups), "group entries have a tag with >= 10 entries")

# (2) the other group entries: which tags do they have?
unmatched = religious[~religious["entry_id"].isin(matched)]
print(unmatched["entry_id"].nunique(), "group entries without such a tag")
print(unmatched["entrytag_name"].value_counts().head(20))

# could some be saved by name? (a tag with the same name as one of the common tags, but a different id)
common_names = set(common.index.get_level_values("entrytag_name"))
same_name = unmatched[unmatched["entrytag_name"].isin(common_names)]
print(same_name["entry_id"].nunique(), "of these entries have a tag whose name matches a common tag")
print(same_name[["entry_id", "entrytag_id", "entrytag_name", "entrytag_path"]].head(20).to_string(index=False))


# ======================================================================================================================
# Part 2: merge tags with the same name, then the same counts
# ======================================================================================================================

# all tags in the religious tree (any entry, not only groups), one row per tag id
all_tags = pd.read_csv("../data/sccsrv3/entity_tags.csv")
tag_ids = all_tags[all_tags["entrytag_path"].str.startswith("Religious Group[", na=False)].drop_duplicates("entrytag_id")
tag_ids = tag_ids[["entrytag_id", "entrytag_name", "entrytag_level", "entrytag_path"]]

# names with several tag ids
copies = tag_ids[tag_ids.duplicated("entrytag_name", keep=False)].sort_values(["entrytag_name", "entrytag_id"])
copies["in_system"] = copies["entrytag_level"] >= 3  # level 2 = directly under the root
print(copies["entrytag_name"].nunique(), "names with several tag ids (", len(copies), "tag ids )")

# keep one copy per name: in the system (has a parent below the root), lowest id first; otherwise the lowest id
keep = copies.sort_values(["entrytag_name", "in_system", "entrytag_id"], ascending=[True, False, True])
keep = keep.drop_duplicates("entrytag_name").set_index("entrytag_name")["entrytag_id"]
copies["keep"] = copies["entrytag_name"].map(keep)

# is the copy we keep the lowest id?
lowest = copies.groupby("entrytag_name")["entrytag_id"].min()
print((keep == lowest).sum(), "of", len(keep), "names: the copy we keep is the lowest id")
print(copies.groupby("entrytag_name")["in_system"].any().value_counts().rename("some copy in the system"))

# merge: every copy becomes the one we keep
merge = dict(zip(copies["entrytag_id"], copies["keep"]))
merged = religious.assign(entrytag_id=religious["entrytag_id"].replace(merge))

# (1) again: tags carried by at least 10 group entries, and group entries with such a tag
n_merged = merged.groupby(["entrytag_id", "entrytag_name"])["entry_id"].nunique().sort_values(ascending=False)
common_merged = n_merged[n_merged >= 10]
matched_merged = merged.loc[merged["entrytag_id"].isin(common_merged.index.get_level_values("entrytag_id")), "entry_id"].unique()
print(len(common_merged), "tags with >= 10 group entries (before merging:", len(common), ")")
print(len(matched_merged), "of", len(groups), "group entries have such a tag (before merging:", len(matched), ")")

# tags that reach 10 only after merging
new = common_merged[~common_merged.index.get_level_values("entrytag_name").isin(common_names)]
print(new)

# (2) again: the group entries still without such a tag
still = merged[~merged["entry_id"].isin(matched_merged)]
print(still["entry_id"].nunique(), "group entries without such a tag")
print(still["entrytag_name"].value_counts().head(15))

# caution for the hierarchy (not for these counts): the copy in the system is sometimes the small one
n_all = all_tags.groupby("entrytag_id")["entry_id"].nunique()
copies["n_entries"] = copies["entrytag_id"].map(n_all)
kept_small = copies.groupby("entrytag_name").filter(
    lambda g: g.loc[g["entrytag_id"] == g["keep"], "n_entries"].iloc[0] < g["n_entries"].max()
)
print(kept_small[["entrytag_name", "entrytag_id", "entrytag_path", "n_entries", "keep"]].to_string(index=False))
