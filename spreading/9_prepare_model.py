import numpy as np
import pandas as pd
import pymc as pm
import arviz as az

# load data
spatiotemporal_data = pd.read_csv("data/overlap_christianity.csv")

### select a feature to investigate ###
question_name = "is unquestionably good"
question_group = "shg"
question_short = "unquestionably"
answers = pd.read_csv(f"../data/preprocessed/{question_group}_long.csv")
answers = answers[answers["question_short"] == question_name]
# answers = answers[answers["poll_name"].str.contains("Group")]
### select only answers with weight 1 and an answer ###
answers = answers[answers["weight"] == 1]
answers = answers.dropna(subset=["answer_value"])
answers = answers[["entry_id", "answer_value"]]

### now we can merge on both
answers = answers.rename(
    columns={"entry_id": "entry_id_from", "answer_value": "answer_value_from"}
)
spatiotemporal_answers = spatiotemporal_data.merge(
    answers, on="entry_id_from", how="inner"
)

answers = answers.rename(
    columns={"entry_id_from": "entry_id_to", "answer_value_from": "answer_value_to"}
)
spatiotemporal_answers = spatiotemporal_answers.merge(
    answers, on="entry_id_to", how="inner"
)

# okay for each entry_to we aggregate
avg_yes = (
    spatiotemporal_answers.groupby("entry_id_to")["answer_value_from"]
    .mean()
    .reset_index(name="avg_yes")
)
avg_christian = (
    spatiotemporal_answers.groupby("entry_id_to")["christian_tradition_from"]
    .mean()
    .reset_index(name="avg_christian")
)
predictors = avg_yes.merge(avg_christian, on="entry_id_to")
answers = spatiotemporal_answers[["entry_id_to", "answer_value_to"]].drop_duplicates()
data = answers.merge(predictors, on="entry_id_to")
data.to_csv(f"data/{question_short}_model.csv", index=False)
