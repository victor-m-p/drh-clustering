import pandas as pd
import numpy as np
from itertools import product


def expand_data(unique_entries, df, question_column):
    expanded_data = []
    for entry in unique_entries:
        subset = df[df["entry_id"] == entry]
        unique_questions = subset[question_column].unique()

        # Iterate through unique question_ids with more than one answer
        combinations = [
            subset[subset[question_column] == q][
                ["answer_numeric", "weight"]
            ].values.tolist()
            for q in unique_questions
        ]
        for combination in product(*combinations):
            row_data = {"entry_id": entry}
            weight_product = 1
            for i, (answer, weight) in enumerate(combination):
                question_col_name = f"Q{unique_questions[i]}"
                row_data[question_col_name] = answer
                weight_product *= weight
            row_data["weight"] = weight_product
            expanded_data.append(row_data)

    # Create the new DataFrame from the expanded data
    expanded_df = pd.DataFrame(expanded_data)

    # Reorder columns
    columns_order = (
        ["entry_id"]
        + [f"Q{q_id}" for q_id in sorted(df[question_column].unique())]
        + ["weight"]
    )
    expanded_df = expanded_df.reindex(columns=columns_order)

    # Fill NaN for missing columns
    expanded_df = expanded_df.fillna(np.nan)

    # drop columns that are all nan
    answer_columns = [
        col for col in expanded_df.columns if col not in ["entry_id", "weight"]
    ]
    expanded_df = expanded_df.dropna(subset=answer_columns, how="all")

    return expanded_df


# load cleaned shg answers
shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
answers_related = pd.read_csv("../data/preprocessed/answers_related.csv")

# for now only in relevant polls that have answers for all questions
polls = ["Religious Group (v5)", "Religious Group (v6)", "Religious Text (v1.0)"]
shg_answers = shg_answers[shg_answers["poll"].isin(polls)]
shg_answers["entry_id"].nunique()  # 1015 (down from 1288)

# find the related question ids for the relevant subsets
## related question id for shg == 4828
## related question id for monitoring == 4954
shg_parent_id = answers_related[answers_related["related_question_id"] == 4828][
    "question_id"
].unique()
monitoring_parent_id = answers_related[answers_related["related_question_id"] == 4954][
    "question_id"
].unique()

# create two different datasets
shg = shg_answers[shg_answers["parent_question_id"].isin(shg_parent_id)]
monitoring = shg_answers[shg_answers["parent_question_id"].isin(monitoring_parent_id)]

# check whether we are missing entries
assert shg["entry_id"].nunique() == shg_answers["entry_id"].nunique()
assert monitoring["entry_id"].nunique() == shg_answers["entry_id"].nunique()

# check whether we are missing entry/question pairs
assert shg.groupby("entry_id").size().min() >= 16  # 16 = n questions for shg
assert (
    monitoring.groupby("entry_id").size().min() >= 20
)  # 20 = n questions for monitoring


"""
NB: come back and check up on whether it is reasonable that monitoring[
    (monitoring["entry_id"] == 2111) & (monitoring["question_id"]==4954)
]we have
so little inconsistency in the answers.
For monitoring we have n=20 for all entries. 
"""

# now take only parent == Yes
shg = shg[shg["parent_answer_code"] == "Yes"]
shg["entry_id"].nunique()  # 1015 --> 597

monitoring = monitoring[monitoring["parent_answer_code"] == "Yes"]
monitoring["entry_id"].nunique()  # 1015 --> 567

# turn into a weighted matrix
shg = shg[["entry_id", "related_question_id", "answer_numeric", "weight"]]
monitoring = monitoring[["entry_id", "related_question_id", "answer_numeric", "weight"]]

# now weight this
shg_unique_entries = shg["entry_id"].unique()
monitoring_unique_entries = monitoring["entry_id"].unique()
shg_expanded = expand_data(shg_unique_entries, shg, "related_question_id")
shg_expanded["entry_id"].nunique()  # 597 --> 556

monitoring_expanded = expand_data(
    monitoring_unique_entries, monitoring, "related_question_id"
)
monitoring_expanded["entry_id"].nunique()  # 567 --> 525

# now save these datasets for modeling
shg_expanded.to_csv("../data/ML/shg.csv", index=False)
monitoring_expanded.to_csv("../data/ML/monitoring.csv", index=False)
