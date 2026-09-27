#!/usr/bin/env bash
# v4 (v6 edition): 9-component composite; Dirichlet / LHS / uniform designs; nested selection; anchors; leaderboards + significance; report.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python v4_random_search/scripts/01_components.py
uv run python v4_random_search/scripts/02_designs.py "$@"
uv run python v4_random_search/scripts/03_selection_validity.py
uv run python v4_random_search/scripts/04_correctness_anchors.py
uv run python v4_random_search/scripts/05_leaderboards.py
uv run python v4_random_search/scripts/06_report.py
