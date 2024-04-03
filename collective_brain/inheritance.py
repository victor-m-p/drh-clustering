"""
looking at inheritance for monitoring and shg.
only looking at groups for now.
only looking at pre-1600 for now.
only looking at parent="YES" for now.

NB: including inconsistent answers. 
"""

import numpy as np
import pandas as pd
import warnings
from fun import calculate_inheritance

warnings.filterwarnings(action="ignore", message="Mean of empty slice")

# 0. setup
question_group = "shg"

# 1. subset relations
from fun import select_relations

df_relations = pd.read_csv("data/spatiotemporal_overlap.csv")
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
df_values = pd.read_csv(f"../data/ML/{question_group}.csv")
df_values["entry_code"] = df_values.index  # for inconsistent answers

# select relations
df_relations = select_relations(
    df_relations=df_relations,
    df_values=df_values,
    entry_metadata=entry_metadata,
    subset_polls=[
        "Religious Group (v5)",
        "Religious Group (v6)",
    ],  # only in group polls
    subset_time=1600,  # only if overlap starts before 1600
)

"""
1. how do we treat NaN: 
for now we do not record anything for NaN.
i.e., there will just be a missing value for whether the culture inherited this.

2. how do we treat inconsistent answers:
we might say that the culture inherited 50%.
we could also ignore these for now. 

3. how do we treat multiple parents (e.g. YES, YES, NO): 
I think we will have to do something like comparing against all parents for each.
Then we will have to create some mean value aggreagation. 
Here we can ignore if there is NAN for a parent. 
"""


### 2. calculate inheritance ###
# run calculation
df_inheritance = calculate_inheritance(df_values, df_relations)

# drop rows that have all nan
feature_names = df_values.drop(
    columns=["entry_code", "entry_id", "weight"]
).columns.tolist()
df_inheritance = df_inheritance.dropna(subset=feature_names, how="all")

# then aggregate by (entry_id_to, entry_id_from)
# then we can drop (entry_code_to, entry_code_from)
df_inheritance = (
    df_inheritance.groupby(["entry_id_to", "entry_id_from"]).mean().reset_index()
)
df_inheritance = df_inheritance.drop(columns=["entry_code_from", "entry_code_to"])


""" calculate stickiness, inheritance(YES), inheritance(NO) 
Stickiness: p(NO|NO) + p(YES|YES) / p(YES|NO) + p(NO|YES)
Inheritance(YES): p(YES|YES) / p(NO|YES)
Inheritance(NO): p(NO|NO) / p(YES|NO)
"""


### 3. set-up inheritance(YES) and inheritance(NO) with mask ###
# for this we only use consistent values
def collapse_rows(df):
    # Function to check consistency and return appropriate value
    def process_group(column):
        unique_values = column.dropna().unique()
        if len(unique_values) > 1:
            return np.nan
        else:
            return column.iloc[0]

    # Group by 'entry_id' and apply the processing function to each group
    result_df = df.groupby("entry_id").agg(lambda x: process_group(x))

    return result_df.reset_index()


df_values_collapsed = collapse_rows(df_values)
df_values_collapsed = df_values_collapsed.drop(columns=["entry_code", "weight"])

# now merge this with inheritance on (id_from)
df_merged = pd.merge(
    df_inheritance,
    df_values_collapsed,
    left_on="entry_id_from",
    right_on="entry_id",
    suffixes=("", "_from"),
    how="inner",
)
feature_names_from = [f + "_from" for f in feature_names]
assert len(df_merged) == len(df_inheritance)


# now mask features
def mask_values(df_merged, df_inheritance, mask_value):
    df_merged = df_merged.sort_values(["entry_id_to", "entry_id_from"])
    df_inheritance = df_inheritance.sort_values(["entry_id_to", "entry_id_from"])
    df_inheritance_mask = df_inheritance.copy()
    for feature in feature_names:
        df_inheritance_mask[feature] = np.where(
            df_merged[feature + "_from"] == mask_value,
            np.nan,
            df_inheritance_mask[feature],
        )
    return df_inheritance_mask


df_inheritance_yes = mask_values(df_merged, df_inheritance, 0.0)
df_inheritance_no = mask_values(df_merged, df_inheritance, 1.0)


# calculate mean features
def calculate_mean_feature(df_inheritance, feature_var):
    df_inheritance_mean = df_inheritance.drop(columns="entry_id_from")
    df_inheritance_mean = (
        df_inheritance_mean.groupby("entry_id_to")
        .mean()
        .mean()
        .reset_index(name=feature_var)
    )
    return df_inheritance_mean


mean_yes = calculate_mean_feature(df_inheritance_yes, "mean_yes")
mean_no = calculate_mean_feature(df_inheritance_no, "mean_no")
mean_overall = calculate_mean_feature(df_inheritance, "mean_overall")

# merge and rename
mean_features = mean_yes.merge(mean_no, on="index", how="inner")
mean_features = mean_features.merge(mean_overall, on="index", how="inner")
mean_features = mean_features.rename(columns={"index": "related_question_id"})
mean_features["related_question_id"] = [
    int(q[1:]) for q in mean_features["related_question_id"]
]

### merge with questions for interpretability ###
shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
shg_answers = shg_answers[["question_short", "related_question_id"]].drop_duplicates()
mean_features = mean_features.merge(shg_answers, on="related_question_id", how="inner")
mean_features.sort_values("mean_yes")

### calculate baseline acceptance ###
"""
Only calculate for the entry_id in df_inheritance.
"""

entry_id_to_idx = df_inheritance["entry_id_to"].unique().tolist()
df_values_subset = df_values[df_values["entry_id"].isin(entry_id_to_idx)]
df_values_subset = df_values_subset.drop(columns=["entry_id", "entry_code", "weight"])
baseline_acceptance = df_values_subset.mean().reset_index(name="baseline_acceptance")
baseline_acceptance = baseline_acceptance.rename(
    columns={"index": "related_question_id"}
)
baseline_acceptance["related_question_id"] = [
    int(q[1:]) for q in baseline_acceptance["related_question_id"]
]

# merge, reorder, and sort
mean_features = mean_features.merge(
    baseline_acceptance, on="related_question_id", how="inner"
)
mean_features.sort_values("baseline_acceptance")

"""
Overall insights: 
- (of course) always very heritable when baseline acceptance is really high or low.
- surprising that so many features have ANY negative inheritance (yes or no).
"""


"""
Slightly surprising that this tracks so closely,
because you could also have something here where
something is really "inheritable" in the sense 
that it is just always NOT inherited (which would
give super low baseline acceptance, and super high inheritance).
We should probably check this on the other data actually. 
"""

## compare with theoretical expectation assuming no inheritance ##
theoretical_expectation = mean_features.copy()

# calculate theoretical expectation
theoretical_expectation = theoretical_expectation.rename(
    columns={"baseline_acceptance": "mean_yes_theory"}
)
theoretical_expectation["mean_no_theory"] = (
    1 - theoretical_expectation["mean_yes_theory"]
)
theoretical_expectation["mean_overall_theory"] = (
    theoretical_expectation["mean_yes_theory"] ** 2
    + theoretical_expectation["mean_no_theory"] ** 2
)

# calculate raw % increase
theoretical_expectation["mean_yes_delta"] = (
    theoretical_expectation["mean_yes"] - theoretical_expectation["mean_yes_theory"]
)
theoretical_expectation["mean_no_delta"] = (
    theoretical_expectation["mean_no"] - theoretical_expectation["mean_no_theory"]
)
theoretical_expectation["mean_overall_delta"] = (
    theoretical_expectation["mean_overall"]
    - theoretical_expectation["mean_overall_theory"]
)

# check results
theoretical_expectation.sort_values("mean_no_delta")

""" BASELINE DIFFERENCES: 
for monitoring:
- more "YES" inheritance:
    - conversion non-religionists (0.16)
    - shirking risk (0.09)
    - gossipping (0.08)
- more "NO" inheritance: 
    - conversion non-religionists (0.06)
    - non-lethal fighting (0.04)
- more "OVERALL" inheritance: 
    - conversion non-religionists (0.20)
    - personal hygiene (0.10)
    - sorcery (0.09)

for shg: 
- more "YES" inheritance
    - is unquestionably good (0.06)
    - permissible to worship other god (0.04)
- more "NO" inheritance
    - permissible to woship other god (0.04)
    - is anthropomorphic (0.01)
- more "OVERALL" inheritance: 
    - permissible to worship other god (0.13)
    - is sky deity (0.07)
    - is anthropomorphic (0.07)

NB: 
1. Overall very weak effects. 

2. We tend to get stronger "inheritance" for features that
are close to equally "YES/NO". Indicates that we have ceiling effect.

--> Let us consider differences in percent
--> e.g., such that 90-->95% is the same as 50-->75%
--> this will make the top-end more volatile though. 
"""


### calculate proportional change (bespoke) ###
def calculate_proportional_change(df, start_col, end_col):
    """
    Calculate the proportional change between two columns in a DataFrame,
    accounting for potential increases or decreases and adjusting for the
    distance to the edge of a 100-point scale.

    Parameters:
    - df: The pandas DataFrame containing the data.
    - start_col: The name of the column to use as the starting value.
    - end_col: The name of the column to use as the ending value.

    Example increases of 100%
    - (1, 2), (10, 20), (50, 75), (80, 90), (90, 95), ...

    Examples of decreases of 100%
    - (2, 1), (20, 10), (75, 50), (90, 80), (95, 90), ...

    Returns:
    - A Series with the calculated proportional change for each row.
    """

    def row_calculation(row):
        distance_to_edge = 100 - max(
            row[start_col], 100 - row[start_col], row[end_col], 100 - row[end_col]
        )
        space_used = row[end_col] - row[start_col]
        return space_used / distance_to_edge if distance_to_edge != 0 else 0

    return df.apply(row_calculation, axis=1)


theoretical_expectation["mean_yes_delta"] = calculate_proportional_change(
    theoretical_expectation, "mean_yes_theory", "mean_yes"
)
theoretical_expectation["mean_no_delta"] = calculate_proportional_change(
    theoretical_expectation, "mean_no_theory", "mean_no"
)
theoretical_expectation["mean_overall_delta"] = calculate_proportional_change(
    theoretical_expectation, "mean_overall_theory", "mean_overall"
)

theoretical_expectation.sort_values("mean_overall_delta")

""" PROPORTIONAL DIFFERENCES
for monitoring: 
- more "YES" inheritance
    - conversion non-religionists (0.31)
    - shirking risk (0.17)
    - gossipping (0.12)
- more "NO" inheritance
    - disrespect elders (0.21)
    - conversion non-religionists (0.12)
    - non-lethal fighting (0.11)
- more "OVERALL" inheritance
    - conversion non-religionists (0.39)
    - personal hygiene (0.18)
    - non-lethal fighting (0.15)

for shg: 
- more "YES" inheritance
    - is chthonic (0.26)
    - is monarch fused (0.23)
    - is monarch manifestation (0.14)
- more "NO" inheritance 
    - causal efficacy (1.7)
    - is anthropomorphic (0.32)
    - indirect causal efficacy (0.27)
- more "OVERALL" inheritance
    - permissible to worship other god (0.27)
    - is sky deity (0.15)
    - is anthropomorphic (0.12)

NB: does this make sense in any way?

In some sense we might read the "overall" inheritance as 
either "stickiness" or just as "does this feature split data
spatio-temporally" (i.e., perhaps permissible to worship other god
is one of the features that is most well predicted by time and space).

Something weird about e.g., very high increase in "NO" inheritance (causal efficacy)
but not having this in "OVERALL" inheritance change. Should we calculate the overall
inheritance change as the sum of "YES" and "NO"? 

We should probably also just consider whether the raw values that we have are any good.
Seems weird that any "inheritance" (of "YES" or "NO") would be really low.

For instance, inheritance of "NO" for "communicates with living" is <10%. 
This is less than the theoretical expectation even, so this seems weird. 
"""

### Sanity check for SHG ###
## look into "NO" for "communicates with living" (4858) ##
# first find all cases where an entry has a "NO" answer.
no_comm = df_values[df_values["Q4858"] == 0.0]["entry_id"].tolist()
# then find all cases where we have this as a parent:
no_comm_parent = df_inheritance[df_inheritance["entry_id_from"].isin(no_comm)]

## No --> Yes (n=59) ##
no_comm_flip = no_comm_parent[no_comm_parent["Q4858"] == 0.0]
no_comm_flip.sort_values("entry_id_to")
# Sadducees (848) No --> Matthew-James... (174) Yes
# Sadducees (848) No --> Qumran (176) Yes
# Achaemenid (424) No --> Hellenistic Uruk (354) Yes
# Sadducees (848) No --> Paul (355) Yes
# Achaemenid (424) No --> Classical Greek (361) Yes
# Manichaeism (1031) No --> Donatism (442) Yes
# Sadducees (848) No --> Roman Imperial (534) Yes
# Tamil Muslims (1570) No --> Veerashaivas (592) Yes
# Byzantine Christian (1694) --> Holy Trinity (676) Yes
# ...

## No --> No (n=5)
no_comm_stay = no_comm_parent[no_comm_parent["Q4858"] == 1.0]
no_comm_stay.sort_values("entry_id_to")
# Sethian Gnostic (893) No --> Theurgy (986) No
# Sething Gnostic (893) No --> Manichaeism (1031) No
# Theurgy (986) No --> Manichaeism (1031) No
# Chan Buddhism (1109) No --> LuWang School (1259) No
# Butonese Muslims (1283) No --> Buginese Muslims (1289) No

"""
This seems really weird. 
I really do not understand that we do not have more 
connected inheritance of the "No" feature. 
"""

### Figure out how to build "chains" ###


### biggest changes ###
df_entry_changes = df_inheritance.copy()
df_entry_changes["rowmean"] = df_entry_changes.drop(
    columns=["entry_id_from", "entry_id_to"]
).mean(axis=1)

## okay say with some threshold for nan ##
non_nan_count = df_entry_changes[feature_names].notna().sum(axis=1)
threshold = len(feature_names) / 2
subset_df = df_entry_changes[non_nan_count > threshold]

subset_df.sort_values("rowmean")

""" most radical shifts:
1133 (Religion in Greco-Roman Egypt) --> 848 (Sadducees) (agree 0%)
1133 (Religion in Greco-Roman Egypt) --> 893 (Sethian Gnostic) (agree 18%)
937 (Vestal Virgins) --> 893 (Sethian Gnostic) (agree 25%)
492 (Roman Divination) --> 986 (Theurgy) (agree 25%)
224 (Old Norse Fornsed) --> 2038 (Cathars, ... "Pure Christians") (agree 27%)
"""

### try to only do "closest" in time for ones where we have multiple ###
## NB: this surprisingly does not do a lot ##
df_inheritance_pairs = df_inheritance[["entry_id_from", "entry_id_to"]]
df_relations = df_relations.drop(columns=["entry_code_from", "entry_code_to"])
df_relations = df_relations.merge(
    df_inheritance_pairs, on=["entry_id_from", "entry_id_to"]
)

# need to get the starting year of the "from" entry
year_from = entry_metadata[["entry_id", "year_from"]].drop_duplicates()
year_from = year_from.rename(columns={"entry_id": "entry_id_from"})
df_relations = df_relations.merge(year_from, on="entry_id_from", how="inner")
df_relations.sort_values("entry_id_to")


# select latest year_from (i.e., closest to the "to" entry)
# if tie we pick at random
def select_max_random(group):
    max_overlap_start = group["overlap_start"].max()
    max_rows = group[group["overlap_start"] == max_overlap_start]
    if len(max_rows) > 1:
        return max_rows.sample(n=1)
    else:
        return max_rows


df_relations_closest = (
    df_relations.groupby("entry_id_to", as_index=False)
    .apply(select_max_random)
    .reset_index(drop=True)
)

# NB: also note here that this is only 184 rows.
df_relations_closest = df_relations_closest[["entry_id_from", "entry_id_to"]]


# Now inner merge on the previous df_inheritance
def merge_inheritance(df_inheritance, df_relations_closest):
    df_closest = df_inheritance.merge(
        df_relations_closest, on=["entry_id_from", "entry_id_to"], how="inner"
    )
    return df_closest


df_closest_overall = merge_inheritance(df_inheritance, df_relations_closest)
df_closest_yes = merge_inheritance(df_inheritance_yes, df_relations_closest)
df_closest_no = merge_inheritance(df_inheritance_no, df_relations_closest)

mean_yes_closest = calculate_mean_feature(df_closest_yes, "mean_yes_closest")
mean_no_closest = calculate_mean_feature(df_closest_no, "mean_no_closest")
mean_overall_closest = calculate_mean_feature(
    df_closest_overall, "mean_overall_closest"
)

# merge these
mean_features_closest = mean_yes_closest.merge(mean_no_closest, on="index", how="inner")
mean_features_closest = mean_features_closest.merge(
    mean_overall_closest, on="index", how="inner"
)
mean_features_closest = mean_features_closest.rename(
    columns={"index": "related_question_id"}
)
mean_features_closest["related_question_id"] = [
    int(q[1:]) for q in mean_features_closest["related_question_id"]
]
mean_features_comparison = mean_features.merge(
    mean_features_closest, on="related_question_id", how="inner"
)

# check it out
mean_features_comparison
