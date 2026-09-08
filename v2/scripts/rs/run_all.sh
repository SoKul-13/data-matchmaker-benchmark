#!/usr/bin/env bash
# Reproduce the v2 paper from the cached predictions (no API calls): ~1 minute.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-.venv/bin/python}
$PY scripts/rs/01_prepare.py
$PY scripts/rs/02_random_search.py
$PY scripts/rs/03_pool_report.py
$PY extensions/divergence_extension.py > output/rs/divergence_extension_demo.txt
command -v tectonic >/dev/null 2>&1 && (cd paper && tectonic main.tex)
echo done
