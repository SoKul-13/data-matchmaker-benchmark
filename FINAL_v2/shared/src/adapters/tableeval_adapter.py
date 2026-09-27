"""TableEval (wenge-research; Hugging Face wenge-research/TableEval, Apache-2.0).  2,325 QA items over
617 real spreadsheets (Simplified / Traditional Chinese and English tables; questions are in Chinese).
Local file: data/raw/tableeval/TableEval-test.jsonl (hf_hub_download).

Framing: sub-tasks with short deterministic golds only - 简单查询, 条件查询, 排序, 数值计算, 统计, 多跳问题,
异常检测 (single-question items) and 表格大小探测 (gold rewritten as 'rows | cols').  Skipped: 拒答 (refusal),
合并单元格探测 (JSON gold), 对比/因果/趋势/相关性 analysis (subjective sentences), 多轮对话, 分组查询, multi-question
items.  Context = context_markdown (items over 3,000 chars dropped).  Original language is kept; the
appended answer-format instruction is Chinese.  A gold longer than 40 chars is typed freeform (rouge_l)."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, List, Optional

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)
RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "tableeval" / "TableEval-test.jsonl"
HF_REPO = "wenge-research/TableEval"
KEEP_SUBTASKS = {"简单查询", "条件查询", "排序", "数值计算", "统计", "多跳问题", "异常检测", "表格大小探测"}
LANG = {"简体中文": "zh-Hans", "繁体中文": "zh-Hant", "英文": "en"}
MAX_CTX, MAX_LIST, FREEFORM_CHARS = 3000, 6, 40
NUM_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


def _size_gold(ans: List[str]):
    rows = cols = None
    for a in ans:
        m = re.search(r"\d+", a)
        if not m:
            continue
        if "行" in a and rows is None:
            rows = m.group(0)
        elif "列" in a and cols is None:
            cols = m.group(0)
    return (rows, cols) if rows and cols else None


class TableEvalAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        path = Path(config.get("dataset_url") or RAW)
        if not path.exists():
            raise FileNotFoundError(f"TableEval file not found at {path}; download 'TableEval-test.jsonl' from hf:{HF_REPO} (repo_type=dataset).")
        items: List[QuestionItem] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            it = self._build(r)
            if it:
                items.append(it)
        return self._select(items, config)

    def _build(self, r: dict) -> Optional[QuestionItem]:
        sub = r.get("sub_task_name")
        if sub not in KEEP_SUBTASKS or len(r.get("question_list") or []) != 1:
            return None
        golds = []
        for g in r.get("golden_answer_list") or []:
            golds += g.get("问题列表") or []
        if len(golds) != 1:
            return None
        ans = golds[0].get("最终答案")
        if not isinstance(ans, list) or not ans or not all(isinstance(a, str) and a.strip() for a in ans) or len(ans) > MAX_LIST:
            return None
        ans = [a.strip() for a in ans]
        ctx = r["context"]
        md = (ctx.get("context_markdown") or "").strip()
        if not md or len(md) > MAX_CTX:
            return None
        q = r["question_list"][0].strip()
        instr = (r.get("instruction") or "").replace("文本：{context}\n\n问题：{question}", "").strip()
        aliases: List[str] = []
        gold_list = None
        answer_type = None
        if sub == "表格大小探测":
            rc = _size_gold(ans)
            if not rc:
                return None
            gold = f"{rc[0]} | {rc[1]}"
            aliases = [f"{rc[0]}行 {rc[1]}列", f"行数：{rc[0]}，列数：{rc[1]}", f"{rc[0]}, {rc[1]}", f"{rc[0]}行，{rc[1]}列"]
            fmt = "统计行列数量时需包含表头。请只按“行数 | 列数”的格式作答，例如 12 | 5，不要解释。"
            answer_type = "text"
        elif len(ans) > 1:
            gold, gold_list, aliases = " | ".join(ans), ans, ["、".join(ans), ", ".join(ans)]
            fmt = (instr + " " if instr else "") + "请只给出最终答案，多个答案之间用“ | ”分隔，不要解释。"
            answer_type = "text"
        else:
            gold = ans[0]
            fmt = (instr + " " if instr else "") + "请只给出最终答案，不要解释。"
            nums = NUM_RE.findall(gold)
            if len(nums) == 1 and nums[0] != gold:
                aliases = [nums[0]]
            if len(gold) > FREEFORM_CHARS:
                answer_type = "freeform"
        return QuestionItem(
            uid=f"tableeval_{r['id']}", question=f"{q}\n{fmt}", ground_truth=gold, difficulty=sub, context=md,
            dataset_name="tableeval", data_type="table", gold_list=gold_list, gold_aliases=aliases, answer_type=answer_type,
            native_metric="rouge_l" if answer_type == "freeform" else "auto",
            extra={"task_name": r.get("task_name"), "sub_task_name": sub, "language": LANG.get(ctx.get("table_language"), ctx.get("table_language")),
                   "table_language_raw": ctx.get("table_language"), "question_language": "zh", "table_structure_type": ctx.get("table_structure_type"),
                   "table_domain": ctx.get("table_domain"), "table_id": r.get("table_id"), "license": "Apache-2.0", "source": f"hf:{HF_REPO}"})
