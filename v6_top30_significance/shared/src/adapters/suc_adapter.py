"""SUC - Structural Understanding Capabilities benchmark from "Table Meets LLM" (Sui et al., WSDM'24;
github.com/microsoft/TableProvider, MIT).  The repository ships no pre-generated SUC files, only the
generator (table_meets_llm/main/unified_benchmark_generator.py) and its source tables
(table_provider/task/dataset/{tabfact,sqa,totto}.jsonl, 1,000 tables each).  This adapter re-generates
the SUC tasks deterministically from those tables with the generator's task definitions:
cell_lookup (value -> position), reverse_lookup (position -> value), row_retrieval, column_retrieval,
size_detection, merged_cell_detection (ToTTo header_hierarchy column spans).
Local files: data/raw/suc/{tabfact,sqa,totto}.jsonl.  Indexing convention is stated in every question:
rows are numbered from 1 starting at the first row below the header, columns from 1 from the left."""
from __future__ import annotations

import ast
import json
import logging
import random
from collections import Counter
from pathlib import Path
from typing import Any, List, Optional

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import render_table

logger = logging.getLogger(__name__)
RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "suc"
SOURCES = {"tabfact": "tabfact.jsonl", "sqa": "sqa.jsonl", "totto": "totto.jsonl"}
GITHUB = "https://raw.githubusercontent.com/microsoft/TableProvider/main/table_provider/task/dataset/"
TASKS = ["cell_lookup", "reverse_lookup", "row_retrieval", "column_retrieval", "size_detection", "merged_cell_detection"]
PER_TASK_CAP = 100
CONVENTION = "Rows are numbered from 1 starting at the first row below the header row; columns are numbered from 1 from the left."


def _clean(rows):
    return [["" if c is None else str(c).strip() for c in r] for r in rows]


class SUCAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = Path(config.get("dataset_url") or RAW)
        missing = [n for n in SOURCES.values() if not (root / n).exists()]
        if missing:
            raise FileNotFoundError(f"SUC source tables missing in {root}: {missing}. Download them from {GITHUB}<name>.")
        rng = random.Random(config.get("seed", 0))
        tables = []
        for src, fn in SOURCES.items():
            for i, line in enumerate((root / fn).read_text(encoding="utf-8").splitlines()):
                if not line.strip():
                    continue
                d = json.loads(line)
                t = d.get("table") or {}
                header, rows = _clean([t.get("header") or []])[0], _clean(t.get("rows") or [])
                if not header or not rows:
                    continue
                ncol = len(header)
                if not 2 <= ncol <= 10 or not 3 <= len(rows) <= 25 or any(len(r) != ncol for r in rows):
                    continue
                rendered = render_table([header] + rows, max_rows=30, max_chars=10**6, title=t.get("caption") or d.get("title") or None)
                if len(rendered) > 3000:
                    continue
                tables.append({"src": src, "idx": i, "header": header, "rows": rows, "rendered": rendered,
                               "hier": t.get("header_hierarchy")})
        rng.shuffle(tables)
        items: List[QuestionItem] = []
        counts = Counter()
        for k, tb in enumerate(tables):
            task = TASKS[k % len(TASKS)]
            if counts[task] >= PER_TASK_CAP:
                task = next((x for x in TASKS if counts[x] < PER_TASK_CAP), None)
                if task is None:
                    break
            it = self._make(task, tb, rng)
            if it is None:
                continue
            items.append(it)
            counts[task] += 1
        return self._select(items, config)

    # ------------------------------------------------------------------------------------------
    def _make(self, task: str, tb: dict, rng: random.Random) -> Optional[QuestionItem]:
        header, rows, R, C = tb["header"], tb["rows"], len(tb["rows"]), len(tb["header"])
        base = dict(difficulty=task, table_data=tb["rendered"], dataset_name="suc", data_type="table", native_metric="auto",
                    extra={"task": task, "source_table": f"{tb['src']}#{tb['idx']}", "n_rows": R, "n_cols": C,
                           "license": "MIT (microsoft/TableProvider)", "source": "Table Meets LLM - SUC (re-generated)"})
        uid = f"suc_{task}_{tb['src']}_{tb['idx']}"
        if task in ("cell_lookup", "reverse_lookup"):
            cnt = Counter(c for r in rows for c in r)
            cnt.update(header)
            cand = [(i, j) for i, r in enumerate(rows) for j, c in enumerate(r) if c and cnt[c] == 1 and len(c) <= 60]
            if not cand:
                return None
            i, j = rng.choice(cand)
            val = rows[i][j]
            if task == "cell_lookup":
                return QuestionItem(uid=uid, question=f"In which row and column of the table is the cell value \"{val}\" located? {CONVENTION} Answer in the form 'row | column', e.g. 2 | 3.",
                                    ground_truth=f"{i + 1} | {j + 1}", answer_type="text",
                                    gold_aliases=[f"({i + 1}, {j + 1})", f"row {i + 1}, column {j + 1}", f"{i + 1}, {j + 1}"], **base)
            return QuestionItem(uid=uid, question=f"What is the value of the cell in row {i + 1}, column {j + 1} of the table? {CONVENTION} Answer with the cell value only.",
                                ground_truth=val, **base)
        if task == "row_retrieval":
            i = rng.randrange(R)
            parts = [c if c else "(empty)" for c in rows[i]]
            return QuestionItem(uid=uid, question=f"List all cell values of row {i + 1} of the table, from left to right. {CONVENTION} Separate the values with ' | ' and write '(empty)' for an empty cell.",
                                ground_truth=" | ".join(parts), gold_list=parts, answer_type="text", gold_aliases=[", ".join(parts)], **base)
        if task == "column_retrieval":
            j = rng.randrange(C)
            if not header[j]:
                return None
            return QuestionItem(uid=uid, question=f"What is the header (column name) of column {j + 1} of the table? {CONVENTION} Answer with the column name only.",
                                ground_truth=header[j], answer_type="text", **base)
        if task == "size_detection":
            return QuestionItem(uid=uid, question=f"How many data rows (excluding the header row) and how many columns does the table have? Answer in the form 'rows | columns', e.g. 12 | 5.",
                                ground_truth=f"{R} | {C}", answer_type="text", gold_aliases=[f"{R} rows, {C} columns", f"{R}, {C}", f"({R}, {C})"], **base)
        if task == "merged_cell_detection":
            hier = tb.get("hier")
            if not hier:
                return None
            spans = []
            for h in hier:
                try:
                    h = ast.literal_eval(h) if isinstance(h, str) else h
                except Exception:
                    return None
                if int(h.get("column_span", 1)) > 1:
                    spans.append(int(h["column_index"]) + 1)
            spans = sorted(set(spans))
            gold = " | ".join(str(s) for s in spans) if spans else "none"
            base["extra"]["n_spans"] = len(spans)
            return QuestionItem(uid=uid, question=f"In the header rows of this table, merged cells are shown as the same value repeated in adjacent columns. Give the column number of the leftmost column of every merged header cell that spans more than one column. {CONVENTION} Separate several numbers with ' | ', or answer 'none' if no header cell is merged.",
                                ground_truth=gold, answer_type="text", gold_list=[str(s) for s in spans] if len(spans) > 1 else None,
                                gold_aliases=(["no merged cells", "null"] if not spans else [", ".join(str(s) for s in spans)]), **base)
        return None
