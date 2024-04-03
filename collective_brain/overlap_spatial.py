import pandas as pd
import geopandas as gpd
from shapely import wkt
from fun import find_spatial_overlaps  # the main function

# load data
entry_metadata = pd.read_csv("../data/preprocessed/entry_metadata.csv")
gis_metadata = pd.read_csv("../data/preprocessed/gis_metadata.csv")

# find region overlap
gis_metadata["geometry"] = gis_metadata["geometry"].apply(wkt.loads)
gis_metadata = gpd.GeoDataFrame(gis_metadata, geometry="geometry")
region_overlap = find_spatial_overlaps(gis_metadata)

# merge back with entry metadata
entry_metadata = entry_metadata[["entry_id", "region_id"]]
region_overlap = entry_metadata.merge(region_overlap, on="region_id", how="inner")

# rename columns (it is not really from-to since symmetric but will make downstream easier)
region_overlap = region_overlap.rename(
    columns={
        "entry_id": "entry_id_from",
        "region_id": "region_id_from",
        "region_overlap": "region_id_to",
    }
)

entry_metadata = entry_metadata.rename(
    columns={"region_id": "region_id_to", "entry_id": "entry_id_to"}
)
region_overlap = entry_metadata.merge(region_overlap, on="region_id_to", how="inner")

# save
region_overlap.to_csv("data/spatial_overlap.csv", index=False)
