import numpy as np
import pandas as pd
from helper_functions import fit, custom_matmul

np.random.seed(1)

## setup ##
c_grid = [c + 1 for c in range(10)]  # ran with n=20
filename = "shg"  # shg
subset = "group"  # group

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

# require at least 50% coverage
n_columns = answers_complete.shape[1]
threshold = n_columns - int(np.round(36 * 0.5))
answers = answers_complete.dropna(thresh=threshold)

# (optionally) subset
if subset == "group":
    entry_metadata = entry_metadata[entry_metadata["poll_name"].str.contains("Group")]
    entry_id = entry_metadata["entry_id"].unique().tolist()
    answers = answers[answers["entry_id"].isin(entry_id)]

# preprocess data for EM
answers = answers.fillna(100)  # everything not 1/0 treated as nan
weight = answers["weight"].values
answer_values = answers.drop(columns=["entry_id", "weight"])
answer_values = answer_values.convert_dtypes()  # to integer
X = answer_values.to_numpy()
Y = np.where(X == 100, np.nan, X)

# find the right number of dimensions
logL_dict = {}
AIC_dict = {}
BIC_dict = {}
n = X.shape[0]  # Number of observations

for c in c_grid:  # For each number of clusters
    theta, q = fit(X, c, weights=weight, num_its=1000, eps=1e-10)

    # does this make sense
    # here we are calculateing log likelihood on theta
    logL = np.sum(
        q
        * (
            custom_matmul(Y, np.log(theta).T)
            + custom_matmul((1 - Y), np.log(1 - theta).T)
        )
    )
    k = c * X.shape[1] + (c - 1)  # Number of parameters
    AIC = (2 * k) - (2 * logL)
    BIC = (np.log(n) * k) - (2 * logL)

    print(f"Clusters: {c}, LogL: {logL}, AIC: {AIC}, BIC: {BIC}")
    logL_dict[c] = logL
    AIC_dict[c] = AIC
    BIC_dict[c] = BIC

# select the number C that minimized BIC.
c = min(BIC_dict, key=BIC_dict.get)
theta, q = fit(X, c)

# gather question dimensions (theta)
question_names = answer_values.columns.tolist()
question_names = [int(q[1:]) for q in question_names]
question_names = pd.DataFrame(question_names, columns=["question_id"])
question_selection = question_names.merge(questions, on="question_id", how="inner")

# gather question dimension (theta)
theta_df = pd.DataFrame(theta.T, columns=[f"dim{i}" for i in range(c)])
theta_df = pd.concat([question_selection, theta_df], axis=1)

# calculate log change and save theta
question_means = np.nanmean(Y, axis=0)
theta_df["question_mean"] = question_means
theta_df.to_csv(f"../data/EM/combined_theta_{subset}.csv", index=False)

# gather entry dimension (q)
entry_ids = answers[["entry_id"]]
df_entries = entry_ids.merge(entry_metadata, on="entry_id", how="inner")
q_df = pd.DataFrame(q, columns=[f"dim{i}" for i in range(c)])
df_entries = pd.concat([df_entries, q_df], axis=1)
df_entries = df_entries.sort_values("entry_id")

# save
df_entries.to_csv(f"../data/EM/combined_q_{subset}.csv", index=False)
