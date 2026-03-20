"""
Trace Map Loader – read docs/TRACE_MAP.md.

Provides: workspace -> help, workspace -> code, services list.
"""

import re
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def load_workspace_to_help() -> dict[str, str]:
    """Parse TRACE_MAP.md section 3. Returns workspace_id -> help_topic_id."""
    path = _PROJECT_ROOT / "docs" / "TRACE_MAP.md"
    result: dict[str, str] = {}
    if not path.exists():
        return result

    text = path.read_text(encoding="utf-8")
    in_section = False
    for line in text.splitlines():
        if "## 3. Workspace → Help" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            m = re.match(r"\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", line)
            if m:
                result[m.group(1).strip()] = m.group(2).strip()
    return result


def load_workspace_to_code() -> dict[str, list[str]]:
    """Parse TRACE_MAP.md section 1. Returns workspace_path -> [code_paths]."""
    path = _PROJECT_ROOT / "docs" / "TRACE_MAP.md"
    result: dict[str, list[str]] = {}
    if not path.exists():
        return result

    text = path.read_text(encoding="utf-8")
    in_section = False
    for line in text.splitlines():
        if "## 1. Workspace → Code" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            m = re.match(r"\|\s*(.+?)\s*\|\s*`([^`]+)`\s*\|", line)
            if m:
                ws_key = m.group(1).strip()
                code_path = m.group(2).strip()
                result.setdefault(ws_key, []).append(code_path)
    return result


def load_services() -> list[str]:
    """Parse TRACE_MAP.md section 2. Returns list of service paths."""
    path = _PROJECT_ROOT / "docs" / "TRACE_MAP.md"
    result: list[str] = []
    if not path.exists():
        return result

    text = path.read_text(encoding="utf-8")
    in_section = False
    for line in text.splitlines():
        if "## 2. Services" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- `"):
            m = re.match(r"-\s*`([^`]+)`", line)
            if m:
                result.append(m.group(1).strip())
    return result
