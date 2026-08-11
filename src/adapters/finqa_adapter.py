import json
import logging
import os
from typing import Any, List
import httpx

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)

DEFAULT_FINQA_URL = "https://raw.githubusercontent.com/czyssrs/FinQA/master/dataset/test.json"



class FinQAAdapter(DatasetAdapter):
    """
    Adapter for FinQA (SEC 10-K report table-and-text numerical reasoning dataset).
    """

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        dataset_url = config.get("dataset_url") or DEFAULT_FINQA_URL
        data_items = []

        if dataset_url.startswith("http://") or dataset_url.startswith("https://"):
            logger.info(f"Downloading FinQA dataset from {dataset_url}")
            resp = httpx.get(dataset_url, follow_redirects=True, timeout=30.0)
            resp.raise_for_status()
            data_items = resp.json()
        elif os.path.exists(dataset_url):
            logger.info(f"Reading FinQA dataset from local file {dataset_url}")
            with open(dataset_url, "r", encoding="utf-8") as f:
                data_items = json.load(f)
        else:
            logger.warning(f"FinQA dataset path {dataset_url} not found, attempting URL download")
            resp = httpx.get(DEFAULT_FINQA_URL, follow_redirects=True, timeout=30.0)
            data_items = resp.json()

        questions: List[QuestionItem] = []
        for idx, item in enumerate(data_items):
            uid = item.get("id") or str(idx)
            q_text = ""
            if "qa" in item and "question" in item["qa"]:
                q_text = item["qa"]["question"]
            elif "question" in item:
                q_text = item["question"]

            gt = ""
            if "qa" in item and "exe_ans" in item["qa"]:
                gt = str(item["qa"]["exe_ans"])
            elif "qa" in item and "answer" in item["qa"]:
                gt = str(item["qa"]["answer"])
            elif "answer" in item:
                gt = str(item["answer"])

            # Table context if present
            table_str = ""
            if "table" in item:
                table_str = json.dumps(item["table"])
            
            text_context = ""
            if "pre_text" in item or "post_text" in item:
                pre = " ".join(item.get("pre_text", []))
                post = " ".join(item.get("post_text", []))
                text_context = f"{pre}\n{post}".strip()

            full_question = q_text
            if text_context or table_str:
                full_question = f"Context:\n{text_context}\n\nTable:\n{table_str}\n\nQuestion: {q_text}"

            if q_text and gt:
                questions.append(
                    QuestionItem(
                        uid=str(uid),
                        question=full_question.strip(),
                        ground_truth=gt.strip(),
                        difficulty="all",
                        context=text_context,
                        table_data=table_str,
                        metric_type="fuzzy_numeric",
                        dataset_name="finqa",
                        data_type="table",
                    )
                )

        num_q = config.get("num_questions")
        if num_q and isinstance(num_q, int) and num_q > 0:
            questions = questions[:num_q]

        logger.info(f"FinQAAdapter loaded {len(questions)} questions")
        return questions
