"""The 7-point grading scale, shared by every labelling script (sample, kit, forms, agreement).

Graders record a RATING: a whole number from 1 (wrong or no answer) to 7 (correct), Likert style, each point named and defined.
The scripts convert it afterwards to a utility on the 0-1 line: utility = (rating - 1) / 6, i.e. 1 -> 0.00, 4 -> 0.50, 7 -> 1.00.
Graders never type a 0-1 value; a recorded "1" always means the lowest point.
"""
from __future__ import annotations
import re

# (rating, utility it converts to (shown), short name, definition)
SCALE = [
    (7, "1.00", "Correct", "Same answer as the reference. Formatting, wording, order of a list and harmless extra words do not matter."),
    (6, "0.83", "Correct, cosmetic defect", "Right answer with a blemish that does not change the meaning: rounding within 1 %, a typo, 'about', a redundant qualifier."),
    (5, "0.67", "Mostly correct", "Right answer with a small part missing or slightly imprecise: a minor detail dropped, most but not all list items (none wrong), slightly under- or over-specified."),
    (4, "0.50", "Half correct", "About half of the required answer, or the right quantity in the wrong form (wrong unit or scale), or a right answer offered beside a wrong one."),
    (3, "0.33", "Mostly wrong, near miss", "Only a small part is right, or a near miss: a number 1-5 % off or a one-digit slip, under half of a list, main fact wrong but a relevant detail right."),
    (2, "0.17", "Wrong but related", "Answers the right question in the right form but the content is wrong: number more than 5 % off (within 10x) or wrong sign, neighbouring cell, confusable entity."),
    (1, "0.00", "Wrong or no answer", "A different value, name or label; the opposite yes/no; a refusal; 'cannot be determined' when a reference exists; no final answer."),
]
SHORT = {7: "Same answer as the reference", 6: "Right, with a blemish that changes nothing (rounding, typo)", 5: "Right, a small part missing or imprecise",
         4: "About half right, or right value in the wrong unit or scale", 3: "Little is right, or a near miss (1-5 % off)",
         2: "Right kind of answer, wrong content", 1: "Wrong, refused or empty"}   # one line per rating, for the legend strip
RATINGS = [s[0] for s in SCALE]                           # 7 ... 1
LEVELS = [(r - 1) / 6 for r in RATINGS]                   # the utilities 1, 5/6, ..., 0
STEP = 1 / 6
ENTRIES = [f"{s[0]} {s[2]}" for s in SCALE]               # "7 Correct", ..., "1 Wrong or no answer" (spreadsheet drop-down)
FORM_CHOICES = ENTRIES[::-1]                              # the forms' grid columns, left to right 1 ... 7
_RE = re.compile(r"^([1-7])(?:[.,]0+)?(?:\D|$)")


def rating(v) -> float:
    """Parse a recorded rating ('6', '6 Correct, cosmetic defect', 6.0) to 1..7; blank or anything else -> nan."""
    if v is None: return float("nan")
    m = _RE.match(str(v).strip())
    return float(m.group(1)) if m else float("nan")


def to_utility(v) -> float:
    """Recorded rating -> utility on the 0-1 line; blank / off-scale -> nan."""
    r = rating(v)
    return (r - 1) / 6 if r == r else float("nan")


def to_rating(u: float) -> int:
    """Utility (exact level or a mean) -> the nearest rating."""
    return int(round(u * 6)) + 1
