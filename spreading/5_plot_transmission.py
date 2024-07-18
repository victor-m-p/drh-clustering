import plotly.graph_objects as go
import numpy as np
import pandas as pd
import networkx as nx


# convenience function
def load_data(question_short):

    # Load your data
    # edges
    df_edges = pd.read_csv("data/spatiotemporal_overlap.csv")

    # nodes
    df_nodes = pd.read_csv(f"data/{question_short}_node_metrics.csv")

    # delete edges that are not in nodes
    df_edges = df_edges[df_edges["entry_id_from"].isin(df_nodes["entry_id"])]
    df_edges = df_edges[df_edges["entry_id_to"].isin(df_nodes["entry_id"])]

    return df_nodes, df_edges


def create_graph(df_nodes, df_edges):

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
            yes_parents=node["yes_parents"],
            yes_children=node["yes_children"],
            christian_parents=node["christian_parents"],
            christian_children=node["christian_children"],
        )

    # Add edges
    for _, edge in df_edges.iterrows():
        G.add_edge(
            edge["entry_id_from"], edge["entry_id_to"], year=edge["overlap_start"]
        )

    # Extract the largest connected component
    gcc = max(nx.connected_components(G), key=len)
    gcc_subgraph = G.subgraph(gcc)

    return gcc_subgraph


def find_focus_nodes(df_nodes, gcc_subgraph):

    # only the ones that answer yes
    df_nodes_yes = df_nodes[df_nodes["answer_value"] == 1]

    # if no upstream then fill with 0
    df_nodes_yes["yes_upstream"] = df_nodes_yes["yes_upstream"].fillna(0)

    # only nodes that are in gcc subgraph
    df_nodes_yes = df_nodes_yes[df_nodes_yes["entry_id"].isin(gcc_subgraph.nodes)]

    # calculate relevant metrics
    df_nodes_yes["yes_delta"] = (
        df_nodes_yes["yes_downstream"] - df_nodes_yes["yes_upstream"]
    )

    # sort by yes_delta and n_children
    df_nodes_yes = df_nodes_yes.sort_values(
        ["yes_delta", "n_children"], ascending=[False, False]
    )

    # take top 10 for highlighting
    df_nodes_yes = df_nodes_yes.head(10)["entry_id"].unique()
    return df_nodes_yes


def create_figure(gcc_subgraph, pos, question_name):

    # Initialize a Plotly graph object
    fig = go.Figure()

    # Add edges as lines
    for u, v in gcc_subgraph.edges():

        # edge coloring
        year_u_v = [
            gcc_subgraph.nodes[u]["year_from"],
            gcc_subgraph.nodes[v]["year_from"],
        ]
        christian_u_v = [
            gcc_subgraph.nodes[u]["christian"],
            gcc_subgraph.nodes[v]["christian"],
        ]
        min_year_idx = np.argmin(year_u_v)
        christian_parent = christian_u_v[min_year_idx]

        if christian_parent:
            line_color = "red"
        else:
            line_color = "grey"

        # main edge plot
        fig.add_trace(
            go.Scatter(
                x=[
                    gcc_subgraph.nodes[u]["year_from"],
                    gcc_subgraph.nodes[v]["year_from"],
                ],
                y=[pos[u][1], pos[v][1]],
                mode="lines",
                line=dict(color=line_color, width=0.2),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # Highlight a few nodes
    focus_nodes = find_focus_nodes(df_nodes, gcc_subgraph)
    focus_nodes_x = [gcc_subgraph.nodes[node]["year_from"] for node in focus_nodes]
    focus_nodes_y = [pos[node][1] for node in focus_nodes]
    fig.add_trace(
        go.Scatter(
            x=focus_nodes_x,
            y=focus_nodes_y,
            mode="markers",
            marker=dict(size=10, color="black"),
            hoverinfo="none",
            showlegend=False,
        )
    )

    ### main node plot ###

    # Prepare node hover texts
    hover_texts = [
        f"Entry Name: {gcc_subgraph.nodes[node]['entry_name']}<br>Entry ID: {node}<br>Answer Value: {gcc_subgraph.nodes[node]['answer_value']}<br>Yes % Parents: {gcc_subgraph.nodes[node]['yes_parents']}<br>Yes % Children: {gcc_subgraph.nodes[node]['yes_children']}<br>Christian % Parents: {gcc_subgraph.nodes[node]['christian_parents']}<br>Christian % Children: {gcc_subgraph.nodes[node]['christian_children']}"
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

    # Add nodes to the plot
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

    # Add custom legend for node colors and shapes (& edges)
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

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="red", width=2),
            legendgroup="edge",
            showlegend=True,
            name="Christian Parent",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="grey", width=2),
            legendgroup="edge",
            showlegend=True,
            name="non-Christian Parent",
        )
    )

    # Set layout properties
    fig.update_layout(
        title=f"{question_name} by Christianity",
        xaxis_title="Start Year",
        yaxis_title="",
        showlegend=True,
        hovermode="closest",
    )

    # Save the plot as an HTML file
    fig.write_html(f"{question_name}.html", full_html=True)

    # Optional: Show the plot in Jupyter Notebook (if needed)
    fig.show()


# loop over both questions
questions_short = ["conversion", "unquestionably"]
questions_name = ["conversion non-religionists", "is unquestionably good"]

for question_short, question_name in zip(questions_short, questions_name):

    # Load your data
    df_nodes, df_edges = load_data(question_short)

    # Create a graph
    gcc_subgraph = create_graph(df_nodes, df_edges)

    # Compute positions using spring layout
    pos = nx.spring_layout(gcc_subgraph, seed=110)

    # Create a Plotly figure
    create_figure(gcc_subgraph, pos, question_name)
