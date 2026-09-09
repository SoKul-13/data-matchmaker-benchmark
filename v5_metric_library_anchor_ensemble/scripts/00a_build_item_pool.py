#!/usr/bin/env python
"""
Step 0a - Build / extend the item pool (data/pool/<dataset>.jsonl) from config/datasets.toml.

Existing pool files are left untouched (their cached predictions stay valid) unless --force.
Each new pool: adapter -> stratified sample of pool_size items (seeded) -> answer type detection
-> in_real_subset = True for all (they are what the models will see).

Usage: uv run python scripts/rs/00a_build_item_pool.py [--datasets a,b] [--force]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import tomllib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from adapters import AdapterRegistry  # noqa: E402
from metrics.answer_types import detect_answer_type  # noqa: E402

FETCH_HEAVY = {"tab_fact", "wikitablequestions", "fetaqa", "hitab", "docfinqa", "abt_buy", "amazon_google", "dblp_scholar",
               "walmart_amazon", "wdc_products", "tpcdi_cells", "multihiertt"}


def stratified_sample(items, n, key, rng):
    if not key or len(items) <= n:
        rng.shuffle(items)
        return items[:n]
    groups = defaultdict(list)
    for it in items:
        groups[str(it.get(key))].append(it)
    for g in groups.values():
        rng.shuffle(g)
    out, i, keys = [], 0, sorted(groups)
    while len(out) < n and any(groups[k] for k in keys):
        k = keys[i % len(keys)]
        if groups[k]:
            out.append(groups[k].pop())
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    cfg = tomllib.loads((ROOT / "config" / "datasets.toml").read_text())
    g = cfg["global"]
    only = {s for s in args.datasets.split(",") if s}
    out_dir = ROOT / "data" / "pool"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for d in cfg["dataset"]:
        name = d["name"]
        if only and name not in only:
            continue
        if not d.get("enabled", True):
            print(f"[{name}] disabled in config; skipped")
            continue
        path = out_dir / f"{name}.jsonl"
        if path.exists() and not args.force:
            n = sum(1 for _ in open(path))
            print(f"[{name}] pool exists ({n} items); kept (use --force to rebuild)")
            continue
        pool_n = int(d.get("pool_size", g["pool_size"]))
        real_n = int(d.get("real_size", pool_n))
        adapter_cfg = {"dataset_name": name, "seed": g["seed"]}
        if name in FETCH_HEAVY:
            adapter_cfg["num_questions"] = pool_n * 2 if not d.get("stratify") else pool_n * 3
        print(f"[{name}] loading ...", flush=True)
        try:
            items = AdapterRegistry.get_adapter(name).load_questions(adapter_cfg)
        except Exception as e:
            print(f"[{name}] FAILED: {e}")
            continue
        if not items:
            print(f"[{name}] no items" + (" (optional; skipped)" if d.get("optional") else ""))
            continue
        rows = [it.model_dump() for it in items]
        rng = random.Random(f"{g['seed']}-{name}")
        pool = stratified_sample(rows, pool_n, d.get("stratify"), rng)
        hint = d.get("hint")
        for r in pool:
            at = detect_answer_type(r["ground_truth"], r.get("gold_aliases"), dataset_hint=r.get("answer_type") or hint, gold_list=r.get("gold_list"))
            r["answer_type"] = at.value
            if r.get("native_metric") == "auto":
                r["native_metric"] = {"numeric": "num_tol", "boolean": "em", "text": "em", "freeform": "rouge_l"}[at.value]
            r["dataset_name"] = name
        real = stratified_sample(list(pool), real_n, "answer_type", random.Random(f"{g['seed']}-{name}-real"))
        real_ids = {r["uid"] for r in real}
        for r in pool:
            r["in_real_subset"] = r["uid"] in real_ids
        pool.sort(key=lambda r: (not r["in_real_subset"], r["uid"]))
        with open(path, "w", encoding="utf-8") as f:
            for r in pool:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        types = Counter(r["answer_type"] for r in pool)
        gold_balance = Counter(r["ground_truth"] for r in pool if r["answer_type"] == "boolean")
        print(f"[{name}] loaded={len(rows)} pool={len(pool)} real={len(real)} types={dict(types)}" + (f" yes/no={dict(gold_balance)}" if gold_balance else ""))
        summary.append({"dataset": name, "tier": d.get("tier"), "loaded": len(rows), "pool": len(pool), "real": len(real), "types": dict(types)})
    with open(out_dir / "_summary_new.json", "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
