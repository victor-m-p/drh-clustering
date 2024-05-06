"""
Temporary.
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

theta_large = pd.read_csv("../data/EM/shg_theta_all_large.csv")
theta_small = pd.read_csv("../data/EM/shg_theta_all.csv")

theta_large_dim = theta_large.drop(
    columns=["question_id", "question_short", "question_mean"]
)
theta_small_dim = theta_small.drop(
    columns=["question_id", "question_short", "question_mean"]
)

# Compute the cosine similarity matrix
similarity_matrix = cosine_similarity(theta_large_dim.T, theta_small_dim.T)

# Finding the most similar column in df_small for each column in df_large
most_similar_columns = pd.DataFrame(
    similarity_matrix, index=theta_large_dim.columns, columns=theta_small_dim.columns
)
most_similar_index = most_similar_columns.idxmax(axis=1)

most_similar_index = most_similar_index.reset_index(name="original_dimensions")
most_similar_index = most_similar_index.rename(columns={"index": "new_dimensions"})
most_similar_index = most_similar_index[["original_dimensions", "new_dimensions"]]
most_similar_index.sort_values("original_dimensions")
