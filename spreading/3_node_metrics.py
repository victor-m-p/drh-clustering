import pandas as pd
import numpy as np
import networkx as nx


def create_node_list(question_short):
    # Load data
    df_nodes = pd.read_csv(f"data/{question_short}_metrics.csv")

    # First add entry name, christian tradition, and year_from
    entry_data = pd.read_csv("data/entry_data_subset.csv")
    entry_data = entry_data[
        ["entry_id", "entry_name", "year_from", "christian_tradition"]
    ]
    df_nodes = df_nodes.merge(entry_data, on="entry_id", how="inner")
    return df_nodes


def create_edge_list(df_nodes):
    # then load spatiotemporal data
    spatiotemporal_overlap = pd.read_csv("data/spatiotemporal_overlap.csv")

    # and remove edges that are not in nodes
    df_edges = spatiotemporal_overlap[
        spatiotemporal_overlap["entry_id_from"].isin(df_nodes["entry_id"])
    ]
    df_edges = df_edges[df_edges["entry_id_to"].isin(df_nodes["entry_id"])]
    return df_edges


# Function to find all downstream nodes of a given node
def find_downstream_nodes(graph, start_node):
    # Perform DFS to get all reachable nodes
    all_nodes = list(nx.dfs_preorder_nodes(graph, start_node))
    # Exclude the start node itself
    all_nodes.remove(start_node)
    # Sort the resulting list
    sorted_nodes = sorted(all_nodes)
    return sorted_nodes


# Function to find all upstream nodes of a given node
def find_upstream_nodes(graph, start_node):
    # Reverse the graph
    reversed_graph = graph.reverse()
    # Perform DFS to get all reachable nodes in the reversed graph
    all_nodes = list(nx.dfs_preorder_nodes(reversed_graph, start_node))
    # Exclude the start node itself
    all_nodes.remove(start_node)
    # Sort the resulting list
    sorted_nodes = sorted(all_nodes)
    return sorted_nodes


# Function to calculate downstream metrics for a given node and return a tuple
def calculate_downstream_metrics(G, df_metrics, start_node):
    downstream_nodes = find_downstream_nodes(G, start_node)
    n_downstream = len(downstream_nodes)

    if n_downstream == 0:
        return (start_node, 0, np.nan, np.nan)

    yes_downstream = df_metrics[df_metrics["entry_id"].isin(downstream_nodes)][
        "answer_value"
    ].mean()
    christian_downstream = df_metrics[df_metrics["entry_id"].isin(downstream_nodes)][
        "christian_tradition"
    ].mean()

    return (
        start_node,
        n_downstream,
        round(yes_downstream, 2),
        round(christian_downstream, 2),
    )


# Function to calculate upstream metrics for a given node and return a tuple
def calculate_upstream_metrics(G, df_metrics, start_node):
    upstream_nodes = find_upstream_nodes(G, start_node)
    n_upstream = len(upstream_nodes)

    if n_upstream == 0:
        return (start_node, 0, np.nan, np.nan)

    yes_upstream = df_metrics[df_metrics["entry_id"].isin(upstream_nodes)][
        "answer_value"
    ].mean()
    christian_upstream = df_metrics[df_metrics["entry_id"].isin(upstream_nodes)][
        "christian_tradition"
    ].mean()

    return (
        start_node,
        n_upstream,
        round(yes_upstream, 2),
        round(christian_upstream, 2),
    )


questions_short = ["unquestionably", "conversion"]

for question_short in questions_short:
    print(question_short)
    # Create node and edge lists
    node_list = create_node_list(question_short)
    edge_list = create_edge_list(node_list)

    G = nx.DiGraph()
    for _, edge in edge_list.iterrows():
        G.add_edge(edge["entry_id_from"], edge["entry_id_to"])

    # Calculate downstream metrics for all nodes
    downstream_metrics = [
        calculate_downstream_metrics(G, node_list, node) for node in G.nodes()
    ]

    # Convert the list of tuples to a DataFrame
    df_downstream_metrics = pd.DataFrame(
        downstream_metrics,
        columns=["entry_id", "n_downstream", "yes_downstream", "christian_downstream"],
    ).sort_values("entry_id")

    # Calculate upstream metrics for all nodes
    upstream_metrics = [
        calculate_upstream_metrics(G, node_list, node) for node in G.nodes()
    ]

    # Convert the list of tuples to a DataFrame
    df_upstream_metrics = pd.DataFrame(
        upstream_metrics,
        columns=["entry_id", "n_upstream", "yes_upstream", "christian_upstream"],
    ).sort_values("entry_id")

    # Merge with the original node list
    node_list = node_list.merge(df_downstream_metrics, on="entry_id", how="inner")
    node_list = node_list.merge(df_upstream_metrics, on="entry_id", how="inner")
    node_list.to_csv("data/" + question_short + "_node_metrics.csv", index=False)
