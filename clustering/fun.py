import re
import numpy as np
import pandas as pd


def fit(X, c, weights=None, num_its=200, eps=1e-10):
    if weights is None:
        weights = np.ones(X.shape[0])  # Default to equal weights if none provided

    # Ensure weights are a NumPy array
    weights = np.array(weights)

    theta = np.random.dirichlet([2] * X.shape[1], size=c)
    q = np.random.dirichlet([2] * c, size=X.shape[0])

    for _ in range(num_its):
        # Modify these lines to incorporate weights
        t0 = np.array([(q[:, r] * weights) @ (X == 0) for r in range(c)]) + eps
        t1 = np.array([(q[:, r] * weights) @ (X == 1) for r in range(c)]) + eps

        theta = t1 / (t0 + t1)
        y = np.exp((X == 1) @ np.log(theta).T + (X == 0) @ np.log(1 - theta).T)

        # Normalize y by its sum, considering weights
        q = (y * weights[:, np.newaxis]) / (y * weights[:, np.newaxis]).sum(axis=1)[
            :, np.newaxis
        ]

    return theta, q


# custom matrix multiplication with np.nan
def custom_matmul(A, B):
    result = np.zeros((A.shape[0], B.shape[1]))
    for i in range(A.shape[0]):
        for j in range(B.shape[1]):
            # Sum over the products of the non-NaN elements
            result[i, j] = np.nansum([A[i, k] * B[k, j] for k in range(A.shape[1])])
    return result


# weighted average for all dimensions
def weighted_average(x, weight_column="weight", grouping_column="world_region"):
    """Calculate weighted average for each column except 'world_region' and 'weight'."""
    result = {}
    for column in x.columns.drop([grouping_column, weight_column]):
        weighted_avg = (x[column] * x[weight_column]).sum() / x[weight_column].sum()
        result[column] = weighted_avg
    return pd.Series(result)


# higheest and lowest per group
def highest_and_lowest_per_group(group):
    max_val = group.max().max()
    min_val = group.min().min()
    max_dim = group.idxmax(axis=1).value_counts().idxmax()
    min_dim = group.idxmin(axis=1).value_counts().idxmax()
    return pd.Series(
        {
            "Highest Value": max_val,
            "Highest Dimension": max_dim,
            "Lowest Value": min_val,
            "Lowest Dimension": min_dim,
        }
    )


def highest_and_lowest_iter(df, iter_columns):
    df_list = []
    for dimension in iter_columns:
        highest_value = df[dimension].max()
        lowest_value = df[dimension].min()
        highest_region = df[df[dimension] == highest_value]["world_region"].values[0]
        lowest_region = df[df[dimension] == lowest_value]["world_region"].values[0]

        # Append data to the list instead of DataFrame
        df_list.append(
            {
                "Dimension": dimension,
                "Highest World Region": highest_region,
                "Lowest World Region": lowest_region,
                "Highest Value": highest_value,
                "Lowest Value": lowest_value,
            }
        )
    new_df = pd.DataFrame(df_list)
    return new_df


def time_bin(df, n, time_column="year_from"):
    df = df.sort_values(by=time_column).reset_index(drop=True)
    df["time_bin"], _ = pd.qcut(df[time_column], n, retbins=True, labels=False)
    df["time_range"] = pd.qcut(df[time_column], n, retbins=False)
    return df


def smooth_time(df, bin_width, step_size):
    df_smoothed = pd.DataFrame()
    min_year, max_year = df["year_from"].min(), df["year_from"].max()
    adjusted_max_year = max_year - bin_width + 1
    bins = range(min_year, adjusted_max_year + 1, step_size)

    for start in bins:
        end = start + bin_width
        mask = (df["year_from"] >= start) & (df["year_from"] < end)
        temp_df = df.loc[mask].copy()
        temp_df["time_bin"] = np.mean([start, end])
        df_smoothed = pd.concat([df_smoothed, temp_df])

    return df_smoothed


def weighted_corr_x_y(x, y, w):
    """
    Calculate weighted correlation between two arrays, ignoring NaN values.

    Parameters:
    x, y -- arrays of values to correlate
    w -- array of weights
    """

    # Remove NaN values and associated weights
    # Only calculate correlations for pairs of non-NaN values
    mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[mask]
    y = y[mask]
    w = w[mask]

    # Ensure that there are enough non-NaN data points
    if len(x) < 2:
        return np.nan

    # Calculate weighted mean
    x_weighted_mean = np.average(x, weights=w)
    y_weighted_mean = np.average(y, weights=w)

    # Calculate weighted covariance and variances
    covariance = np.average((x - x_weighted_mean) * (y - y_weighted_mean), weights=w)
    x_variance = np.average((x - x_weighted_mean) ** 2, weights=w)
    y_variance = np.average((y - y_weighted_mean) ** 2, weights=w)

    # Check for zero variance
    if x_variance == 0 or y_variance == 0:
        return np.nan

    # Calculate the correlation
    correlation = covariance / np.sqrt(x_variance * y_variance)

    # Fill diagonal with 1
    return correlation


def weighted_corr(features, matrix):
    correlations = pd.DataFrame(np.nan, index=features, columns=features)
    for i in range(len(features)):
        for j in range(i + 1, len(features)):
            col_i = features[i]
            col_j = features[j]
            corr = weighted_corr_x_y(
                matrix[col_i],
                matrix[col_j],
                matrix["weight"],
            )
            correlations.at[col_i, col_j] = corr
            correlations.at[col_j, col_i] = corr  # symmetry
    correlations = correlations.fillna(1)  # fill diagonal with 1
    return correlations
