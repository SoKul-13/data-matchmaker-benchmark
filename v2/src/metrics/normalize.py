"""
Normalisation utilities shared by every component metric.

Design goals
------------
* Deterministic and dependency-free (regex only).
* Scale / unit aware number parsing: "$1,577.00", "(12.6)", "14.5%", "1.2 billion".
* A single canonical text normaliser (SQuAD-style) so that token-level metrics
  are comparable across datasets.
"""
from __future__ import annotations

import re
import string
import unicodedata
from dataclasses import dataclass
from typing import List, Optional

# --------------------------------------------------------------------------- #
# Final-answer extraction
# --------------------------------------------------------------------------- #

_TAG_RE = re.compile(r"<FINAL_ANSWER>\s*(.*?)\s*</FINAL_ANSWER>", re.DOTALL | re.IGNORECASE)
_LINE_RE = re.compile(
    r"(?:^|\n)\s*(?:\*\*)?\s*(?:final\s+answer|answer|final)\s*(?:\*\*)?\s*[:=]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_BOXED_RE = re.compile(r"\\boxed\{([^{}]*)\}")
# generic lead-in / trailing templates that wrap a short answer
_LEADIN_RE = re.compile(
    r"^(?:(?:based on|according to|from|using|after)[^,:]{0,80}[,:]\s*)?"
    r"(?:(?:therefore|thus|hence|so|overall|in conclusion|finally)[,\s]+)?"
    r"(?:(?:the|my|our)\s+)?(?:final\s+|correct\s+|best\s+)?(?:answer|result|value|total|figure)\s*(?:is|was|would be|should be|=|:)\s*",
    re.IGNORECASE,
)
_TRAIL_RE = re.compile(
    r"\s*(?:is|was)\s+(?:the\s+)?(?:correct\s+|final\s+)?(?:answer|result|value)(?:\s+(?:according to|based on|from)\b.*)?\.?$",
    re.IGNORECASE,
)


def strip_templates(ans: str) -> str:
    """Remove generic answer scaffolding ('the answer is X.', 'X is the correct answer')."""
    a = ans.strip()
    a2 = _LEADIN_RE.sub("", a, count=1)
    a2 = _TRAIL_RE.sub("", a2, count=1)
    a2 = a2.strip().rstrip(".").strip()
    return a2 if a2 else a


def extract_final_answer(text: Optional[str]) -> str:
    """Return the most answer-like span of a model response.

    Priority: <FINAL_ANSWER> tag > last 'FINAL ANSWER:'/'Answer:' line > \\boxed{} >
    last non-empty line (if the response is multi-line and short) > whole text.
    Never raises; empty input returns "".
    """
    if not text:
        return ""
    text = str(text).strip()
    m = _TAG_RE.findall(text)
    if m:
        cand = m[-1].strip()
        if cand:
            return strip_templates(cand)
    m = _LINE_RE.findall(text)
    if m:
        cand = m[-1].strip().strip("*").strip()
        if cand:
            return strip_templates(cand)
    m = _BOXED_RE.findall(text)
    if m:
        return m[-1].strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) > 1 and len(lines[-1]) <= 200:
        return strip_templates(lines[-1])
    return strip_templates(text) if len(text) <= 400 else text


# --------------------------------------------------------------------------- #
# Number parsing
# --------------------------------------------------------------------------- #

_SCALE_WORDS = {
    "thousand": 1e3, "thousands": 1e3, "k": 1e3,
    "million": 1e6, "millions": 1e6, "mm": 1e6, "mn": 1e6, "m": 1e6,
    "billion": 1e9, "billions": 1e9, "bn": 1e9, "b": 1e9,
    "trillion": 1e12, "trillions": 1e12, "tn": 1e12, "t": 1e12,
}

_NUM_RE = re.compile(
    r"(?P<neg>(?<![\w.])[-\u2212\u2013])?\s*"
    r"(?P<paren>\()?\s*"
    r"(?P<cur>[$€£¥])?\s*"
    r"(?P<num>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)"
    r"\s*(?P<close>\))?"
    r"\s*(?P<pct>%|percent(?:age)?(?:\s+points?)?|pp\b)?"
    r"(?:\s*(?P<scale>thousands?|millions?|billions?|trillions?|\b[kKmMbBtT]\b|\bmm\b|\bmn\b|\bbn\b|\btn\b))?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedNumber:
    value: float          # raw numeric value as written (after sign)
    is_percent: bool      # "%", "percent", "pp"
    scale: float          # 1e6 for "million", 1.0 if none
    is_year_like: bool    # 4-digit integer in [1800, 2100] with no decimal / sign / scale
    span: tuple           # (start, end) in the source string

    @property
    def scaled(self) -> float:
        return self.value * self.scale

    def equivalents(self) -> List[float]:
        """Interpretations under unit / percent ambiguity.

        The list contains the raw value, the scaled value and (for percentage
        ambiguity) the value divided / multiplied by 100.  A prediction matches a
        gold number if ANY pair of interpretations is within tolerance.  This is
        deliberately lenient on unit conventions (e.g. FinQA gold '0.145' vs a
        model answering '14.5%') while remaining strict on the digits themselves.
        """
        eq = {self.value}
        if self.scale != 1.0:
            eq.add(self.scaled)
        if self.is_percent:
            eq.add(self.value / 100.0)
        else:
            eq.add(self.value * 100.0)
            eq.add(self.value / 100.0)
        return sorted(eq)


def extract_numbers(text: Optional[str]) -> List[ParsedNumber]:
    """Extract every number in *text* with sign, percent and scale annotations."""
    if not text:
        return []
    text = str(text).replace("\u2212", "-").replace("\u2013", "-")
    out: List[ParsedNumber] = []
    for m in _NUM_RE.finditer(text):
        num_txt = m.group("num").replace(",", "")
        try:
            val = float(num_txt)
        except ValueError:
            continue
        neg = bool(m.group("neg")) or (bool(m.group("paren")) and bool(m.group("close")))
        if neg:
            val = -val
        pct = bool(m.group("pct"))
        scale_txt = (m.group("scale") or "").lower()
        scale = _SCALE_WORDS.get(scale_txt, 1.0) if scale_txt else 1.0
        # A lone "m"/"b"/"k"/"t" letter is ambiguous; only accept it if it is followed
        # by end-of-string or punctuation (e.g. "$4.2b", "12k").
        if scale_txt in {"k", "m", "b", "t"}:
            end = m.end()
            if end < len(text) and text[end].isalpha():
                scale = 1.0
        year_like = (
            "." not in num_txt and "," not in m.group("num") and not neg and not pct
            and scale == 1.0 and 1800 <= val <= 2100 and len(num_txt) == 4
        )
        out.append(ParsedNumber(val, pct, scale, year_like, (m.start(), m.end())))
    return out


def canonical_number_string(val: float) -> str:
    """'1577.00' -> '1577', '14.50' -> '14.5', keeps up to 6 significant decimals."""
    if val == int(val) and abs(val) < 1e15:
        return str(int(val))
    s = f"{val:.6f}".rstrip("0").rstrip(".")
    return s


# --------------------------------------------------------------------------- #
# Text normalisation
# --------------------------------------------------------------------------- #

_ARTICLES = {"a", "an", "the"}
_PUNCT_TABLE = str.maketrans({c: " " for c in string.punctuation if c not in {".", "-", "%"}})
_MULTI_WS = re.compile(r"\s+")


def normalize_text(text: Optional[str], *, keep_percent: bool = False, drop_articles: bool = True) -> str:
    """SQuAD-style normalisation with number canonicalisation.

    Steps: unicode NFKC -> lowercase -> canonicalise numbers ("1,577.00" -> "1577",
    "(12.6)" -> "-12.6") -> strip currency symbols and punctuation -> drop articles
    -> collapse whitespace.  The percent sign is dropped unless keep_percent=True.
    """
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    s = s.replace("\u2212", "-").replace("\u2013", "-")
    # Canonicalise numbers in place (right-to-left so spans stay valid).
    nums = extract_numbers(s)
    for pn in reversed(nums):
        start, end = pn.span
        repl = canonical_number_string(pn.value)
        if pn.is_percent and keep_percent:
            repl += "%"
        # keep a trailing scale word (it is informative for token overlap)
        tail = s[start:end]
        mscale = re.search(r"(thousand|million|billion|trillion)s?\s*$", tail)
        if mscale:
            repl += " " + mscale.group(1)
        s = s[:start] + " " + repl + " " + s[end:]
    s = re.sub(r"[$€£¥]", " ", s)
    if not keep_percent:
        s = s.replace("%", " ")
    s = s.translate(_PUNCT_TABLE)
    # remove stray dots that are not part of a number and stray hyphens
    s = re.sub(r"(?<!\d)\.(?!\d)", " ", s)
    s = re.sub(r"(?<!\d)-(?!\d)", " ", s)
    toks = s.split()
    if drop_articles:
        toks = [t for t in toks if t not in _ARTICLES]
    return _MULTI_WS.sub(" ", " ".join(toks)).strip()


def tokens(text: Optional[str]) -> List[str]:
    return normalize_text(text).split()
