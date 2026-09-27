# Dataset survey (2026-09-14): 100 ranked datasets for the data-matching benchmark

Read in this order.

| File | Contents |
|---|---|
| `08_EXECUTIVE_SUMMARY.md` | evidence-based top 10 and group lists (primary), then the judgement survey's findings, group sizes, per-version one-liners |
| `05_RANKED_100_evidence.md`, `06_GROUPINGS_evidence.md`, `07_PER_VERSION_FIT_evidence.md` | **the lists to cite**: ranking, 5…50 groups and per-version groups with adoption measured from the paper corpus (`ranked_100_evidence.csv` machine-readable) |
| `10_PAPER_CORPUS.md` + `10a`/`10b`/`10c` | the citation-ranked paper corpus (105 core + ≈115 supplementary papers), which datasets each evaluates on, merged usage counts (`paper_usage.csv`) |
| `11_EVIDENCE_VS_JUDGEMENT.md` | how the evidence ranking differs from the judgement ranking (ρ = 0.89), largest moves, group overlaps, per-version tops |
| `00_SCORING_RUBRIC.md` | the seven criteria and weights, the coverage-quota rule for groups, per-version fit rule |
| `05_RANKED_100.md` | the ranked 1–100 table with all sub-scores and a one-line reason each (`ranked_100.csv` is the same, machine-readable) |
| `06_GROUPINGS.md` | the 5 / 10 / 20 / 25 / 30 / 40 / 50 lists with coverage, inclusivity count, licence flags, and what each size adds |
| `07_PER_VERSION_FIT.md` | which of the 100 each version (v1–v5) can consume, and its own 5…50 lists |
| `01_SURVEY_ENTITY_MATCHING.md` | 44 entity-matching / record-linkage candidates with sizes, licences, links |
| `02_SURVEY_TABLE_QA.md` | 60 table-QA / table-understanding candidates |
| `03_SURVEY_FINANCE_DOCS_AND_INTEGRATION.md` | 36 financial-document QA + 34 data-integration / schema / wrangling candidates |
| `04_SURVEY_ANCHORS.md` | 65 answer-type anchors and human-label meta-evaluation sets |
| `09_SOURCES.md` | every URL used, by family |
| `candidates.csv`, `rank.py`, `rank_evidence.py`, `paper_usage.csv` | scored inputs; `rank.py` regenerates the judgement 05/06/07, `rank_evidence.py` the `_evidence` outputs |

Method: four parallel web surveys for candidates, then three literature harvests (Semantic Scholar citation ranking, PDF text-scan of dataset lists) to measure adoption. The surveys used ≈ 380 searches and page fetches, verification of download links and licences, a written rubric, scoring of 111 finalists, greedy coverage-constrained selection for the group lists. Datasets that could not be verified are marked (unv.) in the surveys and penalised on the L criterion.
