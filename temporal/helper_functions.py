import numpy as np
import pandas as pd


# copied from visualization/helper_functions.py
def smooth_time_end(df, bin_width, step_size):
    df_smoothed = pd.DataFrame()
    min_year, max_year = df["year_from"].min(), df["year_to"].max()
    adjusted_max_year = max_year - bin_width + 1
    bins = range(min_year, adjusted_max_year + 1, step_size)

    for start in bins:
        end = start + bin_width
        # Adjusted condition for finding overlapping intervals
        mask = (df["year_from"] <= end) & (df["year_to"] >= start)
        temp_df = df.loc[mask].copy()
        temp_df["time_bin"] = np.mean([start, end])
        df_smoothed = pd.concat([df_smoothed, temp_df])

    return df_smoothed
