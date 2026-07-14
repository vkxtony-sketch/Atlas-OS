#!/usr/bin/env bash
# Atlas OS - CLI launcher
# Usage: ./scripts/run_cli.sh "your goal"
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}"
GOAL="${1:-build a sample goal}"
exec python "${ROOT}/main.py" "${GOAL}"
