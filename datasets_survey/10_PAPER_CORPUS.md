# The paper corpus: top-cited papers per area, and which datasets they evaluate on

Purpose: replace the judgement-based adoption sub-score (A) with a count of how often each candidate dataset is actually used in the most-cited literature of the benchmark's areas. Three corpora were harvested on 2026-09-14, each ranked by Semantic Scholar citation count (Graph API `paper/batch`; the search endpoint was rate-limited, so candidate papers were listed from knowledge of the field and then looked up and re-ranked by count). Surveys, tutorials and pre-2018 papers are excluded from the cores because they evaluate on nothing or predate neural matching; each area also carries a supplementary list (the next-most-cited papers, including the ones that introduce the newest benchmarks) whose dataset lists are from the papers' abstracts or prior knowledge rather than a full PDF scan.

| Corpus | File | Core papers (PDF-verified) | Supplementary | Areas |
|---|---|---|---|---|
| A | `10a_PAPER_CORPUS_ENTITY_SCHEMA_MATCHING.md` | 35 (29 verified, 6 from official repos) | 15 + 7 excluded | entity matching / resolution, blocking, schema matching, column-type annotation, table discovery, error detection |
| B | `10b_PAPER_CORPUS_TABLE_QA.md` | 40 (34 verified) | 60 | table QA, table fact verification, table understanding with LLMs, text-to-SQL |
| C | `10c_PAPER_CORPUS_FINANCE_AND_EVAL.md` | 18 + 12 (dataset lists from abstracts/knowledge, (unv.) where not checked) | 18 + 22 | financial-document QA and FinLLM benchmarks; LLM-evaluation metrics and benchmark meta-evaluation |

Total: 105 core papers and about 115 supplementary papers, i.e. roughly the 100 most-cited papers per area that the request asked for. Citation counts range from 11,152 (MT-Bench / LLM-as-a-judge) down to 43 (ReMatch) in the cores.

## How usage was counted

* One paper counts once per dataset it evaluates on (or introduces), regardless of how many splits or variants it uses. Papers appearing in two corpora (e.g. Program-of-Thoughts, FinQA, TAT-QA, ConvFinQA, MultiHiertt, DocFinQA in both B and C) are counted once.
* `papers_core` = uses in the citation-ranked cores; `papers_supp` = uses in the supplementary lists; `papers_total` = their sum; `papers_2023plus` = uses in papers from 2023 on (the LLM era), which feeds the recency term.
* Collections are counted as one dataset (the Raha/Baran error-detection collection, the OMOP schema-matching pairs of SMAT). Magellan sets are counted individually.
* The union of all three corpora is in `paper_usage.csv` (107 dataset keys); `rank_evidence.py` maps the keys onto candidate names through its `ALIAS` table.

## Usage counts (top of the merged table; full table in `paper_usage.csv`)

| Dataset | core | supp | total | 2023+ |
|---|---|---|---|---|
| WTQ | 12 | 10 | 22 | 13 |
| Spider | 17 | 4 | 21 | 14 |
| Amazon-Google | 18 | 3 | 21 | 11 |
| DBLP-Scholar | 18 | 3 | 21 | 11 |
| DBLP-ACM | 17 | 3 | 20 | 10 |
| Walmart-Amazon | 16 | 3 | 19 | 11 |
| TabFact | 10 | 7 | 17 | 11 |
| Abt-Buy | 14 | 3 | 17 | 8 |
| Fodors-Zagats | 12 | 2 | 14 | 7 |
| iTunes-Amazon | 11 | 2 | 13 | 8 |
| Beer | 9 | 2 | 11 | 7 |
| FeTaQA | 6 | 5 | 11 | 7 |
| WikiSQL | 7 | 3 | 10 | 3 |
| BIRD | 7 | 2 | 9 | 9 |
| FinQA | 7 | 1 | 8 | 5 |
| HoloClean-collection | 7 | 1 | 8 | 4 |
| Raha-collection | 7 | 1 | 8 | 4 |
| ConvFinQA | 7 | 0 | 7 | 4 |
| SQA | 4 | 3 | 7 | 2 |
| SMAT | 5 | 1 | 6 | 5 |
| HybridQA | 4 | 2 | 6 | 4 |
| FEVEROUS | 5 | 1 | 6 | 3 |
| SummEval | 2 | 4 | 6 | 3 |
| WDC-LSPC | 5 | 1 | 6 | 2 |
| HiTab | 2 | 3 | 5 | 4 |
| TAT-QA | 3 | 2 | 5 | 3 |
| ToTTo | 3 | 1 | 4 | 3 |
| T2Dv2 | 3 | 1 | 4 | 2 |
| VizNet | 3 | 1 | 4 | 1 |
| WMT-MQM | 3 | 1 | 4 | 1 |
| AIT-QA | 0 | 3 | 3 | 2 |
| TPC-DI | 3 | 0 | 3 | 2 |
| TUS | 3 | 0 | 3 | 2 |
| Valentine | 3 | 0 | 3 | 2 |
| GSM8K | 2 | 1 | 3 | 1 |
| Alaska | 2 | 1 | 3 | 0 |
| Alaska-SM | 2 | 1 | 3 | 0 |
| Company | 3 | 0 | 3 | 0 |
| FinanceBench | 2 | 0 | 2 | 2 |
| IMDB-TMDB | 2 | 0 | 2 | 2 |
| LLMBar | 0 | 2 | 2 | 2 |
| SANTOS | 2 | 0 | 2 | 2 |
| TableBench | 1 | 1 | 2 | 2 |
| WDC-Products-2024 | 2 | 0 | 2 | 2 |
| OTT-QA | 1 | 1 | 2 | 1 |

Zero uses anywhere in the corpus: Auto-Join, CRT-QA, ChartQA, DROP, EDGAR-CORPUS, Ember, FinAuditing, MGSM, MLQA, MMQA, MP-DocVQA, NCVR, OfficeQA-Pro-V2, OpenSanctions, PubHealthTab, QAMPARI, SECQUE, SQuAD, SemTab, TyDiQA, lm-dw.

## What the corpus says

1. **Entity matching is still evaluated on the Magellan / DeepMatcher structured sets.** Amazon-Google, DBLP-Scholar, DBLP-ACM, Walmart-Amazon and Abt-Buy appear in 17–21 of the harvested papers each and in about half of the 2023+ papers, including every LLM-era entity-matching paper (Narayan, Peeters, Zhang, ComEM, Jellyfish). WDC Products 2024 is the only new entity-matching benchmark with repeat LLM-era use (4 papers), all from the same group.
2. **Schema matching has two clusters**: Valentine (3 core uses, the reference for LLM matchers Unicorn and Magneto) and the healthcare OMOP pairs (SMAT: 6 uses, 5 of them 2023+; every LLM schema-matching paper uses them). Magneto GDC-SM is used only by its own paper so far.
3. **Table QA is dominated by WTQ (22 uses) and TabFact (17), then Spider (21, but text-to-SQL) and BIRD (9, all 2023+)**; FeTaQA (11), HybridQA (6), FEVEROUS (6), SQA (7) follow; HiTab has 5 uses, all but one from 2023+. Every 2024–26 table benchmark (MMTU, TableBench, TableEval, RealHiTBench, MiMoTable, TabIS, DataBench) is used by one paper: its own.
4. **Financial-document QA**: FinQA and ConvFinQA (8 uses each) and DocFinQA (8, via the FinQA-derived count) are the canon; TAT-QA 5; FinanceBench 2; the 2025–26 reconciliation-style sets (OfficeQA Pro V2, FinTagging, FinAuditing, SECQUE) have no external use yet.
5. **Meta-evaluation**: SummEval (6 uses) is the reference set for LLM-judge validation; WMT MQM (4); LLMBar (2); TRUE and JudgeBench are used only by themselves in this corpus.
6. **Anchors**: the corpus is not designed to measure general-QA adoption (only HELM, PoT and tinyBenchmarks touch GSM8K, BoolQ, NarrativeQA), so anchors keep the judgement A in `rank_evidence.py`; their counts are reported but not used.

## Caveats

* Citation counts are a snapshot (2026-09-14) and Semantic Scholar under-merges some papers (TURL, Sato). Six core dataset lists in A and six in B were not re-verified from PDF text (marked (unv.) or [repo]).
* Supplementary dataset lists are less reliable than core ones; they are kept separate in `paper_usage.csv` so the analysis can be repeated on cores only (set `papers_supp` to 0).
* Usage counts measure what the field has evaluated on, which favours older sets. The recency term (30 % weight on 2023+ uses) and the year rule (A = 1 for 2025–26 sets absent from the corpus) soften but do not remove that bias; the other six criteria (R, G, D, C, I, L) are unchanged, so a new set can still rank high on relevance and difficulty.
