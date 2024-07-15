import numpy as np
import pandas as pd

# lets do just one feature
question_name = "conversion non-religionists"
question_group = "monitoring"
answers = pd.read_csv(f"../data/preprocessed/{question_group}_long.csv")
answers = answers[answers["question_short"] == question_name]

# only do weight = 1
answers = answers[answers["weight"] == 1]

# add time
entry_data = pd.read_csv("data/entry_data_subset.csv")
answers_time_space = answers.merge(entry_data, on="entry_id", how="inner")

#### plotting ####
from spatiotemporal_fun import plot_spatiotemporal, format_year, create_animation
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# make gis regions valid:
answers_time_space["gis_region"] = answers_time_space["gis_region"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(answers_time_space, geometry="gis_region")

# assign colors
color_mapping = {0: "tab:blue", 1: "tab:orange", np.nan: "tab:gray"}
gdf["color_code"] = gdf["answer_value"].map(color_mapping)


# time cutoff
# maybe do time-slices instead
def expand_temporal_window(id_meta, time_window):
    min_start_year = id_meta["year_from"].min()
    max_end_year = id_meta["year_to"].max()

    start_boundary = (min_start_year // time_window) * time_window - time_window
    end_boundary = (max_end_year // time_window + 1) * time_window

    expanded_data = []

    for index, row in id_meta.iterrows():
        for year in range(start_boundary, end_boundary, time_window):
            if year + (time_window - 1) < row["year_from"] or year > row["year_to"]:
                continue

            expanded_data.append(
                {
                    "entry_id": row["entry_id"],
                    "time_slice_start": year,
                }
            )

    expanded_df = pd.DataFrame(expanded_data)
    return expanded_df


# limit to pre-1700 and expand time
gdf_expanded = expand_temporal_window(gdf, 100)
gdf = gdf.merge(gdf_expanded, on="entry_id", how="inner")
unique_time_cutoff = gdf["time_slice_start"].unique()
unique_time_cutoff = np.sort(unique_time_cutoff)

# zoom dictionary
zoom_dict = {
    "xmin": -20,
    "xmax": 140,
    "ymin": -40,
    "ymax": 80,
}

time_slice_path = "spatiotemporal_png"
for time in unique_time_cutoff:
    time_format = format_year(time)
    plot_spatiotemporal(
        gdf=gdf,
        time=time,
        centroid=True,
        active_geometry="gis_region",
        alpha=0.2,
        color_column="color_code",
        zoom=zoom_dict,
        outpath=f"{time_slice_path}/{time_format}.png",
    )

# mp4
animation_dir = "spatiotemporal_animation"
create_animation(format="mp4", inpath=time_slice_path, outpath=animation_dir)
