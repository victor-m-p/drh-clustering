import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from helper_functions import smooth_time_end

# setup
superquestion = "monitoring"
x_min = -2000
bin_width = 500
step_size = 100

# load and merge
df = pd.read_csv(f"../data/preprocessed/{superquestion}_long.csv")
df = df[["entry_id", "question_short", "question_id", "answer_value", "weight"]]

# get entry tags
entry_metadata = pd.read_csv(f"../controls/entry_tags.csv")
df = df.merge(entry_metadata, on="entry_id", how="inner")
df["year_from"] = df["year_from"].astype(int)
df["year_to"] = df["year_to"].astype(int)
df = df.dropna()
df["answer_value"] = df["answer_value"].astype(int)
df[["question_short", "question_id"]].drop_duplicates()

# select questions to show (all is too chaotic)
if superquestion == "shg":
    question_subset = [
        2941,  # anthropomorphic
        2948,  # sky deity
        2984,  # unquestionably good
        3288,  # indirect causal
        3283,  # hunger
        3218,  # worship other
    ]
elif superquestion == "monitoring":
    question_subset = [
        2928,  # prosocial norms
        2970,  # taboos
        2972,  # murder other polities
        2978,  # sex
        2923,  # shirking risk
        2930,  # performance rituals
        2982,  # conversion
    ]
df[["question_id", "question_short"]].drop_duplicates()
df = df[df["question_id"].isin(question_subset)]

# setup
n_rows = 2
n_cols = 2
entry_tags = ["christian", "islamic", "chinese", "buddhist"]
n_before_filtering = df["entry_id"].nunique()


def plot_entry_tags(df, x_min=-2000, bottom_vspace=0.2, include=False, outpath=None):
    n_rows = 2
    n_cols = 2
    n_before_filtering = df["entry_id"].nunique()

    # Create a new figure
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8, 6))

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    # Dictionary to store handles and labels for legend to avoid duplicates
    legend_info = {}

    # Loop over each entry_tag and subplot
    for i, entry_tag in enumerate(entry_tags):
        df_entry = df[df[entry_tag] == include]  # either include or exclude
        n_after_filtering = df_entry["entry_id"].nunique()
        n_removed = n_before_filtering - n_after_filtering
        percent_removed = n_removed / n_before_filtering * 100

        # Calculate time-slices and weighted average, etc.
        df_time = smooth_time_end(df_entry, bin_width, step_size)
        df_agg = (
            df_time.groupby(["time_bin", "question_short"])
            .apply(
                lambda x: (x["answer_value"] * x["weight"]).sum() / x["weight"].sum(),
                include_groups=False,
            )
            .reset_index(name="fraction_yes")
        )
        df_agg_subset = df_agg[df_agg["time_bin"] >= x_min - step_size]

        # Plot on the current subplot
        lineplot = sns.lineplot(
            data=df_agg_subset,
            x="time_bin",
            y="fraction_yes",
            hue="question_short",
            ax=axes[i],
        )

        # Set subplot titles
        if include:
            axes[i].set_title(
                f"{entry_tag} only: n={n_after_filtering} ({percent_removed:.2f}% removed)"
            )
        else:
            axes[i].set_title(
                f"{entry_tag}: removed n={n_removed} ({percent_removed:.2f}%)"
            )
        if i == 0:
            axes[i].set_xlabel("")
            axes[i].set_ylabel("Fraction yes")
        elif i == 1:
            axes[i].set_xlabel("")
            axes[i].set_ylabel("")
        elif i == 2:
            axes[i].set_xlabel("Year")
            axes[i].set_ylabel("Fraction Yes")
        else:
            axes[i].set_xlabel("Year")
            axes[i].set_ylabel("")
        axes[i].set_ylim(0, 1.1)
        axes[i].set_xlim(x_min, 2000)

        # Collect unique handles and labels for legend
        handles, labels = axes[i].get_legend_handles_labels()
        for handle, label in zip(handles, labels):
            if label not in legend_info:
                legend_info[label] = handle

    # Remove repeated legends from subplots
    for ax in axes:
        ax.get_legend().remove()

    # Create a single shared legend
    fig.legend(
        legend_info.values(),  # Unique handles
        legend_info.keys(),  # Unique labels
        loc="lower center",  # Place legend at the lower center
        bbox_to_anchor=(0.5, 0),  # Adjust anchor to keep within the figure
        ncol=3,  # Set number of columns to 3 or as needed
        frameon=False,
    )

    plt.tight_layout()

    # Adjust layout to provide space for the legend
    fig.subplots_adjust(
        bottom=bottom_vspace
    )  # Increase space at the bottom for the legend

    if outpath:
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
    else:
        plt.show()


plot_entry_tags(
    df,
    bottom_vspace=0.2,
    include=False,
    outpath=f"../figures/exluded_by_tags_{superquestion}.jpg",
)
plot_entry_tags(
    df,
    bottom_vspace=0.2,
    include=True,
    outpath=f"../figures/included_by_tags_{superquestion}.jpg",
)
