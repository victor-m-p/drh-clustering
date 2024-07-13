import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def find_spatial_overlaps(gdf):
    overlaps = gpd.sjoin(gdf, gdf, how="inner", op="intersects")

    # Filter out self-joins (where a region is joined with itself)
    overlaps = overlaps[overlaps["region_id_left"] != overlaps["region_id_right"]]

    # Create a result DataFrame with required format
    result = overlaps[["region_id_left", "region_id_right"]]

    # Drop duplicates because the spatial join may find multiple intersections for the same region pairs
    result = result.drop_duplicates().reset_index(drop=True)

    # Rename columns to the desired output format
    result.rename(
        columns={"region_id_left": "region_id", "region_id_right": "region_overlap"},
        inplace=True,
    )

    # Duplicate the data to have both (X, Y) and (Y, X)
    result_reversed = result.rename(
        columns={"region_id": "region_overlap", "region_overlap": "region_id"}
    )
    final_result = pd.concat([result, result_reversed], ignore_index=True)

    # Drop duplicates again, in case reversing the pairs has created any
    final_result = final_result.drop_duplicates().reset_index(drop=True)

    return final_result


def find_temporal_overlaps(df):
    df_sorted = df.sort_values(by="year_from")

    # Find overlapping periods using a more efficient method with sorting
    overlaps = []
    active_intervals = []

    for i, current_row in df_sorted.iterrows():
        # Check current row with all active intervals for overlaps
        for active in active_intervals:
            if current_row["year_from"] <= active[1]["year_to"]:
                # There is an overlap
                overlaps.append(
                    (
                        active[1]["entry_id"],
                        current_row["entry_id"],
                        current_row["year_from"],
                    )
                )

        # Add the current row to the list of active intervals
        active_intervals.append((i, current_row))

        # Remove intervals from active list that ended before the current row's start
        active_intervals = [
            active
            for active in active_intervals
            if active[1]["year_to"] >= current_row["year_from"]
        ]

    df_overlap = pd.DataFrame(
        overlaps, columns=["entry_id_from", "entry_id_to", "overlap_start"]
    )
    return df_overlap


def plot_two_regions(gdf, region_id1, region_id2, area_threshold=0.1):
    """
    Plot the geometries of two regions on a world map. If a region is smaller than a threshold, plot its centroid instead.

    Parameters:
    gdf: GeoDataFrame containing the 'geometry' and 'region_id' columns.
    region_id1, region_id2: The region IDs of the two regions to visualize.
    area_threshold: Minimum area threshold to decide whether to plot the region's geometry or its centroid.
    """
    # Load a low-resolution world map
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    # Filter the GeoDataFrame for the two regions
    region1 = gdf[gdf["region_id"] == region_id1]
    region2 = gdf[gdf["region_id"] == region_id2]

    # Start the plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    # Plot the world map
    world.plot(ax=ax, color="lightgrey")

    # Function to plot region or its centroid based on area size
    def plot_region_or_centroid(region, ax, color):
        if region.geometry.iloc[0].area < area_threshold:
            # Plot centroid if region is small
            region_centroid = region.centroid
            region_centroid.plot(
                ax=ax, color=color, marker="o", markersize=100
            )  # Adjust markersize as needed
        else:
            # Plot region's geometry if it's above the threshold
            region.plot(ax=ax, color=color, alpha=0.5)

    # Plot the geometries of the two regions or their centroids
    plot_region_or_centroid(region1, ax, "tab:blue")
    plot_region_or_centroid(region2, ax, "tab:red")

    # Set title and axis visibility
    ax.set_title(f"Regions {region_id1} and {region_id2}")
    ax.axis("off")


### functions for inheritance ###
def array_overlap(arr1, arr2):
    # Check that the arrays are of the same length
    if len(arr1) != len(arr2):
        raise ValueError("Arrays must have the same length")

    # Create an empty array with the same length as the input arrays, filled with nan
    result = np.full(arr1.shape, np.nan)

    # Set to 1.0 where both arrays have the same value and neither is nan
    same_value = (arr1 == arr2) & (~np.isnan(arr1) & ~np.isnan(arr2))
    result[same_value] = 1.0

    # Set to 0.0 where values are different and neither is nan
    different_value = (arr1 != arr2) & (~np.isnan(arr1) & ~np.isnan(arr2))
    result[different_value] = 0.0

    # The rest of the result will naturally be nan where either of the input arrays has nan
    return result


def calculate_inheritance(df_values, df_relations):
    """
    calculate inheritance of features from one entry to another.
    values for each entry are given as a bitstring (df_values).
    relations between entries are given as a dataframe (df_relations).
    """

    # get unique entry codes:
    unique_entry_code_to_idx = df_relations["entry_code_to"].unique()

    # set up lists for inheritance and metadata
    inheritance_list = []
    metadata_list = []

    # loop over the unique "to" idx
    for entry_to_idx in unique_entry_code_to_idx:
        # get information on the "to" idx.
        entry_to_bitstring = df_values[df_values["entry_code"] == entry_to_idx].drop(
            columns=["entry_code", "entry_id", "weight"]
        )
        entry_to_np = entry_to_bitstring.to_numpy()

        # get information on the "from" idx(s)
        unique_entry_code_from_idx = (
            df_relations[df_relations["entry_code_to"] == entry_to_idx][
                "entry_code_from"
            ]
            .unique()
            .tolist()
        )

        # loop through the "from" idx
        for entry_from_idx in unique_entry_code_from_idx:
            entry_from_bitstring = df_values[
                df_values["entry_code"] == entry_from_idx
            ].drop(columns=["entry_code", "entry_id", "weight"])
            entry_from_np = entry_from_bitstring.to_numpy()

            # calculate inheritance and log
            inheritance_array = array_overlap(entry_from_np, entry_to_np)
            inheritance_list.append(inheritance_array)

            # log metadata
            metadata_list.append((entry_from_idx, entry_to_idx))

    # gather results into dataframe
    features = df_values.drop(
        columns=["entry_id", "entry_code", "weight"]
    ).columns.tolist()
    inheritance_array = np.vstack(inheritance_list)
    df_val = pd.DataFrame(inheritance_array, columns=features)
    df_idx = pd.DataFrame(metadata_list, columns=["entry_code_from", "entry_code_to"])
    df_inheritance = pd.concat([df_idx, df_val], axis=1)

    # now add metadata
    df_weight = df_values[["entry_id", "entry_code"]].drop_duplicates()
    df_weight_to = df_weight.rename(
        columns={
            "entry_id": "entry_id_to",
            "entry_code": "entry_code_to",
            # "weight": "weight_to",
        }
    )
    df_weight_from = df_weight.rename(
        columns={
            "entry_id": "entry_id_from",
            "entry_code": "entry_code_from",
            # "weight": "weight_from",
        }
    )

    df_inheritance = df_inheritance.merge(df_weight_to, on="entry_code_to", how="inner")
    df_inheritance = df_inheritance.merge(
        df_weight_from, on="entry_code_from", how="inner"
    )

    return df_inheritance


def select_relations(
    df_relations, df_values, entry_metadata, subset_polls=None, subset_time=None
):
    """
    subset polls: list
    subset time: integer
    """
    # subset based on polls and time
    if subset_polls:
        entry_metadata = entry_metadata[entry_metadata["poll_name"].isin(subset_polls)]
    if subset_time:
        entry_metadata = entry_metadata[entry_metadata["year_from"] < subset_time]
    entry_metadata = entry_metadata[["entry_id"]].drop_duplicates()
    entry_metadata_from = entry_metadata.rename(columns={"entry_id": "entry_id_from"})
    entry_metadata_to = entry_metadata.rename(columns={"entry_id": "entry_id_to"})
    df_relations = df_relations.merge(
        entry_metadata_from, on="entry_id_from", how="inner"
    )
    df_relations = df_relations.merge(entry_metadata_to, on="entry_id_to", how="inner")

    # inner join with values data
    df_values_idx = df_values[["entry_id", "entry_code"]].drop_duplicates()
    df_values_from_idx = df_values_idx.rename(
        columns={"entry_id": "entry_id_from", "entry_code": "entry_code_from"}
    )
    df_values_to_idx = df_values_idx.rename(
        columns={"entry_id": "entry_id_to", "entry_code": "entry_code_to"}
    )
    df_relations = df_relations.merge(
        df_values_from_idx, on="entry_id_from", how="inner"
    )
    df_relations = df_relations.merge(df_values_to_idx, on="entry_id_to", how="inner")

    return df_relations
