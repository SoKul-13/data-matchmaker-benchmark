"""
Synthetic known-quality anchors (the calibration target when human labels are unavailable).

For every gold answer we generate answers of KNOWN utility u in [0, 1]:
  u = 1.0   correct, in several surface styles (bare / verbose / paraphrase / tagged)
  u < 1     one error operator applied, with a stated utility (severity scale below)
The anchor set is what metric selection and weight search are scored against: a good metric ranks
anchors by u (Spearman), separates correct from wrong (AUC), and gives the same score to the same u
regardless of dataset or style.  The severity scale is the ONLY hand-set input; it is perturbed in
validation.  Operators are typed: numeric / text / boolean / freeform.
"""
from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from metrics.answer_types import AnswerType
from metrics.normalize import canonical_number_string, extract_numbers

UTILITY: Dict[str, float] = {
    "identity": 1.00, "verbose": 1.00, "tagged": 1.00, "paraphrase": 0.95, "unit_variant": 1.00,
    "near_miss_small": 0.75, "near_miss_medium": 0.45, "near_miss_large": 0.15, "digit_typo": 0.20,
    "magnitude": 0.05, "sign_flip": 0.05, "wrong_random": 0.00, "no_answer": 0.00,
    "hedge": 0.30, "list_dump": 0.25, "partial": 0.50, "superset": 0.60, "typo": 0.60, "shuffled": 0.40, "flip": 0.00,
}
NO_ANSWER = ["I cannot determine the answer from the given information.", "The information provided is insufficient to answer.", "Unknown"]
VERBOSE = ["Based on the provided data, the answer is {a}.", "The answer is {a}.", "Therefore, the final answer is {a}.", "{a} is the correct answer according to the table."]
_STOP = {"the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "and", "is", "was", "were", "are", "by", "as", "that", "which", "it", "its", "this", "from"}


def _rng(*parts) -> random.Random:
    return random.Random(int(hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:12], 16))


@dataclass
class Item:
    uid: str
    dataset: str
    gold: str
    atype: AnswerType
    aliases: List[str]
    gold_list: Optional[List[str]] = None


def _num(item):
    n = extract_numbers(item.gold); return n[0] if n else None


def _fmt(v, like):
    g = extract_numbers(like); dec = 0
    if g:
        raw = like[g[0].span[0]:g[0].span[1]]
        dec = len(raw.split(".")[1].rstrip("%").strip()) if "." in raw else 0
    s = canonical_number_string(round(v, min(dec + 1, 4)))
    m = re.search(r"(%|percent|million|billion|thousand|trillion)", like, re.I)
    return (f"{s}{m.group(1)}" if m and m.group(1) == "%" else f"{s} {m.group(1)}") if m else s


def _wrong_random(item, rng, pool):
    o = [p for p in pool if p.uid != item.uid and p.atype == item.atype]
    return rng.choice(o).gold if o else NO_ANSWER[0]


def apply(op: str, item: Item, rng: random.Random, pool: Sequence[Item]) -> str:
    n = _num(item)
    if op == "identity":
        return item.gold
    if op == "verbose":
        return rng.choice(VERBOSE).format(a=item.gold)
    if op == "tagged":
        return f"<REASONING>Let me check the table carefully.</REASONING><FINAL_ANSWER>{item.gold}</FINAL_ANSWER>"
    if op == "paraphrase":
        return paraphrase(item, rng)
    if op == "unit_variant":
        if item.atype == AnswerType.NUMERIC and n is not None:
            if n.is_percent:
                return canonical_number_string(round(n.value / 100, 6))
            if "million" in item.gold.lower():
                return canonical_number_string(n.value * 1e6)
            if 0 < abs(n.value) < 1:
                return f"{canonical_number_string(round(n.value * 100, 6))}%"
            return f"${item.gold}" if "$" not in item.gold else item.gold.replace("$", "USD ")
        return item.gold
    if op in ("near_miss_small", "near_miss_medium", "near_miss_large"):
        if n is None:
            return apply("partial", item, rng, pool)
        lo, hi = {"near_miss_small": (0.011, 0.03), "near_miss_medium": (0.03, 0.15), "near_miss_large": (0.15, 0.6)}[op]
        u = rng.uniform(lo, hi) * rng.choice([-1, 1])
        return _fmt(n.value * (1 + u) if n.value else u, item.gold)
    if op == "digit_typo":
        if n is None:
            return apply("typo", item, rng, pool)
        s = canonical_number_string(n.value); d = [i for i, ch in enumerate(s) if ch.isdigit()]
        if not d:
            return apply("magnitude", item, rng, pool)
        i = rng.choice(d); s2 = s[:i] + str((int(s[i]) + rng.randint(1, 9)) % 10) + s[i + 1:]
        try:
            return _fmt(float(s2), item.gold)
        except ValueError:
            return apply("magnitude", item, rng, pool)
    if op == "magnitude":
        return _fmt(n.value * rng.choice([10, 0.1, 100, 0.01]), item.gold) if n is not None else _wrong_random(item, rng, pool)
    if op == "sign_flip":
        return _fmt(-n.value, item.gold) if n is not None and n.value else _wrong_random(item, rng, pool)
    if op == "wrong_random":
        return _wrong_random(item, rng, pool)
    if op == "no_answer":
        return rng.choice(NO_ANSWER)
    if op == "hedge":
        if item.atype == AnswerType.NUMERIC and n is not None:
            return f"{item.gold} or {_fmt(n.value * (1 + rng.choice([-1, 1]) * rng.uniform(0.1, 0.4)), item.gold)}"
        if item.atype == AnswerType.BOOLEAN:
            return "yes or no, it depends on the interpretation"
        return f"{item.gold} or {_wrong_random(item, rng, pool)}"
    if op == "list_dump":
        others = [p.gold for p in pool if p.uid != item.uid and p.atype == item.atype]; rng.shuffle(others)
        c = [item.gold] + others[:3]; rng.shuffle(c)
        return "yes or no" if item.atype == AnswerType.BOOLEAN else (" ".join(c) if item.atype == AnswerType.FREEFORM else ", ".join(c))
    if op == "partial":
        if item.gold_list and len(item.gold_list) > 1:
            return " | ".join(item.gold_list[: rng.randint(1, len(item.gold_list) - 1)])
        t = item.gold.split()
        if len(t) <= 1:
            return apply("typo", item, rng, pool)
        k = max(1, len(t) // 2); s = rng.randint(0, len(t) - k); return " ".join(t[s:s + k])
    if op == "superset":
        o = _wrong_random(item, rng, pool)
        return f"{item.gold} {o}" if item.atype == AnswerType.FREEFORM else f"{item.gold}, {o}"
    if op == "typo":
        s = list(item.gold)
        if len(s) < 3:
            return _wrong_random(item, rng, pool)
        for _ in range(1 + (len(s) > 8)):
            i = rng.randrange(len(s))
            if s[i].isalpha():
                s[i] = rng.choice("abcdefghijklmnopqrstuvwxyz")
            elif s[i].isdigit():
                s[i] = str((int(s[i]) + rng.randint(1, 9)) % 10)
        return "".join(s)
    if op == "shuffled":
        t = item.gold.split(); rng.shuffle(t); return " ".join(t)
    if op == "flip":
        return "no" if item.gold.strip().lower() in {"yes", "true", "1", "entailed"} else "yes"
    raise ValueError(op)


def paraphrase(item: Item, rng: random.Random) -> str:
    n = _num(item)
    if item.atype == AnswerType.NUMERIC and n is not None:
        return apply("unit_variant", item, rng, [])
    if item.atype == AnswerType.BOOLEAN:
        return rng.choice(["True", "true."]) if item.gold.lower() in {"yes", "true", "1"} else rng.choice(["False", "false."])
    t = item.gold.split()
    if len(t) <= 8:
        return rng.choice([item.gold.upper(), item.gold.lower(), item.gold.title(), f"the {item.gold}", f"{item.gold}."])
    clauses = [c.strip() for c in re.split(r",\s+|\s+and\s+|;\s+", item.gold) if c.strip()]
    if len(clauses) > 1:
        k = rng.randrange(1, len(clauses)); clauses = clauses[k:] + clauses[:k]
    w = [x for x in " ".join(clauses).split() if not (x.lower().strip(".,") in _STOP and rng.random() < 0.5)]
    out = " ".join(w); return out[0].upper() + out[1:] if out else item.gold


OPS_BY_TYPE: Dict[AnswerType, List[str]] = {
    AnswerType.NUMERIC: ["identity", "verbose", "tagged", "paraphrase", "unit_variant", "near_miss_small", "near_miss_medium", "near_miss_large",
                         "digit_typo", "magnitude", "sign_flip", "wrong_random", "no_answer", "hedge", "list_dump"],
    AnswerType.TEXT: ["identity", "verbose", "tagged", "paraphrase", "partial", "superset", "typo", "wrong_random", "no_answer", "hedge", "list_dump"],
    AnswerType.BOOLEAN: ["identity", "verbose", "tagged", "paraphrase", "flip", "no_answer", "hedge"],
    AnswerType.FREEFORM: ["identity", "verbose", "tagged", "paraphrase", "partial", "superset", "shuffled", "wrong_random", "no_answer", "list_dump"],
}


def generate(items: Sequence[Item], seed: int = 20260908) -> List[dict]:
    """Every applicable operator for every item -> rows {uid, dataset, atype, op, utility, prediction}."""
    rows = []
    for it in items:
        for op in OPS_BY_TYPE[it.atype]:
            rng = _rng(seed, it.uid, op)
            rows.append({"uid": it.uid, "dataset": it.dataset, "atype": it.atype.value, "op": op, "utility": UTILITY[op],
                         "prediction": apply(op, it, rng, items)})
    return rows
