import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#### setup ####
c = 8  # minimize BIC
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
dim0: minimal concept (0.22): highest in rituals, norms, oaths, ...
dim1: maximal concept (0.96): lowest in taboo, hygiene, sex, ...
dim2: maximal_concept (0.89): lowest in hygiene, risk, taboo, ...
dim3: maximal concept (0.86): lower in: risk, hygiene, conversion non-rel, ...
dim4: medium concept (0.74): lowest in murder, conversion, fighting, ...
dim5: medium concept (0.57): lowest in risk, conversion, gossiping, ... (highest in murder, oaths, ritual)
dim6: maximal concept (0.99): lowest in risk, conversion, fairness, ...
dim7: maximal concept (0.86): lowest in conversion, risk, sorcery, ...
"""

df_theta.sort_values("question_mean")

"""
generally most common features: 
* performance of rituals
* ritual observance
* honouring oaths
* prosocial norm adherence
* lying

generally least common features: 
* shirking risk
* conversion non-religionists
* personal hygiene
* non-lethal fighting
* gossiping

exciting thing potentially: 
* from minimal concept --> medium concept --> full concept
* would be interesting to know which cases have parent == Yes but all answers No
* do we learn anything additional about cultural packages?
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
entry_dim.sort_values("dim7", ascending=False).head(5)
shg_answers[shg_answers["entry_id"] == 841]

""" Examples in each dimensions: 

dim0 (minimal concept with max. 1 property)
1852 (Communion Letters by Whitley...): NAN for conversion.
1158 (Early Daoist text...): Yes prosocial norm adherence.
1044 (Han Imperial Cult...): Nan (field doesn't know) for ritual performance, Yes for ritual observance.
1847 (Arthasastra): Yes to prosocial norm adherence, NaN for taboos.
NB: many of these are texts so might not reflect group not having features.

dim1: (generally "YES" with only "murder other polities" as No)
1650 (Al-Muqaddima d'Abd Al...): No to murder other polities.
1928 (Gathering of the messenger of God...): No to murder other polities.
931 (Jesuits in Britain): No to prosocial norm and taboos
1309 (Circumcellions): No to murder other polities, hygiene, some nan.

dim2: (generally "YES" without rituals)
879 (Free Methodist Church): No to rituals, hygiene, taboos.
953 (Sachchai): No to rituals, hygiene, taboos.
950 (Religious society of friends): No to rituals.
968 (Anabaptist Mennonites): No rituals, hygiene, sorcery, 

dim3: (generally "YES" but does not care about elders and some others)
914 (Tariqa Shadhiliyya): No to gossip, elders, lazy, 
894 (Universal Fellowship...): No to hygiene, elders, lazy, taboo
1013 (Estado da India Renegades...): No to hygiene, fairness, gossip, elders, non-lethal fighting (nan lazy)
1588 (In the Shade of the Qur'an): No to elders, non-lethal fighting.

dim4: (generally "YES" but without murder, conversion, fighting)
1791 (Qadiria a Bagdad...): no conversion and murder (co-rel., other rel.)
472 (Karma Kagyo or Kamtsang...): no conversion, taboo, mutder (all) and fighting
1904 (L'ordre Qadiri en Tunisie...): no conversion, muder (co-rel., other rel.)
1683 (Book of Leviticus): no conversion, murder (all), and a few other.
NB: seems like many of these are text as well 

dim5: (generally very MIXED, always with rituals, murder, prosocial norms)
928: (Ghost Dance Movement...): has rituals, murder, prosocial (incl. lying, oaths, etc.)
1993 (Ancient Boeotians): has rituals, murder, prosocial (incl. oaths, taboos, etc.)
1129 (Ancient Thessalians): has rituals, murder, prosocial (incl. taboo, oaths, etc.)
2009 (Ancient Arcadians): has rituals, murder, prosocial (incl. taboo, oaths, etc.)
632 (Local Religion at Selinous): has rituals, murder, prosocial (incl. taboo, oaths, etc.)
NB: seems that core is rituals, murder, prosocial norms (some are mixed e.g. taboo, lying, etc.)

dim6: (The "maximal" cultural package)
2116 (Qadiriyyah Movement...): Yes to all
1652 (Le Livre de al-Ibana...): Yes to all
1654 (Le Parti du Movement...): Yes to all
1708 (Al-Ibadia): Yes to all

dim7: (Generally "Yes" with less taboo?)
960 (Bon): No conversion, lazy, sex, lying
1618 (Diya'u al-Ta'aweel fee..): No taboo, sex, sorcery, fighting
1811 (Kitab Qasidat...): No sorcery, fighting, sex, taboo
841 (Sa skya): No conversion, lazy, sex.
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
- high: dim1 (maximal) lowest taboo, hygiene, sex)
- low: dim0 (minimal) highest in rituals, norms, oaths. 

Central Eurasia: 
- high: dim6 (maximal) lowest in risk, conversion, fairness.
- low: dim0 (minimal) see above

East Asia:
- high: dim0 (minimal) see above
- low: dim4 (medium concept) lowest in murder, conversion, fighting

Europe: 
- high: dim0 (minimal) see above
- low: dim1 (maximal) see above

North America:
- high: dim2 (maximal): lowest in hygiene, risk, taboo
- low: dim7 (maximal): lowest in conversion, risk, sorcery

Oceania-Australia: 
- high: dim0 (minimal) see above
- low: dim4 (medium) see above

South America: 
- high: dim7 (maximal) see above
- low: dim4 (medium) see above

South Asia: 
- high: dim5 (medium) lowest in risk, conversion, gossip
- low: dim0 (minimal) see above

Southeast Asia:
- high: dim4 (medium) see above
- low: dim5 (medium) see above

Southwest Asia:
- high: dim0 (minimal) see above
- low: dim1 (maximal) see above

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
plt.ylim(0, 0.4)
plt.legend(title="Dimension")
plt.tight_layout()
plt.show()

""" of note: 
1. Clearly very limited data before -2000.
2. dim0 (minimal) clearly just dies from -500 to current.
3. dim5 (rituals, murder, prosoc) also collapses from -800 to current.
4. dim1 ("YES" without murder other polities) rises steadily from -500 to current.
5. dim6 (maximal concept) also strong rise (especially around 800).

Question is whether any of this is interesting / makes sense, and how we make it compelling.
There could be a story about evolution of cultural packages; 
potentially from minimal concepts (what is typically present there) to more maximal concepts.
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
--> dim4 (without murder, conversion, fighting) is most "small scale". 
--> dim0 (most minimal concept) is second-most "small scale"
--> dim5 (mixed but always with rituals, murder, prosocial) is most "large scale"
--> dim7 (maximal concept with less taboo) is second-most large scale

2. NB: we have variation in missingness and inconsistency across dimensions.
--> by inconsistency I mean coded as both large-scale and small-scale.
--> we should look into these cases as well as the "other" answers, for instance:
256: Etruscan Religion
479: Mesopotamian city-states
1805: Wahhabisme
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
1. Notable that nothing is negatively correlations. 
Suggests that the first distinction we should make is between "maximality" and "minimality" of concept.
This is also evident from the cultural packages that we have found: 
e.g., dim0 (minimal) and dim6 (maximal). 

2. With that said, there are some strong clusters: 
2.1. ritual observance and performance is its own thing 
2.2. disrespecting elders, property crimes, lying is a cluster. 
2.3. muder coreligionists, murder other religions, murder other polities is a cluster.

3. Broader cluster of related beliefs and some that are more independent: 
--> related: elders, property, lying, lazy, gossip, econ. fairness, sorcery, fighting, sex, murder.
--> distinct: taboo, rituals, prosocial norms, shirking risk, conversion. 
"""

# 5. relative numbers
dim = "dim7"
df_theta["relative_difference"] = df_theta[dim] - df_theta["question_mean"]
df_temporary = df_theta[["question_short", dim, "question_mean", "relative_difference"]]
df_temporary.sort_values("relative_difference")

"""
dim0 (0.22):
Has less of everything than average.
Really low murder, close to average on rituals (more than 50%)
--> less: murder (-0.81, -0.77, -0.71), gossip (-0.73)
--> more: rituals (-0.13, -0.19), taboo (-0.38)

dim1 (0.96):
Has more of everything (except taboo) than average:
Relatively high in the ones that are rare (ceiling effect of 100%)
--> less: taboo (-0.04), prosocial norms (0.02)
--> more: shirking risk (0.45), conversion (0.43)

dim2 (0.89): 
--> less: hygiene (-0.24), rituals (-0.17, -0.15)
--> more: non-lethat fighting (0.30), murder (0.24, 0.23, 0.17)

dim3: 
--> less: shirking risk (-0.23), disrespect elders (-0.05)
--> more: murder (0.24, 0.16, 0.15), sorcery (0.23), sex (0.2)

dim4: 
--> less: murder (-0.76, -0.67, -0.35) and conversion (-0.27)
--> more: hygiene (0.22), shirking risk (0.2)

dim5: 
--> less: gossip (-0.58), shirking risk (-0.55), conversion (-0.48)
--> more: murder coreligionists (0.16), honor oaths (0.04)

dim6: 
Has more of everything than average 
--> less: rituals (0.05, 0.06), oaths (0.07)
--> more: shirking risk (0.4), conversion non-religionists (0.39)

dim7: 
--> less: conversion non-rel. (-0.29), sorcery (-0.09), taboo (-0.05)
--> more: gossip (0.27), hygiene (0.25), murder (0.24, 0.23, 0.14)
"""

"""
Future directions: 
* (validation): Impact of "Text" and number of dimensions
* (validation): spatio-temporal weighting? (currently no). 
* change-point detection (where are the break-points?)
* cultural transmission and universality. 
* ...
"""
