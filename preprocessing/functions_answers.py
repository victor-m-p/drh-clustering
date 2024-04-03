import pandas as pd
import re
import numpy as np
from itertools import product


def map_question_relation(
    question_id_poll: pd.DataFrame, question_relation: pd.DataFrame, base_poll
):
    """
    Function assumes:
    1. question exists in both related_questions (as either question_id or related_question_id)
    2. question has a relation to a "Religious Group (v6)" question.
    3. the relation exists as a row in the question_relation table (in either direction)
    4. if this is not the case the question will be removed.

    Examples of questions that we remove (because they do not have a relation to group poll v6):

    Loop within Religious Place for instance:
    question_id: 5232, 6336, 5659, 6337, 5660, 5233

    Loop within Religious Text and Religious Place:
    question_id: 8411, 5637, 6061, 6738, 7571
    """

    # merge left
    merge_left = question_id_poll.merge(
        question_relation, on="question_id", how="inner"
    )
    # rename
    question_relation = question_relation.rename(
        columns={
            "question_id": "related_question_id",
            "related_question_id": "question_id",
        }
    )
    # merge right
    merge_right = question_id_poll.merge(
        question_relation, on="question_id", how="inner"
    )
    # concat
    df = pd.concat([merge_left, merge_right])
    # filter
    df = df[df["poll"] == base_poll]
    # remove poll
    df = df.drop(columns="poll")
    # drop duplicates
    df = df.drop_duplicates().reset_index(drop=True)
    # insert missing self-links
    unique_question_ids = df["question_id"].unique()
    unique_related_question_ids = df["related_question_id"].unique()
    missing_related_ids = [
        qid for qid in unique_question_ids if qid not in unique_related_question_ids
    ]
    new_rows = pd.DataFrame(
        {"question_id": missing_related_ids, "related_question_id": missing_related_ids}
    )
    if len(new_rows) > 0:
        df = pd.concat([df, new_rows], ignore_index=True)
    # switch labels
    df = df.rename(
        columns={
            "question_id": "related_question_id",
            "related_question_id": "question_id",
        }
    )
    # now add back in the labels
    df = df.merge(question_id_poll, on="question_id", how="inner")
    # sort by question id
    df = df.sort_values(by=["question_id"])
    # tests
    assert df["related_question_id"].nunique() <= df["question_id"].nunique()

    return df


def code_parent_questions(questions: pd.DataFrame) -> pd.DataFrame:
    """code parent question id as numeric (0 = nan)

    Args:
        questions (pd.DataFrame): dataframe with questions

    Returns:
        pd.DataFrame: dataframe with recoded parent question id
    """
    questions["parent_question_id"] = questions["parent_question_id"].fillna(0)
    questions["parent_question_id"] = questions["parent_question_id"].astype(int)
    return questions


def recode_answer_string(answer: str) -> str:
    """recode answers into "Yes", "No", or "Other"

    Args:
        answer (str): answer string

    Returns:
        str: recoded answer string
    """
    # This is not something that we should actually do.
    # Regular expressions for matching 'yes' or 'no' followed by space or end of string
    yes_pattern = re.compile(r"\byes\b", re.IGNORECASE)
    no_pattern = re.compile(r"\bno\b", re.IGNORECASE)

    if yes_pattern.search(answer):
        return "Yes"
    elif no_pattern.search(answer):
        return "No"
    else:
        return "Other"


def unique_combinations(df: pd.DataFrame, unique_columns: list) -> pd.DataFrame:
    combinations_questions = df[unique_columns].drop_duplicates()
    entry_ids = df["entry_id"].unique()
    question_ids = df["question_id"].unique()
    product_questions_entries = pd.DataFrame(
        product(entry_ids, question_ids), columns=["entry_id", "question_id"]
    )
    combinations_filled = product_questions_entries.merge(
        combinations_questions, on="question_id", how="inner"
    )
    df = combinations_filled.merge(df, on=["entry_id"] + unique_columns, how="left")

    # df >= product because it should have all combinations and some entries
    # will have multiple answers for the same question (or other duplication)
    assert len(df) >= len(entry_ids) * len(question_ids)
    return df


def calculate_question_level(question_id, question_parent_mapping):
    # Base level
    level = 0

    # Traverse up the hierarchy until a question with no parent (parent_question_id == 0) is found
    while question_parent_mapping[question_id] != 0:
        question_id = question_parent_mapping[question_id]
        level += 1
    return level


def assign_question_level(df: pd.DataFrame) -> pd.DataFrame:
    question_parent_mapping = df[
        ["question_id", "parent_question_id"]
    ].drop_duplicates()
    question_parent_mapping = pd.Series(
        question_parent_mapping.parent_question_id.values,
        index=question_parent_mapping.question_id,
    ).to_dict()
    df["question_level"] = df["question_id"].apply(
        lambda q_id: calculate_question_level(q_id, question_parent_mapping)
    )
    return df


def find_parent_answer(row, df):
    if row["question_level"] == 0:
        return np.nan

    # Filter the DataFrame for the parent row
    parent_row = df[
        (df["entry_id"] == row["entry_id"])
        & (df["question_id"] == row["parent_question_id"])
    ]

    # many cases will be nan so check that first
    if parent_row.empty or pd.isna(parent_row.iloc[0]["answer_code"]):
        return np.nan

    # if a "Yes" exists, we should assume that this is the answer that has a sub-question
    sort_order = {"Yes": 0, "Other": 1, "No": 2}

    # Sort the parent_row DataFrame based on the custom sort order
    parent_row_sorted = parent_row.copy()
    parent_row_sorted["sort_key"] = parent_row_sorted["answer_code"].map(sort_order)
    parent_row_sorted = parent_row_sorted.sort_values(by="sort_key")

    # Return the first value from the sorted DataFrame
    return parent_row_sorted.iloc[0]["answer_code"]


def assign_parent_answer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(by="question_level", ascending=True).reset_index(drop=True)
    df["parent_answer_code"] = df.apply(lambda row: find_parent_answer(row, df), axis=1)
    return df


def code_implied_answers(df: pd.DataFrame) -> pd.DataFrame:
    # for testing:
    number_yes_before = df.groupby("answer_code").size()["Yes"]
    number_other_before = df.groupby("answer_code").size()["Other"]
    number_no_before = df.groupby("answer_code").size()["No"]

    df["answer_implied"] = "No"
    df["parent_answer_implied"] = "No"
    df = df.sort_values(by="question_level", ascending=True).reset_index(drop=True)
    for index, row in df.iterrows():
        # If answer_code is NaN and parent's answer_code is "No", then set answer_code to "No"
        if pd.isna(row["answer_code"]) and row["parent_answer_code"] == "No":
            # Set the current row's answer_code and answer_implied
            df.at[index, "answer_code"] = "No"
            df.at[index, "answer_implied"] = "Yes"

            # Propagate to the questions that have the current row's answer as the parent
            parent_indices = df[
                (df["entry_id"] == row["entry_id"])
                & (df["parent_question_id"] == row["question_id"])
            ].index

            # Update the parent_answer_code and parent_answer_implied for all matching rows
            df.loc[parent_indices, "parent_answer_code"] = "No"
            df.loc[parent_indices, "parent_answer_implied"] = "Yes"

    # for testing
    assert number_yes_before == df.groupby("answer_code").size()["Yes"]
    assert number_other_before == df.groupby("answer_code").size()["Other"]
    assert number_no_before <= df.groupby("answer_code").size()["No"]

    return df
