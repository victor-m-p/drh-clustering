import numpy as np
import pandas as pd
from spatiotemporal_fun import plot_spatiotemporal, format_year, create_animation
import geopandas as gpd
from shapely import wkt
import os


# convenience functions
def map_to_color_code(row):
    if row["answer_value"] == 1 and row["christian_tradition"]:
        return "tab:orange"
    elif row["answer_value"] == 1 and not row["christian_tradition"]:
        return "tab:red"
    elif row["answer_value"] == 0 and row["christian_tradition"]:
        return "tab:green"
    elif row["answer_value"] == 0 and not row["christian_tradition"]:
        return "tab:blue"


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


# zoom dictionary
zoom_dict = {
    "xmin": -20,
    "xmax": 140,
    "ymin": -40,
    "ymax": 80,
}

# setup
png_path = "spatiotemporal_png"
ani_path = "spatiotemporal_animation"
temporal_slice = 100

# lets do just one feature
question_shorthands = ["conversion", "unquestionably"]

# just do 1 for now
question_short = "conversion"

# read data
answers = pd.read_csv(f"data/{question_short}_metrics.csv")

# add time
entry_data = pd.read_csv("data/entry_data_subset.csv")
answers_time_space = answers.merge(entry_data, on="entry_id", how="inner")

# make gis regions valid:
answers_time_space["gis_region"] = answers_time_space["gis_region"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(answers_time_space, geometry="gis_region")

# assign colors
gdf["color_code"] = gdf.apply(map_to_color_code, axis=1)

# expand time
gdf_expanded = expand_temporal_window(gdf, temporal_slice)
gdf = gdf.merge(gdf_expanded, on="entry_id", how="inner")
unique_time_cutoff = gdf["time_slice_start"].unique()
unique_time_cutoff = np.sort(unique_time_cutoff)

# create pngs
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
        outpath=f"{png_path}/{time_format}.png",
    )

# create animation
create_animation(
    format="mp4",
    inpath=ani_path,
    outpath="spatiotemporal_animation",
    outname=f"{question_short}_animation",
)

# loop over questions
for question_short in question_shorthands:

    # read data
    answers = pd.read_csv(f"data/{question_short}_metrics.csv")

    # add time
    entry_data = pd.read_csv("data/entry_data_subset.csv")
    answers_time_space = answers.merge(entry_data, on="entry_id", how="inner")

    # make gis regions valid:
    answers_time_space["gis_region"] = answers_time_space["gis_region"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(answers_time_space, geometry="gis_region")

    # assign colors
    gdf["color_code"] = gdf.apply(map_to_color_code, axis=1)

    # expand time
    gdf_expanded = expand_temporal_window(gdf, temporal_slice)
    gdf = gdf.merge(gdf_expanded, on="entry_id", how="inner")
    unique_time_cutoff = gdf["time_slice_start"].unique()
    unique_time_cutoff = np.sort(unique_time_cutoff)

    # create pngs
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
            outpath=f"{png_path}/{time_format}.png",
        )

    # create animation
    create_animation(
        format="mp4",
        inpath=ani_path,
        outpath="spatiotemporal_animation",
        outname=f"{question_short}_animation.mp4",
    )

    # delete all PNG files in spatiotemporal_png folder
    # for filename in os.listdir(png_path):
    #    file_path = os.path.join(png_path, filename)
    #    os.remove(file_path)
