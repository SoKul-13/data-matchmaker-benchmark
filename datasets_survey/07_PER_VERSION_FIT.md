# Per-version fit: which datasets each version can use, and the recommended groups of 5/10/20/25/30/40/50 per version

Rule: a dataset 'fits' a version if the version's scorer can consume its gold format without new code (stated per version). Within the fitting set, groups are built with the same three-pass procedure (top half by importance, then coverage quotas, then importance) as `06_GROUPINGS.md`, restricted to fitting datasets. If a quota family has no fitting member it is skipped.

## v1 (original judge: TPC-DI rubric + hand-set composite)

v1 grades short QA answers with a fixed composite and scores the TPC-DI join task; it can only consume short-answer table/document QA and its own task. Entity matching and schema sets have no path into v1.

Fitting datasets: 39 of 100. Not fitting (top examples): Magneto GDC-SM, Valentine, WDC Products 2024 (hard negatives), Machamp (7 GEM tasks), Abt-Buy, Amazon-Google, Walmart-Amazon (+dirty), DBLP-Scholar (+dirty), Papadakis-Christen Dn1-Dn8, FinTagging (FinNI+FinCL), Alaska Camera (SIGMOD 2020), Alaska schema-matching GT, SMAT (MIMIC Synthea CMS to OMOP), OpenSanctions Pairs, Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), BIRD, Spider 2.0, Auto-Join, WDC LSPC / Products-2017, DBLP-ACM (+dirty), OAEI 2025 ontology tracks, MusicBrainz 20K, TyDi QA GoldP, MMQA (multi-table PK/FK), Alaska Monitor/Notebook, Cross-dataset .

**Top 5:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 29. TPC-DI (cell-level task)

**Top 10:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 25. TAT-QA; 29. TPC-DI (cell-level task)

**Top 20:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.)

**Top 25:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA

**Top 30:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA; 61. DocMath-Eval; 66. DataBench (SemEval 2025); 73. TempTabQA; 74. ConvFinQA; 80. InfoTabs

**Top 40:** only 39 fitting datasets exist; list = all of them.
**Top 40:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA; 61. DocMath-Eval; 66. DataBench (SemEval 2025); 73. TempTabQA; 74. ConvFinQA; 80. InfoTabs; 81. TAT-DQA; 83. FinanceMath; 84. ChartQA; 85. EDGAR-CORPUS; 86. SECQUE; 88. SQA; 90. MP-DocVQA; 99. CRT-QA; 100. PubHealthTab

**Top 50:** only 39 fitting datasets exist; list = all of them.
**Top 50:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA; 61. DocMath-Eval; 66. DataBench (SemEval 2025); 73. TempTabQA; 74. ConvFinQA; 80. InfoTabs; 81. TAT-DQA; 83. FinanceMath; 84. ChartQA; 85. EDGAR-CORPUS; 86. SECQUE; 88. SQA; 90. MP-DocVQA; 99. CRT-QA; 100. PubHealthTab


## v2 (grid over v1's four weights)

same scorer as v1; needs short golds where F1 / precision / recall / numeric decay are meaningful; boolean sets are fine but uninformative for the four weights; free-form sets stress the weights most.

Fitting datasets: 39 of 100. Not fitting (top examples): Magneto GDC-SM, Valentine, WDC Products 2024 (hard negatives), Machamp (7 GEM tasks), Abt-Buy, Amazon-Google, Walmart-Amazon (+dirty), DBLP-Scholar (+dirty), Papadakis-Christen Dn1-Dn8, FinTagging (FinNI+FinCL), Alaska Camera (SIGMOD 2020), Alaska schema-matching GT, SMAT (MIMIC Synthea CMS to OMOP), OpenSanctions Pairs, Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), BIRD, Spider 2.0, Auto-Join, WDC LSPC / Products-2017, DBLP-ACM (+dirty), OAEI 2025 ontology tracks, MusicBrainz 20K, TyDi QA GoldP, MMQA (multi-table PK/FK), Alaska Monitor/Notebook, Cross-dataset .

**Top 5:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 29. TPC-DI (cell-level task)

**Top 10:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 25. TAT-QA; 29. TPC-DI (cell-level task)

**Top 20:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.)

**Top 25:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA

**Top 30:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA; 61. DocMath-Eval; 66. DataBench (SemEval 2025); 73. TempTabQA; 74. ConvFinQA; 80. InfoTabs

**Top 40:** only 39 fitting datasets exist; list = all of them.
**Top 40:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA; 61. DocMath-Eval; 66. DataBench (SemEval 2025); 73. TempTabQA; 74. ConvFinQA; 80. InfoTabs; 81. TAT-DQA; 83. FinanceMath; 84. ChartQA; 85. EDGAR-CORPUS; 86. SECQUE; 88. SQA; 90. MP-DocVQA; 99. CRT-QA; 100. PubHealthTab

**Top 50:** only 39 fitting datasets exist; list = all of them.
**Top 50:** 2. MMTU; 5. HiTab; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 18. WikiTableQuestions; 19. TabIS; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 29. TPC-DI (cell-level task); 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 45. MiMoTable; 48. OfficeQA Pro/Full; 51. FEVEROUS; 56. HybridQA; 60. DocFinQA; 61. DocMath-Eval; 66. DataBench (SemEval 2025); 73. TempTabQA; 74. ConvFinQA; 80. InfoTabs; 81. TAT-DQA; 83. FinanceMath; 84. ChartQA; 85. EDGAR-CORPUS; 86. SECQUE; 88. SQA; 90. MP-DocVQA; 99. CRT-QA; 100. PubHealthTab


## v3 (native metric per dataset + literature aggregation views)

v3 uses each dataset's official metric, so any dataset with a clear metric fits, including entity matching (accuracy/F1), schema matching (F1, MRR) and SQL (execution accuracy); it rewards many items per dataset (Bradley–Terry and IRT need pairs) and penalises sets without an official metric.

Fitting datasets: 91 of 100. Not fitting (top examples): WMT MQM, FinAuditing, SummEval, GitTables CTA, EDGAR-CORPUS, SECQUE, JudgeBench, LLMBar, TRUE.

**Top 5:** 1. Magneto GDC-SM; 2. MMTU; 3. Valentine; 4. WDC Products 2024 (hard negatives); 5. HiTab

**Top 10:** 1. Magneto GDC-SM; 2. MMTU; 3. Valentine; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 10. DBLP-Scholar (+dirty); 15. OfficeQA Pro V2; 25. TAT-QA

**Top 20:** 1. Magneto GDC-SM; 2. MMTU; 3. Valentine; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 21. OpenSanctions Pairs; 23. TableEval; 25. TAT-QA; 26. SciTab; 28. SemTab 2025 (MammoTab Secu-table); 39. FinanceBench (150 open); 53. DROP

**Top 25:** 1. Magneto GDC-SM; 2. MMTU; 3. Valentine; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 13. FinTagging (FinNI+FinCL); 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 21. OpenSanctions Pairs; 23. TableEval; 25. TAT-QA; 26. SciTab; 28. SemTab 2025 (MammoTab Secu-table); 39. FinanceBench (150 open); 41. FinQA; 46. TyDi QA GoldP; 53. DROP; 68. VitaminC

**Top 30:** 1. Magneto GDC-SM; 2. MMTU; 3. Valentine; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 13. FinTagging (FinNI+FinCL); 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 17. Alaska schema-matching GT; 21. OpenSanctions Pairs; 23. TableEval; 25. TAT-QA; 26. SciTab; 28. SemTab 2025 (MammoTab Secu-table); 30. BIRD; 37. AIT-QA; 39. FinanceBench (150 open); 41. FinQA; 46. TyDi QA GoldP; 52. Raha/Baran error detection collection; 53. DROP; 68. VitaminC

**Top 40:** 1. Magneto GDC-SM; 2. MMTU; 3. Valentine; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 13. FinTagging (FinNI+FinCL); 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 17. Alaska schema-matching GT; 18. WikiTableQuestions; 19. TabIS; 20. SMAT (MIMIC Synthea CMS to OMOP); 21. OpenSanctions Pairs; 23. TableEval; 25. TAT-QA; 26. SciTab; 28. SemTab 2025 (MammoTab Secu-table); 35. TabFact; 37. AIT-QA; 38. DBLP-ACM (+dirty); 39. FinanceBench (150 open); 41. FinQA; 43. BizBench (SEC-Num etc.); 44. MusicBrainz 20K; 46. TyDi QA GoldP; 52. Raha/Baran error detection collection; 53. DROP; 55. MGSM; 60. DocFinQA; 67. SANTOS; 68. VitaminC; 82. T2Dv2

**Top 50:** 1. Magneto GDC-SM; 2. MMTU; 3. Valentine; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 13. FinTagging (FinNI+FinCL); 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 17. Alaska schema-matching GT; 18. WikiTableQuestions; 19. TabIS; 20. SMAT (MIMIC Synthea CMS to OMOP); 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 24. Jellyfish DP tasks (ED DI SM EM); 25. TAT-QA; 26. SciTab; 28. SemTab 2025 (MammoTab Secu-table); 35. TabFact; 36. FeTaQA; 37. AIT-QA; 38. DBLP-ACM (+dirty); 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 44. MusicBrainz 20K; 46. TyDi QA GoldP; 48. OfficeQA Pro/Full; 50. Cross-dataset EM study (11 sets LODO); 52. Raha/Baran error detection collection; 53. DROP; 55. MGSM; 60. DocFinQA; 62. QAMPARI; 63. North Carolina Voters 5M; 67. SANTOS; 68. VitaminC; 76. NarrativeQA; 77. MLQA; 82. T2Dv2


## v4 (9-metric composite, random search, rank agreement)

v4 scores answer text with the 9-component composite, so it needs QA-style golds (numbers, spans, lists, sentences, yes/no); entity-matching sets work as yes/no items; schema and SQL sets do not fit without a wrapper. Its objective needs several datasets that genuinely rank models differently.

Fitting datasets: 60 of 100. Not fitting (top examples): Magneto GDC-SM, Valentine, FinTagging (FinNI+FinCL), Alaska schema-matching GT, SMAT (MIMIC Synthea CMS to OMOP), Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), TPC-DI (cell-level task), BIRD, Spider 2.0, Auto-Join, OAEI 2025 ontology tracks, TyDi QA GoldP, MMQA (multi-table PK/FK), Raha/Baran error detection collection, DROP, MGSM, WMT MQM, QAMPARI, MultiTabQA, SANTOS, VitaminC, FinAuditing, lm-dw / BIG-bench data wrangling, NarrativeQA, MLQA, SummEval, GitTables CTA, T2Dv2, HoloClean datasets, TUS Small/Large, JudgeBench, LLMBar, TRUE, TURL WikiTables CTA/CPA,.

**Top 5:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy

**Top 10:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 15. OfficeQA Pro V2; 25. TAT-QA

**Top 20:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 23. TableEval; 25. TAT-QA; 26. SciTab; 39. FinanceBench (150 open)

**Top 25:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 33. WDC LSPC / Products-2017; 34. RobuT; 35. TabFact; 39. FinanceBench (150 open); 41. FinQA

**Top 30:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 33. WDC LSPC / Products-2017; 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 38. DBLP-ACM (+dirty); 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.)

**Top 40:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 33. WDC LSPC / Products-2017; 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 38. DBLP-ACM (+dirty); 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 44. MusicBrainz 20K; 45. MiMoTable; 48. OfficeQA Pro/Full; 49. Alaska Monitor/Notebook; 50. Cross-dataset EM study (11 sets LODO); 51. FEVEROUS; 54. OpenEA (DBP15K DWY100K); 56. HybridQA; 58. Beer (BeerAdvo-RateBeer); 60. DocFinQA

**Top 50:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 33. WDC LSPC / Products-2017; 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 38. DBLP-ACM (+dirty); 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 44. MusicBrainz 20K; 45. MiMoTable; 48. OfficeQA Pro/Full; 49. Alaska Monitor/Notebook; 50. Cross-dataset EM study (11 sets LODO); 51. FEVEROUS; 54. OpenEA (DBP15K DWY100K); 56. HybridQA; 58. Beer (BeerAdvo-RateBeer); 59. Company; 60. DocFinQA; 61. DocMath-Eval; 63. North Carolina Voters 5M; 64. iTunes-Amazon (+dirty); 66. DataBench (SemEval 2025); 69. IMDB-TMDB/TVDB (MovieGraphBenchmark); 70. EMBer (multimodal EM); 71. Geographic Settlements; 73. TempTabQA; 74. ConvFinQA


## v5 (100-metric library + anchors + weight ensemble)

v5 needs alias-derivable golds of diverse answer types (its anchors are generated per gold) and benefits from every answer-type anchor and multilingual set; meta-evaluation sets (SummEval, TRUE, JudgeBench) are the human-label validation the paper still lacks.

Fitting datasets: 77 of 100. Not fitting (top examples): Magneto GDC-SM, Valentine, FinTagging (FinNI+FinCL), Alaska schema-matching GT, SMAT (MIMIC Synthea CMS to OMOP), Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), TPC-DI (cell-level task), BIRD, Spider 2.0, Auto-Join, OAEI 2025 ontology tracks, MMQA (multi-table PK/FK), Raha/Baran error detection collection, SANTOS, FinAuditing, lm-dw / BIG-bench data wrangling, GitTables CTA, T2Dv2, HoloClean datasets, TUS Small/Large, TURL WikiTables CTA/CPA.

**Top 5:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy

**Top 10:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 15. OfficeQA Pro V2; 25. TAT-QA

**Top 20:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 21. OpenSanctions Pairs; 23. TableEval; 25. TAT-QA; 26. SciTab; 39. FinanceBench (150 open); 46. TyDi QA GoldP; 53. DROP

**Top 25:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 39. FinanceBench (150 open); 41. FinQA; 46. TyDi QA GoldP; 53. DROP; 68. VitaminC

**Top 30:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 33. WDC LSPC / Products-2017; 34. RobuT; 35. TabFact; 37. AIT-QA; 39. FinanceBench (150 open); 41. FinQA; 46. TyDi QA GoldP; 53. DROP; 57. WMT MQM; 68. VitaminC

**Top 40:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 33. WDC LSPC / Products-2017; 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 38. DBLP-ACM (+dirty); 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 44. MusicBrainz 20K; 46. TyDi QA GoldP; 53. DROP; 55. MGSM; 57. WMT MQM; 60. DocFinQA; 62. QAMPARI; 68. VitaminC; 77. MLQA; 78. SummEval

**Top 50:** 2. MMTU; 4. WDC Products 2024 (hard negatives); 5. HiTab; 6. Machamp (7 GEM tasks); 7. Abt-Buy; 8. Amazon-Google; 9. Walmart-Amazon (+dirty); 10. DBLP-Scholar (+dirty); 11. Papadakis-Christen Dn1-Dn8; 12. RealHiTBench; 14. SUC (Table Meets LLM); 15. OfficeQA Pro V2; 16. Alaska Camera (SIGMOD 2020); 18. WikiTableQuestions; 19. TabIS; 21. OpenSanctions Pairs; 22. TableBench; 23. TableEval; 25. TAT-QA; 26. SciTab; 33. WDC LSPC / Products-2017; 34. RobuT; 35. TabFact; 36. FeTaQA; 37. AIT-QA; 38. DBLP-ACM (+dirty); 39. FinanceBench (150 open); 40. MultiHiertt; 41. FinQA; 43. BizBench (SEC-Num etc.); 44. MusicBrainz 20K; 45. MiMoTable; 46. TyDi QA GoldP; 48. OfficeQA Pro/Full; 49. Alaska Monitor/Notebook; 50. Cross-dataset EM study (11 sets LODO); 51. FEVEROUS; 53. DROP; 54. OpenEA (DBP15K DWY100K); 55. MGSM; 56. HybridQA; 57. WMT MQM; 58. Beer (BeerAdvo-RateBeer); 60. DocFinQA; 62. QAMPARI; 63. North Carolina Voters 5M; 68. VitaminC; 76. NarrativeQA; 77. MLQA; 78. SummEval


