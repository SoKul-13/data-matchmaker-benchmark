import json
import logging
import os
from typing import Any, List
import httpx

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)

DEFAULT_TATQA_URL = "https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_dev.json"



class TATQAAdapter(DatasetAdapter):
    """
    Adapter for TAT-QA (Table-and-Text Financial QA dataset).
    """

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        dataset_url = config.get("dataset_url") or DEFAULT_TATQA_URL
        data_items = []

        if dataset_url.startswith("http://") or dataset_url.startswith("https://"):
            logger.info(f"Downloading TAT-QA dataset from {dataset_url}")
            resp = httpx.get(dataset_url, follow_redirects=True, timeout=30.0)
            resp.raise_for_status()
            data_items = resp.json()
        elif os.path.exists(dataset_url):
            logger.info(f"Reading TAT-QA dataset from local file {dataset_url}")
            with open(dataset_url, "r", encoding="utf-8") as f:
                data_items = json.load(f)
        else:
            logger.warning(f"TAT-QA dataset path {dataset_url} not found, using fallback download")
            resp = httpx.get(DEFAULT_TATQA_URL, follow_redirects=True, timeout=30.0)
            data_items = resp.json()

        questions: List[QuestionItem] = []
        q_count = 0
        for doc in data_items:
            table = doc.get("table", {})
            table_str = json.dumps(table)
            paragraphs = doc.get("paragraphs", [])
            para_text = "\n".join([p.get("text", "") for p in paragraphs if "text" in p])

            questions_list = doc.get("questions", [])
            for q in questions_list:
                q_count += 1
                uid = q.get("uid") or f"tatqa_{q_count}"
                q_text = q.get("question", "")
                gt = str(q.get("answer", ""))
                
                full_question = f"Financial Context:\n{para_text}\n\nTable Data:\n{table_str}\n\nQuestion: {q_text}"

                if q_text and gt:
                    questions.append(
                        QuestionItem(
                            uid=str(uid),
                            question=full_question.strip(),
                            ground_truth=gt.strip(),
                            difficulty="all",
                            context=para_text,
                            table_data=table_str,
                            metric_type="fuzzy_numeric",
                            dataset_name="tat_qa",
                            data_type="table",
                        )
                    )

        num_q = config.get("num_questions")
        if num_q and isinstance(num_q, int) and num_q > 0:
            questions = questions[:num_q]

        logger.info(f"TATQAAdapter loaded {len(questions)} questions")
        return questions
