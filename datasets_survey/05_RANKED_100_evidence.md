# Evidence-based ranking: the 100 datasets ranked by usage in the top-cited literature

Adoption (A) is now computed from the paper corpus (`paper_usage.csv`, built from `10_PAPER_CORPUS.md`): A = 0.7·5·min(1, ln(1+n)/ln(1+11)) + 0.3·5·min(1, n₂₀₂₃₊/7), where n = number of corpus papers (core + supplementary, see `10_PAPER_CORPUS.md`) evaluating on the dataset and n₂₀₂₃₊ those from 2023 on; 11 and 7 are the corpus 90th percentiles. Datasets absent from the corpus get A = 0 (or 1 if introduced 2025–26). General-purpose anchor sets (family ANC) keep the judgement A because the corpus was built around matching, tables, finance and LLM evaluation, not general QA; their corpus counts are still shown. Other criteria and weights unchanged from `00_SCORING_RUBRIC.md`. Dropped to reach 100: MP-DocVQA, TRUE, LakeBench, EDGAR-CORPUS, WikiSQL, Cora, DA-Code / DSBench, TabMWP, ChartQA, OAEI SPIMBENCH / KG track, Febrl 1-4.

| # | Dataset | Coverage family | Papers core+supp (2023+) | A (was) | Imp. | R | G | D | C | I | L | Licence | Cited by (short names) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Abt-Buy | EM-products | 14+3 (8) | 5.0 (5) | **85.0** | 5 | 3 | 4 | 5 | 2 | 5 | CC BY 4.0 | DeepMatcher; Ditto; Brunner; ZeroER; DL-Blocking; Rotom; JointBERT; HierGAT; R-SupCon; Zeakis; Sudowoodo; ComEM; Jellyfish; Peeters-LLM; supp: Steiner; AnyMatch |
| 2 | Amazon-Google | EM-products | 18+3 (11) | 5.0 (5) | **85.0** | 5 | 3 | 4 | 5 | 2 | 5 | CC BY 4.0 | DeepMatcher; DeepER; Kasai; Ditto; ZeroER; DL-Blocking; Rotom; Narayan; HierGAT; R-SupCon; Table-GPT; Zeakis; Sudowoodo; Zhang-preproc; Sparkly; ComEM; Jellyfis |
| 3 | Magneto GDC-SM | DI-schema/join | 1+0 (1) | 1.19 (3) | **84.6** | 5 | 5 | 5 | 5 | 3 | 5 | CC BY 4.0 | Magneto |
| 4 | Walmart-Amazon (+dirty) | EM-products | 16+3 (11) | 5.0 (5) | **83.0** | 5 | 3 | 4 | 5 | 2 | 4 | academic (Magellan) | DeepMatcher; DeepER; Ditto; Brunner; DL-Blocking; Rotom; Narayan; HierGAT; Table-GPT; Zeakis; Unicorn; Sudowoodo; Zhang-preproc; ComEM; Jellyfish; Peeters-LLM;  |
| 5 | DBLP-Scholar (+dirty) | EM-bibliographic | 18+3 (11) | 5.0 (5) | **82.0** | 5 | 3 | 3 | 5 | 2 | 5 | CC BY 4.0 | DeepMatcher; DeepER; Kasai; Ditto; Brunner; ZeroER; DL-Blocking; Rotom; JointBERT; HierGAT; Table-GPT; Zeakis; Unicorn; Sudowoodo; Zhang-preproc; ComEM; Jellyfi |
| 6 | HiTab | TQA-hierarchical/multi | 2+3 (4) | 3.38 (5) | **81.1** | 5 | 4 | 4 | 4 | 3 | 4 | C-UDA 1.0 | HiTab; TableLlama; supp: TableGPT2; Zhao-2023; Cao-2023 |
| 7 | Valentine | DI-schema/join | 3+0 (2) | 2.38 (5) | **81.1** | 5 | 5 | 4 | 5 | 2 | 4 | Apache-2.0 code | Valentine; Unicorn; Magneto |
| 8 | MMTU | TQA-general | 0+1 (1) | 1.19 (4) | **80.6** | 5 | 5 | 5 | 4 | 2 | 5 | MIT | supp: MMTU paper |
| 9 | Machamp (7 GEM tasks) | EM-products | 0+2 (0) | 1.55 (4) | **78.6** | 5 | 5 | 4 | 4 | 3 | 4 | BSD-3 / CC terms | supp: Machamp; PromptEM |
| 10 | SMAT (MIMIC Synthea CMS to OMOP) | DI-schema/join | 5+1 (5) | 3.81 (3) | **78.4** | 5 | 4 | 4 | 3 | 3 | 3 | unstated | Narayan; Zhang-preproc; Jellyfish; ReMatch; Parciak; supp: Matchmaker |
| 11 | WikiTableQuestions | TQA-general | 12+10 (13) | 5.0 (5) | **78.0** | 4 | 3 | 4 | 4 | 2 | 5 | CC BY-SA 4.0 | TaPas; TaBERT; TAPEX; UnifiedSKG; GraPPa; Binder; few(1)-shot; StructGPT; LEVER; Chain-of-Table; DATER; TableLlama; supp: WTQ paper; ReAcTable; TableLLM; TableG |
| 12 | WDC Products 2024 (hard negatives) | EM-products | 2+0 (2) | 1.98 (5) | **77.9** | 5 | 4 | 5 | 5 | 2 | 3 | unstated | ChatGPT-EM; Peeters-LLM |
| 13 | FinTagging (FinNI+FinCL) | DI-schema/join | 0+1 (1) | 1.19 (2) | **76.6** | 5 | 5 | 5 | 4 | 2 | 3 | unstated | supp: FinTagging paper |
| 14 | Papadakis-Christen Dn1-Dn8 | EM-other | 0+1 (1) | 1.19 (3) | **75.6** | 5 | 4 | 5 | 4 | 2 | 4 | unstated (Zenodo) | supp: Papadakis re-evaluation |
| 15 | Alaska Camera (SIGMOD 2020) | EM-products | 2+1 (0) | 1.95 (3) | **74.9** | 5 | 4 | 4 | 3 | 2 | 5 | MIT | JointBERT; HierGAT; supp: Alaska paper |
| 16 | Alaska schema-matching GT | DI-schema/join | 2+1 (0) | 1.95 (3) | **74.9** | 5 | 4 | 4 | 3 | 2 | 5 | MIT | JointBERT; HierGAT; supp: Alaska paper |
| 17 | RealHiTBench | TQA-hierarchical/multi | 0+1 (1) | 1.19 (3) | **74.6** | 5 | 5 | 5 | 3 | 3 | 2 | CC BY-NC 4.0 data | supp: RealHiTBench paper |
| 18 | SUC (Table Meets LLM) | TQA-general | 1+0 (1) | 1.19 (3) | **73.6** | 5 | 4 | 5 | 4 | 2 | 3 | unstated | SUC |
| 19 | TabIS | TQA-general | 0+1 (1) | 1.19 (2) | **73.6** | 5 | 4 | 5 | 4 | 2 | 3 | unstated | supp: TabIS paper |
| 20 | TableEval | TQA-freeform | 0+1 (1) | 1.19 (2) | **73.6** | 4 | 4 | 4 | 3 | 5 | 5 | Apache-2.0 | supp: TableEval paper |
| 21 | OpenSanctions Pairs | EM-people/org | 0+0 (0) | 1 (2) | **73.0** | 5 | 5 | 2 | 5 | 5 | 2 | CC BY-NC 4.0 | not in corpus |
| 22 | BIRD | TQA-sql | 7+2 (9) | 4.74 (5) | **72.2** | 3 | 3 | 4 | 4 | 2 | 5 | CC BY-SA 4.0 | BIRD; DIN-SQL; DAIL-SQL; CodeS; MAC-SQL; CHESS; CHASE-SQL; supp: Li-2024 Dawn; TableGPT2 |
| 23 | OfficeQA Pro V2 | FIN-document | 0+0 (0) | 1 (3) | **72.0** | 5 | 5 | 5 | 4 | 2 | 1 | CC BY-SA gated | not in corpus |
| 24 | TPC-DI (cell-level task) | DI-schema/join | 3+0 (2) | 2.38 (3) | **71.1** | 5 | 4 | 3 | 5 | 2 | 2 | CC BY-NC-ND spec | Valentine (source); Magneto; Unicorn (via Valentine) |
| 25 | TabFact | TQA-verification | 10+7 (11) | 5.0 (5) | **71.0** | 4 | 2 | 2 | 5 | 2 | 5 | CC BY 4.0 | TabFact; TAPEX; UnifiedSKG; Binder; few(1)-shot; StructGPT; Chain-of-Table; DATER; SUC; TableLlama; supp: ReAcTable; TableLLM; TableGPT2; TAP4LLM; TabSQLify; Li |
| 26 | FeTaQA | TQA-freeform | 6+5 (7) | 5.0 (5) | **71.0** | 3 | 4 | 3 | 3 | 2 | 5 | CC BY-SA 4.0 | FeTaQA; UnifiedSKG; few(1)-shot; Chain-of-Table; DATER; TableLlama; supp: ReAcTable; TableLLM; TableGPT2; ReasTAP; CABINET |
| 27 | DBLP-ACM (+dirty) | EM-bibliographic | 17+3 (10) | 5.0 (5) | **70.0** | 5 | 1 | 1 | 5 | 2 | 5 | CC BY 4.0 | DeepMatcher; DeepER; Kasai; Ditto; Brunner; ZeroER; DL-Blocking; Rotom; Narayan; HierGAT; Table-GPT; Zeakis; Sudowoodo; Zhang-preproc; ComEM; Jellyfish; Peeters |
| 28 | TableBench | TQA-general | 1+1 (2) | 1.98 (4) | **69.9** | 4 | 4 | 4 | 3 | 2 | 5 | Apache-2.0 | TableBench; supp: TableGPT2 |
| 29 | WDC LSPC / Products-2017 | EM-products | 5+1 (2) | 3.17 (4) | **69.5** | 5 | 2 | 3 | 4 | 2 | 4 | Common Crawl terms | Ditto; JointBERT; HierGAT; R-SupCon; Sparkly; supp: AnyMatch |
| 30 | TAT-QA | TQA-financial | 3+2 (3) | 3.17 (5) | **69.5** | 4 | 3 | 3 | 4 | 2 | 5 | CC BY 4.0 | TAT-QA; PoT; FinBen; supp: TableLLM; TAT-LLM |
| 31 | SciTab | TQA-verification | 0+1 (1) | 1.19 (3) | **68.6** | 4 | 4 | 5 | 4 | 2 | 3 | unstated | supp: SciTab paper |
| 32 | DocFinQA | TQA-financial | 7+1 (5) | 4.17 (3) | **68.5** | 3 | 3 | 4 | 3 | 2 | 5 | MIT | FinQA; PoT; PIXIU; FinBen; Li; InvestLM; Fin-R1; supp: TAT-LLM |
| 33 | AIT-QA | TQA-hierarchical/multi | 0+3 (2) | 2.38 (3) | **68.1** | 5 | 3 | 3 | 4 | 2 | 3 | unstated | supp: AIT-QA paper; Zhao-2023; Cao-2023 |
| 34 | Beer (BeerAdvo-RateBeer) | EM-other | 9+2 (7) | 5.0 (4) | **68.0** | 4 | 2 | 3 | 3 | 2 | 4 | Magellan | DeepMatcher; Ditto; Narayan; HierGAT; Table-GPT; Unicorn; Sudowoodo; Zhang-preproc; Jellyfish; supp: AnyMatch; Papadakis |
| 35 | TyDi QA GoldP | ANC-multilingual | 0+0 (0) | 4 (4) | **68.0** | 2 | 3 | 3 | 4 | 5 | 5 | Apache 2.0 | anchor: A kept from judgement (corpus out of scope) |
| 36 | FinQA | TQA-financial | 7+1 (5) | 4.17 (5) | **67.5** | 4 | 2 | 3 | 3 | 2 | 5 | MIT | FinQA; PoT; PIXIU; FinBen; Li; InvestLM; Fin-R1; supp: TAT-LLM |
| 37 | iTunes-Amazon (+dirty) | EM-other | 11+2 (8) | 5.0 (4) | **67.0** | 4 | 2 | 2 | 4 | 2 | 4 | Magellan | DeepMatcher; Ditto; Brunner; Narayan; HierGAT; Table-GPT; Zeakis; Unicorn; Sudowoodo; Zhang-preproc; Jellyfish; supp: AnyMatch; Papadakis |
| 38 | DROP | ANC-numeric | 0+0 (0) | 5 (5) | **67.0** | 2 | 3 | 3 | 5 | 2 | 5 | CC BY-SA 4.0 | anchor: A kept from judgement (corpus out of scope) |
| 39 | MGSM | ANC-numeric | 0+0 (0) | 4 (4) | **67.0** | 2 | 3 | 2 | 5 | 5 | 5 | CC BY-SA 4.0 | anchor: A kept from judgement (corpus out of scope) |
| 40 | Raha/Baran error detection collection | DI-cleaning | 7+1 (4) | 3.95 (4) | **66.8** | 3 | 3 | 3 | 4 | 2 | 5 | Apache-2.0 | Raha; Baran; Rotom; Narayan; Sudowoodo; Zhang-preproc; Jellyfish; supp: Cocoon |
| 41 | Jellyfish DP tasks (ED DI SM EM) | DI-other | 1+0 (1) | 1.19 (4) | **66.6** | 4 | 4 | 3 | 4 | 2 | 5 | CC BY 4.0 | Jellyfish |
| 42 | MiMoTable | TQA-hierarchical/multi | 0+1 (1) | 1.19 (2) | **65.6** | 4 | 4 | 4 | 3 | 5 | 1 | unstated | supp: MiMoTable paper |
| 43 | RobuT | TQA-general | 0+1 (1) | 1.19 (3) | **65.6** | 4 | 4 | 4 | 4 | 2 | 3 | unstated | supp: RobuT paper |
| 44 | SOTAB V2 | DI-schema/join | 1+0 (1) | 1.19 (4) | **65.6** | 4 | 4 | 4 | 4 | 2 | 3 | unstated | Jellyfish |
| 45 | FEVEROUS | TQA-verification | 5+1 (3) | 3.38 (4) | **65.1** | 3 | 3 | 3 | 4 | 2 | 5 | CC BY-SA 3.0 | FEVEROUS; UnifiedSKG; few(1)-shot; SUC; TableLlama; supp: TAP4LLM |
| 46 | SemTab 2025 (MammoTab Secu-table) | DI-annotation | 0+0 (0) | 1 (4) | **65.0** | 4 | 4 | 4 | 4 | 2 | 3 | unstated | not in corpus |
| 47 | QAMPARI | ANC-list/table | 0+0 (0) | 3 (3) | **65.0** | 2 | 4 | 4 | 4 | 2 | 5 | CC0 | anchor: A kept from judgement (corpus out of scope) |
| 48 | Spider 2.0 | TQA-sql | 1+0 (1) | 1.19 (4) | **64.6** | 3 | 4 | 4 | 4 | 2 | 5 | MIT | Spider 2.0 |
| 49 | MMQA (multi-table PK/FK) | TQA-sql | 0+0 (0) | 1 (2) | **64.0** | 5 | 4 | 4 | 3 | 2 | 1 | unstated | not in corpus |
| 50 | MultiTabQA | ANC-list/table | 0+1 (1) | 2 (2) | **64.0** | 3 | 4 | 3 | 4 | 2 | 5 | MIT | anchor: A kept from judgement (corpus out of scope) |
| 51 | VitaminC | ANC-boolean | 0+1 (0) | 3 (3) | **64.0** | 2 | 4 | 3 | 5 | 2 | 5 | CC BY-SA 3.0 | anchor: A kept from judgement (corpus out of scope) |
| 52 | Alaska Monitor/Notebook | EM-products | 2+1 (0) | 1.95 (3) | **63.9** | 4 | 2 | 4 | 3 | 2 | 5 | MIT | JointBERT; HierGAT; supp: Alaska paper |
| 53 | BizBench (SEC-Num etc.) | FIN-document | 0+1 (1) | 1.19 (3) | **63.6** | 4 | 3 | 3 | 4 | 2 | 5 | Apache-2.0 | supp: BizBench paper |
| 54 | MusicBrainz 20K | EM-other | 1+0 (1) | 1.19 (3) | **63.6** | 4 | 3 | 3 | 3 | 3 | 5 | CC BY 4.0 | Sparkly |
| 55 | Auto-Join | DI-schema/join | 0+0 (0) | 0 (3) | **63.0** | 5 | 4 | 4 | 3 | 2 | 2 | MSR research licence | not in corpus |
| 56 | ConvFinQA | TQA-financial | 7+1 (5) | 4.17 (4) | **62.5** | 3 | 2 | 3 | 3 | 2 | 5 | MIT | FinQA; PoT; PIXIU; FinBen; Li; InvestLM; Fin-R1; supp: TAT-LLM |
| 57 | NarrativeQA | ANC-span/freeform | 0+1 (0) | 4 (4) | **62.0** | 2 | 3 | 3 | 4 | 2 | 5 | Apache 2.0 | anchor: A kept from judgement (corpus out of scope) |
| 58 | MLQA | ANC-multilingual | 0+0 (0) | 4 (4) | **62.0** | 2 | 2 | 2 | 4 | 5 | 5 | CC BY-SA 3.0 | anchor: A kept from judgement (corpus out of scope) |
| 59 | Company | EM-other | 3+0 (0) | 1.95 (3) | **61.9** | 4 | 3 | 3 | 3 | 2 | 4 | Magellan | DeepMatcher; Ditto; JointBERT |
| 60 | HybridQA | TQA-general | 4+2 (4) | 3.6 (5) | **61.8** | 3 | 3 | 3 | 4 | 2 | 3 | unstated | HybridQA; UnifiedSKG; SUC; TableLlama; supp: TableGPT2; TAP4LLM |
| 61 | OfficeQA Pro/Full | FIN-document | 0+1 (1) | 1.19 (3) | **61.6** | 4 | 3 | 5 | 4 | 2 | 1 | CC BY-SA gated | supp: OfficeQA Pro paper |
| 62 | Cross-dataset EM study (11 sets LODO) | EM-other | 0+1 (1) | 1.19 (3) | **61.6** | 4 | 3 | 3 | 4 | 2 | 4 | inherits | supp: AnyMatch |
| 63 | FinanceBench (150 open) | FIN-document | 2+0 (2) | 1.98 (5) | **60.9** | 4 | 3 | 4 | 3 | 2 | 2 | CC BY-NC 4.0 | FinanceBench; Report Chunking |
| 64 | MultiHiertt | TQA-hierarchical/multi | 1+0 (0) | 0.98 (4) | **60.9** | 4 | 4 | 4 | 3 | 2 | 2 | MIT | MultiHiertt |
| 65 | IMDB-TMDB/TVDB (MovieGraphBenchmark) | EM-other | 2+0 (2) | 1.98 (3) | **59.9** | 4 | 3 | 3 | 3 | 2 | 3 | MIT code; IMDB rebuilt | Zeakis; ComEM |
| 66 | HoloClean datasets | DI-cleaning | 7+1 (4) | 3.95 (4) | **59.9** | 3 | 2 | 3 | 3 | 2 | 4 | Apache-2.0 (unv.) | Raha; Baran; Rotom; Narayan; Sudowoodo; Zhang-preproc; Jellyfish; supp: Cocoon |
| 67 | DocMath-Eval | FIN-document | 0+1 (1) | 1.19 (3) | **59.6** | 3 | 3 | 4 | 3 | 2 | 5 | MIT (unv.) | supp: DocMath-Eval paper |
| 68 | TempTabQA | TQA-general | 0+1 (1) | 1.19 (2) | **59.6** | 3 | 3 | 4 | 4 | 2 | 4 | unstated | supp: TempTabQA paper |
| 69 | FinAuditing | DI-schema/join | 0+0 (0) | 1 (2) | **59.0** | 4 | 4 | 4 | 2 | 2 | 2 | unstated | not in corpus |
| 70 | OAEI 2025 ontology tracks | DI-other | 1+0 (1) | 1.19 (5) | **58.6** | 3 | 3 | 3 | 4 | 4 | 3 | mostly open | Unicorn (OAEI OM) |
| 71 | WMT MQM | META | 3+1 (1) | 2.48 (5) | **58.4** | 1 | 3 | 3 | 5 | 4 | 5 | Apache 2.0 | BERTScore; BLEURT; COMET; supp: GEMBA |
| 72 | TriviaQA | ANC-span/freeform | 0+1 (1) | 5 (5) | **58.0** | 2 | 3 | 2 | 5 | 2 | 2 | unknown | anchor: A kept from judgement (corpus out of scope) |
| 73 | BoolQ | ANC-boolean | 0+1 (0) | 5 (5) | **58.0** | 2 | 2 | 1 | 5 | 2 | 5 | CC BY-SA 3.0 | anchor: A kept from judgement (corpus out of scope) |
| 74 | GSM8K (Platinum) | ANC-numeric | 0+3 (1) | 5 (5) | **58.0** | 2 | 2 | 1 | 5 | 2 | 5 | MIT | anchor: A kept from judgement (corpus out of scope) |
| 75 | SQuAD 2.0 | ANC-span/freeform | 0+0 (0) | 5 (5) | **58.0** | 2 | 2 | 1 | 5 | 2 | 5 | CC BY-SA 4.0 | anchor: A kept from judgement (corpus out of scope) |
| 76 | SANTOS | DI-discovery | 2+0 (2) | 1.98 (4) | **57.9** | 3 | 3 | 2 | 3 | 3 | 5 | CC BY 4.0 | Starmie; SANTOS |
| 77 | TAT-DQA | FIN-document | 1+1 (1) | 1.76 (3) | **57.3** | 3 | 2 | 3 | 4 | 2 | 5 | CC BY 4.0 | TAT-DQA; supp: TAT-LLM |
| 78 | SQA | TQA-general | 4+3 (2) | 3.36 (4) | **57.1** | 4 | 2 | 1 | 4 | 2 | 3 | MSR licence | TaPas; TAPEX; UnifiedSKG; SUC; supp: SQA paper; TAP4LLM; ReasTAP |
| 79 | T2Dv2 | DI-annotation | 3+1 (2) | 2.7 (4) | **57.1** | 3 | 2 | 2 | 4 | 2 | 5 | Apache | Sherlock; Table-GPT; Unicorn; supp: TURL |
| 80 | SummEval | META | 2+4 (3) | 3.38 (5) | **57.1** | 1 | 3 | 3 | 5 | 2 | 5 | MIT | SummEval; G-Eval; supp: GPTScore; UniEval; TRUE; Wang-ChatGPT-eval |
| 81 | EMBer (multimodal EM) | EM-products | 0+0 (0) | 0 (2) | **57.0** | 3 | 4 | 4 | 3 | 3 | 3 | unstated | not in corpus |
| 82 | SECQUE | FIN-document | 0+0 (0) | 1 (2) | **57.0** | 3 | 3 | 4 | 2 | 2 | 5 | CC BY 4.0 | not in corpus |
| 83 | Geographic Settlements | EM-other | 0+0 (0) | 0 (2) | **57.0** | 3 | 3 | 3 | 3 | 4 | 5 | CC BY 4.0 | not in corpus |
| 84 | Fodors-Zagats | EM-other | 12+2 (7) | 5.0 (5) | **56.0** | 3 | 1 | 1 | 4 | 2 | 4 | none stated | DeepMatcher; DeepER; Kasai; Ditto; ZeroER; Narayan; HierGAT; Table-GPT; Unicorn; Sudowoodo; Zhang-preproc; Jellyfish; supp: AnyMatch; Papadakis |
| 85 | LLMBar | META | 0+2 (2) | 1.98 (3) | **55.9** | 1 | 3 | 4 | 5 | 2 | 5 | MIT | supp: LLMBar; RewardBench |
| 86 | DataBench (SemEval 2025) | TQA-general | 0+1 (1) | 1.19 (4) | **55.6** | 3 | 3 | 2 | 4 | 2 | 5 | MIT | supp: DataBench paper |
| 87 | FinanceMath | FIN-document | 0+1 (1) | 1.19 (3) | **55.6** | 2 | 2 | 4 | 5 | 2 | 5 | MIT | supp: FinanceMath paper |
| 88 | North Carolina Voters 5M | EM-people/org | 0+0 (0) | 0 (3) | **55.0** | 4 | 3 | 2 | 3 | 2 | 5 | CC BY 4.0 | not in corpus |
| 89 | InfoTabs | TQA-verification | 0+1 (0) | 0.98 (3) | **54.9** | 3 | 2 | 3 | 4 | 2 | 5 | Apache-2.0 | supp: InfoTabs paper |
| 90 | TUS Small/Large | DI-discovery | 3+0 (2) | 2.38 (4) | **54.1** | 3 | 2 | 2 | 3 | 3 | 4 | unstated | TUS; Starmie; SANTOS |
| 91 | JudgeBench | META | 0+1 (1) | 1.19 (3) | **53.6** | 1 | 3 | 4 | 5 | 2 | 5 | MIT | supp: JudgeBench paper |
| 92 | FinDER | FIN-document | 0+0 (0) | 1 (2) | **53.0** | 3 | 3 | 4 | 3 | 2 | 2 | CC BY-NC 4.0 | not in corpus |
| 93 | Finance Agent Benchmark | FIN-document | 0+0 (0) | 1 (2) | **53.0** | 3 | 3 | 4 | 2 | 2 | 3 | CC BY 4.0 | not in corpus |
| 94 | lm-dw / BIG-bench data wrangling | DI-other | 0+0 (0) | 0 (3) | **53.0** | 3 | 3 | 3 | 4 | 3 | 3 | unstated | not in corpus |
| 95 | Spider 1.0 | TQA-sql | 17+4 (14) | 5.0 (5) | **53.0** | 2 | 1 | 1 | 4 | 2 | 5 | CC BY-SA 4.0 | RAT-SQL; TaBERT; PICARD; GraPPa; TestSuite; UnifiedSKG; DIN-SQL; DAIL-SQL; StructGPT; RESDSQL; LEVER; CodeS; MAC-SQL; C3; CHESS; CHASE-SQL; Liu-eval; supp: Spid |
| 96 | OpenEA (DBP15K DWY100K) | EM-other | 0+0 (0) | 0 (5) | **52.0** | 2 | 3 | 3 | 4 | 5 | 3 | GPL-3.0 | not in corpus |
| 97 | GitTables CTA | DI-annotation | 0+1 (0) | 0.98 (4) | **51.9** | 3 | 3 | 3 | 2 | 2 | 4 | CC0 vs CC BY (conflict) | supp: GitTables |
| 98 | CRT-QA | TQA-general | 0+0 (0) | 0 (2) | **51.0** | 3 | 3 | 3 | 3 | 2 | 4 | unstated | not in corpus |
| 99 | PubHealthTab | TQA-verification | 0+0 (0) | 0 (2) | **51.0** | 3 | 3 | 3 | 3 | 3 | 3 | unstated | not in corpus |
| 100 | TURL WikiTables CTA/CPA | DI-annotation | 1+1 (0) | 1.55 (4) | **50.7** | 3 | 2 | 3 | 3 | 2 | 3 | unstated | DoDuo; supp: TURL |
