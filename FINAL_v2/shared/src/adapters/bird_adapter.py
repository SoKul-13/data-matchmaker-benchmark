"""BIRD (Li et al., NeurIPS'23; bird-bench.github.io; dev set, licence CC BY-SA 4.0) reframed as
schema-grounded question answering: the gold SQL is executed against the SQLite database and the
result becomes the gold answer, so the model must answer the question from the data, not write SQL.
Local files: data/raw/bird/dev_20240627/{dev.json, dev_databases/<db>/<db>.sqlite}.

Framing: only questions whose gold result is a single value or a short list (<= 5 cells, no NULLs)
are kept; gold_list for multi-cell results.  Context = CREATE TABLE statements of the tables referenced
in the SQL (capped at 3,000 chars) + the BIRD 'evidence' hint.  db_id and the SQL are stored in extra.
Every SQL runs with a 10 s timeout; results are cached in data/raw/bird/_gold_exec_cache.json."""
from __future__ import annotations

import json
import logging
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, List, Optional

from .base_adapter import DatasetAdapter, QuestionItem

logger = logging.getLogger(__name__)
RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "bird" / "dev_20240627"
MAX_CELLS, QUERY_TIMEOUT_S, MAX_CTX = 5, 10.0, 3000
MAX_ROWS_FETCH = MAX_CELLS + 2
MAX_GOLD_TOKENS = 8


def _fmt(v) -> str:
    if isinstance(v, float):
        if v.is_integer() and abs(v) < 1e15:
            return str(int(v))
        return f"{v:.6f}".rstrip("0").rstrip(".")
    return str(v)


def _run_sql(conn: sqlite3.Connection, sql: str) -> dict:
    deadline = time.monotonic() + QUERY_TIMEOUT_S
    conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 20000)
    try:
        rows = conn.execute(sql).fetchmany(MAX_ROWS_FETCH)
        return {"rows": [list(r) for r in rows]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"[:200]}
    finally:
        conn.set_progress_handler(None, 0)


def _referenced_schema(conn: sqlite3.Connection, sql: str, max_chars: int = MAX_CTX) -> str:
    tables = [(n, s) for n, s in conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL") if not n.startswith("sqlite_")]
    used = [(n, s) for n, s in tables if re.search(r"(?<![\w])[`\"\[]?" + re.escape(n) + r"[`\"\]]?(?![\w])", sql, flags=re.I)]
    if not used:
        used = tables
    budget = max(400, max_chars // max(1, len(used)))
    parts = []
    for n, s in used:
        s = re.sub(r"\n\s*\n", "\n", s.strip())
        if len(s) > budget:
            s = s[:budget].rstrip() + "\n    ... (columns truncated)\n)"
        parts.append(s)
    out = "\n\n".join(parts)
    return out if len(out) <= max_chars else out[:max_chars] + "\n... (schema truncated)"


class BIRDAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = Path(config.get("dataset_url") or RAW)
        dev, dbs = root / "dev.json", root / "dev_databases"
        if not dev.exists() or not dbs.is_dir():
            raise FileNotFoundError(f"BIRD dev set not found: expected {dev} and {dbs}/<db>/<db>.sqlite (dev_20240627.zip from bird-bench.github.io).")
        cache_path = root.parent / "_gold_exec_cache.json"
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        data = json.loads(dev.read_text(encoding="utf-8"))
        conns: dict = {}
        schemas: dict = {}
        dirty = False
        items: List[QuestionItem] = []
        t0 = time.time()
        for k, q in enumerate(data):
            qid, db = str(q["question_id"]), q["db_id"]
            sql = q["SQL"]
            key = f"{qid}:{hash(sql) & 0xFFFFFFFF}"
            if db not in conns:
                p = dbs / db / f"{db}.sqlite"
                if not p.exists():
                    logger.warning(f"BIRD database missing: {p}")
                    conns[db] = None
                else:
                    conns[db] = sqlite3.connect(f"file:{p}?mode=ro", uri=True, timeout=QUERY_TIMEOUT_S)
                    conns[db].text_factory = lambda b: b.decode("utf-8", errors="replace")
            conn = conns[db]
            if conn is None:
                continue
            if key not in cache:
                cache[key] = _run_sql(conn, sql)
                dirty = True
                if k % 200 == 0:
                    logger.info(f"BIRD: executed {k + 1}/{len(data)} gold queries ({time.time() - t0:.0f}s)")
            res = cache[key]
            rows = res.get("rows")
            if not rows or "error" in res:
                continue
            cells = [c for r in rows for c in r]
            if not 1 <= len(cells) <= MAX_CELLS or any(c is None for c in cells):
                continue
            parts = [_fmt(c) for c in cells]
            if any(len(x.split()) > MAX_GOLD_TOKENS or len(x) > 120 for x in parts):   # keep golds short
                continue
            gold_list = parts if len(parts) > 1 else None
            evidence = (q.get("evidence") or "").strip()
            skey = (db, sql)
            if skey not in schemas:
                schemas[skey] = _referenced_schema(conn, sql, MAX_CTX - len(evidence) - len(db) - 40)
            ctx = f"### Database: {db}\n{schemas[skey]}" + (f"\n\n### Hint\n{evidence}" if evidence else "")
            fmt = "Answer with the values only, separated by ' | '." if gold_list else "Answer with the value only."
            items.append(QuestionItem(
                uid=f"bird_{qid}", question=f"{q['question'].strip()}\n{fmt}", ground_truth=" | ".join(parts) if gold_list else parts[0],
                difficulty=q.get("difficulty") or "all", context=ctx, dataset_name="bird", data_type="document", gold_list=gold_list,
                gold_aliases=[", ".join(parts)] if gold_list else [], native_metric="auto",
                extra={"db_id": db, "sql": sql, "question_id": q["question_id"], "evidence": evidence, "n_cells": len(cells),
                       "n_result_rows": len(rows), "bird_difficulty": q.get("difficulty"), "license": "CC BY-SA 4.0", "source": "BIRD dev_20240627"}))
        if dirty:
            cache_path.write_text(json.dumps(cache))
        for c in conns.values():
            if c is not None:
                c.close()
        return self._select(items, config)
