import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from helper_functions import smooth_time_end

# setup
subset = "groups"  # all
x_min = -2000
bin_width = 100  # years per rolling window (used in labels and file names)
step_size = 50
fig_dir = "fig/selected_questions"
os.makedirs(fig_dir, exist_ok=True)

# select questions to show (all is too chaotic)
question_subsets = {
    "shg": [
        2941,  # anthropomorphic
        2948,  # sky deity
        2984,  # unquestionably good
        3288,  # indirect causal
        3283,  # hunger
        3218,  # worship other
    ],
    "monitoring": [
        2928,  # prosocial norms
        2970,  # taboos
        2972,  # murder other polities
        2923,  # shirking risk
        2930,  # performance rituals
        2982,  # conversion
        2985,  # econ fair
    ],
}

# fix question labels (line breaks for the legend)
label_fixes = {
    "shg": {
        "indirect causal efficacy the world": "indirect causal efficacy\nin this world",
        "permissible to worship other god?": "permissible to worship\nother god?",
    },
    "monitoring": {
        "conversion non-religionists": "conversion\nnon-religionists",
        "prosocial norm adherence": "prosocial norm\nadherence",
    },
}

# load and merge
df = pd.read_csv(f"../data/preprocessed/answers_subset_{subset}.csv")
df = df[["entry_id", "question_short", "question_id", "answer_value", "weight"]]
entry_metadata = pd.read_csv(f"../data/sccsrv3/entry_data.csv")
entry_metadata = entry_metadata[["entry_id", "year_from", "year_to", "poll_name"]]
df = df.merge(entry_metadata, on="entry_id", how="inner")
df["year_from"] = df["year_from"].astype(int)
df["year_to"] = df["year_to"].astype(int)
df = df.dropna()
df["answer_value"] = df["answer_value"].astype(int)
# note: some entries can have conflicting answers; keeping this.

for superquestion, question_subset in question_subsets.items():
    df_sub = df[df["question_id"].isin(question_subset)]

    # time-slices
    df_time = smooth_time_end(df_sub, bin_width, step_size)

    # weighted average
    df_agg = (
        df_time.groupby(["time_bin", "question_short"])
        .apply(lambda x: (x["answer_value"] * x["weight"]).sum() / x["weight"].sum(), include_groups=False)
        .reset_index(name="fraction_yes")
    )

    # Take only from the time range
    df_agg_subset = df_agg[df_agg["time_bin"] >= x_min - step_size].copy()
    y_max = df_agg_subset["fraction_yes"].max()
    y_max = y_max + 0.05
    df_agg_subset["question_short"] = df_agg_subset["question_short"].replace(label_fixes[superquestion])

    # Plot
    plt.figure(figsize=(10, 5), dpi=300)
    sns.lineplot(data=df_agg_subset, x="time_bin", y="fraction_yes", hue="question_short")
    plt.xticks(rotation=45)
    plt.yticks()
    plt.xlabel(f"Year ({bin_width}-year rolling window)", size=12)
    plt.ylabel("Fraction yes", size=12)
    plt.ylim(0, y_max)

    # Adjust y axis ticks
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.1))

    # Specify the number of columns in the legend
    ncol = 1

    # Place the legend below the plot without a title and without a box
    plt.legend(
        fontsize=14,
        loc="upper center",
        bbox_to_anchor=(1.3, 1.05),
        ncol=ncol,
        frameon=False,
    )

    plt.tight_layout()
    plt.savefig(
        f"{fig_dir}/{superquestion}_{subset}_{bin_width}.jpg",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
