import pandas as pd
import numpy as np


# convenience functions
def clean_answers(answers, question_name):
    # take out relevant question
    answers = answers[answers["question_short"] == question_name]

    # only consistent and binary answers
    answers = answers[answers["weight"] == 1]
    answers = answers.dropna(subset=["answer_value"])
    answers = answers[["entry_id", "answer_value"]]
    return answers


def merge_data(answers, spatiotemporal_data):

    # merge both ways
    answers_from = answers.rename(
        columns={"entry_id": "entry_id_from", "answer_value": "answer_value_from"}
    )
    spatiotemporal_from = spatiotemporal_data.merge(
        answers_from, on="entry_id_from", how="inner"
    )

    answers_to = answers.rename(
        columns={"entry_id": "entry_id_to", "answer_value": "answer_value_to"}
    )
    spatiotemporal_both = spatiotemporal_from.merge(
        answers_to, on="entry_id_to", how="inner"
    )

    return spatiotemporal_both


def calculate_metrics(spatiotemporal_answers):
    # aggregate "yes" and "christian" parents and children
    yes_parents = (
        spatiotemporal_answers.groupby("entry_id_to")["answer_value_from"]
        .mean()
        .reset_index(name="yes_parents")
    )
    yes_children = (
        spatiotemporal_answers.groupby("entry_id_from")["answer_value_to"]
        .mean()
        .reset_index(name="yes_children")
    )
    christian_parents = (
        spatiotemporal_answers.groupby("entry_id_to")["christian_tradition_from"]
        .mean()
        .reset_index(name="christian_parents")
    )
    christian_children = (
        spatiotemporal_answers.groupby("entry_id_from")["christian_tradition_to"]
        .mean()
        .reset_index(name="christian_children")
    )
    n_children = (
        spatiotemporal_answers.groupby("entry_id_from")
        .size()
        .reset_index(name="n_children")
    )
    n_parents = (
        spatiotemporal_answers.groupby("entry_id_to")
        .size()
        .reset_index(name="n_parents")
    )
    # gather data
    n_children = n_children.rename(columns={"entry_id_from": "entry_id"})
    n_parents = n_parents.rename(columns={"entry_id_to": "entry_id"})
    yes_parents = yes_parents.rename(columns={"entry_id_to": "entry_id"})
    yes_children = yes_children.rename(columns={"entry_id_from": "entry_id"})
    christian_parents = christian_parents.rename(columns={"entry_id_to": "entry_id"})
    christian_children = christian_children.rename(
        columns={"entry_id_from": "entry_id"}
    )
    df_metrics = yes_parents.merge(yes_children, on="entry_id", how="outer")
    df_metrics = df_metrics.merge(christian_parents, on="entry_id", how="outer")
    df_metrics = df_metrics.merge(christian_children, on="entry_id", how="outer")
    df_metrics = df_metrics.merge(n_children, on="entry_id", how="outer")
    df_metrics = df_metrics.merge(n_parents, on="entry_id", how="outer")
    df_metrics = np.round(df_metrics, 2)  # round all floats
    return df_metrics


# load data
spatiotemporal_data = pd.read_csv("data/spatiotemporal_overlap.csv")
entry_data = pd.read_csv("data/entry_data_subset.csv")

# run this for both features
question_names = ["conversion non-religionists", "is unquestionably good"]
question_groups = ["monitoring", "shg"]
question_shorts = ["conversion", "unquestionably"]

for question_name, question_group, question_short in zip(
    question_names, question_groups, question_shorts
):
    # load
    answers = pd.read_csv(f"../data/preprocessed/{question_group}_long.csv")

    # clean answers
    answers = clean_answers(answers, question_name)

    # merge with spatiotemporal data
    spatiotemporal_answers = merge_data(answers, spatiotemporal_data)

    # calculate metrics
    df_metrics = calculate_metrics(spatiotemporal_answers)

    # add answers back
    df_metrics = df_metrics.merge(answers, on="entry_id", how="inner")
    df_metrics.to_csv(f"data/{question_short}_metrics.csv", index=False)
