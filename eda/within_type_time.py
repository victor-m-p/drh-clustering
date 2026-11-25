"""
Change over time within society type (state, empire; bands, tribes and chiefdoms are mostly after 1500).
Share "Yes" per question, one line per society type; groups (v5 + v6) and texts separately.
Rolling window of bin_width years, moved in steps of step_size (as in temporal/); an entry counts in every
window its time span overlaps; windows with fewer than min_n entries in light grey.

Questions (one figure each):
- politics: parent questions, supernatural punishment and reward, the religion and politics questions of
  preprocessing/curate_covariates.py (answers_covariates.csv), the supreme high god elite questions
- shg, monitoring: all child questions, order as in temporal/plot_all_questions_time.py
- punishment, reward: present, when (this life, afterlife), who and why (answers_covariates.csv)
Conflicting answers (an entry answers a question both "Yes" and "No", weight < 1 in the preprocessed files;
about 0.2% of entry x question answers) are left out.

Inferred vs. as answered (column inferred in the preprocessed files):
- the grids use the answers as given (inferred = False): child questions are conditional (only answered when
  their parent is "Yes"); unanswered is left out, never "No"
- the summary figures show both (see below)
- inferred "No" (preprocessing): supreme high god present when supernatural beings are absent; the supreme high god
  and monitoring child questions when their parent is "No" (curate_answers.py); head of polity is head of religion
  (2339) and political officials are religious officials (2319) when official political support (2300) is "No";
  punishment (reward) when, who and why when supernatural punishment (reward) is "No" (curate_covariates.py)
Text polls ask other things for 2300, 2339 and 2319 (funding and support of the text's production).

Figures: fig/within_type_time/{questions}_{poll}_{bin_width}.jpg, summary_{variant}_{bin_width}.jpg

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
    "punishment": [
        "supernatural punishment", "punishment this life", "punishment afterlife",
        "punishment by high god only", "punishment by many beings", "punishment impersonal",
        "punishment for group norms", "punishment for ritual", "punishment for selfishness", "punishment random",
    ],
    "reward": [
        "supernatural reward", "reward this life", "reward afterlife",
        "reward by high god only", "reward by many beings", "reward impersonal",
        "reward for group norms", "reward for ritual", "reward for selfishness", "reward random",
    ],
}
titles = {
    "politics": "Religion and politics", "monitoring": "Supernatural Monitoring", "shg": "Supreme High God",
    "punishment": "Supernatural Punishment", "reward": "Supernatural Reward",
}

"""
Answers: one row per answer (entry_id, poll_name, question_short, answer_value, weight, inferred),
all society types; answers (states and empires, as answered) for the grids.
"""

cols = ["entry_id", "poll_name", "question_short", "answer_value", "weight", "inferred"]
parents = pd.read_csv("../data/preprocessed/answers_parents_all.csv")
children = pd.read_csv("../data/preprocessed/answers_subset_all_unconditional.csv").dropna(subset=["answer_value"])
covariate_answers = pd.read_csv("../data/preprocessed/answers_covariates.csv")

answers_all = pd.concat([parents[cols], children[cols], covariate_answers[cols]], ignore_index=True)
answers_all = answers_all[answers_all["weight"] == 1]  # conflicting answers left out
answers_all["poll"] = np.where(answers_all["poll_name"].str.contains("Group"), "group", "text")
assert set(q for qs in questions.values() for q in qs) <= set(answers_all["question_short"])

# society type (missing when not codable or unanswered) and time span
covariates = pd.read_csv("../data/preprocessed/entry_covariates.csv")[["entry_id", "social_complexity"]]
entry_metadata = pd.read_csv("../data/sccsrv3/entry_data.csv")[["entry_id", "year_from", "year_to"]]
answers_all = answers_all.merge(covariates, on="entry_id", how="left").merge(entry_metadata, on="entry_id")
answers_all[["year_from", "year_to"]] = answers_all[["year_from", "year_to"]].astype(int)
answers = answers_all[answers_all["social_complexity"].isin(types) & ~answers_all["inferred"]]

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
    fig.suptitle(f"{titles[name]}: {poll_labels[poll].lower()} (as answered; fewer than {min_n} entries in light grey)",
                 size=16, x=0.01, ha="left")
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/{name}_{poll}_{bin_width}.jpg", bbox_inches="tight")
    plt.close()


for poll in poll_labels:
    for name in questions:
        plot_grid(poll, name)

"""
Summary figures: key questions in six panels by theme, one figure per variant; all society types in a
variant are pooled. Parent questions as grey reference lines; windows with fewer than min_n entries not shown;
dotted vertical line at year 0.

Baseline (summary_eswa): religious groups in states and empires in Europe and Southwest Asia (the only macro-region
covered across the whole period), answers as given. Each variant changes the baseline as follows:
- eswa_unconditional: inferred "No" included (see the top of this file)
- eswa_non_abrahamic: without Christian, Jewish and Islamic entries (tradition tags from
  modeling/1_code_entrytags.py; an entry is left out if it has any of the three)
- states_empires: all regions
- eswa_all_types: all society types, including entries without a codable society type
- all: all regions and all society types
- eswa_texts: religious texts instead of groups (literacy left out: all texts are literate)
- all_non_abrahamic, all_texts: as eswa_non_abrahamic and eswa_texts, but all regions and all society types
  (in Europe and Southwest Asia almost all state and empire groups after 500 CE are Abrahamic, and texts are few)
Regions: world_region of the entry's region (as in modeling/3_prepare_data.py); Europe and Southwest Asia merged.

Two extra variables, derived after the selection:
- literacy: entry level, groups only (entry_covariates.csv; unanswered left out)
- any elite / monarch tie: "Yes" if any of the four supreme high god elite questions is "Yes",
  "No" if at least one is answered and none is "Yes"
Punishment and reward: this life / afterlife are conditional on punishment (reward) present; who and why
in addition on the cause or agent / reason (reward: cause/purpose) being known.
"""

series_colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]  # categorical, fixed order
reference_styles = {
    "supernatural monitoring present": (0, (4, 2)), "supreme high god present": (0, (1, 1.5)),
    "supernatural punishment": (0, (1, 1.5)), "supernatural reward": (0, (1, 1.5)),
}
elite_questions = ["is monarch fused", "is monarch manifestation", "is kin to elites", "other elite loyalty"]
meta_cols = ["entry_id", "poll_name", "poll", "social_complexity", "year_from", "year_to"]

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
    "Supernatural punishment": (
        ["punishment afterlife", "punishment by high god only", "punishment impersonal", "punishment for selfishness"],
        ["supernatural punishment"]),
    "Supernatural reward": (
        ["reward afterlife", "reward by high god only", "reward impersonal", "reward for selfishness"],
        ["supernatural reward"]),
}

# Abrahamic traditions (Christian, Jewish, Islamic; modeling/1_code_entrytags.py)
entry_tags = pd.read_csv("../modeling/data/entry_tags.csv")
abrahamic = set(entry_tags.loc[entry_tags[["christian", "jewish", "islamic"]].any(axis=1), "entry_id"])

# Europe and Southwest Asia (one world region per entry)
region_data = pd.read_csv("../data/sccsrv3/region_data.csv")[["region_id", "world_region"]].drop_duplicates()
regions = entry_tags[["entry_id", "region_id"]].merge(region_data, on="region_id", how="left")
assert not regions["entry_id"].duplicated().any()
eswa = set(regions.loc[regions["world_region"].isin(["Europe", "Southwest Asia"]), "entry_id"])

baseline = dict(poll="group", types="states_empires", region="eswa", inference="answered", traditions="all")
variants = {
    "eswa": {},
    "eswa_unconditional": dict(inference="unconditional"),
    "eswa_non_abrahamic": dict(traditions="non_abrahamic"),
    "states_empires": dict(region="all"),
    "eswa_all_types": dict(types="all"),
    "all": dict(region="all", types="all"),
    "eswa_texts": dict(poll="text"),
    "all_non_abrahamic": dict(region="all", types="all", traditions="non_abrahamic"),
    "all_texts": dict(region="all", types="all", poll="text"),
}


def select(poll, types, region, inference, traditions):
    """Answers for one variant, with the two derived variables."""
    d = answers_all[answers_all["poll"] == poll]
    if inference == "answered":
        d = d[~d["inferred"]]
    if types == "states_empires":
        d = d[d["social_complexity"].isin(["state", "empire"])]
    if region == "eswa":
        d = d[d["entry_id"].isin(eswa)]
    if traditions == "non_abrahamic":
        d = d[~d["entry_id"].isin(abrahamic)]

    elite = d[d["question_short"].isin(elite_questions)].groupby(meta_cols, dropna=False)["answer_value"].max().reset_index()
    elite = elite.assign(question_short="any elite / monarch tie", weight=1.0)
    derived = [elite]
    if poll == "group":
        literacy = d[meta_cols].drop_duplicates().merge(
            pd.read_csv("../data/preprocessed/entry_covariates.csv")[["entry_id", "literacy"]], on="entry_id"
        )
        literacy = literacy.rename(columns={"literacy": "answer_value"}).dropna(subset=["answer_value"])
        derived.append(literacy.assign(question_short="literacy", weight=1.0))
    return pd.concat([d] + derived, ignore_index=True)


def describe(poll, types, region, inference, traditions):
    """Figure title for one variant."""
    who = poll_labels[poll] + (" in states and empires" if types == "states_empires" else " (all society types)")
    where = ", Europe and Southwest Asia" if region == "eswa" else ", all regions"
    parts = [
        "without Christian, Jewish and Islamic entries" if traditions == "non_abrahamic" else None,
        "inferred \"No\" included" if inference == "unconditional" else "as answered",
        f"grey: parent questions; fewer than {min_n} entries not shown",
    ]
    return f"{who}{where} ({'; '.join(p for p in parts if p)})"


def pool(d):
    """Weighted share "Yes" per question and time window (all society types in d pooled)."""
    pooled = smooth_time_end(d, bin_width, step_size)
    pooled = (
        pooled.assign(yes=pooled["answer_value"] * pooled["weight"])
        .groupby(["question_short", "time_bin"])
        .agg(n=("weight", "sum"), yes=("yes", "sum"))
        .reset_index()
    )
    pooled["p"] = (pooled["yes"] / pooled["n"]).where(pooled["n"] >= min_n)
    return pooled[pooled["time_bin"] >= x_min - step_size]


def draw_panel(ax, pooled, qs, references, x_end, title=None, label_size=9.5):
    """Lines for qs (categorical colors) and references (grey), labelled at their ends."""
    ends = []
    has_data = lambda q: pooled.loc[pooled["question_short"] == q, "p"].notna().any()
    # labels without the theme prefix (the panel title says punishment or reward)
    label = lambda q: q.removeprefix("punishment ").removeprefix("reward ")
    ax.axvline(0, color=color_sparse, lw=1, ls=":", zorder=0)
    for q in [q for q in references if has_data(q)]:
        pq = pooled[pooled["question_short"] == q].sort_values("time_bin")
        ax.plot(pq["time_bin"], pq["p"], color="#898781", lw=1.6, ls=reference_styles[q], zorder=1)
        last = pq.dropna(subset=["p"]).iloc[-1]
        ends.append((last["p"], last["time_bin"], q, "#898781"))
    for q, color in zip([q for q in qs if has_data(q)], series_colors):
        pq = pooled[pooled["question_short"] == q].sort_values("time_bin")
        ax.plot(pq["time_bin"], pq["p"], color=color, lw=2.2, zorder=2)
        last = pq.dropna(subset=["p"]).iloc[-1]
        ax.plot(last["time_bin"], last["p"], "o", ms=5, color=color, mec="white", mew=1, zorder=3)
        ends.append((last["p"], last["time_bin"], label(q), color))

    # direct labels at the line ends, spread so they do not overlap
    if ends:
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


for name, changes in variants.items():
    options = baseline | changes
    d = select(**options)
    pooled = pool(d)
    x_end = pooled.loc[pooled["p"].notna(), "time_bin"].max()
    fig, axes = plt.subplots(3, 2, figsize=(17, 14), dpi=300, sharey=True)
    for ax, (title, (qs, references)) in zip(axes.flat, themes.items()):
        draw_panel(ax, pooled, qs, references, x_end, title=title, label_size=10)
    for ax in axes[:, 0]:
        ax.set_ylabel("Fraction yes", size=11, color=color_text)
    fig.supxlabel(f"Year ({bin_width}-year rolling window)", size=12, color=color_text)
    fig.suptitle(describe(**options), size=14, x=0.01, ha="left")
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.55)
    plt.savefig(f"{fig_dir}/summary_{name}_{bin_width}.jpg", bbox_inches="tight")
    plt.close()
    print(f"{name}: {d['entry_id'].nunique()} entries")
