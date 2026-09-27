#!/usr/bin/env python
"""v4 step 5 - leaderboards + params + bootstrap + significance under: em_only, v1_rubric, top1..top5, best_anchor, pareto_knee; rule agreement; diagnostics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from stats.leaderboard import dataset_diagnostics, majority_baselines, poststrat_for, report_rule, rule_agreement, summary_of  # noqa: E402


def main():
    idx = json.load(open(OUT / "tensors_index.json")); T = np.load(OUT / "tensors.npz"); COMP = idx["components"]; datasets, models, fam = idx["datasets"], idx["models"], idx["families"]
    X = {d: T[f"X_{d}"] for d in datasets}; grid = pd.read_csv(OUT / "grid_candidates.csv"); corr = pd.read_csv(OUT / "anchors" / "correctness.csv"); WC = [f"w_{c}" for c in COMP]
    ck = json.load(open(OUT / "anchors" / "correctness.json"))["pareto_knee"]["weights"]
    rules = {"em_only": grid[grid.label == "em_only"].iloc[0][WC].to_numpy(float), "v1_rubric": grid[grid.label == "v1_rubric"].iloc[0][WC].to_numpy(float)}
    for i in range(5):
        rules[f"top{i + 1}"] = grid.iloc[i][WC].to_numpy(float)
    rules["best_anchor"] = corr.loc[corr.rho.idxmax(), WC].to_numpy(float); rules["pareto_knee"] = np.array([ck[c] for c in COMP])
    maj = majority_baselines(DATA / "pool", datasets); results = {}; weights = {}; ps = poststrat_for(DATA / "pool", datasets, idx["uids"])
    for name, w in rules.items():
        items = [np.einsum("nmk,k->nm", np.nan_to_num(X[d]), w) for d in datasets]; weights[name] = dict(zip(COMP, np.round(w, 2).tolist()))
        results[name] = report_rule(name, items, datasets, models, fam, OUT / "leaderboards" / name, weights=weights[name], majority=maj, poststrat=ps)
        print(f"[{name}] BT ranking: " + ", ".join(f"{m}={int(r)}" for m, r in zip(models, results[name]["rank_bt"])))
    rule_agreement(results).to_csv(OUT / "leaderboards" / "rule_agreement.csv"); json.dump(summary_of(results, models, weights), open(OUT / "leaderboards" / "summary.json", "w"), indent=2)
    diag = dataset_diagnostics(results["v1_rubric"], datasets, models, fam, OUT / "diagnostics", label="v1 rubric")
    print(diag[["dataset", "mean_score", "spread_across_models", "ranking_self_stability_tau", "exclude_from_objective"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
