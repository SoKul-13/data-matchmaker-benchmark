"""
Statistical significance for model comparisons across datasets and within datasets.

Inputs are always the same two objects:
  S      (n_models x n_datasets) mean score per model and dataset
  items  list over datasets of (n_items_d x n_models) per-item score matrices (same model order as S)

  friedman_nemenyi(S, models)        Friedman test across datasets (Demšar 2006) + Nemenyi critical difference + pairwise
                                     Holm-corrected Wilcoxon signed-rank on the per-dataset scores (García & Herrera 2008)
  pairwise_item_tests(items, models) per dataset and per model pair: paired permutation test on per-item score differences
                                     (Koehn 2004 style, 10,000 draws) + Wilcoxon; Holm correction within each dataset
  kendall_w(S)                       Kendall's coefficient of concordance among datasets (how much the datasets agree)
  bootstrap_ranking(items, rule)     item bootstrap of the pooled ranking; returns the full draw matrices (ranks, scores)
  paired_objective_test(a, b)        paired bootstrap / permutation p-value for a difference of two per-resample objectives
  tau_granularity(n_models)          the attainable Kendall tau values for n models (what a rank claim can resolve)
  holm(pvals)                        Holm step-down correction
"""
from __future__ import annotations

import itertools
from typing import Dict, List, Sequence

import numpy as np
from scipy import stats

from pooling.rank_aggregation import consensus_ranking, ranks_from_scores


def holm(p: Sequence[float]) -> np.ndarray:
    p = np.asarray(p, float); m = len(p); order = np.argsort(p); adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i]); adj[i] = min(1.0, running)
    return adj


def tau_granularity(n_models: int) -> List[float]:
    if n_models > 8:
        pairs = n_models * (n_models - 1) // 2
        return sorted({round(1 - 4 * d / (2 * pairs), 4) for d in range(pairs + 1)})
    base = np.arange(n_models)
    return sorted({round(float(stats.kendalltau(base, p)[0]), 4) for p in itertools.permutations(base)})


def friedman_nemenyi(S: np.ndarray, models: Sequence[str]) -> Dict:
    M, D = S.shape
    R = np.vstack([ranks_from_scores(S[:, j]) for j in range(D)])          # D x M, 1 = best
    mean_rank = R.mean(0)
    if D < 3 or M < 2:
        return {"note": "Friedman needs >= 3 datasets and >= 2 models", "mean_rank": dict(zip(models, mean_rank.tolist()))}
    chi2, p = stats.friedmanchisquare(*[S[i, :] for i in range(M)])
    # Iman-Davenport F correction (Demšar 2006)
    ff = (D - 1) * chi2 / (D * (M - 1) - chi2) if D * (M - 1) - chi2 > 0 else np.inf
    p_ff = 1 - stats.f.cdf(ff, M - 1, (M - 1) * (D - 1)) if np.isfinite(ff) else 0.0
    q_alpha = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164, 11: 3.219, 12: 3.268, 13: 3.313, 14: 3.354, 15: 3.391}
    q = q_alpha.get(M, 3.391)
    cd = q * np.sqrt(M * (M + 1) / (6 * D))
    pairs = []
    for i, j in itertools.combinations(range(M), 2):
        diff = S[i, :] - S[j, :]
        try:
            w_stat, w_p = stats.wilcoxon(diff, zero_method="zsplit") if np.any(diff != 0) else (0.0, 1.0)
        except ValueError:
            w_stat, w_p = 0.0, 1.0
        pairs.append({"a": models[i], "b": models[j], "mean_rank_diff": float(mean_rank[i] - mean_rank[j]),
                      "nemenyi_significant": bool(abs(mean_rank[i] - mean_rank[j]) > cd), "wilcoxon_p": float(w_p),
                      "wins_a": int((diff > 0).sum()), "wins_b": int((diff < 0).sum()), "ties": int((diff == 0).sum())})
    adj = holm([x["wilcoxon_p"] for x in pairs])
    for x, a in zip(pairs, adj):
        x["wilcoxon_p_holm"] = float(a); x["wilcoxon_significant_05"] = bool(a < 0.05)
    return {"n_models": M, "n_datasets": D, "friedman_chi2": float(chi2), "friedman_p": float(p), "iman_davenport_F": float(ff),
            "iman_davenport_p": float(p_ff), "nemenyi_cd_05": float(cd), "mean_rank": dict(zip(models, mean_rank.round(3).tolist())),
            "pairwise": pairs, "tau_granularity": tau_granularity(M)}


def paired_permutation(x: np.ndarray, y: np.ndarray, n_perm: int = 10_000, seed: int = 0) -> float:
    d = np.asarray(x, float) - np.asarray(y, float); d = d[~np.isnan(d)]
    if len(d) == 0 or np.all(d == 0):
        return 1.0
    rng = np.random.default_rng(seed); obs = abs(d.mean())
    signs = rng.choice([-1.0, 1.0], size=(n_perm, len(d)))
    return float((np.abs((signs * d).mean(1)) >= obs - 1e-12).mean())


def pairwise_item_tests(items: Sequence[np.ndarray], datasets: Sequence[str], models: Sequence[str], n_perm: int = 10_000, seed: int = 0) -> List[Dict]:
    rows = []
    for X, d in zip(items, datasets):
        pr = []
        for i, j in itertools.combinations(range(X.shape[1]), 2):
            a, b = X[:, i], X[:, j]; ok = ~(np.isnan(a) | np.isnan(b))
            p_perm = paired_permutation(a[ok], b[ok], n_perm, seed)
            try:
                p_w = float(stats.wilcoxon(a[ok] - b[ok], zero_method="zsplit")[1]) if np.any(a[ok] != b[ok]) else 1.0
            except ValueError:
                p_w = 1.0
            pr.append({"dataset": d, "a": models[i], "b": models[j], "mean_a": float(np.nanmean(a)), "mean_b": float(np.nanmean(b)),
                       "diff": float(np.nanmean(a) - np.nanmean(b)), "n_items": int(ok.sum()), "p_perm": p_perm, "p_wilcoxon": p_w})
        for x, ap, aw in zip(pr, holm([x["p_perm"] for x in pr]), holm([x["p_wilcoxon"] for x in pr])):
            x["p_perm_holm"] = float(ap); x["p_wilcoxon_holm"] = float(aw); x["significant_05"] = bool(ap < 0.05)
        rows += pr
    return rows


def kendall_w(S: np.ndarray) -> Dict[str, float]:
    M, D = S.shape
    R = np.vstack([ranks_from_scores(S[:, j]) for j in range(D)]).T       # M x D
    Rsum = R.sum(1); Sdev = ((Rsum - Rsum.mean()) ** 2).sum()
    W = 12 * Sdev / (D ** 2 * (M ** 3 - M)) if M > 1 else float("nan")
    chi2 = D * (M - 1) * W; p = 1 - stats.chi2.cdf(chi2, M - 1) if M > 1 else float("nan")
    return {"kendall_W": float(W), "chi2": float(chi2), "p": float(p), "n_datasets": int(D), "n_models": int(M)}


def bootstrap_ranking(items: Sequence[np.ndarray], rule: str = "borda", n_boot: int = 1000, seed: int = 0, score_fn=None) -> Dict[str, np.ndarray]:
    """Item bootstrap within each dataset; returns ranks (n_boot x M), pooled scores (n_boot x M) and the per-dataset means (n_boot x M x D)."""
    rng = np.random.default_rng(seed); M = items[0].shape[1]; D = len(items)
    ranks = np.empty((n_boot, M)); means = np.empty((n_boot, M, D))
    for b in range(n_boot):
        S = np.stack([np.nanmean(X[rng.integers(0, X.shape[0], X.shape[0])], 0) for X in items], 1)
        means[b] = S; ranks[b] = consensus_ranking(S, rule)
    lo, hi = np.percentile(ranks, [2.5, 97.5], axis=0)
    return {"ranks": ranks, "means": means, "rank_lo": lo, "rank_hi": hi, "rank_mean": ranks.mean(0),
            "p_first": (ranks == 1).mean(0)}


def paired_objective_test(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    """a, b: per-resample values of an objective for two candidates (same resamples).  Paired bootstrap: CI of the difference and
    p = share of resamples where a <= b (one-sided).  No permutation test: resamples are not independent observations."""
    a, b = np.asarray(a, float), np.asarray(b, float); d = a - b
    return {"mean_diff": float(d.mean()), "ci95_lo": float(np.percentile(d, 2.5)), "ci95_hi": float(np.percentile(d, 97.5)),
            "p_boot_one_sided": float((d <= 0).mean()), "share_a_ahead": float((d > 0).mean())}
