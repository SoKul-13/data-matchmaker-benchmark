"""TableBench (Wu et al. 2024; Hugging Face Multilingual-Multimodal-NLP/TableBench, Apache-2.0).
Local file: data/raw/tablebench/TableBench.jsonl (the TQA_test split: id, qtype, qsubtype, table{columns,data}, question, answer).

Framing: qtype in {FactChecking, NumericalReasoning}; DataAnalysis and Visualization are skipped.
Gold = answer; numeric-looking answers are typed numeric, 'a, b' answers become gold_list."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import render_table

RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "tablebench" / "TableBench.jsonl"
HF_REPO = "Multilingual-Multimodal-NLP/TableBench"
KEEP = {"FactChecking", "NumericalReasoning"}
NUM_RE = re.compile(r"^[-+]?\$?\d[\d,]*(\.\d+)?%?$")


class TableBenchAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        path = Path(config.get("dataset_url") or RAW)
        if not path.exists():
            raise FileNotFoundError(f"TableBench file not found at {path}; download 'TableBench.jsonl' from hf:{HF_REPO} (repo_type=dataset).")
        items: List[QuestionItem] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("qtype") not in KEEP:
                continue
            ans = str(r.get("answer", "")).strip()
            if not ans:
                continue
            t = r["table"]
            table = render_table([t["columns"]] + list(t["data"]), max_rows=60, max_chars=3000)
            parts = [p.strip() for p in ans.split(", ") if p.strip()] if ", " in ans else [ans]
            gold_list = parts if len(parts) > 1 else None
            numeric = gold_list is None and bool(NUM_RE.match(ans))
            fmt = "Answer with the number only." if numeric else "Answer with the value only; if several values are required, separate them with ' | '."
            items.append(QuestionItem(
                uid=f"tablebench_{r['id']}", question=f"{r['question'].strip()}\n{fmt}",
                ground_truth=" | ".join(parts) if gold_list else ans, difficulty=r.get("qsubtype") or r["qtype"],
                table_data=table, dataset_name="tablebench", data_type="table", gold_list=gold_list,
                gold_aliases=[ans] if gold_list else [], answer_type="numeric" if numeric else None, native_metric="auto",
                extra={"qtype": r["qtype"], "qsubtype": r.get("qsubtype"), "license": "Apache-2.0", "source": f"hf:{HF_REPO}"}))
        return self._select(items, config)
