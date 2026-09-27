# Things only you can do (everything except manual labelling)

1. **Approve the prediction run** (≈ USD 22: gpt-5.5, gpt-5.4-mini, claude-opus-5, claude-sonnet-5 on the 7 new
   datasets, 1,050 items). `cd v5_metric_library_anchor_ensemble && uv run python scripts/00_run_models.py --sequential`, then `scripts/run_all.sh`.
2. **Gemini**: enable billing on the key at https://aistudio.google.com/apikey (or wait for the free-tier daily
   reset). No config change needed; gemini-3.1-pro and gemini-3.8-flash then run automatically.
3. **Free open-model keys** (no card): Groq https://console.groq.com/keys → `GROQ_API_KEY=` (Llama-3.3-70B);
   Mistral https://console.mistral.ai/api-keys → `MISTRAL_API_KEY=` (Mistral Large); OpenRouter
   https://openrouter.ai/keys → `OPENROUTER_API_KEY=` (Qwen-2.5-72B `:free`). Paste into `v5_metric_library_anchor_ensemble/.env` (placeholders
   are commented at the bottom).
4. **DeepSeek** (≈ USD 0.50 for the whole run): https://platform.deepseek.com → `DEEPSEEK_API_KEY=`.
5. **xAI** (optional): buy credits at https://console.x.ai, set `enabled = true` on grok-4 in `config/models.toml`.
6. **MultiHiertt** (optional): download `dev.json` from the Google Drive link in github.com/psunlpgroup/MultiHiertt
   to `v5_metric_library_anchor_ensemble/data/raw/multihiertt/dev.json`; then `uv run python scripts/00a_build_item_pool.py --datasets multihiertt`.
7. **OfficeQA corpus** (optional, later): request access to `databricks/officeqa` on Hugging Face to run it with
   retrieval instead of closed-book; until then it stays parked.
8. **Human labels** (the one thing this list excludes): when ready, a CSV `uid,dataset,model,label` with label in
   {1 correct, 0.5 partial, 0 wrong} for ~300 sampled answers; `02_select_metrics.py --labels` uses it as the anchor.

Items 2–4 take the model count from 4 to 8+, which every statistic in the paper needs most.
