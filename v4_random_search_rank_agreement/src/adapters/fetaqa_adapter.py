import json
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import load_text_or_url, render_table

DEFAULT_FETAQA_URL = "https://raw.githubusercontent.com/Yale-LILY/FeTaQA/main/data/fetaQA-v1_test.jsonl"


class FeTaQAAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        rows = []
        for l in load_text_or_url(config.get("dataset_url") or DEFAULT_FETAQA_URL).splitlines():
            try:
                rows.append(json.loads(l))
            except json.JSONDecodeError:
                continue
        out = []
        for r in self._select(rows, config):
            title = f"{r.get('table_page_title', '')} - {r.get('table_section_title', '')}".strip(" -")
            out.append(QuestionItem(uid=str(r.get("feta_id")), question=str(r.get("question", "")).strip(), ground_truth=str(r.get("answer", "")).strip(),
                                    table_data=render_table(r.get("table_array", []), max_rows=40, max_chars=3500, title=title),
                                    dataset_name="fetaqa", data_type="table", answer_type="freeform", native_metric="rouge_l"))
        return out
