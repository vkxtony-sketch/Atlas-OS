#!/usr/bin/env bash
# Atlas OS - FastAPI server launcher
# Usage: ./scripts/run_api.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}"
exec python -m uvicorn api.server:app --host "${ATLAS_API_HOST:-127.0.0.1}" --port "${ATLAS_API_PORT:-8000}"
