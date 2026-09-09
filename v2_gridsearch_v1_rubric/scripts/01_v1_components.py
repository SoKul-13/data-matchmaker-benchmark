#!/usr/bin/env python
"""
v2 step 1 - Compute the FOUR v1 rubric components for every cached (model, item) pair.

v1 scored an answer as  R = 0.35*F1 + 0.35*exp(-2.5*MRE) + 0.15*Precision + 0.15*Recall  with hand-set weights.
Here we only compute the four ingredients (token F1, numeric decay, token precision, token recall) plus the
dataset's native metric, using the fixed gold handling (aliases, units, lists).  Weights come in step 2.
Output: output/components_v1.csv  (model, dataset, uid, answer_type, native_value, f1, decay, precision, recall)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from metrics import AnswerType, component_dict  # noqa: E402

NATIVE = {"num_tol": "num_tol", "em": "em", "rouge_l": "rouge_l"}


def main():
    out = ROOT / "output"; out.mkdir(exist_ok=True)
    preds = {}
    for f in sorted((ROOT / "data" / "predictions").glob("*.jsonl")):
        for l in open(f, encoding="utf-8"):
            r = json.loads(l); preds[(r["model"], r["dataset"], r["uid"])] = r.get("prediction") or ""
    models = sorted({k[0] for k in preds})
    rows = []
    for f in sorted((ROOT / "data" / "pool").glob("*.jsonl")):
        items = [json.loads(l) for l in open(f, encoding="utf-8")]
        items = [it for it in items if it.get("in_real_subset") and all((m, f.stem, it["uid"]) in preds for m in models)]
        if not items:
            print(f"[{f.stem}] no predictions; skipped"); continue
        for it in items:
            at = AnswerType(it["answer_type"])
            for m in models:
                d = component_dict(preds[(m, f.stem, it["uid"])], it["ground_truth"], it.get("gold_aliases"), at, gold_list=it.get("gold_list"))
                rows.append({"model": m, "dataset": f.stem, "uid": it["uid"], "answer_type": at.value, "native_value": d[NATIVE.get(it.get("native_metric", "em"), "em")],
                             "f1": d["tok_f1"], "decay": d["num_decay"], "precision": d["tok_prec"], "recall": d["tok_rec"]})
        print(f"[{f.stem}] {len(items)} items x {len(models)} models")
    df = pd.DataFrame(rows); df.to_csv(out / "components_v1.csv", index=False)
    print(df.groupby("dataset")[["f1", "decay", "precision", "recall", "native_value"]].mean().round(3).to_string())


if __name__ == "__main__":
    main()
