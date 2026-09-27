# Per-version fit (evidence-based adoption): which datasets each version can use, and the recommended groups of 5/10/20/25/30/40/50 per version

Rule: a dataset 'fits' a version if the version's scorer can consume its gold format without new code (stated per version). Within the fitting set, groups are built with the same three-pass procedure (top half by importance, then coverage quotas, then importance) as `06_GROUPINGS_evidence.md`, restricted to fitting datasets. If a quota family has no fitting member it is skipped.

## v1 (original judge: TPC-DI rubric + hand-set composite)

v1 grades short QA answers with a fixed composite and scores the TPC-DI join task; it can only consume short-answer table/document QA and its own task. Entity matching and schema sets have no path into v1.

Fitting datasets: 38 of 100. Not fitting (top examples): Abt-Buy, Amazon-Google, Magneto GDC-SM, Walmart-Amazon (+dirty), DBLP-Scholar (+dirty), Valentine, Machamp (7 GEM tasks), SMAT (MIMIC Synthea CMS to OMOP), WDC Products 2024 (hard negatives), FinTagging (FinNI+FinCL), Papadakis-Christen Dn1-Dn8, Alaska Camera (SIGMOD 2020), Alaska schema-matching GT, OpenSanctions Pairs, BIRD, DBLP-ACM (+dirty), WDC LSPC / Products-2017, Beer (BeerAdvo-RateBeer), TyDi QA GoldP, iTunes-Amazon (+dirty), DROP, MGSM, Raha/Baran error detection collection, Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), QAMPARI, Spider 2.0, MMQA (mult.

**Top 5:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 24. TPC-DI (cell-level task)

**Top 10:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 30. TAT-QA

**Top 20:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 53. BizBench (SEC-Num etc.)

**Top 25:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open)

**Top 30:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 64. MultiHiertt; 67. DocMath-Eval; 68. TempTabQA; 77. TAT-DQA; 78. SQA

**Top 40:** only 38 fitting datasets exist; list = all of them.
**Top 40:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 64. MultiHiertt; 67. DocMath-Eval; 68. TempTabQA; 77. TAT-DQA; 78. SQA; 82. SECQUE; 86. DataBench (SemEval 2025); 87. FinanceMath; 89. InfoTabs; 92. FinDER; 93. Finance Agent Benchmark; 98. CRT-QA; 99. PubHealthTab

**Top 50:** only 38 fitting datasets exist; list = all of them.
**Top 50:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 64. MultiHiertt; 67. DocMath-Eval; 68. TempTabQA; 77. TAT-DQA; 78. SQA; 82. SECQUE; 86. DataBench (SemEval 2025); 87. FinanceMath; 89. InfoTabs; 92. FinDER; 93. Finance Agent Benchmark; 98. CRT-QA; 99. PubHealthTab


## v2 (grid over v1's four weights)

same scorer as v1; needs short golds where F1 / precision / recall / numeric decay are meaningful; boolean sets are fine but uninformative for the four weights; free-form sets stress the weights most.

Fitting datasets: 38 of 100. Not fitting (top examples): Abt-Buy, Amazon-Google, Magneto GDC-SM, Walmart-Amazon (+dirty), DBLP-Scholar (+dirty), Valentine, Machamp (7 GEM tasks), SMAT (MIMIC Synthea CMS to OMOP), WDC Products 2024 (hard negatives), FinTagging (FinNI+FinCL), Papadakis-Christen Dn1-Dn8, Alaska Camera (SIGMOD 2020), Alaska schema-matching GT, OpenSanctions Pairs, BIRD, DBLP-ACM (+dirty), WDC LSPC / Products-2017, Beer (BeerAdvo-RateBeer), TyDi QA GoldP, iTunes-Amazon (+dirty), DROP, MGSM, Raha/Baran error detection collection, Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), QAMPARI, Spider 2.0, MMQA (mult.

**Top 5:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 24. TPC-DI (cell-level task)

**Top 10:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 30. TAT-QA

**Top 20:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 53. BizBench (SEC-Num etc.)

**Top 25:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open)

**Top 30:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 64. MultiHiertt; 67. DocMath-Eval; 68. TempTabQA; 77. TAT-DQA; 78. SQA

**Top 40:** only 38 fitting datasets exist; list = all of them.
**Top 40:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 64. MultiHiertt; 67. DocMath-Eval; 68. TempTabQA; 77. TAT-DQA; 78. SQA; 82. SECQUE; 86. DataBench (SemEval 2025); 87. FinanceMath; 89. InfoTabs; 92. FinDER; 93. Finance Agent Benchmark; 98. CRT-QA; 99. PubHealthTab

**Top 50:** only 38 fitting datasets exist; list = all of them.
**Top 50:** 6. HiTab; 8. MMTU; 11. WikiTableQuestions; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 28. TableBench; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 36. FinQA; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 53. BizBench (SEC-Num etc.); 56. ConvFinQA; 60. HybridQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 64. MultiHiertt; 67. DocMath-Eval; 68. TempTabQA; 77. TAT-DQA; 78. SQA; 82. SECQUE; 86. DataBench (SemEval 2025); 87. FinanceMath; 89. InfoTabs; 92. FinDER; 93. Finance Agent Benchmark; 98. CRT-QA; 99. PubHealthTab


## v3 (native metric per dataset + literature aggregation views)

v3 uses each dataset's official metric, so any dataset with a clear metric fits, including entity matching (accuracy/F1), schema matching (F1, MRR) and SQL (execution accuracy); it rewards many items per dataset (Bradley–Terry and IRT need pairs) and penalises sets without an official metric.

Fitting datasets: 92 of 100. Not fitting (top examples): FinAuditing, WMT MQM, SummEval, SECQUE, LLMBar, JudgeBench, Finance Agent Benchmark, GitTables CTA.

**Top 5:** 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 6. HiTab; 7. Valentine

**Top 10:** 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 7. Valentine; 8. MMTU; 23. OfficeQA Pro V2; 30. TAT-QA

**Top 20:** 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 7. Valentine; 8. MMTU; 9. Machamp (7 GEM tasks); 10. SMAT (MIMIC Synthea CMS to OMOP); 11. WikiTableQuestions; 17. RealHiTBench; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 30. TAT-QA; 38. DROP; 46. SemTab 2025 (MammoTab Secu-table); 53. BizBench (SEC-Num etc.)

**Top 25:** 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 7. Valentine; 8. MMTU; 9. Machamp (7 GEM tasks); 10. SMAT (MIMIC Synthea CMS to OMOP); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 13. FinTagging (FinNI+FinCL); 14. Papadakis-Christen Dn1-Dn8; 17. RealHiTBench; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 30. TAT-QA; 32. DocFinQA; 38. DROP; 46. SemTab 2025 (MammoTab Secu-table); 51. VitaminC; 53. BizBench (SEC-Num etc.)

**Top 30:** 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 7. Valentine; 8. MMTU; 9. Machamp (7 GEM tasks); 10. SMAT (MIMIC Synthea CMS to OMOP); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 13. FinTagging (FinNI+FinCL); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 20. TableEval; 21. OpenSanctions Pairs; 22. BIRD; 23. OfficeQA Pro V2; 25. TabFact; 30. TAT-QA; 32. DocFinQA; 33. AIT-QA; 35. TyDi QA GoldP; 38. DROP; 40. Raha/Baran error detection collection; 46. SemTab 2025 (MammoTab Secu-table); 51. VitaminC; 53. BizBench (SEC-Num etc.)

**Top 40:** 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 7. Valentine; 8. MMTU; 9. Machamp (7 GEM tasks); 10. SMAT (MIMIC Synthea CMS to OMOP); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 13. FinTagging (FinNI+FinCL); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 16. Alaska schema-matching GT; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 27. DBLP-ACM (+dirty); 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 34. Beer (BeerAdvo-RateBeer); 35. TyDi QA GoldP; 36. FinQA; 38. DROP; 39. MGSM; 40. Raha/Baran error detection collection; 46. SemTab 2025 (MammoTab Secu-table); 51. VitaminC; 53. BizBench (SEC-Num etc.); 61. OfficeQA Pro/Full; 76. SANTOS; 79. T2Dv2

**Top 50:** 1. Abt-Buy; 2. Amazon-Google; 3. Magneto GDC-SM; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 7. Valentine; 8. MMTU; 9. Machamp (7 GEM tasks); 10. SMAT (MIMIC Synthea CMS to OMOP); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 13. FinTagging (FinNI+FinCL); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 16. Alaska schema-matching GT; 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 22. BIRD; 23. OfficeQA Pro V2; 24. TPC-DI (cell-level task); 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 34. Beer (BeerAdvo-RateBeer); 35. TyDi QA GoldP; 36. FinQA; 37. iTunes-Amazon (+dirty); 38. DROP; 39. MGSM; 40. Raha/Baran error detection collection; 42. MiMoTable; 46. SemTab 2025 (MammoTab Secu-table); 47. QAMPARI; 51. VitaminC; 53. BizBench (SEC-Num etc.); 57. NarrativeQA; 58. MLQA; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 76. SANTOS; 79. T2Dv2; 88. North Carolina Voters 5M


## v4 (9-metric composite, random search, rank agreement)

v4 scores answer text with the 9-component composite, so it needs QA-style golds (numbers, spans, lists, sentences, yes/no); entity-matching sets work as yes/no items; schema and SQL sets do not fit without a wrapper. Its objective needs several datasets that genuinely rank models differently.

Fitting datasets: 60 of 100. Not fitting (top examples): Magneto GDC-SM, Valentine, SMAT (MIMIC Synthea CMS to OMOP), FinTagging (FinNI+FinCL), Alaska schema-matching GT, BIRD, TPC-DI (cell-level task), TyDi QA GoldP, DROP, MGSM, Raha/Baran error detection collection, Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), QAMPARI, Spider 2.0, MMQA (multi-table PK/FK), MultiTabQA, VitaminC, Auto-Join, NarrativeQA, MLQA, HoloClean datasets, FinAuditing, OAEI 2025 ontology tracks, WMT MQM, TriviaQA, BoolQ, GSM8K (Platinum), SQuAD 2.0, SANTOS, T2Dv2, SummEval, LLMBar, TUS Small/Large, JudgeBench, lm-dw / BIG-bench data wrangling,.

**Top 5:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 6. HiTab; 8. MMTU

**Top 10:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 23. OfficeQA Pro V2; 30. TAT-QA

**Top 20:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 30. TAT-QA; 53. BizBench (SEC-Num etc.)

**Top 25:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 28. TableBench; 29. WDC LSPC / Products-2017; 30. TAT-QA; 32. DocFinQA; 53. BizBench (SEC-Num etc.)

**Top 30:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 28. TableBench; 29. WDC LSPC / Products-2017; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 34. Beer (BeerAdvo-RateBeer); 36. FinQA; 37. iTunes-Amazon (+dirty); 53. BizBench (SEC-Num etc.)

**Top 40:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 28. TableBench; 29. WDC LSPC / Products-2017; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 34. Beer (BeerAdvo-RateBeer); 36. FinQA; 37. iTunes-Amazon (+dirty); 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 52. Alaska Monitor/Notebook; 53. BizBench (SEC-Num etc.); 54. MusicBrainz 20K; 56. ConvFinQA; 59. Company; 60. HybridQA; 61. OfficeQA Pro/Full; 62. Cross-dataset EM study (11 sets LODO)

**Top 50:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 28. TableBench; 29. WDC LSPC / Products-2017; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 34. Beer (BeerAdvo-RateBeer); 36. FinQA; 37. iTunes-Amazon (+dirty); 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 52. Alaska Monitor/Notebook; 53. BizBench (SEC-Num etc.); 54. MusicBrainz 20K; 56. ConvFinQA; 59. Company; 60. HybridQA; 61. OfficeQA Pro/Full; 62. Cross-dataset EM study (11 sets LODO); 63. FinanceBench (150 open); 64. MultiHiertt; 65. IMDB-TMDB/TVDB (MovieGraphBenchmark); 67. DocMath-Eval; 68. TempTabQA; 77. TAT-DQA; 78. SQA; 81. EMBer (multimodal EM); 82. SECQUE; 88. North Carolina Voters 5M


## v5 (100-metric library + anchors + weight ensemble)

v5 needs alias-derivable golds of diverse answer types (its anchors are generated per gold) and benefits from every answer-type anchor and multilingual set; meta-evaluation sets (SummEval, TRUE, JudgeBench) are the human-label validation the paper still lacks.

Fitting datasets: 76 of 100. Not fitting (top examples): Magneto GDC-SM, Valentine, SMAT (MIMIC Synthea CMS to OMOP), FinTagging (FinNI+FinCL), Alaska schema-matching GT, BIRD, TPC-DI (cell-level task), Raha/Baran error detection collection, Jellyfish DP tasks (ED DI SM EM), SOTAB V2, SemTab 2025 (MammoTab Secu-table), Spider 2.0, MMQA (multi-table PK/FK), Auto-Join, HoloClean datasets, FinAuditing, OAEI 2025 ontology tracks, SANTOS, T2Dv2, TUS Small/Large, lm-dw / BIG-bench data wrangling, Spider 1.0, GitTables CTA, TURL WikiTables CTA/CPA.

**Top 5:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 6. HiTab; 8. MMTU

**Top 10:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 23. OfficeQA Pro V2; 30. TAT-QA

**Top 20:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 30. TAT-QA; 35. TyDi QA GoldP; 38. DROP; 53. BizBench (SEC-Num etc.)

**Top 25:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 30. TAT-QA; 32. DocFinQA; 35. TyDi QA GoldP; 38. DROP; 51. VitaminC; 53. BizBench (SEC-Num etc.)

**Top 30:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 28. TableBench; 29. WDC LSPC / Products-2017; 30. TAT-QA; 32. DocFinQA; 33. AIT-QA; 35. TyDi QA GoldP; 38. DROP; 51. VitaminC; 53. BizBench (SEC-Num etc.); 71. WMT MQM

**Top 40:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 28. TableBench; 29. WDC LSPC / Products-2017; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 34. Beer (BeerAdvo-RateBeer); 35. TyDi QA GoldP; 36. FinQA; 37. iTunes-Amazon (+dirty); 38. DROP; 39. MGSM; 42. MiMoTable; 47. QAMPARI; 51. VitaminC; 53. BizBench (SEC-Num etc.); 58. MLQA; 61. OfficeQA Pro/Full; 71. WMT MQM; 80. SummEval

**Top 50:** 1. Abt-Buy; 2. Amazon-Google; 4. Walmart-Amazon (+dirty); 5. DBLP-Scholar (+dirty); 6. HiTab; 8. MMTU; 9. Machamp (7 GEM tasks); 11. WikiTableQuestions; 12. WDC Products 2024 (hard negatives); 14. Papadakis-Christen Dn1-Dn8; 15. Alaska Camera (SIGMOD 2020); 17. RealHiTBench; 18. SUC (Table Meets LLM); 19. TabIS; 20. TableEval; 21. OpenSanctions Pairs; 23. OfficeQA Pro V2; 25. TabFact; 26. FeTaQA; 27. DBLP-ACM (+dirty); 28. TableBench; 29. WDC LSPC / Products-2017; 30. TAT-QA; 31. SciTab; 32. DocFinQA; 33. AIT-QA; 34. Beer (BeerAdvo-RateBeer); 35. TyDi QA GoldP; 36. FinQA; 37. iTunes-Amazon (+dirty); 38. DROP; 39. MGSM; 42. MiMoTable; 43. RobuT; 45. FEVEROUS; 47. QAMPARI; 50. MultiTabQA; 51. VitaminC; 52. Alaska Monitor/Notebook; 53. BizBench (SEC-Num etc.); 54. MusicBrainz 20K; 56. ConvFinQA; 57. NarrativeQA; 58. MLQA; 59. Company; 61. OfficeQA Pro/Full; 63. FinanceBench (150 open); 71. WMT MQM; 80. SummEval; 88. North Carolina Voters 5M


