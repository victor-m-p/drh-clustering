import pandas as pd

answers = pd.read_csv("../data/raw/answerset.csv")

# extract the relevant question
social_complexity = answers[
    answers["question_name"]
    == "The society to which the religious group belongs is best characterized as (please choose one):"
]

# take relevant columns
social_complexity = social_complexity[
    ["entry_id", "entry_name", "question_id", "question_name", "answer"]
].drop_duplicates()

# read the social complexity recode table
social_complexity_recode = pd.read_csv("../data/raw/social_complexity_recode.csv")
social_complexity_recode = social_complexity_recode.drop(columns=["notes"])

# take answer from social complexity recode where it exists
# Merge the two dataframes on 'entry_id' and 'question_name' using an outer join
df_merged = pd.merge(
    social_complexity,
    social_complexity_recode,
    on=["entry_id", "entry_name", "question_id", "question_name"],
    how="left",
    suffixes=("", "_recode"),
)

# Use the 'answer_value' from literacy recode where it exists
df_merged["answer"] = df_merged["answer_recode"].combine_first(df_merged["answer"])

# Drop the auxiliary 'answer_value_small' column
df_result = df_merged.drop(columns=["answer_recode"])

# Group into small-scale and large-scale
recoding_dictionary = {
    "A band": 0,  # small scale
    "A chiefdom": 0,  # small scale
    "A tribe": 0,  # small scale
    "A state": 1,  # large scale
    "An empire": 1,  # large scale
    "Un estado": 1,  # large scale
}
df_result["social_complexity_large"] = df_result["answer"].map(recoding_dictionary)

# drop cases that do not have relevant answer
df_clean = df_result.dropna(subset=["social_complexity_large"])

# drop original answer to remove duplication
df_clean = df_clean.drop(columns=["answer"])
df_clean = df_clean.drop_duplicates()

# now take only the ones in our sample
answers_groups = pd.read_csv("../data/preprocessed/answers_subset_groups.csv")
answers_groups = answers_groups[["entry_id"]].drop_duplicates()
df_clean = df_clean.merge(answers_groups, on="entry_id", how="inner")

# check remaining inconsistency
df_inconsistency = (
    df_clean.groupby("entry_id")
    .size()
    .reset_index(name="count")
    .sort_values(by="count")
)
df_inconsistency = df_inconsistency[df_inconsistency["count"] > 1]

# we have n=4 cases of remaining inconsistency
inconsistent_entries = df_result[
    df_result["entry_id"].isin(df_inconsistency["entry_id"])
]

"""
Mesopotamian city-state cults... (479) is "A state" and "A tribe"
Pasupatas (535) is "A chiefdom" and "An empire" and "A state"
Wahhabisme (1805) is "A band" and "An empire"
Inka and non-Inka groups in Cusco, Peru (2240) is "A chiefdom" and "An empire"
"""

# drop these cases from the analysis
df_clean = df_clean[~df_clean["entry_id"].isin(df_inconsistency["entry_id"])]
df_clean.to_csv("social_complexity.csv", index=False)
