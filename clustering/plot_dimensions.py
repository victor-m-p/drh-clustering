import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#### setup ####
c = 8  # minimize BIC
superquestion = "shg"
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_{c}_all.csv")
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_{c}_all.csv")

# First plot data preparation
df_plot1 = df_theta.drop(columns=["related_question_id", "question_mean"])
df_plot1.set_index("question_short", inplace=True)

# Second plot data preparation
df_plot2 = df_theta.drop(columns=["related_question_id"])
df_plot2.set_index("question_short", inplace=True)
value_columns = df_plot2.columns.difference(["question_mean"])
df_plot_relative = df_plot2[value_columns].sub(df_plot2["question_mean"], axis=0)

## plot 1 -- only overall ##
fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=300)  # Adjust the figsize as needed
sns.heatmap(df_plot1, cmap="coolwarm", center=0, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
ax.set_xlabel("Dimension", size=14)
ax.set_ylabel("Question", size=14)
plt.xticks(size=12)
plt.yticks(size=12)
# plt.suptitle("Question Weights", size=15, y=1)
plt.tight_layout()
plt.savefig(f"fig/{superquestion}_{c}_weights.jpg")


## plot 2 -- side-by-side ##
fig, ax = plt.subplots(1, 2, figsize=(12, 6))  # Adjust the figsize as needed

# Plotting the first heatmap
sns.heatmap(df_plot1, cmap="coolwarm", center=0, ax=ax[0])
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha="right")
ax[0].set_xlabel("Dimension")
ax[0].set_ylabel("Question")
ax[0].set_title("Absolute Weighting")

# Plotting the second heatmap
sns.heatmap(df_plot_relative, cmap="coolwarm", center=0, ax=ax[1])
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha="right")
ax[1].set_xlabel("Dimension")
ax[1].set_ylabel("Question")
ax[1].set_title("Relative Weighting")
ax[1].set_yticklabels([])  # Remove the y-tick labels

plt.suptitle("Question Weightings", size=15, y=1.02)
plt.tight_layout()
plt.show()
