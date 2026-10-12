"""
Overview of all questions over time: one small panel per question,
one figure for supernatural monitoring (20) and one for supreme high gods (16).
Same calculation as plot_question_time.py (500-year rolling window, step 50,
conflicting answers weighted 1/n). Stretches based on fewer than min_n
entries are drawn in light grey.
Run from inside temporal/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from helper_functions import smooth_time_end

# setup
subset = "groups"  # all
x_min = -2000
bin_width = 500
step_size = 50
min_n = 10  # bins with fewer entries than this are drawn in light grey
fig_dir = "fig/all_questions"
os.makedirs(fig_dir, exist_ok=True)

# questions in topic order (same order as clustering/plot_dimensions.py)
question_groups = {
    "monitoring": {
        "harm": [
            "murder coreligionists",
            "murder other religions",
            "murder other polities",
            "non-lethal fighting",
        ],
        "social norms": [
            "prosocial norm adherence",
            "lying",
            "honouring oaths",
            "property crimes",
            "economic fairness",
            "gossiping",
            "laziness",
            "shirking risk",
            "disrespecting elders",
            "sex",
        ],
        "ritual and purity": [
            "ritual observance",
            "performance of rituals",
            "taboos",
            "personal hygiene",
            "sorcery",
        ],
        "conversion": ["conversion non-religionists"],
    },
    "shg": {
        "power": [
            "knowledge this world",
            "causal efficacy the world",
            "indirect causal efficacy the world",
            "communicates with living",
        ],
        "character": ["is unquestionably good", "positive emotion", "negative emotion"],
        "nature": ["is anthropomorphic", "possesses hunger", "is sky deity", "is chthonic"],
        "exclusivity": ["permissible to worship other god?"],
        "elites": [
            "is monarch fused",
            "is monarch manifestation",
            "is kin to elites",
            "other elite loyalty",
        ],
    },
}
titles = {"monitoring": "Supernatural Monitoring", "shg": "Supreme High God"}

# colors (line, sparse stretches, chrome)
color_line = "#2a78d6"
color_sparse = "#c3c2b7"
color_grid = "#e1e0d9"
color_muted = "#898781"

# load and merge (as in plot_question_time.py)
df = pd.read_csv(f"../data/preprocessed/answers_subset_{subset}.csv")
df = df[["entry_id", "question_short", "question_id", "answer_value", "weight"]]
entry_metadata = pd.read_csv(f"../data/sccsrv3/entry_data.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to", "poll_name"]]
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
df_agg = df_agg[df_agg["time_bin"] >= x_min - step_size]
x_max = df_agg["time_bin"].max()

for superquestion, groups in question_groups.items():
    questions = [q for group in groups.values() for q in group]
    assert set(questions) <= set(df_agg["question_short"]), "question names do not match the data"

    ncol = 4
    nrow = int(np.ceil(len(questions) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.5 * ncol, 2.3 * nrow), dpi=300, sharex=True, sharey=True)

    for ax, question in zip(axes.flat, questions):
        d = df_agg[df_agg["question_short"] == question].sort_values("time_bin")
        # full line in light grey, then the well-supported stretches on top
        ax.plot(d["time_bin"], d["fraction_yes"], color=color_sparse, linewidth=1.6)
        ax.plot(d["time_bin"], d["fraction_yes"].where(d["n"] >= min_n), color=color_line, linewidth=2.2)
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

    fig.supxlabel("Year (500-year rolling window)", size=14, color="#52514e")
    fig.supylabel("Fraction yes", size=14, color="#52514e")
    fig.suptitle(
        titles[superquestion],
        size=18,
        x=0.01,
        ha="left",
    )
    plt.tight_layout()
    plt.savefig(
        f"{fig_dir}/questions_temporal_all_{superquestion}_{subset}.jpg",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
