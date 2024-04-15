import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# setup
superquestion = "shg"
x_min = -2000
bin_width = 500
step_size = 100

# find christian entries
entry_tags = pd.read_csv("../data/raw/entry_tags.csv")

# find out what we match with "Christ":
entrytag_id = [
    18,  # Christian Traditions
    905,  # Abrahamic Traditions
    915,  # Evangelicalism
    971,  # Methodism
    1032,  # Protestantism
    996,  # Roman Catholic
    999,  # Catholic
    1031,  # Pentecostal
    1570,  # Christianity
]
entry_string_match = "Christian"

# find christian entries
christian_entries = (
    entry_tags[
        (entry_tags["entrytag_id"].isin(entrytag_id))
        | (entry_tags["parent_tag_id"].isin(entrytag_id))
        | (entry_tags["entry_tag"].str.contains(entry_string_match))
    ]["entry_id"]
    .unique()
    .tolist()
)

# find non-christian entries
non_christian_entries = (
    entry_tags[~entry_tags["entry_id"].isin(christian_entries)]["entry_id"]
    .unique()
    .tolist()
)

# load and merge
df = pd.read_csv(f"../data/preprocessed/{superquestion}_long.csv")
df = df[["entry_id", "question_short", "question_id", "answer_value", "weight"]]
entry_metadata = pd.read_csv(f"../data/preprocessed/entry_metadata.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to"]]
df = df.merge(entry_metadata, on="entry_id", how="inner")
df["year_from"] = df["year_from"].astype(int)
df["year_to"] = df["year_to"].astype(int)
df = df.dropna()
df["answer_value"] = df["answer_value"].astype(int)
df = df[df["entry_id"].isin(non_christian_entries)]

# select questions to show (all is too chaotic)
if superquestion == "shg":
    question_subset = [
        4829,  # anthropomorphic
        4830,  # sky deity
        4836,  # unquestionably good
        4852,  # indirect causal
        4855,  # hunger
        4856,  # worship other
    ]
elif superquestion == "monitoring":
    question_subset = [
        4955,  # prosocial norms
        4956,  # taboos
        4963,  # murder other polities
        4964,  # sex
        4973,  # shirking risk
        4978,  # performance rituals
        4979,  # conversion
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
    f"../figures/{superquestion}_question_time_filter_christian.jpg",
    dpi=300,
    bbox_inches="tight",
)

# sanity check #
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
entry_metadata = entry_metadata[["entry_id", "entry_name"]].drop_duplicates()
df_entries = df[["entry_id"]].drop_duplicates()
df_entries = df_entries.merge(entry_metadata, on="entry_id", how="inner")