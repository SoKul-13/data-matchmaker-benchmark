"""Shared helpers: cached HTTP fetch, zip member fetch, table rendering."""
from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from pathlib import Path
from typing import Any, List, Optional, Sequence

import httpx

CACHE_DIR = Path(os.environ.get("DMB_CACHE_DIR", Path(__file__).resolve().parents[2] / "data" / "cache"))


def fetch_bytes(url: str, timeout: float = 120.0, cache: bool = True) -> bytes:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".bin")
    if cache and path.exists():
        return path.read_bytes()
    resp = httpx.get(url, follow_redirects=True, timeout=timeout)
    resp.raise_for_status()
    if cache:
        path.write_bytes(resp.content)
    return resp.content


def fetch_text(url: str, timeout: float = 120.0, cache: bool = True) -> str:
    return fetch_bytes(url, timeout, cache).decode("utf-8", errors="replace")


def load_text_or_url(src: str, timeout: float = 120.0) -> str:
    if src.startswith("http://") or src.startswith("https://"):
        return fetch_text(src, timeout=timeout)
    with open(src, "r", encoding="utf-8") as f:
        return f.read()


_ZIPS: dict = {}


def zip_member(url_or_path: str, member: str) -> Optional[str]:
    """Read one member (suffix match) from a zip archive; the archive is opened once and cached."""
    if url_or_path not in _ZIPS:
        data = fetch_bytes(url_or_path) if url_or_path.startswith("http") else Path(url_or_path).read_bytes()
        _ZIPS[url_or_path] = zipfile.ZipFile(io.BytesIO(data))
    z = _ZIPS[url_or_path]
    cand = [n for n in z.namelist() if n.endswith(member)]
    if not cand:
        return None
    return z.read(cand[0]).decode("utf-8", errors="replace")


def render_table(rows: Sequence[Sequence[Any]], *, max_rows: int = 40, max_chars: int = 4000,
                 title: Optional[str] = None) -> str:
    lines: List[str] = []
    if title:
        lines.append(f"Table: {title}")
    for i, row in enumerate(rows):
        if i >= max_rows:
            lines.append(f"... ({len(rows) - max_rows} more rows omitted)")
            break
        lines.append(" | ".join("" if c is None else str(c).strip() for c in row))
        if i == 0:
            lines.append("-" * min(60, len(lines[-1])))
    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... (table truncated)"
    return text


def render_json_table(table: Any, **kw) -> str:
    if isinstance(table, list):
        return render_table(table, **kw)
    if isinstance(table, dict):
        if "header" in table and "rows" in table:
            return render_table([table["header"]] + list(table["rows"]), **kw)
        if "table" in table:
            return render_json_table(table["table"], **kw)
        cols = list(table.keys())
        if cols and all(isinstance(table[c], list) for c in cols):
            n = max(len(table[c]) for c in cols)
            return render_table([cols] + [[table[c][i] if i < len(table[c]) else "" for c in cols] for i in range(n)], **kw)
    return json.dumps(table)[: kw.get("max_chars", 4000)]


def render_record(rec: dict, skip=("id",)) -> str:
    return "\n".join(f"{k}: {v}" for k, v in rec.items() if k not in skip and str(v).strip() not in ("", "None", "nan"))
