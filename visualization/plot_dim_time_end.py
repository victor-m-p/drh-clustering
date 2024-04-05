""" 
Also considers end time. 
"""

# consider automatic selection of y axis
# consider automatic handling of filese and c value
# handle legend in a better way

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

pd.options.mode.chained_assignment = None

# setup
c = 10
x_min = -1000
superquestion = "shg"

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

# 3. smoothed over time
bin_width = 500
step_size = 100
max_year = df_temporal["year_to"].max()
x_max = max_year - (bin_width / 2)

from helper_functions import smooth_time_end

df_smoothed = smooth_time_end(df_temporal, bin_width, step_size)

# Aggregate the data within each bin for each dimension
df_smoothed_agg = (
    df_smoothed.groupby("time_bin")[dimension_columns].mean().reset_index()
)

# Melt the aggregated DataFrame for plotting
df_smoothed_long = df_smoothed_agg.melt(
    id_vars=["time_bin"],
    value_vars=dimension_columns,
    var_name="dimension",
    value_name="value",
)

# Take only from the time range
df_smoothed_long = df_smoothed_long[df_smoothed_long["time_bin"] >= x_min - step_size]
y_max = df_smoothed_long["value"].max()
y_max = y_max + 0.05

# Plot
plt.figure(figsize=(8, 4), dpi=300)
sns.lineplot(data=df_smoothed_long, x="time_bin", y="value", hue="dimension")
plt.xticks(rotation=45)
plt.yticks()
delta = int(np.round(bin_width / 2, 0))
plt.xlabel(f"Year", size=12)
plt.ylabel("Dimension weight", size=12)
plt.xlim(x_min, x_max)
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
    f"../figures/{superquestion}_{c}_temporal_span.jpg", dpi=300, bbox_inches="tight"
)
