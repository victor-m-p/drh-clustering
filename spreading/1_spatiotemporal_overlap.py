"""
2024-07-17

This is the document where we could consider calculating % overlap in 
- space (polygon % overlap)
- time (time % overlap)
"""

import pandas as pd
from fun import find_temporal_overlaps, find_spatial_overlaps
import geopandas as gpd
from shapely import wkt

# load
entry_metadata = pd.read_csv("data/entry_data_subset.csv")
entry_metadata_year = entry_metadata[["entry_id", "year_from", "year_to"]]

### temporal overlaps ###
temporal_overlap = find_temporal_overlaps(entry_metadata_year)

### spatial overlaps ###
gis_metadata = pd.read_csv("../data/raw/region_data.csv")
gis_metadata = gis_metadata[~gis_metadata["gis_region"].isna()]

# find region overlap
gis_metadata["geometry"] = gis_metadata["gis_region"].apply(wkt.loads)
gis_metadata = gpd.GeoDataFrame(gis_metadata, geometry="geometry")
spatial_overlap = find_spatial_overlaps(gis_metadata)  # takes a bit

# merge back with entry metadata
entry_metadata_space = entry_metadata[["entry_id", "region_id"]].drop_duplicates()
spatial_overlap = entry_metadata_space.merge(
    spatial_overlap, on="region_id", how="inner"
)

# rename columns (it is not really from-to since symmetric but will make downstream easier)
spatial_overlap = spatial_overlap.rename(
    columns={
        "entry_id": "entry_id_from",
        "region_id": "region_id_from",
        "region_overlap": "region_id_to",
    }
)

entry_metadata_space = entry_metadata_space.rename(
    columns={"region_id": "region_id_to", "entry_id": "entry_id_to"}
)
spatial_overlap = entry_metadata_space.merge(
    spatial_overlap, on="region_id_to", how="inner"
)

### combine ###
df_overlap = spatial_overlap.merge(
    temporal_overlap, on=["entry_id_from", "entry_id_to"], how="inner"
).sort_values("overlap_start")

### overlap christianity ###
entry_metadata_christianity = entry_metadata[["entry_id", "christian_tradition"]]
entry_metadata_from = entry_metadata_christianity.rename(
    columns={
        "entry_id": "entry_id_from",
        "christian_tradition": "christian_tradition_from",
    },
)
entry_metadata_to = entry_metadata_christianity.rename(
    columns={
        "entry_id": "entry_id_to",
        "christian_tradition": "christian_tradition_to",
    },
)

df_overlap = df_overlap.merge(entry_metadata_from, on="entry_id_from", how="inner")
df_overlap = df_overlap.merge(entry_metadata_to, on="entry_id_to", how="inner")

# save
df_overlap.to_csv("data/spatiotemporal_overlap.csv", index=False)
