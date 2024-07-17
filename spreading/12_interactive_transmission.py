import plotly.graph_objects as go
import numpy as np
import pandas as pd
import networkx as nx

# setup
file_name = "conversion"  # "unquestionably"
question_label = "Conversion non-Religionists"  # "Unquestionably Good"
question_group = "monitoring"  # "shg"
question_name = "conversion non-religionists"  # "is unquestionably good"

# Load your data
df_edges = pd.read_csv("data/overlap_christianity.csv")
df_nodes = pd.read_csv("data/entry_data_subset.csv")
df_nodes = df_nodes[["entry_id", "entry_name", "year_from", "christian_tradition"]]

# Get all of the nodes that actually exist for the question
# With consistent answers
answers = pd.read_csv(f"../data/preprocessed/{question_group}_long.csv")
answers = answers[(answers["answer_value"].notna()) & (answers["weight"] == 1)]
answers = answers[answers["question_short"] == question_name]
answers = answers[["entry_id", "answer_value"]].drop_duplicates()
entries = answers["entry_id"].unique()
df_nodes = df_nodes.merge(answers, on="entry_id", how="inner")
df_edges = df_edges[df_edges["entry_id_to"].isin(entries)]
df_edges = df_edges[df_edges["entry_id_from"].isin(entries)]

# add node data for entries where we have this
node_data = pd.read_csv(f"data/{file_name}_model.csv")
node_data = node_data.rename(
    columns={"answer_value_to": "answer_value", "entry_id_to": "entry_id"}
)
node_data["avg_yes"] = np.round(node_data["avg_yes"], 2)
node_data["avg_christian"] = np.round(node_data["avg_christian"], 2)
node_data = node_data.drop(columns="answer_value")
df_nodes = df_nodes.merge(node_data, on="entry_id", how="left")

# quick fix
# node_data["avg_yes"] = df_nodes["avg_yes"].fillna(-100)
# node_data["avg_christian"] = node_data["avg_christian"].fillna(-100)
# so how are we missing this from unquestionably good? #

# Create a graph
G = nx.Graph()

# Add nodes
for _, node in df_nodes.iterrows():
    G.add_node(
        node["entry_id"],
        entry_name=node["entry_name"],
        year_from=node["year_from"],
        christian=node["christian_tradition"],
        answer_value=node["answer_value"],
        avg_yes=node["avg_yes"],
        avg_christian=node["avg_christian"],
    )

# Add edges
for _, edge in df_edges.iterrows():
    G.add_edge(edge["entry_id_from"], edge["entry_id_to"], year=edge["overlap_start"])

# Extract the largest connected component
gcc = max(nx.connected_components(G), key=len)
gcc_subgraph = G.subgraph(gcc)

# Compute positions using spring layout
pos = nx.spring_layout(gcc_subgraph, seed=42)
gcc_y_positions = {node: pos[node][1] for node in pos}

# Initialize a Plotly graph object
fig = go.Figure()

# Add edges as lines
for u, v in gcc_subgraph.edges():
    fig.add_trace(
        go.Scatter(
            x=[gcc_subgraph.nodes[u]["year_from"], gcc_subgraph.nodes[v]["year_from"]],
            y=[pos[u][1], pos[v][1]],
            mode="lines",
            line=dict(color="grey", width=0.2),
            hoverinfo="none",
            showlegend=False,
        )
    )

# Prepare node hover texts
hover_texts = [
    f"Entry Name: {gcc_subgraph.nodes[node]['entry_name']}<br>Entry ID: {node}<br>Answer Value: {gcc_subgraph.nodes[node]['answer_value']}<br>Christian Descent: {gcc_subgraph.nodes[node]['avg_christian']}<br>Yes Descent: {gcc_subgraph.nodes[node]['avg_yes']}"
    for node in gcc_subgraph
]

# Determine marker symbols based on answer value
marker_symbols = [
    "circle" if gcc_subgraph.nodes[node]["christian"] else "square"
    for node in gcc_subgraph
]

# Add nodes as scatter points
node_x = [gcc_subgraph.nodes[node]["year_from"] for node in gcc_subgraph]
node_y = [pos[node][1] for node in gcc_subgraph]
node_colors = [
    "orange" if gcc_subgraph.nodes[node]["answer_value"] == 1 else "blue"
    for node in gcc_subgraph
]

fig.add_trace(
    go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        marker=dict(
            size=5,  # Adjust size as needed
            color=node_colors,
            symbol=marker_symbols,
            line_width=1,
        ),
        hovertext=hover_texts,
        hoverinfo="text",
        showlegend=False,
    )
)

# Add custom legend for node colors and shapes
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(size=10, color="orange", symbol="circle"),
        legendgroup="color",
        showlegend=True,
        name="Answer: Yes",
    )
)

fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(size=10, color="blue", symbol="circle"),
        legendgroup="color",
        showlegend=True,
        name="Answer: No",
    )
)

fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(size=10, color="grey", symbol="circle"),
        legendgroup="shape",
        showlegend=True,
        name="Christian Tradition",
    )
)

fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(size=10, color="grey", symbol="square"),
        legendgroup="shape",
        showlegend=True,
        name="non-Christian Tradition",
    )
)

# Set layout properties
fig.update_layout(
    title=f"{question_label} by Christianity",
    xaxis_title="Start Year",
    yaxis_title="",
    showlegend=True,
    hovermode="closest",
)

# Save the plot as an HTML file
fig.write_html(f"{question_label}.html", full_html=True)

# Optional: Show the plot in Jupyter Notebook (if needed)
fig.show()
