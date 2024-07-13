"""
VMP 2024-06-28
Control for writing. 
Consider moving to preprocessing if we keep this. 
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# setup
condition = False
superquestion = "monitoring"
x_min = -2000
bin_width = 500
step_size = 100

# find has writing
answerset = pd.read_csv("../data/raw/answerset.csv")

# take written language super-questions
written_language = answerset[
    (answerset["question_name"].str.contains("written language"))
    & (answerset["parent_question_id"].isna())
]

# n = 732 unique entries here.
# of course all of the text entries do have writing.
written_language["entry_id"].nunique()
written_language = written_language[
    ["entry_id", "question_name", "answer_value"]
].drop_duplicates()

# now use the literacy recoding table
literacy_recode = pd.read_csv("../data/raw/literacy_recode.csv")
literacy_recode = literacy_recode[["entry_id", "question_name", "answer_value"]]

# take answer from literacy recode where it exists
# Merge the two dataframes on 'entry_id' and 'question_name' using an outer join
df_merged = pd.merge(
    written_language,
    literacy_recode,
    on=["entry_id", "question_name"],
    how="outer",
    suffixes=("", "_small"),
)

# sanity check
assert len(literacy_recode) == len(df_merged[df_merged["answer_value_small"].notna()])

# Use the 'answer_value' from literacy recode where it exists
df_merged["answer_value"] = df_merged["answer_value_small"].combine_first(
    df_merged["answer_value"]
)

# Drop the auxiliary 'answer_value_small' column
df_result = df_merged.drop(columns=["answer_value_small"])

# Now we can compute whether each entry has a "YES" for at least one of the questions
written_language_yes = df_result[df_result["answer_value"] == 1]
written_language_entries = written_language_yes["entry_id"].unique().tolist()

# Also add all relevant Text entries to the list (they all have literacy)
religious_text = answerset[answerset["poll_name"] == "Religious Text (v1.0)"]
religious_text_entries = religious_text["entry_id"].unique().tolist()

# Combine the two lists (sets)
written_language_entries = list(set(written_language_entries + religious_text_entries))

### now we can do the rest of our analysis ###
### we should do this as a function and plot for both those that HAVE and DO NOT HAVE literacy ###

# load and merge
df = pd.read_csv(f"../data/preprocessed/{superquestion}_long.csv")
df = df[["entry_id", "question_short", "question_id", "answer_value", "weight"]]
entry_metadata = pd.read_csv(f"../data/raw/entry_data.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to"]]
df = df.merge(entry_metadata, on="entry_id", how="inner")
df["year_from"] = df["year_from"].astype(int)
df["year_to"] = df["year_to"].astype(int)
df = df.dropna()
df["answer_value"] = df["answer_value"].astype(int)

# now we assign literacy
df["literacy"] = df["entry_id"].apply(lambda x: x in written_language_entries)
df = df[df["literacy"] == condition]

# select questions to show (all is too chaotic)
if superquestion == "shg":
    question_subset = [
        2941,  # anthropomorphic
        2948,  # sky deity
        2984,  # unquestionably good
        3288,  # indirect causal
        3283,  # hunger
        3218,  # worship other
    ]
elif superquestion == "monitoring":
    question_subset = [
        2928,  # prosocial norms
        2970,  # taboos
        2972,  # murder other polities
        2978,  # sex
        2923,  # shirking risk
        2930,  # performance rituals
        2982,  # conversion
    ]
df[["question_id", "question_short"]].drop_duplicates()
df = df[df["question_id"].isin(question_subset)]

# time-slices
from helper_functions import smooth_time_end

df_time = smooth_time_end(df, bin_width, step_size)

# weighted average
df_agg = (
    df_time.groupby(["time_bin", "question_short"])
    .apply(lambda x: (x["answer_value"] * x["weight"]).sum() / x["weight"].sum())
    .reset_index(name="fraction_yes")
)

# Take only from the time range
df_agg_subset = df_agg[df_agg["time_bin"] >= x_min - step_size]
y_max = df_agg_subset["fraction_yes"].max()
y_max = y_max + 0.05

# Plot
plt.figure(figsize=(10, 4), dpi=300)
sns.lineplot(data=df_agg_subset, x="time_bin", y="fraction_yes", hue="question_short")
plt.xticks(rotation=45)
plt.yticks()
delta = int(np.round(bin_width / 2, 0))
plt.xlabel(f"Year", size=12)
plt.ylabel("Fraction yes", size=12)
# plt.xlim(x_min, x_max)
plt.ylim(0, y_max)

# Adjust y axis ticks
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.1))

# Specify the number of columns in the legend
ncol = 1

# Place the legend below the plot without a title and without a box
plt.legend(
    fontsize=12,
    loc="upper center",
    bbox_to_anchor=(1.5, 1.05),
    ncol=ncol,
    frameon=False,
)

plt.tight_layout()
plt.savefig(
    f"../figures/{superquestion}_question_time_literacy_{condition}.jpg",
    dpi=300,
    bbox_inches="tight",
)
