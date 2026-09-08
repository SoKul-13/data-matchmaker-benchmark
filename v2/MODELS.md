# Models in consideration and how to activate them

All models live in `config/models.toml`. **A model runs only if its credentials are present in
`.env`**; otherwise `scripts/rs/00_run_models.py` prints `skipped <model> no key` and continues.
Nothing else needs editing. Commented placeholder lines for every key are at the bottom of `.env`
and in `sample.env`.

## Policy
Industry-standard models only: per major provider the flagship and its standard tier. No small or
deliberately weak models. Predictions for GPT-4.1-mini, GPT-5-mini and Claude Haiku 4.5 from earlier
runs are kept in `data/predictions/_excluded/` and are not used.

## Status right now

| Provider | Models | Key | Status |
|---|---|---|---|
| OpenAI | gpt-5.5 (flagship), gpt-5.4-mini (standard) | `OPENAI_API_KEY` | present, cached |
| Anthropic | claude-opus-5 (flagship), claude-sonnet-5 (standard) | `ANTHROPIC_API_KEY` | present, cached |
| Google | gemini-3.1-pro (flagship), gemini-3.8-flash (standard) | `GEMINI_API_KEY` | present, **free-tier quota exhausted**: enable billing at https://aistudio.google.com/apikey or wait for the daily reset, then run |
| xAI | grok-4 | `XAI_API_KEY` | key present, **no credits**; `enabled = false` until credits are bought at https://console.x.ai |
| Meta | llama-3.3-70b | `GROQ_API_KEY` (free tier) or Together | not set |
| DeepSeek | deepseek-v2, deepseek-r1 | `DEEPSEEK_API_KEY` (cheap) | not set |
| Alibaba | qwen-2.5-72b | `TOGETHER_API_KEY` or `OPENROUTER_API_KEY` (`:free`) | not set |
| Mistral | mistral-large | `MISTRAL_API_KEY` (free experiment tier) | not set |

## Free options, in the order I would do them

1. **Gemini**: the key exists; enable billing or wait for the free-tier daily reset. Adds a third major provider.
2. **Groq** (https://console.groq.com/keys, no card): Llama-3.3-70B, Meta's open-weight flagship.
3. **Mistral** (https://console.mistral.ai/api-keys, free experiment plan): Mistral Large.
4. **OpenRouter** (https://openrouter.ai/keys): Qwen-2.5-72B via the `:free` model id (edit the qwen entry's base_url / model_id / api_key_env as noted in the toml).
5. **DeepSeek** (paid but about $0.50 for the whole run): DeepSeek-V3 and R1.
6. **xAI**: buy credits, set `enabled = true` on grok-4.

## Run

```bash
uv run python scripts/rs/00_run_models.py --dry-run             # which models are active / skipped
uv run python scripts/rs/00_run_models.py --models llama-3.3-70b --limit 3   # smoke test
uv run python scripts/rs/00_run_models.py --sequential          # all active models (cached, resumable)
scripts/rs/run_all.sh                                           # recalibrate + leaderboard + paper
```

Predictions are appended to `data/predictions/<model>.jsonl`; re-running only fills gaps. The spend
cap in `[global].budget_usd` applies to paid models.

## Adding a model that is not listed

Append to `config/models.toml`:

```toml
[[model]]
name = "my-model"
provider = "openai_compat"          # any OpenAI-compatible chat endpoint
model_id = "<id the endpoint expects>"
base_url = "https://.../v1"         # or "$SOME_ENV_VAR"
api_key_env = "SOME_KEY"
price_in = 0.0
price_out = 0.0
tier = "open"
```
