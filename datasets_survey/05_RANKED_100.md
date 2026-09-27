# The 100 datasets, ranked 1–100 by importance for an LLM data-matching benchmark

Importance = 100 × Σ weight × sub-score/5 with weights R .25 (relevance), A .15 (adoption), G .15 (generalisation), D .15 (discriminative today), C .10 (gold/metric clarity), I .10 (inclusivity), L .10 (licence/access). Sub-scores 0–5 are in `ranked_100.csv`; rubric in `00_SCORING_RUBRIC.md`. 111 candidates were scored; the 11 lowest were dropped (FinDER, Finance Agent Benchmark, Fodors-Zagats, DA-Code / DSBench, Cora, LakeBench, TabMWP, Febrl 1-4, Spider 1.0, OAEI SPIMBENCH / KG track, WikiSQL).

| # | Dataset | Family | Coverage family | Domain | Answer type | Licence | Imp. | R | A | G | D | C | I | L | Why here |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Magneto GDC-SM | schema / data integration | DI-schema/join | biomedical schema harmonisation | column mapping | CC BY 4.0 | **90.0** | 5 | 3 | 5 | 5 | 5 | 3 | 5 | real harmonisation; many-to-one; value vocab |
| 2 | MMTU | table QA & understanding | TQA-general | 52 datasets 25 data-management tasks | mixed | MIT | **89.0** | 5 | 4 | 5 | 5 | 4 | 2 | 5 | omnibus incl. schema/entity subtasks; GPT-5 0.70 |
| 3 | Valentine | schema / data integration | DI-schema/join | schema matching (TPC-DI OpenData ChEMBL) | column pairs | Apache-2.0 code | **89.0** | 5 | 5 | 5 | 4 | 5 | 2 | 4 | de-facto schema-matching benchmark for LLM papers |
| 4 | WDC Products 2024 (hard negatives) | entity matching | EM-products | products web | boolean | unstated | **87.0** | 5 | 5 | 4 | 5 | 5 | 2 | 3 | best-designed modern product EM; hard negatives; LLM F1 ~0.9 |
| 5 | HiTab | table QA & understanding | TQA-hierarchical/multi | statistical reports hierarchical | span/number | C-UDA 1.0 | **86.0** | 5 | 5 | 4 | 4 | 4 | 3 | 4 | best real statistical tables; hierarchy |
| 6 | Machamp (7 GEM tasks) | entity matching | EM-products | products bib restaurants books movies | boolean | BSD-3 / CC terms | **86.0** | 5 | 4 | 5 | 4 | 4 | 3 | 4 | schema-heterogeneous matching (struct vs text) |
| 7 | Abt-Buy | entity matching | EM-products | products textual | boolean | CC BY 4.0 | **85.0** | 5 | 5 | 3 | 4 | 5 | 2 | 5 | canonical textual EM; not saturated |
| 8 | Amazon-Google | entity matching | EM-products | software products | boolean | CC BY 4.0 | **85.0** | 5 | 5 | 3 | 4 | 5 | 2 | 5 | canonical; PLM F1 ~0.75 |
| 9 | Walmart-Amazon (+dirty) | entity matching | EM-products | electronics | boolean | academic (Magellan) | **83.0** | 5 | 5 | 3 | 4 | 5 | 2 | 4 | standard product task with headroom |
| 10 | DBLP-Scholar (+dirty) | entity matching | EM-bibliographic | bibliographic | boolean | CC BY 4.0 | **82.0** | 5 | 5 | 3 | 3 | 5 | 2 | 5 | canonical bibliographic |
| 11 | Papadakis-Christen Dn1-Dn8 | entity matching | EM-other | products bibliographic movies | boolean | unstated (Zenodo) | **81.0** | 5 | 3 | 4 | 5 | 4 | 2 | 4 | realistic imbalance; corrects saturation of classics |
| 12 | RealHiTBench | table QA & understanding | TQA-hierarchical/multi | 24 domains hierarchical | mixed | CC BY-NC 4.0 data | **80.0** | 5 | 3 | 5 | 5 | 3 | 3 | 2 | purpose-built header-hierarchy matching |
| 13 | FinTagging (FinNI+FinCL) | schema / data integration | DI-schema/join | 10-K XBRL concept linking | label/number | unstated | **79.0** | 5 | 2 | 5 | 5 | 4 | 2 | 3 | taxonomy alignment; FinCL acc ~0.17 |
| 14 | SUC (Table Meets LLM) | table QA & understanding | TQA-general | structural probes cell lookup | cell | unstated | **79.0** | 5 | 3 | 4 | 5 | 4 | 2 | 3 | purest data-reading probe |
| 15 | OfficeQA Pro V2 | financial document QA | FIN-document | Receipts/Outlays 1793-2024 multi-doc | numeric | CC BY-SA gated | **78.0** | 5 | 3 | 5 | 5 | 4 | 2 | 1 | cross-document reconciliation; gated; 90 Qs |
| 16 | Alaska Camera (SIGMOD 2020) | entity matching | EM-products | camera specs 24 sources | cluster/boolean | MIT | **78.0** | 5 | 3 | 4 | 4 | 3 | 2 | 5 | schema-agnostic messy web specs; SM + ER gold |
| 17 | Alaska schema-matching GT | schema / data integration | DI-schema/join | product attribute mapping (687-1026 mappings) | column pairs | MIT | **78.0** | 5 | 3 | 4 | 4 | 3 | 2 | 5 | thousands of heterogeneous attribute names |
| 18 | WikiTableQuestions | table QA & understanding | TQA-general | Wikipedia tables | short/number/list | CC BY-SA 4.0 | **78.0** | 4 | 5 | 3 | 4 | 4 | 2 | 5 | canonical single-table QA; typed evaluator; ~75 % |
| 19 | TabIS | table QA & understanding | TQA-general | information seeking with distractor tables | binary choice | unstated | **76.0** | 5 | 2 | 4 | 5 | 4 | 2 | 3 | hard negatives across tables |
| 20 | SMAT (MIMIC Synthea CMS to OMOP) | schema / data integration | DI-schema/join | healthcare schema matching | column pairs | unstated | **76.0** | 5 | 3 | 4 | 4 | 3 | 3 | 3 | real healthcare schemas |
| 21 | OpenSanctions Pairs | entity matching | EM-people/org | people and organisations 45 jurisdictions | boolean | CC BY-NC 4.0 | **76.0** | 5 | 2 | 5 | 2 | 5 | 5 | 2 | only large real person/org set; multilingual names; near ceiling |
| 22 | TableBench | table QA & understanding | TQA-general | mixed analysis+viz | number/text/code | Apache-2.0 | **76.0** | 4 | 4 | 4 | 4 | 3 | 2 | 5 | hard TableQA leaderboard |
| 23 | TableEval | table QA & understanding | TQA-freeform | zh/en nested spreadsheets | free-form | Apache-2.0 | **76.0** | 4 | 2 | 4 | 4 | 3 | 5 | 5 | multilingual realistic spreadsheets |
| 24 | Jellyfish DP tasks (ED DI SM EM) | schema / data integration | DI-other | mixed data preprocessing | boolean/value | CC BY 4.0 | **75.0** | 4 | 4 | 4 | 3 | 4 | 2 | 5 | LLM-era DP suite in one format |
| 25 | TAT-QA | table QA & understanding | TQA-financial | financial hybrid | span/multi-span/number/count | CC BY 4.0 | **75.0** | 4 | 5 | 3 | 3 | 4 | 2 | 5 | mixed answer types; scale handling |
| 26 | SciTab | table QA & understanding | TQA-verification | paper tables claims | 3-way | unstated | **74.0** | 4 | 3 | 4 | 5 | 4 | 2 | 3 | expert numeric claims |
| 27 | SOTAB V2 | schema / data integration | DI-schema/join | Schema.org web tables CTA/CPA | label | unstated | **74.0** | 4 | 4 | 4 | 4 | 4 | 2 | 3 | format-heterogeneity splits |
| 28 | SemTab 2025 (MammoTab Secu-table) | schema / data integration | DI-annotation | cell entity/column type annotation | label | unstated | **74.0** | 4 | 4 | 4 | 4 | 4 | 2 | 3 | canonical STI venue; NIL cells |
| 29 | TPC-DI (cell-level task) | schema / data integration | DI-schema/join | brokerage ETL join+aggregate | numeric/list | CC BY-NC-ND spec | **73.0** | 5 | 3 | 4 | 3 | 5 | 2 | 2 | the benchmark's own task; mapping spec is gold |
| 30 | BIRD | table QA & understanding | TQA-sql | 95 SQL DBs dirty values | SQL | CC BY-SA 4.0 | **73.0** | 3 | 5 | 3 | 4 | 4 | 2 | 5 | value-grounded SQL; 82 vs 93 human |
| 31 | Spider 2.0 | table QA & understanding | TQA-sql | enterprise SQL 3000+ columns | SQL/result | MIT | **73.0** | 3 | 4 | 4 | 4 | 4 | 2 | 5 | schema-scale; agent-dominated |
| 32 | Auto-Join | schema / data integration | DI-schema/join | join-key transformations | join result | MSR research licence | **72.0** | 5 | 3 | 4 | 4 | 3 | 2 | 2 | join-key reconciliation; 31 cases |
| 33 | WDC LSPC / Products-2017 | entity matching | EM-products | products 4 categories | boolean | Common Crawl terms | **72.0** | 5 | 4 | 2 | 3 | 4 | 2 | 4 | standard web-product benchmark; superseded by WDC 2024 |
| 34 | RobuT | table QA & understanding | TQA-general | perturbed WTQ/WikiSQL/SQA | short/cell | unstated | **71.0** | 4 | 3 | 4 | 4 | 4 | 2 | 3 | reading robustness |
| 35 | TabFact | table QA & understanding | TQA-verification | Wikipedia tables boolean | boolean | CC BY 4.0 | **71.0** | 4 | 5 | 2 | 2 | 5 | 2 | 5 | boolean table anchor; ~90 % |
| 36 | FeTaQA | table QA & understanding | TQA-freeform | Wikipedia free-form | sentence | CC BY-SA 4.0 | **71.0** | 3 | 5 | 4 | 3 | 3 | 2 | 5 | the free-form anchor |
| 37 | AIT-QA | table QA & understanding | TQA-hierarchical/multi | airline 10-K hierarchical | cell value | unstated | **70.0** | 5 | 3 | 3 | 3 | 4 | 2 | 3 | pure cell-location on SEC tables; small |
| 38 | DBLP-ACM (+dirty) | entity matching | EM-bibliographic | bibliographic | boolean | CC BY 4.0 | **70.0** | 5 | 5 | 1 | 1 | 5 | 2 | 5 | near solved; sanity check |
| 39 | FinanceBench (150 open) | financial document QA | FIN-document | 10-K/10-Q with evidence | numeric/text/free-form | CC BY-NC 4.0 | **70.0** | 4 | 5 | 3 | 4 | 3 | 2 | 2 | canonical but 150 rows and NC |
| 40 | MultiHiertt | table QA & understanding | TQA-hierarchical/multi | multi-table financial | number/span | MIT | **70.0** | 4 | 4 | 4 | 4 | 3 | 2 | 2 | multi-table hierarchy; Drive-only |
| 41 | FinQA | table QA & understanding | TQA-financial | SEC 10-K table+text | number | MIT | **70.0** | 4 | 5 | 2 | 3 | 3 | 2 | 5 | canonical numeric reasoning; label noise; contaminated |
| 42 | OAEI 2025 ontology tracks | schema / data integration | DI-other | ontology alignment | alignment | mostly open | **70.0** | 3 | 5 | 3 | 3 | 4 | 4 | 3 | 20-year canon; ontology-centric |
| 43 | BizBench (SEC-Num etc.) | financial document QA | FIN-document | finance program QA + quantity extraction | number | Apache-2.0 | **69.0** | 4 | 3 | 3 | 3 | 4 | 2 | 5 | SEC-Num extraction subtask |
| 44 | MusicBrainz 20K | entity matching | EM-other | music multi-source | cluster | CC BY 4.0 | **69.0** | 4 | 3 | 3 | 3 | 3 | 3 | 5 | multi-source clustering; synthetic corruptions |
| 45 | MiMoTable | table QA & understanding | TQA-hierarchical/multi | zh/en multi-sheet | mixed | unstated | **68.0** | 4 | 2 | 4 | 4 | 3 | 5 | 1 | multi-sheet; download unverified |
| 46 | TyDi QA GoldP | answer-type anchor | ANC-multilingual | 11 languages natural questions | span/yes-no/null | Apache 2.0 | **68.0** | 2 | 4 | 3 | 3 | 4 | 5 | 5 | non-translated multilingual |
| 47 | MMQA (multi-table PK/FK) | table QA & understanding | TQA-sql | Spider-derived multi-table | answer+SQL+keys | unstated | **67.0** | 5 | 2 | 4 | 4 | 3 | 2 | 1 | foreign-key discovery; unverified download |
| 48 | OfficeQA Pro/Full | financial document QA | FIN-document | Treasury Bulletins 697 docs | numeric | CC BY-SA gated | **67.0** | 4 | 3 | 3 | 5 | 4 | 2 | 1 | long-doc numeric grounding; gated |
| 49 | Alaska Monitor/Notebook | entity matching | EM-products | monitor and notebook specs | cluster | MIT | **67.0** | 4 | 3 | 2 | 4 | 3 | 2 | 5 | as Alaska camera |
| 50 | Cross-dataset EM study (11 sets LODO) | entity matching | EM-other | mixed | boolean | inherits | **67.0** | 4 | 3 | 3 | 3 | 4 | 2 | 4 | protocol for zero-shot LLM EM |
| 51 | FEVEROUS | table QA & understanding | TQA-verification | text+table claims with evidence cells | 3-way+cells | CC BY-SA 3.0 | **67.0** | 3 | 4 | 3 | 3 | 4 | 2 | 5 | evidence-cell retrieval |
| 52 | Raha/Baran error detection collection | schema / data integration | DI-cleaning | hospital flights beers rayyan tax | cell label | Apache-2.0 | **67.0** | 3 | 4 | 3 | 3 | 4 | 2 | 5 | de-facto error-detection benchmark |
| 53 | DROP | answer-type anchor | ANC-numeric | typed numeric/date/span | number/date/spans | CC BY-SA 4.0 | **67.0** | 2 | 5 | 3 | 3 | 5 | 2 | 5 | typed official evaluator |
| 54 | OpenEA (DBP15K DWY100K) | entity matching | EM-other | KG entity alignment cross-lingual | alignment | GPL-3.0 | **67.0** | 2 | 5 | 3 | 3 | 4 | 5 | 3 | KG alignment not tabular |
| 55 | MGSM | answer-type anchor | ANC-numeric | multilingual numeric 11 langs | number | CC BY-SA 4.0 | **67.0** | 2 | 4 | 3 | 2 | 5 | 5 | 5 | locale number formats |
| 56 | HybridQA | table QA & understanding | TQA-general | table+linked passages | short span | unstated | **66.0** | 3 | 5 | 3 | 3 | 4 | 2 | 3 | cell to passage joining |
| 57 | WMT MQM | human-label meta-evaluation | META | segment-level MQM | scores | Apache 2.0 | **66.0** | 1 | 5 | 3 | 3 | 5 | 4 | 5 | gold-standard human labels |
| 58 | Beer (BeerAdvo-RateBeer) | entity matching | EM-other | beverages | boolean | Magellan | **65.0** | 4 | 4 | 2 | 3 | 3 | 2 | 4 | low-resource probe |
| 59 | Company | entity matching | EM-other | companies long text | boolean | Magellan | **65.0** | 4 | 3 | 3 | 3 | 3 | 2 | 4 | only long-text EM |
| 60 | DocFinQA | table QA & understanding | TQA-financial | full 10-K long context | number | MIT | **65.0** | 3 | 3 | 3 | 4 | 3 | 2 | 5 | 123k-word contexts; costly |
| 61 | DocMath-Eval | financial document QA | FIN-document | long financial docs with tables | number | MIT (unv.) | **65.0** | 3 | 3 | 3 | 4 | 3 | 2 | 5 | complong multi-table |
| 62 | QAMPARI | answer-type anchor | ANC-list/table | list answers | entity list | CC0 | **65.0** | 2 | 3 | 4 | 4 | 4 | 2 | 5 | cleanest list anchor |
| 63 | North Carolina Voters 5M | entity matching | EM-people/org | people synthetic errors | cluster | CC BY 4.0 | **64.0** | 4 | 3 | 3 | 2 | 3 | 2 | 5 | only large person benchmark; synthetic |
| 64 | iTunes-Amazon (+dirty) | entity matching | EM-other | music | boolean | Magellan | **64.0** | 4 | 4 | 2 | 2 | 4 | 2 | 4 | small non-product task |
| 65 | MultiTabQA | answer-type anchor | ANC-list/table | table-valued answers | table | MIT | **64.0** | 3 | 2 | 4 | 3 | 4 | 2 | 5 | only graded table-EM metric |
| 66 | DataBench (SemEval 2025) | table QA & understanding | TQA-general | real CSVs typed answers | bool/number/category/list | MIT | **64.0** | 3 | 4 | 3 | 2 | 4 | 2 | 5 | saturated with code |
| 67 | SANTOS | schema / data integration | DI-discovery | open-data table union search | table set | CC BY 4.0 | **64.0** | 3 | 4 | 3 | 2 | 3 | 3 | 5 | discovery; lexical baselines saturate |
| 68 | VitaminC | answer-type anchor | ANC-boolean | contrastive claims small edits | 3-way | CC BY-SA 3.0 | **64.0** | 2 | 3 | 4 | 3 | 5 | 2 | 5 | numeric-edit sensitivity |
| 69 | IMDB-TMDB/TVDB (MovieGraphBenchmark) | entity matching | EM-other | movies | boolean | MIT code; IMDB rebuilt | **63.0** | 4 | 3 | 3 | 3 | 3 | 2 | 3 | non-product domain |
| 70 | EMBer (multimodal EM) | entity matching | EM-products | products text+images | boolean | unstated | **63.0** | 3 | 2 | 4 | 4 | 3 | 3 | 3 | only multimodal EM |
| 71 | Geographic Settlements | entity matching | EM-other | geographic multilingual names | cluster | CC BY 4.0 | **63.0** | 3 | 2 | 3 | 3 | 3 | 4 | 5 | small geo task |
| 72 | FinAuditing | schema / data integration | DI-schema/join | multi-doc XBRL consistency | label | unstated | **62.0** | 4 | 2 | 4 | 4 | 2 | 2 | 2 | cross-statement linkage (unverified details) |
| 73 | TempTabQA | table QA & understanding | TQA-general | infobox temporal | span/number | unstated | **62.0** | 3 | 2 | 3 | 4 | 4 | 2 | 4 | temporal arithmetic |
| 74 | ConvFinQA | table QA & understanding | TQA-financial | conversational finance | number | MIT | **62.0** | 3 | 4 | 2 | 3 | 3 | 2 | 5 | dialogue chaining |
| 75 | lm-dw / BIG-bench data wrangling | schema / data integration | DI-other | string wrangling by example | string | unstated | **62.0** | 3 | 3 | 3 | 3 | 4 | 3 | 3 | format normalisation |
| 76 | NarrativeQA | answer-type anchor | ANC-span/freeform | free-form with 2 references | short free-form | Apache 2.0 | **62.0** | 2 | 4 | 3 | 3 | 4 | 2 | 5 | paraphrase tolerance |
| 77 | MLQA | answer-type anchor | ANC-multilingual | 7 languages spans | span | CC BY-SA 3.0 | **62.0** | 2 | 4 | 2 | 2 | 4 | 5 | 5 | per-language normalisation |
| 78 | SummEval | human-label meta-evaluation | META | human Likert on summaries | ratings | MIT | **62.0** | 1 | 5 | 3 | 3 | 5 | 2 | 5 | validate scorer vs humans |
| 79 | GitTables CTA | schema / data integration | DI-annotation | GitHub CSVs | label | CC0 vs CC BY (conflict) | **61.0** | 3 | 4 | 3 | 3 | 2 | 2 | 4 | weak automatic labels |
| 80 | InfoTabs | table QA & understanding | TQA-verification | infobox NLI | 3-way | Apache-2.0 | **61.0** | 3 | 3 | 2 | 3 | 4 | 2 | 5 | key-value reading |
| 81 | TAT-DQA | financial document QA | FIN-document | financial PDF pages | span/number | CC BY 4.0 | **61.0** | 3 | 3 | 2 | 3 | 4 | 2 | 5 | document-image variant |
| 82 | T2Dv2 | schema / data integration | DI-annotation | web tables to DBpedia | label | Apache | **61.0** | 3 | 4 | 2 | 2 | 4 | 2 | 5 | older canon; small |
| 83 | FinanceMath | financial document QA | FIN-document | finance textbook numeric | float 3dp | MIT | **61.0** | 2 | 3 | 2 | 4 | 5 | 2 | 5 | rounding convention; knowledge not documents |
| 84 | ChartQA | financial document QA | FIN-document | charts | numeric/text | GPL-3.0 | **61.0** | 2 | 5 | 3 | 3 | 4 | 2 | 3 | reading values off charts; GPL |
| 85 | EDGAR-CORPUS | financial document QA | FIN-document | 220k 10-Ks raw | corpus | Apache-2.0 | **61.0** | 2 | 4 | 4 | 3 | 2 | 2 | 5 | source for synthesising matching tasks |
| 86 | SECQUE | financial document QA | FIN-document | SEC filings expert analysis | free-text | CC BY 4.0 | **60.0** | 3 | 2 | 3 | 4 | 2 | 2 | 5 | cross-filing comparison; judged |
| 87 | HoloClean datasets | schema / data integration | DI-cleaning | hospital flights food physicians | cell repair | Apache-2.0 (unv.) | **60.0** | 3 | 4 | 2 | 3 | 3 | 2 | 4 | canonical cleaning sets |
| 88 | SQA | table QA & understanding | TQA-general | conversational cell selection | cell coordinates | MSR licence | **59.0** | 4 | 4 | 2 | 1 | 4 | 2 | 3 | cell coordinates; easy |
| 89 | TUS Small/Large | schema / data integration | DI-discovery | Canadian open data union search | table set | unstated | **59.0** | 3 | 4 | 2 | 2 | 3 | 3 | 4 | standard TUS; noisy GT |
| 90 | MP-DocVQA | financial document QA | FIN-document | multi-page document images | span+page | MIT | **59.0** | 2 | 3 | 3 | 3 | 4 | 2 | 5 | page finding; vision |
| 91 | JudgeBench | human-label meta-evaluation | META | objective pairwise correctness | A>B | MIT | **59.0** | 1 | 3 | 3 | 4 | 5 | 2 | 5 | objective judge labels |
| 92 | LLMBar | human-label meta-evaluation | META | adversarial pairwise | A>B | MIT | **59.0** | 1 | 3 | 3 | 4 | 5 | 2 | 5 | superficial-quality traps |
| 93 | TRUE | human-label meta-evaluation | META | 11 factuality sets unified | binary | Apache 2.0 | **59.0** | 1 | 4 | 3 | 3 | 5 | 2 | 5 | binary + ROC-AUC protocol |
| 94 | TURL WikiTables CTA/CPA | schema / data integration | DI-annotation | Wikipedia tables | label | unstated | **58.0** | 3 | 4 | 2 | 3 | 3 | 2 | 3 | long-tail types |
| 95 | TriviaQA | answer-type anchor | ANC-span/freeform | entity with alias lists | entity | unknown | **58.0** | 2 | 5 | 3 | 2 | 5 | 2 | 2 | alias-list anchor |
| 96 | BoolQ | answer-type anchor | ANC-boolean | yes/no with passage | boolean | CC BY-SA 3.0 | **58.0** | 2 | 5 | 2 | 1 | 5 | 2 | 5 | boolean anchor; saturated |
| 97 | GSM8K (Platinum) | answer-type anchor | ANC-numeric | grade-school numeric | number | MIT | **58.0** | 2 | 5 | 2 | 1 | 5 | 2 | 5 | clean numeric EM anchor; saturated |
| 98 | SQuAD 2.0 | answer-type anchor | ANC-span/freeform | extractive span + no-answer | span | CC BY-SA 4.0 | **58.0** | 2 | 5 | 2 | 1 | 5 | 2 | 5 | EM/F1 script standard |
| 99 | CRT-QA | table QA & understanding | TQA-general | WTQ with unanswerable | short/unanswerable | unstated | **57.0** | 3 | 2 | 3 | 3 | 3 | 2 | 4 | abstention probe |
| 100 | PubHealthTab | table QA & understanding | TQA-verification | public-health web tables | 3-way | unstated | **57.0** | 3 | 2 | 3 | 3 | 3 | 3 | 3 | messy scraped tables |

Family counts in the 100: schema / data integration 20, table QA & understanding 30, entity matching 22, financial document QA 11, answer-type anchor 12, human-label meta-evaluation 5.

Reading the scores: R dominates by design (a dataset that is not about matching or reading structured data cannot rank high however famous); A rewards canon status; G rewards a new domain/modality/answer type; D penalises saturated sets (WikiSQL, Spider 1.0, TabMWP, DBLP-ACM) and floor sets; I lifts multilingual or non-Western sources (TableEval, MiMoTable, OpenSanctions, MGSM, TyDi); L penalises gated, NC or unlocated data (OfficeQA, FinanceBench, RealHiTBench data, MMQA).
