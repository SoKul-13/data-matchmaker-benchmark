"""FinTagging (TheFinAI; https://huggingface.co/collections/TheFinAI/fintagging) - FinCL subtask only:
link a numeric entity in a 10-K sentence or table snippet to its US-GAAP XBRL concept.
Source: Hugging Face `TheFinAI/FinCL-eval` (test parquet, 52,572 rows; columns context, category
[text|table], entity, entity_type, query, answer).

Item = the snippet with the number highlighted (<<...>>), the entity's XBRL data type, and ~10 candidate
concepts (true one + hard negatives sharing the leading CamelCase tokens, filled with concepts of the same
data type); answer = concept name (`us-gaap:Xyz`; the bare local name is an alias).
answer_type text, native_metric em.  Raw file: data/raw/fintagging/FinCL-eval_test.parquet.
"""
import logging
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import clip, ensure_file, hf_headers, hf_resolve, raw_dir

logger = logging.getLogger(__name__)
REPO = "TheFinAI/FinCL-eval"
QUESTION = ("Which US-GAAP XBRL concept should the highlighted number be tagged with? "
            "Answer with the exact concept name from the candidate list.")


def _camel(name: str) -> List[str]:
    local = name.split(":")[-1]
    return re.findall(r"[A-Z][a-z0-9]*|[A-Z]+(?![a-z])", local)


def _table_snippet(html: str, entity: str, budget: int = 1500) -> str:
    rows = re.split(r"</tr\s*>", html, flags=re.I)
    out_rows = []
    for r in rows:
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.split(r"<t[dh][^>]*>", r, flags=re.I)]
        cells = [c for c in cells if c and c not in ("$", ")", "%")]
        if cells:
            out_rows.append(" | ".join(cells))
    if not out_rows:
        return clip(re.sub(r"<[^>]+>", " ", html), budget)
    hit = next((i for i, r in enumerate(out_rows) if entity in r.replace(",", "")), None)
    header = out_rows[:2]
    if hit is None:
        body = out_rows[2:8]
    else:
        body = out_rows[max(2, hit - 3): hit + 3]
    return clip("\n".join(header + (["..."] if hit and hit > 5 else []) + body), budget)


def _highlight(text: str, entity: str) -> str:
    for pat in (re.escape(entity), re.escape(f"{float(entity):,.0f}") if entity.replace(".", "", 1).isdigit() else None):
        if pat:
            new, n = re.subn(r"(?<![\w.])" + pat + r"(?![\w])", lambda m: f"<<{m.group(0)}>>", text, count=1)
            if n:
                return new
    return text + f"\n[highlighted number: {entity}]"


class FinTaggingAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        import pandas as pd
        root = raw_dir("fintagging")
        p = ensure_file(root / "FinCL-eval_test.parquet", hf_resolve(REPO, "data/test-00000-of-00001.parquet"),
                        headers=hf_headers(), hint="Download data/test-00000-of-00001.parquet from https://huggingface.co/datasets/" + REPO)
        df = pd.read_parquet(p)
        seed = config.get("seed", 0)
        num_q = 0 if config.get("census") else int(config.get("num_questions") or 400)
        n_cand = int(config.get("fincl_candidates", 10))
        rng = random.Random(seed)
        concepts = sorted(df["answer"].unique())
        by_type: Dict[str, set] = defaultdict(set)
        for a, t in zip(df["answer"], df["entity_type"]):
            by_type[t].add(a)
        toks = {c: _camel(c) for c in concepts}
        by_first: Dict[str, List[str]] = defaultdict(list)
        for c, tk in toks.items():
            if tk:
                by_first[tk[0]].append(c)
        # sample: half text, half table (text is the minority category)
        idx_text = df.index[df["category"] == "text"].tolist()
        idx_table = df.index[df["category"] != "text"].tolist()
        picked = (list(idx_text) + list(idx_table)) if config.get("census") else rng.sample(idx_text, min(num_q // 2, len(idx_text))) + rng.sample(idx_table, min(num_q - num_q // 2, len(idx_table)))
        rng.shuffle(picked)
        out = []
        for i in picked:
            r = df.loc[i]
            gold, etype, ent = str(r["answer"]), str(r["entity_type"]), str(r["entity"])
            gt = toks[gold]
            same2 = [c for c in by_first.get(gt[0], []) if c != gold and toks[c][:2] == gt[:2]] if gt else []
            same1 = [c for c in by_first.get(gt[0], []) if c != gold and c not in same2] if gt else []
            rng_i = random.Random(f"{seed}-{i}")
            rng_i.shuffle(same2)
            rng_i.shuffle(same1)
            cands = [gold] + same2[: n_cand - 1]
            cands += same1[: n_cand - len(cands)]
            if len(cands) < n_cand:
                pool = [c for c in by_type.get(etype, set()) if c not in cands] or [c for c in concepts if c not in cands]
                cands += rng_i.sample(pool, min(n_cand - len(cands), len(pool)))
            rng_i.shuffle(cands)
            if r["category"] == "text":
                snippet = _highlight(clip(str(r["context"]), 1500), ent)
                kind = "sentence"
            else:
                m = re.search(r"<context>(.*?)</context>", str(r["query"]), flags=re.S)
                row = (m.group(1).strip() if m else "")
                if row.lower() in ("", "none", "nan"):  # ~22% of table rows have no compact row: take it from the table
                    row = next((ln for ln in _table_snippet(str(r["context"]), ent, budget=100000).split("\n")
                                if ent in ln.replace(",", "")), "")
                excerpt = _highlight(_table_snippet(str(r["context"]), ent), ent)
                snippet = (f"Row containing the number: {_highlight(row, ent)}\n\n" if row else "") + f"Table excerpt:\n{excerpt}"
                kind = "table"
            ctx = (f"Filing excerpt ({kind}); the number to tag is marked with << >>:\n{snippet}\n\n"
                   f"Number: {ent}   XBRL data type: {etype}\n\nCandidate concepts:\n" + "\n".join(f"- {c}" for c in cands))
            out.append(QuestionItem(
                uid=f"fintagging_fincl_{i}", question=QUESTION, ground_truth=gold, gold_aliases=[gold.split(":")[-1]],
                difficulty=str(r["category"]), context=clip(ctx, 2500), dataset_name="fintagging", data_type="document",
                answer_type="text", native_metric="em",
                extra={"task": "FinCL", "category": str(r["category"]), "entity": ent, "entity_type": etype,
                       "n_candidates": len(cands), "n_hard_same_prefix": len([c for c in cands if c != gold and toks[c][:1] == gt[:1]]),
                       "n_concepts_total": len(concepts), "source": "https://huggingface.co/datasets/" + REPO,
                       "licence": "see dataset card (TheFinAI FinTagging; derived from SEC EDGAR filings, public domain)"}))
        return out
