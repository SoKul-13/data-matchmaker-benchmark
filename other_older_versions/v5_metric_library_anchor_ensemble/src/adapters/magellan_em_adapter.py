"""Entity matching (Magellan / DeepMatcher benchmark datasets): Abt-Buy, Amazon-Google,
DBLP-GoogleScholar, Walmart-Amazon.  Each item = one record pair; gold = yes / no (same entity)."""
import csv
import io
import logging
import random
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import fetch_text, render_record

logger = logging.getLogger(__name__)
BASE = "https://pages.cs.wisc.edu/~anhai/data1/deepmatcher_data/"
SETS: Dict[str, str] = {
    "abt_buy": "Textual/Abt-Buy/exp_data/",
    "amazon_google": "Structured/Amazon-Google/exp_data/",
    "dblp_scholar": "Structured/DBLP-GoogleScholar/exp_data/",
    "walmart_amazon": "Structured/Walmart-Amazon/exp_data/",
}


def _table(url: str) -> Dict[str, dict]:
    rows = list(csv.DictReader(io.StringIO(fetch_text(url))))
    return {r["id"]: r for r in rows}


class MagellanEMAdapter(DatasetAdapter):
    def __init__(self, name: str):
        self.name = name

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        base = BASE + SETS[self.name]
        pairs = list(csv.DictReader(io.StringIO(fetch_text(base + "test.csv"))))
        A, B = _table(base + "tableA.csv"), _table(base + "tableB.csv")
        num_q, seed = config.get("num_questions") or 0, config.get("seed", 0)
        pos = [p for p in pairs if p["label"] == "1"]
        neg = [p for p in pairs if p["label"] == "0"]
        rng = random.Random(seed)
        if num_q:  # balanced sample: half matches, half non-matches
            k = num_q // 2
            pairs = rng.sample(pos, min(k, len(pos))) + rng.sample(neg, min(num_q - k, len(neg)))
            rng.shuffle(pairs)
        out = []
        for p in pairs:
            a, b = A.get(p["ltable_id"]), B.get(p["rtable_id"])
            if not a or not b:
                continue
            label = "yes" if p["label"] == "1" else "no"
            out.append(QuestionItem(
                uid=f"{self.name}_{p['ltable_id']}_{p['rtable_id']}",
                question="Do these two records refer to the same real-world entity (the same product / publication)? Answer yes or no.",
                ground_truth=label, context=f"### Record A\n{render_record(a)}\n\n### Record B\n{render_record(b)}",
                dataset_name=self.name, data_type="record_pair", answer_type="boolean", native_metric="em",
                gold_aliases=["match" if label == "yes" else "no match", "1" if label == "yes" else "0"]))
        return out
