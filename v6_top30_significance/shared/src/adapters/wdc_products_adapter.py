"""WDC Products (Web Data Commons product matching, 2017 gold standard) via the Hugging Face
datasets-server API.  Four categories (computers, cameras, shoes, watches); balanced yes / no."""
import json
import logging
import random
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import fetch_text, render_record

logger = logging.getLogger(__name__)
ROWS = "https://datasets-server.huggingface.co/rows?dataset=wdc/products-2017&config={cfg}&split=test&offset={off}&length=100"
CATEGORIES = ["computers", "cameras", "shoes", "watches"]


class WDCProductsAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        size = config.get("wdc_size", "medium")
        per_cat_rows = int(config.get("rows_per_category", 300))
        rows = []
        for cat in CATEGORIES:
            for off in range(0, per_cat_rows, 100):
                try:
                    payload = json.loads(fetch_text(ROWS.format(cfg=f"{cat}_{size}", off=off)))
                except Exception as e:  # pragma: no cover
                    logger.warning(f"WDC {cat} offset {off}: {e}")
                    break
                batch = [dict(r["row"], _cat=cat) for r in payload.get("rows", [])]
                if not batch:
                    break
                rows.extend(batch)
        num_q, seed = config.get("num_questions") or 0, config.get("seed", 0)
        rng = random.Random(seed)
        if config.get("census"):
            num_q = 0
        if num_q:
            pos = [r for r in rows if str(r["label"]) == "1"]
            neg = [r for r in rows if str(r["label"]) == "0"]
            rows = rng.sample(pos, min(num_q // 2, len(pos))) + rng.sample(neg, min(num_q - num_q // 2, len(neg)))
            rng.shuffle(rows)
        out = []
        for r in rows:
            def rec(side):
                return {k: r.get(f"{k}_{side}") for k in ["brand", "title", "description", "price", "specTableContent"]}
            label = "yes" if str(r["label"]) == "1" else "no"
            out.append(QuestionItem(
                uid=f"wdc_{r['pair_id']}", question="Do these two product offers describe the same product? Answer yes or no.",
                ground_truth=label, difficulty=r["_cat"],
                context=f"### Offer A\n{render_record(rec('left'))[:1500]}\n\n### Offer B\n{render_record(rec('right'))[:1500]}",
                dataset_name="wdc_products", data_type="record_pair", answer_type="boolean", native_metric="em",
                gold_aliases=["match" if label == "yes" else "no match"]))
        return out
