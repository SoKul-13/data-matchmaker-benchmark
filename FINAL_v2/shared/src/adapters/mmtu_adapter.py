"""MMTU - Massive Multi-task Table Understanding (Microsoft, NeurIPS'25; MIT licence).
Source: Hugging Face dataset MMTU-benchmark/MMTU, one parquet with ~28k prompts across 25 tasks.
Local file: data/raw/mmtu/data/train-00000-of-00001.parquet (huggingface_hub.hf_hub_download).

Framing: we keep only the tasks whose gold is a short deterministic value (no code / SQL / formula /
whole-table outputs) and whose prompt fits in 3,000 chars.  The MMTU instruction preamble (which asks
for a JSON object) is stripped; the data part of the prompt goes to table_data and we write a plain
question that ends with an explicit answer-format instruction.  The task name is stored in
extra["task"] and in `difficulty` (so the pool can be stratified across tasks)."""
from __future__ import annotations

import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)
RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "mmtu"
PARQUET = RAW / "data" / "train-00000-of-00001.parquet"
HF_REPO = "MMTU-benchmark/MMTU"
MAX_PROMPT_CHARS = 3000
PER_TASK_CAP = 120          # items kept per task before the pool sampler runs (seeded)

# task -> markers at which the data part of the prompt starts (earliest match wins)
DATA_MARKERS: Dict[str, List[str]] = {
    "Table-QA": ["\nTable Caption:\n", "\nPre-text", "\nTable:\n"],
    "Table-Fact-Verification": ["\nTable Caption:\n", "\nTable:\n"],
    "Entity-Matching": ["\nEntity A:\n"],
    "Column-type-annotation": ["\nInput Table:\n"],
    "Cell-entity-annotation": ["\nInput Table:\n"],
    "header-value-matching": ["\nTable Data:\n"],
    "Data-Imputation": ["\nInput Table:\n"],
    "Error-Detect": ["\nColumn:\n"],
    "Columns-property-anotation": ["\nInput table:\n", "\nInput Table:\n"],
}
DBP_ONT = "http://dbpedia.org/ontology/"
DBP_RES = "http://dbpedia.org/resource/"


def _data_part(task: str, prompt: str) -> str:
    idx = [prompt.find(m) for m in DATA_MARKERS[task]]
    idx = [i for i in idx if i >= 0]
    return prompt[min(idx):].strip() if idx else prompt.strip()


def _split_tail(text: str, marker: str):
    """Split 'data ... <marker>tail' -> (data, tail); tail is None when the marker is absent."""
    i = text.rfind(marker)
    if i < 0:
        return text.strip(), None
    return text[:i].strip(), text[i + len(marker):].strip()


def _short(url: str) -> str:
    return url.rsplit("/", 1)[-1]


class MMTUAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        path = Path(config.get("dataset_url") or PARQUET)
        if not path.exists():
            raise FileNotFoundError(
                f"MMTU parquet not found at {path}. Download with huggingface_hub.hf_hub_download('{HF_REPO}', "
                f"'data/train-00000-of-00001.parquet', repo_type='dataset', local_dir='{RAW}').")
        import pyarrow.parquet as pq
        tbl = pq.read_table(path, columns=["prompt", "metadata", "task", "dataset"])
        prompts, metas, tasks, dsets = (tbl.column(c).to_pylist() for c in ("prompt", "metadata", "task", "dataset"))
        rng = random.Random(config.get("seed", 0))
        by_task: Dict[str, list] = {t: [] for t in DATA_MARKERS}
        for i, (p, m, t, d) in enumerate(zip(prompts, metas, tasks, dsets)):
            if t in by_task and len(p) <= MAX_PROMPT_CHARS:
                by_task[t].append((i, p, m, d))
        items: List[QuestionItem] = []
        for task, rows in by_task.items():
            rows = list(rows)
            rng.shuffle(rows)
            if task == "Error-Detect":       # 97% of the golds are 'no error'; balance the two outcomes
                err = [r for r in rows if json.loads(r[2]).get("label")]
                ok = [r for r in rows if not json.loads(r[2]).get("label")][: len(err)]
                rows = err + ok
                rng.shuffle(rows)
            n = 0
            for i, p, m, d in rows:
                if n >= PER_TASK_CAP:
                    break
                try:
                    it = self._build(task, i, p, json.loads(m), d)
                except Exception as e:  # pragma: no cover
                    logger.debug(f"MMTU {task} row {i}: {e}")
                    it = None
                if it is not None:
                    items.append(it)
                    n += 1
        return self._select(items, config)

    # ------------------------------------------------------------------------------------------
    def _build(self, task: str, i: int, prompt: str, md: dict, dset: str) -> Optional[QuestionItem]:
        data = _data_part(task, prompt)
        base = dict(uid=f"mmtu_{task}_{md.get('test_case', i)}".replace(" ", "_"), difficulty=task, dataset_name="mmtu",
                    data_type="table", native_metric="auto",
                    extra={"task": task, "source_dataset": dset, "test_case": md.get("test_case"), "license": "MIT",
                           "source": f"hf:{HF_REPO}"})
        if task == "Table-QA":
            table, q = _split_tail(data, "\nQuestion:\n")
            if not q:
                return None
            qa = md.get("qa") or {}
            gold = str(qa.get("answer") or md.get("label") or "").strip()
            if not gold or gold.lower() in ("none", "null", "nan"):
                return None
            aliases = []
            if qa.get("answer") is not None and md.get("label") is not None and str(md["label"]) != gold:
                aliases.append(str(md["label"]))
            parts = [s.strip() for s in gold.split("|") if s.strip()] if "|" in gold else [gold]
            gold_list = parts if len(parts) > 1 else None
            return QuestionItem(question=f"{q}\nAnswer with the value only (for several values, separate them with ' | ').",
                                ground_truth=" | ".join(parts), table_data=table, gold_list=gold_list, gold_aliases=aliases, **base)
        if task == "Table-Fact-Verification":
            table, stmt = _split_tail(data, "\nStatement:\n")
            lab = str(md.get("label", "")).upper()
            if not stmt or lab not in ("ENTAILED", "REFUTED"):
                return None
            yes = lab == "ENTAILED"
            return QuestionItem(question=f"Statement: {stmt}\nIs this statement entailed by the table (yes) or refuted by it (no)? Answer yes or no.",
                                ground_truth="yes" if yes else "no", table_data=table, answer_type="boolean",
                                gold_aliases=["entailed", "1"] if yes else ["refuted", "0"], **base)
        if task == "Entity-Matching":
            yes = str(md.get("label")) == "1"
            return QuestionItem(question="Do Entity A and Entity B refer to the same real-world entity? Answer yes or no.",
                                ground_truth="yes" if yes else "no", table_data=data, answer_type="boolean",
                                gold_aliases=["match", "1"] if yes else ["non-match", "no match", "0"], **base)
        if task == "Column-type-annotation":
            table, col = _split_tail(data, "\nTarget entity column:")
            lab = str(md.get("label", "")).strip()
            if not col or not lab:
                return None
            okay = [u for u in str(md.get("okay_annotation") or "").split() if u]
            aliases = [lab] + [_short(u) for u in okay] + okay
            return QuestionItem(question=f"Which DBpedia ontology class ({DBP_ONT}<class>) most precisely describes all entities in column {col.strip()}? Answer with the class name only, e.g. Building.",
                                ground_truth=_short(lab), table_data=table, answer_type="text", gold_aliases=aliases, **base)
        if task == "Cell-entity-annotation":
            table, tail = _split_tail(data, "\nTarget cell located at")
            labs = [u for u in str(md.get("label", "")).split() if u]
            if not tail or not labs:
                return None
            cell = str(md.get("cell_value", "")).strip()
            golds = [_short(u) for u in labs]
            aliases = [g.replace("_", " ") for g in golds] + golds[1:] + labs
            return QuestionItem(question=f"Which DBpedia resource ({DBP_RES}<entity>) does the target cell '{cell}' (row {md.get('row_id')}, column {md.get('col_name')}) refer to? Answer with the entity name only, e.g. Ida_Lupino.",
                                ground_truth=golds[0], table_data=table, answer_type="text", gold_aliases=aliases, **base)
        if task == "header-value-matching":
            lab = md.get("label") or []
            if not isinstance(lab, list) or not 1 <= len(lab) <= 8:
                return None
            parts = [str(x).strip() for x in lab]
            return QuestionItem(question="Assign to each column of the table (Col_0, Col_1, ... in order) the most suitable header from the candidate list. Answer with the chosen headers only, in column order, separated by ' | '.",
                                ground_truth=" | ".join(parts), table_data=data, answer_type="text",
                                gold_list=parts if len(parts) > 1 else None, gold_aliases=[", ".join(parts)], **base)
        if task == "Data-Imputation":
            gold = str(md.get("label", "")).strip()
            if not gold or gold.lower() == "nan":
                return None
            return QuestionItem(question="What value belongs in the cell marked [MISSING]? Answer with the value only.",
                                ground_truth=gold, table_data=data, **base)
        if task == "Error-Detect":
            lab = md.get("label") or []
            gold = str(lab[0]).strip() if lab else "none"
            return QuestionItem(question="Does this column contain a value that is clearly a data error (typo, wrong format or semantically incompatible with the rest of the column)? Answer with that cell value exactly as written, or 'none' if there is no clear error.",
                                ground_truth=gold, table_data=data, answer_type="text",
                                gold_aliases=(["null", "no error", "no"] if gold == "none" else [str(x) for x in lab[1:]]), **base)
        if task == "Columns-property-anotation":
            table, tail = _split_tail(data, "\nHead column:")
            lab = str(md.get("label", "")).strip()
            if not tail or not lab:
                return None
            return QuestionItem(question=f"Which DBpedia ontology property ({DBP_ONT}<property>) best describes the relationship from the head column {md.get('col_a_name')} to the tail column {md.get('col_b_name')}? Answer with the property name only, e.g. hometown.",
                                ground_truth=_short(lab), table_data=table, answer_type="text", gold_aliases=[lab], **base)
        return None
