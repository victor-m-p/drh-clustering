"""
Change over time within society type (state, empire; bands, tribes and chiefdoms are mostly after 1500).
Share "Yes" per question, one line per society type; groups (v5 + v6) and texts separately.
Rolling window of bin_width years, moved in steps of step_size (as in temporal/); an entry counts in every
window its time span overlaps; windows with fewer than min_n entries in light grey.

Questions (one figure each):
- politics: parent questions, supernatural punishment and reward, the covariate questions of
  preprocessing/curate_covariates.py (answers_covariates.csv), the supreme high god elite questions
- shg, monitoring: all child questions (conditional, as in temporal/), order as in temporal/plot_all_questions_time.py
Entries with conflicting answers count with weight 1/n per answer.

Inferred vs. as answered:
- inferred "No": supreme high god present when supernatural beings are absent (curate_answers.py);
  head of polity is head of religion (2339) and political officials are religious officials (2319)
  when official political support (2300) is "No" (curate_covariates.py)
- any elite / monarch tie (summary figures): derived here, see below
- everything else as answered: supreme high god and monitoring child questions are conditional
  (only answered when their parent is "Yes"); unanswered is left out, never "No"
Text polls ask other things for 2300, 2339 and 2319 (funding and support of the text's production).

Figures: fig/within_type_time/{questions}_{poll}_{bin_width}.jpg

Run from inside eda/ after preprocessing/curate_answers.py and preprocessing/curate_covariates.py.
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
bin_width = 500  # years per rolling window (used in labels and file names)
step_size = 50
min_n = 10
fig_dir = "fig/within_type_time"
os.makedirs(fig_dir, exist_ok=True)
types = ["state", "empire"]
type_colors = ["#5598e7", "#104281"]  # blue ramp, light to dark
poll_labels = {"group": "Religious groups", "text": "Religious texts"}
color_grid = "#e1e0d9"
color_sparse = "#c3c2b7"
color_text = "#52514e"

questions = {
    "politics": [
        "supernatural monitoring present", "supreme high god present",
        "supernatural punishment", "supernatural reward",
        "official political support", "head of polity is head of religion",
        "political officials are religious officials",
        "is monarch fused", "is monarch manifestation", "is kin to elites", "other elite loyalty",
    ],
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
titles = {"politics": "Religion and politics", "monitoring": "Supernatural Monitoring", "shg": "Supreme High God"}

"""
Answers: one row per answer (entry_id, poll_name, question_short, answer_value, weight).
"""

cols = ["entry_id", "poll_name", "question_short", "answer_value", "weight"]
parents = pd.read_csv("../data/preprocessed/answers_parents_all.csv")
parents = parents[parents["question_short"].isin(questions["politics"])]
children = pd.read_csv("../data/preprocessed/answers_subset_all.csv").dropna(subset=["answer_value"])
covariate_answers = pd.read_csv("../data/preprocessed/answers_covariates.csv")

answers = pd.concat([parents[cols], children[cols], covariate_answers[cols]], ignore_index=True)
answers["poll"] = np.where(answers["poll_name"].str.contains("Group"), "group", "text")
assert set(q for qs in questions.values() for q in qs) <= set(answers["question_short"])

# society type and time span
covariates = pd.read_csv("../data/preprocessed/entry_covariates.csv")[["entry_id", "social_complexity"]]
entry_metadata = pd.read_csv("../data/sccsrv3/entry_data.csv")[["entry_id", "year_from", "year_to"]]
answers = answers.merge(covariates, on="entry_id").merge(entry_metadata, on="entry_id")
answers = answers[answers["social_complexity"].isin(types)]
answers[["year_from", "year_to"]] = answers[["year_from", "year_to"]].astype(int)

# weighted share "Yes" and number of entries per poll, question, society type and time window
window = smooth_time_end(answers, bin_width, step_size)
by_window = (
    window.assign(yes=window["answer_value"] * window["weight"])
    .groupby(["poll", "question_short", "social_complexity", "time_bin"])
    .agg(n=("weight", "sum"), yes=("yes", "sum"))
    .reset_index()
)
by_window["p"] = by_window["yes"] / by_window["n"]
by_window = by_window[by_window["time_bin"] >= x_min - step_size]
by_window.to_csv(f"data/within_type_time_{bin_width}.csv", index=False)


def style(ax):
    ax.set_ylim(0, 1.02)
    ax.set_yticks([0, 0.5, 1])
    ax.grid(axis="y", color=color_grid, lw=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(color_sparse)
    ax.tick_params(length=0, labelsize=10, colors=color_text)


def plot_grid(poll, name):
    qs = questions[name]
    ncol = 4
    nrow = int(np.ceil(len(qs) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.6 * ncol, 2.5 * nrow), dpi=300, sharex=True, sharey=True)
    for ax, q in zip(axes.flat, qs):
        for t, color in zip(types, type_colors):
            st = by_window[(by_window["poll"] == poll) & (by_window["question_short"] == q)
                           & (by_window["social_complexity"] == t)].sort_values("time_bin")
            ax.plot(st["time_bin"], st["p"], color=color_sparse, lw=1.2, zorder=1)
            ax.plot(st["time_bin"], st["p"].where(st["n"] >= min_n), color=color, lw=2, zorder=2, label=t)
        ax.set_title(q, size=11.5, loc="left")
        style(ax)
        ax.set_xlim(x_min, 2000)
        ax.set_xticks([-2000, -1000, 0, 1000, 2000])
    for ax in axes.flat[len(qs):]:
        ax.set_visible(False)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=11, loc="upper right", ncol=len(types))
    fig.supxlabel(f"Year ({bin_width}-year rolling window)", size=13, color=color_text)
    fig.supylabel("Fraction yes", size=13, color=color_text)
    fig.suptitle(f"{titles[name]}: {poll_labels[poll].lower()} (fewer than {min_n} entries in light grey)",
                 size=16, x=0.01, ha="left")
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/{name}_{poll}_{bin_width}.jpg", bbox_inches="tight")
    plt.close()


for poll in poll_labels:
    for name in questions:
        plot_grid(poll, name)

"""
Summary figures: key questions, groups, states and empires pooled (bin_width-year rolling window).
Parent questions as grey reference lines; windows with fewer than min_n entries not shown.
- summary_group: eight questions in one panel
- summary_themes_{poll}: more questions in four panels by theme (religion and the polity, nature of the
  supreme high god, morality / exclusivity, monitoring); literacy is left out for texts
- summary_themes_group_non_abrahamic: the same for groups without Christian, Jewish and Islamic entries
  (tradition tags from modeling/1_code_entrytags.py; an entry is left out if it has any of the three)
- summary_themes_group_region_*: the same within world regions (all traditions; world_region as in
  modeling/3_prepare_data.py), some merged: Europe and Southwest Asia, East and Southeast Asia, South Asia, Africa.
  Africa is early Egypt and mostly sub-Saharan entries after 1500. The Americas, Oceania and Central Eurasia
  are mostly after 1500 and not shown.
Two extra variables:
- literacy: entry level, groups only (entry_covariates.csv; unanswered left out; all texts literate by construction)
- any elite / monarch tie: "Yes" if any of the four supreme high god elite questions is "Yes",
  "No" if at least one is answered and none is "Yes" (conditional on supreme high god present)
"""

series_colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]  # categorical, fixed order
reference_styles = {"supernatural monitoring present": (0, (4, 2)), "supreme high god present": (0, (1, 1.5))}
elite_questions = ["is monarch fused", "is monarch manifestation", "is kin to elites", "other elite loyalty"]
meta_cols = ["entry_id", "poll_name", "poll", "social_complexity", "year_from", "year_to"]

elite = answers[answers["question_short"].isin(elite_questions)].groupby(meta_cols)["answer_value"].max().reset_index()
elite = elite.assign(question_short="any elite / monarch tie", weight=1.0)
literacy = answers[meta_cols].drop_duplicates().merge(
    pd.read_csv("../data/preprocessed/entry_covariates.csv")[["entry_id", "literacy"]], on="entry_id"
)
literacy = literacy[literacy["poll"] == "group"].rename(columns={"literacy": "answer_value"}).dropna(subset=["answer_value"])
literacy = literacy.assign(question_short="literacy", weight=1.0)
summary_answers = pd.concat([answers, elite, literacy], ignore_index=True)

# Abrahamic traditions (Christian, Jewish, Islamic; modeling/1_code_entrytags.py)
entry_tags = pd.read_csv("../modeling/data/entry_tags.csv")
abrahamic = set(entry_tags.loc[entry_tags[["christian", "jewish", "islamic"]].any(axis=1), "entry_id"])


def pool(d):
    """Weighted share "Yes" per poll, question and time window (states and empires pooled)."""
    pooled = smooth_time_end(d, bin_width, step_size)
    pooled = (
        pooled.assign(yes=pooled["answer_value"] * pooled["weight"])
        .groupby(["poll", "question_short", "time_bin"])
        .agg(n=("weight", "sum"), yes=("yes", "sum"))
        .reset_index()
    )
    pooled["p"] = (pooled["yes"] / pooled["n"]).where(pooled["n"] >= min_n)
    return pooled[pooled["time_bin"] >= x_min - step_size]


pooled_all = pool(summary_answers)
pooled_non_abrahamic = pool(summary_answers[~summary_answers["entry_id"].isin(abrahamic)])
x_end = pooled_all["time_bin"].max()


def draw_panel(ax, pooled, poll, qs, references, title=None, label_size=9.5):
    """Lines for qs (categorical colors) and references (grey), labelled at their ends."""
    ends = []
    qs = [q for q in qs if pooled.loc[(pooled["poll"] == poll) & (pooled["question_short"] == q), "p"].notna().any()]
    for q in references:
        pq = pooled[(pooled["poll"] == poll) & (pooled["question_short"] == q)].sort_values("time_bin")
        ax.plot(pq["time_bin"], pq["p"], color="#898781", lw=1.6, ls=reference_styles[q], zorder=1)
        last = pq.dropna(subset=["p"]).iloc[-1]
        ends.append((last["p"], last["time_bin"], q, "#898781"))
    for q, color in zip(qs, series_colors):
        pq = pooled[(pooled["poll"] == poll) & (pooled["question_short"] == q)].sort_values("time_bin")
        ax.plot(pq["time_bin"], pq["p"], color=color, lw=2.2, zorder=2)
        last = pq.dropna(subset=["p"]).iloc[-1]
        ax.plot(last["time_bin"], last["p"], "o", ms=5, color=color, mec="white", mew=1, zorder=3)
        ends.append((last["p"], last["time_bin"], q, color))

    # direct labels at the line ends, spread so they do not overlap
    ends.sort()
    gap = 0.075 if len(ends) <= 6 else 0.045
    label_y = [ends[0][0]]
    for y, *_ in ends[1:]:
        label_y.append(max(y, label_y[-1] + gap))
    shift = max(0, label_y[-1] - 1.0)
    label_y = [y - shift for y in label_y]
    for (y, x, q, color), ly in zip(ends, label_y):
        ax.annotate(q, xy=(x, y), xytext=(x_end + 120, ly), fontsize=label_size, color=color_text, va="center",
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.8), annotation_clip=False)

    ax.set_xlim(-1500, x_end)
    ax.set_xticks([-1500, -1000, -500, 0, 500, 1000, 1500])
    style(ax)
    if title:
        ax.set_title(title, size=12, loc="left")


# eight questions in one panel
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
draw_panel(ax, pooled_all, "group", [
    "official political support", "head of polity is head of religion",
    "is unquestionably good", "is anthropomorphic", "permissible to worship other god?",
    "economic fairness", "conversion non-religionists", "possesses hunger",
], list(reference_styles))
ax.set_xlabel(f"Year ({bin_width}-year rolling window)", size=11, color=color_text)
ax.set_ylabel("Fraction yes", size=11, color=color_text)
ax.set_title(f"Religious groups in states and empires (grey: parent questions; fewer than {min_n} entries not shown)",
             size=12, loc="left")
plt.savefig(f"{fig_dir}/summary_group_{bin_width}.jpg", bbox_inches="tight")
plt.close()

# more questions in four panels by theme
themes = {
    "Religion and the polity": (
        ["official political support", "head of polity is head of religion", "any elite / monarch tie", "literacy"], []),
    "Supreme high god: nature": (
        ["is anthropomorphic", "possesses hunger", "is sky deity", "negative emotion"], ["supreme high god present"]),
    "Supreme high god: morality and exclusivity": (
        ["is unquestionably good", "permissible to worship other god?"], ["supreme high god present"]),
    "Supernatural monitoring": (
        ["economic fairness", "conversion non-religionists", "non-lethal fighting", "gossiping"],
        ["supernatural monitoring present"]),
}
# all groups and texts; groups without the Abrahamic traditions
versions = [
    (pooled_all, "group", "Religious groups", "group"),
    (pooled_all, "text", "Religious texts", "text"),
    (pooled_non_abrahamic, "group", "Religious groups without Christian, Jewish and Islamic entries", "group_non_abrahamic"),
]
for pooled, poll, label, name in versions:
    fig, axes = plt.subplots(2, 2, figsize=(17, 9.5), dpi=300, sharey=True)
    for ax, (title, (qs, references)) in zip(axes.flat, themes.items()):
        draw_panel(ax, pooled, poll, qs, references, title=title, label_size=10)
    for ax in axes[:, 0]:
        ax.set_ylabel("Fraction yes", size=11, color=color_text)
    fig.supxlabel(f"Year ({bin_width}-year rolling window)", size=12, color=color_text)
    fig.suptitle(f"{label} in states and empires (grey: parent questions; fewer than {min_n} entries not shown)",
                 size=14, x=0.01, ha="left")
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.55)
    plt.savefig(f"{fig_dir}/summary_themes_{name}_{bin_width}.jpg", bbox_inches="tight")
    plt.close()

# entries per window (any answer), all groups vs. without the Abrahamic traditions
n_entries = smooth_time_end(summary_answers[summary_answers["poll"] == "group"].drop_duplicates("entry_id"), bin_width, step_size)
n_entries["abrahamic"] = n_entries["entry_id"].isin(abrahamic)
print(n_entries.groupby(["time_bin", "abrahamic"])["entry_id"].nunique().unstack(fill_value=0).iloc[::10])

# within macro-regions (all traditions)
region_data = pd.read_csv("../data/sccsrv3/region_data.csv")[["region_id", "world_region"]].drop_duplicates()
regions = entry_tags[["entry_id", "region_id"]].merge(region_data, on="region_id", how="left")
macro_regions = {
    "Europe": "Europe and Southwest Asia", "Southwest Asia": "Europe and Southwest Asia",
    "East Asia": "East and Southeast Asia", "Southeast Asia": "East and Southeast Asia",
    "South Asia": "South Asia", "Africa": "Africa",
}
macro_region = regions.set_index("entry_id")["world_region"].map(macro_regions)

group_answers = summary_answers[summary_answers["poll"] == "group"]
for region in ["Europe and Southwest Asia", "East and Southeast Asia", "South Asia", "Africa"]:
    pooled = pool(group_answers[group_answers["entry_id"].map(macro_region) == region])
    fig, axes = plt.subplots(2, 2, figsize=(17, 9.5), dpi=300, sharey=True)
    for ax, (title, (qs, references)) in zip(axes.flat, themes.items()):
        draw_panel(ax, pooled, "group", qs, references, title=title, label_size=10)
    for ax in axes[:, 0]:
        ax.set_ylabel("Fraction yes", size=11, color=color_text)
    fig.supxlabel(f"Year ({bin_width}-year rolling window)", size=12, color=color_text)
    fig.suptitle(f"Religious groups in states and empires, {region} (grey: parent questions; fewer than {min_n} entries not shown)",
                 size=14, x=0.01, ha="left")
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.55)
    name = region.lower().replace(" and ", "_").replace(" ", "_")
    plt.savefig(f"{fig_dir}/summary_themes_group_region_{name}_{bin_width}.jpg", bbox_inches="tight")
    plt.close()

entries_region = group_answers.drop_duplicates("entry_id").assign(macro_region=lambda d: d["entry_id"].map(macro_region))
print(entries_region["macro_region"].value_counts(dropna=False))
