"""WDC LSPC / Products-2017 product matching (Hugging Face `wdc/products-2017`), gold-standard test
splits of the four categories (computers, cameras, shoes, watches), read from the raw json.gz files.

Differs from `wdc_products` (which streams the first 300 rows per category through the datasets-server
API): here the full ~1,100-pair test set per category is used and any pair already in the
data/pool/wdc_products.jsonl pool is excluded, so the two suites do not share items.
One item per offer pair, gold yes / no, balanced within each category.
"""
import gzip
import json
import logging
import random
from pathlib import Path
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import V6, balanced_sample, clip, default_pool_n, ensure_file, hf_headers, hf_resolve, raw_dir, render_kv

logger = logging.getLogger(__name__)
CATEGORIES = ["computers", "cameras", "shoes", "watches"]
FIELDS = ["brand", "title", "description", "price", "specTableContent"]
QUESTION = "Do these two product offers (from different web shops) describe the same product? Answer yes or no."


def _clean(v):
    if v is None:
        return None
    import re
    s = str(v).strip()
    # WDC strings carry RDF-style quoting / language tags: "\"Gigabyte\"@en", "...\"@fr"
    s = re.sub(r'"\s*@[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?', "", s).replace('"', "").strip()
    return s or None


class WDCLSPCAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = raw_dir("wdc_lspc")
        excluded = set()
        other = V6 / "data" / "pool" / "wdc_products.jsonl"
        if other.exists():
            for line in open(other, encoding="utf-8"):
                excluded.add(json.loads(line)["uid"].replace("wdc_", "", 1))
        rows = []
        for cat in CATEGORIES:
            p = ensure_file(root / f"{cat}_test.json.gz", hf_resolve("wdc/products-2017", f"{cat}/test.json.gz"),
                            hint=f"Expected {cat}/test.json.gz from https://huggingface.co/datasets/wdc/products-2017",
                            headers=hf_headers())
            for line in gzip.open(p, "rt", encoding="utf-8"):
                r = json.loads(line)
                if r["pair_id"] in excluded:
                    continue
                r["_cat"] = cat
                rows.append(r)
        num_q, seed = int(config.get("num_questions") or default_pool_n("wdc_lspc")), config.get("seed", 0)
        rng = random.Random(seed)
        per_cat = max(2, -(-num_q // len(CATEGORIES)))  # ceil; per-category balanced
        chosen = []
        if config.get("census"):
            chosen = list(rows); per_cat = 0                 # census: every labelled test pair, official class ratio
        for cat in (CATEGORIES if per_cat else []):
            sub = [r for r in rows if r["_cat"] == cat]
            pos = [r for r in sub if str(r["label"]) == "1"]
            neg = [r for r in sub if str(r["label"]) == "0"]
            chosen += balanced_sample(pos, neg, per_cat, rng)
        rng.shuffle(chosen)
        out = []
        for r in chosen:
            def rec(side):
                return {k: _clean(r.get(f"{k}_{side}")) for k in FIELDS}
            label = "yes" if str(r["label"]) == "1" else "no"
            out.append(QuestionItem(
                uid=f"wdc_lspc_{r['pair_id']}", question=QUESTION, ground_truth=label, difficulty=r["_cat"],
                context=f"### Offer A\n{render_kv(rec('left'), max_val=600, max_total=1150)}\n\n### Offer B\n{render_kv(rec('right'), max_val=600, max_total=1150)}",
                dataset_name="wdc_lspc", data_type="record_pair", answer_type="boolean", native_metric="em",
                gold_aliases=["match" if label == "yes" else "no match", "1" if label == "yes" else "0"],
                extra={"category": r["_cat"], "split": "test", "source": "hf:wdc/products-2017",
                       "licence": "WDC Product Data Corpus - CC BY 4.0 (see dataset card)",
                       "cluster_id_left": r.get("cluster_id_left"), "cluster_id_right": r.get("cluster_id_right")}))
        return out
