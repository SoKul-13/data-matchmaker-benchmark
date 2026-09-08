#!/usr/bin/env python
"""
Step 1 - Build the (model, dataset, item) component matrix from the ORIGINAL catalogue
datasets and the cached real-model predictions.

Datasets (7, all from the v1 catalogue): officeqa, finqa, tat_qa, tab_fact, financebench,
fetaqa, wikitablequestions.  Items = the 40-item real subset per dataset (data/pool/*.jsonl).
Predictions = data/predictions/<model>.jsonl (cached API outputs, no new calls).

Output: output/rs/components.npz  (M: n x 10 = 9 component metrics + hedge flag)
        output/rs/index.csv       (model, dataset, uid, answer_type, native_metric)
        output/rs/datasets.md     (dataset summary table)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from metrics import ALL_COLUMNS, AnswerType, component_vector  # noqa: E402

DATASETS = ["officeqa", "finqa", "tat_qa", "tab_fact", "financebench", "fetaqa", "wikitablequestions"]
DOMAIN = {
    "officeqa": ("U.S. Treasury Bulletins 1939-2025 (Databricks); closed-book", "document QA, numeric"),
    "finqa": ("SEC 10-K filings, table + text (EMNLP 2021)", "hybrid numeric reasoning"),
    "tat_qa": ("Financial reports, table + paragraphs (ACL 2021)", "hybrid: arithmetic / span / multi-span / count"),
    "tab_fact": ("Wikipedia tables, statement verification (ICLR 2020)", "boolean fact checking"),
    "financebench": ("10-K / 10-Q filings with evidence (Patronus 2023)", "document QA, numeric + text"),
    "fetaqa": ("Wikipedia tables, free-form answers (TACL 2022)", "generative table QA"),
    "wikitablequestions": ("Open-domain Wikipedia tables (ACL 2015)", "table QA, short answers / lists"),
}


def main():
    out = ROOT / "output" / "rs"
    out.mkdir(parents=True, exist_ok=True)
    items = {}
    for d in DATASETS:
        for l in open(ROOT / "data" / "pool" / f"{d}.jsonl", encoding="utf-8"):
            r = json.loads(l)
            if r.get("in_real_subset"):
                items[(d, r["uid"])] = r
    preds = {}
    for f in sorted((ROOT / "data" / "predictions").glob("*.jsonl")):
        for l in open(f, encoding="utf-8"):
            r = json.loads(l)
            if (r["dataset"], r["uid"]) in items:
                preds[(r["model"], r["dataset"], r["uid"])] = r
    models = sorted({k[0] for k in preds})
    rows, M = [], []
    for m in models:
        for (d, uid), it in items.items():
            p = preds.get((m, d, uid))
            text = (p or {}).get("prediction") or ""
            v = component_vector(text, it["ground_truth"], it.get("gold_aliases"), AnswerType(it["answer_type"]), gold_list=it.get("gold_list"))
            M.append(v)
            rows.append({"model": m, "dataset": d, "uid": uid, "answer_type": it["answer_type"],
                         "native_metric": it.get("native_metric", "em"), "missing": p is None or bool(p.get("error"))})
    M = np.asarray(M, dtype=np.float32)
    idx = pd.DataFrame(rows)
    np.savez_compressed(out / "components.npz", M=M, columns=np.array(ALL_COLUMNS))
    idx.to_csv(out / "index.csv", index=False)
    # dataset summary
    lines = ["| Dataset | Source / domain | Task type | Items | Answer types |", "|---|---|---|---|---|"]
    for d in DATASETS:
        sub = idx[(idx.dataset == d) & (idx.model == models[0])]
        mix = ", ".join(f"{k} {v}" for k, v in sub.answer_type.value_counts().items())
        lines.append(f"| {d} | {DOMAIN[d][0]} | {DOMAIN[d][1]} | {len(sub)} | {mix} |")
    (out / "datasets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"models={models}\npairs={len(idx)} missing={int(idx.missing.sum())}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
