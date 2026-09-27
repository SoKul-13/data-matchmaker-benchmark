"""Papadakis, Christen et al., "A Critical Re-evaluation of Benchmark Datasets for (Deep) Learning-Based
Matching Algorithms" - the eight new datasets Dn1..Dn8 (Zenodo record 8164151, CC BY 4.0;
https://github.com/gpapadis/DLMatchers).

These sets were built so that the class ratio and the difficulty are NOT the artificially balanced ones
of the classic benchmarks, so this adapter samples uniformly at random from each test split and keeps
each set's own positive share (recorded in extra.set_positive_share).  One item per pair, gold yes / no.
Raw files: data/raw/papadakis_dn/Dn<k>.zip -> Dn<k>/test_set.csv (left_* / right_* columns).
"""
import csv
import logging
import random
import zipfile
from pathlib import Path
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import clip, default_pool_n, ensure_file, raw_dir, render_kv

logger = logging.getLogger(__name__)
ZENODO = "https://zenodo.org/api/records/8164151/files/Dn{k}.zip/content"
SETS = {  # k -> short description (from the paper's Table 3)
    1: "Abt-Buy style products (name, description, price)",
    2: "Amazon-Google style products (title, description, manufacturer, price)",
    3: "bibliographic records (title, authors, venue, year)",
    4: "TV episodes (title, name, episode / season, genres)",
    5: "TV episodes (title, name, episode / season)",
    6: "TV episodes with abstracts and release dates",
    7: "Walmart-Amazon style products (title, model, price, weight, brand, dimensions)",
    8: "bibliographic records (title, authors, venue, year)",
}
QUESTION = "Do these two records refer to the same real-world entity? Answer yes or no."


def _rows(zip_path: Path, k: int) -> List[dict]:
    csv.field_size_limit(10 ** 9)
    with zipfile.ZipFile(zip_path) as z:
        member = [n for n in z.namelist() if n.endswith(f"Dn{k}/test_set.csv")][0]
        text = z.read(member).decode("utf-8", errors="replace")
    return list(csv.DictReader(text.splitlines()))


def _side(r: dict, side: str) -> dict:
    return {k[len(side) + 1:]: v.strip().strip('"') for k, v in r.items() if k.startswith(side + "_") and k != f"{side}_id"}


class PapadakisDnAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = raw_dir("papadakis_dn")
        num_q, seed = int(config.get("num_questions") or default_pool_n("papadakis_dn")), config.get("seed", 0)
        rng = random.Random(seed)
        per_set = max(5, -(-num_q // len(SETS)))  # ceil; uniform within each set
        out = []
        for k, desc in SETS.items():
            zp = ensure_file(root / f"Dn{k}.zip", ZENODO.format(k=k),
                             hint=f"Download Dn{k}.zip from https://zenodo.org/record/8164151")
            rows = _rows(zp, k)
            n_pos = sum(1 for r in rows if r["label"].strip() == "1")
            share = n_pos / max(1, len(rows))
            for r in (rows if config.get("census") else rng.sample(rows, min(per_set, len(rows)))):  # uniform: class ratio preserved in expectation
                label = "yes" if r["label"].strip() == "1" else "no"
                a, b = _side(r, "left"), _side(r, "right")
                out.append(QuestionItem(
                    uid=f"papadakis_dn{k}_{r['id']}", question=QUESTION, ground_truth=label, difficulty=f"Dn{k}",
                    context=f"### Record A\n{render_kv(a, max_val=500, max_total=1150)}\n\n### Record B\n{render_kv(b, max_val=500, max_total=1150)}",
                    dataset_name="papadakis_dn", data_type="record_pair", answer_type="boolean", native_metric="em",
                    gold_aliases=["match" if label == "yes" else "no match", "1" if label == "yes" else "0"],
                    extra={"set": f"Dn{k}", "set_description": desc, "split": "test",
                           "set_positive_share": round(share, 4), "set_test_pairs": len(rows),
                           "sampling": "uniform (class ratio preserved, not balanced)",
                           "source": "https://zenodo.org/record/8164151", "licence": "CC BY 4.0"}))
        rng.shuffle(out)
        return out
