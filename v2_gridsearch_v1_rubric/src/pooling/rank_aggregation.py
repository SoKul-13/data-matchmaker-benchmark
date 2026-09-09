"""
Rank pooling / ensemble across datasets.

Input: a score table  scores[system, dataset]  (mean composite score per dataset).
Output: consensus rankings under several aggregation rules, agreement statistics
and bootstrap rank distributions.

Rules
-----
mean_score   : arithmetic mean of per-dataset scores (baseline; scale-sensitive)
mean_z       : mean of per-dataset z-scores (removes dataset difficulty offsets)
mean_rank    : mean of per-dataset ranks
borda        : Borda count (sum of (n - rank))
copeland     : pairwise-majority wins minus losses across datasets
kemeny       : Kemeny-Young optimal ranking (exact for n <= 9, local search otherwise)
rrf          : reciprocal rank fusion, 1 / (k + rank)
"""
from __future__ import annotations

import itertools
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy import stats


def ranks_from_scores(x: np.ndarray, higher_better: bool = True) -> np.ndarray:
    """1-based average ranks (ties share the mean rank)."""
    v = -x if higher_better else x
    return stats.rankdata(v, method="average")


def kendall_tau(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.all(a == a[0]) or np.all(b == b[0]):
        return 0.0
    t, _ = stats.kendalltau(a, b)
    return float(0.0 if np.isnan(t) else t)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.all(a == a[0]) or np.all(b == b[0]):
        return 0.0
    r, _ = stats.spearmanr(a, b)
    return float(0.0 if np.isnan(r) else r)


# --------------------------------------------------------------------------- #
# aggregation rules: S (n_sys, n_datasets), optional dataset weights -> aggregate score (higher better)
# --------------------------------------------------------------------------- #

def _w(S: np.ndarray, weights: Optional[np.ndarray]) -> np.ndarray:
    if weights is None:
        return np.ones(S.shape[1]) / S.shape[1]
    w = np.asarray(weights, dtype=float)
    return w / w.sum()


def agg_mean_score(S, weights=None):
    return S @ _w(S, weights)


def agg_mean_z(S, weights=None):
    mu, sd = S.mean(0, keepdims=True), S.std(0, keepdims=True) + 1e-12
    return ((S - mu) / sd) @ _w(S, weights)


def _rank_matrix(S):
    return np.stack([ranks_from_scores(S[:, j]) for j in range(S.shape[1])], axis=1)


def agg_mean_rank(S, weights=None):
    return -(_rank_matrix(S) @ _w(S, weights))


def agg_borda(S, weights=None):
    n = S.shape[0]
    return (n - _rank_matrix(S)) @ _w(S, weights)


def pairwise_preference(S: np.ndarray, weights=None) -> np.ndarray:
    """P[i, j] = weighted fraction of datasets where system i scores strictly higher than j."""
    w = _w(S, weights)
    diff = S[:, None, :] - S[None, :, :]
    return (diff > 0).astype(float) @ w + 0.5 * ((diff == 0).astype(float) @ w) * (1 - np.eye(S.shape[0]))


def agg_copeland(S, weights=None):
    P = pairwise_preference(S, weights)
    wins = (P > 0.5).sum(1)
    losses = (P < 0.5).sum(1)
    return (wins - losses).astype(float)


def agg_rrf(S, weights=None, k: float = 60.0):
    return (1.0 / (k + _rank_matrix(S))) @ _w(S, weights)


def kemeny_order(S: np.ndarray, weights=None, max_exact: int = 9, restarts: int = 20, seed: int = 0) -> np.ndarray:
    """Return the Kemeny-Young consensus order (array of system indices, best first)."""
    P = pairwise_preference(S, weights)
    n = S.shape[0]

    def score(order):
        return sum(P[order[i], order[j]] for i in range(n) for j in range(i + 1, n))

    if n <= max_exact:
        best, best_s = None, -1
        for perm in itertools.permutations(range(n)):
            s = score(perm)
            if s > best_s:
                best, best_s = perm, s
        return np.array(best)
    # local search from Borda order with pairwise swaps
    rng = np.random.default_rng(seed)
    best_order, best_s = None, -1
    for r in range(restarts):
        order = list(np.argsort(-agg_borda(S, weights))) if r == 0 else list(rng.permutation(n))
        improved = True
        cur = score(order)
        while improved:
            improved = False
            for i in range(n - 1):
                for j in range(i + 1, n):
                    o2 = order.copy()
                    o2[i], o2[j] = o2[j], o2[i]
                    s2 = score(o2)
                    if s2 > cur:
                        order, cur, improved = o2, s2, True
        if cur > best_s:
            best_order, best_s = order, cur
    return np.array(best_order)


def agg_kemeny(S, weights=None):
    order = kemeny_order(S, weights)
    out = np.zeros(S.shape[0])
    out[order] = np.arange(S.shape[0], 0, -1)
    return out


RULES: Dict[str, Callable] = {
    "mean_score": agg_mean_score,
    "mean_z": agg_mean_z,
    "mean_rank": agg_mean_rank,
    "borda": agg_borda,
    "copeland": agg_copeland,
    "rrf": agg_rrf,
    "kemeny": agg_kemeny,
}


def consensus_ranking(S: np.ndarray, rule: str = "borda", weights=None) -> np.ndarray:
    """1-based ranks of systems under an aggregation rule."""
    return ranks_from_scores(RULES[rule](S, weights))


def dataset_agreement(S: np.ndarray, consensus_ranks: np.ndarray) -> np.ndarray:
    """Kendall tau between each dataset's ranking and the consensus."""
    return np.array([kendall_tau(-ranks_from_scores(S[:, j]), -consensus_ranks) for j in range(S.shape[1])])


def pairwise_dataset_tau(S: np.ndarray) -> np.ndarray:
    R = _rank_matrix(S)
    D = S.shape[1]
    T = np.eye(D)
    for i in range(D):
        for j in range(i + 1, D):
            T[i, j] = T[j, i] = kendall_tau(-R[:, i], -R[:, j])
    return T


def informativeness_weights(item_scores: Sequence[np.ndarray], n_boot: int = 200, seed: int = 0) -> np.ndarray:
    """Dataset weights = 1 / (mean bootstrap variance of system ranks).  Datasets whose
    rankings are stable under item resampling receive more weight."""
    rng = np.random.default_rng(seed)
    out = []
    for X in item_scores:  # X (n_items, n_sys)
        n = X.shape[0]
        R = []
        for _ in range(n_boot):
            idx = rng.integers(0, n, n)
            R.append(ranks_from_scores(X[idx].mean(0)))
        out.append(1.0 / (np.mean(np.var(np.stack(R), axis=0)) + 1e-6))
    w = np.array(out)
    return w / w.sum()


def bootstrap_consensus(item_scores: Sequence[np.ndarray], rule: str = "borda", n_boot: int = 500,
                        seed: int = 0, weights=None) -> Dict[str, np.ndarray]:
    """Resample items within every dataset, recompute per-dataset means and the
    consensus; return the rank distribution per system.

    item_scores: list over datasets of arrays (n_items_d, n_sys)
    Returns dict with 'rank_samples' (n_boot, n_sys), 'rank_mean', 'rank_ci' (2, n_sys),
    'p_rank' (n_sys, n_sys) probability that system i has rank r."""
    rng = np.random.default_rng(seed)
    n_sys = item_scores[0].shape[1]
    samples = np.zeros((n_boot, n_sys))
    for b in range(n_boot):
        cols = []
        for X in item_scores:
            idx = rng.integers(0, X.shape[0], X.shape[0])
            cols.append(X[idx].mean(0))
        S = np.stack(cols, axis=1)
        samples[b] = consensus_ranking(S, rule, weights)
    p_rank = np.zeros((n_sys, n_sys))
    for r in range(1, n_sys + 1):
        p_rank[:, r - 1] = (np.round(samples) == r).mean(0)
    return {
        "rank_samples": samples,
        "rank_mean": samples.mean(0),
        "rank_ci": np.percentile(samples, [2.5, 97.5], axis=0),
        "p_rank": p_rank,
    }
