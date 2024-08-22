import pandas as pd

superquestion = "shg"  # "monitoring"
subquestion = "is unquestionably good"  # "conversion non-religionists"
question_label = "unquestionably"  # "conversion"

### data on tags and other entry level things ###
entry_tags = pd.read_csv("entry_tags.csv")
entry_tags["poll_group"] = entry_tags["poll_name"].str.contains("Group")
entry_tags = entry_tags[
    [
        "entry_id",
        "entry_name",
        "region_id",
        "year_from",
        "christian",
        "islamic",
        "chinese",
        "buddhist",
        "poll_group",
    ]
]

### include world regions ###
region_data = pd.read_csv("../data/raw/region_data.csv")
region_data = region_data[["region_id", "world_region"]].drop_duplicates()
entry_data = entry_tags.merge(region_data, on="region_id", how="inner")
entry_data = entry_data.drop(columns="region_id")  # not needed anymore

### include literacy ###
literacy = pd.read_csv("literacy.csv")
entry_data = entry_data.merge(literacy, on="entry_id", how="inner")

### cleanup ###
# make everything True/False 1/0 for now
entry_data["christian"] = entry_data["christian"].astype(int)
entry_data["islamic"] = entry_data["islamic"].astype(int)
entry_data["chinese"] = entry_data["chinese"].astype(int)
entry_data["buddhist"] = entry_data["buddhist"].astype(int)
entry_data["poll_group"] = entry_data["poll_group"].astype(int)

# only polls
entry_data = entry_data[entry_data["poll_group"] == 1]

### answers to superquestion ###
answers = pd.read_csv(f"../data/preprocessed/answers_subset_groups.csv")
answers = answers[answers["question_short"] == subquestion]

# only take answers with weight = 1 and non-NA
answers = answers[answers["weight"] == 1]
answers = answers.dropna()
answers["answer_value"] = answers["answer_value"].astype(int)

answers = answers[["entry_id", "question_short", "answer_value"]]
answers_mdl = answers.merge(entry_data, on="entry_id", how="inner")

# min-max normalization
answers_mdl["year_norm"] = (
    answers_mdl["year_from"] - answers_mdl["year_from"].min()
) / (answers_mdl["year_from"].max() - answers_mdl["year_from"].min())

answers_mdl.to_csv(f"{superquestion}_{question_label}.csv", index=False)
