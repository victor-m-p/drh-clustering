import pandas as pd
import numpy as np

# Load data
df_q = pd.read_csv(f"../data/EM/combined_q_group.csv")

# Get maximum dimension for each entry and maximum dimension value
dimension_names = [col for col in df_q.columns if col.startswith("dim")]
df_q["max_dim"] = df_q[dimension_names].idxmax(axis=1)
df_q["max_dim_value"] = df_q[dimension_names].max(axis=1)

# Extract the numerical part from max_dim and convert to integer
df_q["max_dim_num"] = df_q["max_dim"].str.extract(r"(\d+)").astype(int)

# Now select columns
df_q = df_q[["entry_id", "entry_name", "max_dim", "max_dim_value", "max_dim_num"]]
df_q["max_dim_value"] = df_q["max_dim_value"].round(2)

# Drop the numerical column used for sorting
df_q = df_q.drop(columns=["max_dim_num"])

### get the answers ###
# load data
entry_metadata = pd.read_csv("../data/raw/entry_data.csv")
questions = pd.read_csv("../data/preprocessed/answers_subset.csv")
questions = questions[["question_id", "question_short"]].drop_duplicates()
answers_shg = pd.read_csv(f"../data/preprocessed/shg_expanded.csv")
answers_monitoring = pd.read_csv(f"../data/preprocessed/monitoring_expanded.csv")

# bind them together and then only take okay coverage
answers_shg = answers_shg.rename(columns={"weight": "weight_shg"})
answers_monitoring = answers_monitoring.rename(columns={"weight": "weight_monitoring"})
answers_complete = answers_shg.merge(answers_monitoring, on="entry_id", how="inner")
answers_complete["weight"] = (
    answers_complete["weight_shg"] * answers_complete["weight_monitoring"]
)
answers_complete = answers_complete.drop(columns=["weight_shg", "weight_monitoring"])
answers_complete["missing_answers"] = answers_complete.isnull().sum(axis=1)

# require at least 50% coverage
n_columns = answers_complete.shape[1]
threshold = n_columns - int(np.round(36 * 0.5))
answers = answers_complete.dropna(thresh=threshold)

# (optionally) subset
entry_metadata = entry_metadata[entry_metadata["poll_name"].str.contains("Group")]
entry_id = entry_metadata["entry_id"].unique().tolist()
answers = answers[answers["entry_id"].isin(entry_id)]

# get some counts here for reporting
answers = answers[["entry_id", "missing_answers"]].drop_duplicates()
df_q = df_q.merge(answers, on="entry_id", how="inner")

# sort the data and save
df_sorted = df_q.sort_values(
    ["max_dim", "max_dim_value", "missing_answers"], ascending=[True, False, True]
)
df_sorted.to_csv("../tables/cluster_entries.csv", index=False)
df_sorted.to_latex("../tables/cluster_entries.tex", index=False, float_format="%.2f")

# Just for writing about it #
dim0 = df_q[df_q["max_dim"] == "dim0"]
dim0.sort_values(["max_dim_value", "number_nan"], ascending=[False, True])
