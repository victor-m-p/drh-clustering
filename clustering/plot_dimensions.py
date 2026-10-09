"""
Plots of the cluster dimensions (theta: P(Yes) per question and cluster)
for the best solution at each c:
- heatmap (EM_dimensions_{subset}_c{c}.jpg)
- profile plot, one line per cluster (EM_profile_{subset}_c{c}.jpg)
Questions are in a fixed order grouped by topic (same across c), and clusters
are ordered by the median start year of the entries assigned to them.
Run from inside clustering/ after run_clustering.py.
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# setup
c_plot = [3, 4]
subset = "group"
fig_dir = "fig/dimensions"
os.makedirs(fig_dir, exist_ok=True)

# fixed question order, grouped by topic (top to bottom in the plots)
question_groups = {
    # supernatural monitoring (n=20)
    "monitoring: harm": [
        "murder coreligionists",
        "murder other religions",
        "murder other polities",
        "non-lethal fighting",
    ],
    "monitoring: social norms": [
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
    "monitoring: ritual and purity": [
        "ritual observance",
        "performance of rituals",
        "taboos",
        "personal hygiene",
        "sorcery",
    ],
    "monitoring: conversion": ["conversion non-religionists"],
    # supreme high god (n=16)
    "shg: power": [
        "knowledge this world",
        "causal efficacy the world",
        "indirect causal efficacy the world",
        "communicates with living",
    ],
    "shg: character": ["is unquestionably good", "positive emotion", "negative emotion"],
    "shg: nature": ["is anthropomorphic", "possesses hunger", "is sky deity", "is chthonic"],
    "shg: exclusivity": ["permissible to worship other god?"],
    "shg: elites": [
        "is monarch fused",
        "is monarch manifestation",
        "is kin to elites",
        "other elite loyalty",
    ],
}
question_order = [q for group in question_groups.values() for q in group]
group_ends = np.cumsum([len(group) for group in question_groups.values()])[:-1]
monitoring_end = sum(len(g) for k, g in question_groups.items() if k.startswith("monitoring"))

# cluster colors (categorical palette, fixed order) and marker shapes
colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
markers = ["o", "s", "^", "D"]


def format_year(year):
    return f"{-int(year)} BCE" if year < 0 else f"{int(year)} CE"


for c in c_plot:
    # load data
    df_theta = pd.read_csv(f"data/EM_theta_{subset}_c{c}.csv")
    df_q = pd.read_csv(f"data/EM_q_{subset}_c{c}.csv")
    dims = [f"dim{i}" for i in range(c)]

    # first row holds pi (cluster shares); the rest is theta
    pi = df_theta[df_theta["question_id"] == -1].iloc[0]
    df_theta = df_theta[df_theta["question_id"] != -1]

    # order clusters by median start year of the entries assigned to them
    # (one row per entry: weighted sum of q over expanded rows, then top cluster)
    df_q[dims] = df_q[dims].multiply(df_q["weight"], axis=0)
    df_entry = df_q.groupby(["entry_id", "year_from"], as_index=False)[dims].sum()
    df_entry["top"] = df_entry[dims].idxmax(axis=1)
    median_year = df_entry.groupby("top")["year_from"].median().reindex(dims)
    dims_ordered = median_year.sort_values(na_position="last").index.tolist()
    labels = [f"{d} ({pi[d]:.0%})\nmedian {format_year(median_year[d])}" for d in dims_ordered]

    # theta in the fixed question order and cluster order
    df_plot1 = df_theta.set_index("question_short")
    assert set(df_plot1.index) == set(question_order), "question_order does not match the data"
    df_plot1 = df_plot1.loc[question_order]
    question_mean = df_plot1["question_mean"]
    df_plot1 = df_plot1[dims_ordered]
    df_plot1.columns = labels

    ### heatmap ###
    ndim = len(df_plot1.columns)
    fig, ax = plt.subplots(
        1, 1, figsize=(4 + ndim * 1.3, 8), dpi=300
    )  # Adjust the figsize as needed (room for question labels + one column per cluster)
    sns.heatmap(df_plot1, cmap="coolwarm", center=0, ax=ax)
    for y in group_ends:  # separators between topic groups
        ax.axhline(y, color="white", linewidth=2 if y == monitoring_end else 0.8)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, size=9)
    ax.set_xlabel("Dimension", size=14)
    ax.set_ylabel("Question", size=14)
    plt.yticks(size=12)
    plt.tight_layout()
    plt.savefig(
        f"{fig_dir}/EM_dimensions_{subset}_c{c}.jpg",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    ### profile plot: one line per cluster across questions ###
    y_pos = np.arange(len(question_order))
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 8), dpi=300)

    # overall share of Yes per question, as a muted reference
    ax.plot(question_mean.values, y_pos, color="#898781", linewidth=1, linestyle="--", zorder=1, label="all entries")

    for i, (d, label) in enumerate(zip(dims_ordered, labels)):
        ax.plot(
            df_plot1[label].values,
            y_pos,
            color=colors[i],
            linewidth=1.5,
            marker=markers[i],
            markersize=5,
            markeredgecolor="white",
            markeredgewidth=0.6,
            zorder=2,
            label=label.replace("\n", ", "),
        )

    # separators between topic groups, labels for the two parent questions
    for y in group_ends:
        ax.axhline(y - 0.5, color="#c3c2b7" if y == monitoring_end else "#e1e0d9", linewidth=1 if y == monitoring_end else 0.6, zorder=0)
    ax.text(1.02, (monitoring_end - 1) / 2, "supernatural monitoring", rotation=270, va="center", ha="left", color="#52514e", size=10, transform=ax.get_yaxis_transform())
    ax.text(1.02, (monitoring_end + len(question_order) - 1) / 2, "supreme high god", rotation=270, va="center", ha="left", color="#52514e", size=10, transform=ax.get_yaxis_transform())

    ax.set_yticks(y_pos)
    ax.set_yticklabels(question_order, size=10, color="#0b0b0b")
    ax.invert_yaxis()  # first question at the top
    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("P(Yes | cluster)", size=12, color="#52514e")
    ax.grid(axis="x", color="#e1e0d9", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors="#898781", labelcolor="#0b0b0b", labelsize=10)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=2, frameon=False, fontsize=9)
    plt.tight_layout()
    plt.savefig(
        f"{fig_dir}/EM_profile_{subset}_c{c}.jpg",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
