# Coverage-constrained groupings: the 5, 10, 20, 25, 30, 40 and 50 most important datasets

Each list is built in three passes: (0) the top ⌈k/2⌉ datasets by importance are always included; (1) fill a coverage quota per family (entity matching by domain, schema/join, annotation, table QA by kind, financial documents, anchors by answer type, multilingual, meta-evaluation) with the highest-ranked members of that family; (2) fill the remaining slots by global importance. Pass 0 guarantees that no dataset ranked in the top half of a list's size can be crowded out by quotas (without it, quota sums close to k made the 40- and 50-lists almost entirely quota-driven). So a lower-ranked dataset can enter a list ahead of a higher-ranked one when it is the only representative of a family the list must cover (inclusivity / representation); this is stated per list as 'quota entries'. The quotas grow with k so that small lists stay focused on the benchmark's core (matching, schema, tables, financial documents) and larger lists add anchors, multilingual sets and human-label meta-evaluation.

## Top 5

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | by importance |
| 2 | MMTU | TQA-general | 89.0 | by importance |
| 3 | Valentine | DI-schema/join | 89.0 | by importance |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | by importance |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | by importance |

Coverage: DI-schema/join 2, EM-products 1, TQA-general 1, TQA-hierarchical/multi 1.
Multilingual / non-English members: 0. Gated or NC licences to note: none.
Added relative to the previous list: —.

## Top 10

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | by importance |
| 2 | MMTU | TQA-general | 89.0 | by importance |
| 3 | Valentine | DI-schema/join | 89.0 | by importance |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | by importance |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | by importance |
| 6 | Machamp (7 GEM tasks) | EM-products | 86.0 | by importance |
| 7 | Abt-Buy | EM-products | 85.0 | by importance |
| 10 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 15 | OfficeQA Pro V2 | FIN-document | 78.0 | quota entry (covers FIN-document) |
| 25 | TAT-QA | TQA-financial | 75.0 | quota entry (covers TQA-financial) |

Coverage: DI-schema/join 2, EM-bibliographic 1, EM-products 3, FIN-document 1, TQA-financial 1, TQA-general 1, TQA-hierarchical/multi 1.
Multilingual / non-English members: 0. Gated or NC licences to note: OfficeQA Pro V2.
Added relative to the previous list: Machamp (7 GEM tasks), Abt-Buy, DBLP-Scholar (+dirty), OfficeQA Pro V2, TAT-QA.

## Top 20

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | by importance |
| 2 | MMTU | TQA-general | 89.0 | by importance |
| 3 | Valentine | DI-schema/join | 89.0 | by importance |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | by importance |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | by importance |
| 6 | Machamp (7 GEM tasks) | EM-products | 86.0 | by importance |
| 7 | Abt-Buy | EM-products | 85.0 | by importance |
| 8 | Amazon-Google | EM-products | 85.0 | by importance |
| 9 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 10 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 12 | RealHiTBench | TQA-hierarchical/multi | 80.0 | by importance |
| 14 | SUC (Table Meets LLM) | TQA-general | 79.0 | by importance |
| 15 | OfficeQA Pro V2 | FIN-document | 78.0 | by importance |
| 21 | OpenSanctions Pairs | EM-people/org | 76.0 | quota entry (covers EM-people/org); inclusivity |
| 23 | TableEval | TQA-freeform | 76.0 | quota entry (covers TQA-freeform); inclusivity |
| 25 | TAT-QA | TQA-financial | 75.0 | quota entry (covers TQA-financial) |
| 26 | SciTab | TQA-verification | 74.0 | quota entry (covers TQA-verification) |
| 28 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 74.0 | quota entry (covers DI-annotation) |
| 39 | FinanceBench (150 open) | FIN-document | 70.0 | quota entry (covers FIN-document) |
| 53 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |

Coverage: ANC-numeric 1, DI-annotation 1, DI-schema/join 2, EM-bibliographic 1, EM-people/org 1, EM-products 5, FIN-document 2, TQA-financial 1, TQA-freeform 1, TQA-general 2, TQA-hierarchical/multi 2, TQA-verification 1.
Multilingual / non-English members: 2. Gated or NC licences to note: RealHiTBench, OfficeQA Pro V2, OpenSanctions Pairs, FinanceBench (150 open).
Added relative to the previous list: Amazon-Google, Walmart-Amazon (+dirty), RealHiTBench, SUC (Table Meets LLM), OpenSanctions Pairs, TableEval, SciTab, SemTab 2025 (MammoTab Secu-table), FinanceBench (150 open), DROP.

## Top 25

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | by importance |
| 2 | MMTU | TQA-general | 89.0 | by importance |
| 3 | Valentine | DI-schema/join | 89.0 | by importance |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | by importance |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | by importance |
| 6 | Machamp (7 GEM tasks) | EM-products | 86.0 | by importance |
| 7 | Abt-Buy | EM-products | 85.0 | by importance |
| 8 | Amazon-Google | EM-products | 85.0 | by importance |
| 9 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 10 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 11 | Papadakis-Christen Dn1-Dn8 | EM-other | 81.0 | by importance |
| 12 | RealHiTBench | TQA-hierarchical/multi | 80.0 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 79.0 | by importance |
| 14 | SUC (Table Meets LLM) | TQA-general | 79.0 | by importance |
| 15 | OfficeQA Pro V2 | FIN-document | 78.0 | by importance |
| 21 | OpenSanctions Pairs | EM-people/org | 76.0 | by importance; inclusivity |
| 23 | TableEval | TQA-freeform | 76.0 | by importance; inclusivity |
| 25 | TAT-QA | TQA-financial | 75.0 | by importance |
| 26 | SciTab | TQA-verification | 74.0 | quota entry (covers TQA-verification) |
| 28 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 74.0 | quota entry (covers DI-annotation) |
| 39 | FinanceBench (150 open) | FIN-document | 70.0 | quota entry (covers FIN-document) |
| 41 | FinQA | TQA-financial | 70.0 | quota entry (covers TQA-financial) |
| 46 | TyDi QA GoldP | ANC-multilingual | 68.0 | quota entry (covers ANC-multilingual); inclusivity |
| 53 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |
| 68 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |

Coverage: ANC-boolean 1, ANC-multilingual 1, ANC-numeric 1, DI-annotation 1, DI-schema/join 3, EM-bibliographic 1, EM-other 1, EM-people/org 1, EM-products 5, FIN-document 2, TQA-financial 2, TQA-freeform 1, TQA-general 2, TQA-hierarchical/multi 2, TQA-verification 1.
Multilingual / non-English members: 3. Gated or NC licences to note: RealHiTBench, OfficeQA Pro V2, OpenSanctions Pairs, FinanceBench (150 open).
Added relative to the previous list: Papadakis-Christen Dn1-Dn8, FinTagging (FinNI+FinCL), FinQA, TyDi QA GoldP, VitaminC.

## Top 30

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | by importance |
| 2 | MMTU | TQA-general | 89.0 | by importance |
| 3 | Valentine | DI-schema/join | 89.0 | by importance |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | by importance |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | by importance |
| 6 | Machamp (7 GEM tasks) | EM-products | 86.0 | by importance |
| 7 | Abt-Buy | EM-products | 85.0 | by importance |
| 8 | Amazon-Google | EM-products | 85.0 | by importance |
| 9 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 10 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 11 | Papadakis-Christen Dn1-Dn8 | EM-other | 81.0 | by importance |
| 12 | RealHiTBench | TQA-hierarchical/multi | 80.0 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 79.0 | by importance |
| 14 | SUC (Table Meets LLM) | TQA-general | 79.0 | by importance |
| 15 | OfficeQA Pro V2 | FIN-document | 78.0 | by importance |
| 16 | Alaska Camera (SIGMOD 2020) | EM-products | 78.0 | by importance |
| 21 | OpenSanctions Pairs | EM-people/org | 76.0 | by importance; inclusivity |
| 23 | TableEval | TQA-freeform | 76.0 | by importance; inclusivity |
| 25 | TAT-QA | TQA-financial | 75.0 | by importance |
| 26 | SciTab | TQA-verification | 74.0 | by importance |
| 28 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 74.0 | by importance |
| 30 | BIRD | TQA-sql | 73.0 | by importance |
| 37 | AIT-QA | TQA-hierarchical/multi | 70.0 | quota entry (covers TQA-hierarchical/multi) |
| 39 | FinanceBench (150 open) | FIN-document | 70.0 | quota entry (covers FIN-document) |
| 41 | FinQA | TQA-financial | 70.0 | quota entry (covers TQA-financial) |
| 46 | TyDi QA GoldP | ANC-multilingual | 68.0 | quota entry (covers ANC-multilingual); inclusivity |
| 52 | Raha/Baran error detection collection | DI-cleaning | 67.0 | quota entry (covers DI-cleaning) |
| 53 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |
| 57 | WMT MQM | META | 66.0 | quota entry (covers META); inclusivity |
| 68 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |

Coverage: ANC-boolean 1, ANC-multilingual 1, ANC-numeric 1, DI-annotation 1, DI-cleaning 1, DI-schema/join 3, EM-bibliographic 1, EM-other 1, EM-people/org 1, EM-products 6, FIN-document 2, META 1, TQA-financial 2, TQA-freeform 1, TQA-general 2, TQA-hierarchical/multi 3, TQA-sql 1, TQA-verification 1.
Multilingual / non-English members: 4. Gated or NC licences to note: RealHiTBench, OfficeQA Pro V2, OpenSanctions Pairs, FinanceBench (150 open).
Added relative to the previous list: Alaska Camera (SIGMOD 2020), BIRD, AIT-QA, Raha/Baran error detection collection, WMT MQM.

## Top 40

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | by importance |
| 2 | MMTU | TQA-general | 89.0 | by importance |
| 3 | Valentine | DI-schema/join | 89.0 | by importance |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | by importance |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | by importance |
| 6 | Machamp (7 GEM tasks) | EM-products | 86.0 | by importance |
| 7 | Abt-Buy | EM-products | 85.0 | by importance |
| 8 | Amazon-Google | EM-products | 85.0 | by importance |
| 9 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 10 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 11 | Papadakis-Christen Dn1-Dn8 | EM-other | 81.0 | by importance |
| 12 | RealHiTBench | TQA-hierarchical/multi | 80.0 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 79.0 | by importance |
| 14 | SUC (Table Meets LLM) | TQA-general | 79.0 | by importance |
| 15 | OfficeQA Pro V2 | FIN-document | 78.0 | by importance |
| 16 | Alaska Camera (SIGMOD 2020) | EM-products | 78.0 | by importance |
| 17 | Alaska schema-matching GT | DI-schema/join | 78.0 | by importance |
| 18 | WikiTableQuestions | TQA-general | 78.0 | by importance |
| 19 | TabIS | TQA-general | 76.0 | by importance |
| 20 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 76.0 | by importance |
| 21 | OpenSanctions Pairs | EM-people/org | 76.0 | by importance; inclusivity |
| 23 | TableEval | TQA-freeform | 76.0 | by importance; inclusivity |
| 25 | TAT-QA | TQA-financial | 75.0 | by importance |
| 26 | SciTab | TQA-verification | 74.0 | by importance |
| 28 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 74.0 | by importance |
| 35 | TabFact | TQA-verification | 71.0 | by importance |
| 37 | AIT-QA | TQA-hierarchical/multi | 70.0 | by importance |
| 38 | DBLP-ACM (+dirty) | EM-bibliographic | 70.0 | by importance |
| 39 | FinanceBench (150 open) | FIN-document | 70.0 | by importance |
| 41 | FinQA | TQA-financial | 70.0 | quota entry (covers TQA-financial) |
| 43 | BizBench (SEC-Num etc.) | FIN-document | 69.0 | quota entry (covers FIN-document) |
| 44 | MusicBrainz 20K | EM-other | 69.0 | quota entry (covers EM-other) |
| 46 | TyDi QA GoldP | ANC-multilingual | 68.0 | quota entry (covers ANC-multilingual); inclusivity |
| 52 | Raha/Baran error detection collection | DI-cleaning | 67.0 | quota entry (covers DI-cleaning) |
| 53 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |
| 55 | MGSM | ANC-numeric | 67.0 | quota entry (covers ANC-numeric); inclusivity |
| 60 | DocFinQA | TQA-financial | 65.0 | quota entry (covers TQA-financial) |
| 67 | SANTOS | DI-discovery | 64.0 | quota entry (covers DI-discovery) |
| 68 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |
| 79 | GitTables CTA | DI-annotation | 61.0 | quota entry (covers DI-annotation) |

Coverage: ANC-boolean 1, ANC-multilingual 1, ANC-numeric 2, DI-annotation 2, DI-cleaning 1, DI-discovery 1, DI-schema/join 5, EM-bibliographic 2, EM-other 2, EM-people/org 1, EM-products 6, FIN-document 3, TQA-financial 3, TQA-freeform 1, TQA-general 4, TQA-hierarchical/multi 3, TQA-verification 2.
Multilingual / non-English members: 4. Gated or NC licences to note: RealHiTBench, OfficeQA Pro V2, OpenSanctions Pairs, FinanceBench (150 open).
Added relative to the previous list: Alaska schema-matching GT, WikiTableQuestions, TabIS, SMAT (MIMIC Synthea CMS to OMOP), TabFact, DBLP-ACM (+dirty), BizBench (SEC-Num etc.), MusicBrainz 20K, MGSM, DocFinQA, SANTOS, GitTables CTA.

## Top 50

| # | Dataset | Coverage family | Imp. | Role in the group |
|---|---|---|---|---|
| 1 | Magneto GDC-SM | DI-schema/join | 90.0 | by importance |
| 2 | MMTU | TQA-general | 89.0 | by importance |
| 3 | Valentine | DI-schema/join | 89.0 | by importance |
| 4 | WDC Products 2024 (hard negatives) | EM-products | 87.0 | by importance |
| 5 | HiTab | TQA-hierarchical/multi | 86.0 | by importance |
| 6 | Machamp (7 GEM tasks) | EM-products | 86.0 | by importance |
| 7 | Abt-Buy | EM-products | 85.0 | by importance |
| 8 | Amazon-Google | EM-products | 85.0 | by importance |
| 9 | Walmart-Amazon (+dirty) | EM-products | 83.0 | by importance |
| 10 | DBLP-Scholar (+dirty) | EM-bibliographic | 82.0 | by importance |
| 11 | Papadakis-Christen Dn1-Dn8 | EM-other | 81.0 | by importance |
| 12 | RealHiTBench | TQA-hierarchical/multi | 80.0 | by importance |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 79.0 | by importance |
| 14 | SUC (Table Meets LLM) | TQA-general | 79.0 | by importance |
| 15 | OfficeQA Pro V2 | FIN-document | 78.0 | by importance |
| 16 | Alaska Camera (SIGMOD 2020) | EM-products | 78.0 | by importance |
| 17 | Alaska schema-matching GT | DI-schema/join | 78.0 | by importance |
| 18 | WikiTableQuestions | TQA-general | 78.0 | by importance |
| 19 | TabIS | TQA-general | 76.0 | by importance |
| 20 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 76.0 | by importance |
| 21 | OpenSanctions Pairs | EM-people/org | 76.0 | by importance; inclusivity |
| 22 | TableBench | TQA-general | 76.0 | by importance |
| 23 | TableEval | TQA-freeform | 76.0 | by importance; inclusivity |
| 24 | Jellyfish DP tasks (ED DI SM EM) | DI-other | 75.0 | by importance |
| 25 | TAT-QA | TQA-financial | 75.0 | by importance |
| 26 | SciTab | TQA-verification | 74.0 | by importance |
| 28 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 74.0 | by importance |
| 35 | TabFact | TQA-verification | 71.0 | by importance |
| 36 | FeTaQA | TQA-freeform | 71.0 | by importance |
| 37 | AIT-QA | TQA-hierarchical/multi | 70.0 | by importance |
| 38 | DBLP-ACM (+dirty) | EM-bibliographic | 70.0 | by importance |
| 39 | FinanceBench (150 open) | FIN-document | 70.0 | by importance |
| 40 | MultiHiertt | TQA-hierarchical/multi | 70.0 | by importance |
| 41 | FinQA | TQA-financial | 70.0 | by importance |
| 43 | BizBench (SEC-Num etc.) | FIN-document | 69.0 | by importance |
| 44 | MusicBrainz 20K | EM-other | 69.0 | by importance |
| 46 | TyDi QA GoldP | ANC-multilingual | 68.0 | by importance; inclusivity |
| 48 | OfficeQA Pro/Full | FIN-document | 67.0 | by importance |
| 50 | Cross-dataset EM study (11 sets LODO) | EM-other | 67.0 | by importance |
| 52 | Raha/Baran error detection collection | DI-cleaning | 67.0 | quota entry (covers DI-cleaning) |
| 53 | DROP | ANC-numeric | 67.0 | quota entry (covers ANC-numeric) |
| 55 | MGSM | ANC-numeric | 67.0 | quota entry (covers ANC-numeric); inclusivity |
| 60 | DocFinQA | TQA-financial | 65.0 | quota entry (covers TQA-financial) |
| 62 | QAMPARI | ANC-list/table | 65.0 | quota entry (covers ANC-list/table) |
| 63 | North Carolina Voters 5M | EM-people/org | 64.0 | quota entry (covers EM-people/org) |
| 67 | SANTOS | DI-discovery | 64.0 | quota entry (covers DI-discovery) |
| 68 | VitaminC | ANC-boolean | 64.0 | quota entry (covers ANC-boolean) |
| 76 | NarrativeQA | ANC-span/freeform | 62.0 | quota entry (covers ANC-span/freeform) |
| 77 | MLQA | ANC-multilingual | 62.0 | quota entry (covers ANC-multilingual); inclusivity |
| 79 | GitTables CTA | DI-annotation | 61.0 | quota entry (covers DI-annotation) |

Coverage: ANC-boolean 1, ANC-list/table 1, ANC-multilingual 2, ANC-numeric 2, ANC-span/freeform 1, DI-annotation 2, DI-cleaning 1, DI-discovery 1, DI-other 1, DI-schema/join 5, EM-bibliographic 2, EM-other 3, EM-people/org 2, EM-products 6, FIN-document 4, TQA-financial 3, TQA-freeform 2, TQA-general 5, TQA-hierarchical/multi 4, TQA-verification 2.
Multilingual / non-English members: 5. Gated or NC licences to note: RealHiTBench, OfficeQA Pro V2, OpenSanctions Pairs, FinanceBench (150 open), OfficeQA Pro/Full.
Added relative to the previous list: TableBench, Jellyfish DP tasks (ED DI SM EM), FeTaQA, MultiHiertt, OfficeQA Pro/Full, Cross-dataset EM study (11 sets LODO), QAMPARI, North Carolina Voters 5M, NarrativeQA, MLQA.

