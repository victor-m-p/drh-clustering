import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#### setup ####
c = 8  # minimize BIC
superquestion = "shg"
df_q = pd.read_csv(f"../data/EM/{superquestion}_q_{c}.csv")
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_{c}.csv")

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


""" overview: 
dim0: medium concept (0.38): high (knowledge, good, causal, positive) low (chthonic, kin elite, monarch)
dim1: medium concept (0.58): high (knowledge, positive, causal, negative, good) low (kin elite, monarch, worship other)
dim2: medium concept (0.67): high (knowledge, causal, permissible, communicate, hunger, ...) low (monarch manifest/fused, chtonic)
dim3: maximal concept (0.77): high (knowledge, positive, communicate, causal, anthro) low (chthonic, elite kin/loyal)
dim4: medium concept (0.49: high (knowledge, causal, communicate, neg/pos emotion) low (elite kin, chthonic, worship other). 
dim5: minimal concept (0.33): high (worship other, indirect causal, knowledge, good) low (chthonic, hunger, monarch)
dim6: medium concept (0.46): high (knowledge, (in)direct causal, good) low (hunger, elite kin, monarch)
dim7: medium concept (0.58): high (communicate, positive, knowledge, causal) low (monarch, chthonic, elite kin)
"""

df_theta.sort_values("question_mean")

""" overview 
generally most common features: 
* knowledge of this world (0.98)
* causal efficacy this world (0.92)
* communicate with living (0.85)
* positive emotion (0.82)
* unquestionably good (0.81)

generally least common features: 
* monarch fused (0.10)
* kin to elites (0.11)
* monarch manifestation (0.13)
* chthonic (0.15)
* other elite loyalty (0.18)
"""

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
entry_dim.sort_values("dim1", ascending=False).head(20)
shg_answers[shg_answers["entry_id"] == 1795]

""" Examples in each dimensions: 

dim0 (generally: good, knowledge, causal, communicate)
2083 (The spirit of Morality): sky deity, good, knowledge, hunger, communicate
1985 (Christianity in Antioch): good, knowledge, efficacy, positive, communicate
1412 (Tenrikyo): good, knowledge, causal, positive, communicate
1401 (On the Divine Names): good, knowledge, causal, positive, communicate

dim1: (generally: sky deity, chthonic, good, knowledge, causal, pos/neg emotion, hunger, communicate)
2089 (L'ordre Soufit Karkariya): sky deity, chthonic, good, knowledge, pos/neg emotion, communicate
2092 (Interpretation of Imam Ibn Arafa...): sky deity, chthonic, good, knowledge, causal, pos/neg emotion, hunger, communicate
2075 (L'interpretation du Coran...): sky deity, chthonic, good, knowledge, causal, pos/neg emotion, hunger, communicate
2087 (Al-Tabari's interpretation of the Qur'an): sky deity, chthonic, good, knowledge, causal, pos/neg emotion, hunger, communicate
NB: seems to capture Qur'an interpretations. 

dim2: (generally: anthropomorphic, sky, knowledge, causal, hunger, communicate)
1855 (Atra-Hasis): anthropomorphic, sky, knowledge, causal, negative, hunger, worship other
211 (Amarna Religion): elite kin, anthropomorphic, sky, good, knowledge, causal, hunger, communicate
589 (Warrau): (many NAN) anthropomorphic, sky, permissible, negative emotion, causal, hunger
1375 (Epic of Gilgamesh): anthropomorphic, sky, knowledge, causal, negative emotion, hunger, worship other, communicate

dim3: (generally: maximal without elite connection and unquestionably good)
738 (Ancient Egyptian): does not have elite kin, elite loyalty, good, hunger.
520 (Cham Ahier): does not have good, hunger
973 (Sarna religion): does not have anthropomorphic, elite kin, causal efficacy
1037 (Third intermediate Ancient Egypt): does not have chthonic, elite kin/loyalty, good

dim4: (generally: only knowledge, causal, emotion, good, communicate)
1576 (Book of Amos): knowledge, causal, negative emotion (positive NAN), communicate
1058 (Syonggyong chikhae...): anthropomorphic, good, knowledge, causal, pos/neg. emotion, communicate 
985 (The Victorines): anthropomorphic, good, knowlegde, causal efficacy, pos/neg emotion, communicate
958 (Society of Jesus): anthropomorphic, good, knowledge, causal, pos/neg emotion, communicate

dim5: (generally: minimal concept with indirect causal efficy and permissible to woship other gods)
893 (Sethian Gnostic): Only indirect causal and worship other
986 (Theurgy): Only monarch manifestation, good, indirect causal, and worship other
1044 (Han Imperial under Wu): Only sky deity, indirect causal, worship other
862 (Ilm-e-Khsnoom): Only knowledge this world, indirect causal, worship other

dim6: (generally: God without anthropomorphic/emotion/hunger and generally not elite/monarch without worship other)
1606 (Kitab Sara'ir..): without anthropomorphic, elite kin, emotion, hunger, worship other, communicate
2116 (Qadiriyyah Movement..): without anthropomorphic, monarch, elite, emotion, hunger, worship other
1618 (Diya'u al-Ta'aweel..): without anthropomorphic, monarch, elite, emotion, hunger, worship other
2059 (The Garden of Knowers): without anthropomorphic, monarch, elite, (both yes/no to emotion and worship other)

dim7: (generally: communicate, anthropomorphic, emotion, causal, limited elite connection) 
1424 (Santian neijie jing): anthropomorphic, elite loyalty, good, causal, emotion, worship other, communicate
1661 (Ludlul Bel Nemeqi): antropomorphic, elite loyalty, good, knowledge, causal, emotion, worship other, communicate
1248 (Old Assyrian): anthropomorphic, good, knoweldge, causal, emotion, hunger, worship other, communicate
921 (Bhils): antrhopomorphic, elite loyalty, knowledge, causal, emotion, worship other, communicate
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

""" Does any of this make sense?

Africa: 
- high: dim6 (non-anthro)
- low: dim5 (minimal concept)

Central Eurasia: 
- high: dim2 (anthro/sky)
- low: dim3 (miximal without elite)
- NB: very mixed between all dimensions

East Asia:
- high: dim5 (minimal concept)
- low: dim4 (knowledge, emotion, causal, communicate)

Europe: 
- high: dim2 (anthro/sky)
- low: dim6 (non-anthro)

North America:
- high: dim5 (minimal concept)
- low: dim3 (maximal without elite)

Oceania-Australia: 
- high: dim5 (minimal concept)
- low: dim3 (maximal without elite)

South America: 
- high: dim5 (minimal concept)
- low: dim6 (non-anthro)

South Asia: 
- high: dim7 (anthro, knowledge, causal, communicate, ..)
- low: dim1 (sky, chthonic, emotion, ...)

Southeast Asia:
- high: dim5 (minimal concept)
- low: dim0 (good knowledge, causal, communicate, ...)

Southwest Asia:
- high: dim2 (anthro/sky)
- low: dim3 (maximal without elite)

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

""" notes:
This looks like a mess; 
* down: dim2, dim3. 
* up: dim1, (dim0, dim6)
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
plt.ylim(0, 0.4)
plt.legend(title="Dimension")
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
