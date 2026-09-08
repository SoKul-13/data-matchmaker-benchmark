import csv
import io
import logging
from typing import Any, List
import httpx

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)

DEFAULT_OFFICEQA_URL = "https://raw.githubusercontent.com/databricks/officeqa/main/officeqa.csv"


class OfficeQAAdapter(DatasetAdapter):
    """
    Adapter for OfficeQA (U.S. Treasury Bulletins 1939-2025 financial QA benchmark).
    """

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        dataset_url = config.get("dataset_url") or DEFAULT_OFFICEQA_URL
        csv_text = ""

        if dataset_url.startswith("http://") or dataset_url.startswith("https://"):
            logger.info(f"Downloading OfficeQA dataset from {dataset_url}")
            resp = httpx.get(dataset_url, follow_redirects=True, timeout=30.0)
            resp.raise_for_status()
            csv_text = resp.text
        else:
            logger.info(f"Reading OfficeQA dataset from local path {dataset_url}")
            with open(dataset_url, "r", encoding="utf-8") as f:
                csv_text = f.read()

        reader = csv.DictReader(io.StringIO(csv_text))
        questions: List[QuestionItem] = []
        for idx, row in enumerate(reader):
            uid = row.get("uid") or row.get("id") or str(idx)
            q_text = row.get("question") or row.get("Question") or ""
            gt = row.get("ground_truth") or row.get("answer") or row.get("Answer") or ""
            diff = row.get("difficulty") or row.get("Difficulty") or "all"
            if q_text and gt:
                questions.append(
                    QuestionItem(
                        uid=str(uid),
                        question=q_text.strip(),
                        ground_truth=gt.strip(),
                        difficulty=diff.lower(),
                        metric_type="fuzzy_numeric",
                        dataset_name="officeqa",
                        data_type="document",
                    )
                )

        num_q = config.get("num_questions")
        difficulty_filter = config.get("difficulty", "all").lower()

        if difficulty_filter != "all":
            questions = [q for q in questions if q.difficulty == difficulty_filter]

        if num_q and isinstance(num_q, int) and num_q > 0:
            questions = questions[:num_q]

        logger.info(f"OfficeQAAdapter loaded {len(questions)} questions")
        return questions
