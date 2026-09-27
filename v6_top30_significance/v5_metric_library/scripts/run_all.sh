#!/usr/bin/env bash
# v5 (v6 edition): matrix (models + anchors for every pool) -> metric selection -> exhaustive grid + ensemble -> leaderboard -> validation -> notes;
# then designs vs exhaustive, leaderboards with significance under em / native / ensemble / top-5, and REPORT.md.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python v5_metric_library/scripts/01_compute_matrix.py
uv run python v5_metric_library/scripts/02_select_metrics.py
uv run python v5_metric_library/scripts/03_grid_weights.py
uv run python v5_metric_library/scripts/04_leaderboard.py
uv run python v5_metric_library/scripts/05_validate.py
uv run python v5_metric_library/scripts/06_report.py || echo "06_report (paper notes) failed; continuing"
uv run python v5_metric_library/scripts/07_designs_leaderboards.py
uv run python v5_metric_library/scripts/08_report.py
