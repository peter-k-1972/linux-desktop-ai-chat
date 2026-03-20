#!/bin/bash
# Starter für Linux Desktop Chat
# Wechselt ins Projektverzeichnis, aktiviert die venv und startet die neue GUI-Shell

cd "$(dirname "$(realpath "$0")")"
source .venv/bin/activate
exec python -m app "$@"
