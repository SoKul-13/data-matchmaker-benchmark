# The 30 datasets for the v6 run: what each one is, why it is in, and the pre-run notes

Ranking source: `datasets_survey/05_RANKED_100_evidence.md` (adoption measured from a citation-ranked corpus of ≈220 papers; other
criteria: relevance, generalisation, discriminative power today, gold clarity, inclusivity, licence). "Uses" = number of corpus papers
that evaluate on the dataset (2023+ in brackets). OfficeQA (closed-book, already answered) is kept alongside as the 31st.

## A. Entity matching: is this pair of records the same real-world thing? (answer yes/no; 12 sets)

| # | Dataset | What it is | Why it is in | Uses | Licence |
|---|---|---|---|---|---|
| 1 | Abt-Buy | 1,081 vs 1,092 electronics product listings from two shops, matched by free-text titles and descriptions | the canonical *textual* matching task; frontier models still miss abbreviations and model-number variants, so it discriminates | 17 (8) | CC BY 4.0 |
| 2 | Amazon-Google | 1,363 vs 3,226 software products (name, manufacturer, price) | the hardest classic: fine-tuned models reach F1 ≈ 0.75 only; used by 21 of 35 matching papers | 21 (11) | CC BY 4.0 |
| 4 | Walmart-Amazon (+dirty) | 2,554 vs 22,074 electronics with structured attributes; the "dirty" variant shuffles values into wrong columns | the standard structured product task with headroom; the dirty variant tests robustness to schema noise | 19 (11) | Magellan academic |
| 5 | DBLP-Scholar (+dirty) | 2,616 DBLP vs 64,263 Google Scholar citation records | the canonical bibliographic task; noisy Scholar records keep it unsaturated | 21 (11) | CC BY 4.0 |
| 9 | Machamp (7 GEM tasks) | seven tasks that match a structured record against a text description, or records with different schemas | the only benchmark for *heterogeneous* matching (structured vs text), which is what real integration looks like | 2 (0) | BSD-3 / CC |
| 12 | WDC Products 2024 | web product offers with hard negatives (near-identical products that are not the same) at several corner-case rates | the best-designed modern product set; hard negatives are exactly where LLM matchers fail | 2 (2) | unstated |
| 14 | Papadakis-Christen Dn1-Dn8 | eight re-built classic sets with realistic match/non-match imbalance | corrects the saturation of the classics; shows whether a scorer is fooled by class balance | 1 (1) | Zenodo |
| 15 | Alaska Camera | camera specifications from 24 web sources with entity clusters as gold | schema-agnostic, genuinely messy web data; the same source also has schema gold (row 16) | 3 (0) | MIT |
| 21 | OpenSanctions Pairs | person and organisation records from sanctions lists in 45 jurisdictions, multilingual names | the only large real people/organisation matching set; the inclusivity entry for names in many scripts | 0 | CC BY-NC 4.0 |
| 27 | DBLP-ACM (+dirty) | 2,616 DBLP vs 2,294 ACM records | near-solved (F1 ≈ 0.99); kept as the sanity check that every scorer must get right | 20 (10) | CC BY 4.0 |
| 29 | WDC LSPC / Products-2017 | web product offers in four categories (computers, cameras, watches, shoes) | the standard web-product benchmark before 2024; comparability with the transformer-era papers | 6 (2) | Common Crawl terms |

## B. Schema matching and integration: which column maps to which? (answer: a column name or mapping; 6 sets)

| # | Dataset | What it is | Why it is in | Uses | Licence |
|---|---|---|---|---|---|
| 3 | Magneto GDC-SM | real biomedical data harmonisation: source columns from cancer studies mapped to the GDC data model, many-to-one, with value vocabularies | the most realistic schema-matching gold in existence; many-to-one mappings and controlled vocabularies are what defeats current LLM matchers | 1 (1) | CC BY 4.0 |
| 7 | Valentine | schema-matching pairs built from TPC-DI, OpenData, ChEMBL, WikiData and Magellan with controlled noise (joinable, unionable, semantically joinable) | the de-facto benchmark every LLM schema-matching paper reports on (Unicorn, Magneto) | 3 (2) | Apache-2.0 |
| 10 | SMAT (MIMIC / Synthea / CMS → OMOP) | healthcare source schemas mapped to the OMOP common data model | real healthcare schemas; used by every 2023+ LLM schema-matching paper | 6 (5) | unstated |
| 13 | FinTagging (FinNI + FinCL) | numbers in SEC 10-K filings linked to XBRL taxonomy concepts (thousands of labels) | taxonomy alignment in finance; frontier accuracy on concept linking is ≈ 0.17, the largest headroom in the suite | 1 (1) | unstated |
| 16 | Alaska schema-matching GT | 687 to 1,026 attribute mappings across the camera and monitor sources | thousands of heterogeneous attribute names from real web pages | 3 (0) | MIT |
| 24 | TPC-DI (cell-level task) | the benchmark's own task: join and aggregate brokerage ETL tables; each customer's gold cells come from the mapping spec | the task the green agent was built for; keeps v1's original rubric comparable with the new scorers | 3 (2) | CC BY-NC-ND spec |

## C. Table question answering and table understanding (answer: number, span, list, boolean or sentence; 11 sets)

| # | Dataset | What it is | Why it is in | Uses | Licence |
|---|---|---|---|---|---|
| 6 | HiTab | 10,672 questions over hierarchical statistical tables from government and Statistics Canada reports | the best real hierarchical tables; header hierarchy is a matching problem; frontier models still at ≈ 0.8 | 5 (4) | C-UDA 1.0 |
| 8 | MMTU | 25 data-management tasks over 52 datasets, including schema matching, entity matching, join and transformation subtasks | the omnibus table-understanding benchmark; GPT-5 scores ≈ 0.70, so it separates models | 1 (1) | MIT |
| 11 | WikiTableQuestions | 22,033 questions over Wikipedia tables with a typed evaluator | the canonical single-table QA set (22 corpus uses) and still ≈ 75 % for frontier models | 22 (13) | CC BY-SA 4.0 |
| 17 | RealHiTBench | 3,071 questions over 708 real hierarchical tables in 24 domains, with fact checking, numerical reasoning, data analysis and structure questions | purpose-built to test header-hierarchy matching; the hardest current hierarchical set | 1 (1) | CC BY-NC 4.0 |
| 18 | SUC (Table Meets LLM) | structural probes: find a cell, detect a merged header, retrieve a row | the purest test of whether a model can *read* a table before reasoning about it | 1 (1) | unstated |
| 19 | TabIS | information seeking where the answer table sits among distractor tables; binary choice | hard negatives across tables, the table analogue of entity-matching hard negatives | 1 (1) | unstated |
| 20 | TableEval | Chinese and English nested spreadsheets with free-form answers | the only realistic multilingual spreadsheet set; the inclusivity entry for tables | 1 (1) | Apache-2.0 |
| 22 | BIRD | 1,534 dev questions over 95 SQLite databases with dirty values and external knowledge | value-grounded text-to-SQL; run here by executing gold SQL so the gold is the *result value*, usable by every version | 9 (9) | CC BY-SA 4.0 |
| 25 | TabFact | 117,854 statements over Wikipedia tables, entailed or refuted | the boolean table anchor with 17 corpus uses; ≈ 90 % for frontier models, so it also checks the boolean scorer | 17 (11) | CC BY 4.0 |
| 26 | FeTaQA | 10,330 free-form sentence answers over Wikipedia tables | the free-form anchor: the only way to test ROUGE/F1-type components against sentence golds | 11 (7) | CC BY-SA 4.0 |
| 28 | TableBench | 886 questions over mixed tables: fact checking, numerical reasoning, data analysis, chart code | the hard current TableQA leaderboard set | 2 (2) | Apache-2.0 |

## D. Financial documents (2 sets, plus OfficeQA closed-book kept as the 31st)

| # | Dataset | What it is | Why it is in | Uses | Licence |
|---|---|---|---|---|---|
| 23 | OfficeQA Pro V2 | 90 questions that need numbers reconciled across the U.S. Treasury's Combined Statements 1793–2024 (1,435 documents, 249 referenced) | cross-document reconciliation, the financial form of data matching; access granted, documents will be given in context | 0 | CC BY-SA 4.0 (gated) |
| 30 | TAT-QA | 16,552 questions over financial reports mixing tables and text; span, multi-span, count and arithmetic answers | mixed answer types and unit/scale handling, the stress test for the numeric components | 5 (3) | CC BY 4.0 |
| 31 | OfficeQA (full, closed-book) | the earlier OfficeQA set answered without documents | already answered by four models; kept for continuity, excluded from the objective because every model is at floor | 1 (1) | Apache-2.0 |

Dropped from the earlier suite by the ranking: FinQA (rank 36) and FinanceBench (rank 56, NC rows).

## E. Why the suite looks like this
* Twelve entity-matching and six schema-matching sets, because those are the tasks the benchmark is named for and they were absent from v1–v4.
* Eleven table sets, chosen so that hierarchy (HiTab, RealHiTBench), structure (SUC, TabIS), free-form (FeTaQA), boolean (TabFact), SQL (BIRD) and multilingual (TableEval) are each covered.
* Saturated classics are kept only where they serve as a sanity check (DBLP-ACM) or a canonical comparison point (TabFact, WTQ).
* Every set has a public download except OfficeQA Pro V2 (gated, access granted). Non-commercial licences (RealHiTBench, OpenSanctions, TPC-DI spec) are fine for the paper but must be stated.

## F. Pre-run review, in plain language (full table in `PRE_RUN_REVIEW.md`)

**Why decoding settings matter.** Models add randomness when they answer; at the provider default (temperature 1.0) the same question can get a different answer on a different day. With four models and 40 items, a handful of flipped answers can swap second and third place, so a reader who repeats the experiment may get a different ranking. Temperature 0 makes each model give its most likely answer every time. Answering a 100-item subset three times gives one number for the paper, "agreement between repeated runs was X %", which is the only defence against "how much of your ranking is noise?". Reasoning models ignore temperature, which is another reason to measure it.

**Item counts.** Old pools have 40 answered items, new pools 150. Beyond the cost surprise, item count sets how precise each dataset score is: at 40 items a 70 % score is really "55 to 85 %"; at 100 it is "61 to 79 %". That is the difference between "looks different" and "is different".

**Entity-matching balance.** The pools are half matches, half non-matches; the published test splits are 10–20 % matches. The balance is a defensible benchmark choice (it stops "always no" from scoring 85 %), but the numbers are then not comparable to published F1, so the paper must report positive-class F1, the majority baseline, and the ratio.

**Winner's curse.** Trying 100 weightings and keeping the best mixes real signal with luck that fits these particular items; a confidence interval computed on the same items cannot see the luck. Choosing on one half of the items and measuring on the other half gives an honest, usually slightly lower, number.

**Floor datasets.** When every model scores zero on a dataset, the code records "zero agreement" and the dataset drags the objective down instead of being ignored. OfficeQA closed-book is the case; it is excluded from the objective and OfficeQA Pro V2 runs with its documents.

**Limitations to state, not fix.** Four models give Kendall τ only seven possible values; the v2/v4 objective measures consistency between datasets, not correctness (v5's anchors measure correctness); v5's anchors are lexical perturbations judged by lexical metrics; only 100 of a large lattice is searched (Latin hypercube and all 255 view subsets in v6); bootstraps resample items only; datasets are equally weighted regardless of family; answer extraction is heuristic.

## G. Decisions still open before the run
1. Items per dataset: 40 (≈ USD 45–50 on the four cached models), 100 (recommended, ≈ USD 110), or 150 (≈ USD 170).
2. Temperature 0 everywhere (recommended) or provider defaults with three samples per item.
3. Family-balanced pooling as headline or as a secondary table.
