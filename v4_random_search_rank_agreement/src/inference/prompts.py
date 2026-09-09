"""Prompt construction for QA items.  The same template is used for every model."""
from __future__ import annotations

from typing import Dict

SYSTEM_PROMPT = (
    "You are a precise question-answering system for financial documents, tables and "
    "quantitative reasoning. Use ONLY the provided context when context is given; if no "
    "context is given, answer from your own knowledge. Reason briefly and then finish with "
    "one line of the exact form:\nFINAL ANSWER: <answer>\n"
    "The FINAL ANSWER line must contain only the answer, nothing else."
)

TYPE_INSTRUCTIONS = {
    "numeric": "The answer is a single number. Include a percent sign or unit word (e.g. million) "
               "only if the question asks for it. Do not give a range or several candidates.",
    "boolean": "Answer exactly 'yes' or 'no'.",
    "text": "Give the shortest exact answer (a name, phrase or value). If several items are "
            "required, separate them with ' | '.",
    "freeform": "Answer in one complete, informative sentence.",
}


def build_prompt(item: Dict) -> str:
    parts = []
    ctx = item.get("context")
    tbl = item.get("table_data")
    if ctx:
        parts.append(f"### Context\n{ctx}")
    if tbl:
        parts.append(f"### Table\n{tbl}")
    parts.append(f"### Question\n{item['question']}")
    parts.append("### Answer format\n" + TYPE_INSTRUCTIONS.get(item.get("answer_type", "text"), TYPE_INSTRUCTIONS["text"]))
    return "\n\n".join(parts)
