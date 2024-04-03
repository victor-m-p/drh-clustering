import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#### setup ####
c = 6  # also pretty good and much simpler
superquestion = "monitoring"
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_{c}_group.csv")
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_{c}_group.csv")


#### overview of dimensions ####
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


### temporal analysis ###
dimension_columns = [f"dim{x}" for x in range(c)]
temporal_columns = ["entry_id", "entry_name", "year_from"] + dimension_columns
df_temporal = df_q[temporal_columns]
df_temporal["year_from"] = df_temporal["year_from"].astype(int)


# 1. sort into n bins
from fun import time_bin

n = 5
df_temporal = time_bin(df_temporal, n)


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
plt.ylim(0, 0.4)
plt.legend(title="Dimension", loc="upper right")
plt.tight_layout()
plt.show()

""" of note: 
1. Clearly very limited data before -2000.
2. dim2 (hungry sky deity permitting worship of other Gods): declines especially after -500. 
3. dim0 (see above) and dim1 (see above) rise and peak around 1100.
4. dim4 (minimal) and dim6 (see above) peak for most recent data. 

Will take some digging to really understand these (and perhaps these are not the best dimensions):
Very broadly we move from more maximal to more minimal concepts. 
Very broadly we move away from anthropomorphic and hungry gods. 
"""

#### Dimensions and Social Scale ####
iv_dv_cols = ["entry_id", "entry_name", "social_scale", "region_area"]
iv_dv_cols = iv_dv_cols + dimension_columns
iv_dv = df_q[iv_dv_cols]
iv_dv = iv_dv[iv_dv["social_scale"].isin(["small-scale", "large-scale"])]
iv_dv["max_dimension_column"] = iv_dv[dimension_columns].idxmax(axis=1)
iv_dv = iv_dv.drop(columns=dimension_columns)
iv_dv["social_scale_binary"] = np.where(iv_dv["social_scale"] == "large-scale", 1, 0)
iv_dv.groupby("max_dimension_column")["social_scale_binary"].mean()

""" social scale take-aways: 
1. there is some signal but very mixed:
--> dim1 and dim5 most "small scale" (these gods are not: hungry, chthonic, monarch)
--> dim4 and dim0 most "large scale" (these gods are: elite/monarch, chthonic)
"""

""" region area take-aways
1. I believe that this is misleading because we have texts.
2. Smallest median region is dim4 by far, but I suspect these are texts.
"""

#### Pairwise Correlations ####
df_matrix = pd.read_csv(f"../data/ML/{superquestion}.csv")
df_matrix = df_matrix.drop(columns=["entry_id"])

# 1. remap the columns to interpretable format:
unique_question_mapping = shg_answers[
    shg_answers["related_question_id"].isin(unique_questions)
]
unique_question_mapping = unique_question_mapping[
    ["related_question_id", "question_short"]
].drop_duplicates()
unique_question_mapping["related_question_id"] = "Q" + unique_question_mapping[
    "related_question_id"
].astype(str)
unique_question_mapping_dict = dict(
    zip(
        unique_question_mapping["related_question_id"],
        unique_question_mapping["question_short"],
    )
)

# 2. calculate the weighted correlations
from fun import weighted_corr

df_matrix = df_matrix.rename(columns=unique_question_mapping_dict)
features = df_matrix.columns[:-1]  # all columns except the last 'weight' column
correlations = weighted_corr(features, df_matrix)

# 3. clustering to highlight patterns
from scipy.spatial.distance import squareform
from scipy.cluster import hierarchy

distances = 1 - np.abs(correlations)
condensed_dist_matrix = squareform(distances, checks=False)
linkage = hierarchy.linkage(condensed_dist_matrix, method="weighted")
dendro = hierarchy.dendrogram(linkage, no_plot=True)
sorted_indexes = dendro["leaves"]
sorted_corr = correlations.iloc[sorted_indexes, sorted_indexes]

# 4. plot the heatmap
mask = np.triu(np.ones_like(sorted_corr, dtype=bool))

plt.figure(figsize=(10, 9))
sns.heatmap(
    sorted_corr,
    mask=mask,
    annot=True,
    vmax=1,
    center=0,
    fmt=".1f",
    cmap="coolwarm",
    cbar_kws={"shrink": 0.5},
    square=True,
)
plt.title("Clustered Correlation Matrix Heatmap")
plt.show()

""" Take-aways on correlations: 
1. Not a super strong signal here. 
2. There does seem to be some (weak packages): 
2.1: emotion, causal efficacy, communicate with living, anthropomorphic.
2.2: causal efficacy, communicate with living, knowledge of this world.
2.3: (worship other and hunger) or (unquestionably good)

A possible story is that Gods get less anthropomorphic (e.g., hungry)
Gods become more good and less likely to allow worship of other Gods. 
"""

"""
Future directions: 
* (validation): Impact of "Text" and number of dimensions
* (validation): spatio-temporal weighting? (currently no). 
* change-point detection (where are the break-points?)
* cultural transmission and universality. 
* ...
"""
