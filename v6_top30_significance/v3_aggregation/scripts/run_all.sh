#!/usr/bin/env bash
# v3 (v6 edition): native scores; 8 views + all 255 combinations + LHS/lattice mixes + params with SE + split-half honesty; leaderboards + significance; report.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python v3_aggregation/scripts/01_native_scores.py
uv run python v3_aggregation/scripts/02_views_combos.py "$@"
uv run python v3_aggregation/scripts/03_leaderboards.py
uv run python v3_aggregation/scripts/04_report.py
