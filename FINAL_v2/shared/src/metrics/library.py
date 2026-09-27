"""
Answer-level metric library: 100 metrics, each  f(ctx) -> float in [0, 1].

All metrics compare a model's final answer with a gold answer (max over gold aliases where the
metric is alias-sensitive).  They are grouped in families; `METRICS` maps name -> (family, fn).
`compute_all(pred, gold, aliases, atype, gold_list)` returns the 100-vector in METRIC_NAMES order.

Families (count):  em 10 | num_tol 12 | num_graded 9 | token 12 | char 9 | seq 10 | set 7 |
                   semantic 8 (optional, needs sentence-transformers; zeros if unavailable) |
                   structure 7 | length 5 | commit 4 | task 7
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from rapidfuzz.distance import DamerauLevenshtein, Jaro, JaroWinkler, Levenshtein

from .answer_types import AnswerType, detect_answer_type, normalize_boolean, split_list_answer
from .normalize import ParsedNumber, canonical_number_string, extract_final_answer, extract_numbers, normalize_text

_STOP = set("the a an of in on at to for and or is are was were be by with as that this it its from than then "
            "which what who how many much total per each".split())
_YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)\b")


# --------------------------------------------------------------------------------------------- context
@dataclass
class Ctx:
    pred_raw: str
    ans: str                      # extracted final answer (templates stripped)
    ans_norm: str
    ans_toks: List[str]
    golds: List[str]              # gold + aliases
    golds_norm: List[str]
    golds_toks: List[List[str]]
    atype: AnswerType
    gold_list: Optional[List[str]]
    pred_nums: List[ParsedNumber]
    gold_nums: List[List[ParsedNumber]]
    program: Optional[str] = None
    cache: dict = field(default_factory=dict)

    def best(self, fn: Callable[[str, List[str], str, List[str]], float]) -> float:
        """max over golds of fn(ans_norm, ans_toks, gold_norm, gold_toks)"""
        return max((fn(self.ans_norm, self.ans_toks, g, t) for g, t in zip(self.golds_norm, self.golds_toks)), default=0.0)


def make_ctx(pred, gold, aliases=None, atype=None, gold_list=None, program=None) -> Ctx:
    pred = pred or ""
    if atype is None:
        atype = detect_answer_type(gold, aliases, gold_list=gold_list)
    ans = extract_final_answer(pred)
    golds = [gold] + [a for a in (aliases or []) if a and a != gold]
    if atype == AnswerType.BOOLEAN:
        b = normalize_boolean(ans) or normalize_boolean(pred)
        ans = b if b is not None else ans
        golds = [normalize_boolean(gold) or gold]
    ans_norm = normalize_text(ans)
    return Ctx(pred, ans, ans_norm, ans_norm.split(), golds, [normalize_text(g) for g in golds],
               [normalize_text(g).split() for g in golds], atype, gold_list, extract_numbers(ans), [extract_numbers(g) for g in golds], program)


# --------------------------------------------------------------------------------------------- helpers
def _prf(p: List[str], g: List[str], beta: float = 1.0) -> Tuple[float, float, float]:
    if not p and not g:
        return 1.0, 1.0, 1.0
    if not p or not g:
        return 0.0, 0.0, 0.0
    n = sum((Counter(p) & Counter(g)).values())
    if n == 0:
        return 0.0, 0.0, 0.0
    pr, rc = n / len(p), n / len(g)
    f = (1 + beta ** 2) * pr * rc / (beta ** 2 * pr + rc)
    return pr, rc, f


def _ngrams(t: Sequence[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(t[i:i + n]) for i in range(len(t) - n + 1)]


def _lcs(a: Sequence, b: Sequence) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def _f(p, r):
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


def _rel_err(p: ParsedNumber, g: ParsedNumber) -> float:
    best = math.inf
    for gv in g.equivalents():
        for pv in p.equivalents():
            err = 0.0 if abs(pv - gv) <= 1e-6 else abs(pv - gv) / max(abs(gv), 1e-6)
            best = min(best, err)
    return best


def _primary_pair(c: Ctx) -> Optional[Tuple[ParsedNumber, ParsedNumber, float]]:
    """(primary predicted number, best gold number, min relative error) or None."""
    if "pp" in c.cache:
        return c.cache["pp"]
    res = None
    if c.pred_nums:
        gold_is_year = any(n.is_year_like for gs in c.gold_nums for n in gs[:1])
        cands = [n for n in c.pred_nums if not n.is_year_like or gold_is_year] or c.pred_nums
        p = cands[0]
        for gs in c.gold_nums:
            for g in gs[:1]:
                e = _rel_err(p, g)
                if res is None or e < res[2]:
                    res = (p, g, e)
    c.cache["pp"] = res
    return res


def _stem(t: str) -> str:
    for suf in ("ing", "ies", "es", "ed", "ly", "s"):
        if len(t) > 4 and t.endswith(suf):
            return t[: -len(suf)] + ("y" if suf == "ies" else "")
    return t


def _chrf(a: str, b: str, n: int, beta: float = 2.0) -> float:
    a, b = a.replace(" ", ""), b.replace(" ", "")
    if not a or not b:
        return 1.0 if a == b else 0.0
    ga, gb = Counter(a[i:i + n] for i in range(len(a) - n + 1)), Counter(b[i:i + n] for i in range(len(b) - n + 1))
    if not ga or not gb:
        return 0.0
    m = sum((ga & gb).values())
    if m == 0:
        return 0.0
    p, r = m / sum(ga.values()), m / sum(gb.values())
    return (1 + beta ** 2) * p * r / (beta ** 2 * p + r)


def _bleu(p: List[str], g: List[str], max_n: int) -> float:
    if not p or not g:
        return 0.0
    logs = []
    for n in range(1, max_n + 1):
        pn, gn = Counter(_ngrams(p, n)), Counter(_ngrams(g, n))
        tot = max(sum(pn.values()), 1)
        match = sum((pn & gn).values())
        logs.append(math.log((match + 1) / (tot + 1)))    # add-one smoothing
    bp = 1.0 if len(p) >= len(g) else math.exp(1 - len(g) / max(len(p), 1))
    return bp * math.exp(sum(logs) / max_n)


def _list_parts(c: Ctx) -> List[str]:
    raw = c.ans
    parts = split_list_answer(raw) if ("|" in raw or ";" in raw) else [x for x in re.split(r"\s*(?:,|\band\b)\s*", raw) if x.strip()]
    return [normalize_text(x) for x in parts if normalize_text(x)]


def _gold_part_options(c: Ctx) -> List[List[str]]:
    """candidate gold part-lists: the declared gold_list, plus every alias that is itself a '|' list"""
    opts = []
    if c.gold_list:
        opts.append([normalize_text(g) for g in c.gold_list])
    for g in c.golds:
        if "|" in g:
            opts.append([normalize_text(x) for x in split_list_answer(g)])
    return opts or [[c.golds_norm[0]]]


def _gold_parts(c: Ctx) -> List[str]:
    return _gold_part_options(c)[0]


def _best_parts(c: Ctx, fn) -> float:
    p = _list_parts(c)
    return max(fn(p, g) for g in _gold_part_options(c))


def _is_hedged(c: Ctx) -> bool:
    if "hedged" in c.cache:
        return c.cache["hedged"]
    low = " " + c.ans.lower() + " "
    h = (" or " in low and not any(" or " in g.lower() for g in c.golds)) or low.strip().startswith("either")
    if c.atype == AnswerType.NUMERIC and len(c.pred_nums) > 1:
        eqs = [set(round(v, 6) for v in n.equivalents()) for n in c.pred_nums if not n.is_year_like]
        merged: List[set] = []
        for e in eqs:
            if not any(e & m for m in merged):
                merged.append(e)
        h = h or len(merged) > 1
    if c.atype == AnswerType.BOOLEAN:
        toks = set(normalize_text(extract_final_answer(c.pred_raw)).split())
        h = h or (bool(toks & {"yes", "true"}) and bool(toks & {"no", "false"}))
    if c.atype == AnswerType.TEXT:
        parts = _list_parts(c)
        n_gold = len(c.gold_list) if c.gold_list else 1
        h = h or (len(parts) >= max(3, n_gold + 2) and all(len(x.split()) <= 6 for x in parts))
    c.cache["hedged"] = h
    return h


_ABSTAIN = re.compile(r"\b(cannot|can't|unable|insufficient|not (?:enough|available|provided|possible)|no answer|unknown|n/a)\b", re.I)


# --------------------------------------------------------------------------------------------- metric definitions
METRICS: Dict[str, Tuple[str, Callable[[Ctx], float]]] = {}


def metric(family: str):
    def deco(fn):
        METRICS[fn.__name__] = (family, fn)
        return fn
    return deco


# ---- family: exact match (10)
@metric("em")
def em_raw(c):                 return float(any(c.ans.strip() == g.strip() for g in c.golds))
@metric("em")
def em_norm(c):                return float(any(c.ans_norm == g for g in c.golds_norm))
@metric("em")
def em_casefold(c):            return float(any(c.ans.strip().lower() == g.strip().lower() for g in c.golds))
@metric("em")
def em_no_space(c):            return float(any(c.ans_norm.replace(" ", "") == g.replace(" ", "") for g in c.golds_norm))
@metric("em")
def em_numbers_only(c):
    pn = [canonical_number_string(n.value) for n in c.pred_nums]
    return float(any(pn and pn == [canonical_number_string(n.value) for n in gs] for gs in c.gold_nums))
@metric("em")
def em_first_token(c):         return float(bool(c.ans_toks) and any(t and c.ans_toks[0] == t[0] for t in c.golds_toks))
@metric("em")
def em_list_set(c):            return _best_parts(c, lambda p, g: float(set(p) == set(g)))
@metric("em")
def em_list_ordered(c):        return _best_parts(c, lambda p, g: float(p == g))
@metric("em")
def list_recall(c):            return _best_parts(c, lambda p, g: len(set(g) & set(p)) / len(set(g)) if g else 0.0)
@metric("em")
def list_precision(c):         return _best_parts(c, lambda p, g: len(set(g) & set(p)) / len(set(p)) if p else 0.0)

# ---- family: numeric tolerance ladder (12)
def _tol(th):
    def fn(c):
        pp = _primary_pair(c)
        if pp is None:
            return em_norm(c) if c.atype != AnswerType.NUMERIC else 0.0
        return float(pp[2] <= th)
    return fn
for _th, _nm in [(0.001, "num_tol_0p1"), (0.005, "num_tol_0p5"), (0.01, "num_tol_1"), (0.02, "num_tol_2"), (0.05, "num_tol_5"), (0.10, "num_tol_10"), (0.20, "num_tol_20")]:
    _fn = _tol(_th); _fn.__name__ = _nm; metric("num_tol")(_fn); globals()[_nm] = _fn
@metric("num_tol")
def num_abs_0p01(c):
    pp = _primary_pair(c); return 0.0 if pp is None else float(min(abs(pv - gv) for gv in pp[1].equivalents() for pv in pp[0].equivalents()) <= 0.01)
@metric("num_tol")
def num_sign_agree(c):
    pp = _primary_pair(c); return 0.0 if pp is None else float((pp[0].value >= 0) == (pp[1].value >= 0))
@metric("num_tol")
def num_magnitude_agree(c):
    pp = _primary_pair(c)
    if pp is None or pp[0].value == 0 or pp[1].value == 0:
        return 0.0 if pp is None else float(pp[0].value == pp[1].value)
    return float(abs(math.log10(abs(pp[0].scaled)) - math.log10(abs(pp[1].scaled))) < 0.5)
@metric("num_tol")
def num_unit_equiv_hit(c):
    pp = _primary_pair(c); return 0.0 if pp is None else float(pp[2] <= 0.01 and (pp[0].is_percent != pp[1].is_percent or pp[0].scale != pp[1].scale))
@metric("num_tol")
def num_round_to_gold_precision(c):
    pp = _primary_pair(c)
    if pp is None:
        return 0.0
    g = canonical_number_string(pp[1].value); dec = len(g.split(".")[1]) if "." in g else 0
    return float(round(pp[0].value, dec) == round(pp[1].value, dec))

# ---- family: numeric graded (9)
def _decay(gamma):
    def fn(c):
        pp = _primary_pair(c)
        if pp is None:
            return em_norm(c) if c.atype != AnswerType.NUMERIC else 0.0
        return math.exp(-gamma * min(pp[2], 2.0))
    return fn
for _g, _nm in [(0.5, "num_decay_0p5"), (1.0, "num_decay_1"), (2.5, "num_decay_2p5"), (5.0, "num_decay_5"), (10.0, "num_decay_10")]:
    _fn = _decay(_g); _fn.__name__ = _nm; metric("num_graded")(_fn); globals()[_nm] = _fn
@metric("num_graded")
def num_inv_rel(c):
    pp = _primary_pair(c); return 0.0 if pp is None else 1.0 / (1.0 + pp[2])
@metric("num_graded")
def num_linear(c):
    pp = _primary_pair(c); return 0.0 if pp is None else 1.0 - min(pp[2], 1.0)
@metric("num_graded")
def num_log_ratio(c):
    pp = _primary_pair(c)
    if pp is None or pp[0].value == 0 or pp[1].value == 0 or (pp[0].value < 0) != (pp[1].value < 0):
        return 0.0 if pp is None or pp[0].value != pp[1].value else 1.0
    return math.exp(-min(abs(math.log(abs(v / g))) for g in pp[1].equivalents() for v in pp[0].equivalents() if g and v and (v > 0) == (g > 0)))
@metric("num_graded")
def num_smape(c):
    pp = _primary_pair(c)
    if pp is None:
        return 0.0
    v, g = pp[0].value, pp[1].value
    return 1.0 - (abs(v - g) / ((abs(v) + abs(g)) or 1.0))

# ---- family: token overlap (12)
@metric("token")
def tok_prec(c):   return c.best(lambda a, at, g, gt: _prf(at, gt)[0])
@metric("token")
def tok_rec(c):    return c.best(lambda a, at, g, gt: _prf(at, gt)[1])
@metric("token")
def tok_f1(c):     return c.best(lambda a, at, g, gt: _prf(at, gt)[2])
@metric("token")
def tok_f0p5(c):   return c.best(lambda a, at, g, gt: _prf(at, gt, 0.5)[2])
@metric("token")
def tok_f2(c):     return c.best(lambda a, at, g, gt: _prf(at, gt, 2.0)[2])
@metric("token")
def bigram_prec(c): return c.best(lambda a, at, g, gt: _prf(_ngrams(at, 2), _ngrams(gt, 2))[0] if len(at) > 1 and len(gt) > 1 else float(at == gt))
@metric("token")
def bigram_rec(c):  return c.best(lambda a, at, g, gt: _prf(_ngrams(at, 2), _ngrams(gt, 2))[1] if len(at) > 1 and len(gt) > 1 else float(at == gt))
@metric("token")
def bigram_f1(c):   return c.best(lambda a, at, g, gt: _prf(_ngrams(at, 2), _ngrams(gt, 2))[2] if len(at) > 1 and len(gt) > 1 else float(at == gt))
@metric("token")
def trigram_f1(c):  return c.best(lambda a, at, g, gt: _prf(_ngrams(at, 3), _ngrams(gt, 3))[2] if len(at) > 2 and len(gt) > 2 else float(at == gt))
@metric("token")
def stem_f1(c):     return c.best(lambda a, at, g, gt: _prf([_stem(t) for t in at], [_stem(t) for t in gt])[2])
@metric("token")
def content_f1(c):  return c.best(lambda a, at, g, gt: _prf([t for t in at if t not in _STOP], [t for t in gt if t not in _STOP])[2])
@metric("token")
def content_rec(c): return c.best(lambda a, at, g, gt: _prf([t for t in at if t not in _STOP], [t for t in gt if t not in _STOP])[1])

# ---- family: character-level (9)
@metric("char")
def lev_sim(c):       return c.best(lambda a, at, g, gt: float(Levenshtein.normalized_similarity(a, g)))
@metric("char")
def damerau_sim(c):   return c.best(lambda a, at, g, gt: float(DamerauLevenshtein.normalized_similarity(a, g)))
@metric("char")
def jaro_sim(c):      return c.best(lambda a, at, g, gt: float(Jaro.similarity(a, g)))
@metric("char")
def jaro_winkler(c):  return c.best(lambda a, at, g, gt: float(JaroWinkler.similarity(a, g)))
@metric("char")
def lcs_substr_ratio(c):
    def f(a, at, g, gt):
        if not a or not g:
            return float(a == g)
        best = 0
        for i in range(len(a)):
            for j in range(len(g)):
                k = 0
                while i + k < len(a) and j + k < len(g) and a[i + k] == g[j + k]:
                    k += 1
                best = max(best, k)
        return best / max(len(a), len(g))
    return c.best(f) if len(c.ans_norm) < 300 else lev_sim(c)
@metric("char")
def chrf2(c):  return c.best(lambda a, at, g, gt: _chrf(a, g, 2))
@metric("char")
def chrf3(c):  return c.best(lambda a, at, g, gt: _chrf(a, g, 3))
@metric("char")
def chrf4(c):  return c.best(lambda a, at, g, gt: _chrf(a, g, 4))
@metric("char")
def prefix_ratio(c):
    def f(a, at, g, gt):
        n = 0
        while n < min(len(a), len(g)) and a[n] == g[n]:
            n += 1
        return n / max(len(g), 1)
    return c.best(f)

# ---- family: sequence / MT-style (10)
@metric("seq")
def rouge1(c):  return c.best(lambda a, at, g, gt: _prf(at, gt)[2])
@metric("seq")
def rouge2(c):  return c.best(lambda a, at, g, gt: _prf(_ngrams(at, 2), _ngrams(gt, 2))[2] if len(at) > 1 and len(gt) > 1 else float(at == gt))
@metric("seq")
def rouge_l(c):
    def f(a, at, g, gt):
        if not at or not gt:
            return float(at == gt)
        l = _lcs(at, gt); return _f(l / len(at), l / len(gt)) if l else 0.0
    return c.best(f)
@metric("seq")
def rouge_l_recall(c):
    return c.best(lambda a, at, g, gt: (_lcs(at, gt) / len(gt)) if at and gt else float(at == gt))
@metric("seq")
def bleu1(c):  return c.best(lambda a, at, g, gt: _bleu(at, gt, 1))
@metric("seq")
def bleu2(c):  return c.best(lambda a, at, g, gt: _bleu(at, gt, 2))
@metric("seq")
def bleu4(c):  return c.best(lambda a, at, g, gt: _bleu(at, gt, 4))
@metric("seq")
def meteor_lite(c):
    def f(a, at, g, gt):
        p, r, _ = _prf([_stem(t) for t in at], [_stem(t) for t in gt])
        if p + r == 0:
            return 0.0
        fm = 10 * p * r / (r + 9 * p)
        chunks = max(1, len(at) - _lcs(at, gt) + 1)
        return fm * (1 - 0.5 * (chunks / max(len(at), 1)) ** 3)
    return c.best(f)
@metric("seq")
def ter_score(c):
    return c.best(lambda a, at, g, gt: 1.0 - min(1.0, Levenshtein.distance(at, gt) / max(len(gt), 1)))
@metric("seq")
def wer_score(c):
    return c.best(lambda a, at, g, gt: 1.0 - min(1.0, Levenshtein.distance(" ".join(at), " ".join(gt)) / max(len(" ".join(gt)), 1)))

# ---- family: set / containment (7)
@metric("set")
def jaccard(c):    return c.best(lambda a, at, g, gt: len(set(at) & set(gt)) / len(set(at) | set(gt)) if (at or gt) else 1.0)
@metric("set")
def dice(c):       return c.best(lambda a, at, g, gt: 2 * len(set(at) & set(gt)) / (len(set(at)) + len(set(gt))) if (at or gt) else 1.0)
@metric("set")
def overlap_coef(c): return c.best(lambda a, at, g, gt: len(set(at) & set(gt)) / min(len(set(at)), len(set(gt))) if at and gt else float(at == gt))
@metric("set")
def gold_in_pred(c):  return float(any(g and g in c.ans_norm for g in c.golds_norm))
@metric("set")
def pred_in_gold(c):  return float(bool(c.ans_norm) and any(c.ans_norm in g for g in c.golds_norm))
@metric("set")
def number_set_jaccard(c):
    p = {round(n.value, 6) for n in c.pred_nums}
    return max((len(p & {round(n.value, 6) for n in gs}) / len(p | {round(n.value, 6) for n in gs}) if (p or gs) else 1.0) for gs in c.gold_nums)
@metric("set")
def entity_set_jaccard(c):
    def ents(s):
        return {t for t in re.findall(r"\b[A-Z][a-zA-Z]+\b", s)}
    p = ents(c.ans)
    return max((len(p & ents(g)) / len(p | ents(g)) if (p or ents(g)) else 1.0) for g in c.golds)

# ---- family: semantic (8, optional)
_EMB = {"loaded": False, "models": {}}


def _embed_sim(c: Ctx, model_name: str) -> float:
    if not _EMB["loaded"]:
        _EMB["loaded"] = True
        try:
            from sentence_transformers import SentenceTransformer  # noqa
            _EMB["ok"] = True
        except Exception:
            _EMB["ok"] = False
    if not _EMB.get("ok"):
        return 0.0
    from sentence_transformers import SentenceTransformer
    if model_name not in _EMB["models"]:
        _EMB["models"][model_name] = SentenceTransformer(model_name)
    m = _EMB["models"][model_name]
    v = m.encode([c.ans] + c.golds, normalize_embeddings=True)
    return float(max(np.dot(v[0], v[i]) for i in range(1, len(v))))
for _mn, _nm in [("sentence-transformers/all-MiniLM-L6-v2", "emb_cos_minilm"), ("BAAI/bge-small-en-v1.5", "emb_cos_bge")]:
    _fn = (lambda mn: (lambda c: _embed_sim(c, mn)))(_mn); _fn.__name__ = _nm; metric("semantic")(_fn)
@metric("semantic")
def emb_cos_minilm_thresh(c): return float(_embed_sim(c, "sentence-transformers/all-MiniLM-L6-v2") >= 0.8)
@metric("semantic")
def emb_cos_bge_thresh(c):    return float(_embed_sim(c, "BAAI/bge-small-en-v1.5") >= 0.8)
@metric("semantic")
def emb_question_free_placeholder(c): return 0.0     # reserved: question-conditioned relevance (needs question in ctx)
@metric("semantic")
def nli_gold_entails_pred(c): return 0.0             # reserved: NLI model (not shipped)
@metric("semantic")
def nli_pred_entails_gold(c): return 0.0             # reserved
@metric("semantic")
def bertscore_f_placeholder(c): return 0.0           # reserved: BERTScore (not shipped)

# ---- family: structure & format (7)
@metric("structure")
def type_agree(c):
    at = detect_answer_type(c.ans) if c.ans else None
    return float(at == c.atype)
@metric("structure")
def final_tag_present(c):     return float(bool(re.search(r"<FINAL_ANSWER>|FINAL ANSWER\s*:", c.pred_raw, re.I)))
@metric("structure")
def single_candidate(c):      return float(not _is_hedged(c))
@metric("structure")
def list_length_match(c):     return _best_parts(c, lambda p, g: float(len(p) == len(g)))
@metric("structure")
def unit_word_match(c):
    def units(s):
        return set(re.findall(r"\b(million|billion|thousand|trillion|percent|dollars?|usd|years?|months?|days?)\b", s.lower()))
    return float(any(units(c.ans) == units(g) for g in c.golds))
@metric("structure")
def percent_sign_agree(c):    return float(any(("%" in c.ans) == ("%" in g) for g in c.golds))
@metric("structure")
def currency_symbol_agree(c): return float(any(bool(re.search(r"[$€£]", c.ans)) == bool(re.search(r"[$€£]", g)) for g in c.golds))

# ---- family: length / verbosity (5)
@metric("length")
def length_ratio_score(c):
    g = max((len(t) for t in c.golds_toks), default=0); p = len(c.ans_toks)
    return 0.0 if not g and p else (1.0 if not g else min(p, g) / max(p, g))
@metric("length")
def brevity_penalty(c):
    g = max((len(t) for t in c.golds_toks), default=0); p = len(c.ans_toks)
    return 1.0 if p >= g else math.exp(1 - g / max(p, 1))
@metric("length")
def not_too_long(c):
    g = max((len(t) for t in c.golds_toks), default=1); return float(len(c.ans_toks) <= 2 * g + 2)
@metric("length")
def extra_token_score(c):
    def f(a, at, g, gt):
        extra = len(at) - sum((Counter(at) & Counter(gt)).values()); return max(0.0, 1.0 - extra / max(len(at), 1))
    return c.best(f)
@metric("length")
def not_abstaining(c):        return float(not _ABSTAIN.search(c.ans) and bool(c.ans.strip()))

# ---- family: commitment / consistency (4)
@metric("commit")
def hedge_free(c):            return float(not _is_hedged(c))
@metric("commit")
def number_count_agree(c):    return float(any(len([n for n in c.pred_nums if not n.is_year_like]) == len([n for n in gs if not n.is_year_like]) for gs in c.gold_nums))
@metric("commit")
def first_last_number_agree(c):
    nums = [n for n in c.pred_nums if not n.is_year_like]
    return 1.0 if len(nums) < 2 else float(abs(nums[0].value - nums[-1].value) <= 1e-6 * max(1, abs(nums[-1].value)) or _rel_err(nums[0], nums[-1]) <= 0.01)
@metric("commit")
def reasoning_final_consistent(c):
    """the final number also appears in the reasoning text (not invented at the last line)"""
    pp = _primary_pair(c)
    if pp is None:
        return 1.0
    body = c.pred_raw[: max(0, len(c.pred_raw) - len(c.ans))]
    return float(any(abs(n.value - pp[0].value) <= 1e-6 * max(1, abs(pp[0].value)) for n in extract_numbers(body)) or not body.strip())

# ---- family: task-specific (7)
@metric("task")
def bool_label_agree(c):
    b = normalize_boolean(c.ans); g = normalize_boolean(c.golds[0]); return float(b is not None and b == g) if g else em_norm(c)
@metric("task")
def year_aware_em(c):
    py, gy = set(_YEAR_RE.findall(c.ans)), set(y for g in c.golds for y in _YEAR_RE.findall(g))
    return float(py == gy) if gy else em_norm(c)
@metric("task")
def attribute_match_score(c):
    """for record-pair tasks: agreement of the boolean label weighted by confidence words"""
    b = normalize_boolean(c.ans); g = normalize_boolean(c.golds[0])
    if g is None:
        return em_norm(c)
    conf = 0.5 if re.search(r"\b(probably|likely|possibly|might)\b", c.ans.lower()) else 1.0
    return float(b == g) * conf
@metric("task")
def program_exec_match(c):    return 0.0 if not c.program else num_tol_1(c)   # placeholder: exec of program not shipped
@metric("task")
def sql_result_match_placeholder(c): return 0.0
@metric("task")
def numeric_or_em(c):         return num_tol_1(c) if c.atype == AnswerType.NUMERIC else em_norm(c)
@metric("task")
def native_style_metric(c):
    """the native metric family by type: num_tol_1 / em / rouge_l"""
    return {AnswerType.NUMERIC: num_tol_1, AnswerType.BOOLEAN: bool_label_agree, AnswerType.TEXT: em_norm, AnswerType.FREEFORM: rouge_l}[c.atype](c)


METRIC_NAMES: List[str] = list(METRICS.keys())
FAMILIES: Dict[str, List[str]] = {}
for _n, (_fam, _) in METRICS.items():
    FAMILIES.setdefault(_fam, []).append(_n)
assert len(METRIC_NAMES) == 100, len(METRIC_NAMES)

SEMANTIC = FAMILIES["semantic"]


def compute_all(pred, gold, aliases=None, atype=None, gold_list=None, program=None, *, semantic: bool = False) -> np.ndarray:
    c = make_ctx(pred, gold, aliases, atype, gold_list, program)
    out = np.zeros(len(METRIC_NAMES), dtype=np.float32)
    for i, n in enumerate(METRIC_NAMES):
        if not semantic and n in SEMANTIC:
            continue
        try:
            out[i] = min(1.0, max(0.0, float(METRICS[n][1](c))))
        except Exception:
            out[i] = 0.0
    return out
