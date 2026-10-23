"""
Correlations between the 36 child questions (items), to check whether a proposed grouping into packages holds up.
Groups only, conditional answers (items are only answered when the parent question is "Yes"; monitoring
and supreme high god items are therefore correlated over entries where both parents are "Yes").
Tetrachoric correlations (latent normal variables behind the 0/1 answers; unlike the phi coefficient, not
limited by differences in how often items are "yes"), pairwise over entries that answered both items.
Conflicting answers (weight < 1) are left out for that item.
"Permissible to worship other god?" is reversed (yes = not permissible), so all items in a package point the same way.
Figures:
- correlations ordered by hierarchical clustering (labels coloured by family: monitoring / supreme high god)
- correlations ordered by the proposed (partly data-driven, partly theoretical) packages (boxes)
Run from inside eda/ after modeling/3_prepare_data.py.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm, multivariate_normal
from scipy.optimize import brentq
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

# setup
min_n = 30  # pairs answered by fewer entries are left empty
fig_dir = "fig/item_correlations"
data_dir = "data"
os.makedirs(fig_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# proposed packages (in plotting order); "potentially" members at the end of their package
packages = {
    "moral monitoring": [
        "murder coreligionists", "murder other religions", "murder other polities", "non-lethal fighting",
        "prosocial norm adherence", "lying", "honouring oaths", "property crimes", "economic fairness",
        "gossiping", "laziness", "shirking risk", "disrespecting elders", "sex", "sorcery", "personal hygiene",
    ],
    "ritual monitoring": ["ritual observance", "performance of rituals", "taboos"],
    "moralizing / universalizing": ["conversion non-religionists", "is unquestionably good", "worship other god not permissible (reversed)"],
    "agency and mind": [
        "knowledge this world", "causal efficacy the world", "communicates with living",
        "positive emotion", "negative emotion", "possesses hunger",
        "is anthropomorphic", "indirect causal efficacy the world",
    ],
    "political": ["is monarch fused", "is monarch manifestation", "is kin to elites", "other elite loyalty"],
    "cosmological": ["is sky deity", "is chthonic"],
}
package_colors = {
    "moral monitoring": "#2a78d6", "ritual monitoring": "#1baf7a", "moralizing / universalizing": "#8e5bc4",
    "agency and mind": "#eb6834", "political": "#a0522d", "cosmological": "#5f5e5a",
}
family_colors = {"monitoring": "#2a78d6", "supreme high god": "#eb6834"}
items = [q for qs in packages.values() for q in qs]
package_of = {q: p for p, qs in packages.items() for q in qs}

# answers: one row per entry, one column per item (groups, conditional, conflicting answers left out)
d = pd.read_csv("../modeling/data/model_data.csv")
d = d[(d["poll"] == "group") & (d["family"] != "parent") & (~d["inferred"]) & (d["weight"] == 1)].copy()
reversed_item = d["question_short"] == "permissible to worship other god?"
d.loc[reversed_item, "answer_value"] = 1 - d.loc[reversed_item, "answer_value"]
d.loc[reversed_item, "question_short"] = "worship other god not permissible (reversed)"
family_of = d.drop_duplicates("question_short").set_index("question_short")["family"].map({"monitoring": "monitoring", "shg": "supreme high god"}).to_dict()
wide = d.pivot_table(index="entry_id", columns="question_short", values="answer_value")[items]
print(f"entries: {len(wide)}")


def tetrachoric(x, y):
    """tetrachoric correlation of two 0/1 vectors (0.5 added to empty cells)"""
    table = np.array([[np.sum((x == i) & (y == j)) for j in (0, 1)] for i in (0, 1)], dtype=float)
    table[table == 0] = 0.5
    p = table / table.sum()
    h, k = norm.ppf(p[0].sum()), norm.ppf(p[:, 0].sum())  # thresholds: P(X <= h) = P(x = 0)

    # P(x = 0, y = 0) under a bivariate normal with correlation r
    def diff(r):
        return multivariate_normal.cdf([h, k], mean=[0, 0], cov=[[1, r], [r, 1]]) - p[0, 0]

    lo, hi = -0.999, 0.999
    if diff(lo) * diff(hi) > 0:  # outside the range: the closer bound
        return lo if abs(diff(lo)) < abs(diff(hi)) else hi
    return brentq(diff, lo, hi)


# pairwise correlations and number of entries
r = pd.DataFrame(np.eye(len(items)), index=items, columns=items)
n = pd.DataFrame(0, index=items, columns=items)
for i, a in enumerate(items):
    for b in items[i:]:
        both = wide[[a, b]].dropna()
        n.loc[a, b] = n.loc[b, a] = len(both)
        if a != b:
            r.loc[a, b] = r.loc[b, a] = tetrachoric(both[a].values, both[b].values) if len(both) >= min_n else np.nan
r.to_csv(f"{data_dir}/item_correlations.csv")
n.to_csv(f"{data_dir}/item_correlations_n.csv")
upper = np.triu_indices(len(items), 1)
print(f"entries per pair: min {n.values[upper].min()}, median {int(np.median(n.values[upper]))}")

# mean correlation within each package and with all other items
summary = []
for p, qs in packages.items():
    others = [q for q in items if q not in qs]
    within = r.loc[qs, qs].values[np.triu_indices(len(qs), 1)]
    summary.append({
        "package": p, "items": len(qs),
        "mean r within": round(np.nanmean(within), 2),
        "mean r with other items": round(np.nanmean(r.loc[qs, others].values), 2),
    })
summary = pd.DataFrame(summary)
summary.to_csv(f"{data_dir}/item_correlations_packages.csv", index=False)
print(summary.to_string(index=False))


def heatmap(r, order, title, path, label_of, label_colors, legend_title, boxes=False):
    m = r.loc[order, order]
    fig, ax = plt.subplots(figsize=(15, 13), dpi=300)
    im = ax.imshow(m.values, cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(len(order)):
        for j in range(len(order)):
            if i != j and not np.isnan(m.values[i, j]):
                ax.text(j, i, f"{m.values[i, j]:.1f}", ha="center", va="center", fontsize=5.5,
                        color="white" if abs(m.values[i, j]) > 0.6 else "#0b0b0b")
    ax.set_xticks(range(len(order)))
    ax.set_yticks(range(len(order)))
    ax.set_xticklabels(order, rotation=90, fontsize=8)
    ax.set_yticklabels(order, fontsize=8)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(label_colors[label_of[label.get_text()]])
    if boxes:  # outline the proposed packages
        start = 0
        for qs in packages.values():
            ax.add_patch(plt.Rectangle((start - 0.5, start - 0.5), len(qs), len(qs), fill=False, lw=1.6, edgecolor="#0b0b0b"))
            start += len(qs)
    handles = [plt.Line2D([], [], color=c, lw=6, label=l) for l, c in label_colors.items()]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.12, 1), frameon=False, fontsize=9, title=legend_title)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="tetrachoric correlation")
    ax.set_title(title, loc="left", fontsize=13)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


# ordered by hierarchical clustering (average linkage on 1 - r; missing pairs treated as r = 0)
dist = 1 - r.fillna(0).values
np.fill_diagonal(dist, 0)
order = [items[i] for i in leaves_list(linkage(squareform(dist, checks=False), method="average"))]
heatmap(r, order, "Item correlations, ordered by hierarchical clustering (groups, conditional)",
        f"{fig_dir}/item_correlations_clustered.jpg", family_of, family_colors, "family")

# ordered by the proposed packages
heatmap(r, items, "Item correlations, ordered by proposed packages (groups, conditional)",
        f"{fig_dir}/item_correlations_packages.jpg", package_of, package_colors, "proposed package", boxes=True)
