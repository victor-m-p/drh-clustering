import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# setup
superquestion = "shg"  # monitoring

# load data
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_all.csv")
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_all.csv")

# First plot data preparation
df_plot1 = df_theta.drop(columns=["question_id", "question_mean"])
df_plot1.set_index("question_short", inplace=True)

# plot
ndim = len(df_plot1.columns)
fig, ax = plt.subplots(1, 1, figsize=(ndim, 8), dpi=300)  # Adjust the figsize as needed
sns.heatmap(df_plot1, cmap="coolwarm", center=0, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
ax.set_xlabel("Dimension", size=14)
ax.set_ylabel("Question", size=14)
plt.xticks(size=12)
plt.yticks(size=12)
plt.tight_layout()
plt.savefig(f"../figures/{superquestion}_dimensions.jpg", dpi=300, bbox_inches="tight")
