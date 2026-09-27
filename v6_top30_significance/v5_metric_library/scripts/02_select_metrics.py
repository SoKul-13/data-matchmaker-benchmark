#!/usr/bin/env python
"""
v3 step 2 - Deduplicate the 100 metrics and select the k that carry information about answer quality.

Anchor: synthetic known-quality answers (utility u per operator) by default; --labels file.csv
(columns uid,dataset,model,label in {0,0.5,1}) switches the anchor to human labels on real answers.
Steps: (1) drop constant metrics, cluster |Spearman| >= 0.95 -> representatives; (2) per-metric agreement
with the anchor (rho, AUC); (3) forward selection maximising leave-one-dataset-out Spearman of an NNLS fit.
Outputs: output/metric_table.csv, output/clusters.json, output/selected.json
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
from calibration.select import anchor_agreement, dedupe, fit_nnls, forward_select, lodo_rho  # noqa: E402
from metrics.library import FAMILIES, METRIC_NAMES  # noqa: E402

PREFER = ["native_style_metric", "em_norm", "num_tol_1", "tok_f1", "rouge_l", "lev_sim", "num_decay_2p5", "jaccard", "tok_rec", "tok_prec", "chrf3", "bleu2", "hedge_free"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default=None)
    ap.add_argument("--k-max", type=int, default=10)
    ap.add_argument("--thresh", type=float, default=0.95)
    args = ap.parse_args()
    out = OUT
    if args.labels:
        M = np.load(out / "matrix_models.npz")["M"]; idx = pd.read_csv(out / "index_models.csv")
        lab = pd.read_csv(args.labels)
        m = idx.merge(lab, on=["uid", "dataset", "model"], how="inner")
        A, u, groups = M[m.index.to_numpy()], m["label"].to_numpy(float), m["dataset"].to_numpy()
        anchor = f"human labels ({len(u)} answers)"
    else:
        A = np.load(out / "matrix_anchors.npz")["A"]; ia = pd.read_csv(out / "index_anchors.csv")
        u, groups = ia["utility"].to_numpy(float), ia["dataset"].to_numpy()
        anchor = f"synthetic anchors ({len(u)} answers, {ia.op.nunique()} operators)"
    keep, clusters = dedupe(A, METRIC_NAMES, args.thresh, PREFER)
    agr = anchor_agreement(A, u, groups)
    agr.insert(0, "metric", METRIC_NAMES)
    agr["family"] = [next(f for f, ms in FAMILIES.items() if n in ms) for n in METRIC_NAMES]
    agr["representative"] = [j in keep for j in range(len(METRIC_NAMES))]
    agr["cluster"] = [next((rep for rep, ms in clusters.items() if n in ms), "_constant") for n in METRIC_NAMES]
    agr.sort_values("rho", ascending=False).to_csv(out / "metric_table.csv", index=False)
    GATE_FAMILIES = {"structure", "commit", "length"}      # indicators (1 for most wrong answers) act as constant offsets; used as a gate instead
    cands = [j for j in keep if agr.loc[j, "rho"] > 0.05 and agr.loc[j, "auc"] > 0.55 and agr.loc[j, "family"] not in GATE_FAMILIES]
    selected, trace = forward_select(A, u, groups, cands, args.k_max)
    w = fit_nnls(A[:, selected], u)
    res = {"anchor": anchor, "n_metrics": len(METRIC_NAMES), "n_constant": len(clusters.get("_constant", [])), "n_representatives": len(keep),
           "n_candidates": len(cands), "selected": [METRIC_NAMES[j] for j in selected], "selected_idx": selected,
           "nnls_weights": {METRIC_NAMES[j]: float(x) for j, x in zip(selected, w)}, "trace": [{**t, "added": METRIC_NAMES[t["added"]]} for t in trace],
           "lodo_rho_selected": lodo_rho(A, u, groups, selected), "lodo_rho_native_only": lodo_rho(A, u, groups, [METRIC_NAMES.index("native_style_metric")]),
           "lodo_rho_em_only": lodo_rho(A, u, groups, [METRIC_NAMES.index("em_norm")])}
    json.dump(res, open(out / "selected.json", "w"), indent=2)
    json.dump(clusters, open(out / "clusters.json", "w"), indent=2)
    print(f"anchor: {anchor}\nconstant: {res['n_constant']}  representatives: {len(keep)}  candidates: {len(cands)}")
    print("top metrics by anchor rho:\n", agr.sort_values("rho", ascending=False).head(12)[["metric", "family", "rho", "auc", "representative"]].round(3).to_string(index=False))
    print("\nselected:", res["selected"]); print("nnls weights:", {k: round(v, 3) for k, v in res["nnls_weights"].items()})
    print(f"LODO rho: selected {res['lodo_rho_selected']:.3f} | native-only {res['lodo_rho_native_only']:.3f} | em-only {res['lodo_rho_em_only']:.3f}")


if __name__ == "__main__":
    main()
