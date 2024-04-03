"""
VMP 2023-02-26:
This script is used to weight inconsistent answers. The logic is as follows:
For each (entry_id, question_id, expert_id) group we take most recent answer.
If there is still both yes/no with same (most recent) date, take both.
If there is only either (yes/no) and (other/nan) take (yes/no).
If there is only (other/nan) and (other/nan) take (other/nan).
Add weight to (entry_id, question_id) pairs. 
"""

import numpy as np
import pandas as pd
from constants import question_coding

# import answers data
answers = pd.read_csv("../data/preprocessed/answers.csv")

# create dataframe from constant (dictionary)
question_coding_df = pd.DataFrame(
    list(question_coding.items()), columns=["question_name", "question_short"]
)

# find the related question ids
# this is the problem: we are merging on question name here ....
answers_question_name = answers.merge(
    question_coding_df, on="question_name", how="inner"
)

related_questions_short = (
    answers_question_name[["related_question_id", "question_short"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

assert len(related_questions_short) == len(question_coding_df)
assert (
    related_questions_short["related_question_id"].nunique()
    == question_coding_df["question_name"].nunique()
)

# now merge this in (inner) to get the SHG subset
shg_questions = answers.merge(
    related_questions_short, on="related_question_id", how="inner"
)

# resolve incompatible answers:

""" 
idea is to do this for each expert on the entry. 
take the most recently provided answer (often previous answers have been corrected).
if there is still both yes/no with same (most recent) date, take both.
if there is only either (yes/no) and (other/nan) take (yes/no).
"""

# need raw data here to get per-question expert
raw_data = pd.read_csv("../data/dump/raw_data.csv")

data_history = raw_data[
    ["entry_id", "question_id", "answer", "expert_id", "date_modified"]
].drop_duplicates()

shg_resolved = shg_questions.merge(
    data_history, on=["entry_id", "question_id", "answer"], how="left"
)

shg_resolved.sort_values(
    by=["entry_id", "question_id", "expert_id", "date_modified"],
    ascending=[True, True, True, False],
    inplace=True,
)

# in cases where answer is NAN we get NAN for expert_id
# for our purposes, fine to just fill with "missing".
shg_resolved["expert_id"] = shg_resolved["expert_id"].fillna("missing")


# Step 2: Apply custom logic
def filter_rows(group):
    if len(group) == 1:  # I think it errors here.
        return group
    else:
        # Take the most recent value based on 'date_modified'
        top_date = group["date_modified"].iloc[0]
        top_group = group[group["date_modified"] == top_date]

        # If there is both a 'Yes' and a 'No', keep both
        if (
            "Yes" in top_group["answer_code"].values
            and "No" in top_group["answer_code"].values
        ):
            return top_group

        # If there's a tie and one is 'Yes' or 'No', select only that
        yes_no_rows = top_group[top_group["answer_code"].isin(["Yes", "No"])]
        if not yes_no_rows.empty:
            return yes_no_rows

        # If still multiple values, keep them
        return top_group


# Step 3: Apply the function to each group
shg_resolved = (
    shg_resolved.groupby(["entry_id", "question_id", "expert_id"])
    .apply(filter_rows)
    .reset_index(drop=True)
)

# remove some columns
shg_resolved = shg_resolved.drop(columns=["expert_id", "date_modified"])
shg_resolved = shg_resolved.drop_duplicates().reset_index(drop=True)

shg_resolved.groupby(["entry_id", "question_id"]).size().reset_index(
    name="count"
).sort_values(["count", "entry_id"], ascending=[False, True])

# recode "Yes"==1, "No"==1, "Other==np.nan".
shg_resolved["answer_numeric"] = shg_resolved["answer_code"].replace(
    {"Yes": 1, "No": 0, "Other": np.nan}
)

# now add weights (e.g., if "Yes" and "No" give 0.5 weight)
from functions_weighting import weight_inconsistent_answers

shg_weighted = weight_inconsistent_answers(shg_resolved)

# save this
shg_weighted.to_csv("../data/preprocessed/shg_answers.csv", index=False)
