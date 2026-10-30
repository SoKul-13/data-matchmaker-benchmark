# Paper folder: summary reports, organised by version

Every report is a self-contained Overleaf project (upload the folder or its zip, compile `main.tex` with pdfLaTeX). Each contains only two written sections, **Setup** and **Results**, followed by an appendix that includes every figure and every table that can be drawn from that version's saved outputs. The `data/` folder of each package holds the raw CSV / JSON / NPZ outputs so any number can be re-derived.

| Folder | Report | Source of the numbers | Zip |
|---|---|---|---|
| `v2/` | Summary report, v2: exhaustive grid over the deployed judge's four weights (the final version) | `FINAL_v2/v2_gridsearch/output/` (run 2026-09-27 13:12) | `v2_overleaf.zip` |
| `v3/` | Summary report, v3: eight aggregation views, all 255 subsets + 200 sampled mixes, parameters with standard errors | `v6_top30_significance/v3_aggregation/output/` | `v3_overleaf.zip` |
| `v4/` | Summary report, v4: nine-component composite, three sampled designs, honest selection | `v6_top30_significance/v4_random_search/output/` | `v4_overleaf.zip` |
| `v5/` | Summary report, v5: 100-metric library calibrated on 31,380 anchors, top-100 ensemble | `v6_top30_significance/v5_metric_library/output/` | `v5_overleaf.zip` |
| `comparison/` | Summary report: the four audits side by side, results compared on common axes, and what is better per version | the four packages above | `comparison_overleaf.zip` |

All four versions run on the same 31 datasets, the same ten models and the same cached answers, so their leaderboards are directly comparable; the comparison report is where that comparison is made.

## Contents of each package
* `main.tex` - Setup, Results (one figure or table per result, short prose), appendix A (all figures), appendix B (all tables).
* `figures/` - PNG (and PDF where generated) for every figure; captions are in `main.tex`.
* `tables/` - one `.tex` file per table; include any of them in your own text with `\input{tables/<name>.tex}`.
* `data/` - the version's full output folder (grid / candidates, selection, anchors, leaderboards per rule with bootstrap draws and significance, diagnostics, coverage, manifest) plus its `REPORT.md`.
* `README.md` - file counts and provenance.
* `main.pdf` - compiled locally with tectonic as a check (not needed by Overleaf).

## Other files here
* `summary_results.tex` / `summary_results.pdf` - the Setup + Results text of the v2 report on its own (the same text that `v2/main.tex` starts with), with a one-line summary per section and a *Notable* paragraph under every figure and table. Its tables are `\input` from `v2/tables/`, so it is only as current as the last package build.
* `v2/DETAILED_ANALYSIS.md` / `.html` - section-by-section analysis of every v2 output file (run facts, scoring, grid, selection, transfer, anchors, leaderboards, significance, comparability, diagnostics); the HTML embeds the figures.
* `v2/figures_paper/` and `v2_figures_paper.zip` - the 16 publication figures (PDF + PNG), `FIGURES.md` with captions and placement, `figures_paper.tex` with ready `\begin{figure}` blocks.
* `v2/main.tex` appendix A carries a reading guide (what it encodes, how to read it, what it shows) under each of the 47 figures; the text lives in `scripts/figure_explanations_v2.py`.
* `PAPER_PLAN.md`, `METHODS_AND_RELATED_WORK.md`, `DATASETS_TABLE.md`, `draft.md` - planning notes, the methods / related-work write-up, the 31-dataset table and the partial paper draft.
* `figures/` - the eleven original v2 figures (also copied into `v2/figures/`).
* `scripts/rebuild_all.sh` - one command for everything: the four pipelines, then every package, analysis and figure, then the compiles (`--paper` skips the pipelines). The individual steps: `make_overleaf_package.py` (v2), `make_version_packages.py` (v3, v4, v5, comparison), `detailed_analysis_v2.py`, `md_to_html_report.py`, `make_paper_figures.py`. Run from `FINAL_v2/` with `uv run python ...`.
