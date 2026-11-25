"""
vmp 2024-06-26
"""

import pandas as pd
from itertools import product
from helper_functions import check_data

""" 
Take out relevant columns.

answer_value coded as: 
1: Ye
0: No
-1: Field doesn't know / I don't know (we recode this to np.nan)

"""

# load data
data = pd.read_csv("../data/sccsrv3/answerset.csv")
check_data(data) # 1687 entries

# take out the relevant columns
answers = data[
    [
        "poll_name",
        "entry_id",
        "question_id",
        "question_name",
        "answer_value",
    ]
].drop_duplicates()

""" 
Related questions. 
For each question (id) find the related question (id) in the "Religious Group (v6)" poll.
This is important for subsetting questions from various polls that correspond 
to each other, but might be named differently. 
"""

question_relation = pd.read_csv("../data/sccsrv3/questionrelation.csv")
answers = answers.merge(question_relation, on=["question_id", "poll_name"], how="inner")

# There is one group of questions where the related question
# matches two types of questions:
# "Has knowledge of this world" and "Has other knowledge of this world"
# We only want the first type
remove_questions = [3240, 4848, 8012]
answers = answers[~answers["question_id"].isin(remove_questions)]

# now drop question_id and rename related
answers = answers.drop(columns=["question_id"])
answers = answers.rename(
    columns={
        "related_question_id": "question_id",
    }
)
check_data(answers) 

"""
n answers = 366150
n entries = 1687

Select all of the questions in "question_coding".

These are: 
- "A supreme high god is present:"
- "Is supernatural monitoring present:"
and most of their child questions. 

"""

from constants import question_coding

# create dataframe with questions of interest and shorthands
short_question_names = pd.DataFrame(
    list(question_coding.items()), columns=["question_id", "question_short"]
)
short_question_names["question_id"] = short_question_names["question_id"].astype(int)
answers_subset = answers.merge(short_question_names, on="question_id", how="inner")
answers_subset = answers_subset.drop(columns=["question_name"])

check_data(answers_subset)

"""
n answers = 24679
n entries = 1272

Select only relevant polls: 
- Religious Group (v5)
- Religious Group (v6)
- Religious Text (v1.0)
"""

from constants import polls

answers_subset = answers_subset[answers_subset["poll_name"].isin(polls)]
check_data(answers_subset)

"""
n answers = 21870
n entries = 867

take only yes-no answers
"""

# take only yes-no answers
answers_subset = answers_subset[answers_subset["answer_value"].isin([0, 1])]
check_data(answers_subset)

""" 
n answers = 19822
n entries = 860

Fill in missing values with np.nan 

n answers = 27.875 (1: 11.621, 0: 5.899, NaN: 10.355) 
n entries = 774
"""

# rename to related
answers_subset.dtypes

# entry_id, question_id #
unique_entries = answers_subset["entry_id"].unique()
unique_questions = answers_subset["question_id"].unique()
product_questions_entries = pd.DataFrame(
    product(unique_entries, unique_questions), columns=["entry_id", "question_id"]
)
# add information
poll_entry = answers_subset[["entry_id", "poll_name"]].drop_duplicates()
question_mapping = answers_subset[["question_id", "question_short"]].drop_duplicates()
product_questions_entries = product_questions_entries.merge(
    poll_entry, on="entry_id", how="inner"
)
product_questions_entries = product_questions_entries.merge(
    question_mapping, on="question_id", how="inner"
)
# now merge with answers
answers_filled = product_questions_entries.merge(
    answers_subset,
    on=["entry_id", "question_id", "poll_name", "question_short"],
    how="left",
)
check_data(answers_filled)

""" 
n rows = 30978
n entries = 860


Now we assign weight to the data:
weight = 1 / number of answers for the same entry_id and question_id

"""

from helper_functions import assign_weight

answers_filled = assign_weight(answers_filled, "entry_id", "question_id")

# sanity check
total_weight = answers_filled["weight"].sum().astype(int)
n_entries = answers_filled["entry_id"].nunique()
n_questions = answers_filled["question_id"].nunique()
assert total_weight == n_entries * n_questions

answers_filled.to_csv("../data/preprocessed/answers_subset_all.csv", index=False)
check_data(answers_filled)

# this we have to do individually for groups #
# also write for only groups
answers_filled_groups = answers_filled[
    answers_filled["poll_name"].str.contains("Group")
].drop(columns="weight")
answers_filled_groups = assign_weight(answers_filled_groups, "entry_id", "question_id")
answers_filled_groups.to_csv(
    "../data/preprocessed/answers_subset_groups.csv", index=False
)

"""
### NEW (2026-10-19): unconditional answers ###

Child questions are only asked when the parent is "Yes":
- 2890 (supernatural monitoring present) -> monitoring questions
- 2893 (supernatural beings present) -> 2919 (supreme high god present) -> shg questions
Here we infer "No" for a child when its parent is "No" (inferred = True),
except for 3218 (permissible to worship other gods), where we infer "Yes".
Not inferred when the parent is answered both "Yes" and "No".
The (conditional) files above are unchanged.

2919 (supreme high god present) is used as answered: no "No" is inferred from 2893 "No" (dropped 2026-11-23).
Many entries with 2893 "No" are Abrahamic (4 of 7 groups, 38 of 50 texts in the 3000 BCE-1500 CE window of
modeling/13_main.Rmd), so their coders probably read "supernatural beings" as beings other than God, and an
inferred "no supreme high god" would be wrong. As a consequence, the shg questions are not inferred for these
entries either (2919 is missing for them).
"""

import numpy as np
from constants import parent_coding, parent_question, infer_yes

assert set(parent_question) - {2919} == set(answers_filled["question_id"])

# parent answers (same selection as for the child questions above)
parent_names = pd.DataFrame(list(parent_coding.items()), columns=["question_id", "question_short"])
parent_names["question_id"] = parent_names["question_id"].astype(int)
parents = answers.merge(parent_names, on="question_id", how="inner").drop(columns=["question_name"])
parents = parents[parents["poll_name"].isin(polls) & parents["answer_value"].isin([0, 1])]
parents["inferred"] = False  # parents are used as answered (no 2893 "No" -> 2919 "No"; see above)
parents = assign_weight(parents, "entry_id", "question_id")

# parent answer per entry: 0 = "No", 1 = "Yes", in between = both
parent_answers = (
    parents.groupby(["entry_id", "question_id"])["answer_value"].mean()
    .reset_index()
    .rename(columns={"question_id": "parent_question_id", "answer_value": "parent_answer"})
)

# add entries that only answered parent questions (all child answers missing)
new_entries = parents.loc[~parents["entry_id"].isin(answers_filled["entry_id"]), ["entry_id", "poll_name"]].drop_duplicates()
new_rows = new_entries.merge(question_mapping, how="cross")
new_rows["weight"] = 1.0
unconditional = pd.concat([answers_filled, new_rows], ignore_index=True)

# infer "No" (or "Yes" for infer_yes) for missing child answers when the parent is "No"
unconditional["parent_question_id"] = unconditional["question_id"].map(parent_question)
unconditional = unconditional.merge(parent_answers, on=["entry_id", "parent_question_id"], how="left")
assert not (unconditional["answer_value"].notna() & (unconditional["parent_answer"] == 0)).any()
unconditional["inferred"] = unconditional["answer_value"].isna() & (unconditional["parent_answer"] == 0)
unconditional.loc[unconditional["inferred"], "answer_value"] = (
    unconditional.loc[unconditional["inferred"], "question_id"].isin(infer_yes).astype(int)
)
unconditional = unconditional.drop(columns=["parent_question_id", "parent_answer"])

# keep entries with at least one answer (new entries without any inferred answer drop out)
unconditional = unconditional[unconditional.groupby("entry_id")["answer_value"].transform("count") > 0]

# sanity checks: undoing the inference gives the conditional data; weights as above
check = unconditional[unconditional["entry_id"].isin(answers_filled["entry_id"])].copy()
check.loc[check["inferred"], "answer_value"] = np.nan
assert check[answers_filled.columns].reset_index(drop=True).equals(answers_filled)
assert round(unconditional["weight"].sum()) == unconditional["entry_id"].nunique() * unconditional["question_id"].nunique()

# save (entries are in one poll each, so weights hold for the groups subset)
unconditional.to_csv("../data/preprocessed/answers_subset_all_unconditional.csv", index=False)
unconditional[unconditional["poll_name"].str.contains("Group")].to_csv(
    "../data/preprocessed/answers_subset_groups_unconditional.csv", index=False
)
parents.to_csv("../data/preprocessed/answers_parents_all.csv", index=False)
parents[parents["poll_name"].str.contains("Group")].to_csv(
    "../data/preprocessed/answers_parents_groups.csv", index=False
)
check_data(unconditional)

### END NEW ###

"""
### NEW (2026-10-19): expert per entry ###

For looking into expert effects (not used in the analyses).
expert_id is not a person id in SCCSR.v3 (one id can have several names, e.g. 708),
so "expert" is the expert name in lower case (this merges e.g. "Ltaief Zorgui" and "ltaief zorgui").
"""

entry_experts = pd.read_csv("../data/sccsrv3/entry_data.csv")
entry_experts = entry_experts[entry_experts["entry_id"].isin(unconditional["entry_id"]) | entry_experts["entry_id"].isin(parents["entry_id"])]
entry_experts = entry_experts[["entry_id", "entry_name", "poll_name", "year_from", "year_to", "expert_id", "expert_name", "editor_name"]]
entry_experts["expert"] = entry_experts["expert_name"].str.lower().str.split().str.join(" ")
entry_experts["n_entries_expert"] = entry_experts.groupby("expert")["entry_id"].transform("count")
entry_experts.to_csv("../data/preprocessed/entry_experts.csv", index=False)

### END NEW ###

""" 
n rows = 30978
n entries = 860

Now we split data into two subsets: 
- subquestions of "A supreme high god is present:" (shg)
- subquestions of "Is supernatural monitoring present:" (monitoring)
"""

# need to sort out the parent question ids for this
# answers_raw = pd.read_csv("../data/sccsrv3/answerset.csv")
# answers_raw = answers_raw[["question_id", "parent_question_id"]].drop_duplicates()

# parents_monitoring = answers_raw[answers_raw["parent_question_id"] == 2890]
# parents_shg = answers_raw[answers_raw["parent_question_id"] == 2919]

# questions_monitoring = parents_monitoring["question_id"].tolist()
# questions_shg = parents_shg["question_id"].tolist()

# shg = answers_filled[answers_filled["question_id"].isin(questions_shg)]
# monitoring = answers_filled[answers_filled["question_id"].isin(questions_monitoring)]

# sanity check
# assert len(shg) + len(monitoring) == len(answers_filled)

# save data
# shg.to_csv("../data/preprocessed/shg_long.csv", index=False)
# monitoring.to_csv("../data/preprocessed/monitoring_long.csv", index=False)

# check_data(shg)
# check_data(monitoring)


from helper_functions import expand_data
groups_expanded = expand_data(answers_filled_groups, "question_id", "entry_id")

# how many total group entries?
groups_expanded["entry_id"].nunique()  # n = 618

# how many complete answer sets
np.sum(groups_expanded.isna().sum(axis=1) == 0)  # n = 193 rows of non-na
groups_unique = groups_expanded.drop_duplicates(subset="entry_id", keep="first")
np.sum(groups_unique.isna().sum(axis=1) == 0)  # n = 177 complete entries

# now remove those that have fewer than 50% answers
n_columns = groups_expanded.shape[1]
n_questions = 36
threshold = 0.5
threshold = n_columns - int(np.round(n_questions * threshold))
groups_threshold = groups_expanded.dropna(thresh=threshold)

# how many observations now?
len(groups_threshold)  # n = 376 rows
groups_threshold["entry_id"].nunique()  # 358 unique groups

# save
groups_threshold.to_csv("../data/preprocessed/groups_expanded.csv", index=False)

# shg_expanded.to_csv("../data/preprocessed/shg_expanded.csv", index=False)
# monitoring_expanded.to_csv("../data/preprocessed/monitoring_expanded.csv", index=False)

unconditional