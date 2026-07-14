#!/usr/bin/env bash
# Atlas OS - Streamlit dashboard launcher
# Usage: ./scripts/run_ui.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}"
exec python -m streamlit run ui/dashboard.py
