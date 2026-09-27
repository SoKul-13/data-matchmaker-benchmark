"""TabIS - Table Information Seeking (Pang et al., Findings of ACL 2024; github.com/coszero/TabIS).
Data: Google Drive zip linked from the README (file id 1MFwMTHgxOTh7QFFRQ3cszoMCFxhNv9ui), unpacked to
data/raw/tabis/TabIS_data_2/.  Single-choice questions with two options (A / B).

Subsets used (difficulty = group):
  tis_basic      mc-totto-ma2/totto-b-tis.json, mc-hitab-ma2/hitab-b-tis.json  (basic TIS: pick the faithful statement)
  tis_structure  totto-su-tis.json, hitab-su-tis.json                            (structure-aware TIS: row / column statements)
  tsu_synthetic  TSU/mc-{pcl,rcl,prl,rrl,pll,rll}_wiki/md-one-real.json         (cell / row / column lookup on real wiki tables)
The one-shot demonstration in the original prompt is dropped; the test table, question and options are
given zero-shot.  Gold = option letter; gold_aliases = the option text; choices = both option texts."""
from __future__ import annotations

import json
import logging
import random
import re
from pathlib import Path
from typing import Any, List, Optional

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)
RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "tabis" / "TabIS_data_2"
TIS_FILES = {"tis_basic": ["mc-totto-ma2/totto-b-tis.json", "mc-hitab-ma2/hitab-b-tis.json"],
             "tis_structure": ["mc-totto-ma2/totto-su-tis.json", "mc-hitab-ma2/hitab-su-tis.json"]}
TSU_FILES = [f"TSU/mc-{k}_wiki/md-one-real.json" for k in ("pcl", "rcl", "prl", "rrl", "pll", "rll")]
MAX_TABLE_CHARS = 3000
PER_FILE_CAP = 100
TSU_CONVENTION = "(Row and column numbers count from 1; the header row is row 1 and the leftmost column is column 1.)"
FMT = "Answer with the letter of the correct option only (A or B)."


def _parse_options(opt: str):
    m = re.match(r"\s*A\.\s*(.*?)\s*\nB\.\s*(.*)\s*$", opt, flags=re.S)
    return (m.group(1).strip(), m.group(2).strip()) if m else (None, None)


class TabISAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = Path(config.get("dataset_url") or RAW)
        if not root.is_dir():
            raise FileNotFoundError(f"TabIS data not found at {root}; download the zip from the README link in github.com/coszero/TabIS and unpack it there.")
        rng = random.Random(config.get("seed", 0))
        items: List[QuestionItem] = []
        for group, files in TIS_FILES.items():
            for rel in files:
                items += self._load_tis(root / rel, group, rng)
        for rel in TSU_FILES:
            items += self._load_tsu(root / rel, rng)
        return self._select(items, config)

    def _item(self, uid, group, subset, table, question, a, b, letter, extra) -> Optional[QuestionItem]:
        if letter not in ("A", "B") or not a or not b or not table or len(table) > MAX_TABLE_CHARS:
            return None
        correct = a if letter == "A" else b
        return QuestionItem(uid=uid, question=f"{question}\nOptions:\nA. {a}\nB. {b}\n{FMT}", ground_truth=letter, difficulty=group,
                            table_data=table, dataset_name="tabis", data_type="table", answer_type="text", native_metric="em",
                            choices=[a, b], gold_aliases=[correct, f"{letter}. {correct}", f"({letter})", f"{letter}."],
                            extra={"group": group, "subset": subset, "license": "Apache-2.0 (coszero/TabIS)",
                                   "source": "TabIS (github.com/coszero/TabIS, Google Drive release)", **extra})

    def _load_tis(self, path: Path, group: str, rng: random.Random) -> List[QuestionItem]:
        if not path.exists():
            logger.warning(f"TabIS file missing: {path}")
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        rng.shuffle(data)
        subset = path.stem
        out: List[QuestionItem] = []
        for x in data:
            el = (x.get("components") or {}).get("elements") or {}
            q, meta, table = el.get("question"), el.get("meta_info"), el.get("table")
            if not q or not table:
                continue
            tbl = (f"Meta information: {meta}\n" if meta else "") + table
            it = self._item(f"tabis_{subset}_{x.get('index')}", group, subset, tbl, q, el.get("opt_a"), el.get("opt_b"), x.get("response"),
                            {"option_types": x.get("option_types"), "ques_type": x.get("ques_type"), "source_dataset": "HiTab" if "hitab" in subset else "ToTTo"})
            if it:
                out.append(it)
            if len(out) >= PER_FILE_CAP:
                break
        return out

    def _load_tsu(self, path: Path, rng: random.Random) -> List[QuestionItem]:
        if not path.exists():
            logger.warning(f"TabIS file missing: {path}")
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        rng.shuffle(data)
        subset = "tsu_" + path.parent.name.replace("mc-", "").replace("_wiki", "")
        out: List[QuestionItem] = []
        for x in data:
            a, b = _parse_options(x.get("options", ""))
            p = x.get("prompt", "")
            i, j = p.find("Table:\n"), p.rfind("\nOptions:")
            table = p[i + len("Table:\n"):j].strip() if 0 <= i < j else None
            q = f"{x.get('question', '').strip()} {TSU_CONVENTION}"
            it = self._item(f"tabis_{subset}_{x.get('id')}", "tsu_synthetic", subset, table, q, a, b, x.get("response"),
                            {"task_type": x.get("task_type"), "source_dataset": "Wikipedia tables (TabIS TSU)"})
            if it:
                out.append(it)
            if len(out) >= PER_FILE_CAP:
                break
        return out
