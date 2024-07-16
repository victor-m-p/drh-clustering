import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

df_edges = pd.read_csv("data/overlap_christianity.csv")
df_nodes = pd.read_csv("data/entry_data_subset.csv")
df_nodes = df_nodes[["entry_id", "year_from", "christian_tradition"]]

# Create a graph
G = nx.Graph()

# Add nodes with start_year attribute
for _, node in df_nodes.iterrows():
    G.add_node(
        node["entry_id"],
        year_from=node["year_from"],
        christian=node["christian_tradition"],
    )

# Add edges from DataFrame
for _, edge in df_edges.iterrows():
    G.add_edge(edge["entry_id_from"], edge["entry_id_to"], year=edge["overlap_start"])

# Extract the largest connected component (GCC)
gcc = max(nx.connected_components(G), key=len)
gcc_subgraph = G.subgraph(gcc)

# Compute y-positions using the spring layout
# We can do this smarter I'm sure.
pos = nx.spring_layout(gcc_subgraph, seed=42)  # Use seed for reproducibility
gcc_y_positions = {
    node: pos[node][1] for node in pos
}  # Extract the second element for y-coordinate

# Create plot
fig, ax = plt.subplots(figsize=(10, 8))

# Plot each connection in the GCC
for u, v in gcc_subgraph.edges():
    y_from = gcc_y_positions[u]
    y_to = gcc_y_positions[v]
    x_from = gcc_subgraph.nodes[u]["year_from"]
    x_to = gcc_subgraph.nodes[v]["year_from"]

    # Draw a line between the two nodes at their start years
    ax.plot(
        [x_from, x_to],
        [y_from, y_to],
        linestyle="-",
        color="tab:grey",
        alpha=0.2,
        linewidth=0.2,
    )

for node in gcc_subgraph:
    y = gcc_y_positions[node]
    x = gcc_subgraph.nodes[node]["year_from"]
    ax.plot(
        x,
        y,
        marker="o",
        color=["tab:orange" if gcc_subgraph.nodes[node]["christian"] else "tab:blue"][
            0
        ],
        markersize=1,
    )

# Set axes labels and title
ax.set_xlabel("Start Year")
ax.set_ylabel("")
ax.set_title("Phylogenetic Relationships by Christianity")
ax.grid(True)
plt.xlim(-1000, 1650)

from matplotlib.lines import Line2D

legend_elements = [
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Christian Traditions",
        markerfacecolor="tab:orange",
        markersize=10,
    ),
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Non-Christian Traditions",
        markerfacecolor="tab:blue",
        markersize=10,
    ),
]
ax.legend(handles=legend_elements, loc="upper left")

# Show the plot
plt.tight_layout()
plt.show()
