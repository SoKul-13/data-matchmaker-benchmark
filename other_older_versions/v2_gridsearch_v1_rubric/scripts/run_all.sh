#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
$PY scripts/01_v1_components.py
$PY scripts/02_gridsearch.py
