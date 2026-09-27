#!/usr/bin/env python
"""
v3 step 3 - Grid search over the selected metrics' weights; keep the 100 best weightings as an ensemble.

Objective per weighting (all computed on anchors except native fidelity):
  J = a_rho * Spearman(score, utility)  +  a_auc * AUC(correct vs wrong)
    + a_cons * (1 - JS between datasets at matched operator / ln2)  +  a_nat * tau(composite vs native model ranking)
Default alpha = rho .35, auc .20, consistency .25, native .20.
Outputs: output/grid_all.csv (every weighting + terms), output/ensemble.json (top-100 weightings, mean weights),
         output/baselines_grid.csv
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]          # this version's folder (output/ lives here)
V6 = ROOT.parent                                     # the shared v6 folder (shared/src, data/, config/)
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from calibration.grid import anchor_terms, gated_scores, native_fidelity, objective, simplex_grid, with_gate  # noqa: E402
from metrics.library import METRIC_NAMES  # noqa: E402

ALPHA = {"rho": 0.30, "auc": 0.15, "consistency": 0.20, "native": 0.15, "bad": 0.20}


def evaluate(W, A_sel, hA, u, groups, ops, M_sel, hM, native, model_idx, ds_idx, n_models, n_ds, batch=256):
    parts = []
    for i in range(0, len(W), batch):
        Wb = W[i:i + batch]
        S = gated_scores(A_sel, hA, Wb)
        t = anchor_terms(S, u, groups, ops)
        t["tau_native"] = native_fidelity(gated_scores(M_sel, hM, Wb), native, model_idx, ds_idx, n_models, n_ds)
        t["J"] = objective(t, ALPHA)
        parts.append(pd.DataFrame(t))
    return pd.concat(parts, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--step", type=float, default=None)
    args = ap.parse_args()
    out = OUT
    sel = json.load(open(out / "selected.json")); cols = sel["selected_idx"]; names = sel["selected"]
    A = np.load(out / "matrix_anchors.npz")["A"][:, cols]; ia = pd.read_csv(out / "index_anchors.csv")
    M = np.load(out / "matrix_models.npz")["M"]; im = pd.read_csv(out / "index_models.csv")
    models, dss = sorted(im.model.unique()), sorted(im.dataset.unique())
    model_idx, ds_idx = im.model.map({m: i for i, m in enumerate(models)}).to_numpy(), im.dataset.map({d: i for i, d in enumerate(dss)}).to_numpy()
    K = len(cols)
    step = args.step or (0.02 if K <= 3 else 0.05 if K <= 6 else 0.1)
    W = with_gate(simplex_grid(K, step))
    hcol = METRIC_NAMES.index("hedge_free")
    hA = np.load(out / "matrix_anchors.npz")["A"][:, hcol]; hM = M[:, hcol]
    print(f"selected {K} metrics {names}; grid step {step} x 5 hedge penalties: {len(W):,} weightings")
    df = evaluate(W, A, hA, ia.utility.to_numpy(float), ia.dataset.to_numpy(), ia.op.to_numpy(), M[:, cols], hM, im.native_value.to_numpy(float), model_idx, ds_idx, len(models), len(dss))
    for k, n in enumerate(names):
        df[f"w_{n}"] = W[:, k]
    df["lambda"] = W[:, -1]
    df = df.sort_values("J", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", np.arange(1, len(df) + 1))
    df.to_csv(out / "grid_all.csv", index=False)
    top = df.head(args.top)
    Wtop = top[[f"w_{n}" for n in names] + ["lambda"]].to_numpy()
    ens = {"selected": names, "selected_idx": cols, "hedge_col": hcol, "alpha": ALPHA, "grid_step": step, "n_grid": int(len(W)), "top_k": args.top,
           "mean_weights": {n: float(x) for n, x in zip(names, Wtop[:, :-1].mean(0))}, "mean_lambda": float(Wtop[:, -1].mean()),
           "weight_spread": {n: [float(Wtop[:, k].min()), float(Wtop[:, k].max())] for k, n in enumerate(names)},
           "top_weightings": Wtop.tolist(), "J_top1": float(top.J.iloc[0]), "J_top100": float(top.J.iloc[-1]), "J_median_grid": float(df.J.median()),
           "terms_top1": {t: float(top[t].iloc[0]) for t in ["rho", "auc", "js", "tau_native", "bad"]},
           "terms_ensemble_mean": {t: float(top[t].mean()) for t in ["rho", "auc", "js", "tau_native", "bad"]}}
    json.dump(ens, open(out / "ensemble.json", "w"), indent=2)
    # baselines: single metrics and uniform, evaluated with the same objective
    base_rows = []
    Afull = np.load(out / "matrix_anchors.npz")["A"]
    for name in ["native_style_metric", "em_norm", "tok_f1", "rouge_l", "num_tol_1"]:
        j = METRIC_NAMES.index(name)
        t = anchor_terms(Afull[:, [j]], ia.utility.to_numpy(float), ia.dataset.to_numpy(), ia.op.to_numpy())
        t["tau_native"] = native_fidelity(M[:, [j]], im.native_value.to_numpy(float), model_idx, ds_idx, len(models), len(dss))
        t["J"] = objective(t, ALPHA); base_rows.append({"baseline": name, **{k: float(v[0]) for k, v in t.items()}})
    Wu = np.hstack([np.ones((1, K)) / K, [[0.0]]])
    t = anchor_terms(gated_scores(A, hA, Wu), ia.utility.to_numpy(float), ia.dataset.to_numpy(), ia.op.to_numpy())
    t["tau_native"] = native_fidelity(gated_scores(M[:, cols], hM, Wu), im.native_value.to_numpy(float), model_idx, ds_idx, len(models), len(dss)); t["J"] = objective(t, ALPHA)
    base_rows.append({"baseline": "uniform_over_selected_no_gate", **{k: float(v[0]) for k, v in t.items()}})
    base_rows.append({"baseline": "ensemble_top100", **{k: ens["terms_ensemble_mean"][k] for k in ["rho", "auc", "js", "tau_native", "bad"]}, "J": float(top.J.mean())})
    pd.DataFrame(base_rows).to_csv(out / "baselines_grid.csv", index=False)
    print(top.head(5)[["rank", "J", "rho", "auc", "js", "tau_native", "bad"] + [f"w_{n}" for n in names] + ["lambda"]].round(3).to_string(index=False))
    print("ensemble mean weights:", {k: round(v, 3) for k, v in ens["mean_weights"].items()}, "mean lambda", round(ens["mean_lambda"], 2))
    print(pd.DataFrame(base_rows).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
