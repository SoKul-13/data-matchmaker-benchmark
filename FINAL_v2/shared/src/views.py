"""
Aggregation views from the literature: each maps per-item native scores (models x datasets x items)
to one number per model.  See notes/01_LITERATURE_REVIEW.md for the papers behind each.
"""
from __future__ import annotations

import itertools
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

from pooling.rank_aggregation import consensus_ranking, ranks_from_scores

VIEWS = ["mean_raw", "baseline_norm_mean", "z_mean", "mean_win_rate", "borda", "kemeny_score", "bradley_terry", "irt_ability"]


def per_dataset_table(items: pd.DataFrame) -> pd.DataFrame:
    return items.pivot_table(index="model", columns="dataset", values="score", aggfunc="mean")


def view_mean_raw(T, **_):
    return T.mean(1)


def view_baseline_norm_mean(T, baseline: Dict[str, float], **_):
    """Open LLM Leaderboard v2: (raw - random baseline) / (1 - baseline), clipped at 0, then mean."""
    N = T.copy()
    for d in T.columns:
        b = baseline.get(d, 0.0); N[d] = ((T[d] - b) / (1 - b)).clip(lower=0)
    return N.mean(1)


def view_z_mean(T, **_):
    return ((T - T.mean(0)) / (T.std(0) + 1e-9)).mean(1)


def view_mean_win_rate(T, **_):
    """HELM: per dataset, fraction of other models beaten (ties 1/2), averaged over datasets."""
    S = T.to_numpy(); n = S.shape[0]
    wr = np.zeros(n)
    for j in range(S.shape[1]):
        col = S[:, j]
        wr += np.array([(np.sum(col[i] > np.delete(col, i)) + 0.5 * np.sum(col[i] == np.delete(col, i))) / (n - 1) for i in range(n)])
    return pd.Series(wr / S.shape[1], index=T.index)


def view_borda(T, **_):
    S = T.to_numpy(); n = S.shape[0]
    pts = sum(n - ranks_from_scores(S[:, j]) for j in range(S.shape[1]))
    return pd.Series(pts / S.shape[1], index=T.index)


def view_kemeny_score(T, **_):
    r = consensus_ranking(T.to_numpy(), "kemeny")
    return pd.Series(len(r) - r, index=T.index)


def _bt_fit(wins: np.ndarray) -> np.ndarray:
    """Bradley-Terry strengths from a wins matrix W[i, j] = number of items where i beat j (ties split)."""
    n = wins.shape[0]

    def nll(beta):
        b = np.concatenate([[0.0], beta])
        p = expit(b[:, None] - b[None, :])
        return -np.sum(wins * np.log(p + 1e-12)) + 0.01 * np.sum(beta ** 2)
    res = minimize(nll, np.zeros(n - 1), method="L-BFGS-B")
    b = np.concatenate([[0.0], res.x]); return b - b.mean()


def view_bradley_terry(T, items: pd.DataFrame = None, **_):
    """Chatbot Arena: per item, model i 'beats' j if its score is higher; fit BT strengths by MLE."""
    models = list(T.index); n = len(models); W = np.zeros((n, n))
    piv = items.pivot_table(index=["dataset", "uid"], columns="model", values="score").reindex(columns=models).to_numpy()
    for i, j in itertools.combinations(range(n), 2):
        a, b = piv[:, i], piv[:, j]
        W[i, j] += np.sum(a > b) + 0.5 * np.sum(a == b); W[j, i] += np.sum(b > a) + 0.5 * np.sum(a == b)
    return pd.Series(_bt_fit(W), index=T.index)


def view_irt_ability(T, items: pd.DataFrame = None, **_):
    """tinyBenchmarks-style Rasch model: P(correct) = sigmoid(theta_model - b_item), correct = score >= 0.5;
    joint MLE with a small ridge; returns theta centred at 0."""
    models = list(T.index)
    piv = items.pivot_table(index=["dataset", "uid"], columns="model", values="score").reindex(columns=models).to_numpy()
    Y = (piv >= 0.5).astype(float); I, M = Y.shape

    def nll(x):
        th, b = x[:M], x[M:]
        p = expit(th[None, :] - b[:, None])
        return -np.sum(Y * np.log(p + 1e-12) + (1 - Y) * np.log(1 - p + 1e-12)) + 0.01 * np.sum(th ** 2) + 0.001 * np.sum(b ** 2)
    res = minimize(nll, np.zeros(M + I), method="L-BFGS-B", options={"maxiter": 300})
    th = res.x[:M]; return pd.Series(th - th.mean(), index=T.index)


VIEW_FNS = {"mean_raw": view_mean_raw, "baseline_norm_mean": view_baseline_norm_mean, "z_mean": view_z_mean, "mean_win_rate": view_mean_win_rate,
            "borda": view_borda, "kemeny_score": view_kemeny_score, "bradley_terry": view_bradley_terry, "irt_ability": view_irt_ability}


def all_views(items: pd.DataFrame, baseline: Dict[str, float]) -> pd.DataFrame:
    T = per_dataset_table(items)
    return pd.DataFrame({v: VIEW_FNS[v](T, baseline=baseline, items=items) for v in VIEWS})


def standardise(V: pd.DataFrame) -> pd.DataFrame:
    """each view to z-scores across models so that mixing weights are comparable"""
    return (V - V.mean(0)) / (V.std(0) + 1e-9)
