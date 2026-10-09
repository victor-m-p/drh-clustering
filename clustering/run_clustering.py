"""
Latent class (EM) clustering of group entries, with multiple random starts per c.
For each c we run n_starts fits (seed = c * 1000 + start) and keep the best by logL.

Writes to ../data/EM/:
- EM_starts_{subset}.csv: logL for every start (diagnostics).
- EM_model_selection_{subset}.csv: best logL, AIC, BIC per c, and how many starts reached the best.
- EM_theta_{subset}_c{c}.csv, EM_q_{subset}_c{c}.csv: best solution for each candidate c.
  First row of the theta file holds pi (cluster shares).
"""

import numpy as np
import pandas as pd
from helper_functions import fit

## setup ##
c_grid = [c + 1 for c in range(10)]  # tried up to 20
n_starts = 100  # random starts per c
candidates = [2, 3, 4, 5, 6, 7]  # save full solutions for these
logL_tol = 0.01  # a start "reached the best" if within this of the best logL
subset = "group" # only set up for groups

# load data
entry_metadata = pd.read_csv("../data/raw/entry_data.csv")
questions = pd.read_csv("../data/preprocessed/answers_subset_groups.csv")
questions = questions[["question_id", "question_short"]].drop_duplicates()
answers = pd.read_csv(f"../data/preprocessed/groups_expanded.csv")

# preprocess data for EM
answers = answers.fillna(100)  # everything not 1/0 treated as nan
weight = answers["weight"].values
answer_values = answers.drop(columns=["entry_id", "weight"])
X = answer_values.to_numpy(dtype=float) # float arr; missing coded as 100 (ignored by fit because not 0/1)
n = weight.sum() # number of entries (effective sample size)

# fit all starts and keep the best per c
starts = []
best = {}
for c in c_grid:  # For each number of clusters
    for s in range(n_starts):
        seed = c * 1000 + s  # one seed per start, so any start can be rerun
        theta, q, pi, logL, n_its = fit(X, c, weights=weight, seed=seed)
        starts.append({"c": c, "seed": seed, "logL": logL, "n_its": n_its})
        if c not in best or logL > best[c]["logL"]:
            best[c] = {"theta": theta, "q": q, "pi": pi, "logL": logL, "seed": seed}

starts = pd.DataFrame(starts)
starts.to_csv(f"../data/EM/EM_starts_{subset}.csv", index=False)

# log likelihood and information criteria (for the best start per c)
selection = []
for c in c_grid:
    starts_c = starts[starts["c"] == c]
    logL = best[c]["logL"]
    k = c * X.shape[1] + (c - 1)  # c x 36 thetas + (c - 1) mixing proportions
    AIC = (2 * k) - (2 * logL)
    BIC = (np.log(n) * k) - (2 * logL)
    n_reached_best = int((starts_c["logL"] > logL - logL_tol).sum())

    print(f"Clusters: {c}, LogL: {logL}, AIC: {AIC}, BIC: {BIC}, reached best: {n_reached_best}/{n_starts}")
    selection.append(
        {
            "c": c,
            "k": k,
            "logL": logL,
            "AIC": AIC,
            "BIC": BIC,
            "n_reached_best": n_reached_best,
            "median_logL": starts_c["logL"].median(),
            "best_seed": best[c]["seed"],
            "max_its": starts_c["n_its"].max(),
        }
    )

selection = pd.DataFrame(selection)
selection.to_csv(f"../data/EM/EM_model_selection_{subset}.csv", index=False)
print(f"c minimizing BIC: {selection.loc[selection['BIC'].idxmin(), 'c']}")

# gather question dimensions (theta)
question_names = answer_values.columns.tolist()
question_names = [int(col[1:]) for col in question_names]
question_names = pd.DataFrame(question_names, columns=["question_id"])
question_selection = question_names.merge(questions, on="question_id", how="inner")

# overall share of Yes per question, for comparison
Y = np.where(X == 100, np.nan, X)
question_means = np.nanmean(Y, axis=0)

# save the best solution for each candidate c
for c in candidates:
    theta, q, pi = best[c]["theta"], best[c]["q"], best[c]["pi"]
    dims = [f"dim{i}" for i in range(c)]

    # theta (with pi as the first row)
    theta_df = pd.DataFrame(theta.T, columns=dims)
    theta_df = pd.concat([question_selection, theta_df], axis=1)
    theta_df["question_mean"] = question_means
    pi_row = pd.DataFrame([[-1, "pi (cluster share)", *pi]], columns=["question_id", "question_short", *dims])
    theta_df = pd.concat([pi_row, theta_df], ignore_index=True)
    theta_df.to_csv(f"../data/EM/EM_theta_{subset}_c{c}.csv", index=False)

    # gather entry dimension (q); one row per expanded row, with its weight
    entry_ids = answers[["entry_id", "weight"]]
    df_entries = entry_ids.merge(entry_metadata, on="entry_id", how="inner")
    q_df = pd.DataFrame(q, columns=dims)
    df_entries = pd.concat([df_entries, q_df], axis=1)
    df_entries = df_entries.sort_values("entry_id", kind="stable")

    # save
    df_entries.to_csv(f"../data/EM/EM_q_{subset}_c{c}.csv", index=False)
