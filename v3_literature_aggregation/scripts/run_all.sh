#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
$PY scripts/01_native_scores.py
$PY scripts/02_gridsearch_views.py
