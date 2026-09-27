#!/usr/bin/env python
"""v4 step 4 - correctness of every candidate on v5's known-utility anchors (nine components).  Outputs: output/anchors/*"""
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
from metrics import AnswerType, COMPONENT_NAMES, component_dict  # noqa: E402
from search.audit import anchor_components, correctness  # noqa: E402

COMP = list(COMPONENT_NAMES)


def comp_fn(pred, r):
    c = component_dict(pred, r["ground_truth"], r.get("gold_aliases"), AnswerType(r["answer_type"]), gold_list=r.get("gold_list"))
    return {k: c[k] for k in COMP + ["hedge_free"]}


def main():
    idx = json.load(open(OUT / "tensors_index.json")); datasets = idx["datasets"]
    A = anchor_components(DATA / "pool", datasets, comp_fn, OUT / "anchors" / "anchor_components.csv")
    grid = pd.read_csv(OUT / "grid_candidates.csv"); W = grid[[f"w_{c}" for c in COMP]].to_numpy(float)
    s = correctness(A, COMP, W, grid, OUT / "anchors", ref_label="v1_rubric", extra_rules={"exact_match": A.em.to_numpy(float)})
    print(json.dumps({k: s[k] for k in ["reference", "best_J", "best_rho", "pareto_knee", "extra_rules", "spearman_J_vs_rho_across_candidates"]}, indent=1))


if __name__ == "__main__":
    main()
