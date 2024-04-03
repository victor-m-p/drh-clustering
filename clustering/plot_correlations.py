"""
Produce plots of weighted correlations for monitoring and shg. 

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# setup
superquestion = "monitoring"

# load data
df_matrix = pd.read_csv(f"../data/ML/{superquestion}.csv")
df_matrix = df_matrix.drop(columns=["entry_id"])

shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
shg_answers = shg_answers[
    ["entry_id", "related_question_id", "question_short", "answer_numeric"]
].drop_duplicates()

# remap columns to interpretable format
unique_questions = df_matrix.drop(columns="weight").columns.tolist()
unique_questions = [int(x[1:]) for x in unique_questions]

# 1. remap the columns to interpretable format:
unique_question_mapping = shg_answers[
    shg_answers["related_question_id"].isin(unique_questions)
]
unique_question_mapping = unique_question_mapping[
    ["related_question_id", "question_short"]
].drop_duplicates()
unique_question_mapping["related_question_id"] = "Q" + unique_question_mapping[
    "related_question_id"
].astype(str)
unique_question_mapping_dict = dict(
    zip(
        unique_question_mapping["related_question_id"],
        unique_question_mapping["question_short"],
    )
)

# 2. calculate the weighted correlations
from fun import weighted_corr

df_matrix = df_matrix.rename(columns=unique_question_mapping_dict)
features = df_matrix.columns[:-1]  # all columns except the last 'weight' column
correlations = weighted_corr(features, df_matrix)

# 3. clustering to highlight patterns
from scipy.spatial.distance import squareform
from scipy.cluster import hierarchy

distances = 1 - np.abs(correlations)
condensed_dist_matrix = squareform(distances, checks=False)
linkage = hierarchy.linkage(condensed_dist_matrix, method="weighted")
dendro = hierarchy.dendrogram(linkage, no_plot=True)
sorted_indexes = dendro["leaves"]
sorted_corr = correlations.iloc[sorted_indexes, sorted_indexes]

# 4. plot the heatmap
mask = np.triu(np.ones_like(sorted_corr, dtype=bool))

plt.figure(figsize=(9, 9), dpi=300)
sns.heatmap(
    sorted_corr,
    mask=mask,
    annot=True,
    vmax=1,
    center=0,
    vmin=-1,
    fmt=".1f",
    cmap="coolwarm",
    cbar_kws={"shrink": 0.5},
    square=True,
)
plt.title("Clustered Correlation Matrix Heatmap", size=18)
plt.xticks(size=12)
plt.yticks(size=12)
plt.tight_layout()
plt.savefig(f"fig/{superquestion}_correlation_heatmap.jpg")
