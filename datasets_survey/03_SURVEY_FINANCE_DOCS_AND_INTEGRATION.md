# Survey C: financial / business document QA (family A) and data integration, schema matching, wrangling, table discovery (family B). Verified September 2026.

✓ = page fetched; (unv.) = snippet or memory only. Score = family-internal 1–5 importance for a data-matching benchmark.

## Family A — financial and business document QA

| Name | Year | Source | Domain | Size | Task / answer | Metric | Licence | Download | Adoption | Hard because | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FinanceBench | 2023 | Patronus AI (Islam et al.) | SEC 10-K/10-Q/8-K | 10,231 total; **150 open** ✓ | open-book extraction / numeric / logic | expert grading | CC BY-NC 4.0 (150); rest commercial ✓ | HF PatronusAI/financebench | very high (RAG vendors) | locating figures in 100+ page PDFs | 4 |
| OfficeQA Pro / Full | 2025–26 | Databricks | Treasury Bulletins 1939–2025, 697 docs ✓ | Pro 133 / Full 246 numeric ✓ | grounded numeric QA | reward.py tolerance 0/0.1/1/5 % ✓ | CC BY-SA 4.0, **gated HF** ✓ | HF databricks/officeqa | new | retrieval over decades of scanned tables | 4 |
| OfficeQA Pro V2 | 2026 | Databricks | Receipts/Outlays 1793–2024, 1,435 PDFs ✓ | 90 Qs, median 5.5 docs/Q ✓ | multi-document numeric | reward.py; 3 answer shapes ✓ | CC BY-SA 4.0, gated ✓ | HF databricks/officeqa-pro-v2 | newest | cross-document reconciliation of series | 5 |
| DocFinQA | 2024 | Kensho, ACL 2024 | full 10-K | 7,437 (5,740/780/922) ✓ | numeric + program, 123k-word context | accuracy | MIT ✓ | HF kensho/DocFinQA | standard long-doc | needle in 100k+ tokens | 4 |
| FinQA | 2021 | Chen et al., EMNLP 2021 | S&P 500 report pages | 8,281 | program → number | execution acc ✓ | MIT ✓ | github czyssrs/FinQA | most cited; contaminated | multi-step arithmetic | 3 |
| ConvFinQA | 2022 | Chen et al., EMNLP 2022 | as FinQA | 3,892 conv / 14,115 turns ✓ | multi-turn numeric | execution acc | MIT ✓ | github czyssrs/ConvFinQA | in FinBen | coreference | 3 |
| TAT-QA | 2021 | NExT++, ACL 2021 | hybrid report | 16,552 / 2,757 ✓ | span/spans/arithmetic/count | EM, F1 ✓ | CC BY 4.0 ✓ | github NExTplusplus/tat-qa | canonical | scale inference | 3 |
| TAT-DQA | 2022 | NExT++, ACM MM 2022 | report page images | 16,558 / 3,067 pages ✓ | as TAT-QA on PDFs | EM, F1 | CC BY 4.0 ✓ | HF next-tat/TAT-DQA | moderate | layout | 3 |
| MultiHiertt | 2022 | PSU, ACL 2022 | multi-table reports | ~10.4k | numeric program | EM/F1 (CodaLab) | MIT ✓ | Google Drive via GitHub ✓ | DocMath seed | hierarchical, table choice | 3 |
| FinanceMath | 2024 | Yale, ACL 2024 | textbook-style finance | 200 / 1,000 ✓ | numeric 3 dp | accuracy | MIT ✓ | HF yale-nlp/FinanceMath | moderate | domain formulas | 2 |
| DocMath-Eval | 2024 | Yale, ACL 2024 | long financial docs | 4 subsets, ~4k | numeric | accuracy | MIT (unv.) | HF yale-nlp/DocMath-Eval | moderate | complong multi-table | 3 |
| FinTextQA | 2024 | HKUST, ACL 2024 | textbooks + agency docs | 1,262 | long-form | ROUGE/LLM judge (unv.) | (unv.) | HF GPS-Lab/FinTextQA (unv.) | low | generation | 1 |
| BizBench | 2024 | Kensho, ACL 2024 | finance/business | 19,050; 8 tasks incl. SEC-Num ✓ | program QA + quantity extraction | per-task acc ✓ | Apache-2.0 ✓ | HF kensho/bizbench | moderate | SEC-Num exact figure extraction | 3 |
| SEC-QA | 2024/25 | Kensho, FinNLP 2025 | multi-doc filings | framework; LOFin 333 (unv.) | multi-doc numeric | accuracy | (unv.); no public link | ACL anthology ✓ | low | cross-filing aggregation | 2 |
| EDGAR-CORPUS | 2021 | AUEB, ECONLP | all 10-Ks 1993–2020 | 220,375 filings ✓ | raw corpus | n/a | Apache-2.0 ✓ | HF eloukas/edgar-corpus | source material | n/a | 2 (source) |
| ECTSum | 2022 | IIT Kharagpur, EMNLP 2022 | earnings-call transcripts | 2,425 | bullet summarisation | ROUGE, numeric precision | GPL-3.0 ✓ | github rajdeep345/ECTSum | moderate | numbers under compression | 1 |
| FinDER | 2025 | LinqAlpha et al. | 10-K | 5,703 triplets ✓ | RAG retrieval + answer | nDCG + correctness | CC BY-NC 4.0 ✓ | HF Linq-AI-Research/FinDER | growing | expert acronym queries | 3 |
| FinTruthQA | 2024 | Chinese investor Q&A | zh | 6,000 | disclosure-quality label | F1 | (unv.) | github bethxx99/FinTruthQA | low | subjective | 1 |
| Fin-Fact | 2023/25 | IIT-DM | financial claims + images | 3,369 | fact label + explanation | F1, ROUGE | MIT | HF amanrangapur/Fin-Fact | low | multimodal | 1 |
| FinBen 2.0 | 2024 | TheFinAI, NeurIPS D&B | 36–42 datasets | aggregate | mixed | per-task | mixed | HF TheFinAI/flare-* ✓ | Open-FinLLM LB | breadth | 2 |
| PIXIU / FLARE | 2023 | TheFinAI | 9 datasets | aggregate | mixed | mixed | MIT code | same repo | superseded | – | 1 |
| MultiFinBen | 2025 | TheFinAI | 34 datasets, 5 langs, OCR | aggregate | mixed | mixed | (unv.) | HF TheFinAI/multifinben ✓ | new | OCR | 2 |
| FinTagging | 2025 | TheFinAI | 10-K XBRL tagging | v2: 142 10-Ks, 319,893 sentences, 21,576 tables | FinNI extraction → FinCL concept linking (10k concepts) | P/R/F1; FinCL acc ≈ 0.17 ✓ | (unv.) | HF TheFinAI/FinNI-eval, FinCL-eval ✓ | new | taxonomy alignment | 5 |
| FinAuditing | 2025 | TheFinAI | multi-doc XBRL | (unv.) | semantic matching, relation extraction, cross-doc consistency | (unv.) | (unv.) | github The-FinAI/FinAuditing ✓ | new | cross-statement linkage | 4 (unv.) |
| FinVerBench | 2026 | (unv.) | 10-K XBRL, 43 cos | (unv.) | statement verification under 4 perturbations | (unv.) | (unv.) | arXiv 2605.29586 | new | calibrated error detection | 3 (unv.) |
| "XBRL-Bench" | – | – | – | – | not found under this name; use FinTagging / FinAuditing / FinLoRA | – | – | github Open-Finance-Lab/FinLoRA ✓ | – | – | n/a |
| FinNLP shared tasks | 2024–26 | FinNLP / NTU | varies | varies | varies | varies | varies | sigfintech.github.io/finnlp2026 ✓ | community | – | 1–2 |
| FinDABench / BIBench | 2024/25 | ECNU, COLING 2025 | financial data analysis (zh likely) | 15,200 / 8,900 | calculation, anomaly, chart | (unv.) | (unv.) | github cubenlp/BIBench ✓ | low | multi-dimension | 2 |
| FinEval | 2023/25 | SUFE | Chinese finance exams | 8,351+ | MC | accuracy | CC BY-NC-SA 4.0 | HF SUFE-AIFLM-Lab/FinEval | zh evals | knowledge | 1 |
| SECQUE | 2025 | Ben-Yoash et al. | SEC filings analysis | 565 expert Qs ✓ | free-text analysis | multi-LLM judge ✓ | CC BY 4.0 ✓ | HF nogabenyoash/SecQue | new | cross-filing comparison | 3 |
| Finance Agent Benchmark | 2025 | Vals AI | recent filings, 9 categories | 537; 50 public ✓ | agentic research | rubric ✓ | CC BY 4.0 ✓ | HF vals-ai/finance_agent_benchmark | tracked LB | live retrieval | 3 |
| Fin-RATE / FinRetrieval / BigFinanceBench / FinAgentBench | 2025–26 | various | agent retrieval | (unv.) | (unv.) | (unv.) | (unv.) | arXiv only | new | – | unv. |
| DocVQA | 2021 | CVC/IIIT, WACV | industry document images | ~50k Qs | extractive VQA | ANLS | non-commercial via RRC (unv.) | docvqa.org; HF lmms-lab/DocVQA | ubiquitous VLM | layout/OCR | 2 |
| InfographicVQA | 2022 | same | infographics | 30,000 ✓ | extractive + reasoning | ANLS | annotations CC BY | docvqa.org ✓ | ubiquitous | chart+text | 1 |
| MP-DocVQA | 2023 | Tito et al. | multi-page scans | 46,436 Qs / 47,952 pages ✓ | VQA + page id | ANLS ✓ | MIT ✓ | HF rubentito/mp-docvqa | moderate | which page | 2 |
| ChartQA | 2022 | vis-nlp, Findings ACL 2022 | charts | ~9.6k human + 23.1k aug | numeric/text | relaxed accuracy 5 % ✓ | GPL-3.0 ✓ | HF ahmed-masry/ChartQA | ubiquitous VLM | reading values | 2 |
| PlotQA | 2020 | IIT Madras, WACV | synthetic plots | 28.9M | numeric/categorical | accuracy | CC BY 4.0 | github NiteshMethani/PlotQA | moderate | scale | 1 |

## Family B — data integration, schema matching, wrangling, table discovery, annotation

| Name | Year | Source | Domain | Size | Task / answer | Metric | Licence | Download | Adoption | Hard because | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TPC-DI | 2014 | TPC (Poess et al., VLDB) | brokerage ETL | DIGen scale factors | source→warehouse mappings | throughput | spec CC BY-NC-ND; tools TPC EULA | tpc.org/tpcdi ✓ | seed for Valentine | multi-format, SCD | 3 |
| Valentine | 2021 | TU Delft, ICDE 2021 | fabricated from TPC-DI, Open Data, ChEMBL ✓ | 540 pairs, 4 scenarios | column-to-column matching | P/R/F1, MRR ✓ | Apache-2.0 code; Zenodo data | github delftdata/valentine ✓ | de-facto LLM-SM benchmark | obfuscated headers | 5 |
| Magneto GDC-SM | 2025 | NYU VIDA, VLDB 2025 | biomedical: 10 tables → GDC (736 cols) ✓ | 10 source tables | source→standard schema | Recall@k, MRR | CC BY 4.0 ✓ | zenodo 14963587 ✓ | rising | many-to-one, value vocab | 5 |
| OAEI 2025 | annual | OM community | ontologies, 13 tracks ✓ | Anatomy ~1.5k mappings | ontology alignment | P/R/F1 | mostly open | oaei.ontologymatching.org ✓ | 20-year canon | logical coherence | 3 |
| SemTab 2025 | 2019–25 | ISWC | Wikidata-aligned tables | MammoTab 870 tables / 84,907 cells; Secu-table 1,554 ✓ | CEA/CTA/CPA | P/R/F1 ✓ | not stated | sem-tab-challenge.github.io/2025 ✓ | canonical STI | NIL, noise | 4 |
| MammoTab 25 | 2025 | Milano-Bicocca | ~839k Wikipedia tables | large | CEA/CTA/NIL | F1 | (unv.) | unimib-datai.github.io | new | scale | 3 |
| T2Dv2 | 2016 | WDC Mannheim | web tables → DBpedia | 779 tables | CTA/CPA/CEA | P/R/F1 | Apache | webdatacommons.org ✓ | older canon | small | 3 |
| TURL WikiTables CTA/CPA | 2020 | OSU, VLDB 2020 | Wikipedia tables | 255 types, 121 relations | CTA, CPA | F1 | (unv.) | github sunlab-osu/TURL | widely used | long tail | 3 |
| VizNet-Sato / Sherlock | 2019–20 | Megagon/UMass | web tables, 78 types | ~122k columns | CTA | F1 | (unv.) | github megagonlabs/sato | classic | context | 2 |
| SOTAB V2 | 2023 | WDC Mannheim | Schema.org web tables | CTA 45,834 tables; CPA 30,220 ✓ | CTA, CPA + hard splits ✓ | micro-F1 ✓ | not stated | webdatacommons.org/sotab/v2 ✓ | LLM CTA papers | format heterogeneity | 4 |
| GitTables | 2023 | UvA, SIGMOD 2023 | 1M GitHub CSVs | 16.3 GB; 1,101-table CTA bench | CTA | macro-F1 | CC0 vs CC BY 4.0 (conflict) | zenodo 6517052 ✓ | pretraining corpus | weak labels | 3 |
| TUS Small/Large | 2018 | Toronto, VLDB 2018 | Canadian open data | 1,530 / 5,043 tables | table union search | P/R@k, MAP | (unv.) | zenodo 14151800 ✓ | standard | lexical baselines saturate | 3 |
| SANTOS | 2023 | Northeastern/Toronto, SIGMOD 2023 | open data lake | small + 1.8 GB real | union search w/ relationships | P/R@k, MAP | CC BY 4.0 ✓ | zenodo 14151800 ✓ | standard | semantics | 3 |
| LakeBench | 2024 | BIT, VLDB 2024 | 16M tables, 1 TB ✓ | 8 benchmarks (union/join/subset) | discovery | P/R | not stated | github RLGen/LakeBench ✓ | big | noisy GT | 3 |
| "Something's Fishy" TUS | 2025 | Boutaleb et al., TRL@ACL | relabelled TUS/SANTOS/Pylon/UGEN/LakeBench ✓ | meta | union search | P/R | (unv.) | zenodo 15499092 ✓ | growing | shows lexical baselines win | 2 |
| Auto-Join | 2017 | MSR, SIGMOD 2017 | web table pairs | 31 cases ✓ | learn key transformations to join | correctness vs GT | MSR licence ✓ | github Yeye-He/Auto-Join ✓ | cited | key format reconciliation | 4 |
| TDE (Transform-Data-by-Example) | 2018 | MSR, VLDB 2018 | string transformations | 200+ tasks | by-example synthesis | task correctness | MSR (unv.) | paper PDF | moderate | long tail | 3 |
| lm-dw / BIG-bench mult_data_wrangling | 2022 | UPV, MLJ | dates, emails, names, units | 3,744 instances | wrangling by example | accuracy | (unv.) | github gonzalojaimovitch/lm-dw ✓ | modest | format normalisation | 2 |
| HoloClean datasets | 2017 | Stanford/Wisconsin, VLDB | hospital, flights, food, physicians | hospital 1k × 19 | error detection/repair | cell P/R/F1 | Apache-2.0 (unv.) | github HoloClean/holoclean ✓ | canonical cleaning | denial constraints | 3 |
| Raha/Baran collection | 2019–20 | TU Berlin, SIGMOD/VLDB | hospital, flights, beers, rayyan, movies, tax, adult | tax 200k × 15 | error detection | cell P/R/F1 | Apache-2.0 ✓ | github BigDaMa/raha ✓ | de-facto ED bench | real errors | 3 |
| Jellyfish DP tasks | 2024 | Osaka/NEC, VLDB 2024 | ED, DI, SM (SMAT), EM (Magellan) | instruction set | yes/no or value | F1 / acc | CC BY 4.0 data ✓ | HF NECOUDBFM/Jellyfish-Instruct ✓ | standard LLM-DP | mixed tasks one format | 4 |
| SMAT schema-matching sets | 2021 | Zhang et al., ADBIS | MIMIC-III, Synthea, CMS → OMOP | (unv.) | attribute-pair match | F1 | (unv.) | github JZCS2018/SMAT | used by Jellyfish | real healthcare schemas | 4 (unv.) |
| DI2KG / Alaska | 2019–21 | Roma Tre | camera 29,787 / monitor 16,662 / notebook 23,167 specs ✓ | SM GT 687/1,026/960 mappings; ER GT 103/232/208 entities ✓ | schema matching + entity resolution | P/R/F1 | MIT ✓ | github merialdo/research.alaska ✓ (site unreachable) | SIGMOD contests 2020–22 | thousands of attribute names | 4 |
| SchemaNet (LLMatch) | 2025 | Wang, Li et al. | 7 enterprise datasets | (unv.) | multi-table schema alignment | F1 | (unv.) | arXiv 2507.10897 | new | real enterprise | 3 (unv.) |
| HRS-B (ConStruM) | 2026 | (unv.) | Health and Retirement Study metadata | (unv.) | large-schema matching | (unv.) | (unv.) | arXiv 2601.20482 | new | cross-attribute context | unv. |
| Enterprise CTA (SportsTables vs SAP) | 2025 | TU Darmstadt/SAP, VLDB | public + private | – | CTA; F1 0.94 → 0.07–0.38 enterprise | F1 | SAP not released | vldb.org p196 | diagnostic | cryptic names | 2 |
| DA-Code / DABench / DSBench | 2024–25 | various | data-prep/analysis agents | 500 / 257 tasks | code agents | solution match | varies | github liqiangjing/dsbench ✓ | moderate | multi-step | 2 |
| TableGPT2 RealTabBench | 2024 | Zhejiang | BI tables | 360 (subset public) | table analysis | acc / judge | (unv.) | github tablegpt/tablegpt-agent | moderate | irregular layouts | 1 |
| DataDreamer | 2024 | Patel et al., ACL 2024 | library, not benchmark | – | – | – | MIT | github datadreamer-dev | – | – | n/a |
| Text-to-Transform, AutoDI, ADE, MELD | – | – | not found as data-matching benchmarks | – | – | – | – | – | – | – | n/a |
| NLCTables, LakeGen, JOSIE open-data join | 2019–25 | various | table discovery | – | union/join with NL conditions | P/R@k | (unv.) | arXiv | new | – | 2 (unv.) |
| SIGMOD/DI2KG matching challenges | 2020–22 | contests | products | see Alaska | ER/SM | F1 | MIT | see Alaska | historical | – | folded |

**Family A canon:** FinQA → ConvFinQA → TAT-QA/TAT-DQA → MultiHiertt (2021–22, MIT/CC-BY, contaminated, short-context); FinanceBench and DocFinQA for long documents; DocVQA/ChartQA for images. The 2025–26 wave (OfficeQA V2, FinTagging, FinDER, SECQUE, Finance Agent Benchmark, FinAuditing, FinVerBench) is where the matching flavour lives: cross-document reconciliation, taxonomy concept linking (FinCL ≈ 0.17), cross-statement consistency. Licensing: FinanceBench exposes 150 of 10,231 rows (NC); OfficeQA is CC BY-SA but gated with an anti-training clause and a 4–14 GB corpus; FinDER NC; Finance Agent Benchmark 50 of 537 public; DocVQA family via RRC portal; ChartQA/ECTSum GPL-3; FinEval NC-SA. "XBRL-Bench" does not exist under that name. EDGAR-CORPUS (Apache) is the cleanest raw source for synthesising matching tasks.

**Family B canon:** Valentine (schema matching), SOTAB V2 and T2Dv2/TURL (CTA/CPA), SemTab (annual, LLM-focused now), TUS/SANTOS/LakeBench (discovery), Raha/HoloClean (error detection), Jellyfish-Instruct + Magellan (LLM-era DP suite), OAEI (ontologies). Niche but high value: Magneto GDC-SM (CC BY 4.0, real harmonisation), Alaska/DI2KG (MIT, thousands of attributes, SM + ER), Auto-Join (31 join-key cases). Issues: TPC-DI spec CC BY-NC-ND and tools under TPC EULA; Auto-Join/TDE MSR research-only; GitTables licence conflict; SOTAB V2 / LakeBench no licence; SchemaNet and SAP data unreleased; DI2KG site unreachable (data on GitHub); TUS/SANTOS/LakeBench GT noisy enough that lexical baselines saturate. MELD, AutoDI, ADE, Text-to-Transform do not correspond to findable benchmarks; DataDreamer is a library.
