#!/usr/bin/env python
"""
Census of every dataset's OFFICIAL population: how many items each stratum has in the split the adapter reads (test / dev), so
per-dataset scores on our stratified pool can be post-stratified into official-split estimates (shared/src/stats/poststrat.py).

For each enabled dataset: load the adapter with {"census": True} and no cap -> the whole labelled population (balanced adapters
return every pair; capped adapters return every item) -> count strata with the SAME rule the pool uses:
  boolean matching sets      -> gold label (yes / no)            [official class ratio]
  sets with a stratify key   -> that key (difficulty = task / sub-benchmark / question type / database ...)
  everything else            -> detected answer type
Comparability notes are hard-coded per dataset where the population is not the published benchmark (constructed pairs, trimmed
candidate lists, task subsets, changed grading).  Output: data/pool/_official_strata.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "shared" / "src"))
DATA, CONFIG = ROOT / "data", ROOT / "config"
from adapters.adapter_registry import AdapterRegistry  # noqa: E402
from metrics.answer_types import detect_answer_type  # noqa: E402
from stats.poststrat import stratum_of  # noqa: E402

# population notes: comparable = the census population IS the published split (up to our answer-format filters)
NOTES = {
    "alaska_camera": (False, "pairs constructed from entity clusters (hard negatives by title overlap); no official pair split"),
    "alaska_schema": (True, "monitor half of the schema-matching gold only (camera GT unavailable)"),
    "valentine": (True, "4 table pairs per (sub-benchmark x pair type) + all Magellan / WikiData pairs; per-column framing, candidates trimmed to budget"),
    "magneto_gdc": (True, "per-column framing; 40 candidate targets shown of 736"),
    "smat": (True, "per-column framing; 10 candidates (true + 9 hard negatives)"),
    "fintagging": (True, "FinCL only; 10 candidate concepts shown"),
    "bird": (True, "questions whose gold SQL returns 1-5 short cells; graded on the result value, not on SQL execution accuracy"),
    "mmtu": (True, "9 of 25 MMTU tasks (short deterministic golds only)"),
    "realhitbench": (True, "Fact Checking + Numerical Reasoning only (Structure Comprehending golds are empty in the release; Data Analysis / Visualization are free text)"),
    "suc": (True, "SUC tasks regenerated from the TableProvider source tables (no released item file)"),
    "tabis": (True, "zero-shot, three strata"), "tableeval": (True, "8 short-gold sub-tasks, single-turn only"), "tablebench": (True, "FactChecking + NumericalReasoning only"),
    "officeqa": (False, "closed-book run; every model at floor"), "officeqa_pro_v2": (True, "all 90 questions; referenced pages in context"),
    "opensanctions_pairs": (True, "population = the dataset's stratified sample_1000.json, not the full 390 MB pair file"),
    "wdc_products": (True, "WDC Products 2024 test split at the fetched size"), "tpcdi_cells": (True, "the benchmark's own cell task; population = all generated cells"),
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--datasets", default=""); ap.add_argument("--force", action="store_true"); args = ap.parse_args()
    cfg = tomllib.loads((CONFIG / "datasets.toml").read_text()); g = cfg["global"]; out_path = DATA / "pool" / "_official_strata.json"
    strata = json.load(open(out_path)) if out_path.exists() else {}
    only = {x.strip() for x in args.datasets.split(",") if x.strip()}
    for d in cfg["dataset"]:
        name = d["name"]
        if (only and name not in only) or not d.get("enabled", True) or (name in strata and not args.force):
            continue
        key = d.get("stratify"); t0 = time.time(); print(f"[{name}] census ...", flush=True)
        try:
            items = AdapterRegistry.get_adapter(name).load_questions({"dataset_name": name, "seed": g["seed"], "census": True})
        except Exception as e:  # noqa: BLE001
            strata[name] = {"key": key, "counts": {}, "n": 0, "comparable": False, "note": f"census failed: {e}"}; print(f"[{name}] FAILED: {e}"); continue
        rows = [it.model_dump() for it in items]
        for r in rows:
            if not r.get("answer_type"):
                r["answer_type"] = detect_answer_type(r["ground_truth"], r.get("gold_aliases"), dataset_hint=d.get("hint"), gold_list=r.get("gold_list")).value
        counts = Counter(stratum_of(name, r, key) for r in rows)
        comp, note = NOTES.get(name, (True, "official split"))
        n_pos = sum(c for k, c in counts.items() if k == "yes" or k.endswith("|yes")); is_pairs = all(k in ("yes", "no") or k.endswith(("|yes", "|no")) for k in counts)
        strata[name] = {"key": key if key else ("gold_label" if is_pairs else "answer_type"), "counts": dict(counts), "n": len(rows), "comparable": comp, "note": note,
                        "official_positive_share": (n_pos / len(rows)) if is_pairs and rows else None, "census_time_s": round(time.time() - t0, 1)}
        print(f"[{name}] n={len(rows)} strata={dict(counts) if len(counts) <= 12 else f'{len(counts)} strata'} ({time.time() - t0:.0f}s)")
        json.dump(strata, open(out_path, "w"), indent=2)
    json.dump(strata, open(out_path, "w"), indent=2); print("wrote", out_path)


if __name__ == "__main__":
    main()
