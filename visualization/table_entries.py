import pandas as pd

# setup
superquestion = "shg"

# load data
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_all.csv")
df_answers = pd.read_csv(f"../data/preprocessed/{superquestion}_expanded.csv")

# get maximum dimension for each entry and maximum dimension value
dimension_names = [col for col in df_q.columns if col.startswith("dim")]
df_q["max_dim"] = df_q[dimension_names].idxmax(axis=1)
df_q["max_dim_value"] = df_q[dimension_names].max(axis=1)

# now select columns
df_q = df_q[["entry_id", "entry_name", "max_dim", "max_dim_value"]]
df_q["max_dim_value"] = df_q["max_dim_value"].round(2)

# get how many questions answered
df_answers = df_answers.drop(columns=["entry_id", "weight"])
df_missing_answers = df_answers.isna().sum(axis=1).reset_index(name="num_not_answered")
df_missing_answers = df_missing_answers.drop(columns=["index"])

# merge this in
df_q = pd.concat([df_q, df_missing_answers], axis=1)
df_q = df_q.sort_values(
    by=["max_dim", "max_dim_value", "num_not_answered"], ascending=[True, False, True]
)

# save 1 overview table
df_q.to_csv(f"../tables/{superquestion}_entries.csv", index=False)
