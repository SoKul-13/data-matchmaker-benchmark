import json
import logging
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import load_text_or_url, render_json_table

logger = logging.getLogger(__name__)
DEFAULT_FINQA_URL = "https://raw.githubusercontent.com/czyssrs/FinQA/master/dataset/test.json"


class FinQAAdapter(DatasetAdapter):
    """FinQA: gold = human display answer (e.g. '14%'), alias = program result ('0.14464')."""

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        data_items = json.loads(load_text_or_url(config.get("dataset_url") or DEFAULT_FINQA_URL))
        questions: List[QuestionItem] = []
        for idx, item in enumerate(data_items):
            qa = item.get("qa", {})
            q_text = qa.get("question") or item.get("question") or ""
            exe = qa.get("exe_ans")
            disp = str(qa.get("answer") or "").strip()
            exe_s = "" if exe is None else str(exe).strip()
            if not q_text or (not disp and not exe_s):
                continue
            if exe_s.lower() in {"yes", "no"}:
                gold, aliases, atype, native = exe_s.lower(), [], "boolean", "em"
            else:
                gold = disp or exe_s
                aliases = [a for a in {exe_s, disp} if a and a != gold]
                atype, native = "numeric", "num_tol"
            ctx = f"{' '.join(item.get('pre_text', []))}\n{' '.join(item.get('post_text', []))}".strip()
            questions.append(QuestionItem(
                uid=str(item.get("id") or idx), question=q_text.strip(), ground_truth=gold, context=ctx[:4000],
                table_data=render_json_table(item.get("table", []), max_rows=40, max_chars=3500),
                dataset_name="finqa", data_type="table", gold_aliases=aliases, answer_type=atype, native_metric=native))
        return self._select(questions, config)
