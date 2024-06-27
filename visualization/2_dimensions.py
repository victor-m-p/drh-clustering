import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, leaves_list
from constants import monitoring_question_order

# setup
superquestion = "shg"  # monitoring

# load data
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_all.csv")
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_all.csv")

# First plot data preparation
df_plot1 = df_theta.drop(columns=["question_id", "question_mean"])
df_plot1.set_index("question_short", inplace=True)

### re-order for clarity ###
# Compute the linkage matrix for rows
row_linkage_matrix = linkage(df_plot1, method="average", metric="euclidean")
# Get the order of the leaves (rows) after clustering
row_order = leaves_list(row_linkage_matrix)
# Reorder the rows of the DataFrame
df_plot1_reordered = df_plot1.iloc[row_order]

# plot
ndim = len(df_plot1_reordered.columns)
fig, ax = plt.subplots(
    1, 1, figsize=(ndim * 0.8, 8), dpi=300
)  # Adjust the figsize as needed
sns.heatmap(df_plot1_reordered, cmap="coolwarm", center=0, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
ax.set_xlabel("Dimension", size=14)
ax.set_ylabel("Question", size=14)
plt.xticks(size=12)
plt.yticks(size=12)
plt.tight_layout()
plt.savefig(f"../figures/{superquestion}_dimensions.jpg", dpi=300, bbox_inches="tight")
