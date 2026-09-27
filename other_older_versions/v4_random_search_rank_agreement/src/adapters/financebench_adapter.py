import json
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import load_text_or_url

DEFAULT_FB_URL = "https://raw.githubusercontent.com/patronus-ai/financebench/main/data/financebench_open_source.jsonl"


class FinanceBenchAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        rows = [json.loads(l) for l in load_text_or_url(config.get("dataset_url") or DEFAULT_FB_URL).splitlines() if l.strip()]
        max_ctx = int(config.get("max_context_chars", 6000))
        out = []
        for r in self._select(rows, config):
            ctx = "\n\n".join(e.get("evidence_text", "") for e in (r.get("evidence") or []) if isinstance(e, dict))[:max_ctx]
            out.append(QuestionItem(uid=str(r.get("financebench_id")), question=f"Company: {r.get('company', '')} (filing: {r.get('doc_name', '')})\n{r.get('question', '')}".strip(),
                                    ground_truth=str(r.get("answer", "")).strip(), difficulty=str(r.get("question_type", "all")), context=ctx,
                                    dataset_name="financebench", data_type="document", native_metric="auto"))
        return out
