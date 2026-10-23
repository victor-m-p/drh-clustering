"""
Features over time by tradition, to see whether change happens within traditions
or through replacement (e.g. Christianity always high, and simply becoming more common).
Each group entry is assigned to one tradition, using the flags from
modeling/1_code_entrytags.py in this priority:
Islamic > Buddhist > Christian > Jewish > Hindu > Chinese > Other
("Chinese" is then Chinese religion that is not Buddhist: Daoist, Confucian, folk, state;
Jain and Sikh entries are in "Other").
Figures:
- composition: share of entries in each tradition over time
- one panel per question (monitoring, supreme high god), one line per tradition
Same calculation as plot_question_time.py (rolling window of bin_width years, moved
in steps of step_size; conflicting answers weighted 1/n). A tradition's line is only drawn in bins
with at least min_n entries of that tradition.
Run from inside temporal/ after modeling/1_code_entrytags.py.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from helper_functions import smooth_time_end

# setup
subset = "groups"
x_min = -2000
bin_width = 100  # years per rolling window (used in labels and file names)
step_size = 50
min_n = 5  # minimum entries of a tradition in a bin for its line to be drawn
fig_dir = "fig/traditions"
os.makedirs(fig_dir, exist_ok=True)

# traditions (in priority order) and colors (categorical palette, fixed order; "Other" in grey; "All" = all entries, dashed black)
traditions = ["Islamic", "Buddhist", "Christian", "Jewish", "Hindu", "Chinese", "Other"]
colors = {
    "Christian": "#2a78d6",
    "Islamic": "#eb6834",
    "Buddhist": "#1baf7a",
    "Chinese": "#eda100",
    "Jewish": "#e87ba4",
    "Hindu": "#008300",
    "Other": "#898781",
}
color_all = "#0b0b0b"
plot_order = ["Christian", "Islamic", "Jewish", "Buddhist", "Hindu", "Chinese", "Other"]  # legend order
color_grid = "#e1e0d9"
color_muted = "#898781"

# questions in topic order (same order as plot_all_questions_time.py)
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

# tradition per entry
entry_tags = pd.read_csv("../modeling/data/entry_tags.csv").drop_duplicates("entry_id")
flags = {"Islamic": "islamic", "Buddhist": "buddhist", "Christian": "christian", "Jewish": "jewish", "Hindu": "hindu", "Chinese": "chinese"}
entry_tags["tradition"] = "Other"
for tradition in reversed(traditions[:-1]):  # highest priority assigned last
    entry_tags.loc[entry_tags[flags[tradition]].astype(bool), "tradition"] = tradition
entry_tags = entry_tags[["entry_id", "tradition"]]

# load and merge (as in plot_question_time.py)
df = pd.read_csv(f"../data/preprocessed/answers_subset_{subset}.csv")
df = df[["entry_id", "question_short", "question_id", "answer_value", "weight"]]
entry_metadata = pd.read_csv(f"../data/sccsrv3/entry_data.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to"]]
df = df.merge(entry_metadata, on="entry_id", how="inner")
df = df.merge(entry_tags, on="entry_id", how="inner")
df["year_from"] = df["year_from"].astype(int)
df["year_to"] = df["year_to"].astype(int)
df = df.dropna()
df["answer_value"] = df["answer_value"].astype(int)
print("group entries per tradition:", df.drop_duplicates("entry_id")["tradition"].value_counts().to_dict())


def style(ax, x_max):
    ax.set_xlim(x_min, x_max)
    ax.set_xticks([-2000, -1000, 0, 1000])
    ax.grid(color=color_grid, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=color_muted, labelsize=11.5, labelcolor="#52514e")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#c3c2b7")


### composition: share of entries per tradition over time ###
entries = df.drop_duplicates("entry_id")[["entry_id", "year_from", "year_to", "tradition"]]
entries_time = smooth_time_end(entries, bin_width, step_size)
composition = entries_time.groupby(["time_bin", "tradition"]).size().unstack(fill_value=0)
composition = composition[composition.index >= x_min - step_size]
n_bin = composition.sum(axis=1)
share = composition.div(n_bin, axis=0)[plot_order]
x_max = share.index.max()

fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
ax.stackplot(share.index, *[share[t] for t in plot_order], labels=plot_order, colors=[colors[t] for t in plot_order], alpha=0.85, edgecolor="white", linewidth=0.5)
style(ax, x_max)
ax.set_ylim(0, 1)
ax.set_ylabel("Share of entries", size=13, color="#52514e")
ax.set_xlabel(f"Year ({bin_width}-year rolling window)", size=13, color="#52514e")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=12)
ax.set_title(f"Composition of the sample by tradition ({subset})", size=15, loc="left")
plt.tight_layout()
plt.savefig(f"{fig_dir}/composition_{subset}_{bin_width}.jpg", dpi=300, bbox_inches="tight")
plt.close()

### features over time by tradition ###
df_time = smooth_time_end(df, bin_width, step_size)
df_agg = (
    df_time.groupby(["time_bin", "question_short", "tradition"])
    .apply(lambda x: (x["answer_value"] * x["weight"]).sum() / x["weight"].sum(), include_groups=False)
    .reset_index(name="fraction_yes")
)
df_n = df_time.groupby(["time_bin", "question_short", "tradition"])["entry_id"].nunique().reset_index(name="n")
df_agg = df_agg.merge(df_n, on=["time_bin", "question_short", "tradition"])
df_agg = df_agg[(df_agg["time_bin"] >= x_min - step_size) & (df_agg["n"] >= min_n)]

# all entries together (the same line as in plot_question_time.py)
df_all = (
    df_time.groupby(["time_bin", "question_short"])
    .apply(lambda x: (x["answer_value"] * x["weight"]).sum() / x["weight"].sum(), include_groups=False)
    .reset_index(name="fraction_yes")
)
df_all = df_all[df_all["time_bin"] >= x_min - step_size]

for superquestion, questions in question_groups.items():
    ncol = 4
    nrow = int(np.ceil(len(questions) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.5 * ncol, 2.5 * nrow), dpi=300, sharex=True, sharey=True)
    for ax, question in zip(axes.flat, questions):
        d = df_all[df_all["question_short"] == question].set_index("time_bin")["fraction_yes"].reindex(share.index)
        ax.plot(d.index, d.values, color=color_all, linewidth=2.2, linestyle="--", label="All", zorder=3)
        for tradition in plot_order:
            d = df_agg[(df_agg["question_short"] == question) & (df_agg["tradition"] == tradition)].sort_values("time_bin")
            # reindex on all bins so gaps (n < min_n) break the line
            d = d.set_index("time_bin")["fraction_yes"].reindex(share.index)
            ax.plot(d.index, d.values, color=colors[tradition], linewidth=1.8, label=tradition)
        ax.set_title(question, size=13, color="#0b0b0b", loc="left")
        ax.set_ylim(0, 1.02)
        ax.set_yticks([0, 0.5, 1])
        style(ax, x_max)
    for ax in axes.flat[len(questions):]:
        ax.set_visible(False)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", ncol=len(plot_order) + 1, frameon=False, fontsize=13, bbox_to_anchor=(0.005, 1.005))
    fig.supxlabel(f"Year ({bin_width}-year rolling window)", size=14, color="#52514e")
    fig.supylabel("Fraction yes", size=14, color="#52514e")
    fig.suptitle(titles[superquestion], size=18, x=0.01, y=1.075, ha="left")
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/{superquestion}_{subset}_{bin_width}.jpg", dpi=300, bbox_inches="tight")
    plt.close()
