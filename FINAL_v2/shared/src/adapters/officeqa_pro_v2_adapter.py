"""OfficeQA Pro v2 (Databricks, 2026; Hugging Face gated dataset databricks/officeqa-pro-v2; data CC-BY-SA 4.0,
code Apache-2.0).  90 questions over U.S. Treasury Combined Statements / receipts documents (1793-2024).
Local files (HF_TOKEN needed for the download): data/raw/officeqa_pro_v2/officeqa_pro_v2.csv and the parsed
JSONs of the 249 referenced documents under data/raw/officeqa_pro_v2/parsed_corpus/jsons/<slug>.json
(snapshot_download with allow_patterns = the referenced filenames only; ~430 MB instead of 794 MB).

Framing: open-book with oracle retrieval - context = text of the pages listed in source_docs
(pdf_page_number is 1-based; JSON page_id is 0-based), table HTML flattened to pipe rows, capped at
6,000 chars shared evenly across the listed pages.  Gold: bare numbers / currency / percent are numeric
(bare number added as alias); bracketed '[a, b]' answers become gold_list.  All 90 items are kept."""
from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)
RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "officeqa_pro_v2"
HF_REPO = "databricks/officeqa-pro-v2"
MAX_CTX, MIN_PAGE_SHARE = 6000, 300
DOC_RE = re.compile(r"corpus_file=(?P<file>[^|;]+?)\.txt\s*\|\s*pdf_page_number=(?P<page>\d+|N/A)")
DOC_RE_ALT = re.compile(r"(?P<file>(?:combined_statement|govinfo_receipts)__[\w.\-]+?)(?:\.txt)?\s+page\s+(?P<page>\d+)")   # a few rows: '<slug> page N'
SKIP_TYPES = {"page_header", "page_footer", "page_number"}


def _html_table_to_text(html: str) -> str:
    rows = []
    for tr in re.findall(r"<tr.*?</tr>", html, flags=re.S | re.I):
        cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows) if rows else re.sub(r"<.*?>", " ", html)


def _page_text(doc: dict, page_id: int) -> str:
    out = []
    for e in doc.get("elements", []):
        if e.get("type") in SKIP_TYPES or not any(b.get("page_id") == page_id for b in e.get("bbox", [])):
            continue
        c = e.get("content") or ""
        out.append(_html_table_to_text(c) if e.get("type") == "table" or "<table" in c[:20] else c)
    return "\n".join(x for x in out if x.strip()).strip()


def _allocate(chunks: List[Tuple[str, str]], budget: int) -> str:
    """Give every (label, text) an equal share; unused share is redistributed once."""
    if not chunks:
        return ""
    n = len(chunks)
    budget -= sum(len(label) + 8 for label, _ in chunks)          # headers and separators count toward the cap
    share = max(MIN_PAGE_SHARE, budget // n)
    taken = [min(len(t), share) for _, t in chunks]
    spare = budget - sum(taken)
    for i, (_, t) in enumerate(chunks):
        if spare <= 0:
            break
        extra = min(len(t) - taken[i], spare)
        if extra > 0:
            taken[i] += extra
            spare -= extra
    parts = []
    for (label, t), k in zip(chunks, taken):
        body = t if k >= len(t) else t[:k].rstrip() + " ..."
        parts.append(f"### {label}\n{body}")
    out = "\n\n".join(parts)
    return out if len(out) <= MAX_CTX else out[:MAX_CTX - 4].rstrip() + " ..."


class OfficeQAProV2Adapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = Path(config.get("dataset_url") or RAW)
        csv_path, json_dir = root / "officeqa_pro_v2.csv", root / "parsed_corpus" / "jsons"
        if not csv_path.exists():
            raise FileNotFoundError(f"OfficeQA Pro v2 questions not found at {csv_path}; hf_hub_download('{HF_REPO}', 'officeqa_pro_v2.csv', repo_type='dataset', token=HF_TOKEN) (gated).")
        if not json_dir.is_dir():
            raise FileNotFoundError(f"OfficeQA Pro v2 parsed corpus not found at {json_dir}; snapshot_download('{HF_REPO}', allow_patterns=[parsed_corpus/jsons/<referenced>.json ...]).")
        docs: Dict[str, dict] = {}
        items: List[QuestionItem] = []
        with open(csv_path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            src = r.get("source_docs") or ""
            refs = [(m.group("file").strip(), m.group("page")) for m in DOC_RE.finditer(src)]
            if not refs:
                refs = [(m.group("file").strip(), m.group("page")) for m in DOC_RE_ALT.finditer(src)]
            files = [s.strip().removesuffix(".txt") for s in (r.get("source_files") or "").split(";") if s.strip()]
            for fslug in files:                      # files listed without a page entry
                if fslug not in {a for a, _ in refs}:
                    refs.append((fslug, "N/A"))
            seen, chunks, missing = set(), [], []
            for slug, page in refs:
                if (slug, page) in seen:
                    continue
                seen.add((slug, page))
                if slug not in docs:
                    p = json_dir / f"{slug}.json"
                    docs[slug] = json.loads(p.read_text(encoding="utf-8")).get("document", {}) if p.exists() else None
                doc = docs[slug]
                if doc is None:
                    missing.append(slug)
                    continue
                if page == "N/A":
                    txt, label = "", f"{slug} (first pages)"
                else:
                    pid = int(page) - 1
                    txt = _page_text(doc, pid) or _page_text(doc, int(page))
                    label = f"{slug}, page {page}"
                if not txt:                                   # no page given / empty page: first pages with text
                    found = []
                    for i in range(len(doc.get("pages", []))):
                        t = _page_text(doc, i)
                        if t:
                            found.append(t)
                        if len(found) >= 2:
                            break
                    txt = "\n".join(found).strip()
                if txt:
                    chunks.append((label, txt))
            ctx = _allocate(chunks, MAX_CTX)
            ans = (r.get("answer") or "").strip()
            gold_list, aliases, answer_type, native = None, [], "numeric", "num_tol"
            if ans.startswith("[") and ans.endswith("]"):
                parts = [p.strip() for p in ans[1:-1].split(",") if p.strip()]
                if len(parts) > 1:
                    gold_list, answer_type, native, aliases = parts, None, "em", [ans, ", ".join(parts)]
                    gold = " | ".join(parts)
                else:
                    gold = parts[0] if parts else ans
            else:
                gold = ans
                bare = re.sub(r"[,$%\s]", "", ans)
                if bare != ans:
                    aliases = [bare]
            items.append(QuestionItem(
                uid=f"officeqa_pro_v2_{r.get('uid')}", question=f"{(r.get('question') or '').strip()}\nGive only the final answer, no explanation.",
                ground_truth=gold, difficulty="all", context=ctx, dataset_name="officeqa_pro_v2", data_type="document",
                gold_list=gold_list, gold_aliases=aliases, answer_type=answer_type, native_metric=native,
                extra={"uid": r.get("uid"), "source_files": files, "source_docs": r.get("source_docs"), "n_source_docs": len(refs),
                       "n_pages_in_context": len(chunks), "missing_docs": missing, "context_chars": len(ctx),
                       "license": "CC-BY-SA 4.0 (data); Apache-2.0 (code)", "source": f"hf:{HF_REPO} (gated)"}))
        return items
