"""
Gold-answer typing.

Every gold answer is routed to one of four calibration groups.  The composite
metric uses a separate weight vector per group, but the *same* component
functions, so the grid search is well posed and the final score is comparable
across datasets that mix types (e.g. TAT-QA, WikiTableQuestions, FinanceBench).
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Iterable, List, Optional

from .normalize import extract_numbers, normalize_text

_YES = {"yes", "true", "1", "entailed", "entail", "y", "t"}
_NO = {"no", "false", "0", "refuted", "refute", "n", "f", "not entailed"}

_UNIT_WORDS = {
    "million", "millions", "billion", "billions", "thousand", "thousands", "trillion", "trillions",
    "percent", "percentage", "points", "point", "pp", "dollars", "dollar", "usd", "eur", "gbp",
    "units", "unit", "years", "year", "months", "month", "days", "day", "weeks", "week", "hours",
    "hour", "minutes", "minute", "seconds", "second", "people", "shares", "share", "times", "x",
    "cents", "cent", "kg", "km", "m", "cm", "mm", "lb", "lbs", "oz", "ft", "in", "mi", "ml", "l",
    "usd", "mn", "bn", "k", "approximately", "about", "roughly", "around", "per", "of", "in", "to",
    "and", "or", "total", "net", "increase", "decrease", "more", "less", "than", "each", "one",
}


class AnswerType(str, Enum):
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    TEXT = "text"          # short span, entity, list of short spans, multiple choice
    FREEFORM = "freeform"  # sentence-length generative answers (FeTaQA, some FinanceBench)


def normalize_boolean(text: Optional[str]) -> Optional[str]:
    """Map a free-form answer onto 'yes' / 'no' (None if no boolean token found).

    Looks at the whole normalised answer first ('yes', 'true', '1'), then at the
    first token, then anywhere in the string with word boundaries.
    """
    if text is None:
        return None
    s = normalize_text(text)
    if not s:
        return None
    if s in _YES:
        return "yes"
    if s in _NO:
        return "no"
    if s.startswith("not entailed"):
        return "no"
    toks = s.split()
    if toks[0] in _YES:
        return "yes"
    if toks[0] in _NO:
        return "no"
    # first occurrence wins
    best = None
    for i, t in enumerate(toks):
        if t in _YES - {"1", "y", "t"}:
            best = (i, "yes"); break
        if t in _NO - {"0", "n", "f"}:
            best = (i, "no"); break
    return best[1] if best else None


def _looks_numeric(gold: str) -> bool:
    nums = extract_numbers(gold)
    if len(nums) != 1:
        # allow ranges like "5-7" or "between 5 and 7"? -> treat as text
        return False
    norm = normalize_text(gold, keep_percent=False)
    toks = [t for t in norm.split() if not re.fullmatch(r"-?\d+(\.\d+)?", t)]
    residual = [t for t in toks if t not in _UNIT_WORDS]
    return len(residual) <= 1


_WORD_BOOL = (_YES | _NO) - {"0", "1", "y", "n", "t", "f"}


def detect_answer_type(gold: str, aliases: Optional[Iterable[str]] = None, *,
                       dataset_hint: Optional[str] = None, freeform_min_tokens: int = 9,
                       gold_list: Optional[List[str]] = None) -> AnswerType:
    """Infer the calibration group of a gold answer.

    Order of tests: boolean (word form only: yes/no/true/false/entailed/refuted)
    -> list golds are TEXT -> numeric -> freeform (long) -> text.
    `dataset_hint` may force a type ('boolean' for TabFact/BoolQ, 'freeform' for FeTaQA);
    a boolean hint is only honoured when the gold really is a yes/no word.
    """
    gold = (gold or "").strip()
    if dataset_hint == "boolean" and normalize_text(gold) not in _YES | _NO:
        dataset_hint = None
    if dataset_hint in {t.value for t in AnswerType}:
        return AnswerType(dataset_hint)
    if normalize_text(gold) in _WORD_BOOL:
        return AnswerType.BOOLEAN
    if gold_list and len(gold_list) > 1:
        return AnswerType.TEXT
    cands = [gold] + [a for a in (aliases or []) if a]
    if any(_looks_numeric(c) for c in cands):
        return AnswerType.NUMERIC
    if len(normalize_text(gold).split()) >= freeform_min_tokens:
        return AnswerType.FREEFORM
    return AnswerType.TEXT


def split_list_answer(gold: str) -> List[str]:
    """WikiTableQuestions style 'A|B|C' or 'A; B' multi-answers -> list."""
    if "|" in gold:
        parts = [p.strip() for p in gold.split("|")]
    elif ";" in gold:
        parts = [p.strip() for p in gold.split(";")]
    else:
        return [gold.strip()]
    return [p for p in parts if p]
