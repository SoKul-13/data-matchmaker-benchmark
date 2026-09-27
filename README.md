# Data Matchmaker Benchmark

Green-agent evaluator for the AgentBeats A2A platform: a judge that scores AI models on data-matching work
(record matching, financial table and document question answering, table integration) across many datasets and
turns the scores into one comparable leaderboard. Five versions, each a self-contained `uv` project. Read
[OVERALL_SUMMARY.md](OVERALL_SUMMARY.md) first (every version from the ground up, what has been run, what still must run, pros and cons vs industry practice),
then [FINAL_v2/](FINAL_v2/README.md) for the final, self-contained v2 (the version to run and to write up), [v6_top30_significance/](v6_top30_significance/README.md) for the same v2 next to v3, v4 and v5 on the shared suite (all four versions on the 31-dataset suite with exhaustive / LHS designs, honest selection, parameter dumps and significance tests; one REPORT.md per version), [GUIDE_UNDER_THE_HOOD.md](GUIDE_UNDER_THE_HOOD.md) for the formulas and [SEARCH_DESIGN_REPORT.md](SEARCH_DESIGN_REPORT.md) for exactly how each version generates and evaluates its weight candidates, [PRE_RUN_REVIEW.md](PRE_RUN_REVIEW.md) for the known weaknesses and the fixes planned in v6, and [TOP30_DATASETS_AND_PRE_RUN_NOTES.md](TOP30_DATASETS_AND_PRE_RUN_NOTES.md) for the 30 datasets of the next run with what each is and why, [V2_VARIANTS_PLAN.md](V2_VARIANTS_PLAN.md) for the five v2-style variants planned for the paper, and [DECISIONS_AND_RATIONALE.md](DECISIONS_AND_RATIONALE.md) for every open design decision with options, trade-offs, the call and the literature; the dataset survey (100 ranked datasets with adoption measured from a citation-ranked corpus of ≈220 papers, 5…50 groupings, per-version fit) is in [datasets_survey/](datasets_survey/README.md); each folder has a `notes/CODE_FLOW.md` listing every script, function and file.

| Folder | Test | What it does | Weights chosen how | Checked against |
|---|---|---|---|---|
| `FINAL_v2/` | **final v2** | exhaustive 1,771-point grid over v1's four weights on the 31-dataset suite; honest selection, transfer, anchors, leaderboards with significance, official-split estimates | see `FINAL_v2/README.md` | runs on cached answers; model run pending |
| `other_older_versions/v1/` | original judge | TPC-DI join task + hand-set 4-metric rubric `0.35 F1 + 0.35 decay + 0.15 P + 0.15 R` | by hand | nothing |
| `other_older_versions/v2_gridsearch_v1_rubric/` | grid over v1's weights | same four ingredients, 105 weightings (v1 + corners + 100 random grid points) scored by cross-dataset rank agreement | grid search | agreement among the models being ranked |
| `other_older_versions/v3_literature_aggregation/` | literature aggregation views | ten papers reviewed; eight of their aggregation rules (win rate, Borda, Kemeny, Bradley–Terry, IRT ability, baseline-normalised mean, z-mean, raw mean) on each dataset's own metric; 109 mixes scored by stability, transitivity and agreement with a Kemeny reference | grid search over the view mix | bootstrap stability + consensus |
| `other_older_versions/v4_random_search_rank_agreement/` | random search, rank agreement | 9-metric composite, 100 random weightings, objective = mean τ to the Borda-pooled ranking; pooling with Borda/Kemeny/RRF; bootstrap; LODO; KL/JS as extension; 14 dataset adapters; paper | random search | agreement among the models being ranked |
| `other_older_versions/v5_metric_library_anchor_ensemble/` | metric library + anchors | 100 answer-level metrics, 12,813 synthetic answers of known quality, correlation dedup + out-of-dataset forward selection, grid × hedge penalty with the 100 best weightings averaged, difficulty-adjusted leaderboard, LODO and severity perturbation; paper; full notes | grid search + ensemble | synthetic answers of known quality + native metrics |

All five use the same cached model answers (`data/predictions/`, 4 models × 7 datasets × 40 items) so results are
comparable; v4/v5 also carry 7 further datasets with items prepared and predictions pending (see
`other_older_versions/v5_metric_library_anchor_ensemble/notes/06_USER_TODO.md`). API keys go in a `.env` inside the folder you run; `.env`
files are git-ignored.
