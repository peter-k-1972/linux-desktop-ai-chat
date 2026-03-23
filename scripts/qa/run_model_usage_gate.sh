#!/usr/bin/env bash
# Lokales Subsystem-Gate: Usage/Ledger, Aggregation, Quota, Runtime-Instrumentierung, Asset-Scan.
# Kein Live-Ollama / keine Qt-E2E. Aufruf vom Projektroot oder hier: ./scripts/qa/run_model_usage_gate.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
exec pytest -m model_usage_gate -q --tb=short "$@"
