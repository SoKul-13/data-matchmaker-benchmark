#!/usr/bin/env bash
# v2 (v6 edition): exhaustive grid + designs, nested selection / plateau / transfer / sensitivity, anchor correctness, leaderboards + significance, report.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python v2_gridsearch/scripts/01_v1_components.py
uv run python v2_gridsearch/scripts/02_exhaustive_grid.py "$@"
uv run python v2_gridsearch/scripts/03_selection_validity.py
uv run python v2_gridsearch/scripts/04_correctness_anchors.py
uv run python v2_gridsearch/scripts/05_leaderboards.py
uv run python v2_gridsearch/scripts/06_report.py
