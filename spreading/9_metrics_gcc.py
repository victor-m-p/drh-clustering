"""
Figuring out which entries are not in the GCC subgraph.
I suspect that many of them are connected to other entries,
just not to the GCC. 
"""

import pandas as pd

# load metrics
df_metrics = pd.read_csv("data/conversion_node_metrics.csv")
entry_data = pd.read_csv("data/entry_data_subset.csv")
gcc_nodes = pd.read_csv("data/gcc_nodes_conversion.csv")

# merge everything
df_metrics = df_metrics.merge(gcc_nodes, on="entry_id", how="left", indicator=True)
df_metrics = df_metrics.rename(columns={"_merge": "in_gcc"})
df_metrics["in_gcc"] = df_metrics["in_gcc"].replace({"both": True, "left_only": False})

# find the earliest yes answers
metrics_yes = df_metrics[df_metrics["answer_value"] == 1]
metrics_yes.sort_values("year_from").head(10)

# is it specific regions that are left out?
gcc_nodes = entry_data.merge(gcc_nodes, on="entry_id", how="left", indicator=True)
gcc_nodes.groupby("world_region")["_merge"].value_counts(normalize=True)

# we need to find a way to connect this I think.
# look into the sub-graphs (e.g., other connected parts that are lacking connection with GCC
gcc_nodes[gcc_nodes["_merge"] == "left_only"].head(10)
