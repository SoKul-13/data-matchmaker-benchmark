#!/usr/bin/env python
"""
v3 step 1 - Compute the 100-metric matrix for (a) every real (model, item) pair and (b) every synthetic anchor.

Outputs (output/):
  matrix_models.npz   M (n_pairs x 100) + index_models.csv (model, dataset, uid, answer_type, native_metric, native_value)
  matrix_anchors.npz  A (n_anchor x 100) + index_anchors.csv (dataset, uid, answer_type, op, utility)
Datasets: enabled in config/datasets.toml; models only where predictions cover >= 90% of the real subset;
anchors for ALL enabled pools (no predictions needed).  --semantic enables the embedding family.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from anchors.ladder import Item, generate  # noqa: E402
from metrics.answer_types import AnswerType  # noqa: E402
from metrics.library import METRIC_NAMES, compute_all  # noqa: E402

NATIVE_COL = {"num_tol": "num_tol_1", "em": "em_norm", "rouge_l": "rouge_l"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semantic", action="store_true")
    ap.add_argument("--min-coverage", type=float, default=0.9)
    args = ap.parse_args()
    out = ROOT / "output"; out.mkdir(exist_ok=True)
    cfg = tomllib.loads((ROOT / "config" / "datasets.toml").read_text())
    enabled = [d["name"] for d in cfg["dataset"] if d.get("enabled", True)]
    pools = {}
    for d in enabled:
        f = ROOT / "data" / "pool" / f"{d}.jsonl"
        if f.exists():
            pools[d] = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
            pools[d] = [r for r in pools[d] if r.get("in_real_subset")]
    preds = {}
    for f in sorted((ROOT / "data" / "predictions").glob("*.jsonl")):
        for l in open(f, encoding="utf-8"):
            r = json.loads(l); preds[(r["model"], r["dataset"], r["uid"])] = r.get("prediction") or ""
    models = sorted({k[0] for k in preds})
    # ---- models
    rows, M = [], []
    for d, items in pools.items():
        cov = [it for it in items if all((m, d, it["uid"]) in preds for m in models)]
        if not cov or len(cov) < args.min_coverage * len(items):
            print(f"[{d}] models: pending ({len(cov)}/{len(items)} covered) -> anchors only")
            continue
        for it in cov:
            at = AnswerType(it["answer_type"])
            for m in models:
                v = compute_all(preds[(m, d, it["uid"])], it["ground_truth"], it.get("gold_aliases"), at, it.get("gold_list"), semantic=args.semantic)
                M.append(v)
                rows.append({"model": m, "dataset": d, "uid": it["uid"], "answer_type": at.value, "native_metric": it.get("native_metric", "em"),
                             "native_value": float(v[METRIC_NAMES.index(NATIVE_COL.get(it.get("native_metric", "em"), "em_norm"))])})
        print(f"[{d}] models: {len(cov)} items x {len(models)} models")
    M = np.asarray(M, dtype=np.float32)
    np.savez_compressed(out / "matrix_models.npz", M=M, names=np.array(METRIC_NAMES))
    pd.DataFrame(rows).to_csv(out / "index_models.csv", index=False)
    # ---- anchors
    arows, A = [], []
    for d, items in pools.items():
        its = [Item(r["uid"], d, r["ground_truth"], AnswerType(r["answer_type"]), r.get("gold_aliases") or [], r.get("gold_list")) for r in items]
        by_uid = {r["uid"]: r for r in items}
        for a in generate(its):
            r = by_uid[a["uid"]]
            v = compute_all(a["prediction"], r["ground_truth"], r.get("gold_aliases"), AnswerType(r["answer_type"]), r.get("gold_list"), semantic=args.semantic)
            A.append(v); arows.append({k: a[k] for k in ["dataset", "uid", "atype", "op", "utility"]})
        print(f"[{d}] anchors: {len(its)} items")
    A = np.asarray(A, dtype=np.float32)
    np.savez_compressed(out / "matrix_anchors.npz", A=A, names=np.array(METRIC_NAMES))
    pd.DataFrame(arows).to_csv(out / "index_anchors.csv", index=False)
    print(f"\nmodels matrix {M.shape}, anchors matrix {A.shape}")


if __name__ == "__main__":
    main()
