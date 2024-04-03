"""
VMP 13-08-2023:

Weighting inconsistent answers.
Apply the following logic:

if inconsistent answers (e.g. yes/no) weight according to the
amount of yes/no in the data. If either a yes/no answer exists 
then drop rows with np.nan (missing answers or "don't know").
"""

import numpy as np
import pandas as pd


# Function to handle each group
def process_group(group):
    mean_value = group["answer_numeric"].mean()
    entry_id = int(group["entry_id"].iloc[0])
    question_id = int(group["question_id"].iloc[0])

    if pd.isna(mean_value):  # all answers are NaN
        return pd.DataFrame(
            {
                "entry_id": [entry_id],
                "question_id": [question_id],
                "answer_numeric": [np.nan],
                "weight": [1],
            }
        )  # Changed weight to 1
    elif mean_value == 0:
        return pd.DataFrame(
            {
                "entry_id": [entry_id],
                "question_id": [question_id],
                "answer_numeric": [0.0],
                "weight": [1],
            }
        )
    elif mean_value == 1:
        return pd.DataFrame(
            {
                "entry_id": [entry_id],
                "question_id": [question_id],
                "answer_numeric": [1.0],
                "weight": [1],
            }
        )
    else:  # 0 < mean_value < 1
        return pd.DataFrame(
            {
                "entry_id": [entry_id, entry_id],
                "question_id": [question_id, question_id],
                "answer_numeric": [1.0, 0.0],
                "weight": [mean_value, 1 - mean_value],
            }
        )


def weight_inconsistent_answers(answers: pd.DataFrame) -> pd.DataFrame:
    """weight answers given inconsistency

    Args:
        answers (pd.DataFrame): answers dataframe

    Returns:
        pd.DataFrame: answers dataframe with weight column
    """

    subset = answers[["entry_id", "question_id", "answer_numeric"]]
    grouped = subset.groupby(["entry_id", "question_id"], as_index=False)
    result = pd.concat(
        [process_group(group) for _, group in grouped], ignore_index=True
    )
    answers_weighted = answers.merge(
        result, on=["entry_id", "question_id", "answer_numeric"], how="inner"
    )
    return answers_weighted


import pandas as pd


def expand_temporal_window(id_meta, time_window):
    min_start_year = id_meta["start_year"].min()
    max_end_year = id_meta["end_year"].max()

    start_boundary = (min_start_year // time_window) * time_window - time_window
    end_boundary = (max_end_year // time_window + 1) * time_window

    expanded_data = []

    for index, row in id_meta.iterrows():
        for year in range(start_boundary, end_boundary, time_window):
            if year + (time_window - 1) < row["start_year"] or year > row["end_year"]:
                continue

            expanded_data.append(
                {
                    "entry_id": row["entry_id"],
                    "world_region": row["world_region"],
                    "time_slice_start": year,
                }
            )

    expanded_df = pd.DataFrame(expanded_data)
    return expanded_df


def calculate_spatiotemporal_weights(group):
    group_size = len(group)
    group["weight"] = 1 / group_size
    return group


def expand_spatiotemporal_weights(
    metadata: pd.DataFrame,
    world_regions: pd.DataFrame,
    id_reference: pd.DataFrame,
    time_window: int,
):
    year_information = metadata[
        ["entry_id", "start_year", "end_year"]
    ].drop_duplicates()
    region_information = world_regions[["entry_id", "world_region"]].drop_duplicates()
    metadata = year_information.merge(region_information, on="entry_id", how="inner")
    entries = id_reference[["entry_id"]].drop_duplicates()
    id_meta = entries.merge(metadata, on="entry_id", how="inner")
    expanded_temporal_window = expand_temporal_window(id_meta, time_window)
    weighted_spatiotemporal_window = expanded_temporal_window.groupby(
        ["world_region", "time_slice_start"]
    ).apply(calculate_spatiotemporal_weights)
    return weighted_spatiotemporal_window
