#!/usr/bin/env bash
# v3 end-to-end from cached predictions (minutes, no API calls).  Step 0 (model run) is manual: see notes/06_USER_TODO.md
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
$PY scripts/01_compute_matrix.py        # 100 metrics for models and anchors
$PY scripts/02_select_metrics.py        # dedupe + anchor-based selection (add --labels file.csv for human labels)
$PY scripts/03_grid_weights.py          # grid over selected metrics, top-100 ensemble
$PY scripts/04_leaderboard.py           # pooled leaderboard
$PY scripts/05_validate.py              # LODO, severity perturbation, probes
$PY scripts/06_report.py                # figures, tables, numbers.tex, notes/04_RESULTS.md
command -v tectonic >/dev/null 2>&1 && (cd paper && tectonic main.tex) || true
echo done
