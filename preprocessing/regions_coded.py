import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from shapely import wkt
import pygeos
from shapely.ops import nearest_points

# Countries and World Regions
countries_gdf = gpd.read_file("countries.gpkg")
world_regions = pd.read_csv("../data/raw/world_regions.csv")
countries_regions = countries_gdf.merge(world_regions, on="iso_a3", how="left")

### Wrangle our previous GIS data
gis_metadata = pd.read_csv("../data/preprocessed/gis_metadata.csv")
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
entry_metadata = entry_metadata.merge(gis_metadata, on="region_id", how="inner")
entry_metadata = entry_metadata[
    ["entry_id", "entry_name", "region_id", "geometry"]
].drop_duplicates()
entry_gis_complete = entry_metadata[entry_metadata["geometry"].notnull()]
entry_gis_complete["geometry"] = entry_gis_complete["geometry"].apply(wkt.loads)
entry_gis_gdf = gpd.GeoDataFrame(entry_gis_complete, geometry="geometry")
entry_gis_gdf = entry_gis_gdf.set_crs("EPSG:4326")

### Find intersections
intersection = gpd.overlay(countries_regions, entry_gis_gdf, how="intersection")

### Find the ones that do not have overlap
non_overlapping = entry_gis_gdf[
    ~entry_gis_gdf["entry_id"].isin(intersection["entry_id"])
]

countries_regions_pygeos = pygeos.from_shapely(countries_regions["geometry"])
non_overlapping_pygeos = pygeos.from_shapely(non_overlapping["geometry"])

# Initialize an empty column for storing the closest country's index
non_overlapping["closest_country_idx"] = np.nan

# Iterate over non_overlapping geometries to find the closest country
for idx, geometry in enumerate(non_overlapping_pygeos):
    # Calculate distances to all countries and find the index of the minimum
    distances = pygeos.distance(geometry, countries_regions_pygeos)
    closest_country_idx = np.argmin(distances)
    # Store the index of the closest country
    non_overlapping.iloc[
        idx, non_overlapping.columns.get_loc("closest_country_idx")
    ] = closest_country_idx

# Map the closest country's info back to the non_overlapping DataFrame
# This step depends on what information you want to carry over (e.g., country name)
non_overlapping["country"] = non_overlapping["closest_country_idx"].map(
    countries_regions["name"]
)

### prepare merge with countries_regions
# prepare countries regions
countries_regions = intersection[
    ["Country", "World.Region", "entry_id", "entry_name", "region_id"]
].drop_duplicates()
countries_regions = countries_regions.rename(
    columns={"World.Region": "world_region", "Country": "country"}
)
countries_regions["has_country"] = True
countries_regions = countries_regions.dropna()
countries_wr = countries_regions[["country", "world_region"]].drop_duplicates()

# prepare non-overlapping
non_overlapping = non_overlapping[
    ["entry_id", "entry_name", "country", "region_id"]
].drop_duplicates()
non_overlapping = non_overlapping.merge(countries_wr, on="country", how="left")

# fix remaining non-overlapping
non_overlapping.loc[non_overlapping["entry_name"] == "Trukese", "world_region"] = (
    "Oceania-Australia"
)

# now merge them
countries_regions["has_country"] = True
non_overlapping["has_country"] = False
countries_regions = pd.concat([countries_regions, non_overlapping])

# fix the last records (France and previous France I believe)
entries_missing = ~entry_metadata["entry_id"].isin(countries_regions["entry_id"])
entries_missing = entry_metadata[entries_missing]
entries_fixed = pd.DataFrame(
    {
        "entry_id": [610, 1657, 1659, 1701],
        "world_region": ["Africa", "Europe", "Europe", "Europe"],
        "country": ["Somalia", "France", "France", "France"],
    }
)
entries_fixed = entries_fixed.merge(entries_missing, on="entry_id", how="inner")
entries_fixed = entries_fixed.drop(columns="geometry")
entries_fixed["has_country"] = True

### merge this in
countries_regions = pd.concat([countries_regions, entries_fixed])
countries_regions["entry_id"].nunique() == entry_metadata["entry_id"].nunique()
countries_regions.to_csv("../data/preprocessed/regions_coded.csv", index=False)

### Check some cases:
# Church of Jesus Christ: we have correct
# Tiwi: we have correct
# Wesleyanism: we have correct
# Generally: seems like our approach works better.
