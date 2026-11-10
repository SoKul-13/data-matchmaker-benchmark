"""Render labelling rows as images: a card per row (key fields as a two-column table, the data table as a real grid with borders,
the context as wrapped text) and the 7-point scale as a table.  Used by 06_render_row_images.py (Google Forms route) and by
04_make_labeller_handoff.py (form sample, scale image in the kit).  Images are 1,480 px wide; Forms shows them at about half that.
"""
from __future__ import annotations
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from label_scale import SCALE, SHORT

W, PAD, FS = 1480, 28, 26
REG = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
BOLD = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
INK, MUTED, LINE, HEAD, ZEBRA, HILITE, ACCENT = "#1f2328", "#57606a", "#c9d1d9", "#e8eef6", "#f6f8fa", "#fff4cc", "#5b3fb5"
_cache = {}


def font(bold=False, size=FS):
    k = (bold, size)
    if k not in _cache:
        f = None
        for path in (BOLD if bold else REG):
            if Path(path).exists():
                try: f = ImageFont.truetype(path, size); break
                except OSError: pass
        _cache[k] = f or ImageFont.load_default()
    return _cache[k]


def wrap(text, fnt, maxw):
    """Word-wrap to a pixel width; words longer than the width are split."""
    out = []
    for para in str(text).split("\n"):
        if not para.strip(): out.append(""); continue
        cur = ""
        for word in re.findall(r"\S+\s*", para):
            if fnt.getlength((cur + word).rstrip()) <= maxw: cur += word; continue
            if cur: out.append(cur.rstrip()); cur = ""
            while fnt.getlength(word.rstrip()) > maxw:  # a single long token
                k = len(word)
                while k > 1 and fnt.getlength(word[:k]) > maxw: k -= 1
                out.append(word[:k]); word = word[k:]
            cur = word
        if cur.strip(): out.append(cur.rstrip())
    return out or [""]


class Text:
    def __init__(self, text, bold=False, size=FS, color=INK, gap=10):
        self.f = font(bold, size); self.lines = wrap(text, self.f, W - 2 * PAD); self.lh = int(size * 1.38); self.color = color; self.gap = gap
    def height(self): return self.lh * len(self.lines) + self.gap
    def draw(self, d, y):
        for i, ln in enumerate(self.lines): d.text((PAD, y + i * self.lh), ln, fill=self.color, font=self.f)


class Grid:
    """A table with borders.  rows = list of lists of strings; widths in px; header = first row shaded; fills = optional row colours."""
    def __init__(self, rows, widths, header=True, size=FS, bold_first_col=False, fills=None, cellpad=10):
        self.rows, self.widths, self.header, self.size, self.cp, self.bfc, self.fills = rows, widths, header, size, cellpad, bold_first_col, fills or {}
        self.lh = int(size * 1.34); self.cells = []; self.heights = []
        for i, r in enumerate(rows):
            line = []
            for j, c in enumerate(r):
                f = font(bold=(header and i == 0) or (bold_first_col and j == 0), size=size)
                line.append((f, wrap(c, f, widths[j] - 2 * cellpad)))
            self.cells.append(line); self.heights.append(max(len(w) for _, w in line) * self.lh + 2 * cellpad)
    def height(self): return sum(self.heights) + 16
    def draw(self, d, y):
        x0 = PAD
        for i, line in enumerate(self.cells):
            x = x0; h = self.heights[i]
            fill = self.fills.get(i) or (HEAD if (self.header and i == 0) else (ZEBRA if i % 2 == 0 else "white"))
            for j, (f, lines) in enumerate(line):
                d.rectangle([x, y, x + self.widths[j], y + h], fill=fill, outline=LINE, width=2)
                for k, ln in enumerate(lines): d.text((x + self.cp, y + self.cp + k * self.lh), ln, fill=INK, font=f)
                x += self.widths[j]
            y += h


def parse_table(text):
    """Pipe-delimited text -> (title lines, header, rows, trailing lines).  Lines without a pipe before the header are titles."""
    titles, header, rows, tail = [], None, [], []
    for ln in str(text).split("\n"):
        t = ln.strip()
        if not t: continue
        if re.fullmatch(r"[-=+| :]+", t) and "-" in t: continue
        if "|" not in t:
            (tail if header else titles).append(t); continue
        cells = [c.strip() for c in t.strip("|").split("|")]
        if header is None: header = cells
        else: rows.append(cells)
    return titles, header, rows, tail


def table_blocks(text):
    titles, header, rows, tail = parse_table(text)
    blocks = [Text(t, bold=True) for t in titles[:4]]
    if header is None: return blocks + [Text("\n".join(tail))] if tail else blocks
    n = max(len(header), max((len(r) for r in rows), default=0))
    header = header + [""] * (n - len(header)); rows = [r + [""] * (n - len(r)) for r in rows]
    avail = W - 2 * PAD
    for size in (FS, 23, 20):
        f, fb = font(False, size), font(True, size)
        nat = [min(max([fb.getlength(header[j])] + [f.getlength(r[j]) for r in rows]) + 24, 520) for j in range(n)]
        nat = [max(w, 70) for w in nat]
        if sum(nat) > avail:  # shrink the widest columns until the table fits, never below 120 px
            cap = max(nat)
            while sum(min(w, cap) for w in nat) > avail and cap > 120: cap -= 10
            nat = [min(w, cap) for w in nat]
        if sum(nat) <= avail:
            extra = (avail - sum(nat)) if sum(nat) > 0.75 * avail else 0  # nearly full width: stretch to the edge
            widths = [int(w + extra * w / sum(nat)) for w in nat]
            return blocks + [Grid([header] + rows, widths, header=True, size=size)] + ([Text("\n".join(tail), color=MUTED)] if tail else [])
    # too many columns for one grid: several grids side by side in reading order, each repeating the first column as the row key
    size = 22; f, fb = font(False, size), font(True, size)
    nat = [max(min(max([fb.getlength(header[j])] + [f.getlength(r[j]) for r in rows]) + 22, 300), 70) for j in range(n)]
    key = min(nat[0], 260); chunks, cur, used = [], [], key
    for j in range(1, n):
        if cur and used + nat[j] > avail: chunks.append(cur); cur, used = [], key
        cur.append(j); used += nat[j]
    if cur: chunks.append(cur)
    for ci, cols in enumerate(chunks, 1):
        blocks.append(Text(f"Columns {cols[0] + 1} to {cols[-1] + 1} of {n} (part {ci} of {len(chunks)}; the first column is repeated)", bold=True, size=20, color=MUTED, gap=4))
        blocks.append(Grid([[header[0]] + [header[j] for j in cols]] + [[r[0]] + [r[j] for j in cols] for r in rows], [key] + [nat[j] for j in cols], header=True, size=size, bold_first_col=True, cellpad=7))
    if tail: blocks.append(Text("\n".join(tail), color=MUTED))
    return blocks


KV = re.compile(r"^([^:\n]{1,48}):\s?(.*)$")


def _sections(text):
    """Split a context into (heading, lines) sections on lines that start with '#'."""
    secs, head, buf = [], None, []
    for ln in str(text).split("\n"):
        if ln.startswith("#"):
            if head is not None or any(x.strip() for x in buf): secs.append((head, buf))
            head, buf = ln.lstrip("# ").strip(), []
        else: buf.append(ln)
    if head is not None or any(x.strip() for x in buf): secs.append((head, buf))
    return secs


def _kv(lines):
    """[(key, value)] when every non-empty line reads 'key: value', else None."""
    out = []
    for ln in lines:
        if not ln.strip(): continue
        m = KV.match(ln.strip())
        if not m: return None
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out if len(out) >= 1 else None


def context_blocks(text):
    """Two records side by side when the context is a pair of 'key: value' records (entity matching); a key/value table per section
    when a section is 'key: value' lines; wrapped text otherwise."""
    secs = _sections(text); avail = W - 2 * PAD; blocks = []
    kvs = [(h, _kv(ls)) for h, ls in secs]
    if len(secs) == 2 and all(k for _, k in kvs) and all(h for h, _ in kvs):
        (ha, a), (hb, b) = kvs; keys = [k for k, _ in a] + [k for k, _ in b if k not in dict(a)]
        da, db = dict(a), dict(b); half = (avail - 260) // 2
        rows = [["field", ha, hb]] + [[k, da.get(k, ""), db.get(k, "")] for k in keys]
        return [Grid(rows, [260, half, avail - 260 - half], header=True, size=24, bold_first_col=True)]
    for (h, ls), (_, kv) in zip(secs, kvs):
        if h: blocks.append(Text(h, bold=True, gap=4))
        if kv and len(kv) >= 2: blocks.append(Grid([[k, v] for k, v in kv], [360, avail - 360], header=False, size=24, bold_first_col=True, cellpad=7))
        elif any(x.strip() for x in ls): blocks.append(Text("\n".join(ls).strip("\n"), size=24))
    return blocks


def compose(blocks, path: Path | None = None):
    h = sum(b.height() for b in blocks) + 2 * PAD
    img = Image.new("RGB", (W, max(h, 80)), "white"); d = ImageDraw.Draw(img); y = PAD
    for b in blocks: b.draw(d, y); y += b.height()
    if path is not None: img.quantize(64).save(path, optimize=True)
    return img


def row_card(r, path: Path | None = None):
    """r: a row of the blind sheet (dict-like).  The card shows everything needed to grade except the full reply."""
    kv = [["Task", r["task_family"]], ["Source", r["dataset_description"]], ["Answer type", r["answer_type"]]]
    if str(r.get("choices") or "").strip(): kv.append(["Choices", r["choices"]])
    kv.append(["Question", r["question"]]); i_ref = len(kv); kv.append(["Reference answer", r["gold_answer"]])
    if str(r.get("accepted_alternatives") or "").strip(): kv.append(["Also accepted", r["accepted_alternatives"]])
    if str(r.get("gold_is_a_list") or "").strip(): kv.append(["Reference is a list", "every item is required"])
    i_ans = len(kv); kv.append(["System's final answer (grade this)", str(r["model_final_answer"]) or "(no final answer)"])
    blocks = [Text(str(r["row_id"]), bold=True, size=34, color=ACCENT, gap=14),
              Grid(kv, [330, W - 2 * PAD - 330], header=False, bold_first_col=True, fills={i_ref: "#e6f4ea", i_ans: HILITE})]
    if str(r.get("table") or "").strip(): blocks += [Text("Table shown to the system", bold=True, color=MUTED, gap=6)] + table_blocks(r["table"])
    if str(r.get("context") or "").strip(): blocks += [Text("Context shown to the system", bold=True, color=MUTED, gap=6)] + context_blocks(r["context"])
    return compose(blocks, path)


def scale_image(path: Path | None = None):
    rows = [["Rating", "Name", "When to use it", "Later"]] + [[str(p), name, d, u] for p, u, name, d in SCALE]
    fills = {1: "#e6f4ea", 4: HILITE, 7: "#fde8e8"}
    blocks = [Text("The scale: a rating from 1 to 7", bold=True, size=32, gap=12),
              Grid(rows, [110, 330, W - 2 * PAD - 540, 100], header=True, size=24, fills=fills),
              Text("Anchors: 7 = I would accept this as the reference answer; 4 = half of it is right; 1 = nothing is right. Between two neighbouring ratings, choose the lower. "
                   "Yes/no answers use only 7 or 1. You record the rating; the last column is the 0-1 value it is converted to afterwards. hedged = Yes when the final answer offers more than one candidate, a range, or will not commit.", size=23, color=MUTED)]
    return compose(blocks, path)


STRIP_COLORS = {1: "#f8d7d4", 2: "#fbe3d3", 3: "#fdefd2", 4: "#fff4cc", 5: "#eef3cf", 6: "#dff0d5", 7: "#cfe9d6"}


def scale_strip(path: Path | None = None):
    """The legend shown above every rating question: seven cells from 1 (left) to 7 (right), aligned with the form's 1-7 scale row."""
    cw = (W - 2 * PAD) // 7; fnum, fname, fdef = font(True, 44), font(True, 22), font(False, 20)
    cells = []
    for r in range(1, 8):
        name = next(s[2] for s in SCALE if s[0] == r)
        cells.append((r, wrap(name, fname, cw - 22), wrap(SHORT[r], fdef, cw - 22)))
    hn = max(len(c[1]) for c in cells) * 28; hd = max(len(c[2]) for c in cells) * 26; H = PAD + 58 + hn + 8 + hd + 18 + PAD
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    for i, (r, nm, df) in enumerate(cells):
        x = PAD + i * cw; d.rectangle([x, PAD, x + cw - 6, H - PAD], fill=STRIP_COLORS[r], outline=LINE, width=2)
        d.text((x + cw / 2 - fnum.getlength(str(r)) / 2 - 3, PAD + 6), str(r), fill=INK, font=fnum)
        for k, ln in enumerate(nm): d.text((x + 10, PAD + 58 + k * 28), ln, fill=INK, font=fname)
        for k, ln in enumerate(df): d.text((x + 10, PAD + 58 + hn + 8 + k * 26), ln, fill=MUTED, font=fdef)
    if path is not None: img.quantize(64).save(path, optimize=True)
    return img
