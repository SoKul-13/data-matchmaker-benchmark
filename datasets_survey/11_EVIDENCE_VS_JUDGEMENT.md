# Evidence-based ranking versus judgement-based ranking

The judgement ranking (`05_RANKED_100.md`) scored adoption by expert judgement. The evidence ranking (`05_RANKED_100_evidence.md`) replaces that sub-score with usage counts from the citation-ranked paper corpus (`10_PAPER_CORPUS.md`); the other six criteria and all weights are unchanged. Spearman ρ between the two rankings over the 96 datasets in both top-100 lists: **0.885**. Four datasets swap in (Fodors-Zagats, Spider 1.0, FinDER, Finance Agent Benchmark) for four that drop out (ChartQA, EDGAR-CORPUS, MP-DocVQA, TRUE).

## Top 10 side by side

| # | Evidence-based | papers (2023+) | Imp. | Judgement-based | Imp. |
|---|---|---|---|---|---|
| 1 | Abt-Buy | 17 (8) | 85.0 | Magneto GDC-SM | 90.0 |
| 2 | Amazon-Google | 21 (11) | 85.0 | MMTU | 89.0 |
| 3 | Magneto GDC-SM | 1 (1) | 84.6 | Valentine | 89.0 |
| 4 | Walmart-Amazon (+dirty) | 19 (11) | 83.0 | WDC Products 2024 (hard negatives) | 87.0 |
| 5 | DBLP-Scholar (+dirty) | 21 (11) | 82.0 | HiTab | 86.0 |
| 6 | HiTab | 5 (4) | 81.1 | Machamp (7 GEM tasks) | 86.0 |
| 7 | Valentine | 3 (2) | 81.1 | Abt-Buy | 85.0 |
| 8 | MMTU | 1 (1) | 80.6 | Amazon-Google | 85.0 |
| 9 | Machamp (7 GEM tasks) | 2 (0) | 78.6 | Walmart-Amazon (+dirty) | 83.0 |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | 6 (5) | 78.4 | DBLP-Scholar (+dirty) | 82.0 |

## Largest moves

| Dataset | judgement rank | evidence rank | why |
|---|---|---|---|
| DocFinQA | 60 | 32 | 8 corpus uses through the FinQA lineage; open licence |
| iTunes-Amazon (+dirty) | 64 | 37 | 13 uses; still in half of the LLM-era EM papers |
| Beer (BeerAdvo-RateBeer) | 58 | 34 | 11 uses |
| lm-dw / BIG-bench data wrangling | 75 | 94 | no external use |
| DataBench (SemEval 2025) | 66 | 86 | only its own paper |
| Auto-Join | 32 | 55 | no use in the corpus |
| FinanceBench (150 open) | 39 | 63 | 2 uses; NC rows |
| MultiHiertt | 40 | 64 | 1 use, pre-2023 |
| North Carolina Voters 5M | 63 | 88 | no use in the corpus |
| OAEI 2025 ontology tracks | 42 | 70 | 1 use (Unicorn) |
| OpenEA (DBP15K DWY100K) | 54 | 96 | no use in the corpus (KG alignment is a separate literature) |

## Group overlap (evidence vs judgement lists)

| k | shared | evidence-only | judgement-only |
|---|---|---|---|
| 5 | 3 / 5 | Abt-Buy, Amazon-Google | MMTU, WDC Products 2024 (hard negatives) |
| 10 | 8 / 10 | Amazon-Google, Walmart-Amazon (+dirty) | WDC Products 2024 (hard negatives), Machamp (7 GEM tasks) |
| 20 | 16 / 20 | SMAT (MIMIC Synthea CMS to OMOP), WikiTableQuestions, TabFact, BizBench (SEC-Num etc.) | WDC Products 2024 (hard negatives), SUC (Table Meets LLM), SciTab, FinanceBench (150 open) |
| 25 | 20 / 25 | SMAT (MIMIC Synthea CMS to OMOP), WikiTableQuestions, TabFact, DocFinQA, BizBench (SEC-Num etc.) | SUC (Table Meets LLM), SciTab, FinanceBench (150 open), FinQA, TyDi QA GoldP |
| 30 | 25 / 30 | SMAT (MIMIC Synthea CMS to OMOP), WikiTableQuestions, TabFact, DocFinQA, BizBench (SEC-Num etc.) | SUC (Table Meets LLM), SciTab, FinanceBench (150 open), FinQA, WMT MQM |
| 40 | 37 / 40 | Beer (BeerAdvo-RateBeer), OfficeQA Pro/Full, T2Dv2 | FinanceBench (150 open), MusicBrainz 20K, GitTables CTA |
| 50 | 44 / 50 | BIRD, TPC-DI (cell-level task), Beer (BeerAdvo-RateBeer), iTunes-Amazon (+dirty), MiMoTable, T2Dv2 | TableBench, Jellyfish DP tasks (ED DI SM EM), MultiHiertt, MusicBrainz 20K, Cross-dataset EM study (11 sets LODO), GitTables CTA |

Both lists are built with the same three-pass procedure (top half by importance, coverage quotas, importance fill). At every size, the shared core is 60–90 % of the list; the evidence lists trade the newest sets (WDC Products 2024, Alaska, TabIS, SUC) for the Magellan classics (Amazon-Google, Walmart-Amazon, DBLP-Scholar) at small k and bring in DocFinQA, iTunes-Amazon and Beer at larger k.

## Per-version top lists under evidence (full 5/10/20/25/30/40/50 in `07_PER_VERSION_FIT_evidence.md`)

**v1** — top 5: 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 24. TPC-DI (cell-level task)
top 10: 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 30. TAT-QA

**v2** — top 5: 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 24. TPC-DI (cell-level task)
top 10: 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 30. TAT-QA

**v3** — top 5: 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 6. HiTab; 7. Valentine
top 10: 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 7. Valentine; 8. MMTU; 23. OfficeQA Pro V2; 30. TAT-QA

**v4** — top 5: 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 6. HiTab; 8. MMTU
top 10: 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 23. OfficeQA Pro V2; 30. TAT-QA

**v5** — top 5: 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 6. HiTab; 8. MMTU
top 10: 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 23. OfficeQA Pro V2; 30. TAT-QA

## Reading

* **What survives both methods** is the recommendation itself: schema matching (Magneto, Valentine), the unsaturated Magellan product sets (Abt-Buy, Amazon-Google, Walmart-Amazon), DBLP-Scholar, HiTab and MMTU form the top 10 either way; OfficeQA Pro V2 and TAT-QA enter every top-10 list as the financial-document and financial-table quota entries.
* **Where the methods disagree** is exactly where one would expect: judgement rewards new, well-designed sets before the field has adopted them (WDC Products 2024, TabIS, SUC, Alaska); evidence rewards sets the field has actually standardised on (iTunes-Amazon, Beer, DocFinQA, TabFact, FeTaQA). The paper should report the evidence ranking as primary (it is auditable: every count traces to a listed paper) and cite the judgement ranking as the forward-looking variant.
* **The corpus also settles two open questions from the judgement survey**: (i) the Magellan sets are not legacy; they remain the evaluation standard in 2023–26 LLM matching papers, so the benchmark must include them for comparability; (ii) no multilingual table-QA set has any external use, confirming the inclusivity gap rather than filling it.
* Reproduce: `python3 rank.py` (judgement) and `python3 rank_evidence.py` (evidence); both read `candidates.csv`, the second also `paper_usage.csv`.
