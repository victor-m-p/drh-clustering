import plotly.graph_objects as go
import numpy as np
import pandas as pd
import networkx as nx

# setup
file_name = "conversion"  # "unquestionably"
question_label = "Conversion non-Religionists"  # "Unquestionably Good"

# Load your data
df_edges = pd.read_csv("data/overlap_christianity.csv")
df_nodes = pd.read_csv("data/entry_data_subset.csv")
df_nodes = df_nodes[["entry_id", "entry_name", "year_from", "christian_tradition"]]

unquestionably_good = pd.read_csv(f"data/{file_name}_model.csv")
unquestionably_good = unquestionably_good.rename(
    columns={"answer_value_to": "answer_value", "entry_id_to": "entry_id"}
)
unquestionably_good["avg_yes"] = np.round(unquestionably_good["avg_yes"], 2)
unquestionably_good["avg_christian"] = np.round(unquestionably_good["avg_christian"], 2)
df_nodes = df_nodes.merge(unquestionably_good, on="entry_id", how="inner")

# edges should be in the dataset
df_edges = df_edges[df_edges["entry_id_to"].isin(df_nodes["entry_id"])]
df_edges = df_edges[df_edges["entry_id_from"].isin(df_nodes["entry_id"])]

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

# Add edges as lines with custom data attributes
edge_trace_indices = []
for u, v in gcc_subgraph.edges():
    trace = go.Scatter(
        x=[gcc_subgraph.nodes[u]["year_from"], gcc_subgraph.nodes[v]["year_from"]],
        y=[pos[u][1], pos[v][1]],
        mode="lines",
        line=dict(color="grey", width=0.2),
        hoverinfo="none",
        showlegend=False,
        customdata=[(u, v)],  # Custom data for edges
    )
    fig.add_trace(trace)
    edge_trace_indices.append(len(fig.data) - 1)

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

# Add nodes as scatter points with custom data attributes
node_x = [gcc_subgraph.nodes[node]["year_from"] for node in gcc_subgraph]
node_y = [pos[node][1] for node in gcc_subgraph]
node_colors = [
    "orange" if gcc_subgraph.nodes[node]["answer_value"] == 1 else "blue"
    for node in gcc_subgraph
]

node_trace = go.Scatter(
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
    customdata=list(gcc_subgraph.nodes),  # Custom data for nodes
    showlegend=False,
)

fig.add_trace(node_trace)

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

# JavaScript to highlight edges on hover
hover_js = f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{
    console.log('DOM content loaded and script running');
    alert('JavaScript is running');

    var myPlot = document.getElementById('myDiv');
    if (myPlot) {{
        console.log('Plotly div found:', myPlot);

        myPlot.on('plotly_hover', function(data) {{
            console.log('Hover event triggered');
            console.log('Hovered node data:', data.points[0]);

            var edges = {edge_trace_indices};
            var points = data.points;
            var update = {{
                'line.color': [],
                'line.width': []
            }};

            for (var i = 0; i < edges.length; i++) {{
                update['line.color'][i] = 'grey';
                update['line.width'][i] = 0.2;
            }}

            var hoveredNode = points[0].customdata;
            console.log('Hovered node ID:', hoveredNode);

            for (var i = 0; i < edges.length; i++) {{
                var edgeData = myPlot.data[edges[i]].customdata[0];
                console.log('Edge data:', edgeData);
                if (edgeData.includes(hoveredNode)) {{
                    update['line.color'][i] = 'red';
                    update['line.width'][i] = 2;
                }}
            }}

            Plotly.restyle(myPlot, update);
        }});

        myPlot.on('plotly_unhover', function(data) {{
            console.log('Unhover event triggered');

            var edges = {edge_trace_indices};
            var update = {{
                'line.color': [],
                'line.width': []
            }};

            for (var i = 0; i < edges.length; i++) {{
                update['line.color'][i] = 'grey';
                update['line.width'][i] = 0.2;
            }}

            Plotly.restyle(myPlot, update);
        }});
    }} else {{
        console.log('Plotly div not found');
    }}
}});
</script>
"""

# Save the plot as an HTML file with embedded JavaScript
html_string = fig.to_html(include_plotlyjs="cdn", full_html=False)
html_string = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{question_label}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div id="myDiv" style="width: 100%; height: 100vh;"></div>
    <script>
        var myPlotDiv = document.getElementById('myDiv');
        Plotly.newPlot(myPlotDiv, {fig.to_json()}, {{
            responsive: true
        }}).then(function() {{
            {hover_js}
        }});
    </script>
</body>
</html>
"""

with open(f"{question_label}.html", "w") as f:
    f.write(html_string)
