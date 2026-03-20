"""
QA Knowledge Graph – Hilfsfunktionen.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_KNOWLEDGE_GRAPH_DIR = Path(__file__).resolve().parent
_QA_DIR = _KNOWLEDGE_GRAPH_DIR.parent
_SCRIPTS_DIR = _QA_DIR.parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent

DEFAULT_DOCS_QA = _PROJECT_ROOT / "docs" / "qa"


def get_project_root() -> Path:
    """Projekt-Root-Verzeichnis."""
    return _PROJECT_ROOT


def get_docs_qa_dir(base: Path | None = None) -> Path:
    """docs/qa Verzeichnis."""
    return (base or _PROJECT_ROOT) / "docs" / "qa"


def load_json(path: Path | None) -> dict[str, Any] | None:
    """Lädt JSON-Datei. Gibt None bei Fehler oder fehlender Datei."""
    if path is None:
        return None
    if not path.exists() or not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def parse_regression_catalog_md(content: str) -> dict[str, Any]:
    """
    Extrahiert aus REGRESSION_CATALOG.md: failure_class → test_domains.
    Deterministisch, gleiche Logik wie generate_qa_graph.
    """
    result: dict[str, Any] = {
        "failure_class_to_domains": {},
        "failure_class_to_tests": {},
        "test_domains": [],
    }
    current_domain: str | None = None
    seen_domains: set[str] = set()

    for line in content.split("\n"):
        if "## Historische Bugs" in line or "## Erweiterung" in line:
            current_domain = None
            continue
        m_domain = re.match(r"^###\s+(.+)/?\s*$", line)
        if m_domain:
            current_domain = m_domain.group(1).strip().rstrip("/")
            if current_domain and current_domain not in seen_domains:
                seen_domains.add(current_domain)
                result["test_domains"].append(current_domain)
            continue

        if line.strip().startswith("|") and "---" not in line and current_domain:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3:
                datei, test, fehlerklasse = parts[0], parts[1], parts[2]
                if (
                    datei
                    and datei != "Datei"
                    and test
                    and test != "Test"
                    and datei.startswith("test_")
                ):
                    if fehlerklasse and fehlerklasse not in ("–", "-"):
                        for fk in [x.strip() for x in fehlerklasse.split(",")]:
                            fk = fk.strip()
                            # Normalisiere: "ui_state_drift (streaming hängt)" -> "ui_state_drift"
                            if " (" in fk:
                                fk = fk.split(" (")[0].strip()
                            if fk and re.match(r"^[a-z_]+$", fk):
                                if fk not in result["failure_class_to_domains"]:
                                    result["failure_class_to_domains"][fk] = []
                                if current_domain not in result["failure_class_to_domains"][fk]:
                                    result["failure_class_to_domains"][fk].append(current_domain)
                                if fk not in result["failure_class_to_tests"]:
                                    result["failure_class_to_tests"][fk] = []
                                entry = f"{current_domain}/{datei}::{test}"
                                if entry not in result["failure_class_to_tests"][fk]:
                                    result["failure_class_to_tests"][fk].append(entry)

    result["test_domains"] = sorted(seen_domains)
    return result


def _to_relative_source(path: Path, project_root: Path) -> str:
    """Konvertiert Pfad zu relativem Source-String."""
    try:
        rel = path.resolve().relative_to(project_root.resolve())
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(path)
