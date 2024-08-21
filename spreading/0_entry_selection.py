"""
2023-07-17 VMP
1. select entries that have relevant answers
2. match christianity tags 
3. select world regions (excluding global)
"""

import pandas as pd

# load
entry_data = pd.read_csv("../data/raw/entry_data.csv")
answers_subset = pd.read_csv("../data/preprocessed/answers_subset.csv")
answers_subset = answers_subset["entry_id"].unique()

### only the entries that have relevant data ###
entry_data = entry_data[entry_data["entry_id"].isin(answers_subset)]

### fix errors in the data ###
entry_id = 1429
end_year = -1700

entry_data.loc[entry_data["entry_id"] == entry_id, "year_to"] = end_year

### assign christianity ###
entry_tags = pd.read_csv("../data/raw/entity_tags.csv")

### christian tags ###
christian_tags = [
    18,  # Christian Traditions
    774,  # Early Christianity
    775,  # Early Christianity
    915,  # Evangelicalism
    971,  # Methodism
    984,  # Medieval Christianity
    996,  # Roman Catholic
    999,  # Catholic
    1006,  # Christian Restorationism
    1014,  # Christianity of the Global south
    1015,  # Born Again Christianity
    1030,  # American Christianity
    1031,  # Pentecostal
    1032,  # Protestantism
    1169,  # Early Christian Monasticism in Egypt
    1377,  # Christian monasticism
    1424,  # Christian Theology
    1570,  # Christianity
    1573,  # Christian
    1575,  # Christianity
    43608,  # Celtic Christianity
    43643,  # Orthodox Christianity
]

christian_entries = (
    entry_tags[
        (entry_tags["entrytag_id"].isin(christian_tags))
        | (entry_tags["parent_entrytag_id"].isin(christian_tags))
    ]["entry_id"]
    .unique()
    .tolist()
)

# christian traditions
entry_tags["christian_tradition"] = entry_tags["entry_id"].isin(christian_entries)
entry_tags = entry_tags[["entry_id", "christian_tradition"]].drop_duplicates()

# merge with entry data
entry_data = entry_data.merge(entry_tags, on="entry_id", how="inner")
entry_data = entry_data[
    [
        "entry_id",
        "entry_name",
        "year_from",
        "year_to",
        "region_id",
        "christian_tradition",
    ]
]

### region data ###
region_data = pd.read_csv("../data/raw/region_data.csv")
region_data = region_data[["region_id", "world_region", "gis_region"]].drop_duplicates()
region_data = region_data[region_data["gis_region"].notna()]

# subset world regions (old world)
world_regions = [
    "Europe",
    "East Asia",
    "Southwest Asia",
    "South Asia",
    "Southeast Asia",
    "Central Eurasia",
    "Africa",
]
region_data = region_data[region_data["world_region"].isin(world_regions)]

### some regions are crazy large (global)--remove them ###
import geopandas as gpd
from shapely import wkt

region_data["gis_region"] = region_data["gis_region"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(region_data, geometry="gis_region")

# for region area we have to reproject #
gdf.set_crs("EPSG:4326", inplace=True)
gdf.to_crs("+proj=cea", inplace=True)
gdf["area_sq_km"] = gdf["gis_region"].area / 10**6
gdf = gdf[gdf["area_sq_km"] < 2.5e7]  # remove global entries
gdf = gdf[["region_id", "area_sq_km"]]

# merge with region data and then entry data
region_data = region_data.merge(gdf, on="region_id", how="inner")

### merge inner with entry data ###
entry_data = entry_data.merge(region_data, on="region_id", how="inner")

# only entries that start before 1600 #
entry_data = entry_data[entry_data["year_from"] < 1600]
entry_data.to_csv("data/entry_data_subset.csv", index=False)
