"""
Sample figure: entries by start year, region and source (groups, texts), Abrahamic vs. other.

Same sample as modeling/13_main.Rmd (groups) and modeling/15_texts.Rmd (texts): start year in 3000 BCE-1500 CE,
the four regions, no eHRAF/Pulotu entries, and at least one answer to a modeled question (as answered: no inferred
answers, no conflicting answers). Abrahamic coding from modeling/1_code_entrytags.py (column abrahamic).
One point per entry at its start year, jittered vertically; grey band: 800-200 BCE.

Figure: fig/sample/sample.jpg

Run from inside eda/ after modeling/3_prepare_data.py.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# setup
regions = ["Southwest Asia", "Europe", "Africa", "East Asia"]
year_min, year_max = -3000, 1500
parents = ["supernatural monitoring present", "supreme high god present"]
color_abrahamic = "#7d4fc9"
color_other = "#a3a29b"
color_band = "#ecebe6"
color_text = "#52514e"
fig_dir = "fig/sample"
os.makedirs(fig_dir, exist_ok=True)

# data (same filters as modeling/13_main.Rmd and 15_texts.Rmd)
source_of = pd.read_csv("../data/sccsrv3/entry_data.csv", usecols=["entry_id", "data_source"]).drop_duplicates("entry_id")
d = pd.read_csv("../modeling/data/model_data.csv").merge(source_of, on="entry_id", how="left")
ds = d["data_source"].fillna("")
d = d[
    d["poll"].isin(["group", "text"])
    & d["world_region"].isin(regions)
    & (ds != "eHRAF") & ~ds.str.startswith("Pulotu")
    & d["year_from"].between(year_min, year_max - 1)
    & (d["weight"] == 1) & ~d["inferred"]
    & ((d["family"] != "parent") | d["question_short"].isin(parents))
]
entries = d[["entry_id", "poll", "world_region", "year_from", "abrahamic"]].drop_duplicates()
assert entries["entry_id"].is_unique
print(entries["poll"].value_counts())  # 275 groups, 235 texts

# plot: one panel per region, groups above texts
rng = np.random.default_rng(1)
rows = {"group": 1, "text": 0}
labels = {"group": "groups", "text": "texts"}
fig, axes = plt.subplots(len(regions), 1, figsize=(8, 7), sharex=True)
for ax, region in zip(axes, regions):
    ax.axvspan(-800, -200, color=color_band, zorder=0, lw=0)
    for poll, y in rows.items():
        e = entries[(entries["world_region"] == region) & (entries["poll"] == poll)]
        jitter = rng.uniform(-0.22, 0.22, len(e))
        for abr, color in [(0, color_other), (1, color_abrahamic)]:
            sel = (e["abrahamic"] == abr).to_numpy()
            ax.scatter(e["year_from"][sel], y + jitter[sel], s=10, color=color, alpha=0.8, lw=0, zorder=2)
        ax.text(1.01, y, f"{len(e)} ({int(e['abrahamic'].sum())} Abr.)", transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=8, color=color_text)
    ax.set_title(region, loc="left", fontsize=10, fontweight="bold")
    ax.set_yticks(list(rows.values()), [labels[p] for p in rows])
    ax.set_ylim(-0.5, 1.5)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#e1e0d9", lw=0.6, zorder=1)
    ax.set_axisbelow(True)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)

ticks = np.arange(year_min, year_max + 1, 500)
axes[-1].set_xticks(ticks, [f"{-t} BCE" if t < 0 else ("0" if t == 0 else f"{t} CE") for t in ticks], fontsize=8)
axes[-1].set_xlim(year_min - 50, year_max + 50)
axes[-1].set_xlabel("Start year")
handles = [plt.Line2D([], [], marker="o", ls="", color=c, markersize=5) for c in [color_abrahamic, color_other]]
fig.legend(handles, ["Abrahamic", "other"], loc="upper center", ncol=2, frameon=False, fontsize=9)
fig.tight_layout(rect=(0, 0, 0.97, 0.96))
fig.savefig(os.path.join(fig_dir, "sample.jpg"), dpi=300)
