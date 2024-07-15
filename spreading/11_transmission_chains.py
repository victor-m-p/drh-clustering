import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

df_edges = pd.read_csv("data/overlap_christianity.csv")
df_nodes = pd.read_csv("data/entry_data_subset.csv")
df_nodes = df_nodes[["entry_id", "year_from"]]

# Create a graph
G = nx.Graph()

# Add nodes with start_year attribute
for _, node in df_nodes.iterrows():
    G.add_node(node["entry_id"], year_from=node["year_from"])

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
fig, ax = plt.subplots(figsize=(10, 6))

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
        marker="o",
        linestyle="-",
        color="b",
        alpha=0.2,
        linewidth=0.2,
        markersize=0.8,
    )  # 'o' for the nodes, '-' for the line

# Set axes labels and title
ax.set_xlabel("Start Year")
ax.set_ylabel("Entry IDs")
ax.set_title("Visualizing Phylogenetic Relationships with Node Start Years")
ax.grid(True)
plt.xlim(-3000, 1600)

# Show the plot
plt.tight_layout()
plt.show()
