"""
Vectorised rank agreement for MANY candidate weightings at once (needed for exhaustive grids x nested bootstraps).

  ranks_many(S)          S (C x M x D) scores -> ranks (C x M x D), 1 = best, average ranks for ties
  borda_many(R)          R (C x M x D) -> pooled Borda ranking per candidate (C x M)
  tau_many(R, Rc)        Kendall tau-b between each dataset's ranking R[c, :, d] and the consensus Rc[c, :] -> (C x D)
  J_many(S)              mean tau to the Borda pool, per candidate -> (C,), plus min agreement and pairwise tau
  tau_pairs(R)           mean pairwise tau between datasets per candidate -> (C,)

All functions are exact (tie-aware tau-b) and only use numpy broadcasting; for M models the pair set has M(M-1)/2 entries.
"""
from __future__ import annotations

import numpy as np
from itertools import combinations


def ranks_many(S: np.ndarray) -> np.ndarray:
    """average ranks along axis 1 (models), higher score = rank 1"""
    C, M, D = S.shape
    X = -S
    order = np.argsort(X, axis=1, kind="stable")
    ranks = np.empty_like(X)
    idx = np.arange(1, M + 1, dtype=float)
    np.put_along_axis(ranks, order, np.broadcast_to(idx[None, :, None], (C, M, D)).copy(), axis=1)
    # tie handling: average ranks of equal values
    Xs = np.take_along_axis(X, order, axis=1)
    same_as_prev = np.zeros_like(Xs, dtype=bool); same_as_prev[:, 1:, :] = Xs[:, 1:, :] == Xs[:, :-1, :]
    if same_as_prev.any():
        rs = np.take_along_axis(ranks, order, axis=1)
        # group ids increase when value changes
        grp = np.cumsum(~same_as_prev, axis=1)
        out = rs.copy()
        for c in range(C):
            for d in range(D):
                g = grp[c, :, d]
                if same_as_prev[c, :, d].any():
                    sums = np.bincount(g, weights=rs[c, :, d]); cnt = np.bincount(g)
                    with np.errstate(invalid="ignore", divide="ignore"):
                        out[c, :, d] = (sums / cnt)[g]
        np.put_along_axis(ranks, order, out, axis=1)
    return ranks


_PAIR_CACHE = {}


def _pairs(M):
    if M not in _PAIR_CACHE:
        p = np.array(list(combinations(range(M), 2))); _PAIR_CACHE[M] = (p[:, 0], p[:, 1])
    return _PAIR_CACHE[M]


def tau_b(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """a, b: (..., M) rank vectors -> tau-b along the last axis (ties handled)."""
    i, j = _pairs(a.shape[-1])
    sa = np.sign(a[..., i] - a[..., j]); sb = np.sign(b[..., i] - b[..., j])
    conc = (sa * sb).sum(-1)
    na = (sa != 0).sum(-1); nb = (sb != 0).sum(-1)
    den = np.sqrt(na * nb)
    with np.errstate(invalid="ignore", divide="ignore"):
        t = np.where(den > 0, conc / den, 0.0)
    return t


def borda_many(R: np.ndarray) -> np.ndarray:
    C, M, D = R.shape
    pts = (M - R).sum(2)                               # C x M, higher = better
    return ranks_many(pts[:, :, None])[:, :, 0]


def J_many(S: np.ndarray) -> dict:
    R = ranks_many(S)                                  # C x M x D
    Rc = borda_many(R)                                 # C x M
    T = tau_b(np.moveaxis(R, 1, 2), Rc[:, None, :])    # C x D
    i, j = _pairs(S.shape[2])
    Rd = np.moveaxis(R, 1, 2)                          # C x D x M
    Tp = tau_b(Rd[:, i, :], Rd[:, j, :])               # C x pairs(D)
    return {"J": T.mean(1), "min_agree": T.min(1), "pairwise_tau": Tp.mean(1), "tau_per_dataset": T, "consensus_ranks": Rc}
