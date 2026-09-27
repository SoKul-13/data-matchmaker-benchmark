# Coverage-constrained groupings (evidence-based adoption): the 5, 10, 20, 25, 30, 40 and 50 most important datasets

Each list is built in three passes: (0) the top ⌈k/2⌉ datasets by importance are always included; (1) fill a coverage quota per family (entity matching by domain, schema/join, annotation, table QA by kind, financial documents, anchors by answer type, multilingual, meta-evaluation) with the highest-ranked members of that family; (2) fill the remaining slots by global importance. Pass 0 guarantees that no dataset ranked in the top half of a list's size can be crowded out by quotas (without it, quota sums close to k made the 40- and 50-lists almost entirely quota-driven). So a lower-ranked dataset can enter a list ahead of a higher-ranked one when it is the only representative of a family the list must cover (inclusivity / representation); this is stated per list as 'quota entries'. The quotas grow with k so that small lists stay focused on the benchmark's core (matching, schema, tables, financial documents) and larger lists add anchors, multilingual sets and human-label meta-evaluation.

## Top 5

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 85.0 | by importance |
| 2 | Amazon-Google | EM-products | 85.0 | by importance |
| 3 | Magneto GDC-SM | DI-schema/join | 84.6 | by importance |
| 6 | HiTab | TQA-hierarchical/multi | 81.1 | quota entry (covers TQA-hierarchical/multi) |
| 7 | Valentine | DI-schema/join | 81.1 | quota entry (covers DI-schema/join) |

Coverage: DI-schema/join 2, EM-products 2, TQA-hierarchical/multi 1.
Multilingual / non-English members: 0. Gated or NC licences to note: none.
Added relative to the previous list: —.

## Top 10

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 85.0 | by importance |
| 2 | Amazon-Google | EM-products | 85.0 | by importance |
| 3 | Magneto GDC-SM | DI-schema/join | 84.6 | by importance |
| 4 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 6 | HiTab | TQA-hierarchical/multi | 81.1 | by importance |
| 7 | Valentine | DI-schema/join | 81.1 | by importance |
| 8 | MMTU | TQA-general | 80.6 | by importance |
| 23 | OfficeQA Pro V2 | FIN-document | 72.0 | quota entry (covers FIN-document) |
| 30 | TAT-QA | TQA-financial | 69.5 | quota entry (covers TQA-financial) |

Coverage: DI-schema/join 2, EM-bibliographic 1, EM-products 3, FIN-document 1, TQA-financial 1, TQA-general 1, TQA-hierarchical/multi 1.
Multilingual / non-English members: 0. Gated or NC licences to note: OfficeQA Pro V2.
Added relative to the previous list: Walmart-Amazon (+dirty), DBLP-Scholar (+dirty), MMTU, OfficeQA Pro V2, TAT-QA.

## Top 20

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 85.0 | by importance |
| 2 | Amazon-Google | EM-products | 85.0 | by importance |
| 3 | Magneto GDC-SM | DI-schema/join | 84.6 | by importance |
| 4 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 6 | HiTab | TQA-hierarchical/multi | 81.1 | by importance |
| 7 | Valentine | DI-schema/join | 81.1 | by importance |
| 8 | MMTU | TQA-general | 80.6 | by importance |
| 9 | Machamp (7 GEM tasks) | EM-products | 78.6 | by importance |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 78.4 | by importance |
| 11 | WikiTableQuestions | TQA-general | 78.0 | by importance |
| 17 | RealHiTBench | TQA-hierarchical/multi | 74.6 | by importance |
| 20 | TableEval | TQA-freeform | 73.6 | by importance; inclusivity |
| 21 | OpenSanctions Pairs | EM-people/org | 73.0 | quota entry (covers EM-people/org); inclusivity |
| 23 | OfficeQA Pro V2 | FIN-document | 72.0 | quota entry (covers FIN-document) |
| 25 | TabFact | TQA-verification | 71.0 | quota entry (covers TQA-verification) |
| 30 | TAT-QA | TQA-financial | 69.5 | quota entry (covers TQA-financial) |
| 38 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |
| 46 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 65.0 | quota entry (covers DI-annotation) |
| 53 | BizBench (SEC-Num etc.) | FIN-document | 63.6 | quota entry (covers FIN-document) |

Coverage: ANC-numeric 1, DI-annotation 1, DI-schema/join 3, EM-bibliographic 1, EM-people/org 1, EM-products 4, FIN-document 2, TQA-financial 1, TQA-freeform 1, TQA-general 2, TQA-hierarchical/multi 2, TQA-verification 1.
Multilingual / non-English members: 2. Gated or NC licences to note: RealHiTBench, OpenSanctions Pairs, OfficeQA Pro V2.
Added relative to the previous list: Machamp (7 GEM tasks), SMAT (MIMIC Synthea CMS to OMOP), WikiTableQuestions, RealHiTBench, TableEval, OpenSanctions Pairs, TabFact, DROP, SemTab 2025 (MammoTab Secu-table), BizBench (SEC-Num etc.).

## Top 25

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 85.0 | by importance |
| 2 | Amazon-Google | EM-products | 85.0 | by importance |
| 3 | Magneto GDC-SM | DI-schema/join | 84.6 | by importance |
| 4 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 6 | HiTab | TQA-hierarchical/multi | 81.1 | by importance |
| 7 | Valentine | DI-schema/join | 81.1 | by importance |
| 8 | MMTU | TQA-general | 80.6 | by importance |
| 9 | Machamp (7 GEM tasks) | EM-products | 78.6 | by importance |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 78.4 | by importance |
| 11 | WikiTableQuestions | TQA-general | 78.0 | by importance |
| 12 | WDC Products 2024 (hard negatives) | EM-products | 77.9 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 76.6 | by importance |
| 14 | Papadakis-Christen Dn1-Dn8 | EM-other | 75.6 | by importance |
| 17 | RealHiTBench | TQA-hierarchical/multi | 74.6 | by importance |
| 20 | TableEval | TQA-freeform | 73.6 | by importance; inclusivity |
| 21 | OpenSanctions Pairs | EM-people/org | 73.0 | by importance; inclusivity |
| 23 | OfficeQA Pro V2 | FIN-document | 72.0 | by importance |
| 25 | TabFact | TQA-verification | 71.0 | by importance |
| 30 | TAT-QA | TQA-financial | 69.5 | quota entry (covers TQA-financial) |
| 32 | DocFinQA | TQA-financial | 68.5 | quota entry (covers TQA-financial) |
| 38 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |
| 46 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 65.0 | quota entry (covers DI-annotation) |
| 51 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |
| 53 | BizBench (SEC-Num etc.) | FIN-document | 63.6 | quota entry (covers FIN-document) |

Coverage: ANC-boolean 1, ANC-numeric 1, DI-annotation 1, DI-schema/join 4, EM-bibliographic 1, EM-other 1, EM-people/org 1, EM-products 5, FIN-document 2, TQA-financial 2, TQA-freeform 1, TQA-general 2, TQA-hierarchical/multi 2, TQA-verification 1.
Multilingual / non-English members: 2. Gated or NC licences to note: RealHiTBench, OpenSanctions Pairs, OfficeQA Pro V2.
Added relative to the previous list: WDC Products 2024 (hard negatives), FinTagging (FinNI+FinCL), Papadakis-Christen Dn1-Dn8, DocFinQA, VitaminC.

## Top 30

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 85.0 | by importance |
| 2 | Amazon-Google | EM-products | 85.0 | by importance |
| 3 | Magneto GDC-SM | DI-schema/join | 84.6 | by importance |
| 4 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 6 | HiTab | TQA-hierarchical/multi | 81.1 | by importance |
| 7 | Valentine | DI-schema/join | 81.1 | by importance |
| 8 | MMTU | TQA-general | 80.6 | by importance |
| 9 | Machamp (7 GEM tasks) | EM-products | 78.6 | by importance |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 78.4 | by importance |
| 11 | WikiTableQuestions | TQA-general | 78.0 | by importance |
| 12 | WDC Products 2024 (hard negatives) | EM-products | 77.9 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 76.6 | by importance |
| 14 | Papadakis-Christen Dn1-Dn8 | EM-other | 75.6 | by importance |
| 15 | Alaska Camera (SIGMOD 2020) | EM-products | 74.9 | by importance |
| 17 | RealHiTBench | TQA-hierarchical/multi | 74.6 | by importance |
| 20 | TableEval | TQA-freeform | 73.6 | by importance; inclusivity |
| 21 | OpenSanctions Pairs | EM-people/org | 73.0 | by importance; inclusivity |
| 22 | BIRD | TQA-sql | 72.2 | by importance |
| 23 | OfficeQA Pro V2 | FIN-document | 72.0 | by importance |
| 25 | TabFact | TQA-verification | 71.0 | by importance |
| 30 | TAT-QA | TQA-financial | 69.5 | by importance |
| 32 | DocFinQA | TQA-financial | 68.5 | quota entry (covers TQA-financial) |
| 33 | AIT-QA | TQA-hierarchical/multi | 68.1 | quota entry (covers TQA-hierarchical/multi) |
| 35 | TyDi QA GoldP | ANC-multilingual | 68.0 | quota entry (covers ANC-multilingual); inclusivity |
| 38 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |
| 40 | Raha/Baran error detection collection | DI-cleaning | 66.8 | quota entry (covers DI-cleaning) |
| 46 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 65.0 | quota entry (covers DI-annotation) |
| 51 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |
| 53 | BizBench (SEC-Num etc.) | FIN-document | 63.6 | quota entry (covers FIN-document) |

Coverage: ANC-boolean 1, ANC-multilingual 1, ANC-numeric 1, DI-annotation 1, DI-cleaning 1, DI-schema/join 4, EM-bibliographic 1, EM-other 1, EM-people/org 1, EM-products 6, FIN-document 2, TQA-financial 2, TQA-freeform 1, TQA-general 2, TQA-hierarchical/multi 3, TQA-sql 1, TQA-verification 1.
Multilingual / non-English members: 3. Gated or NC licences to note: RealHiTBench, OpenSanctions Pairs, OfficeQA Pro V2.
Added relative to the previous list: Alaska Camera (SIGMOD 2020), BIRD, AIT-QA, TyDi QA GoldP, Raha/Baran error detection collection.

## Top 40

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 85.0 | by importance |
| 2 | Amazon-Google | EM-products | 85.0 | by importance |
| 3 | Magneto GDC-SM | DI-schema/join | 84.6 | by importance |
| 4 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 6 | HiTab | TQA-hierarchical/multi | 81.1 | by importance |
| 7 | Valentine | DI-schema/join | 81.1 | by importance |
| 8 | MMTU | TQA-general | 80.6 | by importance |
| 9 | Machamp (7 GEM tasks) | EM-products | 78.6 | by importance |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 78.4 | by importance |
| 11 | WikiTableQuestions | TQA-general | 78.0 | by importance |
| 12 | WDC Products 2024 (hard negatives) | EM-products | 77.9 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 76.6 | by importance |
| 14 | Papadakis-Christen Dn1-Dn8 | EM-other | 75.6 | by importance |
| 15 | Alaska Camera (SIGMOD 2020) | EM-products | 74.9 | by importance |
| 16 | Alaska schema-matching GT | DI-schema/join | 74.9 | by importance |
| 17 | RealHiTBench | TQA-hierarchical/multi | 74.6 | by importance |
| 18 | SUC (Table Meets LLM) | TQA-general | 73.6 | by importance |
| 19 | TabIS | TQA-general | 73.6 | by importance |
| 20 | TableEval | TQA-freeform | 73.6 | by importance; inclusivity |
| 21 | OpenSanctions Pairs | EM-people/org | 73.0 | by importance; inclusivity |
| 23 | OfficeQA Pro V2 | FIN-document | 72.0 | by importance |
| 25 | TabFact | TQA-verification | 71.0 | by importance |
| 27 | DBLP-ACM (+dirty) | EM-bibliographic | 70.0 | by importance |
| 30 | TAT-QA | TQA-financial | 69.5 | by importance |
| 31 | SciTab | TQA-verification | 68.6 | by importance |
| 32 | DocFinQA | TQA-financial | 68.5 | by importance |
| 33 | AIT-QA | TQA-hierarchical/multi | 68.1 | by importance |
| 34 | Beer (BeerAdvo-RateBeer) | EM-other | 68.0 | by importance |
| 35 | TyDi QA GoldP | ANC-multilingual | 68.0 | by importance; inclusivity |
| 36 | FinQA | TQA-financial | 67.5 | by importance |
| 38 | DROP | ANC-numeric | 67.0 | by importance |
| 39 | MGSM | ANC-numeric | 67.0 | by importance; inclusivity |
| 40 | Raha/Baran error detection collection | DI-cleaning | 66.8 | by importance |
| 46 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 65.0 | quota entry (covers DI-annotation) |
| 51 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |
| 53 | BizBench (SEC-Num etc.) | FIN-document | 63.6 | quota entry (covers FIN-document) |
| 61 | OfficeQA Pro/Full | FIN-document | 61.6 | quota entry (covers FIN-document) |
| 76 | SANTOS | DI-discovery | 57.9 | quota entry (covers DI-discovery) |
| 79 | T2Dv2 | DI-annotation | 57.1 | quota entry (covers DI-annotation) |

Coverage: ANC-boolean 1, ANC-multilingual 1, ANC-numeric 2, DI-annotation 2, DI-cleaning 1, DI-discovery 1, DI-schema/join 5, EM-bibliographic 2, EM-other 2, EM-people/org 1, EM-products 6, FIN-document 3, TQA-financial 3, TQA-freeform 1, TQA-general 4, TQA-hierarchical/multi 3, TQA-verification 2.
Multilingual / non-English members: 4. Gated or NC licences to note: RealHiTBench, OpenSanctions Pairs, OfficeQA Pro V2, OfficeQA Pro/Full.
Added relative to the previous list: Alaska schema-matching GT, SUC (Table Meets LLM), TabIS, DBLP-ACM (+dirty), SciTab, Beer (BeerAdvo-RateBeer), FinQA, MGSM, OfficeQA Pro/Full, SANTOS, T2Dv2.

## Top 50

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 85.0 | by importance |
| 2 | Amazon-Google | EM-products | 85.0 | by importance |
| 3 | Magneto GDC-SM | DI-schema/join | 84.6 | by importance |
| 4 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 6 | HiTab | TQA-hierarchical/multi | 81.1 | by importance |
| 7 | Valentine | DI-schema/join | 81.1 | by importance |
| 8 | MMTU | TQA-general | 80.6 | by importance |
| 9 | Machamp (7 GEM tasks) | EM-products | 78.6 | by importance |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 78.4 | by importance |
| 11 | WikiTableQuestions | TQA-general | 78.0 | by importance |
| 12 | WDC Products 2024 (hard negatives) | EM-products | 77.9 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 76.6 | by importance |
| 14 | Papadakis-Christen Dn1-Dn8 | EM-other | 75.6 | by importance |
| 15 | Alaska Camera (SIGMOD 2020) | EM-products | 74.9 | by importance |
| 16 | Alaska schema-matching GT | DI-schema/join | 74.9 | by importance |
| 17 | RealHiTBench | TQA-hierarchical/multi | 74.6 | by importance |
| 18 | SUC (Table Meets LLM) | TQA-general | 73.6 | by importance |
| 19 | TabIS | TQA-general | 73.6 | by importance |
| 20 | TableEval | TQA-freeform | 73.6 | by importance; inclusivity |
| 21 | OpenSanctions Pairs | EM-people/org | 73.0 | by importance; inclusivity |
| 22 | BIRD | TQA-sql | 72.2 | by importance |
| 23 | OfficeQA Pro V2 | FIN-document | 72.0 | by importance |
| 24 | TPC-DI (cell-level task) | DI-schema/join | 71.1 | by importance |
| 25 | TabFact | TQA-verification | 71.0 | by importance |
| 26 | FeTaQA | TQA-freeform | 71.0 | by importance |
| 27 | DBLP-ACM (+dirty) | EM-bibliographic | 70.0 | by importance |
| 30 | TAT-QA | TQA-financial | 69.5 | by importance |
| 31 | SciTab | TQA-verification | 68.6 | by importance |
| 32 | DocFinQA | TQA-financial | 68.5 | by importance |
| 33 | AIT-QA | TQA-hierarchical/multi | 68.1 | by importance |
| 34 | Beer (BeerAdvo-RateBeer) | EM-other | 68.0 | by importance |
| 35 | TyDi QA GoldP | ANC-multilingual | 68.0 | by importance; inclusivity |
| 36 | FinQA | TQA-financial | 67.5 | by importance |
| 37 | iTunes-Amazon (+dirty) | EM-other | 67.0 | by importance |
| 38 | DROP | ANC-numeric | 67.0 | by importance |
| 39 | MGSM | ANC-numeric | 67.0 | by importance; inclusivity |
| 40 | Raha/Baran error detection collection | DI-cleaning | 66.8 | by importance |
| 42 | MiMoTable | TQA-hierarchical/multi | 65.6 | by importance; inclusivity |
| 46 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 65.0 | by importance |
| 47 | QAMPARI | ANC-list/table | 65.0 | by importance |
| 51 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |
| 53 | BizBench (SEC-Num etc.) | FIN-document | 63.6 | quota entry (covers FIN-document) |
| 57 | NarrativeQA | ANC-span/freeform | 62.0 | quota entry (covers ANC-span/freeform) |
| 58 | MLQA | ANC-multilingual | 62.0 | quota entry (covers ANC-multilingual); inclusivity |
| 61 | OfficeQA Pro/Full | FIN-document | 61.6 | quota entry (covers FIN-document) |
| 63 | FinanceBench (150 open) | FIN-document | 60.9 | quota entry (covers FIN-document) |
| 76 | SANTOS | DI-discovery | 57.9 | quota entry (covers DI-discovery) |
| 79 | T2Dv2 | DI-annotation | 57.1 | quota entry (covers DI-annotation) |
| 88 | North Carolina Voters 5M | EM-people/org | 55.0 | quota entry (covers EM-people/org) |

Coverage: ANC-boolean 1, ANC-list/table 1, ANC-multilingual 2, ANC-numeric 2, ANC-span/freeform 1, DI-annotation 2, DI-cleaning 1, DI-discovery 1, DI-schema/join 6, EM-bibliographic 2, EM-other 3, EM-people/org 2, EM-products 6, FIN-document 4, TQA-financial 3, TQA-freeform 2, TQA-general 4, TQA-hierarchical/multi 4, TQA-sql 1, TQA-verification 2.
Multilingual / non-English members: 6. Gated or NC licences to note: RealHiTBench, OpenSanctions Pairs, OfficeQA Pro V2, TPC-DI (cell-level task), OfficeQA Pro/Full, FinanceBench (150 open).
Added relative to the previous list: BIRD, TPC-DI (cell-level task), FeTaQA, iTunes-Amazon (+dirty), MiMoTable, QAMPARI, NarrativeQA, MLQA, FinanceBench (150 open), North Carolina Voters 5M.

