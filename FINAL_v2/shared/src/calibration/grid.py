"""Weight grid over the selected metrics, objective on anchors + native fidelity, top-K ensemble."""
from __future__ import annotations

import itertools
from typing import Dict, List, Sequence

import numpy as np
from scipy import stats

LN2 = float(np.log(2.0))
NBINS, EPS = 10, 1e-3


LAMBDAS = [0.0, 0.25, 0.5, 0.75, 1.0]


def with_gate(W: np.ndarray, lambdas=LAMBDAS) -> np.ndarray:
    """append a hedge-penalty column to every weight vector: (n*len(lambdas), K+1)"""
    return np.concatenate([np.hstack([W, np.full((len(W), 1), l)]) for l in lambdas])


def gated_scores(X: np.ndarray, hedge_free: np.ndarray, Wg: np.ndarray) -> np.ndarray:
    """X (n, K) selected metrics, hedge_free (n,), Wg (B, K+1) -> (n, B) scores = (X w) * (1 - lambda * hedged)"""
    S = X @ Wg[:, :-1].T
    return S * (1.0 - Wg[None, :, -1] * (1.0 - hedge_free)[:, None])


def simplex_grid(K: int, step: float, max_points: int = 200_000, seed: int = 0) -> np.ndarray:
    units = int(round(1 / step))
    out = []
    for cuts in itertools.combinations(range(units + K - 1), K - 1):
        prev, comp = -1, []
        for c in cuts:
            comp.append(c - prev - 1); prev = c
        comp.append(units + K - 2 - prev)
        out.append(comp)
    W = np.asarray(out, dtype=np.float64) / units
    if len(W) > max_points:
        W = W[np.random.default_rng(seed).choice(len(W), max_points, replace=False)]
    return W


def _rank_cols(S: np.ndarray) -> np.ndarray:
    return stats.rankdata(S, axis=0)


def anchor_terms(S: np.ndarray, u: np.ndarray, groups: np.ndarray, ops: np.ndarray) -> Dict[str, np.ndarray]:
    """S (n_anchor, B) scores for B weightings.  Returns per-weighting terms:
    rho (mean per-dataset Spearman with u), auc (correct vs wrong), js (cross-dataset JS at matched operator)."""
    B = S.shape[1]
    ru = stats.rankdata(u)
    rhos = []
    for g in np.unique(groups):
        m = groups == g
        if m.sum() < 8:
            continue
        rs = _rank_cols(S[m]); rc = rs - rs.mean(0); uc = (ru[m] - ru[m].mean())[:, None]
        den = np.sqrt((rc ** 2).sum(0) * (uc ** 2).sum()) + 1e-12
        rhos.append((rc * uc).sum(0) / den)
    rho = np.nanmean(np.stack(rhos), 0)
    pos, neg = S[u >= 0.95], S[u <= 0.3]
    # AUC via rank-sum (vectorised over B)
    allv = np.concatenate([pos, neg]); r = _rank_cols(allv)
    auc = (r[: len(pos)].sum(0) - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
    # JS between datasets at the same operator
    bins = np.clip((S * NBINS).astype(int), 0, NBINS - 1)
    gid = {(g, o): i for i, (g, o) in enumerate(sorted({(g, o) for g, o in zip(groups, ops)}))}
    ids = np.array([gid[(g, o)] for g, o in zip(groups, ops)])
    H = np.zeros((len(gid), NBINS, B))
    for b in range(B):
        np.add.at(H[:, :, b], (ids, bins[:, b]), 1)
    P = (H + EPS) / (H.sum(1, keepdims=True) + EPS * NBINS)
    js_vals = []
    by_op: Dict[str, List[int]] = {}
    for (g, o), i in gid.items():
        by_op.setdefault(o, []).append(i)
    for o, idxs in by_op.items():
        for a in range(len(idxs)):
            for c in range(a + 1, len(idxs)):
                Pa, Pb = P[idxs[a]], P[idxs[c]]; Mx = 0.5 * (Pa + Pb)
                js_vals.append(0.5 * (Pa * np.log(Pa / Mx)).sum(0) + 0.5 * (Pb * np.log(Pb / Mx)).sum(0))
    js = np.mean(np.stack(js_vals), 0) if js_vals else np.zeros(B)
    bad = S[u <= 0.001].mean(0) if (u <= 0.001).any() else np.zeros(B)     # mean score of wrong / abstaining anchors
    return {"rho": rho, "auc": auc, "js": js, "bad": bad}


def native_fidelity(S_models: np.ndarray, native: np.ndarray, model_idx: np.ndarray, ds_idx: np.ndarray, n_models: int, n_ds: int) -> np.ndarray:
    """Mean over datasets of Kendall tau between composite and native rankings of models."""
    B = S_models.shape[1]
    taus = []
    for d in range(n_ds):
        m = ds_idx == d
        if not m.any():
            continue
        comp = np.zeros((n_models, B)); nat = np.zeros(n_models); cnt = np.zeros(n_models)
        np.add.at(comp, model_idx[m], S_models[m]); np.add.at(nat, model_idx[m], native[m]); np.add.at(cnt, model_idx[m], 1)
        ok = cnt > 0
        comp, nat = comp[ok] / cnt[ok, None], nat[ok] / cnt[ok]
        if len(nat) < 3:
            continue
        a, b = np.triu_indices(len(nat), 1)
        ds_ = np.sign(comp[a] - comp[b]); dn = np.sign(nat[a] - nat[b])[:, None]
        den = np.sqrt((ds_ != 0).sum(0) * (dn != 0).sum()) + 1e-12
        taus.append((ds_ * dn).sum(0) / den)
    return np.mean(np.stack(taus), 0) if taus else np.zeros(B)


def objective(t: Dict[str, np.ndarray], alpha: Dict[str, float]) -> np.ndarray:
    return (alpha["rho"] * t["rho"] + alpha["auc"] * t["auc"] + alpha["consistency"] * (1 - t["js"] / LN2)
            + alpha["native"] * np.nan_to_num(t["tau_native"]) + alpha.get("bad", 0.0) * (1 - t["bad"]))
