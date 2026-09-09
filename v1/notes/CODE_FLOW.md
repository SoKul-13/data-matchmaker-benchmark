# v1 — complete code flow (original judge)

## Purpose
An A2A "green agent" (judge) that gives a purple agent the TPC-DI data-integration task (join customers, accounts,
trades; aggregate per customer) and scores the returned table with a 100-point rubric; plus, for question-answer
datasets, a hand-set composite score. This is the baseline every later version is compared against.

## Folder tree (what each file is)
```
v1/
  src/server.py        Starlette + A2A server on :9009; also serves the task CSVs at /files/ (list_files, get_file); main() builds the AgentCard
  src/executor.py      Executor: receives an A2A message, creates a task, calls Agent.run, marks completed/failed
  src/agent.py         Agent: EvalRequest (pydantic) -> validate_request -> _run_assessment: builds the TPC-DI task text, talks to the purple agent
                       via Messenger, parses the returned CSV, evaluate_submission() applies the 100-point rubric, generate_llm_feedback()
                       (Gemini, optional) writes commentary; saves output/results.json and output/eval_results.csv
  src/messenger.py     send_message / Messenger.talk_to_agent: A2A client with retries and timeouts
  src/mock_purple.py   a purple agent that fetches the CSVs, joins with pandas, returns the aggregate table (DataIntegrationAgent.integrate_data)
  src/evaluator.py     QA-answer helpers: normalize_text, extract_numbers_with_context (first number wins), detect_unit_in_context,
                       fuzzy_match_answer (number within tolerance + text overlap), score_answer -> (bool, rationale);
                       EvaluatorStrategy.evaluate for binary / exact_match / freeform / fuzzy_numeric; SeparationFunction (cd weighting);
                       export_eval_results_to_csv
  src/adapters/        base_adapter.QuestionItem (uid, question, ground_truth, difficulty, context, table_data, metric_type, dataset_name, data_type),
                       AdapterRegistry.get_adapter(name) -> OfficeQAAdapter | FinQAAdapter | TATQAAdapter | TabFactAdapter | GenericDatasetAdapter
  scripts/rubric_engine.py   compute_precision_recall_f1, extract_first_number, compute_mre, evaluate_original_rubric (100-pt for QA),
                             evaluate_custom_math_rubric = 100*(0.35 F1 + 0.35 exp(-2.5 MRE) + 0.15 P + 0.15 R), compute_full_eval_metrics
  scripts/benchmark_harness.py  MODEL_CATALOG x PARAM_GRID x DATASET_CATALOG loop; execute_model_prediction() SIMULATES answers
                             (random draw vs a per-model "base accuracy"; noisy copy of the gold on failure); writes the four output/*.md and csv/json
  scripts/eval_new_datasets.py  loads 5 items per dataset through the adapters and scores the GOLD against itself (adapter smoke test)
  scripts/run_local_test.py     starts server + mock purple, sends the TPC-DI request, prints the result
  jan15_tasks/         customers_ (120 rows), accounts_ (220), trades_ (1,200) CSVs, finwire XML, prospect XLSX, gold_ground_truth (120 rows x 9 cols)
  tasks/               six smaller schema-matching tasks with ground_truth.json (not used by the judge)
  data/officeqa.csv    246 questions (uid, question, answer, source_docs, source_files, difficulty)
  config/ scenario.toml, a2a-scenario.toml (dataset_name=officeqa, num_questions=246), sample.env
  output/              results.json, eval_results.csv (TPC-DI run); master_benchmark_results.md, model_rankings_and_gridsearch.md,
                       rubric_math_comparison.md, gridsearch_benchmark_raw.csv/json, multi_dataset_eval_summary.json (from the SIMULATED harness)
```

## Flow diagram
```
[client: run_local_test.py or agentbeats-run]
   | A2A JSON-RPC message {"participants": {"data_integrator": url}, "config": {...}}
   v
server.py --> executor.py --> agent.py.run()
                                 |-- validate_request()           (needs role data_integrator)
                                 |-- task text with /files/ URLs -> messenger.talk_to_agent(purple)
                                 |                                     purple: mock_purple.integrate_data() -> CSV
                                 |-- parse CSV -> evaluate_submission():
                                 |       columns 20 pts | row count 10 | customer coverage 15 | numeric 5x8 (exact for counts, 1% for money) | strings 3x5
                                 |-- generate_llm_feedback() (Gemini, if key)
                                 '-- output/results.json, output/eval_results.csv; artifact back to client
```
QA path (never wired into the agent; only in scripts): adapter -> QuestionItem -> rubric_engine.compute_full_eval_metrics(gold, prediction) ->
{exact_match, precision, recall, f1_score, mre_pct, original_rubric_score, custom_rubric_score}.

## Formulas
* TPC-DI rubric: total = col + row + cov + Σ_numeric_cols 8·acc + Σ_string 5·acc, col = ⌊20·|C_sub ∩ C_exp|/|C_exp|⌋, row ∈ {10,8,5,2,0} by |Δrows|,
  cov = ⌊15·coverage⌋, numeric acc = share of customers within 1 % (money) or exact (counts), string acc = share equal (case-insensitive) or symbol overlap.
* Composite for QA: R_custom = 100·(0.35·F1 + 0.35·e^(−2.5·MRE) + 0.15·P + 0.15·R), MRE = |first number in prediction − first number in gold| / |gold|.

## Status: what has been run, what has not
* TPC-DI mode: run against mock_purple (results.json: 68/100; numeric columns 12/40 because the mock's join logic differs from the gold).
* QA leaderboard files in output/: produced by the SIMULATED harness; they are not model results and must not be cited.
* Never run: real model calls in v1 (there is no inference layer); `a2a-scenario.toml`'s officeqa config is ignored by agent.py.

## Known defects (fixed in later versions)
first-number extraction; no gold aliases / units / lists; TAT-QA gold stored as `str(list)`; FinQA used the program result not the human answer;
TabFact statements sent without their table; hand-set weights; simulated leaderboard.
