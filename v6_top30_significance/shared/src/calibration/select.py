"""Metric deduplication and anchor-based selection."""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import nnls


def dedupe(X: np.ndarray, names: Sequence[str], thresh: float = 0.95, prefer: Optional[Sequence[str]] = None) -> Tuple[List[int], Dict[str, List[str]]]:
    """Greedy clustering by |Spearman| >= thresh; returns representative column indices and clusters."""
    keep, clusters = [], {}
    var = X.std(0) > 1e-6
    order = list(range(X.shape[1]))
    if prefer:
        pri = {n: i for i, n in enumerate(prefer)}
        order.sort(key=lambda j: pri.get(names[j], 10 ** 6))
    R = stats.spearmanr(X, axis=0).correlation if X.shape[1] > 1 else np.ones((1, 1))
    R = np.nan_to_num(np.atleast_2d(R))
    for j in order:
        if not var[j]:
            clusters.setdefault("_constant", []).append(names[j]); continue
        rep = next((k for k in keep if abs(R[j, k]) >= thresh), None)
        if rep is None:
            keep.append(j); clusters[names[j]] = [names[j]]
        else:
            clusters[names[rep]].append(names[j])
    return keep, clusters


def anchor_agreement(A: np.ndarray, u: np.ndarray, groups: np.ndarray) -> pd.DataFrame:
    """Per metric: mean-per-dataset Spearman with utility, AUC correct(u>=0.95) vs wrong(u<=0.3), and mean score gap."""
    out = []
    for j in range(A.shape[1]):
        rhos = []
        for g in np.unique(groups):
            m = groups == g
            if m.sum() > 8 and A[m, j].std() > 0:
                r = stats.spearmanr(A[m, j], u[m]).correlation
                if not np.isnan(r):
                    rhos.append(r)
        pos, neg = A[u >= 0.95, j], A[u <= 0.3, j]
        auc = float((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()) if len(pos) and len(neg) else 0.5
        out.append({"rho": float(np.mean(rhos)) if rhos else 0.0, "auc": auc, "gap": float(pos.mean() - neg.mean()) if len(pos) and len(neg) else 0.0})
    return pd.DataFrame(out)


def fit_nnls(A: np.ndarray, u: np.ndarray) -> np.ndarray:
    w, _ = nnls(A, u)
    s = w.sum()
    return w / s if s > 0 else np.ones(A.shape[1]) / A.shape[1]


def lodo_rho(A: np.ndarray, u: np.ndarray, groups: np.ndarray, cols: List[int]) -> float:
    """Mean over datasets of Spearman(utility, NNLS-combination fitted WITHOUT that dataset)."""
    vals = []
    for g in np.unique(groups):
        tr, te = groups != g, groups == g
        if te.sum() < 8:
            continue
        w = fit_nnls(A[tr][:, cols], u[tr])
        s = A[te][:, cols] @ w
        if s.std() > 0:
            r = stats.spearmanr(s, u[te]).correlation
            if not np.isnan(r):
                vals.append(r)
    return float(np.mean(vals)) if vals else 0.0


def forward_select(A: np.ndarray, u: np.ndarray, groups: np.ndarray, candidates: List[int], k_max: int = 10, min_gain: float = 0.002) -> Tuple[List[int], List[dict]]:
    """Greedy forward selection maximising leave-one-dataset-out Spearman of the NNLS combination."""
    selected, trace, best = [], [], -1.0
    while len(selected) < k_max:
        scores = {j: lodo_rho(A, u, groups, selected + [j]) for j in candidates if j not in selected}
        if not scores:
            break
        j, s = max(scores.items(), key=lambda kv: kv[1])
        trace.append({"step": len(selected) + 1, "added": j, "lodo_rho": s, "gain": s - best})
        if s - best < min_gain and selected:
            trace[-1]["stopped"] = True
            break
        selected.append(j); best = s
    return selected, trace
