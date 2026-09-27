#!/usr/bin/env python
"""
v2 step 5 - leaderboards + parameters + bootstrap draws + significance + official-split estimates under: em_only, v1_original, top1..top5 (by J),
best_anchor, pareto_knee; rule agreement; dataset diagnostics.  All heavy lifting in shared stats.leaderboard.report_rule.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from stats.leaderboard import dataset_diagnostics, majority_baselines, poststrat_for, report_rule, rule_agreement, summary_of  # noqa: E402

COMP = ["f1", "decay", "precision", "recall"]; WC = [f"w_{c}" for c in COMP]
V1 = np.array([0.35, 0.35, 0.15, 0.15]); N_BOOT = 1000
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b"


def load():
    T = np.load(OUT / "tensors.npz", allow_pickle=True); idx = json.load(open(OUT / "tensors_index.json"))
    datasets, models, fam = idx["datasets"], idx["models"], idx["families"]
    X = {d: T[f"X_{d}"] for d in datasets}; EM = {d: T[f"EM_{d}"] for d in datasets}
    grid = pd.read_csv(OUT / "grid_exhaustive.csv"); corr = pd.read_csv(OUT / "anchors" / "correctness.csv")
    comp = pd.read_csv(OUT / "components_v1.csv")
    return datasets, models, fam, X, EM, grid, corr, comp


def rules_to_report(grid, corr):
    rules = {"em_only": None, "v1_original": V1}
    for i in range(5):
        rules[f"top{i + 1}"] = grid.iloc[i][WC].to_numpy(float)
    rules["best_anchor"] = corr.loc[corr.rho.idxmax(), WC].to_numpy(float)
    ck = json.load(open(OUT / "anchors" / "correctness.json"))["pareto_knee"]["weights"]; rules["pareto_knee"] = np.array([ck[c] for c in COMP])
    return rules


def item_matrices(rule_w, X, EM, datasets):
    if rule_w is None:
        return [EM[d] for d in datasets]
    return [np.einsum("nmk,k->nm", X[d], rule_w) for d in datasets]


def main():
    datasets, models, fam, X, EM, grid, corr, comp = load()
    uid_order = json.load(open(OUT / "tensors_index.json"))["uids"]; ps = poststrat_for(DATA / "pool", datasets, uid_order)
    rules = rules_to_report(grid, corr); results = {}
    for name, w in rules.items():
        items = item_matrices(w, X, EM, datasets); weights_d = None if w is None else dict(zip(COMP, np.round(w, 2).tolist()))
        results[name] = report_rule(name, items, datasets, models, fam, OUT / "leaderboards" / name, weights=weights_d, majority=majority_baselines(DATA / "pool", datasets), poststrat=ps)
        print(f"[{name}] BT ranking: " + ", ".join(f"{m}={int(r)}" for m, r in zip(models, results[name]['rank_bt'])))
    A = rule_agreement(results); A.to_csv(OUT / "leaderboards" / "rule_agreement.csv")
    json.dump(summary_of(results, models, {n: (None if w is None else dict(zip(COMP, np.round(w, 2).tolist()))) for n, w in rules.items()}), open(OUT / "leaderboards" / "summary.json", "w"), indent=2)
    diag = dataset_diagnostics(results["v1_original"], datasets, models, fam, OUT / "diagnostics", label="v1 rule")
    print("\nrule agreement (tau between BT rankings):\n", A.round(2).to_string()); print("\ndiagnostics:\n", diag[["dataset", "mean_score", "spread_across_models", "ranking_self_stability_tau", "exclude_from_objective"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
