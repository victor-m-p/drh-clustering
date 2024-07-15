import pandas as pd
import numpy as np

spatiotemporal_data = pd.read_csv("data/overlap_christianity.csv")

### select a feature to investigate ###
question_name = "is unquestionably good"
question_group = "shg"
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

### get probabilities out ###
p_yes = spatiotemporal_answers["answer_value_to"].mean()
p_no = 1 - p_yes

p_yes_given_yes = spatiotemporal_answers[
    spatiotemporal_answers["answer_value_from"] == 1
]["answer_value_to"].mean()
p_no_given_yes = 1 - p_yes_given_yes

p_yes_given_no = spatiotemporal_answers[
    spatiotemporal_answers["answer_value_from"] == 0
]["answer_value_to"].mean()
p_no_given_no = 1 - p_yes_given_no

p_yes_given_christian = spatiotemporal_answers[
    spatiotemporal_answers["christian_tradition_from"]
]["answer_value_to"].mean()
p_no_given_christian = 1 - p_yes_given_christian

p_yes_given_no_christian = spatiotemporal_answers[
    ~spatiotemporal_answers["christian_tradition_from"]
]["answer_value_to"].mean()
p_no_given_no_christian = 1 - p_yes_given_no_christian

p_yes_given_yes_and_christian = spatiotemporal_answers[
    (spatiotemporal_answers["answer_value_from"] == 1)
    & (spatiotemporal_answers["christian_tradition_from"] == True)
]["answer_value_to"].mean()

"""
p(Yes) = .85
p(Yes | Yes) = .89
p(Yes | Christian contact) = .93
p(Yes | Yes & Christian contact) = .94
"""

""" for groups only 
p(Yes) = .89
p(Yes | Yes) = .91
p(Yes | Christian contact) = 0.94
p(Yes | Yes & Christian contact) = 0.94
"""

# what are the Christian traditions that are not unquestionably good #
answers = answers.rename(
    columns={"entry_id_to": "entry_id", "answer_value_to": "answer_value"}
)
entry_data_subset = pd.read_csv("data/entry_data_subset.csv")
entry_data_subset = entry_data_subset[["christian_tradition", "entry_id"]]
entry_data_answers = entry_data_subset.merge(answers, on="entry_id", how="inner")
entry_data_answers[
    (entry_data_answers["christian_tradition"] == True)
    & (entry_data_answers["answer_value"] == 0)
].sort_values("entry_id")

""" Many of the Christian entries that do not monitor conversion (non-religionists) are Texts
893: Sethian Gnostic
1700: The Book of Hosea (text)
"""

# how many transitions do we have? #

spatiotemporal_answers[spatiotemporal_answers["christian_tradition_from"] == True]

""" 
total n = 2962
total yes = 2510
total christian (from) = 671
"""

# are there some entries that are much more well represented than others? #
spatiotemporal_answers.groupby("entry_id_to").size().reset_index(
    name="count"
).sort_values("count", ascending=False)

""" (entry id to)
1322 (n=36): Pagans under emperor Julian
972 (n=36): Nestorian Christianity
1688 (n=32): Arianism
...
"""

spatiotemporal_answers.groupby("entry_id_from").size().reset_index(
    name="count"
).sort_values("count", ascending=False)

""" (entry id from)
492 (n=80): Roman Divination
1534 (n=71): Shorter Sukhavativyuha Sutra
972 (n=68): Nestorian Christianity
...
"""

"""
So some entries will have a lot of weight in this analysis.
Not the case to the same degree for the modeling effort. 
"""

### find cases that are not connected in our data ###
entry_id_to = spatiotemporal_answers["entry_id_to"].unique()
entry_id_from = spatiotemporal_answers["entry_id_from"].unique()
entry_id_matched = np.unique(np.concatenate([entry_id_to, entry_id_from]))

# get entry names
entry_data_subset = pd.read_csv("data/entry_data_subset.csv")
entry_data_subset = entry_data_subset[["entry_id", "entry_name"]]
answers = answers.merge(entry_data_subset, on="entry_id", how="inner")
entry_id_total = answers["entry_id"].unique()

# find missing entries
missing_entries = list(set(entry_id_total) - set(entry_id_matched))
answers[answers["entry_id"].isin(missing_entries)]  # less than 10 entries
