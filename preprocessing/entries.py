import pandas as pd


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
    unique_count_df["unique"] = unique_count_df["count"] == 1
    unique_count_df = unique_count_df.drop(columns=["count"])

    # merge with dedup_df
    final_df = dedup_df.merge(unique_count_df, on=entry_column)

    # Testing
    assert df[entry_column].nunique() == len(final_df)
    return final_df


def get_social_scale(answer):
    """
    New choices:
    A nation-state: large-scale

    Make a choice here:
    A city-state?
    A Faith elect?
    A Spiritual Elect?
    A Segmentary Lineage?
    A House society?
    (and some others).
    """

    if answer in ["A band", "A tribe", "A chiefdom"]:
        return "small-scale"
    elif answer in ["A state", "A nation-state", "An empire"]:
        return "large-scale"
    elif answer == "Other [specify in comments]":
        return "other"
    else:
        return "missing"


def determine_social_scale(social_scales):
    unique_scales = set(social_scales)

    # Apply your logic
    if "large-scale" in unique_scales and "small-scale" in unique_scales:
        return "small-scale, large-scale"
    elif "large-scale" in unique_scales:
        return "large-scale"
    elif "small-scale" in unique_scales:
        return "small-scale"
    elif "other" in unique_scales:
        return "other"
    elif "missing" in unique_scales:
        return "missing"


def unique_social_scale(answers_social_scale: pd.DataFrame):
    answers_social_scale["social_scale"] = answers_social_scale["answer"].apply(
        get_social_scale
    )

    # check duplication
    answers_social_scale_grouped = (
        answers_social_scale.groupby(["entry_id", "social_scale"])
        .size()
        .reset_index(name="count")
    )

    answers_social_scale_unique = (
        answers_social_scale_grouped.groupby("entry_id")["social_scale"]
        .apply(determine_social_scale)
        .reset_index()
    )

    return answers_social_scale_unique
