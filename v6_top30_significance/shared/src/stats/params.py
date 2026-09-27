"""
Fitted aggregation-model parameters WITH standard errors, for the parameter dumps.

  bt_fit(wins)            Bradley-Terry strengths from a pairwise win matrix (wins[i, j] = number of items where i beat j; ties 1/2).
                          MLE with a small ridge, identified by sum(beta) = 0; SE from the inverse observed information.
  rasch_fit(Y)            Rasch (1-PL) joint MLE: abilities theta (models) and difficulties b (items) from a binary matrix Y (items x models);
                          SE from the diagonal of the inverse Hessian (ridge-regularised); returns both parameter sets.
  pairwise_wins(items)    build the win matrix from per-dataset (items x models) score matrices.
  copeland_scores(S) / borda_scores(S) / kemeny(S)   the deterministic views with their auxiliaries (Kemeny cost).
"""
from __future__ import annotations

from typing import Dict, Sequence

import numpy as np
from scipy import optimize

from pooling.rank_aggregation import kemeny_order, pairwise_preference, ranks_from_scores


def pairwise_wins(items: Sequence[np.ndarray]) -> np.ndarray:
    M = items[0].shape[1]; W = np.zeros((M, M))
    for X in items:
        for i in range(M):
            for j in range(M):
                if i != j:
                    a, b = X[:, i], X[:, j]; ok = ~(np.isnan(a) | np.isnan(b))
                    W[i, j] += (a[ok] > b[ok]).sum() + 0.5 * (a[ok] == b[ok]).sum()
    return W


def bt_fit(wins: np.ndarray, ridge: float = 0.01) -> Dict[str, np.ndarray]:
    M = wins.shape[0]

    def unpack(x):
        b = np.concatenate([[0.0], x]); return b

    def nll(x):
        b = unpack(x); p = 1 / (1 + np.exp(-(b[:, None] - b[None, :])))
        return -np.sum(wins * np.log(p + 1e-12)) + ridge * np.sum(b ** 2)

    res = optimize.minimize(nll, np.zeros(M - 1), method="L-BFGS-B")
    b = unpack(res.x)
    # observed information for the free parameters (numerical Hessian)
    eps = 1e-4; H = np.zeros((M - 1, M - 1))
    g0 = optimize.approx_fprime(res.x, nll, eps)
    for k in range(M - 1):
        xk = res.x.copy(); xk[k] += eps
        H[:, k] = (optimize.approx_fprime(xk, nll, eps) - g0) / eps
    H = 0.5 * (H + H.T)
    try:
        cov = np.linalg.inv(H); se_free = np.sqrt(np.clip(np.diag(cov), 0, None))
    except np.linalg.LinAlgError:
        se_free = np.full(M - 1, np.nan)
    se = np.concatenate([[0.0], se_free])           # reference model has SE 0 by construction; report contrasts vs it
    centred = b - b.mean()
    return {"beta": centred, "beta_vs_reference": b, "se_vs_reference": se, "converged": bool(res.success), "nll": float(res.fun),
            "n_comparisons": float(wins.sum())}


def rasch_fit(Y: np.ndarray, ridge_theta: float = 0.01, ridge_b: float = 0.001) -> Dict[str, np.ndarray]:
    """Y: (n_items x M) binary (NaN allowed = missing)."""
    N, M = Y.shape; mask = ~np.isnan(Y); Yf = np.nan_to_num(Y)

    def nll(x):
        th, b = x[:M], x[M:]
        z = th[None, :] - b[:, None]; p = 1 / (1 + np.exp(-z))
        ll = mask * (Yf * np.log(p + 1e-12) + (1 - Yf) * np.log(1 - p + 1e-12))
        return -ll.sum() + ridge_theta * np.sum(th ** 2) + ridge_b * np.sum(b ** 2)

    def grad(x):
        th, b = x[:M], x[M:]
        z = th[None, :] - b[:, None]; p = 1 / (1 + np.exp(-z)); r = mask * (Yf - p)
        return np.concatenate([-r.sum(0) + 2 * ridge_theta * th, r.sum(1) + 2 * ridge_b * b])

    x0 = np.zeros(M + N)
    res = optimize.minimize(nll, x0, jac=grad, method="L-BFGS-B", options={"maxiter": 2000})
    th, b = res.x[:M], res.x[M:]
    z = th[None, :] - b[:, None]; p = 1 / (1 + np.exp(-z)); info = mask * p * (1 - p)
    se_theta = 1 / np.sqrt(info.sum(0) + 2 * ridge_theta); se_b = 1 / np.sqrt(info.sum(1) + 2 * ridge_b)   # diagonal approximation
    return {"theta": th - th.mean(), "se_theta": se_theta, "b": b, "se_b": se_b, "converged": bool(res.success), "nll": float(res.fun),
            "n_items": int(N), "n_models": int(M), "share_missing": float(1 - mask.mean())}


def borda_scores(S: np.ndarray) -> np.ndarray:
    M, D = S.shape; return np.stack([M - ranks_from_scores(S[:, j]) for j in range(D)], 1).mean(1)


def copeland_scores(S: np.ndarray) -> np.ndarray:
    P = pairwise_preference(S); return (P > 0.5).sum(1) + 0.5 * ((P == 0.5).sum(1) - 1)


def kemeny(S: np.ndarray) -> Dict[str, np.ndarray]:
    order = kemeny_order(S); M, D = S.shape
    R = np.vstack([ranks_from_scores(S[:, j]) for j in range(D)])
    pos = np.empty(M); pos[order] = np.arange(M)
    cost = 0.0
    for j in range(D):
        for a in range(M):
            for b in range(a + 1, M):
                if (R[j, a] - R[j, b]) * (pos[a] - pos[b]) < 0:
                    cost += 1
    return {"order": order, "position": pos, "kendall_cost": float(cost), "max_cost": float(D * M * (M - 1) / 2)}
