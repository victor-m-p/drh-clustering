import numpy as np
import pandas as pd

spatiotemporal_overlap = pd.read_csv("data/spatiotemporal_overlap.csv")

# lets do just one feature
question_name = "conversion non-religionists"
question_group = "monitoring"
answers = pd.read_csv(f"../data/preprocessed/{question_group}_long.csv")
answers = answers[answers["question_short"] == question_name]

# only do weight = 1
answers = answers[answers["weight"] == 1]

# add time
entry_data = pd.read_csv("../data/raw/entry_data.csv")
temporal_data = entry_data[["entry_id", "year_from", "year_to"]]
answers_time = answers.merge(temporal_data, on="entry_id", how="inner")

assert len(answers_time) == len(answers)

# add space
region_data = pd.read_csv("../data/raw/region_data.csv")
region_data = region_data[region_data["gis_region"].notna()]
region_data = region_data[["region_id", "world_region", "gis_region"]].drop_duplicates()
entry_data = entry_data[["entry_id", "region_id"]].drop_duplicates()
space_data = entry_data.merge(region_data, on="region_id", how="inner")
answers_time_space = answers_time.merge(space_data, on="entry_id", how="inner")

#### plotting ####
from spatiotemporal_fun import plot_spatiotemporal, format_year, create_animation
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# make gis regions valid:
answers_time_space["geometry"] = answers_time_space["gis_region"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(answers_time_space, geometry="geometry")

# assign colors
color_mapping = {0: "tab:blue", 1: "tab:orange", np.nan: "tab:gray"}
gdf["color_code"] = gdf["answer_value"].map(color_mapping)

# time cutoff
gdf = gdf[gdf["year_from"] < 1700]
time_cutoff = gdf["year_from"].sort_values().to_numpy()
time_slice_path = "spatiotemporal_png"

for time in time_cutoff:
    time_format = format_year(time)
    plot_spatiotemporal(
        gdf=gdf,
        time=time,
        centroid=True,
        active_geometry="geometry",
        alpha=0.2,
        color_column="color_code",
        zoom=False,
        outpath=f"{time_slice_path}/{time_format}.png",
    )

# mp4
animation_dir = "spatiotemporal_animation"
create_animation(format="mp4", inpath=time_slice_path, outpath=animation_dir)
