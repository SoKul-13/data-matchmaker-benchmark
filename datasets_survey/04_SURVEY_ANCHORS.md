# Survey D: general anchors for calibrating an answer-scoring metric (65 candidates, verified September 2026)

Importance = value as a calibration anchor for the scorer (not as a capability benchmark), 1–5. (unv.) = not verified by a fetched page.

| # | Name | Group | Year | Source | Size | Gold type | Official metric | Licence | Download | Adoption | Saturation | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GSM8K | numeric | 2021 | Cobbe et al., OpenAI | 1,319 test | number | EM | MIT | HF openai/gsm8k (clean test: madrylab/gsm8k-platinum) | ubiquitous | saturated (>95 %) | 5 |
| 2 | GSM-Hard | numeric | 2023 | Gao et al., ICML 2023 | 1,319 | large number | EM | (unv.) | HF reasoning-machines/gsm-hard | moderate | not saturated w/o tools | 3 |
| 3 | MATH / MATH-500 | numeric | 2021 | Hendrycks et al., NeurIPS D&B | 5k / 500 | \boxed expression | EM after normalisation | MIT | HF hendrycks/competition_math | ubiquitous | near-saturated | 4 |
| 4 | SVAMP | numeric | 2021 | Patel et al., NAACL 2021 | 1,000 | number | accuracy | MIT | github arkilpatel/SVAMP | high | near ceiling | 3 |
| 5 | ASDiv | numeric | 2020 | Miao et al., ACL 2020 | 2,305 | number + unit | accuracy | CC BY-NC 4.0 | github chaochun/nlu-asdiv-dataset | moderate | near ceiling | 3 |
| 6 | MultiArith | numeric | 2015 | Roy & Roth | 600 | number | accuracy | (unv.) | HF ChilleD/MultiArith | historic | saturated | 2 |
| 7 | MAWPS | numeric | 2016 | Koncel-Kedziorski et al. | ~2.4k | number | accuracy | (unv.) | github sroy9/mawps | historic | saturated | 2 |
| 8 | AQuA-RAT | numeric MC | 2017 | Ling et al., ACL 2017 | 254 test | MC | accuracy | Apache 2.0 | HF deepmind/aqua_rat | high | high | 2 |
| 9 | DROP | numeric/span | 2019 | Dua et al., NAACL 2019 | 9.5k dev | number/date/spans | EM + F1 (typed script) | CC BY-SA 4.0 | HF ucinlp/drop | high | ~90 F1 | 4 |
| 10 | NumGLUE | numeric mix | 2022 | Mishra et al., ACL 2022 | 8 tasks | number/span/label | per-task | ODC-By | github allenai/numglue | low–mod | mixed | 3 |
| 11 | MathQA | numeric MC | 2019 | Amini et al., NAACL 2019 | 3k test | MC | accuracy | Apache 2.0 | HF allenai/math_qa | moderate | noisy | 2 |
| 12 | TabMWP | numeric table | 2023 | Lu et al., ICLR 2023 | 38,431 | typed (INT/DEC/EXTR/BOOL/MC) | accuracy by class | CC BY-NC-SA 4.0 | github lupantech/PromptPG | moderate | >90 % | 4 |
| 13 | FinanceMath | numeric finance | 2024 | Zhao et al., ACL 2024 | 1,200 | float 3 dp | tolerance acc | MIT | HF yale-nlp/FinanceMath | growing | not saturated | 5 |
| 14 | MGSM | numeric multilingual | 2022 | Shi et al., ICLR 2023 | 250 × 11 langs | number | EM | CC BY-SA 4.0 | HF juletxara/mgsm | high | near ceiling | 4 |
| 15 | GSM-Plus | numeric adversarial | 2024 | Li et al., ACL 2024 | 10,552 | number / no-answer | accuracy | CC BY-SA 4.0 (no training) | HF qintongli/GSM-Plus | moderate | not saturated | 3 |
| 16 | BoolQ | boolean | 2019 | Clark et al., NAACL 2019 | 3,270 dev | yes/no | accuracy | CC BY-SA 3.0 | HF google/boolq | ubiquitous | saturated | 5 |
| 17 | StrategyQA | boolean | 2021 | Geva et al., TACL 2021 | 2,780 | yes/no | accuracy | MIT | github eladsegal/strategyqa | high | ~85 % | 3 |
| 18 | FEVER (label) | 3-way | 2018 | Thorne et al., NAACL 2018 | 185k | S/R/NEI | label acc | CC BY-SA 3.0 | HF fever/fever | ubiquitous | near ceiling | 3 |
| 19 | SciFact | 3-way | 2020 | Wadden et al., EMNLP 2020 | 1,409 | S/C/NEI | label F1 | CC BY-NC 2.0 | HF allenai/scifact | moderate | not saturated | 2 |
| 20 | VitaminC | 3-way contrastive | 2021 | Schuster et al., NAACL 2021 | 489k | S/R/NEI | accuracy | CC BY-SA 3.0 | HF tals/vitaminc | moderate | challenging pairs | 3 |
| 21 | PUBHEALTH | 4-way | 2020 | Kotonya & Toni, EMNLP 2020 | 12,288 | true/false/unproven/mixture | acc, F1 | MIT | HF ImperialCollegeLondon/health_fact | low–mod | not saturated | 2 |
| 22 | ANLI | NLI | 2020 | Nie et al., ACL 2020 | 163k | 3-way | accuracy | CC BY-NC 4.0 | HF facebook/anli | high | ~80 | 2 |
| 23 | RTE | NLI | 2019 | SuperGLUE | 3k | binary | accuracy | (unv.) | HF aps/super_glue rte | ubiquitous | saturated | 2 |
| 24 | TabFact | boolean table | 2020 | Chen et al., ICLR 2020 | 118k | entailed/refuted | accuracy | CC BY 4.0 | HF ibm-research/tab_fact | high | ~90 % | 4 |
| 25 | SQuAD 1.1/2.0 | span | 2016/18 | Rajpurkar et al. | 11,873 dev (2.0) | span / no-answer | EM + F1 (official script) | CC BY-SA 4.0 | HF rajpurkar/squad_v2 | ubiquitous | saturated | 5 |
| 26 | Natural Questions (short/open) | span | 2019 | Kwiatkowski et al., TACL 2019 | 7,830 dev | short spans + yes/no + null | EM/F1 | CC BY-SA 3.0 | HF google-research-datasets/nq_open | ubiquitous | open-book near ceiling | 4 |
| 27 | TriviaQA | entity + aliases | 2017 | Joshi et al., ACL 2017 | 17.2k test | entity + alias list | EM/F1 over aliases | unknown | HF mandarjoshi/trivia_qa | ubiquitous | ~90 % closed-book | 4 |
| 28 | WebQuestions | list | 2013 | Berant et al., EMNLP 2013 | 2,032 test | list | set F1 | unknown | HF stanfordnlp/web_questions | historic | moderate | 3 |
| 29 | HotpotQA | span/yes-no | 2018 | Yang et al., EMNLP 2018 | 7.4k dev | span or yes/no | EM/F1 | CC BY-SA 4.0 | HF hotpotqa/hotpot_qa | ubiquitous | not saturated | 4 |
| 30 | QuAC | conv. span | 2018 | Choi et al., EMNLP 2018 | 98k | span/no-answer | F1, HEQ | CC BY-SA 4.0 (conflict MIT) | HF allenai/quac | moderate | – | 2 |
| 31 | AmbigQA | list | 2020 | Min et al., EMNLP 2020 | 2,002 dev | answer set | F1 | CC BY-SA 3.0 | HF sewon/ambig_qa | moderate | not saturated | 3 |
| 32 | QAMPARI | list | 2022 | Amouyal et al. | 1,000 test | entity list | P/R/F1 thresholded | CC0 | github samsam3232/qampari | moderate | not saturated | 4 |
| 33 | RoMQA | list | 2022 | Zhong et al. | dev/test | entity list | F1 | CC BY-NC | github facebookresearch/romqa | low | not saturated | 2 |
| 34 | WikiTableQuestions | table short | 2015 | Pasupat & Liang | 4.3k test | number/date/string list | denotation acc (typed evaluator) | CC BY-SA 4.0 | HF stanfordnlp/wikitablequestions | ubiquitous | ~75 % | 5 |
| 35 | FeTaQA | free-form table | 2022 | Nan et al., TACL 2022 | 2,003 test | sentence + cells | BLEU/ROUGE/BERTScore | CC BY-SA 4.0 | github Yale-LILY/FeTaQA | high | metric-bound | 5 |
| 36 | QTSumm | free-form table | 2023 | Zhao et al., Findings EMNLP 2023 | 7,111 | summary | ROUGE/BERTScore/AutoACU | MIT | HF yale-nlp/QTSumm | moderate | not saturated | 4 |
| 37 | ELI5 | long-form | 2019 | Fan et al., ACL 2019 | 270k | long answer | ROUGE-L | loader defunct | HF sentence-transformers/eli5 mirror | high historically | – | 1 |
| 38 | NarrativeQA | free-form short | 2018 | Kočiský et al., TACL 2018 | 46,765 | 2 references | BLEU/METEOR/ROUGE-L | Apache 2.0 | HF deepmind/narrativeqa | high | not saturated | 4 |
| 39 | MS MARCO NLG | free-form | 2018 | Nguyen et al., Microsoft | 101k dev | answers + wellFormed | BLEU/ROUGE-L | research only | HF microsoft/ms_marco | high | retired | 3 |
| 40 | CNN/DailyMail | summarisation | 2017 | See et al. | 11,490 test | highlights | ROUGE | Apache 2.0 | HF abisee/cnn_dailymail | ubiquitous | – | 2 |
| 41 | XSum | summarisation | 2018 | Narayan et al., EMNLP 2018 | 11.3k test | one sentence | ROUGE | unknown | HF EdinburghNLP/xsum | ubiquitous | – | 2 |
| 42 | WikiHow | summarisation | 2018 | Koupaee & Wang | 230k | headline | ROUGE | CC BY-NC-SA | TFDS wikihow | moderate | – | 1 |
| 43 | WMT MQM human eval | metric meta-eval | 2021–24 | Freitag et al., Google | 10–16 systems/pair, 4 years | MQM spans + scores | metric–human correlation | Apache 2.0 | github google/wmt-mqm-human-evaluation | gold standard | – | 4 |
| 44 | SummEval | metric meta-eval | 2021 | Fabbri et al., TACL 2021 | 1,600 summaries | 1–5 Likert × 4 | correlation | MIT | github Yale-LILY/SummEval | ubiquitous | – | 5 |
| 45 | RealSumm | metric meta-eval | 2020 | Bhandari et al., EMNLP 2020 | 100 docs × 25 systems | LitePyramid recall | correlation | CC BY 4.0 | github neulab/REALSumm | moderate | – | 4 |
| 46 | QAGS | factuality | 2020 | Wang et al., ACL 2020 | ~474 summaries | binary support | correlation | (unv.) | github W4ngatang/qags | high via TRUE | – | 3 |
| 47 | FRANK | factuality | 2021 | Pagnoni et al., NAACL 2021 | 2,250 | error taxonomy | correlation | MIT | github artidoro/frank | high via TRUE | – | 3 |
| 48 | TRUE | factuality suite | 2022 | Honovich et al., NAACL 2022 | 11 datasets | binary grounded | ROC-AUC | Apache 2.0 (code) | github google-research/true | high | – | 5 |
| 49 | USR | dialog meta-eval | 2020 | Mehri & Eskenazi, ACL 2020 | small | Likert | correlation | (unv.) | github Shikib/usr | moderate | – | 2 |
| 50 | LLMBar | judge eval | 2024 | Zeng et al., ICLR 2024 | 419 pairs | pairwise objective | judge accuracy | MIT | HF princeton-nlp/LLMBar | high | judges fail adversarial | 4 |
| 51 | MT-Bench human judgments | judge eval | 2023 | Zheng et al., NeurIPS 2023 | 3,360 human pairs | pairwise | agreement | CC BY 4.0 | HF lmsys/mt_bench_human_judgments | ubiquitous | ceiling ~80 % | 4 |
| 52 | Chatbot Arena conversations | preference | 2023 | Zheng et al. | 33k | vote | agreement | CC BY 4.0 prompts / NC outputs | HF lmsys/chatbot_arena_conversations | ubiquitous | – | 3 |
| 53 | HelpSteer3 | preference | 2025 | Wang et al., NVIDIA | 133k | graded −3..3 | RM accuracy | CC BY 4.0 | HF nvidia/HelpSteer3 | growing | – | 3 |
| 54 | JudgeBench | judge eval | 2025 | Tan et al., ICLR 2025 | 620 pairs | objective A>B | judge accuracy | MIT | HF ScalerLab/JudgeBench | growing | hard | 4 |
| 55 | RewardBench 2 | RM eval | 2025 | Lambert et al., AI2 | new data | best-of-4 | RM accuracy | ODC-By | HF allenai/reward-bench-2 | ubiquitous | v1 saturated | 3 |
| 56 | EvalGen | methodology | 2024 | Shankar et al., UIST 2024 | – | – | – | – | no public labels found | – | – | 1 |
| 57 | AlpacaEval human annotations | preference | 2023 | Dubois et al., NeurIPS 2023 | ~20k | pairwise + cross-annotations | agreement | CC BY-NC 4.0 (conflict) | HF tatsu-lab/alpaca_eval | high | – | 3 |
| 58 | XQuAD | multilingual span | 2020 | Artetxe et al., ACL 2020 | 1,190 × 11 | span | EM/F1 | CC BY-SA 4.0 | HF google/xquad | high | near ceiling | 4 |
| 59 | MLQA | multilingual span | 2020 | Lewis et al., ACL 2020 | 7 langs | span | EM/F1 per-language | CC BY-SA 3.0 | HF facebook/mlqa | high | near ceiling | 4 |
| 60 | TyDi QA GoldP | multilingual span | 2020 | Clark et al., TACL 2020 | 11 langs | span/yes-no/null | EM/F1 | Apache 2.0 | HF google-research-datasets/tydiqa | high | low-resource gaps | 4 |
| 61 | XTREME | aggregator | 2020 | Hu et al., ICML 2020 | 40 langs | per-task | per-task | mixed | HF google/xtreme | high | mixed | 2 |
| 62 | Belebele | multilingual MC | 2024 | Bandarkar et al., ACL 2024 | 900 × 122 | MC | accuracy | CC BY-SA 4.0 | HF facebook/belebele | high | gaps in low-resource | 2 |
| 63 | MultiTabQA | table-valued answers | 2023 | Pal et al., ACL 2023 | Spider-NQ/GeoQuery/Atis | a table | table/row/col/cell EM P/R/F1 | MIT | github kolk/MultiTabQA | low–mod | not saturated | 4 |
| 64 | mMARCO | multilingual passage QA | 2021 | Bonifacio et al. | translated | passage | MRR | (unv.) | HF unicamp-dl/mmarco | moderate | – | 2 (unv.) |
| 65 | Indic table QA | multilingual table | 2024 | arXiv 2410.03576 | (unv.) | (unv.) | (unv.) | (unv.) | (unv.) | low | – | 2 (unv.) |

Group notes (verbatim conclusions): GSM8K-Platinum as the clean numeric anchor; DROP and WTQ have typed official evaluators (the closest precedent to a mixed-type matcher); FinanceMath matches the finance domain with a stated rounding convention; TabMWP carries per-item answer-class labels (NC licence). BoolQ and TabFact are the boolean anchors; VitaminC's contrastive pairs probe small numeric edits. SQuAD's normalise-then-EM/F1 script is the short-answer standard; TriviaQA/NQ give alias lists; QAMPARI (CC0) is the cleanest list anchor. For free-form, FeTaQA/QTSumm are table-grounded; NarrativeQA has two references. For validating a scorer against humans: SummEval, RealSumm, TRUE (binary + ROC-AUC protocol), WMT MQM (segment-level gold standard); LLMBar and JudgeBench have objective pairwise labels. Multilingual: XQuAD, MLQA (ships per-language normalisation), TyDi QA GoldP, MGSM; no canonical multilingual table-QA set exists (a gap to state in the paper).

Licence caveats: NC or restricted: ASDiv, TabMWP, SciFact, ANLI, RoMQA, MS MARCO, WikiHow, AlpacaEval annotations, Arena outputs. Unknown: TriviaQA, WebQuestions, XSum, MultiArith, MAWPS, GSM-Hard, QAGS, USR, GSM8K-Platinum. Card conflicts: WTQ, QuAC, FeTaQA mirror, AlpacaEval, Belebele.
