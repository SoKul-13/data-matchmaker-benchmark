#!/usr/bin/env python
"""
Step 0 - Query LLMs on the real subset of the item pool (v2: writes data/predictions/).

Predictions are cached in output/v2/predictions/<model>.jsonl (one row per item),
so the script can be re-run safely.  A spend cap (config/models.toml [global].budget_usd)
stops the run when the estimated cost is exceeded.

Usage:
  uv run python scripts/rs/00_run_models.py --dry-run          # shows which models are active / skipped
  uv run python scripts/rs/00_run_models.py                    # all active models, real subset (cached)
  uv run python scripts/rs/00_run_models.py --models llama-3.3-70b@groq --limit 3   # smoke test one model
Then re-run scripts/rs/01_prepare.py .. 03_pool_report.py to refresh the calibration and leaderboard.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # the v6 folder
V6 = ROOT
sys.path.insert(0, str(ROOT / "shared" / "src"))
DATA, CONFIG = ROOT / "data", ROOT / "config"

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

from inference.prompts import SYSTEM_PROMPT, build_prompt  # noqa: E402
from inference.providers import DECODING_USED, GenResult, ModelSpec, generate  # noqa: E402


def enabled_datasets():
    import tomllib
    cfg = tomllib.loads((CONFIG / "datasets.toml").read_text())
    return {d["name"] for d in cfg["dataset"] if d.get("enabled", True)}


def load_items(pool_dir: Path, datasets, limit, real_only=True):
    items = []
    allowed = enabled_datasets()
    for f in sorted(pool_dir.glob("*.jsonl")):
        if f.stem not in allowed:
            continue
        if datasets and f.stem not in datasets:
            continue
        rows = [json.loads(l) for l in open(f, encoding="utf-8")]
        if real_only:
            rows = [r for r in rows if r.get("in_real_subset")]
        if limit:
            rows = rows[:limit]
        items.extend(rows)
    return items


def load_cache(path: Path):
    done = {}
    if path.exists():
        for l in open(path, encoding="utf-8"):
            try:
                r = json.loads(l)
                if not r.get("error"):
                    done[(r["dataset"], r["uid"])] = r
            except json.JSONDecodeError:
                continue
    return done


class Budget:
    def __init__(self, cap):
        self.cap, self.spent, self.in_t, self.out_t = cap, 0.0, 0, 0

    def add(self, res: GenResult, spec: ModelSpec):
        self.spent += res.cost_usd(spec)
        self.in_t += res.in_tokens
        self.out_t += res.out_tokens

    @property
    def exceeded(self):
        return self.spent >= self.cap


async def run_model(spec: ModelSpec, items, out_path: Path, budget: Budget, max_tokens: int, log):
    done = load_cache(out_path)
    todo = [it for it in items if (it["dataset_name"], it["uid"]) not in done]
    log(f"[{spec.name}] cached={len(done)} todo={len(todo)}")
    if not todo:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(out_path, "a", encoding="utf-8")
    n_ok = n_err = 0
    t0 = time.time()
    # free-tier throttle: at most spec.rpm requests per minute and spec.rpd per run (cached rows are skipped on the next run)
    gate = asyncio.Lock(); state = {"last": 0.0, "sent": 0, "capped": False}
    min_gap = 60.0 / spec.rpm if spec.rpm else 0.0

    async def one(it):
        nonlocal n_ok, n_err
        if budget.exceeded or state["capped"]:
            return
        async with gate:
            if spec.rpd and state["sent"] >= spec.rpd:
                if not state["capped"]:
                    state["capped"] = True
                    log(f"[{spec.name}] daily cap rpd={spec.rpd} reached; re-run tomorrow to continue from cache")
                return
            wait = state["last"] + min_gap - time.time()
            if wait > 0:
                await asyncio.sleep(wait)
            state["last"] = time.time(); state["sent"] += 1
        prompt = build_prompt(it)
        res = await generate(spec, prompt, SYSTEM_PROMPT, max_tokens=max_tokens)
        budget.add(res, spec)
        row = {"model": spec.name, "model_id": spec.model_id, "dataset": it["dataset_name"], "uid": it["uid"],
               "prediction": res.text, "in_tokens": res.in_tokens, "out_tokens": res.out_tokens,
               "latency_s": round(res.latency_s, 3), "error": res.error, "finish": res.raw_finish, "decoding": DECODING_USED.get(spec.name, "default"),
               "cost_usd": round(res.cost_usd(spec), 6)}
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        if res.error:
            n_err += 1
        else:
            n_ok += 1

    await asyncio.gather(*(one(it) for it in todo))
    f.close()
    log(f"[{spec.name}] done ok={n_ok} err={n_err} in {time.time() - t0:.0f}s | run spend so far ${budget.spent:.2f} "
        f"(in={budget.in_t} out={budget.out_t} tokens)")


async def main_async(args):
    cfg = tomllib.loads((CONFIG / "models.toml").read_text())
    g_temp = cfg["global"].get("temperature", None)
    specs = [ModelSpec(**{"temperature": g_temp, **m}) for m in cfg["model"]]
    if args.models:
        want = {m.strip() for m in args.models.split(",")}
        specs = [s for s in specs if s.name in want]
    skipped = [s for s in specs if not s.key_available()]
    specs = [s for s in specs if s.key_available()]
    for s in skipped:
        reason = "disabled" if not s.enabled else f"no key / URL ({s.api_key_env or s.provider})"
        print(f"skipped {s.name:32s} {reason}")
    order = {"anchor": 0, "fast": 1, "open": 2, "mid": 3, "flagship": 4}
    specs.sort(key=lambda s: (order.get(s.tier, 9), s.name))
    datasets = {d.strip() for d in args.datasets.split(",")} if args.datasets else None
    items = load_items(DATA / "pool", datasets, args.limit, real_only=not args.all_items)
    budget = Budget(args.budget or cfg["global"]["budget_usd"])
    max_tokens = args.max_tokens or cfg["global"].get("max_tokens", 700)
    out_dir = DATA / "predictions"
    log_path = DATA / "predictions" / "_run.log"
    out_dir.mkdir(parents=True, exist_ok=True)

    def log(msg):
        print(msg, flush=True)
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(time.strftime("%H:%M:%S ") + msg + "\n")

    log(f"models={[s.name for s in specs]} items={len(items)} budget=${budget.cap}")
    if args.dry_run:
        chars = sum(len(build_prompt(it)) for it in items)
        log(f"dry-run: ~{chars // 4} prompt tokens per model x {len(specs)} models")
        return
    async def guarded(spec):
        if budget.exceeded:
            log(f"budget cap ${budget.cap} reached; skipping {spec.name}")
            return
        try:
            await run_model(spec, items, out_dir / f"{spec.name}.jsonl", budget, max_tokens, log)
        except Exception as e:  # noqa: BLE001
            log(f"[{spec.name}] FAILED: {type(e).__name__}: {e}")

    if args.sequential:
        for spec in specs:
            await guarded(spec)
    else:
        # models run concurrently (each with its own concurrency limit); the spend cap is shared
        await asyncio.gather(*(guarded(s) for s in specs))
    log(f"TOTAL estimated spend this run: ${budget.spent:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="")
    ap.add_argument("--datasets", default="")
    ap.add_argument("--limit", type=int, default=0, help="items per dataset (0 = whole real subset)")
    ap.add_argument("--all-items", action="store_true", help="use the whole pool, not only the real subset")
    ap.add_argument("--budget", type=float, default=None)
    ap.add_argument("--max-tokens", type=int, default=None, help="override [global] max_tokens (e.g. re-running truncated answers with a larger budget)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sequential", action="store_true", help="run models one after another")
    args = ap.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
