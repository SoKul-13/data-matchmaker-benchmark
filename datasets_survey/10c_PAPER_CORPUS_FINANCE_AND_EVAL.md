# Paper corpus C: financial-document QA / FinLLM benchmarks (area 1) and LLM evaluation metrics / benchmark meta-evaluation (area 2)

Citation counts: Semantic Scholar `paper/batch`, 2026-09-14 (search endpoint rate-limited; OpenAlex fallback for Colombo 2022). Surveys excluded from cores (they evaluate on nothing). (unv.) = dataset list not re-checked against the PDF.

## Area 1 core 18

| # | Paper | First author | Year | Venue | Cites | Datasets evaluated on / introduced |
|---|---|---|---|---|---|---|
| 1 | BloombergGPT | Shijie Wu | 2023 | arXiv | 1505 | FPB, FiQA-SA, Headline, FIN-NER, ConvFinQA; BBH, MMLU |
| 2 | FinQA | Zhiyu Chen | 2021 | EMNLP | 828 | introduces FinQA |
| 3 | TAT-QA | Fengbin Zhu | 2021 | ACL | 627 | introduces TAT-QA |
| 4 | FinGPT (framework) | Hongyang Yang | 2023 | arXiv | 479 | FPB, FiQA-SA, TFNS (unv.) |
| 5 | PIXIU / FinMA / FLARE | Qianqian Xie | 2023 | NeurIPS D&B | 312 | FPB, FiQA-SA, Headline, FIN-NER, FinQA, ConvFinQA, BigData22, ACL18, CIKM18 |
| 6 | FinanceBench | Pranab Islam | 2023 | arXiv | 306 | introduces FinanceBench |
| 7 | ConvFinQA | Zhiyu Chen | 2022 | EMNLP | 287 | introduces ConvFinQA |
| 8 | RAG for financial sentiment | Boyu Zhang | 2023 | ICAIF | 214 | TFNS, FPB |
| 9 | FinBen | Qianqian Xie | 2024 | NeurIPS D&B | 208 | introduces FinBen (36–42 sets incl. FinQA, ConvFinQA, TAT-QA, ECTSum) |
| 10 | MultiHiertt | Yilun Zhao | 2022 | ACL | 202 | introduces MultiHiertt |
| 11 | Are ChatGPT/GPT-4 general-purpose financial solvers? | Xianzhi Li | 2023 | EMNLP Industry | 128 | FPB, FiQA-SA, TweetFinSent, Headlines, FIN3, REFinD, FinQA, ConvFinQA |
| 12 | InvestLM | Yi Yang | 2023 | arXiv | 127 | FPB, FiQA-SA, FinQA, ECTSum, FinSent, FOMC, ESG, FLS |
| 13 | FinGPT instruction-tuning benchmark | Neng Wang | 2023 | NeurIPS WS | 121 | FPB, FiQA-SA, TFNS, Headline, FIN-NER (unv.) |
| 14 | TAT-DQA | Fengbin Zhu | 2022 | ACM MM | 116 | introduces TAT-DQA |
| 15 | ECTSum | Rajdeep Mukherjee | 2022 | EMNLP | 95 | introduces ECTSum |
| 16 | DocFinQA | Varshini Reddy | 2024 | ACL | 93 | introduces DocFinQA |
| 17 | Financial report chunking for RAG | Jimeno-Yepes | 2024 | arXiv | 86 | FinanceBench |
| 18 | Fin-R1 | Zhaowei Liu | 2025 | arXiv | 83 | FinQA, ConvFinQA, TFNS (unv.) |

Excluded: surveys Li 2023 (509), Lee 2024 (178), Nie 2024 (174); Kim "Financial statement analysis with LLMs" (85, proprietary data); Program of Thoughts (already corpus B #1).
Supplementary (counts verified): AlphaFin 82, FinTextQA 78, FinEval 76, DocMath-Eval 61, FinTral 61, FinanceMath 56, Open-FinLLMs 51, Fin-Fact 48, BizBench 39, FinAgentBench 35, Callanan CFA 32, OfficeQA Pro 29 (Databricks 2026, arxiv 2603.08655), FinDER 29, TAT-LLM 25, SEC-QA 24, FinReport 23, XBRL Agent 21, FinTagging 4.

## Area 2 core 12

| # | Paper | First author | Year | Venue | Cites | Datasets evaluated on / introduced |
|---|---|---|---|---|---|---|
| 1 | Judging LLM-as-a-judge (MT-Bench, Chatbot Arena) | Lianmin Zheng | 2023 | NeurIPS D&B | 11152 | introduces MT-Bench human judgments, Arena conversations; MMLU, TruthfulQA |
| 2 | BERTScore | Tianyi Zhang | 2019 | ICLR 2020 | 9579 | WMT16–18 metrics, MSCOCO, PAWS-QQP |
| 3 | G-Eval | Yang Liu | 2023 | EMNLP | 3123 | SummEval, Topical-Chat, QAGS |
| 4 | BIG-bench | Srivastava | 2022 | TMLR 2023 | 2639 | introduces BIG-bench |
| 5 | HELM | Percy Liang | 2022 | TMLR 2023 | 2048 | 16 core scenarios (BoolQ, NarrativeQA, NQ, QuAC, MS MARCO, XSUM, CNN/DM, …) + GSM8K, MATH |
| 6 | BLEURT | Sellam | 2020 | ACL | 2005 | WMT17–19 metrics, WebNLG |
| 7 | COMET | Rei | 2020 | EMNLP | 1718 | WMT17–19 DA, QT21, MQM |
| 8 | Chatbot Arena | Wei-Lin Chiang | 2024 | ICML | 1532 | introduces Arena (240K votes); MT-Bench, MMLU, AlpacaEval |
| 9 | LLMs are not fair evaluators | Peiyi Wang | 2023 | ACL 2024 | 1268 | Vicuna Bench |
| 10 | Can LLMs be an alternative to human evaluations? | Cheng-Han Chiang | 2023 | ACL | 1087 | WritingPrompts |
| 11 | SummEval | Fabbri | 2021 | TACL | 1078 | introduces SummEval |
| 12 | Length-controlled AlpacaEval | Dubois | 2024 | COLM | 954 | AlpacaEval 2.0; Chatbot Arena |

Supplementary (counts verified): Mirage 768, Wang "ChatGPT as NLG evaluator" 657, Prometheus 649, GEMBA 596, Arena-Hard 528, Prometheus 2 527, GPTScore 495, RewardBench 475, Sainz 428, TRUE 397, UniEval 391, LLMBar 350, JudgeBench 337, Tangled up in BLEU 315, tinyBenchmarks 313, Judging the Judges 256, Lessons from the Trenches 198, Elo Uncovered 90, Efficient Benchmarking 74, Leaderboard Illusion 67, BenchBench 23, Colombo 2022 (S2 count unavailable; OpenAlex 22).

## Dataset usage counts (area 1 core 18)

| Dataset | core | 2023+ | papers |
|---|---|---|---|
| FPB | 8 | 8 | BloombergGPT, FinGPT, PIXIU, Zhang-RAG, FinBen, Li, InvestLM, FinGPT-IT |
| FiQA-SA | 7 | 7 | BloombergGPT, FinGPT, PIXIU, FinBen, Li, InvestLM, FinGPT-IT |
| FinQA | 6 (+1 derived) | 5 | FinQA, PIXIU, FinBen, Li, InvestLM, Fin-R1 (+DocFinQA) |
| ConvFinQA | 6 | 5 | ConvFinQA, BloombergGPT, PIXIU, FinBen, Li, Fin-R1 |
| Headlines | 5 | 5 | BloombergGPT, PIXIU, FinBen, Li, FinGPT-IT |
| FIN-NER | 5 | 5 | as Headlines |
| TFNS | 4 | 4 | FinGPT, Zhang-RAG, FinGPT-IT, Fin-R1 |
| ECTSum | 3 | 2 | ECTSum, InvestLM, FinBen |
| TAT-QA | 2 | 1 | TAT-QA, FinBen |
| FinanceBench | 2 | 2 | FinanceBench, Report Chunking |
| BigData22/ACL18/CIKM18 | 2 | 2 | PIXIU, FinBen |
| FOMC | 2 | 2 | FinBen, InvestLM |
| MultiHiertt | 1 | 0 | MultiHiertt |
| TAT-DQA | 1 | 0 | TAT-DQA |
| DocFinQA | 1 | 1 | DocFinQA |

## Dataset usage counts (area 2 core 12)

| Dataset | core | 2023+ | papers |
|---|---|---|---|
| WMT metrics shared tasks | 3 | 0 | BERTScore, BLEURT, COMET |
| Chatbot Arena votes | 3 | 3 | MT-Bench paper, Arena, LC-AlpacaEval |
| MMLU | 3 | 2 | HELM, MT-Bench paper, Arena |
| MT-Bench | 2 | 2 | MT-Bench paper, Arena |
| SummEval | 2 | 1 | SummEval, G-Eval |
| TruthfulQA | 2 | 1 | HELM, MT-Bench paper |
| AlpacaEval 2.0 | 2 | 2 | Arena, LC-AlpacaEval |
| BIG-bench | 1 | 0 | BIG-bench |
| HELM core scenarios (BoolQ, NarrativeQA, NQ, …) | 1 | 0 | HELM |
| Topical-Chat, QAGS | 1 each | 1 | G-Eval |
| Vicuna Bench | 1 | 1 | Wang |
| MQM, QT21 | 1 each | 0 | COMET |
With supplementary papers added: SummEval +4 (GPTScore, UniEval, TRUE, Wang), MT-Bench +5, Chatbot Arena +3, Vicuna Bench +2, TRUE introduces its 11-set suite, LLMBar and JudgeBench introduce themselves, RewardBench includes LLMBar.

Caveats: S2 splits some papers across records (HELM 12 vs 2048; TRUE 8 vs 397); main records reported. Colombo 2022 count unavailable.
