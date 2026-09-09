import json
import logging
import random
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import fetch_text, load_text_or_url, render_table

logger = logging.getLogger(__name__)
DEFAULT_TABFACT_URL = "https://raw.githubusercontent.com/wenhuchen/Table-Fact-Checking/master/tokenized_data/test_examples.json"
TABLE_URL = "https://raw.githubusercontent.com/wenhuchen/Table-Fact-Checking/master/data/all_csv/{table_id}"


class TabFactAdapter(DatasetAdapter):
    """TabFact: one entailed + one refuted statement per sampled table, table fetched and rendered."""

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        data = json.loads(load_text_or_url(config.get("dataset_url") or DEFAULT_TABFACT_URL))
        num_q, seed = config.get("num_questions") or 0, config.get("seed", 0)
        ids = sorted(data)
        random.Random(seed).shuffle(ids)
        n_tables = len(ids) if not num_q else (num_q + 1) // 2
        questions: List[QuestionItem] = []
        for tid in ids[: n_tables + 10]:
            if num_q and len(questions) >= num_q:
                break
            val = data[tid]
            pos, neg, caption = list(val[0]), list(val[1]), str(val[2]) if len(val) > 2 else ""
            try:
                rows = [l.split("#") for l in fetch_text(TABLE_URL.format(table_id=tid)).strip().splitlines()]
                table_str = render_table(rows, max_rows=30, max_chars=3000, title=caption)
            except Exception as e:  # pragma: no cover
                logger.warning(f"TabFact table {tid}: {e}")
                continue
            r = random.Random(f"{seed}-{tid}")
            for stmt, label in [(r.choice(pos), "yes"), (r.choice(neg), "no")] if pos and neg else []:
                questions.append(QuestionItem(
                    uid=f"tabfact_{tid}_{label}", question=f"Is the following statement entailed by the table? Answer yes or no.\nStatement: {stmt}",
                    ground_truth=label, table_data=table_str, dataset_name="tab_fact", data_type="table", answer_type="boolean",
                    native_metric="em", gold_aliases=["1" if label == "yes" else "0", "entailed" if label == "yes" else "refuted"]))
        return questions[:num_q] if num_q else questions
