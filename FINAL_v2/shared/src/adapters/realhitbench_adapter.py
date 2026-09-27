"""RealHiTBench (Wu et al. 2025, ACL; hierarchical real-world tables; licence CC BY-NC 4.0 - non-commercial).
Local files only: data/raw/realhitbench/QA_final.json ({"queries": [...]}) and data/raw/realhitbench/csv/<FileName>.csv.

Framing: QuestionType in {Fact Checking, Numerical Reasoning}.  Structure Comprehending items carry an
empty FinalAnswer / ProcessedAnswer in QA_final.json, so they are skipped; Data Analysis and Visualization
golds are free text / code and are skipped.  Golds longer than 10 tokens are dropped.  The CSV table is
rendered with at most 60 rows x 12 columns; items whose capped table exceeds 3,000 chars are dropped
(so no answer cell is lost to truncation).  Gold = ProcessedAnswer; 'a, b' style answers become
gold_list when every part looks like an independent value."""
from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import render_table

logger = logging.getLogger(__name__)
RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "realhitbench"
KEEP_TYPES = {"Fact Checking", "Numerical Reasoning"}
MAX_ROWS, MAX_COLS, MAX_CHARS, MAX_GOLD_TOKENS = 60, 12, 3000, 10


def _split_gold(ans: str):
    parts = [p.strip() for p in ans.split(", ") if p.strip()]
    if len(parts) > 1 and all(re.match(r"^[A-Z0-9(\"'‘“$-]", p) for p in parts):
        return parts
    return [ans.strip()]


class RealHiTBenchAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = Path(config.get("dataset_url") or RAW)
        qa_path, csv_dir = root / "QA_final.json", root / "csv"
        if not qa_path.exists() or not csv_dir.is_dir():
            raise FileNotFoundError(f"RealHiTBench files missing: expected {qa_path} and {csv_dir}/ (from the RealHiTBench release).")
        queries = json.loads(qa_path.read_text(encoding="utf-8"))["queries"]
        tables: dict = {}
        items: List[QuestionItem] = []
        for q in queries:
            if q.get("QuestionType") not in KEEP_TYPES:
                continue
            ans = str(q.get("ProcessedAnswer") or "").strip()
            if not ans or len(ans.split()) > MAX_GOLD_TOKENS:
                continue
            fn = q["FileName"]
            if fn not in tables:
                p = csv_dir / f"{fn}.csv"
                if not p.exists():
                    tables[fn] = None
                else:
                    with open(p, encoding="utf-8", newline="") as f:
                        grid = [r[:MAX_COLS] for r in csv.reader(f)][:MAX_ROWS]
                    rendered = render_table(grid, max_rows=MAX_ROWS, max_chars=10**7)
                    tables[fn] = rendered if len(rendered) <= MAX_CHARS else None
            table = tables[fn]
            if table is None:
                continue
            parts = _split_gold(ans)
            gold_list = parts if len(parts) > 1 else None
            items.append(QuestionItem(
                uid=f"rhb_{q['id']}",
                question=f"{q['Question'].strip()}\nAnswer with the value only; if several values are required, separate them with ' | '.",
                ground_truth=" | ".join(parts) if gold_list else parts[0], difficulty=q["QuestionType"],
                table_data=table, dataset_name="realhitbench", data_type="table", gold_list=gold_list,
                gold_aliases=[ans] if gold_list else [], native_metric="auto",
                extra={"question_type": q["QuestionType"], "sub_type": q.get("SubQType"), "structure": q.get("CompStrucCata"),
                       "source": q.get("Source"), "file": fn, "final_answer": q.get("FinalAnswer"),
                       "license": "CC BY-NC 4.0 (non-commercial)", "dataset_source": "RealHiTBench QA_final.json + csv/"}))
        return self._select(items, config)
