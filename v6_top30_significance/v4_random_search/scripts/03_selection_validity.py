#!/usr/bin/env python
"""
v4 step 3 - Nested selection / plateau / transfer / sensitivity over the candidate set of step 2 (reference = the v1 rubric).
Sensitivity uses explicit one-step lattice moves around the best and the reference because the design is sampled.
Outputs: output/selection/*
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from search.audit import evaluate_all, neighbours  # noqa: E402
from search.nested import nested_selection, transfer  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--boot", type=int, default=1000); args = ap.parse_args()
    idx = json.load(open(OUT / "tensors_index.json")); T = np.load(OUT / "tensors.npz"); COMP = idx["components"]; datasets, models, fam = idx["datasets"], idx["models"], idx["families"]
    X = {d: T[f"X_{d}"] for d in datasets}; EM = {d: T[f"EM_{d}"] for d in datasets}; NAT = {d: T[f"NAT_{d}"] for d in datasets}
    grid = pd.read_csv(OUT / "grid_candidates.csv"); WC = [f"w_{c}" for c in COMP]; W = grid[WC].to_numpy(float)
    i_ref = int(grid.index[grid.label == "v1_rubric"][0]); sel = OUT / "selection"
    nested = nested_selection(X, W, datasets, i_ref, sel, COMP, boot=args.boot, seed=0, ref_name="v1_rubric")
    tr = transfer(X, W, datasets, fam, i_ref, sel, COMP, ref_name="v1_rubric")
    sens = {}
    for name, c in [("v1_rubric", i_ref), ("best", 0)]:
        Nb = neighbours(W[c], 0.05)
        Jn = evaluate_all(Nb, X, EM, NAT, datasets, models, COMP, with_bt=False)[0].J.to_numpy() if len(Nb) else np.array([grid.J[c]])
        sens[name] = {"n_neighbours": int(len(Nb)), "J_centre": float(grid.J[c]), "J_min": float(Jn.min()), "J_max": float(Jn.max()), "J_mean": float(Jn.mean()),
                      "flatness_range": float(Jn.max() - Jn.min()), "share_neighbours_better": float((Jn > grid.J[c]).mean())}
    json.dump(sens, open(sel / "sensitivity.json", "w"), indent=2)
    print(json.dumps({k: nested[k] for k in ["in_bag_J_of_selected_mean", "out_of_bag_J_of_selected_mean", "optimism_gap", "out_of_bag_J_ref_mean", "plateau_size", "practical_plateau_size", "ref_in_practical_plateau"]}, indent=1))
    print(tr["lodo"][tr["lodo"].weights_from == "heldout_weights"][["held_out", "tau_heldout_mean"]].to_string(index=False))


if __name__ == "__main__":
    main()
