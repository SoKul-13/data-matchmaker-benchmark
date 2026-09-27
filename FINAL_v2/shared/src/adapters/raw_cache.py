"""Helpers for adapters that keep their raw downloads under <V6>/data/raw/<dataset>/.

Every adapter built on these helpers works offline once the files are present and raises a
FileNotFoundError naming the missing file (and where to get it) otherwise.
"""
from __future__ import annotations

import os
import random
import re
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import httpx

V6 = Path(__file__).resolve().parents[3]
RAW = Path(os.environ.get("DMB_RAW_DIR", V6 / "data" / "raw"))


def raw_dir(dataset: str) -> Path:
    p = RAW / dataset
    p.mkdir(parents=True, exist_ok=True)
    return p


def hf_token() -> Optional[str]:
    tok = os.environ.get("HF_TOKEN")
    if tok:
        return tok
    env = V6 / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("HF_TOKEN=") and line.split("=", 1)[1].strip():
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def ensure_file(path: Path, url: Optional[str] = None, *, hint: str = "", timeout: float = 600.0,
                headers: Optional[dict] = None) -> Path:
    """Return `path`, downloading it from `url` first if it is missing.  Raises a clear error otherwise."""
    if path.exists() and path.stat().st_size > 0:
        return path
    if not url:
        raise FileNotFoundError(f"Missing raw file {path}. {hint}".strip())
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=timeout, headers=headers or {}) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
        tmp.replace(path)
    except Exception as e:  # pragma: no cover - network
        if tmp.exists():
            tmp.unlink()
        raise FileNotFoundError(f"Could not download {url} -> {path}: {e}. {hint}".strip()) from e
    return path


def hf_resolve(repo: str, filename: str, kind: str = "datasets") -> str:
    return f"https://huggingface.co/{kind}/{repo}/resolve/main/{filename}"


def hf_headers() -> dict:
    tok = hf_token()
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def default_pool_n(dataset: Optional[str] = None, fallback: int = 150) -> int:
    """pool_size from config/datasets.toml ([[dataset]] override, else [global]).  Balanced adapters emit exactly
    this many items when the pool builder passes no num_questions, so the pool keeps the 50 / 50 split."""
    try:
        import tomllib
        cfg = tomllib.loads((V6 / "config" / "datasets.toml").read_text())
        n = int(cfg.get("global", {}).get("pool_size", fallback))
        for d in cfg.get("dataset", []):
            if dataset and d.get("name") == dataset and d.get("pool_size"):
                n = int(d["pool_size"])
        return n
    except Exception:  # pragma: no cover
        return fallback


def clip(text, n: int) -> str:
    s = "" if text is None else str(text)
    s = s.replace("\r", " ").strip()
    return s if len(s) <= n else s[: n - 3].rstrip() + "..."


def render_kv(rec: dict, *, skip: Iterable[str] = (), max_val: int = 300, max_total: int = 1100) -> str:
    """Render a record as `key: value` lines, dropping empty values and clipping long ones."""
    skip = set(skip)
    lines: List[str] = []
    for k, v in rec.items():
        if k in skip or v is None:
            continue
        if isinstance(v, (list, tuple)):
            v = "; ".join(str(x) for x in v if x is not None and str(x).strip())
        s = re.sub(r"\s+", " ", str(v)).strip()  # collapse tabs / newlines inside values
        if s in ("", "None", "nan", "NaN", "null", "[]", "{}"):
            continue
        lines.append(f"{k}: {clip(s, max_val)}")
    return clip("\n".join(lines), max_total)


def balanced_sample(pos: Sequence, neg: Sequence, n: int, rng: random.Random) -> list:
    """Half positives / half negatives (as far as available), shuffled."""
    k = n // 2
    p = rng.sample(list(pos), min(k, len(pos)))
    q = rng.sample(list(neg), min(n - len(p), len(neg)))
    out = p + q
    rng.shuffle(out)
    return out


def tokens(s: str) -> set:
    import re
    return {t for t in re.split(r"[^a-z0-9]+", str(s).lower()) if len(t) > 1}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0
