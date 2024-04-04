# come back and document this

import pandas as pd
from itertools import product
import numpy as np


def check_data(df):
    n_rows = len(df)
    unique_entries = df["entry_id"].nunique()
    answer_distribution = df.groupby("answer_value", dropna=False).size()
    print(f"Number of rows: {n_rows}")
    print(f"Unique entries: {unique_entries}")
    print(f"Answer distribution: {answer_distribution}")


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


def unique_combinations(
    df: pd.DataFrame, unique_columns: list, entry_column: str, question_column: str
) -> pd.DataFrame:
    """
    Unique combinations of entries and questions.
    Fills in missing combinations with NaNs.
    """
    combinations_questions = df[unique_columns].drop_duplicates()
    entry_ids = df[entry_column].unique()
    question_ids = df[question_column].unique()
    product_questions_entries = pd.DataFrame(
        product(entry_ids, question_ids), columns=[entry_column, question_column]
    )
    combinations_filled = product_questions_entries.merge(
        combinations_questions, on=question_column, how="inner"
    )
    df = combinations_filled.merge(df, on=[entry_column] + unique_columns, how="left")

    # df >= product because it should have all combinations and some entries
    # will have multiple answers for the same question (or other duplication)
    assert len(df) >= len(entry_ids) * len(question_ids)
    return df


def assign_weight(df, entry_column, question_column):
    # Group by 'entry_id' and 'question_id' and calculate the size of each group
    counts = df.groupby([entry_column, question_column]).size()

    # Map the counts to a new 'weight' column, taking the reciprocal of the count
    df["weight"] = df.set_index([entry_column, question_column]).index.map(
        lambda x: 1 / counts[x]
    )

    # Reset the index if you had set it earlier
    df.reset_index(drop=True, inplace=True)

    return df


def expand_data(df, question_column, entry_column):
    unique_entries = df[entry_column].unique().tolist()
    unique_questions = df[question_column].unique().tolist()
    expanded_data = []
    for entry in unique_entries:
        subset = df[df["entry_id"] == entry]
        # Iterate through unique question_ids with more than one answer
        combinations = [
            subset[subset[question_column] == q][
                ["answer_value", "weight"]
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


def mode_feature_by_entry(df, entry_column, feature_columns):
    # Ensure feature_columns is a list, even if it's a single column name
    if not isinstance(feature_columns, list):
        feature_columns = [feature_columns]

    # Group by entry_column and feature_columns and count occurrences
    group_columns = [entry_column] + feature_columns
    df_features = df.groupby(group_columns).size().reset_index(name="count")

    # Sort by entry_column and count, then drop duplicates based on entry_column
    sorted_df = df_features.sort_values(
        by=[entry_column, "count"], ascending=[True, False]
    )
    dedup_df = sorted_df.drop_duplicates(subset=entry_column)
    dedup_df = dedup_df.drop(columns=["count"])

    # Count the number of unique combinations for each entry_column
    unique_count_df = df_features.groupby(entry_column).size().reset_index(name="count")
    unique_count_df = unique_count_df.drop(columns=["count"])

    # merge with dedup_df
    final_df = dedup_df.merge(unique_count_df, on=entry_column)

    # Testing
    assert df[entry_column].nunique() == len(final_df)
    return final_df
