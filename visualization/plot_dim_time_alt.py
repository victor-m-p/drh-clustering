""" 
Also considers end time. 
"""

# consider automatic selection of y axis
# consider automatic handling of filese and c value
# handle legend in a better way

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

pd.options.mode.chained_assignment = None

# setup
c = 7
x_min = -1000
superquestion = "monitoring"

df_q = pd.read_csv(f"../data/EM/{superquestion}_q_{c}_all.csv")
dimension_columns = [f"dim{x}" for x in range(c)]
temporal_columns = [
    "entry_id",
    "entry_name",
    "year_from",
    "year_to",
] + dimension_columns
df_temporal = df_q[temporal_columns]
df_temporal["year_from"] = df_temporal["year_from"].astype(int)
df_temporal["year_to"] = df_temporal["year_to"].astype(int)

# do it based on start year #
min_year = df_temporal["year_from"].min()
max_year = df_temporal["year_to"].max()
bins = [(-3300, -1000), (-1000, 0), (0, 1000), (1000, 1700), (1700, 2025)]

from helper_functions import smooth_time_bins

df_smoothed = smooth_time_bins(df_temporal, bins)
print(df_smoothed.groupby("bin_n").size())

# Aggregate the data within each bin for each dimension
df_smoothed_agg = df_smoothed.groupby("bin_n")[dimension_columns].mean().reset_index()

# Melt the aggregated DataFrame for plotting
df_smoothed_long = df_smoothed_agg.melt(
    id_vars=["bin_n"],
    value_vars=dimension_columns,
    var_name="dimension",
    value_name="value",
)

# Add x axis labels
bin_values_to_labels = df_smoothed[["bin_n", "time_range"]].drop_duplicates()
bin_values_to_labels = bin_values_to_labels.set_index("bin_n")["time_range"].to_dict()

# Take only from the time range
# df_smoothed_long = df_smoothed_long[df_smoothed_long["time_bin"] >= x_min - step_size]
y_max = df_smoothed_long["value"].max()
y_max = y_max + 0.05

# Plot
plt.figure(figsize=(8, 4), dpi=300)
sns.lineplot(data=df_smoothed_long, x="bin_n", y="value", hue="dimension")
plt.xticks(
    list(bin_values_to_labels.keys()), list(bin_values_to_labels.values()), rotation=45
)
plt.xlabel(f"Year", size=12)
plt.ylabel("Dimension weight", size=12)
plt.ylim(0, y_max)

# Adjust y axis ticks
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.1))

# Specify the number of columns in the legend
ncol = 1

# Place the legend below the plot without a title and without a box
plt.legend(
    fontsize=12,
    loc="upper center",
    bbox_to_anchor=(1.12, 1.05),
    ncol=ncol,
    frameon=False,
)

plt.tight_layout()
plt.savefig(
    f"../figures/{superquestion}_{c}_temporal_nonlinear.jpg",
    dpi=300,
    bbox_inches="tight",
)
