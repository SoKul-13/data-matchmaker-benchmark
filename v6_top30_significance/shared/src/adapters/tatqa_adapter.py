import json
import logging
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import load_text_or_url, render_json_table

logger = logging.getLogger(__name__)
DEFAULT_TATQA_URL = "https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_dev.json"


class TATQAAdapter(DatasetAdapter):
    """TAT-QA: arithmetic/count -> numeric gold with scale (+ alias without); span/multi-span -> list gold.
    List golds get per-element unit aliases so '$7,870 thousand | $12,129 thousand' matches '$7,870 | $12,129'."""

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        data_items = json.loads(load_text_or_url(config.get("dataset_url") or DEFAULT_TATQA_URL))
        questions: List[QuestionItem] = []
        n = 0
        for doc in data_items:
            table = doc.get("table", {}).get("table", doc.get("table", []))
            table_str = render_json_table(table, max_rows=40, max_chars=3500)
            para = "\n".join(p.get("text", "") for p in doc.get("paragraphs", []) if "text" in p)[:3500]
            for q in doc.get("questions", []):
                n += 1
                a_type = q.get("answer_type", "span")
                raw, scale = q.get("answer", ""), (q.get("scale") or "").strip()
                gold_list, aliases = None, []
                if a_type in ("arithmetic", "count"):
                    val = str(raw[0] if isinstance(raw, list) and raw else raw).strip()
                    gold = f"{val}%" if scale == "percent" else (f"{val} {scale}" if scale else val)
                    aliases = [val] if scale else []
                    atype, native = "numeric", "num_tol"
                else:
                    parts = [str(x).strip() for x in (raw if isinstance(raw, list) else [raw]) if str(x).strip()]
                    if not parts:
                        continue
                    if len(parts) > 1:
                        gold_list, gold = parts, " | ".join(parts)
                        aliases = ["; ".join(parts), ", ".join(parts)]
                        if scale and scale != "percent":
                            aliases.append(" | ".join(f"{p} {scale}" for p in parts))
                    else:
                        gold = parts[0]
                        if scale and scale != "percent":
                            aliases.append(f"{gold} {scale}")
                    atype, native = None, "em"
                if q.get("question") and gold:
                    questions.append(QuestionItem(
                        uid=str(q.get("uid") or f"tatqa_{n}"), question=q["question"].strip(), ground_truth=gold,
                        difficulty=a_type, context=para, table_data=table_str, dataset_name="tat_qa", data_type="table",
                        gold_aliases=aliases, gold_list=gold_list, answer_type=atype, native_metric=native,
                        extra={"tatqa_answer_type": a_type, "scale": scale}))
        return self._select(questions, config)
