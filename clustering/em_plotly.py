import plotly.express as px
import pandas as pd

### plot monitoring (not reweighted) ###
files = [
    "../data/EM/reweighted_shg_conditional_True_reweight_False_theta.csv",
    "../data/EM/reweighted_monitoring_conditional_True_reweight_False_theta.csv",
]
conditions = ["shg", "monitoring"]
df = pd.read_csv(files[0])

for condition, file in zip(conditions, files):

    df = pd.read_csv(file)

    # Create the 3D scatter plot
    fig = px.scatter_3d(
        df,
        x="dim0_log_change",
        y="dim1_log_change",
        z="dim2_log_change",
        # color='cluster',
        hover_data=["question_short"],
    )

    # Customize the axes labels
    fig.update_layout(
        scene=dict(xaxis_title="dim 0", yaxis_title="dim 1", zaxis_title="dim 2")
    )

    # Show the plot
    fig.show()

    # Export to HTML file
    fig.write_html(f"fig/{condition}_interactive.html")
