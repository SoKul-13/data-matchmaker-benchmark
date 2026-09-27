# Scoring rubric used to rank the 100 candidate datasets

Each dataset receives seven sub-scores (0–5) and an importance score = weighted sum, normalised to 0–100.
The weights reflect the benchmark's purpose (an LLM judge for data-matching / data-reading work) and the
user's criteria (inclusivity, generalisation, representation).

| Sub-score | Weight | 5 means | 0 means |
|---|---|---|---|
| R — task relevance to data matching / integration / reading structured data | 0.25 | the task *is* matching, joining, or reading records/tables/financial documents | unrelated (general chat, vision) |
| A — adoption and credibility | 0.15 | canonical: used in most papers of its family; venue-published; maintained | one paper, no follow-ups |
| G — generalisation value (adds a domain / modality / answer type / difficulty the suite lacks) | 0.15 | new domain and hard for frontier models | redundant with a higher-ranked set |
| D — discriminative power today | 0.15 | frontier models spread out (not at ceiling or floor) | saturated (>95 %) or unanswerable (floor) |
| C — gold quality and metric clarity | 0.10 | clean golds with an official, well-defined metric; aliases derivable | noisy labels, no official metric |
| I — inclusivity / representation (language, domain diversity, non-English or non-US data, underrepresented sources) | 0.10 | multilingual or non-Western sources, diverse domains | English, one domain, one source |
| L — licence and accessibility | 0.10 | permissive licence, direct download, no gate | gated, unclear licence, download broken |

importance = 100 × Σ weight × sub-score / 5.

Grouping rule for the "top-k" lists: each list is built greedily by importance **subject to coverage constraints**, so that the
k selected sets together cover the task families (entity matching, schema/data integration, table QA, financial document QA,
free-form table QA, boolean/verification, numeric anchor, multilingual) in proportion to k. A set can be displaced by a
lower-scored one if the higher one adds no uncovered family. This is stated per list.

Per-version fit: v2/v4 (composite grading on QA-style answers) favour datasets with short golds of mixed answer types;
v3 (native metric per dataset + aggregation) favours datasets with a clear official metric and many items;
v5 (100-metric library + anchors) favours datasets with alias-derivable golds and diverse answer types, plus the
entity-matching sets that make the anchor ladder informative on booleans; the general anchors matter for v5 only.

## Amendment (2026-09-14, evidence-based revision)

* Group lists are built in three passes: (0) the top ⌈k/2⌉ datasets by importance are always included; (1) coverage quotas per family are filled with the best-ranked members of each family; (2) remaining slots by importance. Pass 0 was added because the quota sums for k = 40 and 50 exceeded k, which let a rank-13 dataset fall out of the top-40 list.
* Adoption (A) has an evidence-based variant computed from the citation-ranked paper corpus (`10_PAPER_CORPUS.md`, `paper_usage.csv`): A = 0.7·5·min(1, ln(1+n)/ln(1+A_MAX)) + 0.3·5·min(1, n₂₀₂₃₊/R_MAX), with n the number of corpus papers (core + supplementary) that evaluate on the dataset, n₂₀₂₃₊ those from 2023 on, and A_MAX, R_MAX the 90th percentiles over the corpus. Datasets absent from the corpus get A = 0 (A = 1 if introduced 2025–26). General-purpose anchor sets (family ANC) keep the judgement A because the corpus does not cover general QA. `rank_evidence.py` produces the `_evidence` outputs; `rank.py` the judgement outputs.
