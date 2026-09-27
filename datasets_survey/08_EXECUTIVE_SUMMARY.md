# Dataset survey: executive summary

Scope: 231 candidate datasets surveyed across four families (entity matching 44, table QA 60, financial documents + data integration 70, answer-type anchors and human-label meta-evaluation 65) with web verification of availability and licence on 2026-09-14; 111 finalists scored on a seven-criterion rubric (`00_SCORING_RUBRIC.md`); the 100 highest form the ranked list (`05_RANKED_100.md`, machine-readable `ranked_100.csv`); coverage-constrained groups of 5/10/20/25/30/40/50 are in `06_GROUPINGS.md`; per-version fits and groups in `07_PER_VERSION_FIT.md`; every URL in `09_SOURCES.md`. The ranking is reproducible: `python3 rank.py` regenerates all three outputs from `candidates.csv`.

## Evidence-based revision (primary result)

After the judgement survey, the adoption criterion was re-computed from a citation-ranked corpus of 105 core + ≈115 supplementary papers across entity/schema matching, table QA / text-to-SQL, financial-document QA and LLM evaluation (`10_PAPER_CORPUS.md`; counts in `paper_usage.csv`). Each dataset's A is now a function of how many of those papers evaluate on it, with a recency term for 2023+ use. Spearman ρ with the judgement ranking is 0.88; details and the largest moves in `11_EVIDENCE_VS_JUDGEMENT.md`. Outputs: `05_RANKED_100_evidence.md`, `06_GROUPINGS_evidence.md`, `07_PER_VERSION_FIT_evidence.md`, `ranked_100_evidence.csv`. These are the lists to cite; the judgement lists below remain as the forward-looking variant.

Evidence top 10:

| # | Dataset | Coverage family | Papers (2023+) | Imp. |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 17 (8) | 85.0 |
| 2 | Amazon-Google | EM-products | 21 (11) | 85.0 |
| 3 | Magneto GDC-SM | DI-schema/join | 1 (1) | 84.6 |
| 4 | Walmart-Amazon (+dirty) | EM-products | 19 (11) | 83.0 |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 21 (11) | 82.0 |
| 6 | HiTab | TQA-hierarchical/multi | 5 (4) | 81.1 |
| 7 | Valentine | DI-schema/join | 3 (2) | 81.1 |
| 8 | MMTU | TQA-general | 1 (1) | 80.6 |
| 9 | Machamp (7 GEM tasks) | EM-products | 2 (0) | 78.6 |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 6 (5) | 78.4 |

Evidence group lists (coverage-constrained, top half by importance guaranteed): **5** = Abt-Buy, Amazon-Google, Magneto GDC-SM, HiTab, Valentine; **10** adds Walmart-Amazon, DBLP-Scholar, MMTU, OfficeQA Pro V2 (financial-document quota), TAT-QA; **20** adds Machamp, SMAT, WTQ, RealHiTBench, TableEval, OpenSanctions, TabFact, DROP, SemTab 2025, BizBench; **25** adds WDC Products 2024, FinTagging, Papadakis-Christen, DocFinQA, VitaminC; **30** adds Alaska Camera, BIRD, AIT-QA, TyDi QA, Raha; **40** and **50** add the second representatives per family (DBLP-ACM, Beer, iTunes-Amazon, FeTaQA, FinQA, SciTab, SUC, TabIS, MGSM, MLQA, QAMPARI, SANTOS, T2Dv2, MiMoTable, FinanceBench, NC Voters, NarrativeQA, TPC-DI).

Per version (evidence): v1/v2 top 5 = HiTab, MMTU, WTQ, RealHiTBench, TPC-DI; v3 top 5 = Abt-Buy, Amazon-Google, Magneto, HiTab, Valentine; v4 and v5 top 5 = Abt-Buy, Amazon-Google, Walmart-Amazon, HiTab, MMTU (v5 adds anchors and meta-evaluation from 20 upward).

What the corpus changed: the Magellan product and bibliographic sets are not legacy (17–21 uses each, half of them 2023+), so they move into the top 5; the newest sets (WDC Products 2024, TabIS, SUC, Alaska) keep high relevance and difficulty scores but lose adoption and move to 12–20; DocFinQA, iTunes-Amazon and Beer rise 24–28 places; sets with no use in the corpus (Auto-Join, OpenEA, NC Voters, lm-dw) fall 20–40 places.

## Top 10 overall (judgement-based, original survey)

| # | Dataset | Family | Imp. | One-line reason |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | real harmonisation; many-to-one; value vocab |
| 2 | MMTU | TQA-general | 89.0 | omnibus incl. schema/entity subtasks; GPT-5 0.70 |
| 3 | Valentine | DI-schema/join | 89.0 | de-facto schema-matching benchmark for LLM papers |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | best-designed modern product EM; hard negatives; LLM F1 ~0.9 |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | best real statistical tables; hierarchy |
| 6 | Machamp (7 GEM tasks) | EM-products | 86.0 | schema-heterogeneous matching (struct vs text) |
| 7 | Abt-Buy | EM-products | 85.0 | canonical textual EM; not saturated |
| 8 | Amazon-Google | EM-products | 85.0 | canonical; PLM F1 ~0.75 |
| 9 | Walmart-Amazon (+dirty) | EM-products | 83.0 | standard product task with headroom |
| 10 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | canonical bibliographic |

## Findings that shape the ranking

1. **The benchmark's name is under-served by its own suite.** Entity matching and schema matching, the two families that *are* data matching, were absent from v1–v4's original catalogue. Modern sets exist: WDC Products 2024 (hard negatives), the Magellan classics that remain unsaturated (Abt-Buy, Amazon-Google, Walmart-Amazon), Machamp (schema-heterogeneous matching), Papadakis–Christen's re-balanced sets, and for schema matching Valentine (de-facto standard) and Magneto GDC-SM (real biomedical harmonisation, CC BY 4.0). These take 9 of the top 20 slots.
2. **Several classics are saturated and should be demoted or dropped**: WikiSQL, Spider 1.0, TabMWP, DBLP-ACM, Fodors-Zagats, Febrl, SQA (all D ≤ 1). They remain useful only as smoke tests.
3. **The hard, current table sets are hierarchical and multi-table**: HiTab, RealHiTBench, MMTU (omnibus with schema/entity subtasks; GPT-5 ≈ 0.70), SUC and TabIS (structural probes LLMs fail), MultiHiertt, TableEval (zh/en spreadsheets). WTQ stays because it is canonical, typed-metric and still ~75 %.
4. **Financial documents**: the matching flavour lives in the 2025–26 wave (OfficeQA Pro V2 cross-document reconciliation, FinTagging concept linking with FinCL ≈ 0.17, FinAuditing), but licensing is the obstacle: OfficeQA is gated, FinanceBench exposes 150 NC rows, FinDER is NC. DocFinQA (MIT) and BizBench SEC-Num (Apache) are the open long-document options.
5. **Inclusivity gap**: no canonical multilingual table-QA benchmark exists. TableEval and MiMoTable (zh/en), OpenSanctions Pairs (45 jurisdictions, multilingual names), MGSM, TyDi QA and MLQA are the available levers; the paper should state the gap.
6. **Anchors and meta-evaluation matter only for v5**: GSM8K-Platinum, DROP (typed evaluator), BoolQ, SQuAD 2.0, TriviaQA (aliases), QAMPARI (lists), NarrativeQA (two references), VitaminC (numeric-edit sensitivity); and SummEval / TRUE / WMT MQM / JudgeBench for validating the scorer against human labels.

## How the judgement groups differ by size (see 06_GROUPINGS.md)

* **5**: one each of schema matching (Magneto), omnibus table understanding (MMTU), product matching (WDC 2024), hierarchical tables (HiTab), plus Valentine as the second schema-matching quota entry.
* **10**: adds Machamp, Abt-Buy, DBLP-Scholar (the entity-matching core) and the two financial quota entries, OfficeQA Pro V2 and TAT-QA.
* **20**: adds Amazon-Google, Walmart-Amazon, RealHiTBench, SUC, TableEval, SciTab, OpenSanctions (people/org), SemTab, FinanceBench and the first anchor (DROP).
* **25–30**: add Papadakis–Christen, FinTagging, FinQA, TyDi QA, VitaminC, Alaska Camera, BIRD, AIT-QA, error detection (Raha) and the first meta-evaluation set (WMT MQM).
* **40–50**: add second representatives per family (Alaska schema GT, WTQ, TabIS, SMAT, TabFact, DBLP-ACM, BizBench, MusicBrainz, MGSM, DocFinQA, SANTOS, GitTables, TableBench, Jellyfish, FeTaQA, MultiHiertt, OfficeQA Pro/Full, the cross-dataset EM study, QAMPARI, NC Voters, NarrativeQA, MLQA).

## Per-version recommendation in one line each (details in 07_PER_VERSION_FIT.md)

* v1/v2 (fixed 4-metric composite): only short-answer table and financial QA fit; top-5 = HiTab, WTQ, TAT-QA, TabFact, FinQA-class sets; entity matching enters only as yes/no items.
* v3 (native metrics + aggregation views): the broadest fit; use the global top lists directly, entity matching and schema matching included, because each dataset keeps its own metric.
* v4 (9-metric composite): QA-style golds plus entity matching as boolean items; schema matching and SQL need wrappers, so exclude them.
* v5 (100-metric library + anchors): the global lists plus the answer-type anchors and the human-label meta-evaluation sets; this is the only version that can use SummEval/TRUE/JudgeBench.

## Caveats

In the evidence variant the adoption sub-score is a measurement (paper counts); the other six sub-scores are expert judgements on stated criteria; anyone can change a cell in `candidates.csv` and re-run. Twelve entries carry unverified download links or sizes (marked in the family surveys). Frontier saturation levels are as reported in 2025–26 papers and will drift.
