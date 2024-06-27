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
