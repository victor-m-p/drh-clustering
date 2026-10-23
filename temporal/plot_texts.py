"""
Religious groups vs. groups and texts together over time (same panels as plot_all_questions_time.py).
Conditional answers only (child questions as answered).
Stretches based on fewer than min_n entries are drawn faded.
Run from inside temporal/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from helper_functions import smooth_time_end

# setup
x_min = -2000
bin_width = 100  # years per rolling window (used in labels and file names)
step_size = 50
min_n = 10  # bins with fewer entries than this are drawn faded
fig_dir = "fig/texts"
os.makedirs(fig_dir, exist_ok=True)

# the two versions to compare (label: file) and their colors
versions = {
    "groups": "../data/preprocessed/answers_subset_groups.csv",
    "groups + texts": "../data/preprocessed/answers_subset_all.csv",
}
colors = {"groups": "#2a78d6", "groups + texts": "#eb6834"}

# questions in topic order (same as plot_all_questions_time.py)
question_groups = {
    "monitoring": [
        "murder coreligionists", "murder other religions", "murder other polities", "non-lethal fighting",
        "prosocial norm adherence", "lying", "honouring oaths", "property crimes", "economic fairness",
        "gossiping", "laziness", "shirking risk", "disrespecting elders", "sex",
        "ritual observance", "performance of rituals", "taboos", "personal hygiene", "sorcery",
        "conversion non-religionists",
    ],
    "shg": [
        "knowledge this world", "causal efficacy the world", "indirect causal efficacy the world", "communicates with living",
        "is unquestionably good", "positive emotion", "negative emotion",
        "is anthropomorphic", "possesses hunger", "is sky deity", "is chthonic",
        "permissible to worship other god?",
        "is monarch fused", "is monarch manifestation", "is kin to elites", "other elite loyalty",
    ],
}
titles = {"monitoring": "Supernatural Monitoring", "shg": "Supreme High God"}
color_grid = "#e1e0d9"
color_muted = "#898781"

entry_metadata = pd.read_csv("../data/sccsrv3/entry_data.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to"]]


def fraction_yes(file):
    # load and merge (as in plot_all_questions_time.py)
    df = pd.read_csv(file)
    df = df[["entry_id", "question_short", "question_id", "answer_value", "weight"]]
    df = df.merge(entry_metadata, on="entry_id", how="inner")
    df["year_from"] = df["year_from"].astype(int)
    df["year_to"] = df["year_to"].astype(int)
    df = df.dropna()
    df["answer_value"] = df["answer_value"].astype(int)

    # time-slices: weighted fraction yes and number of entries per (bin, question)
    df_time = smooth_time_end(df, bin_width, step_size)
    df_agg = (
        df_time.groupby(["time_bin", "question_short"])
        .apply(lambda x: (x["answer_value"] * x["weight"]).sum() / x["weight"].sum(), include_groups=False)
        .reset_index(name="fraction_yes")
    )
    df_n = df_time.groupby(["time_bin", "question_short"])["entry_id"].nunique().reset_index(name="n")
    df_agg = df_agg.merge(df_n, on=["time_bin", "question_short"])
    return df_agg[df_agg["time_bin"] >= x_min - step_size]


df_agg = {version: fraction_yes(file) for version, file in versions.items()}
x_max = max(d["time_bin"].max() for d in df_agg.values())

for superquestion, questions in question_groups.items():
    ncol = 4
    nrow = int(np.ceil(len(questions) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.5 * ncol, 2.3 * nrow), dpi=300, sharex=True, sharey=True, layout="constrained")

    for ax, question in zip(axes.flat, questions):
        for version in versions:
            d = df_agg[version]
            d = d[d["question_short"] == question].sort_values("time_bin")
            # full line faded, then the well-supported stretches on top
            ax.plot(d["time_bin"], d["fraction_yes"], color=colors[version], linewidth=1.4, alpha=0.3)
            ax.plot(d["time_bin"], d["fraction_yes"].where(d["n"] >= min_n), color=colors[version], linewidth=2, label=version)
        ax.set_title(question, size=13, color="#0b0b0b", loc="left")
        ax.set_ylim(0, 1.02)
        ax.set_xlim(x_min, x_max)
        ax.set_yticks([0, 0.5, 1])
        ax.set_xticks([-2000, -1000, 0, 1000])
        ax.grid(color=color_grid, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(colors=color_muted, labelsize=11.5, labelcolor="#52514e")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color("#c3c2b7")

    # hide unused panels
    for ax in axes.flat[len(questions):]:
        ax.set_visible(False)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper right", ncol=len(versions), frameon=False, fontsize=13)
    fig.supxlabel(f"Year ({bin_width}-year rolling window)", size=14, color="#52514e")
    fig.supylabel("Fraction yes", size=14, color="#52514e")
    fig.suptitle(titles[superquestion], size=18, x=0.01, ha="left")
    plt.savefig(f"{fig_dir}/{superquestion}_{bin_width}.jpg", dpi=300, bbox_inches="tight")
    plt.close()
