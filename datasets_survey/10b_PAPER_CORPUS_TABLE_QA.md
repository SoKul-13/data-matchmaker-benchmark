# Paper corpus B: table QA, table fact verification, table understanding with LLMs, text-to-SQL (top 40 by citations + 60 supplementary)

Citation counts: Semantic Scholar Graph API `paper/batch`, 2026-09-14. "verified" = arXiv PDF downloaded and text-scanned for dataset names (34 of 40 core papers); the six marked (unv.) are from prior knowledge of the paper.

## Core 40 (citation-ranked)

| # | Paper | First author | Year | Venue | Cites | Family | Datasets evaluated on | URL |
|---|---|---|---|---|---|---|---|---|
| 1 | Program of Thoughts Prompting | Wenhu Chen | 2022 | TMLR 2023 | 1475 | hybrid/TQA | TabMWP, FinQA, ConvFinQA, TAT-QA (+GSM8K, AQuA, SVAMP) | arxiv 2211.12588 |
| 2 | BIRD | Jinyang Li | 2023 | NeurIPS D&B | 1185 | text-to-SQL | BIRD | arxiv 2305.03111 |
| 3 | TaPas | Herzig | 2020 | ACL | 924 | TQA | WTQ, SQA, WikiSQL | arxiv 2004.02349 |
| 4 | RAT-SQL | Bailin Wang | 2019 | ACL 2020 | 898 | text-to-SQL | Spider, WikiSQL | arxiv 1911.04942 |
| 5 | DIN-SQL | Pourreza | 2023 | NeurIPS | 871 | text-to-SQL | Spider, BIRD | arxiv 2304.11015 |
| 6 | TaBERT | Yin | 2020 | ACL | 843 | TQA/SQL | WTQ, Spider | arxiv 2005.08314 |
| 7 | FinQA | Zhiyu Chen | 2021 | EMNLP | 828 | hybrid | FinQA | arxiv 2109.00122 |
| 8 | DAIL-SQL | Dawei Gao | 2023 | PVLDB 2024 | 767 | text-to-SQL | Spider, Spider-Realistic, BIRD | arxiv 2308.15363 |
| 9 | TabFact | Wenhu Chen | 2019 | ICLR 2020 | 729 | TFV | TabFact | arxiv 1909.02164 |
| 10 | PICARD | Scholak | 2021 | EMNLP | 689 | text-to-SQL | Spider, CoSQL | arxiv 2109.05093 |
| 11 | TAT-QA | Fengbin Zhu | 2021 | ACL | 627 | hybrid | TAT-QA | arxiv 2105.07624 |
| 12 | StructGPT | Jinhao Jiang | 2023 | EMNLP | 623 | TU-LLM | WTQ, WikiSQL, TabFact, Spider (+variants) | arxiv 2305.09645 |
| 13 | TabMWP / PromptPG | Pan Lu | 2022 | ICLR 2023 | 466 | TQA math | TabMWP | arxiv 2209.14610 |
| 14 | HybridQA | Wenhu Chen | 2020 | Findings EMNLP | 438 | hybrid | HybridQA | arxiv 2004.07347 |
| 15 | RESDSQL | Haoyang Li | 2023 | AAAI | 411 | text-to-SQL | Spider + DK/Syn/Realistic | arxiv 2302.05965 |
| 16 | TAPEX | Qian Liu | 2021 | ICLR 2022 | 382 | TQA/TFV | WikiSQL, WTQ, SQA, TabFact | arxiv 2107.07653 |
| 17 | UnifiedSKG | Tianbao Xie | 2022 | EMNLP | 376 | multi-task | WTQ, WikiSQL, SQA, TabFact, FEVEROUS, HybridQA, FeTaQA, ToTTo, Spider, SParC, CoSQL, MultiModalQA | arxiv 2201.05966 |
| 18 | LEVER | Ansong Ni | 2023 | ICML | 375 | SQL/TQA | Spider, WTQ | arxiv 2302.08468 |
| 19 | CodeS | Haoyang Li | 2024 | SIGMOD | 343 | text-to-SQL | Spider, BIRD, variants, Bank-Financials, Aminer | arxiv 2402.16347 |
| 20 | Binder | Zhoujun Cheng | 2022 | ICLR 2023 | 334 | TU-LLM | WTQ, TabFact (+MultiModalQA) | arxiv 2210.02875 |
| 21 | Spider 2.0 | Fangyu Lei | 2024 | ICLR 2025 | 318 | text-to-SQL | Spider-2.0 | arxiv 2411.07763 |
| 22 | GraPPa | Tao Yu | 2020 | ICLR 2021 | 302 | SQL/TQA | Spider, WikiSQL, WTQ | arxiv 2009.13845 |
| 23 | MAC-SQL | Bing Wang | 2023 | COLING 2025 | 296 | text-to-SQL | BIRD, Spider | arxiv 2312.11242 |
| 24 | C3 | Xuemei Dong | 2023 | arXiv | 292 | text-to-SQL | Spider | arxiv 2307.07306 |
| 25 | Chain-of-Table | Zilong Wang | 2024 | ICLR | 289 | TU-LLM | WTQ, TabFact, FeTaQA | arxiv 2401.04398 |
| 26 | FeTaQA | Linyong Nan | 2021 | TACL 2022 | 289 | TQA | FeTaQA | arxiv 2104.00369 |
| 27 | ConvFinQA | Zhiyu Chen | 2022 | EMNLP | 287 | hybrid | ConvFinQA | arxiv 2210.03849 |
| 28 | DATER | Yunhu Ye | 2023 | SIGIR | 280 | TU-LLM | WTQ, TabFact, FeTaQA (unv.) | arxiv 2301.13808 |
| 29 | OTT-QA | Wenhu Chen | 2020 | ICLR 2021 | 280 | hybrid open | OTT-QA (unv.) | arxiv 2010.10439 |
| 30 | FEVEROUS | Rami Aly | 2021 | NeurIPS D&B | 274 | TFV | FEVEROUS (unv.) | arxiv 2106.05707 |
| 31 | CHESS | Talaei | 2024 | arXiv | 246 | text-to-SQL | BIRD, Spider (unv.) | arxiv 2405.16755 |
| 32 | Table Meets LLM (SUC) | Yuan Sui | 2023 | WSDM 2024 | 241 | TU-LLM | SUC, TabFact, HybridQA, SQA, FEVEROUS, ToTTo | arxiv 2305.13062 |
| 33 | LLMs are few(1)-shot table reasoners | Wenhu Chen | 2022 | Findings EACL 2023 | 241 | TU-LLM | WTQ, FeTaQA, TabFact, FEVEROUS | arxiv 2210.06710 |
| 34 | TableLlama / TableInstruct | Tianshu Zhang | 2023 | NAACL 2024 | 232 | TU-LLM | HiTab, FeTaQA, TabFact, HybridQA; OOD FEVEROUS, KVRET, ToTTo, WikiSQL, WTQ | arxiv 2311.09206 |
| 35 | CHASE-SQL | Pourreza | 2024 | ICLR 2025 | 215 | text-to-SQL | BIRD, Spider | arxiv 2410.01943 |
| 36 | ChatGPT zero-shot text-to-SQL eval | Aiwei Liu | 2023 | arXiv | 209 | SQL eval | Spider + DK/Realistic/Syn, SParC, CoSQL | arxiv 2303.13547 |
| 37 | Test-suite evaluation for text-to-SQL | Ruiqi Zhong | 2020 | EMNLP | 205 | SQL eval | Spider, SParC, CoSQL | arxiv 2010.02840 |
| 38 | MultiHiertt | Yilun Zhao | 2022 | ACL | 202 | hybrid | MultiHiertt (unv.) | arxiv 2206.01347 |
| 39 | HiTab | Zhoujun Cheng | 2021 | ACL 2022 | 197 | TQA | HiTab (unv.) | arxiv 2108.06712 |
| 40 | TableBench | Xianjie Wu | 2024 | AAAI 2025 | 176 | TU-LLM | TableBench | arxiv 2408.09174 |

Excluded despite citations: TabLLM (443, classification), ToTTo (468) and LogicNLG (184) (generation), surveys (do not evaluate).

## Supplementary (citation counts verified; dataset lists from knowledge unless stated)
WTQ paper (Pasupat 2015, 1094), SQA (283), WikiSQL/Seq2SQL (1631), Spider (2144); surveys: Hong 2024 (277), Fang 2024 (269), Shi 2024 (160), Dong 2022 (82), Zhu 2024 (63), Zhang 2024 (44); ChatDB 172; Rajkumar 2022 166 (Spider); KaggleDBQA 165; Li 2024 "Dawn of NL2SQL" 161 (Spider, BIRD); MCS-SQL 151; InfoTabs 148; ReAcTable 142 (WTQ, TabFact, FeTaQA); OmniSQL 123; TableLLM 112 (WTQ, TabFact, FeTaQA, OTT-QA, TAT-QA); TabPedia 95; DocFinQA 93; DTS-SQL 92; XiYan-SQL 86; AIT-QA 84; TableGPT2 83 (WTQ, TabFact, HiTab, FeTaQA, HybridQA, TableBench, BIRD, Spider); TableGPT 81; TableRAG 81; TableVQA-Bench 81; SQL-PaLM 77; TAP4LLM 60 (TabFact, HybridQA, SQA, ToTTo, FEVEROUS); SciTab 70; Open-WikiTable 69; Nan 2023 prompt design 67; TabSQLify 65 (WTQ, TabFact); Table-LLaVA/MMTab 65; Liu 2023 mixed self-consistency 65 (WTQ, TabFact); RobuT 63; MultiTabQA 63; Deng 2024 tables as texts/images 62; OmniTab 58 (WTQ); ReasTAP 55 (WTQ, WikiSQL, SQA, TabFact, FeTaQA, LogicNLG); Zhao 2023 complex table parsers 53 (HiTab, AIT-QA); DataBench 49; DB-GPT 46; OpenTab 46; Yang 2023 distillation 43; TempTabQA 42; CABINET 39 (WTQ, FeTaQA, WikiSQL); H-STAR 33; Cao 2023 API-assisted 32 (WTQ, HiTab, AIT-QA); TAT-LLM 25 (FinQA, TAT-QA, TAT-DQA); MMTU 23; TableEval 19; MiMoTable 18; SpreadsheetLLM 18; RealHiTBench 17; TabIS 15; TANQ 8; QTSumm 6.

## Dataset usage counts (core 40)

| Dataset | core papers | 2023+ | papers |
|---|---|---|---|
| Spider | 17 | 11 | RAT-SQL, TaBERT, PICARD, GraPPa, TestSuite, UnifiedSKG, DIN-SQL, DAIL-SQL, StructGPT, RESDSQL, LEVER, CodeS, MAC-SQL, C3, CHESS, CHASE-SQL, Liu-eval |
| WTQ | 12 | 5 | TaPas, TaBERT, TAPEX, UnifiedSKG, GraPPa, Binder, few(1)-shot, StructGPT, LEVER, Chain-of-Table, DATER, TableLlama |
| TabFact | 10 | 5 | TabFact, TAPEX, UnifiedSKG, Binder, few(1)-shot, StructGPT, Chain-of-Table, DATER, SUC, TableLlama |
| BIRD | 7 | 7 | BIRD, DIN-SQL, DAIL-SQL, CodeS, MAC-SQL, CHESS, CHASE-SQL |
| WikiSQL | 7 | 2 | TaPas, RAT-SQL, TAPEX, UnifiedSKG, GraPPa, StructGPT, TableLlama |
| FeTaQA | 6 | 3 | FeTaQA, UnifiedSKG, few(1)-shot, Chain-of-Table, DATER, TableLlama |
| FEVEROUS | 5 | 2 | FEVEROUS, UnifiedSKG, few(1)-shot, SUC, TableLlama |
| Spider variants | 5 | 5 | DAIL-SQL, StructGPT, RESDSQL, CodeS, Liu-eval |
| SQA | 4 | 1 | TaPas, TAPEX, UnifiedSKG, SUC |
| HybridQA | 4 | 2 | HybridQA, UnifiedSKG, SUC, TableLlama |
| CoSQL | 4 | 1 | PICARD, TestSuite, UnifiedSKG, Liu-eval |
| SParC | 3 | 1 | TestSuite, UnifiedSKG, Liu-eval |
| ToTTo | 3 | 2 | UnifiedSKG, SUC, TableLlama |
| HiTab | 2 | 1 | HiTab, TableLlama |
| TAT-QA | 2 | 0 | TAT-QA, PoT |
| FinQA | 2 | 0 | FinQA, PoT |
| ConvFinQA | 2 | 0 | ConvFinQA, PoT |
| TabMWP | 2 | 0 | TabMWP, PoT |
| Spider-2.0 | 1 | 1 | Spider 2.0 |
| TableBench | 1 | 1 | TableBench |
| SUC | 1 | 1 | SUC |
| OTT-QA | 1 | 0 | OTT-QA |
| MultiHiertt | 1 | 0 | MultiHiertt |
| AIT-QA, TAT-DQA, DocFinQA, DataBench, TableEval, RealHiTBench, MiMoTable, KaggleDBQA, SciTab, RobuT, Open-WikiTable, CRT-QA, MMTU, TabIS, MMTab, TableVQA, TANQ, TempTabQA, QTSumm, InfoTabs | 0 | 0 | supplementary rows only |

Takeaways: text-to-SQL (Spider, BIRD) dominates the citation-ranked core; the most-used table QA/TFV sets are WTQ, TabFact, WikiSQL, FeTaQA; the 2023+ subset concentrates on Spider, BIRD, WTQ, TabFact. Newer benchmarks (TableBench, MMTU, RealHiTBench, TableEval, DataBench) are too recent to have accumulated citations, so usage counts must be recency-adjusted or they are penalised for being new.
