import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# setup
# superquestion = "A supreme high god is present:"
superquestion = "Is supernatural monitoring present:"
outname = "shg"

# basic imports
shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")

# get the relevant subset
subset_answers = shg_answers[shg_answers["parent_question"] == superquestion]
subset_answers = subset_answers[subset_answers["answer_code"].isin(["Yes", "No"])]
subset_answers = subset_answers[["entry_id", "question_short", "answer_numeric"]]

# merge year
year_from = entry_metadata[["entry_id", "year_from"]]
subset_answers = subset_answers.merge(year_from, on="entry_id", how="inner")

# now we bin year
bin_width = 500
step_size = 100
max_year = subset_answers["year_from"].max()
x_max = max_year - (bin_width / 2)

from fun import smooth_time

df_smoothed = smooth_time(subset_answers, bin_width, step_size)

# Aggregate the data within each bin for each dimension
df_smoothed_agg = (
    df_smoothed.groupby(["time_bin", "question_short"])["answer_numeric"]
    .mean()
    .reset_index()
)

# Plot
fig, ax = plt.subplots(figsize=(7, 3), dpi=300)
fig.patch.set_facecolor("white")
sns.lineplot(
    data=df_smoothed_agg, x="time_bin", y="answer_numeric", hue="question_short"
)
plt.xticks(rotation=45)
delta = int(np.round(bin_width / 2, 0))
plt.xlabel(f"Year (smoothed over {bin_width} years)", size=12)
plt.ylabel("Mean Dimension Value", size=12)
plt.xlim(-2000, x_max)
plt.ylim(0, 1)
ax.legend().remove()
plt.tight_layout()
handles, labels = ax.get_legend_handles_labels()
ncol = 2
nrow = 10
y_align_legend = -0.08 * nrow
fig.legend(
    handles,
    labels,
    loc="lower center",
    bbox_to_anchor=(0.5, y_align_legend),
    ncol=ncol,
    frameon=False,
    fontsize=12,
)
plt.subplots_adjust(left=0.15, bottom=0.35)
# plt.savefig(f"fig/{outname}_time_questions.jpg")
