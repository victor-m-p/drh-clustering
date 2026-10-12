"""
How the cultural packages split as the number of clusters (c) goes up.
One column per c; each package is a bar with height proportional to its share
of entries; bands between columns show the (q-weighted) number of entries
moving from a package at c to a package at c + 1.
Packages are labelled {c}A, {c}B, ... by median start year (oldest first),
the same labels as plot_dimensions.py, and shaded by P(Yes) for color_question.
Also writes a table of all packages (share, median year, distinguishing questions)
and of all flows.
Run from inside clustering/ after run_clustering.py.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap

# setup
c_tree = [2, 3, 4, 5, 6]
subset = "group"
color_question = "conversion non-religionists"  # packages shaded by P(Yes) for this question
min_flow = 2  # do not draw bands carrying fewer entries than this
n_describe = 3  # distinguishing questions listed per package (in the table)
fig_dir = "fig/tree"
table_dir = "tables"
os.makedirs(fig_dir, exist_ok=True)
os.makedirs(table_dir, exist_ok=True)

# sequential palette (one hue, light -> dark) and chrome
cmap = LinearSegmentedColormap.from_list("seq_blue", ["#cde2fb", "#86b6ef", "#2a78d6", "#1c5cab", "#0d366b"])
color_ink = "#0b0b0b"
color_secondary = "#52514e"


def format_year(year):
    return f"{-int(year)} BCE" if year < 0 else f"{int(year)} CE"


def load(c):
    """Best solution at c: theta, one q row per entry, cluster order and labels."""
    dims = [f"dim{i}" for i in range(c)]
    df_theta = pd.read_csv(f"data/EM_theta_{subset}_c{c}.csv")
    theta = df_theta[df_theta["question_id"] != -1].set_index("question_short")

    # one row per entry: weighted sum of q over expanded rows (weights sum to 1 per entry)
    df_q = pd.read_csv(f"data/EM_q_{subset}_c{c}.csv")
    df_q[dims] = df_q[dims].multiply(df_q["weight"], axis=0)
    df_entry = df_q.groupby(["entry_id", "year_from"], as_index=False)[dims].sum()
    df_entry = df_entry.sort_values("entry_id").reset_index(drop=True)

    # order clusters by median start year of the entries assigned to them
    df_entry["top"] = df_entry[dims].idxmax(axis=1)
    median_year = df_entry.groupby("top")["year_from"].median().reindex(dims)
    order = median_year.sort_values(na_position="last").index.tolist()
    labels = {d: f"{c}{chr(65 + i)}" for i, d in enumerate(order)}
    return {"c": c, "dims": dims, "theta": theta, "entry": df_entry, "order": order, "labels": labels, "median_year": median_year}


levels = [load(c) for c in c_tree]
for level in levels[1:]:
    assert level["entry"]["entry_id"].equals(levels[0]["entry"]["entry_id"]), "entries differ across c"
n_entries = len(levels[0]["entry"])

### table of packages ###
rows = []
for level in levels:
    theta = level["theta"]
    for d in level["order"]:
        deviation = (theta[d] - theta["question_mean"]).sort_values()
        more = deviation.index[::-1][:n_describe]
        less = deviation.index[:n_describe]
        rows.append(
            {
                "c": level["c"],
                "package": level["labels"][d],
                "dim": d,
                "n_entries": level["entry"][d].sum(),
                "share": level["entry"][d].sum() / n_entries,
                "median_year": level["median_year"][d],
                color_question: theta.loc[color_question, d],
                "more_than_average": "; ".join(f"{q} ({theta.loc[q, d]:.2f})" for q in more),
                "less_than_average": "; ".join(f"{q} ({theta.loc[q, d]:.2f})" for q in less),
            }
        )
df_packages = pd.DataFrame(rows)
df_packages.to_csv(f"{table_dir}/cluster_tree_packages_{subset}.csv", index=False)

### flows between consecutive c (expected number of entries) ###
flows = []
for prev, nxt in zip(levels[:-1], levels[1:]):
    F = prev["entry"][prev["dims"]].values.T @ nxt["entry"][nxt["dims"]].values  # prev x next
    for i, d_prev in enumerate(prev["dims"]):
        for j, d_next in enumerate(nxt["dims"]):
            flows.append(
                {
                    "c_from": prev["c"],
                    "from": prev["labels"][d_prev],
                    "c_to": nxt["c"],
                    "to": nxt["labels"][d_next],
                    "n_entries": F[i, j],
                }
            )
df_flows = pd.DataFrame(flows)
df_flows.to_csv(f"{table_dir}/cluster_tree_flows_{subset}.csv", index=False)

### figure ###
pad = 0.025  # vertical gap between packages
node_width = 0.12
x_step = 1.0
scale = (1 - pad * (max(c_tree) - 1)) / n_entries  # height per entry, same in all columns

# node positions: oldest package at the top, each column centered vertically
nodes = {}
for k, level in enumerate(levels):
    heights = [level["entry"][d].sum() * scale for d in level["order"]]
    total = sum(heights) + pad * (len(heights) - 1)
    y_top = 0.5 + total / 2
    for d, h in zip(level["order"], heights):
        label = level["labels"][d]
        value = level["theta"].loc[color_question, d]
        nodes[label] = {"x": k * x_step, "top": y_top, "height": h, "value": value, "order": level["order"].index(d)}
        y_top -= h + pad

fig, ax = plt.subplots(figsize=(2.3 * len(c_tree) + 1.5, 8), dpi=300)


def band(ax, x0, y0_top, y0_bot, x1, y1_top, y1_bot, color):
    xm = (x0 + x1) / 2
    verts = [
        (x0, y0_top), (xm, y0_top), (xm, y1_top), (x1, y1_top),
        (x1, y1_bot), (xm, y1_bot), (xm, y0_bot), (x0, y0_bot),
        (x0, y0_top),
    ]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", alpha=0.35, zorder=1))


# bands: outgoing flows stacked by target order, incoming flows stacked by source order
for c_from in c_tree[:-1]:
    f = df_flows[df_flows["c_from"] == c_from].copy()
    f["from_order"] = f["from"].map(lambda l: nodes[l]["order"])
    f["to_order"] = f["to"].map(lambda l: nodes[l]["order"])
    out_cursor = {l: nodes[l]["top"] for l in f["from"].unique()}
    in_cursor = {l: nodes[l]["top"] for l in f["to"].unique()}
    in_pos = {}
    for _, r in f.sort_values(["to_order", "from_order"]).iterrows():
        h = r["n_entries"] * scale
        in_pos[(r["from"], r["to"])] = (in_cursor[r["to"]], in_cursor[r["to"]] - h)
        in_cursor[r["to"]] -= h
    for _, r in f.sort_values(["from_order", "to_order"]).iterrows():
        h = r["n_entries"] * scale
        y0_top, y0_bot = out_cursor[r["from"]], out_cursor[r["from"]] - h
        out_cursor[r["from"]] -= h
        if r["n_entries"] < min_flow:
            continue
        src, dst = nodes[r["from"]], nodes[r["to"]]
        y1_top, y1_bot = in_pos[(r["from"], r["to"])]
        band(ax, src["x"] + node_width, y0_top, y0_bot, dst["x"], y1_top, y1_bot, cmap(src["value"]))

# nodes and labels
for label, node in nodes.items():
    ax.add_patch(
        Rectangle((node["x"], node["top"] - node["height"]), node_width, node["height"], facecolor=cmap(node["value"]), edgecolor="white", linewidth=1, zorder=2)
    )
    share = node["height"] / scale / n_entries
    ax.text(
        node["x"] + node_width + 0.03, node["top"] - node["height"] / 2, f"{label}\n{share:.0%}",
        va="center", ha="left", size=10, color=color_ink, zorder=3,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1},
    )

# column headers
for k, c in enumerate(c_tree):
    ax.text(k * x_step + node_width / 2, 1.04, f"c = {c}", ha="center", va="bottom", size=13, color=color_ink)

ax.set_xlim(-0.1, (len(c_tree) - 1) * x_step + node_width + 0.45)
ax.set_ylim(-0.02, 1.1)
ax.axis("off")

# colorbar for the shading question
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
cbar = fig.colorbar(sm, ax=ax, fraction=0.025, pad=0.01)
cbar.set_label(f"P(Yes): {color_question}", size=11, color=color_secondary)
cbar.ax.tick_params(labelsize=9, colors=color_secondary)
cbar.outline.set_visible(False)

fig.suptitle("Cultural packages as the number of clusters increases", size=15, x=0.02, ha="left")
plt.tight_layout()
plt.savefig(
    f"{fig_dir}/EM_tree_{subset}_{color_question.replace(' ', '_').replace('?', '')}.jpg",
    dpi=300,
    bbox_inches="tight",
)
plt.close()
