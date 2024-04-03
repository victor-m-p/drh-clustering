"""
VMP 2023-01-19:
Decisions: 
1. (year_from, year_to): earliest observed to latest observed. 
2. (region_id): region used for most questions per entry

Note: 
1.1: cold do the mode (year_from, year_to) over questions.
1.2: when analyzing specific questions use the (year_from, year_to) for that question.
2.1: could concatenate all regions for the entry when >1 region is used. 
2.1: this decision will affect auxilliary variables (e.g., sq_km)
"""

import pandas as pd
import numpy as np

# basic imports
df = pd.read_csv("../data/dump/raw_data.csv")
entity_tags = pd.read_csv("../data/dump/entity_tags.csv")
gis_regions = pd.read_csv("../data/dump/gis_regions.csv")

# select columns related to entry metadata
entry_metadata_cols = ["entry_id", "entry_name", "year_from", "year_to", "region_id"]
df_entries = df[entry_metadata_cols].drop_duplicates()

# 1. get the mode regions and mode timespans
from entries import mode_feature_by_entry

mode_region = mode_feature_by_entry(df, "entry_id", "region_id")
mode_region = mode_region.rename(columns={"unique": "unique_region"})


# 2. get the area associated with gis regions
from kml_functions import split_regions, calculate_gis_area

### NB: we should split this process into 2 steps:
### 1. get the meridian splits and save this
### 2. get the areas and save them.

assert len(gis_regions) == gis_regions["region_id"].nunique()
region_split_antimeridian = split_regions(gis_regions)
region_area = calculate_gis_area(region_split_antimeridian)
region_split_antimeridian.to_csv("../data/preprocessed/gis_metadata.csv", index=False)

# why do they become so big?
region_area = region_area[["region_id", "region_area", "region_type"]].drop_duplicates()

# insert nan for region area where there is no gis_region
region_area = region_area.groupby("region_id")["region_area"].sum()
region_area = region_area.reset_index(name="count")
region_area = region_area.rename(columns={"count": "region_area"})
region_overall = mode_region.merge(region_area, on="region_id", how="left")

# add entry_name back in
entry_name_id = df_entries[["entry_id", "entry_name"]].drop_duplicates()
region_overall = region_overall.merge(entry_name_id, on="entry_id", how="inner")
assert len(region_overall) == df_entries["entry_id"].nunique()

# get the region data that we need for most of the analysis
region_key_cols = region_overall[
    ["entry_id", "region_id", "unique_region", "region_area"]
].drop_duplicates()
assert len(region_key_cols) == df_entries["entry_id"].nunique()
assert region_key_cols["entry_id"].nunique() == df_entries["entry_id"].nunique()

# 3. take mode timespan
mode_timespan = mode_feature_by_entry(df, "entry_id", ["year_from", "year_to"])
mode_timespan = mode_timespan.rename(columns={"unique": "unique_timespan"})
assert len(mode_timespan) == df_entries["entry_id"].nunique()
assert mode_timespan["entry_id"].nunique() == df_entries["entry_id"].nunique()

# add entry_name back in
mode_timespan = mode_timespan.merge(entry_name_id, on="entry_id", how="inner")
mode_timespan.to_csv("../data/preprocessed/timespan_metadata.csv", index=False)

# 5. social scale
"""
NB: the question that we use for social scale does not appear to have 
a related question in the place poll 
"""

social_scale_question = df[df["question_name"].str.contains("The society to which")]

social_scale_question = (
    social_scale_question[social_scale_question["poll"] == "Religious Group (v6)"][
        "question_id"
    ]
    .unique()
    .tolist()[0]
)

answers = pd.read_csv("../data/preprocessed/answers.csv")
answers = answers[
    [
        "poll",
        "entry_id",
        "question_id",
        "question_name",
        "answer",
        "related_question_id",
    ]
].drop_duplicates()
answers_social_scale = answers[answers["related_question_id"] == social_scale_question]

from entries import unique_social_scale

answers_social_scale_unique = unique_social_scale(answers_social_scale)

# add entries to this
answers_social_scale_unique = entry_name_id.merge(
    answers_social_scale_unique, on="entry_id", how="left"
)
assert len(answers_social_scale_unique) == df_entries["entry_id"].nunique()
assert (
    answers_social_scale_unique["entry_id"].nunique()
    == df_entries["entry_id"].nunique()
)
answers_social_scale_unique = answers_social_scale_unique.sort_values(
    "entry_id", ascending=True
).reset_index(drop=True)

# save
answers_social_scale_unique.to_csv(
    "../data/preprocessed/social_scale_metadata.csv", index=False
)

# 6. expert/editor
mode_expert = mode_feature_by_entry(
    df[["entry_id", "expert_id"]], "entry_id", "expert_id"
)
mode_expert = mode_expert.merge(df, on=["entry_id", "expert_id"], how="inner")
mode_expert = mode_expert[["entry_id", "expert_id", "expert_name"]].drop_duplicates()
assert len(mode_expert) == df_entries["entry_id"].nunique()

mode_editor = mode_feature_by_entry(
    df[["entry_id", "editor_id"]], "entry_id", "editor_id"
)
mode_editor = mode_editor.merge(df, on=["entry_id", "editor_id"], how="inner")
mode_editor = mode_editor[["entry_id", "editor_id", "editor_name"]].drop_duplicates()
assert len(mode_editor) == df_entries["entry_id"].nunique()

mode_editor_expert = mode_expert.merge(mode_editor, on="entry_id", how="inner")
assert len(mode_editor_expert) == df_entries["entry_id"].nunique()

# 7. date created / modified
entry_dates = df[["entry_id", "date_created", "date_modified"]]

# Convert 'date_created' and 'date_modified' to datetime if they are not already
entry_dates["date_created"] = pd.to_datetime(entry_dates["date_created"])
entry_dates["date_modified"] = pd.to_datetime(entry_dates["date_modified"])

# Group by 'entry_id' and aggregate
entry_dates = entry_dates.groupby("entry_id").agg(
    earliest_date_created=("date_created", "min"),
    latest_date_modified=("date_modified", "max"),
)

# Reset index if you want 'entry_id' as a column
entry_dates = entry_dates.reset_index()
assert len(entry_dates) == df_entries["entry_id"].nunique()

# now merge everything
df_entries_clean = answers_social_scale_unique.merge(
    region_key_cols, on="entry_id", how="inner"
)
df_entries_clean = df_entries_clean.merge(
    mode_timespan, on=["entry_id", "entry_name"], how="inner"
)
df_entries_clean = df_entries_clean.merge(
    mode_editor_expert, on="entry_id", how="inner"
)
df_entries_clean = df_entries_clean.merge(entry_dates, on="entry_id", how="inner")
assert len(df_entries_clean) == df_entries["entry_id"].nunique()
assert df_entries_clean["entry_id"].nunique() == df_entries["entry_id"].nunique()
df_entries_clean = df_entries_clean.sort_values("entry_id", ascending=True).reset_index(
    drop=True
)

# add poll
poll = df[["entry_id", "poll"]].drop_duplicates()
assert len(poll) == df_entries["entry_id"].nunique()
assert poll["entry_id"].nunique() == df_entries["entry_id"].nunique()
df_entries_clean = df_entries_clean.merge(poll, on="entry_id", how="inner")
df_entries_clean["year_from"] = df_entries_clean["year_from"].astype(int)
df_entries_clean["year_to"] = df_entries_clean["year_to"].astype(int)
df_entries_clean.to_csv("../data/preprocessed/entry_metadata.csv", index=False)
