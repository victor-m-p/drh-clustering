import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# setup
c = 3
y_max = 0.7
x_min = -1000
superquestion = "monitoring"

df_q = pd.read_csv(f"../data/EM/{superquestion}_q_{c}_all.csv")
dimension_columns = [f"dim{x}" for x in range(c)]
temporal_columns = ["entry_id", "entry_name", "year_from"] + dimension_columns
df_temporal = df_q[temporal_columns]
df_temporal["year_from"] = df_temporal["year_from"].astype(int)

# 3. smoothed over time
bin_width = 500
step_size = 30
max_year = df_temporal["year_from"].max()
x_max = max_year - (bin_width / 2)

from fun import smooth_time

df_smoothed = smooth_time(df_temporal, bin_width, step_size)

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

# Plot
plt.figure(figsize=(9, 4), dpi=300)
sns.lineplot(data=df_smoothed_long, x="time_bin", y="value", hue="dimension")
plt.xticks(rotation=45)
delta = int(np.round(bin_width / 2, 0))
plt.xlabel(f"Year (smoothed over {bin_width} years)", size=12)
plt.ylabel("Mean Dimension Value", size=12)
plt.xlim(x_min, x_max)
plt.ylim(0, y_max)
plt.legend(title="Dimension", fontsize=12, title_fontsize=12, loc="upper right")
plt.tight_layout()
plt.savefig(f"fig/{superquestion}_{c}_smoothed.jpg")
