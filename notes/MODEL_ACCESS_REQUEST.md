# Model access request: what is free, what needs money, what needs approval

## Status after the key smoke test (2026-09-23, one tiny call per model)

| Model | Result | What is still needed |
|---|---|---|
| gpt-5.5, gpt-5.4-mini, claude-opus-5, claude-sonnet-5 | working | nothing |
| gpt-oss-120b (Groq) | working, free | nothing |
| llama-3.3-70b (Together) | working | nothing |
| deepseek-chat, deepseek-r1 (DeepSeek) | working | nothing |
| gemini-3.1-pro, gemini-3.8-flash | 402 "prepayment credits are depleted" | add prepaid credit to the AI Studio project at https://ai.studio/projects (~USD 5) |
| grok-4 (xAI) | 403 "team doesn't have any credits" | buy credits at console.x.ai, then `enabled = true` |
| mistral-medium (Mistral) | 429 "Rate limit exceeded" on every call, even 30 s apart | activate the free Experiment plan in console.mistral.ai (Billing / plan selection; phone verification). mistral-large is not in the free tier, so the entry is now Mistral Medium 3 |
| qwen-3.7-plus (Together) | 403 "requires third-party models" | Together serves no open-weight Qwen on demand any more; Alibaba's Qwen 3.7 Plus is relayed but needs "third-party models" enabled in Together account settings, then `enabled = true`. Or drop Qwen |
| Hugging Face token | working; OfficeQA Pro V2 access confirmed | nothing |

Working now: 8 of 13 models. Every `.env` (v1–v5) holds the same keys and all five are git-ignored; no key has ever been committed.


Purpose: run the 31-dataset suite (evidence top 30 + OfficeQA) of `v6_top30_significance/` on 13 models. Four models are already paid for
on the first 7 datasets; every other model is wired in `config/models.toml` and starts automatically when its key is in `.env`.
Suite size for the estimates: 1,240 items (31 datasets × 40) for new models; 1,040 items (26 datasets × 40) for the four cached models.

## A. Free (no card; sign up, paste the key, done)

| # | Model | Provider / plan | Key line in `.env` | Where | Limit | Time to finish the suite |
|---|---|---|---|---|---|---|
| 1 | gpt-oss-120b (OpenAI open-weight flagship) | Groq free tier | `GROQ_API_KEY=` | https://console.groq.com/keys | 30 req/min, 1,000 req/day, 200K tokens/day | ~4 daily re-runs (the runner stops at the cap and resumes from cache) |
| 2 | mistral-large | Mistral Experiment plan (phone verification, no card) | `MISTRAL_API_KEY=` | https://console.mistral.ai/api-keys | ~1B tokens/month, ~1 req/s | under 1 hour |
| 3 | RealHiTBench, BIRD | already downloaded | none | – | – | done |

Note on 2: Mistral may use free-tier traffic for training. Our prompts are public benchmark items, so this is acceptable; say so in the paper's ethics line.
Note: Llama 3.3 70B left Groq's free tier on 2026-08-16; on the direct route it runs on Together (section B, item 4).

## B. Needs a small payment (send for approval) — direct route, no OpenRouter account

| # | Item | One-time cost | Unlocks | Where |
|---|---|---|---|---|
| 4 | Together prepaid credit | **USD 5** minimum top-up (~USD 2 used) | llama-3.3-70b, qwen-2.5-72b | https://api.together.xyz/settings/api-keys → `TOGETHER_API_KEY=` |
| 5 | DeepSeek prepaid credit | **USD 2** (~USD 2 used) | deepseek-chat, deepseek-r1 | https://platform.deepseek.com/api_keys → `DEEPSEEK_API_KEY=` |
| 6 | Google AI Studio billing on the existing Gemini key | **~USD 5** usage | gemini-3.1-pro (paid-only since 2026-04) and gemini-3.8-flash (free tier ~20 req/day, unusable) | https://aistudio.google.com/apikey → enable billing; no config change |
| 7 | The four cached models on the 26 new datasets | **USD 32–40** usage | gpt-5.5, gpt-5.4-mini, claude-opus-5 (about 70 % of the cost), claude-sonnet-5 | keys already present; `scripts/00_run_models.py --sequential` |
| 8 | xAI credits (optional) | **USD 5** minimum top-up, ~USD 5 usage | grok-4 | https://console.x.ai → then set `enabled = true` on grok-4 in `config/models.toml` |

Total to approve: USD 44–52 without Grok, USD 54–62 with Grok. Items 4–6 (USD 12) add six models.

## C. Access you must grant yourself (free, but only the account owner can)

| # | Item | Why | Where |
|---|---|---|---|
| 9 | Hugging Face read token | OfficeQA Pro V2 questions and the 249 referenced parsed documents are gated to your account | https://huggingface.co/settings/tokens → `HF_TOKEN=` in `.env` |

## D. Text to send for approval

> Request: USD 12 in API credits (USD 5 Together, USD 2 DeepSeek, USD 5 Google AI Studio) to add six open-weight and Google models to the benchmark, plus USD 40 of usage on the existing OpenAI and Anthropic keys to score 26 additional public datasets (1,040 items × 4 models). Optional: USD 10 for xAI Grok-4. All spend is capped in code (`budget_usd` in `config/models.toml`) and every answer is cached so nothing is paid twice.

## E. What I cannot do for you
Creating accounts, buying credits and pasting keys are account-owner actions. Once a key is in `.env`, run
`uv run python scripts/00_run_models.py --dry-run` to see which models are live, then `--sequential` to run. Free-tier models stop at their
daily cap with a log line and continue from cache on the next run.

Sources for the limits above: Groq free tier ([klymentiev](https://klymentiev.com/blog/groq-pricing), [pricepertoken](https://pricepertoken.com/endpoints/groq/free)),
OpenRouter free routes ([official limits doc](https://openrouter.ai/docs/api_reference/limits), [fast.io](https://fast.io/resources/openrouter-rate-limit/)),
Mistral Experiment plan ([pricepertoken](https://pricepertoken.com/endpoints/mistral/free), [costbench](https://costbench.com/software/llm-api-providers/mistral-ai/free-plan/)),
Gemini free tier ([ai.google.dev rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [scriptbyai](https://www.scriptbyai.com/gemini-api-free-tier-limits/)).
