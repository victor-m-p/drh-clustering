"""
Trying to figure out which entries are unconnected.
"""

import numpy as np
import pandas as pd
import warnings
from fun import calculate_inheritance

warnings.filterwarnings(action="ignore", message="Mean of empty slice")

# 0. setup
question_group = "shg"

# 1. subset relations
from fun import select_relations

df_relations = pd.read_csv("data/spatiotemporal_overlap.csv")
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
df_values = pd.read_csv(f"../data/ML/{question_group}.csv")
df_values["entry_code"] = df_values.index  # for inconsistent answers

# select relations
df_relations_sub = select_relations(
    df_relations=df_relations,
    df_values=df_values,
    entry_metadata=entry_metadata,
    subset_polls=[
        "Religious Group (v5)",
        "Religious Group (v6)",
    ],  # only in group polls
    subset_time=1600,  # only if overlap starts before 1600
)

# this is just 184 total for only groups and only before 1600
df_relations_sub["entry_id_to"].nunique()

# what is the total amount of group entries befoer 1600?
entry_metadata = entry_metadata[
    ["entry_id", "entry_name", "year_from", "year_to", "poll"]
]

entry_subset = entry_metadata[
    (entry_metadata["year_from"] < 1600)
    & (entry_metadata["poll"].isin(["Religious Group (v5)", "Religious Group (v6)"]))
]

# okay, here we have 391 entries
entry_subset["entry_id"].nunique()

# let us find some that are unconnected #
entries_total = entry_subset["entry_id"].unique()
entries_matched = df_relations_sub["entry_id_to"].unique()
entries_unmatched = np.setdiff1d(entries_total, entries_matched)
entry_metadata_missing = entry_metadata[
    entry_metadata["entry_id"].isin(entries_unmatched)
]

len(entries_total)  # 391
len(entries_matched)  # 184
len(entries_unmatched)  # 207

## how many are missing because parent is "NO" ##
# 1) inner join with all of the entries:
shg_question = "A supreme high god is present:"
shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
shg_answers = shg_answers[
    [
        "entry_id",
        "question_id",
        "poll",
        "question_name",
        "parent_question",
        "answer",
        "answer_code",
        "parent_answer_code",
        "answer_implied",
    ]
]
shg_answers = shg_answers[shg_answers["entry_id"].isin(entries_total)]
shg_answers_parent = shg_answers[shg_answers["question_name"] == shg_question]

## how many are NAN (91) from super-questions ##
shg_parent_nan = shg_answers_parent[shg_answers_parent["answer_code"].isna()]

""" examples "NAN" (n=91)
177: Jesus movement 
201: Mediterranean
1505: Sample Religious Group Entry (maybe delete this?)
1945: Theyyam Worshippers
"""

## how many are missing because of "NO" (56) ##
shg_parent_no = shg_answers_parent[shg_answers_parent["answer_code"] == "No"]

""" examples "NO"
217: Roman private religion
775: Jainism
1433: Novatians
1989: Iron Age Celtic Spain and Portugal
"""

## how many are missing because of "Other" (n=15) ##
shg_parent_other = shg_answers_parent[shg_answers_parent["answer_code"] == "Other"]

## how many have "YES" super-question (229) ##
shg_parent_yes = shg_answers_parent[shg_answers_parent["answer_code"] == "Yes"]

## "Yes" to super-question but NAN to all sub-questions (n=14) ##
parent_yes_entries = shg_parent_yes["entry_id"].unique().tolist()
parent_yes = shg_answers[shg_answers["entry_id"].isin(parent_yes_entries)]
parent_yes = parent_yes[parent_yes["parent_question"] == shg_question]
non_nan_count = (
    parent_yes.groupby("entry_id")["answer"].count().reset_index(name="count_not_na")
)
only_nan_count = non_nan_count[non_nan_count["count_not_na"] == 0]

""" examples: 
23: Late Shang Religion
222: Late Classic Lowland Maya
487: Bribri
654: 12th-13th c Cistercians
"""

## Can we find the last ones through linking? ##
non_nan_count = non_nan_count[non_nan_count["count_not_na"] > 0]
non_nan_count_entries = non_nan_count["entry_id"].unique().tolist()

# all of them are in values (sanity check)
df_values[df_values["entry_id"].isin(non_nan_count_entries)]

## how many are not connected to anything ##
# we need to go from 215 --> 184
unique_relations_to_sub = df_relations_sub["entry_id_to"].unique().tolist()
not_in_relations = np.setdiff1d(non_nan_count_entries, unique_relations_to_sub)

## how many of these have some relation?
x = df_relations[df_relations["entry_id_to"].isin(not_in_relations)]


#############################################################

### how many of these are just not in our values data? ###
entries_values = df_values["entry_id"].unique()

## entries unmatched not in values ##
entries_unmatched_not_in_values = np.setdiff1d(entries_unmatched, entries_values)
entries_unmatched_not_in_values
len(entries_unmatched_not_in_values)  # 177 (what; that's like half)

""" n=177 a few examples: 
Some "early" ones: 
23 (Late Shang Religion) has SHG question (yes) but no sub-questions
177 (Jesus Movement) does not have anything in beliefs
198 (Religion in Attica) does not have the question answered
201 (Mediterranean) does not have the question answered
202 (Early Zhou Religion) has SHG question (yes) but only 1 sub-question (that is NAN).
203 (Pre-imperial Chu Religion) has SHG (yes) but no sub-questions
...

Some "late" ones: 
1793 (Monothelitism) has SHG question (No) and therefore no sub-questions
1908 (Buddhist traders) answered in foreign language?
1945 (Theyyam Worshippers) does not have any beliefs answered
1962 (Huayan School) has SHG question (No) and therefore no sub-questions
1989 (Iron age Celtic Spain...) has SHG question (No) and therefore no sub-questions
"""

# take an example (Jesus movement--177)
## NB: this does not have the poll answered (so should not be there).
# another example (Mediterranean--201)


relations_tmp = df_relations[df_relations["entry_id_to"] == 177]  # that's a lot...
relations_tmp = relations_tmp[["entry_id_to", "entry_id_from"]]
relations_tmp = relations_tmp.rename(columns={"entry_id_from": "entry_id"})
relations_tmp = relations_tmp.merge(entry_metadata, on="entry_id")
relations_tmp = relations_tmp[
    relations_tmp["poll"].isin(["Religious Group (v5)", "Religious Group (v6)"])
]
relations_tmp  # should have all of these

### so what goes wrong??? ###
# subset based on polls and time

subset_polls = ["Religious Group (v5)", "Religious Group (v6)"]
entry_metadata = entry_metadata[entry_metadata["poll"].isin(subset_polls)]

subset_time = 1600
entry_metadata = entry_metadata[entry_metadata["year_from"] < subset_time]
entry_metadata = entry_metadata[["entry_id"]].drop_duplicates()

# so far so good I think.
entry_metadata_from = entry_metadata.rename(columns={"entry_id": "entry_id_from"})
entry_metadata_to = entry_metadata.rename(columns={"entry_id": "entry_id_to"})
df_relations = df_relations.merge(entry_metadata_from, on="entry_id_from", how="inner")
df_relations = df_relations.merge(entry_metadata_to, on="entry_id_to", how="inner")
df_relations[df_relations["entry_id_to"] == 177]

# okay, we still have it here.

# inner join with values data
df_values_idx = df_values[["entry_id", "entry_code"]].drop_duplicates()

df_values_from_idx = df_values_idx.rename(
    columns={"entry_id": "entry_id_from", "entry_code": "entry_code_from"}
)

df_values_to_idx = df_values_idx.rename(
    columns={"entry_id": "entry_id_to", "entry_code": "entry_code_to"}
)

df_values_from_idx  # no 177 because this is just not answered at all...


df_relations = df_relations.merge(df_values_from_idx, on="entry_id_from", how="inner")
df_relations[df_relations["entry_id_to"] == 177]

df_relations = df_relations.merge(df_values_to_idx, on="entry_id_to", how="inner")
df_relations[df_relations["entry_id_to"] == 177]

## okay, seems like we should be able to connect some
## just through the groups as well ...
## not even counting the texts or places ...

### how many can we connect by using texts? ###
## --> potentially just to "build the bridge" between polls

### how many can we connect by using all polls? ###
## --> this requires that we "build the bridge" between polls

### did we already try to connect to the nearest? ###
