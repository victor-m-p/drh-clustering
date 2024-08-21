"""
Different ways of calculating overall metrics. 
"""

import pandas as pd

# load metrics
df_metrics = pd.read_csv("data/conversion_node_metrics.csv")

# load entries for overview
df_entries = pd.read_csv("data/entry_data_subset.csv")
df_entries = df_entries[
    ["entry_id", "entry_name", "year_from", "world_region"]
].drop_duplicates()

# load GCC nodes
gcc_nodes = pd.read_csv("data/gcc_nodes_conversion.csv")

### overview of nodes not in GCC ###
### ahhh this is like half of the nodes .... ###
df_entries[~df_entries["entry_id"].isin(gcc_nodes["entry_id"])]

### direct parents and children ###
metrics_direct = df_metrics[
    [
        "entry_id",
        "yes_parents",
        "n_parents",
        "yes_children",
        "n_children",
        "answer_value",
        "christian_tradition",
    ]
]

# if no parents then by definition a "yes" is important so seems okay
metrics_direct["yes_parents"] = metrics_direct["yes_parents"].fillna(0)
metrics_direct["n_parents"] = metrics_direct["n_parents"].fillna(0)

# if no children then irrelevant
metrics_direct = metrics_direct.dropna()

# which ones stick out the most
# some of these are "No" answers, which is interesting.
metrics_direct["delta_yes"] = (
    metrics_direct["yes_children"] - metrics_direct["yes_parents"]
)

# merge with entry data and GCC
metrics_direct = metrics_direct.merge(df_entries, on="entry_id", how="inner")
metrics_direct = metrics_direct.merge(
    gcc_nodes, on="entry_id", how="left", indicator=True
)
metrics_direct = metrics_direct.rename(columns={"_merge": "in_gcc"})
metrics_direct["in_gcc"] = metrics_direct["in_gcc"].replace(
    {"both": True, "left_only": False}
)

metrics_direct.sort_values("delta_yes", ascending=False).head(10)

"""
This first approach captures a lot of things that are not christian
and not even answered with "yes". 

Additionally, some of the entries here are not in the GCC subgraph.
For instance, "Old Norse Fornsed". 

This suggests that what we have might be too broad to really capture
which religions "drive" the spread from religions that are spatio-temporally
co-located with the spread of Christianity. 

Of course, we can condition on "yes" answers here. 
"""

metrics_yes = metrics_direct[metrics_direct["answer_value"] == 1]
metrics_yes.sort_values("delta")

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
entry_data_subset = pd.read_csv("data/entry_data_subset.csv")
entry_data_subset = entry_data_subset[["christian_tradition", "entry_id"]]
entry_data_answers = entry_data_subset.merge(answers, on="entry_id", how="inner")
entry_data_answers[
    (entry_data_answers["christian_tradition"] == True)
    & (entry_data_answers["answer_value"] == 0)
].sort_values("entry_id")

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
