import pandas as pd
import numpy as np

# Load data
df_q = pd.read_csv(f"../data/EM/EM_q_group.csv")

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

# Get the number of answers missing
answers = pd.read_csv(f"../data/preprocessed/groups_expanded.csv")
answers["missing_answers"] = answers.isnull().sum(axis=1)
answers = answers[["entry_id", "missing_answers"]].drop_duplicates()
df_q = df_q.merge(answers, on="entry_id", how="inner")

# sort the data and save
df_sorted = df_q.sort_values(
    ["max_dim", "max_dim_value", "missing_answers"], ascending=[True, False, True]
)
df_sorted.to_csv("../tables/cluster_entries.csv", index=False)
df_sorted.to_latex("../tables/cluster_entries.tex", index=False, float_format="%.2f")
