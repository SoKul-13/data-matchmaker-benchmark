# The 31 datasets of the suite: grouping and the processing applied to each

Generated from `config/datasets.toml`, `data/pool/*.jsonl`, `data/pool/_official_strata.json` and `shared/src/families.py` on 2026-10-14.

Columns: pool = items drawn (seeded stratified sample of the official split); answered = items the models answered; data type = what the prompt shows; answer types = gold types among answered items; native = the dataset's own metric used as the baseline column; stratify = the stratum key used for the pool and the census; pool match share = share of 'yes' golds in the pool (matching sets); official n / match share = the censused official population and its match ratio; comparable = whether post-stratified numbers estimate the published split.

## entity matching (11)

| dataset | pool | answered | data type | answer types | native | stratify | pool match share | official n (key) | official match share | comparable | processing notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abt_buy | 150 | 100 | record_pair | boolean 100 | em | - | 0.49 | 1916 (gold_label) | 0.108 | True | official split |
| alaska_camera | 150 | 100 | record_pair | boolean 100 | em | - | 0.53 | 150 (gold_label) | 0.5 | False | pairs constructed from entity clusters (hard negatives by title overlap); no official pair split |
| amazon_google | 150 | 100 | record_pair | boolean 100 | em | - | 0.45 | 2293 (gold_label) | 0.102 | True | official split |
| dblp_acm | 150 | 100 | record_pair | boolean 100 | em | - | 0.49 | 2473 (gold_label) | 0.18 | True | official split |
| dblp_scholar | 150 | 100 | record_pair | boolean 100 | em | - | 0.51 | 5742 (gold_label) | 0.186 | True | official split |
| machamp | 150 | 100 | record_pair | boolean 100 | em | difficulty | 0.53 | 15280 (difficulty) | 0.175 | True | official split |
| opensanctions_pairs | 150 | 100 | record_pair | boolean 100 | em | - | 0.49 | 1000 (gold_label) | 0.769 | True | population = the dataset's stratified sample_1000.json, not the full 390 MB pair file |
| papadakis_dn | 150 | 100 | record_pair | boolean 100 | em | difficulty | 0.15 | 118819 (difficulty) | 0.018 | True | official split |
| walmart_amazon | 150 | 100 | record_pair | boolean 100 | em | - | 0.41 | 2049 (gold_label) | 0.094 | True | official split |
| wdc_lspc | 150 | 100 | record_pair | boolean 100 | em | difficulty | 0.54 | 4249 (difficulty) | 0.264 | True | official split |
| wdc_products | 150 | 100 | record_pair | boolean 100 | em | difficulty | 0.54 | 1200 (difficulty) | 0.28 | True | WDC Products 2024 test split at the fetched size |

## schema matching / integration (6)

| dataset | pool | answered | data type | answer types | native | stratify | pool match share | official n (key) | official match share | comparable | processing notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| alaska_schema | 93 | 93 | table | text 93 | em | - |  | 93 (answer_type) |  | True | monitor half of the schema-matching gold only (camera GT unavailable) |
| fintagging | 150 | 100 | document | text 100 | em | difficulty |  | 52572 (difficulty) |  | True | FinCL only; 10 candidate concepts shown |
| magneto_gdc | 150 | 100 | table | text 100 | em | difficulty |  | 165 (difficulty) |  | True | per-column framing; 40 candidate targets shown of 736 |
| smat | 150 | 100 | table | text 100 | em | difficulty |  | 176 (difficulty) |  | True | per-column framing; 10 candidates (true + 9 hard negatives) |
| tpcdi_cells | 150 | 100 | table | numeric 75/text 25 | num_tol/em | difficulty |  | 720 (difficulty) |  | True | the benchmark's own cell task; population = all generated cells |
| valentine | 150 | 100 | table | text 100 | em | difficulty |  | 293 (difficulty) |  | True | 4 table pairs per (sub-benchmark x pair type) + all Magellan / WikiData pairs; per-column framing, candidates trimmed to budget |

## table QA / understanding (11)

| dataset | pool | answered | data type | answer types | native | stratify | pool match share | official n (key) | official match share | comparable | processing notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bird | 150 | 100 | document | numeric 50/text 50 | num_tol/em | difficulty |  | 1145 (difficulty) |  | True | questions whose gold SQL returns 1-5 short cells; graded on the result value, not on SQL execution accuracy |
| fetaqa | 120 | 100 | table | freeform 100 | rouge_l | - |  | 2003 (answer_type) |  | True | official split |
| hitab | 150 | 100 | table | numeric 64/text 36 | num_tol/em | - |  | 1584 (answer_type) |  | True | official split |
| mmtu | 150 | 100 | table | text 52/boolean 33/numeric 15 | em/num_tol | difficulty |  | 992 (difficulty) |  | True | 9 of 25 MMTU tasks (short deterministic golds only) |
| realhitbench | 150 | 100 | table | numeric 52/text 45/boolean 3 | num_tol/em | difficulty |  | 1232 (difficulty) |  | True | Fact Checking + Numerical Reasoning only (Structure Comprehending golds are empty in the release; Data Analysis / Visualization are free text) |
| suc | 150 | 100 | table | text 91/numeric 9 | em/num_tol | difficulty |  | 600 (difficulty) |  | True | SUC tasks regenerated from the TableProvider source tables (no released item file) |
| tab_fact | 120 | 100 | table | boolean 100 | em | - | 0.46 | 3390 (gold_label) | 0.5 | True | official split |
| tabis | 150 | 100 | table | text 100 | em | difficulty |  | 996 (difficulty) |  | True | zero-shot, three strata |
| tablebench | 150 | 100 | table | numeric 52/text 48 | num_tol/em | difficulty |  | 493 (difficulty) |  | True | FactChecking + NumericalReasoning only |
| tableeval | 150 | 100 | table | numeric 50/text 49/freeform 1 | num_tol/em/rouge_l | difficulty |  | 957 (difficulty) |  | True | 8 short-gold sub-tasks, single-turn only |
| wikitablequestions | 120 | 100 | table | text 49/numeric 49/boolean 2 | em | - |  | 4344 (answer_type) |  | True | official split |

## financial documents (3)

| dataset | pool | answered | data type | answer types | native | stratify | pool match share | official n (key) | official match share | comparable | processing notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| officeqa | 120 | 100 | document | numeric 89/text 11 | num_tol/em | - |  | 0 (None) |  | False | census failed: Client error '404 Not Found' for url 'https://raw.githubusercontent.com/databricks/officeqa/main/officeqa.csv'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404 |
| officeqa_pro_v2 | 90 | 90 | document | numeric 67/text 23 | num_tol/em | - |  | 90 (answer_type) |  | True | all 90 questions; referenced pages in context |
| tat_qa | 120 | 100 | table | numeric 60/text 32/freeform 8 | em/num_tol | difficulty |  | 1668 (difficulty) |  | True | official split |

## What was done to each dataset (adapter framing), by family

Common to all: items come from the official test or dev split (never train); 150 drawn by seeded stratified sampling; 100 flagged for answering
(all 90 for OfficeQA Pro V2, 93 for Alaska schema); gold aliases, unit / percent equivalence and list golds added where applicable; every question
ends with an explicit answer-format instruction; context capped at about 2,500–3,000 characters (6,000 for OfficeQA Pro V2); the same prompt
for every model.

### Entity matching (record pair → yes / no; native metric exact match; post-stratification reports positive-class F1 at the official match ratio)
- **abt_buy, amazon_google, walmart_amazon, dblp_scholar, dblp_acm** (Magellan / DeepMatcher): official test pairs; balanced 50/50 sample; records rendered as attribute: value lines. Official match shares 9–19 %.
- **wdc_products** (WDC Products 2024): official test split with hard negatives, balanced per product category; **wdc_lspc** (Products-2017): the four category test sets, balanced per category, excluding pairs already used by wdc_products.
- **machamp**: seven heterogeneous-schema tasks (structured vs text, different schemas); balanced within each task; WDC-derived records cleaned of suffixes and language tags.
- **papadakis_dn**: Dn1–Dn8 re-built sets; uniform sampling within each set so the real class ratio (1.8 % overall; Dn3 95 %, Dn5 0.3 %) is preserved; this set is deliberately not balanced.
- **alaska_camera**: entity clusters from the SIGMOD 2020 contest gold; positives = labelled pairs (cross-source preferred), negatives = the hardest third of labelled non-matches by title overlap; not a published pair split, so not comparable.
- **opensanctions_pairs**: the dataset's stratified `sample_1000.json`; balanced; multilingual person / organisation records; licence CC BY-NC.

### Schema matching / integration (one question per source column → target column name; native metric exact match)
- **valentine**: four table pairs per (sub-benchmark × pair type: joinable, semantically joinable, unionable, view-unionable) plus all Magellan / WikiData pairs; up to six source columns per pair; target list trimmed to budget but always containing the gold; the full gold mapping per table is stored for set-level F1.
- **magneto_gdc**: source study columns → GDC data-model columns; 40 of 736 targets shown (gold + name-overlap hard negatives + random); many-to-one golds carried as aliases; value vocabularies shown.
- **smat**: MIMIC-III / Synthea / CMS → OMOP; each source attribute with its description; candidates = true target(s) + 9 hard negatives from the same OMOP table; answers are `table-attribute`.
- **alaska_schema**: monitor source attributes → mediated schema (687-attribute camera gold unavailable behind a dead login); source attribute + 3 sample values + target list.
- **fintagging** (FinCL task only): a number highlighted in a 10-K sentence or table row; 10 candidate XBRL concepts (gold + same-prefix hard negatives); half text, half table items.
- **tpcdi_cells**: the benchmark's own task: per customer, cells of the joined / aggregated brokerage tables from the lite CSVs; numeric and text golds; stratified by difficulty.

### Table question answering / understanding
- **wikitablequestions**: official test questions; typed gold (number / text / list) with aliases; native exact match on the denotation.
- **tab_fact**: official test statements; entailed / refused as yes / no; native exact match; official split is balanced.
- **fetaqa**: official test; free-form sentence gold; native ROUGE-L.
- **hitab**: official test over hierarchical statistical tables; number / text golds; native 1 % numeric tolerance or exact match.
- **mmtu**: 9 of 25 tasks with short deterministic golds (table QA, fact verification, entity matching, column-type and cell-entity annotation, header-value matching, imputation, error detection, column property); task in `extra`; JSON preamble stripped.
- **realhitbench**: Fact Checking and Numerical Reasoning only (Structure Comprehending golds are empty in the release; Data Analysis / Visualization are free text); CSV tables capped at 60 × 12; comma lists → list golds; licence CC BY-NC.
- **suc** (Table Meets LLM): the six structural tasks (cell lookup, reverse lookup, row / column retrieval, size detection, merged-cell detection) regenerated deterministically from the TableProvider source tables because no item file is released; indexing convention stated in every question.
- **tabis**: zero-shot; three strata (basic, structure-aware, synthetic lookups); gold = option letter with the option text as alias.
- **tableeval**: eight short-gold Chinese / English sub-tasks, single-turn only; original per-task instructions preserved; numeric golds with bare-number aliases; long golds scored as free-form.
- **tablebench**: FactChecking and NumericalReasoning sub-types; numeric-looking golds typed numeric; comma lists → list golds.
- **bird**: gold SQL executed read-only on the 11 dev databases (10 s timeout); questions kept when the result is 1–5 short cells; gold = the result value; context = CREATE TABLE statements of the referenced tables + the evidence hint; sampled across databases by difficulty.

### Financial documents
- **tat_qa**: official dev questions over report tables + text; span / multi-span / count / arithmetic answers; stratified by answer form; unit and scale handling in the gold.
- **officeqa_pro_v2**: all 90 questions; the referenced parsed-JSON pages (249 documents, 1-based page numbers verified) placed in context with a 6,000-character budget; scalar / currency / percent → numeric with bare-number alias; bracket lists → list golds.
- **officeqa** (closed-book, the benchmark's original set): kept for continuity; every model at floor, so not comparable and excluded from the objective by the diagnostics flag.

### Families used elsewhere
Family labels (EM, SM, TQA, FIN) drive the family-balanced pooling rule, leave-one-family-out transfer and the per-family optima.
