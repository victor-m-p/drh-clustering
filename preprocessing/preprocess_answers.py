import pandas as pd
import numpy as np
from itertools import product


# read data
data = pd.read_csv("../data/dump/raw_data.csv")

# rename and select columns
data = data.rename(columns={"value": "answer_value"})
questions = data[
    [
        "poll",
        "entry_id",
        "question_id",
        "question_name",
        "parent_question_id",
        "parent_question",
        "answer",
    ]
].drop_duplicates()

#### 1. preprocess answers ####
from functions_answers import (
    code_parent_questions,
    recode_answer_string,
    unique_combinations,
    assign_question_level,
    assign_parent_answer,
    code_implied_answers,
)

## code parent questions
questions = code_parent_questions(questions)

## code answers
questions["answer_code"] = questions["answer"].apply(recode_answer_string)

## do the following for each poll separately ##
"""
NB: could just only use poll, question_id, parent_question_id for the following.
Then we could merge back in question_name, parent_question later. 
We might do that if it is more efficient. 
"""

unique_columns = [
    "poll",
    "question_id",
    "question_name",
    "parent_question_id",
    "parent_question",
]

list_of_dataframes = []
for i in questions["poll"].unique():
    group = questions[questions["poll"] == i]
    group = unique_combinations(group, unique_columns)
    group = assign_question_level(group)
    group = assign_parent_answer(group)
    group = code_implied_answers(group)
    list_of_dataframes.append(group)
questions_cleaned = pd.concat(list_of_dataframes)

# sort out question relations

"""
This needs to happen after the other processing because otherwise we might have removed
rows that are needed to trace answers; for instance, we remove some questions that do
not map to anything in the Religious Group (v6) category. 
"""

question_relation = pd.read_csv("../data/dump/question_relation.csv")
question_id_poll = questions[["question_id", "poll"]].drop_duplicates()

from answers import map_question_relation

related_questions = map_question_relation(
    question_id_poll, question_relation, "Religious Group (v6)"
)

# correct mistake:
related_questions.loc[
    related_questions["question_id"] == 8002, "related_question_id"
] = 4838

related_questions.to_csv("../data/preprocessed/answers_related.csv", index=False)

# merge question relation and answers
questions_meta = questions_cleaned.merge(
    related_questions, on=["question_id", "poll"], how="inner"
)

# write data
questions_meta.to_csv("../data/preprocessed/answers.csv", index=False)
