import numpy as np
import pandas as pd

""" 
Take out relevant columns.

n=287.135
"""
data = pd.read_csv("../data/dump/raw_data.csv")
data = data.rename(columns={"value": "answer_value"})

answers = data[
    [
        "poll",
        "entry_id",
        "question_id",
        "question_name",
        "parent_question_id",
        "parent_question",
        "answer",
        "answer_value",
    ]
].drop_duplicates()

base_question_id = 0
answers["parent_question_id"] = (
    answers["parent_question_id"].fillna(base_question_id).astype(int)
)

""" 
Related questions. 
For each question (id) find the related question (id) in the "Religious Group (v6)" poll.
This is important for subsetting questions from various polls that correspond 
to each other, but might be named differently. 

n=220.100
"""

question_relation = pd.read_csv("../data/dump/question_relation.csv")
question_id_poll = answers[["question_id", "poll"]].drop_duplicates()

from functions_answers import map_question_relation

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


""" 
Select:
- "A supreme high god is present:"
- "Is supernatural monitoring present:"
and all their child questions. 

n=21.688
"""

from constants import question_coding

short_question_names = pd.DataFrame(
    list(question_coding.items()), columns=["question_name", "question_short"]
)

answers_question_name = answers.merge(
    short_question_names, on="question_name", how="inner"
)

# the names match group (v6) so we extract the question IDs from here
# and then we merge on the original "questions" dataframe.
question_id_group_6 = answers_question_name[
    answers_question_name["poll"] == "Religious Group (v6)"
]
question_id_group_6 = question_id_group_6["question_id"].unique().tolist()
answers_subset = answers[answers["related_question_id"].isin(question_id_group_6)]

# now we drop question_id and rename related_question_id
answers_subset = answers_subset.drop(columns=["question_id"])
answers_subset = answers_subset.rename(columns={"related_question_id": "question_id"})

# take the parent-child mappings from group (v6)
parent_mapping_v6 = answers_subset[answers_subset["poll"] == "Religious Group (v6)"]
parent_mapping_v6 = parent_mapping_v6[
    ["question_id", "parent_question_id"]
].drop_duplicates()
answers_subset = answers_subset.drop(columns=["parent_question_id"])
answers_subset = answers_subset.merge(parent_mapping_v6, on="question_id", how="inner")

""" 
Select 
- Religious Group (v5)
- Religious Group (v6)
- Religious Text (v1.0)
as these are the only polls with all of the questions we are interested in.

n = 19.240
"""

from constants import polls

answers_subset = answers_subset[answers_subset["poll"].isin(polls)]
len(answers_subset)

""" 
Fill in missing values with np.nan.
We need this because if the parent question is not "Yes" 
The child will not be present. 

n = 38.047
"""

from functions_answers import unique_combinations

combination_list = []
for df_poll in answers_subset["poll"].unique():
    poll_subset = answers_subset[answers_subset["poll"] == df_poll]
    unique_columns = [
        "poll",
        "question_id",
        "question_name",
        "parent_question_id",
        "parent_question",
    ]
    poll_combinations = unique_combinations(poll_subset, unique_columns)
    combination_list.append(poll_combinations)
answers_subset = pd.concat(combination_list)

""" 
When a child question is missing and the parent answer is "No",
Then we infer that the child question is also "No". 

n = 38.047
-2: 9633
-1: 1749
0: 14.737
1: 11.928
"""


### assign question level ###
questions_levels = answers_subset[
    ["question_id", "parent_question_id"]
].drop_duplicates()

placeholder_value = 100
questions_levels["question_level"] = placeholder_value

# traverse up the hierarchy until base question is found
for i, row in questions_levels.iterrows():
    question_id = row["question_id"]
    parent_question_id = row["parent_question_id"]
    level = 0
    while parent_question_id != base_question_id:
        question_id = parent_question_id
        parent_question_id = questions_levels.loc[
            questions_levels["question_id"] == question_id, "parent_question_id"
        ].values[0]
        level += 1
    questions_levels.loc[i, "question_level"] = level

assert questions_levels[questions_levels["question_level"] == placeholder_value].empty

# merge
answers_subset = answers_subset.merge(
    questions_levels, on=["question_id", "parent_question_id"], how="inner"
)

### then fill in missing "No" answers for child questions ###
nan_placeholder = -2
no_value = 0
answers_subset = answers_subset.sort_values(["question_id", "question_level"])
answers_subset["answer_value"] = (
    answers_subset["answer_value"].fillna(nan_placeholder).astype(int)
)
answers_subset["answer_inferred"] = "False"

for i, row in answers_subset.iterrows():
    # if base level or answer is not missing then continue
    if (
        row["question_level"] == base_question_id
        or row["answer_value"] != nan_placeholder
    ):
        continue

    # else find the parent answer(s)
    else:
        parent_row = answers_subset[
            (answers_subset["entry_id"] == row["entry_id"])
            & (answers_subset["question_id"] == row["parent_question_id"])
        ]

        # we need comparable format for unique parent answers
        # whether there is one or multiple
        unique_parent_answers = parent_row["answer_value"].unique()
        if isinstance(unique_parent_answers, int):
            unique_parent_answers = [unique_parent_answers]

        # if there is a no parent answer then change child value
        if no_value in unique_parent_answers:
            answers_subset.loc[i, "answer_value"] = no_value
            answers_subset.loc[i, "answer_inferred"] = "True"

answers_subset[answers_subset["answer_inferred"] == "True"]
