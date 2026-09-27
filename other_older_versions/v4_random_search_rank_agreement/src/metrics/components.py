"""
Component metrics.  Each function maps (prediction, gold, gold_aliases, answer_type)
to a score in [0, 1].  The composite metric is a convex combination of these.

9 additive components + 1 hedge indicator
-----------------------------------------
 em          normalised exact match (set-equality for list golds, yes/no for boolean)
 num_tol     numeric tolerance hit (|p-g| <= 1% |g|), unit / percent aware; falls back to em
 num_decay   exp(-gamma * relative error) on the primary predicted number; falls back to em
 tok_prec    token precision (SQuAD style)
 tok_rec     token recall
 tok_f1      token F1
 edit_sim    normalised Levenshtein similarity on normalised strings
 rouge_l     LCS-based ROUGE-L F-measure over tokens
 jaccard     token-set Jaccard index
 hedge_free  1 if the answer commits to a single candidate, 0 if it hedges.  This is NOT an
             additive component: the composite is  (sum_k w_k m_k) * (1 - lambda * hedged)
             with the hedge penalty lambda calibrated together with the weights.

All metrics are computed as the max over gold aliases (except hedge_free which is
independent of the gold).  Numeric components use the *primary* predicted number
(the first distinct candidate) so that hedged answers such as "12 or 15" are not
rewarded for the closest candidate.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
from rapidfuzz.distance import Levenshtein

from .answer_types import AnswerType, normalize_boolean, split_list_answer
from .normalize import extract_final_answer, extract_numbers, normalize_text, ParsedNumber

COMPONENT_NAMES: List[str] = [
    "em", "num_tol", "num_decay", "tok_prec", "tok_rec", "tok_f1",
    "edit_sim", "rouge_l", "jaccard",
]
K = len(COMPONENT_NAMES)          # 9 additive components
HEDGE_COL = K                     # column index of the hedge_free indicator in component_vector()
ALL_COLUMNS = COMPONENT_NAMES + ["hedge_free"]

NUM_TOLERANCE = 0.01     # relative tolerance for num_tol
NUM_ABS_EPS = 1e-6       # absolute epsilon for zero golds
DECAY_GAMMA = 2.5        # exp(-gamma * rel_err); rel_err clipped to [0, 2]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _prepare_gold(gold: str, aliases: Optional[Iterable[str]], atype: AnswerType) -> List[str]:
    cands = [gold] + [a for a in (aliases or []) if a and a != gold]
    if atype == AnswerType.BOOLEAN:
        b = normalize_boolean(gold)
        return [b or normalize_text(gold)]
    return cands


def _prepare_pred(pred: str, atype: AnswerType) -> str:
    ans = extract_final_answer(pred)
    if atype == AnswerType.BOOLEAN:
        b = normalize_boolean(ans)
        if b is None:
            b = normalize_boolean(pred)
        return b if b is not None else normalize_text(ans)
    return ans


def _distinct_numbers(nums: Sequence[ParsedNumber], gold_is_year: bool) -> List[ParsedNumber]:
    """Deduplicate candidate numbers by scaled value; drop year-like numbers unless gold is a year."""
    seen, out = set(), []
    for n in nums:
        if n.is_year_like and not gold_is_year:
            continue
        key = round(n.scaled, 9)
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    return out


def _rel_err(p: ParsedNumber, g: ParsedNumber) -> float:
    """Minimum relative error over unit / percent interpretations."""
    best = math.inf
    for gv in g.equivalents():
        for pv in p.equivalents():
            denom = max(abs(gv), NUM_ABS_EPS)
            err = abs(pv - gv) / denom
            if abs(pv - gv) <= NUM_ABS_EPS:
                err = 0.0
            best = min(best, err)
    return best


def _lcs_len(a: Sequence[str], b: Sequence[str]) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


# --------------------------------------------------------------------------- #
# individual components (all take normalised token lists / strings)
# --------------------------------------------------------------------------- #

def _em(pred_norm: str, gold_norm: str, gold_list: Optional[List[str]], pred_raw: str = "") -> float:
    if gold_list and len(gold_list) > 1:
        raw = pred_raw or pred_norm
        if "|" in raw or ";" in raw:
            parts = split_list_answer(raw)
        else:
            parts = [x for x in re.split(r"\s*(?:,|\band\b)\s*", raw) if x.strip()]
        pred_parts = {normalize_text(x) for x in parts if normalize_text(x)}
        return 1.0 if pred_parts == {normalize_text(g) for g in gold_list} else 0.0
    return 1.0 if pred_norm == gold_norm else 0.0


def _prf(pred_toks: List[str], gold_toks: List[str]):
    if not pred_toks and not gold_toks:
        return 1.0, 1.0, 1.0
    if not pred_toks or not gold_toks:
        return 0.0, 0.0, 0.0
    common = Counter(pred_toks) & Counter(gold_toks)
    n = sum(common.values())
    if n == 0:
        return 0.0, 0.0, 0.0
    p = n / len(pred_toks)
    r = n / len(gold_toks)
    return p, r, 2 * p * r / (p + r)


def _rouge_l(pred_toks: List[str], gold_toks: List[str]) -> float:
    if not pred_toks or not gold_toks:
        return 1.0 if pred_toks == gold_toks else 0.0
    l = _lcs_len(pred_toks, gold_toks)
    if l == 0:
        return 0.0
    p, r = l / len(pred_toks), l / len(gold_toks)
    return 2 * p * r / (p + r)


def _jaccard(pred_toks: List[str], gold_toks: List[str]) -> float:
    a, b = set(pred_toks), set(gold_toks)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0


def _edit_sim(pred_norm: str, gold_norm: str) -> float:
    if not pred_norm and not gold_norm:
        return 1.0
    return float(Levenshtein.normalized_similarity(pred_norm, gold_norm))


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #

def component_vector(pred: Optional[str], gold: str, aliases: Optional[Iterable[str]] = None,
                     atype: Optional[AnswerType] = None, *, gold_list: Optional[List[str]] = None) -> np.ndarray:
    """Return a (K+1)-vector: K component scores followed by the hedge_free indicator."""
    from .answer_types import detect_answer_type  # local import to avoid cycle at import time
    if atype is None:
        atype = detect_answer_type(gold, aliases)
    pred = pred or ""
    gold_cands = _prepare_gold(gold, aliases, atype)
    pred_ans = _prepare_pred(pred, atype)
    pred_norm = normalize_text(pred_ans)
    pred_toks = pred_norm.split()

    # ---- hedging: multiple distinct numeric candidates, "A or B" / "either", or an enumeration
    raw_ans = extract_final_answer(pred)          # before boolean normalisation
    pred_nums_all = extract_numbers(pred_ans)
    gold_nums_primary = extract_numbers(gold_cands[0])
    gold_is_year = bool(gold_nums_primary) and gold_nums_primary[0].is_year_like
    pred_nums = _distinct_numbers(pred_nums_all, gold_is_year)
    hedged = False
    if atype == AnswerType.NUMERIC and len(pred_nums) > 1:
        # a value and its percent/scale restatement count as one candidate
        eqs = [set(round(v, 6) for v in n.equivalents()) for n in pred_nums]
        merged = []
        for e in eqs:
            if not any(e & m for m in merged):
                merged.append(e)
        hedged = len(merged) > 1
    if atype in (AnswerType.TEXT, AnswerType.BOOLEAN, AnswerType.NUMERIC):
        low = " " + raw_ans.lower() + " "
        gold_has_or = any(" or " in g.lower() for g in gold_cands)
        if (" or " in low and not gold_has_or) or low.strip().startswith("either"):
            hedged = True
    if atype == AnswerType.BOOLEAN:
        toks = set(normalize_text(raw_ans).split())
        if ("yes" in toks or "true" in toks) and ("no" in toks or "false" in toks):
            hedged = True
    if atype == AnswerType.TEXT:
        # enumerating several SHORT candidates for a gold that is not itself such a list
        def _items(sx):
            return [x.strip() for x in re.split(r"\s*(?:[,|;]|\band\b)\s*", sx) if x.strip()]
        pred_items = _items(raw_ans)
        short_items = [x for x in pred_items if len(x.split()) <= 6]
        n_gold_items = len(gold_list) if gold_list else max(len(_items(g)) for g in gold_cands)
        if len(pred_items) == len(short_items) and len(short_items) >= max(3, n_gold_items + 2):
            hedged = True
    hedge_free = 0.0 if hedged else 1.0

    best = np.zeros(K + 1, dtype=float)
    for g in gold_cands:
        gold_norm = normalize_text(g)
        gold_toks = gold_norm.split()
        em = _em(pred_norm, gold_norm, gold_list, pred_ans)
        p, r, f1 = _prf(pred_toks, gold_toks)
        rl = _rouge_l(pred_toks, gold_toks)
        jac = _jaccard(pred_toks, gold_toks)
        ed = _edit_sim(pred_norm, gold_norm)

        # numeric components
        g_nums = extract_numbers(g)
        if atype == AnswerType.NUMERIC and g_nums:
            gnum = g_nums[0]
            if pred_nums:
                primary = pred_nums[0]
                err = _rel_err(primary, gnum)
                num_tol = 1.0 if err <= NUM_TOLERANCE else 0.0
                num_decay = math.exp(-DECAY_GAMMA * min(err, 2.0))
            else:
                num_tol, num_decay = 0.0, 0.0
        else:
            num_tol, num_decay = em, em

        vec = np.array([em, num_tol, num_decay, p, r, f1, ed, rl, jac, hedge_free])
        if vec[:K].sum() > best[:K].sum():
            best = vec
    best[HEDGE_COL] = hedge_free
    return best


def component_dict(pred: Optional[str], gold: str, aliases: Optional[Iterable[str]] = None,
                   atype: Optional[AnswerType] = None, **kw) -> Dict[str, float]:
    v = component_vector(pred, gold, aliases, atype, **kw)
    return {n: float(x) for n, x in zip(ALL_COLUMNS, v)}
