"""Machamp - Generalized Entity Matching benchmark (Megagon Labs, CIKM 2021;
https://github.com/megagonlabs/machamp).  Seven tasks pairing structured (csv), semi-structured (json)
and unstructured (txt) tables.  Test splits only; one item per pair; gold yes / no; balanced within
each task; the task name is stored in extra / difficulty.

Raw files live under data/raw/machamp/<task>/{left.*, right.*, test.csv} (downloaded from GitHub raw
on first use).  Each test.csv row is `left_index,right_index,label`; indices are positions in the left /
right table (csv row order, json array index, txt line index).
"""
import csv
import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import balanced_sample, clip, default_pool_n, ensure_file, raw_dir, render_kv

logger = logging.getLogger(__name__)
RAW_BASE = "https://raw.githubusercontent.com/megagonlabs/machamp/main/"
TASKS: Dict[str, tuple] = {  # task -> (left file, right file, description)
    "rel-heter": ("left.csv", "right.csv", "structured restaurants, heterogeneous schemas (Fodors-Zagats)"),
    "rel-text": ("left.txt", "right.csv", "paper abstract (text) vs structured publication record (DBLP-ACM)"),
    "semi-homo": ("left.json", "right.json", "semi-structured publications, homogeneous schema (DBLP-Scholar)"),
    "semi-heter": ("left.json", "right.json", "semi-structured books, heterogeneous schemas (Magellan Books)"),
    "semi-rel": ("left.csv", "right.json", "structured vs semi-structured movies (Magellan Movies)"),
    "semi-text-c": ("left.json", "right.txt", "semi-structured product vs product text (WDC computers)"),
    "semi-text-w": ("left.json", "right.txt", "semi-structured product vs product text (WDC watches)"),
}
QUESTION = "Do these two records refer to the same real-world entity? Answer yes or no."


def _load_table(path: Path) -> List[str]:
    """Return the rendered records of a left / right table, indexable by position."""
    if path.suffix == ".csv":
        with open(path, encoding="utf-8", errors="replace", newline="") as f:
            rows = list(csv.DictReader(f))
        return [render_kv(r, skip=("id", "Id"), max_val=400, max_total=1100) for r in rows]
    if path.suffix == ".json":
        with open(path, encoding="utf-8", errors="replace") as f:
            recs = json.load(f)
        skip = {"id", "Id", "id_left", "id_right", "pair_id", "cluster_id_left", "cluster_id_right", "Url", "url"}

        def norm(r: dict) -> dict:  # WDC-derived records: strip _left/_right suffixes and "..."@lang quoting
            out = {}
            for k, v in r.items():
                if k in skip:
                    continue
                k2 = re.sub(r"_(left|right)$", "", str(k))
                if isinstance(v, str):
                    v = re.sub(r'"\s*@[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?', "", v).replace('"', "").strip()
                out[k2] = v
            return out
        return [render_kv(norm(r), max_val=400, max_total=1100) for r in recs]
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            line = re.sub(r"^\d+\s+###\s*", "", line)            # WDC lines start with "<id> ### "
            line = re.sub(r'"\s*@[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?', "", line)   # drop "..."@en language tags
            parts = [p.strip().strip('"').strip() for p in line.split("###")]
            parts = [p for p in parts if p and p.lower() != "null"]
            out.append(clip("\n".join(parts), 1100))
    return out


class MachampAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = raw_dir("machamp")
        num_q, seed = int(config.get("num_questions") or default_pool_n("machamp")), config.get("seed", 0)
        rng = random.Random(seed)
        per_task = max(2, -(-num_q // len(TASKS)))  # ceil; balanced within each task
        out = []
        for task, (lf, rf, desc) in TASKS.items():
            d = root / task
            hint = f"Download from https://github.com/megagonlabs/machamp/tree/main/{task}"
            test = ensure_file(d / "test.csv", RAW_BASE + f"{task}/test.csv", hint=hint)
            left = _load_table(ensure_file(d / lf, RAW_BASE + f"{task}/{lf}", hint=hint))
            right = _load_table(ensure_file(d / rf, RAW_BASE + f"{task}/{rf}", hint=hint))
            with open(test, encoding="utf-8") as f:
                pairs = [r for r in csv.reader(f) if len(r) >= 3]
            pairs = [(int(a), int(b), c.strip()) for a, b, c in pairs if a.strip().isdigit()]
            pairs = [p for p in pairs if p[0] < len(left) and p[1] < len(right)]
            pos = [p for p in pairs if p[2] == "1"]
            neg = [p for p in pairs if p[2] == "0"]
            for a, b, lab in (pairs if config.get("census") else balanced_sample(pos, neg, per_task, rng)):
                label = "yes" if lab == "1" else "no"
                out.append(QuestionItem(
                    uid=f"machamp_{task}_{a}_{b}", question=QUESTION, ground_truth=label, difficulty=task,
                    context=f"### Record A ({lf.split('.')[-1]} table)\n{left[a]}\n\n### Record B ({rf.split('.')[-1]} table)\n{right[b]}",
                    dataset_name="machamp", data_type="record_pair", answer_type="boolean", native_metric="em",
                    gold_aliases=["match" if label == "yes" else "no match", "1" if label == "yes" else "0"],
                    extra={"task": task, "task_description": desc, "left_format": lf.split(".")[-1],
                           "right_format": rf.split(".")[-1], "split": "test",
                           "test_positive_share": round(len(pos) / max(1, len(pairs)), 4),
                           "source": "https://github.com/megagonlabs/machamp",
                           "licence": "Megagon Labs OSS licence; underlying data under original (DeepMatcher / Magellan / WDC) terms"}))
        rng.shuffle(out)
        return out
