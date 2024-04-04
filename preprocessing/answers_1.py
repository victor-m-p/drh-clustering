"""
vmp 2023-04-04
"""

import pandas as pd
from helper_functions import check_data

""" 
Take out relevant columns.

answer_value coded as: 
1: Ye
0: No
-1: Field doesn't know / I don't know (we recode this to np.nan)

n answers = 276.239 (many values before subsetting questions)
n entries = 1.288
"""

# load data
data = pd.read_csv("../data/raw/raw_data.csv")
data = data.rename(columns={"value": "answer_value"})

# take out the relevant columns
answers = data[
    [
        "poll",
        "entry_id",
        "question_id",
        "question_name",
        "parent_question_id",
        "answer_value",
    ]
].drop_duplicates()

# fillna with placeholder value to convert to int
answers["parent_question_id"] = answers["parent_question_id"].fillna(0).astype(int)
check_data(answers)

""" 
Related questions. 
For each question (id) find the related question (id) in the "Religious Group (v6)" poll.
This is important for subsetting questions from various polls that correspond 
to each other, but might be named differently. 

n answers = 211.925
n entries = 1.288
"""

question_relation = pd.read_csv("../data/raw/question_relation.csv")
question_id_poll = answers[["question_id", "poll"]].drop_duplicates()

from helper_functions import map_question_relation

related_questions = map_question_relation(
    question_id_poll, question_relation, "Religious Group (v6)"
)

# correct mistake:
related_questions.loc[
    related_questions["question_id"] == 8002, "related_question_id"
] = 4838

# sanity check
assert len(related_questions) == related_questions["question_id"].nunique()

# merge to get related questions
answers = answers.merge(related_questions, on=["question_id", "poll"], how="inner")

check_data(answers)

""" 
Select all of the questions in "question_coding".

These are: 
- "A supreme high god is present:"
- "Is supernatural monitoring present:"
and most of their child questions. 

n answers = 21.687 (1: 12.987, 0: 6.661, -1: 2.039)
n entries = 1.247
"""

from constants import question_coding

short_question_names = pd.DataFrame(
    list(question_coding.items()), columns=["question_name", "question_short"]
)

answers_question_name = answers.merge(
    short_question_names, on="question_name", how="inner"
)

# the names match group (v6) so we extract the question IDs from here
# and then we merge on the original "answers" dataframe.
# this gives us the relevant questions from all polls
question_id_group_6 = answers_question_name[
    answers_question_name["poll"] == "Religious Group (v6)"
]
question_id_group_6 = question_id_group_6["question_id"].unique().tolist()
answers_subset = answers[answers["related_question_id"].isin(question_id_group_6)]
check_data(answers_subset)

""" 
Add back the short question names 
"""

# now add back the short question names
short_question_names = answers_question_name[
    ["related_question_id", "question_short"]
].drop_duplicates()
answers_subset = answers_subset.merge(
    short_question_names, on="related_question_id", how="inner"
)

""" 
Select only relevant polls: 
- Religious Group (v5)
- Religious Group (v6)
- Religious Text (v1.0)

n answers = 19.239 (1: 11.927, 0: 5.563, -1: 1749)
n entries = 974
"""

from constants import polls

answers_subset = answers_subset[answers_subset["poll"].isin(polls)]
check_data(answers_subset)

""" 
Select only sub-questions for the two main questions: 
- "A supreme high god is present:" (4828)
- "Is supernatural monitoring present:" (4954)

And only select the ones where the parent question was answered with "Yes".

n answers = 16.560 (1: 9.910, 0: 5.043, -1: 1.607)
n entries = 685
"""

# to subset based on parent_question_id we need related_parent_question_id
parent_mapping_v6 = answers_subset[answers_subset["poll"] == "Religious Group (v6)"]
parent_mapping_v6 = parent_mapping_v6[
    ["related_question_id", "parent_question_id"]
].drop_duplicates()
parent_mapping_v6 = parent_mapping_v6.rename(
    columns={"parent_question_id": "related_parent_question_id"}
)
answers_subset = answers_subset.merge(
    parent_mapping_v6, on="related_question_id", how="inner"
)

# now take only subquestions of the two main questions
# and only when parents are answered "Yes" (1)
parent_questions = [4828, 4954]
parent_answers = answers_subset[
    answers_subset["related_question_id"].isin(parent_questions)
]
parent_answers = parent_answers[
    ["entry_id", "related_question_id", "answer_value"]
].drop_duplicates()
parent_answers_yes = parent_answers[parent_answers["answer_value"] == 1]
parent_answers_yes = parent_answers_yes.drop(columns=["answer_value"])
parent_answers_yes = parent_answers_yes.rename(
    columns={"related_question_id": "related_parent_question_id"}
)
answers_subset = answers_subset.merge(
    parent_answers_yes, on=["entry_id", "related_parent_question_id"], how="inner"
)
check_data(answers_subset)

""" 
Clean inconsistent answers (manually coded).
I have also manually coded inconsistent parent questions although they are not used here.

n answers = 16.531 (1: 9.905, 0: 5.034, -1: 1.592)
n entries = 685
"""

from constants import correct_answers

correct_answers = pd.DataFrame(
    correct_answers, columns=["entry_id", "question_id", "answer_value"]
)

merged_answers = pd.merge(
    answers_subset,
    correct_answers,
    on=["entry_id", "question_id"],
    how="left",
    suffixes=("", "_small"),
)

df_filtered = merged_answers[
    (merged_answers["answer_value"] == merged_answers["answer_value_small"])
    | merged_answers["answer_value_small"].isnull()
]
assert len(df_filtered) <= len(answers_subset)
answers_subset = df_filtered.drop(columns=["answer_value_small"])
check_data(answers_subset)

""" 
Fill in missing values with np.nan 

n answers = 24.666 (1: 9.905, 0: 5.034, NaN: 9.727) 
n entries = 685
"""

# rename to related
answers_subset = answers_subset.drop(columns=["question_id", "parent_question_id"])
answers_subset = answers_subset.rename(
    columns={
        "related_question_id": "question_id",
        "related_parent_question_id": "parent_question_id",
    }
)

from helper_functions import unique_combinations

combination_list = []
for df_poll in answers_subset["poll"].unique():
    poll_subset = answers_subset[answers_subset["poll"] == df_poll]
    unique_columns = [
        "poll",
        "question_id",
        "parent_question_id",
        "question_name",
    ]
    poll_combinations = unique_combinations(
        df=poll_subset,
        unique_columns=unique_columns,
        entry_column="entry_id",
        question_column="question_id",
    )
    combination_list.append(poll_combinations)
answers_subset = pd.concat(combination_list)

# recode -1 to np.nan
answers_subset["answer_value"] = answers_subset["answer_value"].replace(-1, pd.NA)
check_data(answers_subset)

""" 
Now we assign weight to the data:
weight = 1 / number of answers for the same entry_id and question_id

n answers = 24.666 (1: 9.905, 0: 5.034, NaN: 9.727)
n entries = 685
"""

from helper_functions import assign_weight

answers_subset = assign_weight(answers_subset, "entry_id", "question_id")
answers_subset.to_csv("../data/preprocessed/answers_subset.csv", index=False)
check_data(answers_subset)

""" 
Now we split data into two subsets: 
- subquestions of "A supreme high god is present:" (shg)
- subquestions of "Is supernatural monitoring present:" (monitoring)

shg answers = 10.963 (1: 3787, 0: 3451, NaN: 3725)
shg entries = 685

monitoring answers = 13.703 (1: 6118, 0: 1583, NaN: 6002)
monitoring entries = 685
"""

shg = answers_subset[answers_subset["parent_question_id"] == 4828]
monitoring = answers_subset[answers_subset["parent_question_id"] == 4954]
check_data(shg)
check_data(monitoring)

""" 
Then we expand the data to have one row per entry_id with all the answers.
The function removes entries that have all NaN values on answers. 

shg entries = 559
monitoring entries = 526
"""

from helper_functions import expand_data

shg_expanded = expand_data(shg, "question_id", "entry_id")
monitoring_expanded = expand_data(monitoring, "question_id", "entry_id")

# check amount of data
shg_expanded["entry_id"].nunique()
monitoring_expanded["entry_id"].nunique()

# save
shg_expanded.to_csv("../data/preprocessed/shg_expanded.csv", index=False)
monitoring_expanded.to_csv("../data/preprocessed/monitoring_expanded.csv", index=False)
