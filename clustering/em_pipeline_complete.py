"""
vmp 5-8-23;
still needs a couple of things to be fully automated
* number of dimensions (AIC/BIC)
* number of clusters

NB: I cannot guarantee that the weighting works but
I have checked that for all weights = 1 it gives
the same result as the unweighted version. 
"""

import numpy as np
import pandas as pd
from fun import fit, custom_matmul

np.random.seed(0)

## setup ##
c_grid = [c + 1 for c in range(3)]
filename = "monitoring"
subset = "all"  # will give only religious groups

# load data
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
answers = answers[["question_short", "related_question_id"]].drop_duplicates()
df = pd.read_csv(f"../data/ML/{filename}.csv")

# (optionally) subset
if subset == "group":
    entry_metadata = entry_metadata[entry_metadata["poll"].str.contains("Group")]
    entry_id = entry_metadata["entry_id"].unique().tolist()
    df = df[df["entry_id"].isin(entry_id)]

# preprocess data for EM
df = df.fillna(100)  # everything not 1/0 treated as nan
weight = df["weight"].values
df_matrix = df.drop(columns=["entry_id", "weight"])
df_matrix = df_matrix.convert_dtypes()  # to integer
X = df_matrix.to_numpy()
Y = np.where(X == 100, np.nan, X)

# find the right number of dimensions
logL_dict = {}  # Assuming you have this dictionary to store log-likelihood values
AIC_dict = {}
BIC_dict = {}
n = X.shape[0]  # Number of observations

for c in c_grid:  # For each number of clusters
    theta, q = fit(X, c)
    logL = np.sum(
        q
        * (
            custom_matmul(Y, np.log(theta).T)
            + custom_matmul((1 - Y), np.log(1 - theta).T)
        )
    )
    k = c * X.shape[1] + c - 1  # Number of parameters
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
questions = df_matrix.columns.tolist()
questions = [int(q[1:]) for q in questions]
questions = pd.DataFrame(questions, columns=["related_question_id"])
questions = questions.merge(answers, on="related_question_id", how="inner")

# gather question dimension (theta)
theta_df = pd.DataFrame(theta.T, columns=[f"dim{i}" for i in range(c)])
theta_df = pd.concat([questions, theta_df], axis=1)

# calculate log change and save theta
question_means = np.nanmean(Y, axis=0)
theta_df["question_mean"] = question_means
# for i in range(3):
#    theta_df[f"dim{i}_log_change"] = theta_df[f"dim{i}"] / theta_df["question_mean"]
#    theta_df[f"dim{i}_log_change"] = [np.log(x) for x in theta_df[f"dim{i}_log_change"]]
# theta_df = theta_df.sort_values("dim0_log_change")
theta_df.to_csv(f"../data/EM/{filename}_theta_{c}_{subset}.csv", index=False)

# gather entry dimension (q)
entry_ids = df[["entry_id"]]
df_entries = entry_ids.merge(entry_metadata, on="entry_id", how="inner")
q_df = pd.DataFrame(q, columns=[f"dim{i}" for i in range(c)])
df_entries = pd.concat([df_entries, q_df], axis=1)

# save
df_entries.to_csv(f"../data/EM/{filename}_q_{c}_{subset}.csv", index=False)
