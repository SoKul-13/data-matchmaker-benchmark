#!/usr/bin/env python
"""
v4 step 1 - the nine composite components (em, num_tol, num_decay, tok_prec, tok_rec, tok_f1, edit_sim, rouge_l, jaccard) + hedge flag +
native metric for every cached (model, item) pair.  Coverage rule as in v2 (model used if it answered >= 90 % of the real subset).
Output: output/components.csv, output/coverage.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from metrics import AnswerType, COMPONENT_NAMES, component_dict  # noqa: E402
from families import family_of  # noqa: E402

NATIVE = {"num_tol": "num_tol", "em": "em", "rouge_l": "rouge_l"}


def main():
    OUT.mkdir(exist_ok=True)
    import tomllib
    enabled = {d["name"] for d in tomllib.loads((CONFIG / "datasets.toml").read_text())["dataset"] if d.get("enabled", True)}
    pools = {p.stem: [json.loads(l) for l in open(p, encoding="utf-8")] for p in sorted((DATA / "pool").glob("*.jsonl")) if p.stem in enabled}
    preds = {}
    for f in sorted((DATA / "predictions").glob("*.jsonl")):
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if not r.get("error"):
                preds[(r["model"], r["dataset"], r["uid"])] = r.get("prediction") or ""
    all_models = sorted({k[0] for k in preds})
    # global coverage rule: a model enters the study only if it answered >= 90 % of all answered (dataset, item) pairs across the suite;
    # a model with a partial run (e.g. a daily quota) is left out entirely instead of appearing with missing cells
    _pairs = {(d, r["uid"]) for d, items in pools.items() for r in items if r.get("in_real_subset") and any((m, d, r["uid"]) in preds for m in all_models)}
    _cov = {m: sum((m, d, u) in preds for d, u in _pairs) / max(1, len(_pairs)) for m in all_models}
    dropped_models = {m: round(c, 3) for m, c in _cov.items() if c < 0.9}; all_models = [m for m in all_models if _cov[m] >= 0.9]
    if dropped_models: print("models left out (suite coverage < 90 %):", dropped_models); rows, cov = [], {}
    for d, items in pools.items():
        real = [r for r in items if r.get("in_real_subset")]
        if not real:
            continue
        answered = [r for r in real if any((m, d, r["uid"]) in preds for m in all_models)]          # items at least one model has answered
        used = list(all_models)   # complete score matrices: every model in the study, items kept only when all of them answered
        real = answered if len(answered) >= 20 else []                                            # need >= 20 answered items to count a dataset
        kept = [r for r in real if all((m, d, r["uid"]) in preds for m in used)] if used else []
        cov[d] = {"real_items": len(real), "answered_items": len(answered), "models_used": used, "items_kept": len(kept)}
        if not kept:
            print(f"[{d}] pending"); continue
        for r in kept:
            at = AnswerType(r["answer_type"]); nm = r.get("native_metric", "em")
            for m in used:
                c = component_dict(preds[(m, d, r["uid"])], r["ground_truth"], r.get("gold_aliases"), at, gold_list=r.get("gold_list"))
                rows.append({"model": m, "dataset": d, "family": family_of(d), "uid": r["uid"], "answer_type": at.value, "native_metric": nm, "native_value": c[NATIVE.get(nm, "em")],
                             **{k: c[k] for k in COMPONENT_NAMES}, "hedge_free": c["hedge_free"]})
        print(f"[{d}] {len(kept)} items x {len(used)} models")
    df = pd.DataFrame(rows); df.to_csv(OUT / "components.csv", index=False); cov["_models_left_out"] = dropped_models; json.dump(cov, open(OUT / "coverage.json", "w"), indent=2)
    print(f"\n{len(df)} rows; datasets {df.dataset.nunique()}, models {df.model.nunique()}")


if __name__ == "__main__":
    main()
