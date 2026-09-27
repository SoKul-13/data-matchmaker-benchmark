#!/usr/bin/env python
"""
v3 step 5 - Validation of the selection + weights.
  (a) leave-one-dataset-out: re-run selection and grid without dataset d, evaluate the resulting ensemble on d
      (anchor Spearman, AUC, and the held-out dataset's JS to the rest) vs the full-data ensemble;
  (b) severity-scale perturbation: utilities +-0.15 (identity fixed at 1, wrong/abstain at 0), 5 draws -> L1 shift of
      the ensemble mean weights and change of the selected set;
  (c) gaming probes: mean ensemble score per anchor operator vs its utility, and vs single-metric baselines.
Outputs: output/validation.json, output/probes.csv, output/lodo.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]          # this version's folder (output/ lives here)
V6 = ROOT.parent                                     # the shared v6 folder (shared/src, data/, config/)
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from anchors.ladder import UTILITY  # noqa: E402
from calibration.grid import anchor_terms, gated_scores, native_fidelity, objective, simplex_grid, with_gate  # noqa: E402
from calibration.select import dedupe, anchor_agreement, forward_select  # noqa: E402
from metrics.library import METRIC_NAMES  # noqa: E402

ALPHA = {"rho": 0.30, "auc": 0.15, "consistency": 0.20, "native": 0.15, "bad": 0.20}
PREFER = ["native_style_metric", "em_norm", "num_tol_1", "tok_f1", "rouge_l", "lev_sim", "num_decay_2p5", "jaccard", "tok_rec", "tok_prec", "chrf3", "bleu2", "hedge_free"]


HCOL = METRIC_NAMES.index("hedge_free")
GATE_FAMILIES = {"structure", "commit", "length"}
from metrics.library import FAMILIES  # noqa: E402
_FAM = {n: f for f, ms in FAMILIES.items() for n in ms}


def calibrate(A, u, groups, ops, M, native, model_idx, ds_idx, n_models, n_ds, top=100, k_max=8):
    keep, _ = dedupe(A, METRIC_NAMES, 0.95, PREFER)
    agr = anchor_agreement(A, u, groups)
    cands = [j for j in keep if agr.loc[j, "rho"] > 0.05 and agr.loc[j, "auc"] > 0.55 and _FAM[METRIC_NAMES[j]] not in GATE_FAMILIES]
    sel, _ = forward_select(A, u, groups, cands, k_max)
    K = len(sel); step = 0.02 if K <= 3 else 0.05 if K <= 6 else 0.1
    W = with_gate(simplex_grid(K, step))
    Js = []
    for i in range(0, len(W), 256):
        Wb = W[i:i + 256]
        t = anchor_terms(gated_scores(A[:, sel], A[:, HCOL], Wb), u, groups, ops)
        t["tau_native"] = native_fidelity(gated_scores(M[:, sel], M[:, HCOL], Wb), native, model_idx, ds_idx, n_models, n_ds) if M is not None else np.zeros(len(Wb))
        Js.append(objective(t, ALPHA))
    J = np.concatenate(Js); order = np.argsort(-J)[:top]
    return sel, W[order]


def ens_scores(A, sel, Wtop):
    return gated_scores(A[:, sel], A[:, HCOL], Wtop).mean(1)


def main():
    out = OUT
    A = np.load(out / "matrix_anchors.npz")["A"]; ia = pd.read_csv(out / "index_anchors.csv")
    M = np.load(out / "matrix_models.npz")["M"]; im = pd.read_csv(out / "index_models.csv")
    ens = json.load(open(out / "ensemble.json")); sel_full = ens["selected_idx"]; Wfull = np.array(ens["top_weightings"])
    u, groups, ops = ia.utility.to_numpy(float), ia.dataset.to_numpy(), ia.op.to_numpy()
    models, dss = sorted(im.model.unique()), sorted(im.dataset.unique())
    model_idx, ds_idx = im.model.map({m: i for i, m in enumerate(models)}).to_numpy(), im.dataset.map({d: i for i, d in enumerate(dss)}).to_numpy()
    native = im.native_value.to_numpy(float)
    full_score = ens_scores(A, sel_full, Wfull)
    # ---- (a) LODO
    lodo = []
    for d in sorted(set(groups)):
        tr, te = groups != d, groups == d
        mtr = (im.dataset != d).to_numpy()
        sel_d, W_d = calibrate(A[tr], u[tr], groups[tr], ops[tr], M[mtr], native[mtr], model_idx[mtr], ds_idx[mtr], len(models), len(dss))
        s_lodo = ens_scores(A[te], sel_d, W_d); s_full = full_score[te]
        rho_l = stats.spearmanr(s_lodo, u[te]).correlation; rho_f = stats.spearmanr(s_full, u[te]).correlation
        # held-out JS to the rest at matched op, under LODO ensemble applied to all anchors
        s_all = ens_scores(A, sel_d, W_d)
        t = anchor_terms(s_all[:, None], u, groups, ops)
        lodo.append({"held_out": d, "selected_lodo": [METRIC_NAMES[j] for j in sel_d], "rho_heldout_lodo": float(rho_l), "rho_heldout_full": float(rho_f),
                     "js_all_lodo": float(t["js"][0]), "same_selection": sorted(sel_d) == sorted(sel_full)})
        print(f"LODO {d:20s} rho held-out: lodo {rho_l:.3f} full {rho_f:.3f} | selected {[METRIC_NAMES[j] for j in sel_d]}")
    pd.DataFrame(lodo).to_csv(out / "lodo.csv", index=False)
    # ---- (b) severity perturbation
    rng = np.random.default_rng(0); shifts, sel_changes = [], []
    mean_w_full = np.zeros(len(METRIC_NAMES)); mean_w_full[sel_full] = Wfull[:, :-1].mean(0)
    for rep in range(5):
        pert = np.clip(u + rng.uniform(-0.15, 0.15, len(u)), 0, 1); pert = np.where(u >= 0.999, 1.0, np.where(u <= 0.001, 0.0, pert))
        sel_p, W_p = calibrate(A, pert, groups, ops, M, native, model_idx, ds_idx, len(models), len(dss))
        mw = np.zeros(len(METRIC_NAMES)); mw[sel_p] = W_p[:, :-1].mean(0)
        shifts.append(float(np.abs(mw - mean_w_full).sum())); sel_changes.append(sorted(sel_p) != sorted(sel_full))
    # ---- (c) probes: mean ensemble score per operator vs utility
    df = ia.assign(ens=full_score, em=A[:, METRIC_NAMES.index("em_norm")], native=A[:, METRIC_NAMES.index("native_style_metric")], f1=A[:, METRIC_NAMES.index("tok_f1")])
    probes = df.groupby("op").agg(utility=("utility", "first"), n=("ens", "size"), ensemble=("ens", "mean"), em=("em", "mean"), native=("native", "mean"), tok_f1=("f1", "mean")).reset_index()
    probes["abs_err_ensemble"] = (probes.ensemble - probes.utility).abs(); probes = probes.sort_values("utility", ascending=False)
    probes.round(3).to_csv(out / "probes.csv", index=False)
    val = {"lodo_mean_rho_lodo": float(np.mean([r["rho_heldout_lodo"] for r in lodo])), "lodo_mean_rho_full": float(np.mean([r["rho_heldout_full"] for r in lodo])),
           "lodo_same_selection_share": float(np.mean([r["same_selection"] for r in lodo])), "severity_l1_shift_mean": float(np.mean(shifts)), "severity_l1_shift_max": float(np.max(shifts)),
           "severity_selection_changed_share": float(np.mean(sel_changes)), "probe_mae_ensemble": float(probes.abs_err_ensemble.mean()),
           "probe_mae_em": float((probes.em - probes.utility).abs().mean()), "probe_mae_native": float((probes.native - probes.utility).abs().mean()),
           "probe_mae_tok_f1": float((probes.tok_f1 - probes.utility).abs().mean())}
    json.dump(val, open(out / "validation.json", "w"), indent=2)
    print("\n", probes.round(2).to_string(index=False)); print("\n", json.dumps(val, indent=1))


if __name__ == "__main__":
    main()
