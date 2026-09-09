#!/usr/bin/env python
"""v3 step 1 - per-item score with each dataset's OWN metric (accuracy / EM / 1% numeric tolerance / ROUGE-L).
Output: output/native_item_scores.csv (model, dataset, uid, answer_type, metric, score) and the random baseline per dataset."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from metrics import AnswerType, component_dict  # noqa: E402


def main():
    out = ROOT / "output"; out.mkdir(exist_ok=True)
    preds = {}
    for f in sorted((ROOT / "data" / "predictions").glob("*.jsonl")):
        for l in open(f, encoding="utf-8"):
            r = json.loads(l); preds[(r["model"], r["dataset"], r["uid"])] = r.get("prediction") or ""
    models = sorted({k[0] for k in preds}); rows, baseline = [], {}
    for f in sorted((ROOT / "data" / "pool").glob("*.jsonl")):
        items = [json.loads(l) for l in open(f, encoding="utf-8")]
        items = [it for it in items if it.get("in_real_subset") and all((m, f.stem, it["uid"]) in preds for m in models)]
        if not items:
            continue
        n_bool = sum(1 for it in items if it["answer_type"] == "boolean")
        baseline[f.stem] = 0.5 * n_bool / len(items)          # random-guess score: 1/2 on yes/no items, 0 elsewhere
        for it in items:
            at = AnswerType(it["answer_type"]); metric = it.get("native_metric", "em")
            for m in models:
                d = component_dict(preds[(m, f.stem, it["uid"])], it["ground_truth"], it.get("gold_aliases"), at, gold_list=it.get("gold_list"))
                rows.append({"model": m, "dataset": f.stem, "uid": it["uid"], "answer_type": at.value, "metric": metric, "score": d[metric]})
        print(f"[{f.stem}] {len(items)} items, native metric(s) {sorted({it.get('native_metric') for it in items})}, random baseline {baseline[f.stem]:.2f}")
    pd.DataFrame(rows).to_csv(out / "native_item_scores.csv", index=False)
    json.dump(baseline, open(out / "random_baseline.json", "w"), indent=2)


if __name__ == "__main__":
    main()
