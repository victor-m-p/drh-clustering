"""
Society type (social_complexity from preprocessing/curate_covariates.py) over time in our sample:
number of entries and share per level (band, tribe, chiefdom, state, empire); groups (v5 + v6) and texts.
Same smoothing as the temporal plots (temporal/plot_question_time.py): rolling window of bin_width years,
moved in steps of step_size; an entry counts in every window its time span overlaps.
Entries without a society type are left out. Shares are not shown for windows with fewer than min_n entries.

Figure: fig/covariates/social_complexity_time_{bin_width}.jpg

Run from inside eda/ after preprocessing/curate_covariates.py.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append("../temporal")
from helper_functions import smooth_time_end

# setup
x_min = -2000
bin_width = 100  # years per rolling window (used in labels and file names)
step_size = 50
min_n = 10
fig_dir = "fig/covariates"
os.makedirs(fig_dir, exist_ok=True)
levels = ["band", "tribe", "chiefdom", "state", "empire"]
level_colors = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]  # ordinal blue ramp, light to dark
poll_labels = {"group": "Religious groups", "text": "Religious texts"}
color_grid = "#e1e0d9"
color_axis = "#c3c2b7"
color_text = "#52514e"

# entries with society type and time span
covariates = pd.read_csv("../data/preprocessed/entry_covariates.csv")
covariates = covariates.dropna(subset=["social_complexity"])[["entry_id", "poll_name", "social_complexity"]]
entry_metadata = pd.read_csv("../data/sccsrv3/entry_data.csv")[["entry_id", "year_from", "year_to"]]
d = covariates.merge(entry_metadata, on="entry_id", how="inner")
assert len(d) == len(covariates)
d["poll"] = np.where(d["poll_name"].str.contains("Group"), "group", "text")
d[["year_from", "year_to"]] = d[["year_from", "year_to"]].astype(int)

# number of entries per window, poll and level
d_time = smooth_time_end(d, bin_width, step_size)
counts = (
    d_time.groupby(["poll", "time_bin", "social_complexity"])["entry_id"].nunique()
    .unstack(fill_value=0)
    .reindex(columns=levels, fill_value=0)
)
counts = counts[counts.index.get_level_values("time_bin") >= x_min - step_size]
x_max = counts.index.get_level_values("time_bin").max()

fig, axes = plt.subplots(2, 2, figsize=(13, 7), dpi=300, sharex=True)
for col, poll in enumerate(poll_labels):
    c = counts.loc[poll]
    total = c.sum(axis=1)
    share = c.div(total, axis=0).where(total >= min_n, axis=0)  # NaN: gap in the areas
    for ax, values in zip(axes[:, col], [c, 100 * share]):
        ax.stackplot(c.index, values.T.values, colors=level_colors, labels=levels, edgecolor="white", linewidth=0.6)
        ax.set_xlim(x_min, x_max)
        ax.set_xticks([-2000, -1000, 0, 1000, 2000])
        ax.grid(color=color_grid, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(color_axis)
        ax.tick_params(length=0, labelsize=10, colors=color_text)
    axes[0, col].set_title(poll_labels[poll], fontsize=13, loc="left")
    axes[1, col].set_ylim(0, 100)
axes[0, 0].set_ylabel("Number of entries", size=11, color=color_text)
axes[1, 0].set_ylabel(f"% of entries\n(windows with {min_n}+ entries)", size=11, color=color_text)
handles, labels = axes[0, 0].get_legend_handles_labels()
axes[0, 1].legend(handles[::-1], labels[::-1], frameon=False, fontsize=10, loc="upper left", bbox_to_anchor=(1.02, 1))
fig.supxlabel(f"Year ({bin_width}-year rolling window)", size=12, color=color_text)
plt.tight_layout()
plt.savefig(f"{fig_dir}/social_complexity_time_{bin_width}.jpg", bbox_inches="tight")
plt.close()

# entries per level and poll, and share before / after 500 CE (by start year)
print(pd.crosstab(d["poll"], d["social_complexity"]).reindex(columns=levels))
print(pd.crosstab([d["poll"], np.where(d["year_from"] < 500, "before 500", "500 and later")],
                  d["social_complexity"], normalize="index").reindex(columns=levels).round(2))
