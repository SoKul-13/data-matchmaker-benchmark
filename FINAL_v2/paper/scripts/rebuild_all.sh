#!/usr/bin/env bash
# Rebuild everything from the cached answers: the four pipelines, then every report, package, figure and analysis under paper/.
# Run from FINAL_v2:  bash paper/scripts/rebuild_all.sh            (pipelines + paper; about 2.5 h, v3's split-half is the slow step)
#                     bash paper/scripts/rebuild_all.sh --paper    (paper outputs only, from the existing pipeline outputs; a few minutes)
set -euo pipefail
cd "$(dirname "$0")/../.."                      # FINAL_v2
V6=../v6_top30_significance
STAMP=$(date +%Y-%m-%d_%H%M)

if [[ "${1:-}" != "--paper" ]]; then
  echo "== pipelines (logs: <version>/output/_rerun_$STAMP.log)"
  bash v2_gridsearch/scripts/run_all.sh > v2_gridsearch/output/_rerun_$STAMP.log 2>&1 &
  (cd $V6/v4_random_search  && bash scripts/run_all.sh > output/_rerun_$STAMP.log 2>&1) &
  (cd $V6/v5_metric_library && bash scripts/run_all.sh > output/_rerun_$STAMP.log 2>&1) &
  (cd $V6/v3_aggregation    && bash scripts/run_all.sh > output/_rerun_$STAMP.log 2>&1) &
  wait
  for d in v2_gridsearch $V6/v3_aggregation $V6/v4_random_search $V6/v5_metric_library; do
    if grep -q Traceback $d/output/_rerun_$STAMP.log; then echo "FAILED: $d (see $d/output/_rerun_$STAMP.log)"; exit 1; fi
    echo "ok: $d $(grep -o 'Generated [0-9-]* [0-9:]*' $d/REPORT.md | head -1)"
  done
fi

echo "== paper outputs"
uv run python paper/scripts/make_overleaf_package.py        # paper/v2/ (+ reading guide per figure) and v2_overleaf.zip
uv run python paper/scripts/make_version_packages.py        # paper/v3 v4 v5 comparison and their zips
uv run python paper/scripts/detailed_analysis_v2.py         # paper/v2/DETAILED_ANALYSIS.md
uv run python paper/scripts/md_to_html_report.py            # paper/v2/DETAILED_ANALYSIS.html
uv run python paper/scripts/make_paper_figures.py           # paper/v2/figures_paper/ (16 paper figures, FIGURES.md, figures_paper.tex)
(cd paper/v2 && rm -f ../v2_figures_paper.zip && zip -qr ../v2_figures_paper.zip figures_paper)

echo "== compile"
(cd paper && tectonic summary_results.tex >/dev/null 2>&1 && echo "ok: summary_results.pdf")
for v in v2 v3 v4 v5 comparison; do (cd paper/$v && tectonic main.tex >/dev/null 2>&1 && echo "ok: $v/main.pdf"); done
echo "done. Hand-written numbers live in paper/summary_results.tex and notes/{EVAL_PROCESS,FINAL_V2_REVIEW,PROJECT_SUMMARY}.md: re-check them against v2_gridsearch/REPORT.md."
