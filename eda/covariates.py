"""
Exploratory plots of answers by society type (social_complexity from preprocessing/curate_covariates.py):
share "Yes" for band, tribe, chiefdom, state, empire; groups (v5 + v6) and texts separately.
Entries without a society type are left out.

Parent questions: supernatural monitoring present (2890), supreme high god present (2919).
Supreme high god present includes the inferred "No" when supernatural beings are absent (2893 "No").
Child questions: conditional answers (only answered when the parent is "Yes").
Entries with conflicting answers count with weight 1/n per answer, so each entry counts once.
Error bars: 95% Wilson intervals (n = number of entries).
Levels with fewer than min_n entries are not plotted (overlays) or drawn in light grey (all questions).

Figures (fig/covariates/):
- parents_social_complexity.jpg: both parent questions
- shg_social_complexity.jpg, monitoring_social_complexity.jpg: selected questions (as in temporal/plot_question_time.py)
- shg_social_complexity_all.jpg, monitoring_social_complexity_all.jpg: all questions, one panel each
  (order as in temporal/plot_all_questions_time.py)

Run from inside eda/ after preprocessing/curate_answers.py and preprocessing/curate_covariates.py.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# setup
min_n = 10
fig_dir = "fig/covariates"
os.makedirs(fig_dir, exist_ok=True)
levels = ["band", "tribe", "chiefdom", "state", "empire"]
poll_labels = {"group": "Religious groups", "text": "Religious texts"}
series_colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]  # categorical, fixed order
color_grid = "#e1e0d9"
color_sparse = "#c3c2b7"
color_text = "#52514e"

# selected questions (as in temporal/plot_question_time.py, without indirect causal efficacy and taboos)
selected = {
    "shg": ["is anthropomorphic", "is sky deity", "is unquestionably good", "permissible to worship other god?", "possesses hunger"],
    "monitoring": [
        "conversion non-religionists", "economic fairness", "murder other polities",
        "performance of rituals", "shirking risk", "prosocial norm adherence",
    ],
}
# all questions in topic order (as in temporal/plot_all_questions_time.py)
all_questions = {
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

# answers with society type (one row per answer)
covariates = pd.read_csv("../data/preprocessed/entry_covariates.csv")[["entry_id", "social_complexity"]].dropna()
parents = pd.read_csv("../data/preprocessed/answers_parents_all.csv")
parents = parents[parents["question_short"].isin(["supernatural monitoring present", "supreme high god present"])]
children = pd.read_csv("../data/preprocessed/answers_subset_all.csv").dropna(subset=["answer_value"])
answers = pd.concat([parents, children], ignore_index=True)
answers["poll"] = np.where(answers["poll_name"].str.contains("Group"), "group", "text")
answers = answers.merge(covariates, on="entry_id", how="inner")
assert set(q for qs in all_questions.values() for q in qs) <= set(answers["question_short"])

# weighted share "Yes" per poll, question and society type, with 95% Wilson interval
s = (
    answers.assign(yes=answers["answer_value"] * answers["weight"])
    .groupby(["poll", "question_short", "social_complexity"])
    .agg(n=("weight", "sum"), yes=("yes", "sum"))
    .reset_index()
)
s["p"] = s["yes"] / s["n"]
z = norm.ppf(0.975)
centre = (s["p"] + z**2 / (2 * s["n"])) / (1 + z**2 / s["n"])
half = z * np.sqrt(s["p"] * (1 - s["p"]) / s["n"] + z**2 / (4 * s["n"] ** 2)) / (1 + z**2 / s["n"])
s["lower"], s["upper"] = np.minimum(centre - half, s["p"]), np.maximum(centre + half, s["p"])  # rounding at p = 0, 1
s.to_csv("data/share_yes_social_complexity.csv", index=False)


def style(ax):
    ax.grid(axis="y", color=color_grid, lw=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(color_sparse)
    ax.tick_params(length=0, labelsize=8, colors=color_text)


def get(poll, question):
    return s[(s["poll"] == poll) & (s["question_short"] == question)].set_index("social_complexity").reindex(levels)


def plot_overlay(questions, path, legend_title):
    """Share "Yes" for several questions in one panel per poll (dodged, with error bars)."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), dpi=300, sharey=True)
    x = np.arange(len(levels))
    offsets = (np.arange(len(questions)) - (len(questions) - 1) / 2) * 0.07
    for ax, poll in zip(axes, poll_labels):
        n = []
        for q, color, offset in zip(questions, series_colors, offsets):
            sq = get(poll, q)
            n.append(sq["n"].fillna(0))
            sq.loc[sq["n"] < min_n, ["p", "lower", "upper"]] = np.nan  # line breaks there
            ax.plot(x + offset, 100 * sq["p"], color=color, lw=2, zorder=2)
            ax.errorbar(
                x + offset, 100 * sq["p"], yerr=100 * np.vstack([sq["p"] - sq["lower"], sq["upper"] - sq["p"]]),
                fmt="o", ms=5, color=color, mec="white", mew=0.8, elinewidth=1, capsize=0, zorder=3, label=q,
            )
        n = pd.concat(n, axis=1)
        ticks = [f"{lev}\nn = {lo:.0f}" if lo == hi else f"{lev}\nn = {lo:.0f}–{hi:.0f}"
                 for lev, lo, hi in zip(levels, n.min(axis=1), n.max(axis=1))]
        ax.set_xticks(x, ticks)
        ax.set_title(poll_labels[poll], fontsize=11, loc="left")
        ax.set_ylim(0, 105)
        style(ax)
    axes[0].set_ylabel('% "Yes"', fontsize=9, color=color_text)
    axes[1].legend(frameon=False, fontsize=8, title=legend_title, title_fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1))
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def plot_all(questions, title, path):
    """One panel per question, groups and texts as two lines; levels with fewer than min_n entries in light grey."""
    ncol = 4
    nrow = int(np.ceil(len(questions) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.5 * ncol, 2.4 * nrow), dpi=300, sharex=True, sharey=True)
    x = np.arange(len(levels))
    for ax, q in zip(axes.flat, questions):
        for poll, color in zip(poll_labels, series_colors):
            sq = get(poll, q)
            ax.plot(x, sq["p"], color=color_sparse, lw=1.4, zorder=1)
            ok = sq["n"] >= min_n
            ax.plot(x, sq["p"].where(ok), color=color, lw=2, marker="o", ms=4, mec="white", mew=0.6, zorder=2,
                    label=poll_labels[poll])
        ax.set_title(q, size=12, loc="left")
        ax.set_ylim(0, 1.02)
        ax.set_yticks([0, 0.5, 1])
        ax.set_xticks(x, levels, rotation=45, ha="right")
        style(ax)
        ax.tick_params(labelsize=10)
    for ax in axes.flat[len(questions):]:
        ax.set_visible(False)
    axes.flat[0].legend(frameon=False, fontsize=9, loc="lower left")
    fig.supylabel("Fraction yes", size=14, color=color_text)
    fig.suptitle(f"{title} (light grey: fewer than {min_n} entries)", size=18, x=0.01, ha="left")
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


plot_overlay(["supernatural monitoring present", "supreme high god present"],
             f"{fig_dir}/parents_social_complexity.jpg", "present")
for family in ["shg", "monitoring"]:
    plot_overlay(selected[family], f"{fig_dir}/{family}_social_complexity.jpg", titles[family])
    plot_all(all_questions[family], titles[family], f"{fig_dir}/{family}_social_complexity_all.jpg")

print(s[s["question_short"].str.contains("present")].pivot(
    index=["poll", "social_complexity"], columns="question_short", values=["p", "n"]).reindex(levels, level=1).round(2))
