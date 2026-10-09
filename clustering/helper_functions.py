import numpy as np
from scipy.special import logsumexp


def fit(X, c, weights=None, num_its=2000, eps=1e-10, tol=1e-8, seed=None):
    '''
    Latent class EM for binary data.
    X: rows x questions (1/0, anything else = missing).
    seed: seed for this start (random initial q), so each start is reproducible.
    Stops when logL improves by less than tol (or after num_its).
    Returns:
    theta: clusters x questions P(Yes)
    q = rows x clusters P(cluster | row)
    pi = cluster shares.
    logL = weighted mixture log-likelihood at the returned parameters.
    n_its = number of iterations run.
    '''

    rng = np.random.default_rng(seed)

    if weights is None:
        weights = np.ones(X.shape[0])  # Default to equal weights if none provided

    # Ensure weights are a NumPy array
    weights = np.array(weights)

    # Initialization step: random soft assignment of rows to clusters.
    q = rng.dirichlet([2] * c, size=X.shape[0])

    logL_old = -np.inf
    for n_its in range(1, num_its + 1):
        # M-step (update theta).
        t0 = np.array([(q[:, r] * weights) @ (X == 0) for r in range(c)]) + eps # weighted count of "No" per (cluster, question); + eps prevents 0/0 and log(0)
        t1 = np.array([(q[:, r] * weights) @ (X == 1) for r in range(c)]) + eps # same as above for "Yes".
        theta = t1 / (t0 + t1) # weighted share of "Yes" per (cluster, question)

        # mixing proportions: weighted share of entries in each cluster
        pi = (q * weights[:, None]).sum(axis=0) / weights.sum()

        # E-step (update q), in log space to avoid underflow.
        ll = (X == 1) @ np.log(theta).T + (X == 0) @ np.log(1 - theta).T + np.log(pi) # log[P(row | cluster) * pi], (rows, clusters)
        row_logL = logsumexp(ll, axis=1) # log P(row) = log sum_r pi_r * P(row | r)

        # Normalize per row (row weights would cancel)
        q = np.exp(ll - row_logL[:, None])

        # mixture log-likelihood, weighted by entry weights; stop when converged
        logL = np.sum(weights * row_logL)
        if logL - logL_old < tol:
            break
        logL_old = logL

    return theta, q, pi, logL, n_its
