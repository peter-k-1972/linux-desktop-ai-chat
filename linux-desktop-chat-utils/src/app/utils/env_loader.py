"""
Zentrales .env-Loading für die Anwendung.

Lädt .env einmalig aus Projektroot oder aktuellem Verzeichnis in os.environ.
Mehrfaches Laden wird verhindert; bestehende Umgebungsvariablen bleiben unverändert.
"""

from __future__ import annotations

import os
from pathlib import Path

_loaded: bool = False


def load_env() -> None:
    """
    Lädt .env einmalig in os.environ.

    Suchreihenfolge: Projektroot (wie get_project_root()), dann Path.cwd().
    Setzt nur Variablen, die noch nicht in os.environ existieren.
    """
    global _loaded
    if _loaded:
        return

    from app.utils.paths import get_project_root

    roots = [
        get_project_root(),
        Path.cwd(),
    ]
    env_path = None
    for root in roots:
        p = root / ".env"
        if p.exists():
            env_path = p
            break
    if not env_path:
        _loaded = True
        return
    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
    except OSError:
        pass
    finally:
        _loaded = True
