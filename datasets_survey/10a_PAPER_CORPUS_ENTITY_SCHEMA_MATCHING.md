# Paper corpus A: entity matching / resolution, schema matching, data integration (top 35 by citations + supplementary)

Citation counts: Semantic Scholar `paper/batch`, 2026-09-14. Dataset lists verified from each paper's PDF text (or official repo where ACM blocked the PDF, marked [repo]). Surveys and pre-2018 papers excluded from the core.

## Core 35

| # | Paper | First author | Year | Venue | Cites | Family | Datasets evaluated on |
|---|---|---|---|---|---|---|---|
| 1 | DeepMatcher | Mudgal | 2018 | SIGMOD | 707 | EM | Beer, iTunes-Amazon, Fodors-Zagats, DBLP-ACM, DBLP-Scholar, Amazon-Google, Walmart-Amazon, Abt-Buy, Company (+dirty) |
| 2 | Ditto | Li | 2020 | PVLDB | 545 | EM | the 9 Magellan sets (+dirty), WDC-LSPC (4 categories) |
| 3 | Can foundation models wrangle your data? | Narayan | 2022 | PVLDB | 376 | EM+ED+DI+SM (LLM) | EM: Fodors-Zagats, Beer, iTunes-Amazon, Walmart-Amazon, DBLP-ACM, Amazon-Google; DI: Restaurant, Buy; ED: Hospital, Adult; SM: Synthea-OMOP |
| 4 | DeepER | Ebraheem | 2018 | PVLDB | 349 | EM | Walmart-Amazon, Amazon-Google, DBLP-ACM, DBLP-Scholar, DBLP-Citeseer, Fodors-Zagats |
| 5 | Table Union Search on Open Data | Nargesian | 2018 | PVLDB | 287 | discovery | TUS |
| 6 | Sherlock | Hulsebos | 2019 | KDD | 239 | CTA | VizNet |
| 7 | Raha | Mahdavi | 2019 | SIGMOD | 192 | error detection | Hospital, Flights, Beers, Rayyan, Movies, Tax |
| 8 | Starmie | Fan | 2023 | PVLDB | 166 | discovery | SANTOS small/large, TUS small/large, WDC web tables |
| 9 | EM with transformer architectures | Brunner | 2020 | EDBT | 164 | EM | Abt-Buy, iTunes-Amazon, Walmart-Amazon, DBLP-ACM, DBLP-Scholar (dirty) |
| 10 | Low-resource deep ER (transfer + active) | Kasai | 2019 | ACL | 155 | EM | DBLP-ACM, DBLP-Scholar, Cora, Fodors-Zagats, Amazon-Google, Zomato-Yelp |
| 11 | Valentine | Koutras | 2021 | ICDE | 143 | SM benchmark | Valentine (TPC-DI, ChEMBL, OpenData, WikiData, Magellan) |
| 12 | Auto-EM | Zhao | 2019 | WWW | 138 | EM | 8 Magellan EM-task-repo tasks |
| 13 | SANTOS | Khatiwada | 2023 | SIGMOD | 135 | discovery | TUS, SANTOS small/large |
| 14 | DL for blocking in EM | Thirumuruganathan | 2021 | PVLDB | 126 | blocking | Amazon-Google, Walmart-Amazon, DBLP-ACM, DBLP-Scholar, Hospital, Songs, Abt-Buy, Restaurants, Books, Cora |
| 15 | Table-GPT | Li (Peng) | 2023 | SIGMOD 2024 | 122 | EM+SM+CTA (LLM) | EM: Amazon-Google, Beer, DBLP-ACM, DBLP-Scholar, Fodors-Zagats, Walmart-Amazon, iTunes-Amazon; CTA: Efthymiou, Limaye, T2D |
| 16 | ZeroER | Wu | 2020 | SIGMOD | 119 | EM | Fodors-Zagats, DBLP-ACM, DBLP-Scholar, Abt-Buy, Amazon-Google |
| 17 | DoDuo | Suhara | 2022 | SIGMOD | 117 | CTA/CPA | WikiTable (TURL), VizNet |
| 18 | Baran | Mahdavi | 2020 | PVLDB | 85 | error correction | Hospital, Flights, Beers, Rayyan, Tax |
| 19 | Rotom | Miao | 2021 | SIGMOD | 75 | EM+ED | [repo] Abt-Buy, Amazon-Google, DBLP-ACM, DBLP-Scholar, Walmart-Amazon; ED: beers, hospital, movies, rayyan, tax |
| 20 | JointBERT | Peeters | 2021 | PVLDB | 75 | EM | WDC-LSPC, Alaska monitors, Abt-Buy, DBLP-Scholar, Company |
| 21 | Pre-trained embeddings for ER | Zeakis | 2023 | PVLDB | 74 | EM | Abt-Buy, Amazon-Google, DBLP-ACM, DBLP-Scholar, Walmart-Amazon, iTunes-Amazon, Restaurants, IMDb-TMDb/TVDB, TMDb-TVDB, IMDb-DBpedia, synthetic dirty-ER |
| 22 | Unicorn | Tu | 2023 | SIGMOD | 71 | multi-task matching | [repo] Walmart-Amazon, DBLP-Scholar, Fodors-Zagats, iTunes-Amazon, Beer; CTA Efthymiou/T2D/Limaye; SM Valentine, DeepMDatasets; Smurf; OAEI OM; SRPRS |
| 23 | ComEM | Wang (Tianshu) | 2024 | COLING 2025 | 70 | EM (LLM) | Abt-Buy, Amazon-Google, DBLP-ACM, DBLP-Scholar, Walmart-Amazon, IMDB-TMDB, IMDB-TVDB, TMDB-TVDB |
| 24 | HierGAT | Yao | 2022 | SIGMOD | 69 | EM | [repo] the 8 Magellan structured sets + dirty, WDC, Alaska |
| 25 | Sudowoodo | Wang (Runhui) | 2023 | ICDE | 68 | EM+ED+column matching | 8 Magellan sets; ED beers/hospital/rayyan/tax; VizNet |
| 26 | Entity matching using LLMs | Peeters | 2025 | EDBT | 66 | EM (LLM) | WDC-Products, Abt-Buy, Walmart-Amazon, Amazon-Google, DBLP-Scholar, DBLP-ACM |
| 27 | DeepJoin | Dong | 2023 | PVLDB | 66 | join discovery | WDC web tables, Wikitable |
| 28 | R-SupCon | Peeters | 2022 | WWW Companion | 65 | EM | Abt-Buy, Amazon-Google, WDC-LSPC computers |
| 29 | LLMs as data preprocessors | Zhang (Haochen) | 2023 | VLDB WS | 65 | ED+DI+SM+EM (LLM) | Adult, Hospital, Buy, Restaurant, Synthea-OMOP, 7 Magellan EM sets |
| 30 | Schema matching with LLMs: experimental study | Parciak | 2024 | VLDB WS | 62 | SM (LLM) | MIMIC-IV → OMOP |
| 31 | Jellyfish | Zhang (Haochen) | 2024 | EMNLP | 52 | ED+DI+SM+EM+CTA (LLM) | Adult, Hospital, Flights, Rayyan; Buy, Restaurant, Flipkart, Phone; MIMIC-III, Synthea, CMS → OMOP; 8 Magellan EM; SOTAB; AE-110k, OA-Mine |
| 32 | Sparkly | Paulsen | 2023 | PVLDB | 52 | blocking | 15 sets incl. Amazon-Google, Songs, Companies; Big Citations, MusicBrainz 20M, WDC 26M |
| 33 | Using ChatGPT for entity matching | Peeters | 2023 | ADBIS WS | 51 | EM (LLM) | WDC-Products |
| 34 | Magneto | Liu (Freire) | 2025 | PVLDB | 48 | SM (LLM) | Magneto-GDC; Valentine (WikiData, OpenData, ChEMBL, TPC-DI, Magellan) |
| 35 | ReMatch | Sheetrit | 2024 | arXiv | 43 | SM (LLM) | MIMIC-III → OMOP, Synthea → OMOP |

Supplementary A (verified, outside the 35): Machamp 40 (7 Machamp sets), PromptEM 40 (Machamp + geo), WDC Products 2024 paper 39, Steiner fine-tuning LLMs for EM 36 (WDC-Products, 5 Magellan), TURL 34 (S2 under-merged; WikiTable CTA, T2D, Limaye, Efthymiou), GNEM 32, Zhang SM-PLM 31 (unv.), Alaska 27, DAEM 22 (unv.), Cocoon 22 (Raha sets), Matchmaker 21 (MIMIC/Synthea-OMOP), LakeBench 21, Papadakis re-evaluation 16 (Magellan sets + Dn), AnyMatch 15 (8 Magellan + WDC), KcMF 14, Sato 13 (VizNet).
Supplementary B (excluded): HoloClean 611 (pre-2018; Hospital, Flights, Food, Physicians), Aurum 296, Magellan 158, surveys Barlaug 157, Christophides 70, Papadakis blocking 66; GitTables corpus 120.

## Dataset usage counts (core 35; 16 papers are 2023+)

| Dataset | core | 2023+ |
|---|---|---|
| Amazon-Google | 18 | 8 |
| DBLP-Scholar | 18 | 8 |
| DBLP-ACM | 17 | 7 |
| Walmart-Amazon | 16 | 8 |
| Abt-Buy | 14 | 5 |
| Fodors-Zagats | 12 | 5 |
| iTunes-Amazon | 11 | 6 |
| Beer | 9 | 5 |
| Hospital (Raha) | 7 | 3 |
| Rayyan | 5 | 2 |
| WDC-LSPC | 5 | 1 |
| Beers / Tax (Raha) | 4 / 4 | 1 / 1 |
| Synthea-OMOP (SMAT) | 4 | 3 |
| Adult; Buy; Restaurant (imputation) | 3 each | 2 each |
| Company | 3 | 0 |
| Flights | 3 | 1 |
| MIMIC-OMOP (SMAT) | 3 | 3 |
| T2D/T2Dv2 | 3 | 2 |
| TUS | 3 | 2 |
| Valentine | 3 | 2 |
| VizNet | 3 | 1 |
| Alaska | 2 | 0 |
| Cora | 2 | 0 |
| Efthymiou; Limaye | 2 each | 2 each |
| IMDb/TMDb/TVDB movies | 2 | 2 |
| SANTOS | 2 | 2 |
| Songs | 2 | 1 |
| WDC-Products-2024 | 2 | 2 |
| WDC web tables corpus | 2 | 2 |
| Magneto-GDC; SOTAB; CMS-OMOP; MusicBrainz; Big Citations; Febrl-style synthetic; TURL WikiTable; DBLP-Citeseer; Zomato-Yelp | 1 each | – |
| Machamp, NCVR, Febrl (real), OpenSanctions, GitTables, LakeBench, Papadakis-Dn | 0 | 0 (Machamp: 2 supplementary; WDC-Products-2024: +2 supplementary) |

Readings: the Magellan/DeepMatcher structured sets dominate (14–18 of 35 papers each, still about half of the 2023+ papers). WDC-Products-2024 is the only new EM benchmark with repeat LLM-era use. Schema matching splits between Valentine and the healthcare OMOP pairs (all 2023+). Data-lake discovery (TUS/SANTOS/WDC web tables) and the Raha cleaning collection are separate clusters. Caveats: TURL and Sato S2 counts are fragmented; six dataset lists unverified (Zhang SM-PLM, DAEM, KcMF, LakeBench, Table-GPT's SM test set, Sparkly's image table).
