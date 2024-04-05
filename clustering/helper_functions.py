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
