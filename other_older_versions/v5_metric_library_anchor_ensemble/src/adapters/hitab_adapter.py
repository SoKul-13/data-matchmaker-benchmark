"""HiTab (hierarchical tables from statistical reports; Microsoft).  Samples from
data/test_samples.jsonl, tables from data/tables.zip (both on GitHub)."""
import ast
import json
import logging
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import load_text_or_url, render_table, zip_member

logger = logging.getLogger(__name__)
SAMPLES = "https://raw.githubusercontent.com/microsoft/HiTab/main/data/test_samples.jsonl"
TABLES_ZIP = "https://raw.githubusercontent.com/microsoft/HiTab/main/data/tables.zip"


class HiTabAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        rows = [json.loads(l) for l in load_text_or_url(config.get("dataset_url") or SAMPLES).splitlines() if l.strip()]
        rows = self._select(rows, config)
        out = []
        for r in rows:
            raw = zip_member(TABLES_ZIP, f"raw/{r['table_id']}.json") or zip_member(TABLES_ZIP, f"hmt/{r['table_id']}.json")
            if not raw:
                continue
            t = json.loads(raw)
            grid = t.get("texts")
            if not grid and isinstance(t.get("data"), list):   # hmt format: cells are {'value': ...}
                grid = [[c.get("value", "") if isinstance(c, dict) else c for c in row] for row in t["data"]]
            grid = grid or []
            table_str = render_table(grid, max_rows=45, max_chars=4000, title=t.get("title"))
            try:
                ans = ast.literal_eval(r["answer"]) if isinstance(r["answer"], str) else r["answer"]
            except Exception:
                ans = [r["answer"]]
            parts = [str(a).strip() for a in (ans if isinstance(ans, list) else [ans])]
            gold_list = parts if len(parts) > 1 else None
            gold = " | ".join(parts) if gold_list else parts[0]
            out.append(QuestionItem(
                uid=f"hitab_{r['id']}", question=r["question"].strip(), ground_truth=gold, difficulty=str(r.get("aggregation")),
                table_data=table_str, dataset_name="hitab", data_type="table", gold_list=gold_list,
                gold_aliases=[", ".join(parts)] if gold_list else [], native_metric="auto",
                extra={"table_source": r.get("table_source"), "aggregation": r.get("aggregation")}))
        return out
