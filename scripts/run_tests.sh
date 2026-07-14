#!/usr/bin/env bash
# Atlas OS - test runner
# Usage: ./scripts/run_tests.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}"
exec python -m pytest tests/ -v
