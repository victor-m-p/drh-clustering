import pandas as pd

# Setup
superquestion = "shg"

# Load data
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_all.csv")
df_answers = pd.read_csv(f"../data/preprocessed/{superquestion}_expanded.csv")

# Get maximum dimension for each entry and maximum dimension value
dimension_names = [col for col in df_q.columns if col.startswith("dim")]
df_q["max_dim"] = df_q[dimension_names].idxmax(axis=1)
df_q["max_dim_value"] = df_q[dimension_names].max(axis=1)

# Extract the numerical part from max_dim and convert to integer
df_q["max_dim_num"] = df_q["max_dim"].str.extract(r"(\d+)").astype(int)

# Now select columns
df_q = df_q[["entry_id", "entry_name", "max_dim", "max_dim_value", "max_dim_num"]]
df_q["max_dim_value"] = df_q["max_dim_value"].round(2)

# Get how many questions answered
df_answers = df_answers.drop(columns=["entry_id", "weight"])
df_missing_answers = df_answers.isna().sum(axis=1).reset_index(name="num_not_answered")
df_missing_answers = df_missing_answers.drop(columns=["index"])

# Merge this in
df_q = pd.concat([df_q, df_missing_answers], axis=1)
df_q = df_q.sort_values(
    by=["max_dim_num", "max_dim_value", "num_not_answered"],
    ascending=[True, False, True],
)

# Drop the numerical column used for sorting
df_q = df_q.drop(columns=["max_dim_num"])

# Save 1 overview table
df_q.to_csv(f"../tables/{superquestion}_entries.csv", index=False)
