import numpy as np
import pandas as pd

# let us flag which entries have been in contact (direct, indirect)
# with christianity
spatiotemporal_data = pd.read_csv("data/spatiotemporal_overlap.csv")

# add christianity
entry_data_subset = pd.read_csv("data/entry_data_subset.csv")
entry_data_subset = entry_data_subset[["entry_id", "christian_tradition"]]

entry_data_subset = entry_data_subset.rename(
    columns={
        "entry_id": "entry_id_from",
        "christian_tradition": "christian_tradition_from",
    }
)
spatiotemporal_data = spatiotemporal_data.merge(
    entry_data_subset, on="entry_id_from", how="inner"
)

entry_data_subset = entry_data_subset.rename(
    columns={
        "entry_id_from": "entry_id_to",
        "christian_tradition_from": "christian_tradition_to",
    }
)
spatiotemporal_data = spatiotemporal_data.merge(
    entry_data_subset, on="entry_id_to", how="inner"
)
spatiotemporal_data.to_csv("data/overlap_christianity.csv", index=False)

# this already gives us direct contact (christian_tradition_from)

### select a feature to investigate ###
question_name = "conversion non-religionists"
question_group = "monitoring"
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
spatiotemporal_answers.to_csv("data/overlap_christianity.csv", index=False)

# now we can get probabilities #
# p(yes | yes)
# p(yes | no)
# p(no | yes)
# p(no | no)
# p(yes)
# p(no)

# p(yes | christian tradition from)
# p(yes | no christian tradition from)
# p(no | christian tradition from)
# p(no | no christian tradition from)

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
p(Yes) = .52
p(Yes | Yes) = .69
p(Yes | Christian contact) = .74
p(Yes | Yes & Christian contact) = .8
"""

""" for groups only 
p(Yes) = .62
p(Yes | Yes) = .72
p(Yes | Christian contact) = 0.83
p(Yes | Yes & Christian contact) = 0.83
"""

# what are the Christian traditions that do not monitor conversion?
answers = answers.rename(
    columns={"entry_id_to": "entry_id", "answer_value_to": "answer_value"}
)
entry_data_subset = entry_data_subset.rename(
    columns={"entry_id_to": "entry_id", "christian_tradition_to": "christian_tradition"}
)

entry_data_answers = entry_data_subset.merge(answers, on="entry_id", how="inner")
entry_data_answers[
    (entry_data_answers["christian_tradition"] == True)
    & (entry_data_answers["answer_value"] == 0)
]

""" Many of the Christian entries that do not monitor conversion (non-religionists) are Texts
859: Valentinians (group)
933: Marcionites (group)
1401: The "On the Divine Names" of Pseudo Denys the Areopagiate (text)
1589: Peshitta (text)
1657: The Institutes of John Cassian (text)
1659: The Conferences of John Cassian (text)
1664: The Didache (text)
1735: Qur'an (somehow Christian, text)
1778: Le Conflit d'Adam et Eve contre Satan ... (text)
2001: The Book of Deuteronomy (text)
2039: Psalm 109 (text)
2140: St. John Chrysostom, Homilies On the Incomprehensible Nature of God (text)
"""
