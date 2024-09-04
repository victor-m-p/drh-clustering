# probably delete this actually
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# setup
social_complexity = pd.read_csv("../modeling/social_complexity.csv")
x_min = -2000
bin_width = 500
step_size = 50

# load and merge
social_complexity
entry_metadata = pd.read_csv(f"../data/raw/entry_data.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to"]].drop_duplicates()
social_complexity = social_complexity.merge(entry_metadata, on="entry_id", how="inner")
social_complexity["year_from"] = social_complexity["year_from"].astype(int)
social_complexity["year_to"] = social_complexity["year_to"].astype(int)
social_complexity = social_complexity.dropna()

# create new variables
social_complexity["question_short"] = "Social Complexity"

# time-slices
from helper_functions import smooth_time_end

df_time = smooth_time_end(social_complexity, bin_width, step_size)
df_agg = (
    df_time.groupby("time_bin")["social_complexity_large"]
    .mean()
    .reset_index(name="fraction_yes")
)

# Take only from the time range
df_agg_subset = df_agg[df_agg["time_bin"] >= x_min - step_size]
y_max = df_agg_subset["fraction_yes"].max()
y_max = y_max + 0.05

# Plot
plt.figure(figsize=(10, 5), dpi=300)
sns.lineplot(data=df_agg_subset, x="time_bin", y="fraction_yes")
plt.xticks(rotation=45)
plt.yticks()
delta = int(np.round(bin_width / 2, 0))
plt.xlabel(f"Year", size=12)
plt.ylabel("Fraction yes", size=12)
plt.ylim(0, y_max)

# Adjust y axis ticks
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.1))

# Specify the number of columns in the legend
ncol = 1

# Place the legend below the plot without a title and without a box
plt.legend(
    fontsize=14,
    loc="upper center",
    bbox_to_anchor=(1.3, 1.05),
    ncol=ncol,
    frameon=False,
)

plt.tight_layout()
plt.savefig(
    f"../figures/questions_temporal_{superquestion}_{subset}.jpg",
    dpi=300,
    bbox_inches="tight",
)
