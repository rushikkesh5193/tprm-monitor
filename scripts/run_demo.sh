#!/usr/bin/env bash
# Regenerate the synthetic inventory and produce the example report.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/gen_vendors.py examples/sample_vendors.json
python3 -m tprm examples/sample_vendors.json --as-of 2026-10-23 --out-dir examples
python3 -m unittest discover -s tests
