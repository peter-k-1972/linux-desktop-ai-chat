#!/usr/bin/env python3
"""
Validiert ein Theme-Manifest (JSON) gegen Schema + Major-Version.

Beispiel:
  python tools/validate_ui_theme_manifest.py app/ui_themes/builtins/light_default/manifest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Repo-Root auf sys.path (Aufruf: python tools/validate_ui_theme_manifest.py …)
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Theme-Manifest validieren")
    parser.add_argument("manifest", type=Path, help="Pfad zu manifest.json")
    args = parser.parse_args()
    path: Path = args.manifest
    if not path.is_file():
        print(f"Datei nicht gefunden: {path}", file=sys.stderr)
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("Manifest muss ein JSON-Objekt sein", file=sys.stderr)
        return 1
    try:
        from app.ui_runtime.manifest_models import theme_manifest_from_dict

        theme_manifest_from_dict(data, source_path=path.resolve())
    except Exception as exc:
        print(f"VALIDATION_FAILED: {exc}", file=sys.stderr)
        return 1
    print("OK", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
