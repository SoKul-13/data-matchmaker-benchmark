import json
import logging
import os
from typing import Any, List
import httpx

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)

DEFAULT_TABFACT_URL = "https://raw.githubusercontent.com/wenhuchen/Table-Fact-Checking/master/tokenized_data/test_examples.json"



class TabFactAdapter(DatasetAdapter):
    """
    Adapter for TabFact (Table-based statement fact verification benchmark).
    """

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        dataset_url = config.get("dataset_url") or DEFAULT_TABFACT_URL
        data_items = []

        if dataset_url.startswith("http://") or dataset_url.startswith("https://"):
            logger.info(f"Downloading TabFact dataset from {dataset_url}")
            resp = httpx.get(dataset_url, follow_redirects=True, timeout=30.0)
            resp.raise_for_status()
            # TabFact JSON lines format or single JSON
            content = resp.text.strip()
            if content.startswith("{") or content.startswith("["):
                try:
                    data_items = json.loads(content)
                except Exception:
                    data_items = [json.loads(line) for line in content.split("\n") if line.strip()]
        elif os.path.exists(dataset_url):
            logger.info(f"Reading TabFact dataset from local file {dataset_url}")
            with open(dataset_url, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content.startswith("{") or content.startswith("["):
                    try:
                        data_items = json.loads(content)
                    except Exception:
                        data_items = [json.loads(line) for line in content.split("\n") if line.strip()]

        questions: List[QuestionItem] = []
        idx = 0

        if isinstance(data_items, dict):
            for table_id, val in data_items.items():
                if isinstance(val, list) and len(val) >= 2:
                    pos_statements = val[0] if isinstance(val[0], list) else []
                    neg_statements = val[1] if isinstance(val[1], list) else []
                    table_info = str(val[2]) if len(val) > 2 else ""

                    for stmt in pos_statements:
                        idx += 1
                        questions.append(
                            QuestionItem(
                                uid=f"tabfact_{idx}",
                                question=f"Given Table {table_id}:\n{table_info}\n\nVerify if statement is TRUE (1) or FALSE (0):\nStatement: {stmt}",
                                ground_truth="1",
                                difficulty="all",
                                metric_type="binary",
                                dataset_name="tab_fact",
                                data_type="table",
                            )
                        )

                    for stmt in neg_statements:
                        idx += 1
                        questions.append(
                            QuestionItem(
                                uid=f"tabfact_{idx}",
                                question=f"Given Table {table_id}:\n{table_info}\n\nVerify if statement is TRUE (1) or FALSE (0):\nStatement: {stmt}",
                                ground_truth="0",
                                difficulty="all",
                                metric_type="binary",
                                dataset_name="tab_fact",
                                data_type="table",
                            )
                        )
                elif isinstance(val, dict):
                    stmt = val.get("statement") or val.get("claim") or ""
                    gt = "1" if str(val.get("label", "1")) in ["1", "entailed", "true"] else "0"
                    idx += 1
                    if stmt:
                        questions.append(
                            QuestionItem(
                                uid=f"tabfact_{idx}",
                                question=str(stmt),
                                ground_truth=gt,
                                metric_type="binary",
                                dataset_name="tab_fact",
                                data_type="table",
                            )
                        )


        num_q = config.get("num_questions")
        if num_q and isinstance(num_q, int) and num_q > 0:
            questions = questions[:num_q]

        logger.info(f"TabFactAdapter loaded {len(questions)} questions")
        return questions
