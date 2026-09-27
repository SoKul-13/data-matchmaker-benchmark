# The model run: what it will do, what it costs, how to start it

Nothing in v6 calls a model API until this is run by hand. Dry run on 2026-09-23 (after re-flagging every pool to 100 answered items):

```
uv run python shared/scripts/00_run_models.py --dry-run
```
→ 3,083 pending items per model (31 datasets; the 200 already-answered items are skipped), about 1.15 M prompt tokens per model, 11 models live
(qwen-3.7-plus disabled until Together's third-party toggle is on; Gemini and Grok need credits before their calls succeed).

## Estimated cost per model (prompt 1.15 M tokens, output ≈ 0.6 M; reasoning models more)

| model | in $/M | out $/M | estimate |
|---|---|---|---|
| claude-opus-5 | 15 | 75 | USD 62 |
| gpt-5.5 | 5 | 20 | USD 18 |
| claude-sonnet-5 | 3 | 15 | USD 13 |
| gemini-3.1-pro | 2 | 12 | USD 10 |
| gpt-5.4-mini | 1 | 6 | USD 5 |
| deepseek-r1 | 0.55 | 2.19 | USD 5 |
| gemini-3.8-flash | 0.5 | 3 | USD 2.5 |
| llama-3.3-70b | 0.88 | 0.88 | USD 1.5 |
| deepseek-chat | 0.27 | 1.10 | USD 1 |
| mistral-medium | free tier (or ≈ USD 1 pay-as-you-go) | | 0–1 |
| gpt-oss-120b | free tier (or ≈ USD 0.5) | | 0–0.5 |
| **total** | | | **≈ USD 120**, of which Opus is half |

The spend cap in `config/models.toml` (`budget_usd`) must be raised to at least 130 before the run; the runner stops at the cap.

## How to run
1. Check keys and caps: `uv run python shared/scripts/00_run_models.py --dry-run`.
2. Smoke test one item per model: `uv run python shared/scripts/00_run_models.py --limit 1 --datasets tab_fact`.
3. Full run, models one after another so free-tier caps do not stall the others: `uv run python shared/scripts/00_run_models.py --sequential`.
   Free-tier models stop at their daily cap with a log line; re-run the same command the next day and they continue from cache.
4. Then the four `run_all.sh` scripts. Each report regenerates in minutes.

## What every prediction row records
model, model_id, dataset, uid, prediction, in_tokens, out_tokens, latency_s, error, finish, cost_usd, **decoding** ("temperature=0.0", or
"default (temperature rejected by API)" for reasoning models that refuse the parameter). The 3× repeat subset for answer-variance is run with
`--limit` on a fixed 100-item sample after the main run (script to be added once the main run exists; it writes to `data/predictions_repeat/`).
