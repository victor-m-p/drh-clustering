import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fun import smooth_time

# setup
c = 3
y_max = 0.7
x_min = -1000

df_q_monitoring = pd.read_csv(f"../data/EM/monitoring_q_{c}_all.csv")
df_q_shg = pd.read_csv(f"../data/EM/shg_q_{c}_all.csv")

dimension_columns = [f"dim{x}" for x in range(c)]
temporal_columns = ["entry_id", "entry_name", "year_from"] + dimension_columns

df_temporal_monitoring = df_q_monitoring[temporal_columns]
df_temporal_q = df_q_shg[temporal_columns]

df_temporal_monitoring["year_from"] = df_temporal_monitoring["year_from"].astype(int)
df_temporal_q["year_from"] = df_temporal_q["year_from"].astype(int)

# 3. smoothed over time
df_smoothed = pd.DataFrame()
bin_width = 500
step_size = 30
max_year = np.max(
    [df_temporal_monitoring["year_from"].max(), df_temporal_q["year_from"].max()]
)
x_max = max_year - (bin_width / 2)

df_smoothed_monitoring = smooth_time(df_temporal_monitoring, bin_width, step_size)
df_smoothed_shg = smooth_time(df_temporal_q, bin_width, step_size)

# Aggregate the data within each bin for each dimension
df_smoothed_agg_monitoring = (
    df_smoothed_monitoring.groupby("time_bin")[dimension_columns].mean().reset_index()
)
df_smoothed_agg_shg = (
    df_smoothed_shg.groupby("time_bin")[dimension_columns].mean().reset_index()
)

# Melt the aggregated DataFrame for plotting
df_smoothed_long_monitoring = df_smoothed_agg_monitoring.melt(
    id_vars=["time_bin"],
    value_vars=dimension_columns,
    var_name="dimension",
    value_name="value",
)
df_smoothed_long_shg = df_smoothed_agg_shg.melt(
    id_vars=["time_bin"],
    value_vars=dimension_columns,
    var_name="dimension",
    value_name="value",
)

# Plot
delta = int(np.round(bin_width / 2, 0))

fig, ax = plt.subplots(1, 2, figsize=(12, 5), dpi=300)  # Adjust the figsize as needed
sns.lineplot(
    data=df_smoothed_long_shg, x="time_bin", y="value", hue="dimension", ax=ax[0]
)
ax[0].set_xlim(x_min, x_max)
ax[0].set_ylim(0, y_max)
ax[0].set_ylabel("Mean Dimension Value", size=12)
ax[0].set_xlabel(f"Year", size=12)
ax[0].legend(title="Dimension", fontsize=12, title_fontsize=12, loc="upper right")
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha="right")
ax[0].set_title("Supernatural high God", size=15)

sns.lineplot(
    data=df_smoothed_long_monitoring, x="time_bin", y="value", hue="dimension", ax=ax[1]
)
ax[1].set_xlim(x_min, x_max)
ax[1].set_ylim(0, y_max)
ax[1].legend(title="Dimension", fontsize=12, title_fontsize=12, loc="upper right")
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha="right")
ax[1].set_ylabel("", size=12)
ax[1].set_xlabel(f"Year", size=12)
ax[1].set_yticklabels([])  # Remove the y-tick labels
ax[1].set_title("Supernatural monitoring", size=15)

plt.tight_layout()
plt.savefig(f"fig/combined_{c}_smoothed.jpg")
