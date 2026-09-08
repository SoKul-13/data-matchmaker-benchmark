import csv
import io
import json
import logging
import os
from typing import Any, List
import httpx

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)


class GenericDatasetAdapter(DatasetAdapter):
    """
    Generic Dataset Adapter supporting arbitrary CSV, JSON, JSONL datasets or HuggingFace endpoints.
    Allows mapping configurable column names (e.g. question_key, answer_key, id_key, context_key).
    """

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        dataset_name = config.get("dataset_name", "generic")
        dataset_url = config.get("dataset_url") or ""
        q_key = config.get("question_key", "question")
        a_key = config.get("answer_key", "ground_truth")
        id_key = config.get("id_key", "id")
        metric_type = config.get("metric_type", "fuzzy_numeric")

        content_str = ""
        if dataset_url.startswith("http://") or dataset_url.startswith("https://"):
            logger.info(f"Downloading generic dataset '{dataset_name}' from {dataset_url}")
            resp = httpx.get(dataset_url, follow_redirects=True, timeout=30.0)
            resp.raise_for_status()
            content_str = resp.text
        elif dataset_url and os.path.exists(dataset_url):
            logger.info(f"Reading generic dataset '{dataset_name}' from {dataset_url}")
            with open(dataset_url, "r", encoding="utf-8") as f:
                content_str = f.read()
        else:
            logger.warning(f"No dataset file found for '{dataset_name}' at '{dataset_url}'")
            return []

        questions: List[QuestionItem] = []

        # Try parsing JSON / JSONL
        if content_str.strip().startswith("[") or content_str.strip().startswith("{"):
            try:
                data = json.loads(content_str)
                if isinstance(data, dict):
                    data = data.get("data") or data.get("rows") or [data]
                for idx, row in enumerate(data):
                    uid = str(row.get(id_key) or row.get("uid") or idx)
                    q = row.get(q_key) or row.get("Question") or row.get("query") or ""
                    a = str(row.get(a_key) or row.get("Answer") or row.get("target") or "")
                    ctx = row.get("context") or row.get("doc") or ""
                    if q and a:
                        prompt = f"Context:\n{ctx}\n\nQuestion: {q}" if ctx else q
                        questions.append(
                            QuestionItem(
                                uid=uid,
                                question=prompt.strip(),
                                ground_truth=a.strip(),
                                difficulty=row.get("difficulty", "all"),
                                context=str(ctx),
                                metric_type=metric_type,
                                dataset_name=dataset_name,
                                data_type="text",
                            )
                        )
                logger.info(f"Loaded {len(questions)} items from JSON")
                return self._apply_filters(questions, config)
            except Exception as e:
                logger.debug(f"JSON parsing failed, trying CSV/JSONL: {e}")

        # Try parsing JSONL
        lines = [l.strip() for l in content_str.split("\n") if l.strip()]
        if lines and lines[0].startswith("{"):
            for idx, line in enumerate(lines):
                try:
                    row = json.loads(line)
                    uid = str(row.get(id_key) or row.get("uid") or idx)
                    q = row.get(q_key) or row.get("Question") or row.get("query") or ""
                    a = str(row.get(a_key) or row.get("Answer") or row.get("target") or "")
                    ctx = row.get("context") or row.get("doc") or ""
                    if q and a:
                        prompt = f"Context:\n{ctx}\n\nQuestion: {q}" if ctx else q
                        questions.append(
                            QuestionItem(
                                uid=uid,
                                question=prompt.strip(),
                                ground_truth=a.strip(),
                                difficulty=row.get("difficulty", "all"),
                                context=str(ctx),
                                metric_type=metric_type,
                                dataset_name=dataset_name,
                                data_type="text",
                            )
                        )
                except Exception:
                    continue
            if questions:
                logger.info(f"Loaded {len(questions)} items from JSONL")
                return self._apply_filters(questions, config)

        # Fallback to CSV/TSV
        delimiter = "\t" if lines and "\t" in lines[0] else ","
        reader = csv.DictReader(io.StringIO(content_str), delimiter=delimiter)
        for idx, row in enumerate(reader):
            uid = str(row.get(id_key) or row.get("uid") or idx)
            q = row.get(q_key) or row.get("question") or row.get("Question") or ""
            a = str(row.get(a_key) or row.get("answer") or row.get("ground_truth") or "")
            ctx = row.get("context") or row.get("document") or ""

            if q and a:
                prompt = f"Context:\n{ctx}\n\nQuestion: {q}" if ctx else q
                questions.append(
                    QuestionItem(
                        uid=uid,
                        question=prompt.strip(),
                        ground_truth=a.strip(),
                        difficulty=row.get("difficulty", "all"),
                        context=str(ctx),
                        metric_type=metric_type,
                        dataset_name=dataset_name,
                        data_type="text",
                    )
                )

        logger.info(f"Loaded {len(questions)} items from CSV")
        return self._apply_filters(questions, config)

    def _apply_filters(self, questions: List[QuestionItem], config: dict[str, Any]) -> List[QuestionItem]:
        num_q = config.get("num_questions")
        diff = config.get("difficulty", "all").lower()
        if diff != "all":
            questions = [q for q in questions if q.difficulty == diff]
        if num_q and isinstance(num_q, int) and num_q > 0:
            questions = questions[:num_q]
        return questions
