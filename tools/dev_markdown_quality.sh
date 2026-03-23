#!/usr/bin/env bash
# Lokaler Shortcut: Markdown Quality Gate aus dem Repository-Root.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec python3 tools/run_markdown_quality_gate.py "$@"
