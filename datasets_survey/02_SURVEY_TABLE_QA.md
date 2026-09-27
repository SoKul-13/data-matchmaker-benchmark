# Survey B: table question answering and table understanding (60 candidates, verified September 2026)

Legend: Adopt. W = widely used, N = niche. Score = family-internal 1–5 importance for a data-matching / data-reading benchmark. (unv.) = not verified by a fetched page.

| # | Name | Year | Source | Domain | Size | Answer type | Official metric | Licence | Download | Adopt. | Hard because | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | WikiTableQuestions (WTQ) | 2015 | Pasupat & Liang, ACL 2015 | Wikipedia | 2,108 tables / 22,033 q | short span, number, list | denotation accuracy | CC BY-SA 4.0 | HF stanfordnlp/wikitablequestions | W | compositional aggregation over messy cells; ~75 % best | 5 |
| 2 | WikiSQL | 2017 | Zhong et al., Salesforce | Wikipedia | 24,241 / 80,654 | simple SQL | LF / execution acc | BSD-3 | HF Salesforce/wikisql | W | trivial SQL, label noise | 2 (saturated) |
| 3 | SQA | 2017 | Iyyer et al., ACL 2017 | Wikipedia | 6,066 seq / 17,553 q | cell coordinates | seq/question acc | MSR licence | HF microsoft/msr_sqa | W | conversational coreference | 3 |
| 4 | TabFact | 2020 | Chen et al., ICLR 2020 | Wikipedia | 16k tables / 118k statements | boolean | accuracy | CC BY 4.0 | tabfact.github.io | W | numeric claims; ~90 % frontier | 4 |
| 5 | FEVEROUS | 2021 | Aly et al., NeurIPS D&B 2021 | Wikipedia text+tables | 87,026 claims | 3-way + evidence cells | FEVEROUS score | CC BY-SA 3.0 | HF fever/feverous | W | evidence-cell retrieval over full Wikipedia | 3 |
| 6 | InfoTabs | 2020 | Gupta et al., ACL 2020 | infoboxes | 23,738 pairs | 3-way NLI | accuracy | Apache-2.0 | github infotabs/infotabs | N/W | adversarial and cross-domain splits | 3 |
| 7 | HybridQA | 2020 | Chen et al., Findings EMNLP 2020 | Wikipedia table+passages | ~70k | short span | EM/F1 | (unv.) | github wenhuchen/HybridQA | W | multi-hop cell↔passage | 3 |
| 8 | OTT-QA | 2021 | Chen et al., ICLR 2021 | open-domain | 46k | short span | EM/F1 | MIT | github wenhuchen/OTT-QA | W | retrieval over 400k tables | 2 |
| 9 | FeTaQA | 2022 | Nan et al., TACL 2022 | Wikipedia | ~10k | free-form sentence + cells | BLEU/ROUGE/BERTScore | CC BY-SA 4.0 | github Yale-LILY/FeTaQA | W | integrate cells into fluent answer | 3 |
| 10 | ToTTo | 2020 | Parikh et al., EMNLP 2020 | Wikipedia | 136k | sentence from highlighted cells | BLEU/PARENT | CC BY-SA 3.0 | github google-research-datasets/ToTTo | W | faithfulness | 2 |
| 11 | HiTab | 2022 | Cheng et al., ACL 2022 | statistics reports | 3,597 / 10,672 | span/number | execution acc | C-UDA 1.0 | github microsoft/HiTab | W | hierarchical headers | 5 |
| 12 | AIT-QA | 2022 | Katsis et al., NAACL Industry 2022 | airline 10-K | 116 / 515 | cell value | accuracy | (unv.) | github IBM/AITQA | N | hierarchical, KPI jargon | 4 |
| 13 | TAT-QA | 2021 | Zhu et al., ACL 2021 | annual reports | 2,757 / 16,552 | span, multi-span, number, count | EM/F1 | CC BY 4.0 | HF next-tat/TAT-QA | W | hybrid arithmetic, scale | 4 |
| 14 | TAT-DQA | 2022 | Zhu et al., ACM MM 2022 | PDF pages | 16,558 | span/number | EM/F1 | CC BY 4.0 | HF next-tat/TAT-DQA | N | document layout | 3 |
| 15 | FinQA | 2021 | Chen et al., EMNLP 2021 | S&P 500 reports | 8,281 | number via program | execution acc | MIT | github czyssrs/FinQA | W | multi-step arithmetic; label noise | 4 |
| 16 | ConvFinQA | 2022 | Chen et al., EMNLP 2022 | finance | 14,115 turns | number | execution acc | MIT | github czyssrs/ConvFinQA | W | conversational chaining | 3 |
| 17 | MultiHiertt | 2022 | Zhao et al., ACL 2022 | finance | ~10.4k | number/span | EM/F1 | (unv.) | github psunlpgroup/MultiHiertt (Drive) | W | multiple hierarchical tables | 4 |
| 18 | DocFinQA | 2024 | Reddy et al., ACL 2024 | full 10-K | 7,437 | number | accuracy | MIT | HF kensho/DocFinQA | N | 123k-word contexts | 3 |
| 19 | TabMWP | 2023 | Lu et al., ICLR 2023 | grade-school math | 38,431 | number/MC | accuracy | CC BY-NC-SA 4.0 | github lupantech/PromptPG | W | near ceiling; NC licence | 2 |
| 20 | TableBench | 2025 | Wu et al., AAAI 2025 | mixed | 886 test | number/text/chart code | acc, ROUGE-L, pass@1 | Apache-2.0 | HF Multilingual-Multimodal-NLP/TableBench | W | analysis + viz; top 79 vs human 86 | 4 |
| 21 | DataBench (SemEval-2025 T8) | 2025 | Osés Grijalba et al. | Kaggle-like | 65 datasets / 1,308 q | bool/number/category/list | accuracy | MIT | HF cardiffnlp/databench | W | needs code execution; saturated with code | 3 |
| 22 | TableEval | 2025 | Zhu et al., EMNLP 2025 | zh/en spreadsheets | 617 / 2,325 | free-form | SEAT (LLM-judged) | Apache-2.0 | HF wenge-research/TableEval | N | multilingual nested Excel | 4 |
| 23 | RealHiTBench | 2025 | Wu et al., Findings ACL 2025 | 24 domains, hierarchical | 708 / 3,752 | mixed | acc / LLM-judge | CC BY-NC 4.0 data | HF spzy/RealHiTBench | N (rising) | nested sub-tables, merged headers | 5 |
| 24 | MiMoTable | 2025 | Li et al., COLING 2025 | zh/en spreadsheets | 428 / 1,719 | mixed | accuracy | (unv.) | data link not located | N | multi-sheet | 4 (unv.) |
| 25 | Spider 1.0 | 2018 | Yu et al., EMNLP 2018 | 200 SQL DBs | 10,181 | SQL | EM/EX | CC BY-SA 4.0 | HF xlangai/spider | W | saturated ~90 % | 2 |
| 26 | Spider 2.0 | 2025 | Lei et al., ICLR 2025 | enterprise SQL | 632 tasks | SQL/result | execution acc | MIT | github xlang-ai/Spider2 | W | >3,000 columns, dialects | 3 |
| 27 | BIRD | 2023 | Li et al., NeurIPS 2023 | 95 DBs | 12,751 | SQL | EX, R-VES | CC BY-SA 4.0 | bird-bench.github.io | W | dirty values; 82 vs human 93 | 3 |
| 28 | KaggleDBQA | 2021 | Lee et al., ACL 2021 | 8 Kaggle DBs | 272 | SQL | EX | (unv.) | github chiahsuan156/KaggleDBQA | N | abbreviated columns | 2 |
| 29 | TabMCQ | 2016 | Jauhar et al. | science | 9,092 MC | MC | accuracy | (unv.) | MSR (unv.) | N | dated | 1 |
| 30 | TabPert | 2021 | Jain et al., EMNLP 2021 demo | infoboxes | platform | NLI | accuracy | (unv.) | github utahnlp/tabpert | N | counterfactual edits | 2 |
| 31 | SciTab | 2023 | Lu et al., EMNLP 2023 | paper tables | 1,224 | 3-way | macro-F1 | (unv.) | github XinyuanLu00/SciTab | N | expert numeric claims | 4 |
| 32 | SEM-TAB-FACTS | 2021 | Wang et al., SemEval 2021 | paper tables | ~5k statements | 3-way + evidence cells | F1 | (unv.) | competition site | N | evidence-cell subtask | 3 |
| 33 | PubHealthTab | 2022 | Akhtar et al., Findings NAACL 2022 | public-health web tables | ~1.9k | 3-way | F1 | (unv.) | github mubasharaak/pubhealthtab | N | scraped tables | 3 |
| 34 | LogicNLG | 2020 | Chen et al., ACL 2020 | Wikipedia | 37k sentences | logical sentence | BLEU, NLI-Acc | MIT | github wenhuchen/LogicNLG | W | generation | 2 |
| 35 | Logic2Text | 2020 | Chen et al., Findings EMNLP 2020 | Wikipedia | 10,753 | sentence from logical form | BLEU + exec | (unv.) | github czyssrs/Logic2Text | N | logical forms | 2 |
| 36 | TANQ | 2025 | Akhtar et al., TACL 2025 | Wikipedia/Wikidata | (unv.) | table generation + attribution | cell F1 | CC BY 4.0 | github google-deepmind/tanq | N | assemble tables from sources | 3 |
| 37 | TempTabQA | 2023 | Gupta et al., EMNLP 2023 | infoboxes | 1,208 / 11,454 | span/number | EM/F1 | (unv.) | zenodo 10022927 | N | temporal arithmetic | 3 |
| 38 | MMTab | 2024 | Zheng et al., ACL 2024 | table images | ~45k | mixed | per-task | (unv.) | github SpursGoZmy/Table-LLaVA | W (VLM) | vision | 2 |
| 39 | TableVQA-Bench | 2024 | Kim et al. | Wikipedia+finance images | 1,500 | short/boolean | accuracy | CC BY 4.0 | HF terryoo/TableVQA-Bench | N | rendered tables | 2 |
| 40 | RobuT | 2023 | Zhao et al., ACL 2023 | WTQ/WikiSQL/SQA perturbed | ~143k | short/cell | accuracy drop | (unv.) | github yilunzhao/RobuT | N | header/content perturbations | 4 |
| 41 | Open-WikiTable | 2023 | Kweon et al., Findings ACL 2023 | open-domain | 67k | short+SQL | EM/EX | (unv.) | github sean0042/Open_WikiTable | N | retrieval | 2 |
| 42 | CRT-QA | 2023 | Zhang et al., EMNLP 2023 | WTQ tables | ~2k | short/unanswerable | accuracy | (unv.) | HF ZhehaoZhang/CRT-QA | N | unanswerable items | 3 |
| 43 | SQUALL | 2020 | Shi et al., Findings EMNLP 2020 | WTQ subset | 11,276 | SQL | EX | (unv.) | github tzshi/squall | N | question→SQL alignments | 2 |
| 44 | TableInstruct | 2024 | Zhang et al., NAACL 2024 | 14 datasets | 2.6M train | mixed | per-task | (unv.) | HF osunlp/TableInstruct | W (train) | repackaged | 2 |
| 45 | QTSumm | 2023 | Zhao et al., Findings EMNLP 2023 | Wikipedia | 7,111 | query summary | ROUGE | MIT | HF yale-nlp/QTSumm | N | generation | 2 |
| 46 | MMTU | 2025 | Xing et al., NeurIPS 2025 D&B | 52 datasets, 25 task types | 28,136 | mixed | task acc | MIT | HF MMTU-benchmark/MMTU | W (rising) | expert data-management tasks; GPT-5 0.70 | 5 |
| 47 | MMQA (multi-table) | 2025 | Wu et al., ICLR 2025 | Spider-derived | 3,312 tables / 5,000 | answer + SQL + PK/FK | EM/EX/key acc | (unv.) | repo not located | N | foreign-key discovery | 4 (unv.) |
| 48 | TQA-Bench | 2026 | Qiu et al., IEEE TBD | multi-table relational | (unv.) | short/number | accuracy | (unv.) | github Relaxed-System-Lab/TQA-Bench | N | long context | 3 |
| 49 | TReB | 2026 | Li et al., SIGIR 2026 | mixed, 26 tasks | – | mixed | EM/BLEU/ROUGE/judge | Apache-2.0 | github JT-LM/jiutian-treb | N | partly repackaged | 3 |
| 50 | ReasonTabQA | 2026 | Pan et al. | industrial zh/en | 1,932 tables | answer + chain | accuracy | (unv.) | not located | N | multi-table nested | 3 (unv.) |
| 51 | TabVerse | 2026 | Ahsan et al. | aligned Wikipedia sets | 700 | QA/structure | accuracy | (unv.) | not located | N | format invariance | 3 (unv.) |
| 52 | SUC (Table Meets LLM) | 2024 | Sui et al., WSDM 2024 | 7 structural tasks | ~1.5k/task | cell lookup, row retrieval, size | accuracy | (unv.) | github microsoft/TableProvider | N/W | coordinate lookup that LLMs miss | 5 |
| 53 | TabIS | 2024 | Pang et al., Findings ACL 2024 | Wikipedia + multi-table | (unv.) | binary choice | accuracy | (unv.) | github coszero/TabIS | N | deceptive options, distractor tables | 4 |
| 54 | Finch | 2025 | Dong et al. | finance spreadsheets | 384 tasks / 1,710 sheets | workflow outputs | human-judged | (unv.) | not located | N | GPT-5.1 Pro 38 % | 3 |
| 55 | LakeQA | 2026 | Wang et al. | data lake 9.5 TB | (unv.) | short | EM | (unv.) | not located | N | search-dominated | 2 |
| 56 | TABLET | 2025 | Alonso et al. | visual tables | 4M | mixed | per-task | (unv.) | not located | N | vision | 2 |
| 57 | TableQAKit | 2023 | Lei et al. | toolkit | – | – | – | (unv.) | github lfy79001/TableQAKit | N | – | 1 |
| 58 | TabLLM benchmarks | 2023 | Hegselmann et al., AISTATS 2023 | tabular classification | 9 datasets | class label | AUC | per-dataset | github clinicalml/TabLLM | W (tab-ML) | not QA | 1 |
| 59 | OpenTab | 2024 | Kong et al., ICLR 2024 | method | – | – | – | – | github amazon-science | N | – | 1 |
| 60 | TabSQLify | 2024 | Nahid & Rafiei, NAACL 2024 | method | – | – | – | – | arXiv 2404.10150 | N | – | 1 |

**Canonical:** WTQ, WikiSQL, SQA, TabFact, FeTaQA, HybridQA/OTT-QA, HiTab, TAT-QA, FinQA/ConvFinQA, Spider, BIRD; TableBench is the de-facto hard TableQA leaderboard since 2024 and MMTU is becoming the omnibus.
**Saturated for frontier models:** WikiSQL, Spider 1.0, TabMWP, SQA, DataBench with code execution, TabFact (~90 %), ToTTo/LogicNLG (generation metrics), Spider 2.0-Snow under agent scaffolds.
**Currently hard:** MMTU (~0.70), TableBench (79 vs 86 human), RealHiTBench, TableEval, MiMoTable, MultiHiertt, DocFinQA, BIRD test, SciTab, SUC and TabIS (structural probes), Finch (38 %), LakeQA (18 %).
**Highest leverage for data matching/reading:** SUC + TabIS (lookup/structure), HiTab + RealHiTBench + AIT-QA (hierarchical cell matching), RobuT (robustness), MMQA (key matching), MMTU (schema/entity subtasks), WTQ and TabFact as calibrated classics. Caveat: TableInstruct/TReB/MMTab repackage older sets (contamination/overlap).

Sources: see 09_SOURCES.md (section B).
