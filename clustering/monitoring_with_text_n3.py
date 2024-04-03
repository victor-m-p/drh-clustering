import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#### setup ####
c = 3  # minimize BIC
superquestion = "monitoring"
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_{c}_all.csv")
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_{c}_all.csv")

# First plot data preparation
df_plot1 = df_theta.drop(columns=["related_question_id", "question_mean"])
df_plot1.set_index("question_short", inplace=True)

# Second plot data preparation
df_plot2 = df_theta.drop(columns=["related_question_id"])
df_plot2.set_index("question_short", inplace=True)
value_columns = df_plot2.columns.difference(["question_mean"])
df_plot_relative = df_plot2[value_columns].sub(df_plot2["question_mean"], axis=0)

# Creating a figure with two subplots side-by-side
fig, ax = plt.subplots(1, 2, figsize=(12, 6))  # Adjust the figsize as needed

# Plotting the first heatmap
sns.heatmap(df_plot1, cmap="coolwarm", center=0, ax=ax[0])
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha="right")
ax[0].set_xlabel("Dimension")
ax[0].set_ylabel("Question")
ax[0].set_title("Absolute Weighting")

# Plotting the second heatmap
sns.heatmap(df_plot_relative, cmap="coolwarm", center=0, ax=ax[1])
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha="right")
ax[1].set_xlabel("Dimension")
ax[1].set_ylabel("Question")
ax[1].set_title("Relative Weighting")
ax[1].set_yticklabels([])  # Remove the y-tick labels

plt.suptitle("Question Weightings", size=15, y=1.02)
plt.tight_layout()
plt.show()


""" overview: 
dim0 (0.82): 
--> pretty maximal.
--> less concerned about conversion of non-religionists
--> less conserned about shirking risk
dim1 (0.33): 
--> pretty minimal. 
--> still high in ritual performance / observance
--> somewhat high in honoring oaths, prosocial norms, and taboos.
dim2 (0.97):
--> almost entirely maximal.
"""

#### which religions high in what? ####
# things we need a lot

#### which religions high in what? ####
# 1. things we need a lot
dimensions = [f"dim{x}" for x in range(c)]
unique_questions = df_theta["related_question_id"].unique().tolist()
entry_dimensions = ["entry_id", "entry_name"] + dimensions

# 2. get answers
shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
shg_answers = shg_answers[
    ["entry_id", "related_question_id", "question_short", "answer_numeric"]
].drop_duplicates()
shg_answers = shg_answers[shg_answers["related_question_id"].isin(unique_questions)]
entry_dim = df_q[entry_dimensions]

# 3. find each in turn and check distribution
entry_dim.sort_values("dim2", ascending=False).head(8)
shg_answers[shg_answers["entry_id"] == 841]

""" Examples in each dimensions: 
dim0: 
--> 950: Religious Society of Friends
--> 771: Muscular Christianity
--> 381: Sikhism: Guru Nanak to Guru Arjan
--> 879: Free Methodist Church
--> 915: Protestantism welcoming People with Disabilities

dim1:
--> 1401: The "On the Divine Names" of Pseudo Denys...
--> 1852: The Communion Letters by Whitley and Anne...
--> 1044: Han Imperial Cult under Emperor Wu
--> 1657: The Institutes of John Cassian
--> 361: Classical Greek Religion

dim2: 
--> 2116: Qadiriyyah Movement in Sokoto Caliphate
--> 1247: Exovedate
--> 1741: Methodism in Zimbabwe
--> 1709: Almohads (al-Muwahhidun)
--> 1653: Le Parti du Mouvement de La Nahda
"""

#### SPACE ####
# 1. preprocessing and weighting
regions_coded = pd.read_csv("../data/preprocessed/regions_coded.csv")
regions_coded = regions_coded[["world_region", "entry_id"]].drop_duplicates()
counts = (
    regions_coded.groupby("entry_id")["world_region"].count().reset_index(name="count")
)
regions_weight = regions_coded.merge(counts, on="entry_id")
regions_weight["weight"] = 1 / regions_weight["count"]
regions_weight.drop(columns=["count"], inplace=True)

# 2. take only entries that are at maximum in 2 world regions
regions_weight = regions_weight[regions_weight["weight"] > 0.5]

# 3. Get weighted average on world_regions for the categories
q_weighted = regions_weight.merge(df_q, on="entry_id", how="inner")
q_weighted = q_weighted[q_weighted["year_from"] < 1950]  # avoid global
q_weighted = q_weighted.drop(
    columns=[
        "entry_id",
        "entry_name",
        "social_scale",
        "region_id",
        "unique_region",
        "region_area",
        "year_from",
        "year_to",
        "unique_timespan",
        "expert_id",
        "expert_name",
        "editor_id",
        "editor_name",
        "earliest_date_created",
        "latest_date_modified",
        "poll",
    ]
)


# 4. highest and lowest dimension per group
from fun import weighted_average

spatial_patterns = (
    q_weighted.groupby("world_region").apply(weighted_average).reset_index()
)


from fun import highest_and_lowest_per_group

highest_lowest_per_region = (
    spatial_patterns.drop("world_region", axis=1)
    .groupby(spatial_patterns["world_region"])
    .apply(highest_and_lowest_per_group)
)
highest_lowest_per_region.reset_index()

""" Some clear spatial patterns here: 

Africa: 
- high on dim2 low on dim1. 

"""

# 5. highest and lowest group per dimension
from fun import highest_and_lowest_iter

highest_lowest_per_dim = []
dimension_columns = [f"dim{x}" for x in range(c)]
highest_lowest_per_dim = highest_and_lowest_iter(spatial_patterns, dimension_columns)
highest_lowest_per_dim

"""
Not sure what to say about this currently.
"""

#### time ####
temporal_columns = ["entry_id", "entry_name", "year_from"] + dimension_columns
df_temporal = df_q[temporal_columns]
df_temporal["year_from"] = df_temporal["year_from"].astype(int)


# 1. sort into n bins
from fun import time_bin

n = 5
df_temporal = time_bin(df_temporal, n)

df_temporal_long = df_temporal.melt(
    id_vars=["entry_id", "entry_name", "year_from", "time_bin", "time_range"],
    value_vars=dimension_columns,
    var_name="dimension",
    value_name="value",
)

# 2. plot
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_temporal_long, x="time_bin", y="value", hue="dimension")

# Move legend outside of the plot
plt.legend(title="Dimension", bbox_to_anchor=(1.05, 1), loc="upper left")

# For setting the x-axis labels to rounded year range from 'time_range'
# Extract years and round them
time_ranges = df_temporal_long["time_range"].unique()
rounded_labels = [
    f"({int(interval.left)}, {int(interval.right)})" for interval in time_ranges
]

# Convert time_bin to corresponding rounded year range for x-ticks
time_bin_to_range = dict(enumerate(rounded_labels))
plt.xticks(range(n), [time_bin_to_range[i] for i in range(n)])

plt.tight_layout()
plt.show()

""" of note: 
1. most minimal dimensions decline over time 
--> dim0 (minimal).
--> dim5 (with murder, rituals, prosocial norms). 
--> dim4 ...

2. most maximal dimensions increase over time
--> dim2, dim6, dim1 (most maximal) are highest for most recent time period.
"""

# 3. smoothed over time
df_smoothed = pd.DataFrame()
bin_width = 500
step_size = 5

from fun import smooth_time

df_smoothed = smooth_time(df_temporal, bin_width, step_size)

# Aggregate the data within each bin for each dimension
df_smoothed_agg = (
    df_smoothed.groupby("time_bin")[dimension_columns].mean().reset_index()
)

# Melt the aggregated DataFrame for plotting
df_smoothed_long = df_smoothed_agg.melt(
    id_vars=["time_bin"],
    value_vars=dimension_columns,
    var_name="dimension",
    value_name="value",
)

# Plot
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_smoothed_long, x="time_bin", y="value", hue="dimension")
plt.xticks(rotation=45)
delta = int(np.round(bin_width / 2, 0))
plt.xlabel(f"Mean year: smoothed over {bin_width} years")
plt.xlim(-1000)
plt.ylim(0, 0.6)
plt.legend(title="Dimension")
plt.tight_layout()
plt.show()

""" of note: 
Clearly we still have the dimension that just dies. 
"""
