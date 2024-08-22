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
data = pd.read_csv("../data/raw/answerset.csv")
check_data(data)

"""
n answers = 364.376 (many values before subsetting questions)
n entries = 1.578
"""

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

question_relation = pd.read_csv("../data/raw/questionrelation.csv")
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
n answers = 347.453
n entries = 1.578

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
n answers = 23.374
n entries = 1.213

Select only relevant polls: 
- Religious Group (v5)
- Religious Group (v6)
- Religious Text (v1.0)
"""

from constants import polls

answers_subset = answers_subset[answers_subset["poll_name"].isin(polls)]
check_data(answers_subset)

"""
n answers = 20.734
n entries = 824

take only yes-no answers
"""

# take only yes-no answers
answers_subset = answers_subset[answers_subset["answer_value"].isin([0, 1])]

check_data(answers_subset)

""" 
n answers = 18.847
n entries = 817

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
n rows = 29.430
n entries = 817


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
n rows = 29430
n entries = 817

Now we split data into two subsets: 
- subquestions of "A supreme high god is present:" (shg)
- subquestions of "Is supernatural monitoring present:" (monitoring)
"""

# need to sort out the parent question ids for this
# answers_raw = pd.read_csv("../data/raw/answerset.csv")
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
import numpy as np

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
