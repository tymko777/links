#!/usr/bin/env bash
set -euo pipefail

python3 -m compileall -q links tests
python3 -m unittest discover -s tests -v

if command -v ruff >/dev/null 2>&1; then
  ruff check .
else
  echo "ruff is not installed; syntax and unit checks completed."
fi
