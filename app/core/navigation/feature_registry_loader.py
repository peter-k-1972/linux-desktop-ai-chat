"""
Feature Registry Loader – read docs/FEATURE_REGISTRY.md.

Returns workspace_id -> {feature_name, code, services, help, tests}.
"""

import re
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def load_feature_registry() -> dict[str, dict]:
    """
    Parse docs/FEATURE_REGISTRY.md.
    Returns workspace_id -> {feature_name, code, services, help, tests}.
    """
    path = _PROJECT_ROOT / "docs" / "FEATURE_REGISTRY.md"
    result: dict[str, dict] = {}
    if not path.exists():
        return result

    text = path.read_text(encoding="utf-8")
    current_ws: Optional[str] = None
    current_feature = ""
    current_code: list[str] = []
    current_services: list[str] = []
    current_help = ""
    current_tests: list[str] = []

    for line in text.splitlines():
        m = re.match(r"^### (.+)$", line)
        if m:
            if current_ws and current_feature:
                result[current_ws] = {
                    "feature_name": current_feature,
                    "code": list(current_code),
                    "services": list(current_services),
                    "help": current_help,
                    "tests": list(current_tests),
                }
            current_feature = m.group(1).strip()
            current_ws = None
            current_code = []
            current_services = []
            current_help = ""
            current_tests = []
            continue

        m = re.match(r"^\|\s*Workspace\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            current_ws = m.group(1).strip()
            continue

        m = re.match(r"^\|\s*Code\s*\|\s*(.+)\s*\|", line)
        if m and current_ws:
            val = m.group(1).strip()
            if val and val != "—":
                for part in re.split(r",\s*(?![^(]*\))", val):
                    part = re.sub(r"`([^`]+)`", r"\1", part).strip()
                    if part and not part.startswith("+"):
                        current_code.append(part)
            continue

        m = re.match(r"^\|\s*Services\s*\|\s*(.+)\s*\|", line)
        if m and current_ws:
            val = m.group(1).strip()
            if val and val != "—":
                for part in re.split(r",\s*", val):
                    part = part.strip().strip("`")
                    if part:
                        current_services.append(part)
            continue

        m = re.match(r"^\|\s*Help\s*\|\s*(.+)\s*\|", line)
        if m and current_ws:
            val = m.group(1).strip().strip("`")
            if val and val != "—":
                current_help = val
            continue

        m = re.match(r"^\|\s*Tests\s*\|\s*(.+)\s*\|", line)
        if m and current_ws:
            val = m.group(1).strip()
            if val and val != "—":
                for part in re.split(r",\s*(?![^(]*\))", val):
                    part = re.sub(r"`([^`]+)`", r"\1", part).strip()
                    if part and not part.startswith("+") and part.endswith(".py"):
                        current_tests.append(part)
            continue

    if current_ws and current_feature:
        result[current_ws] = {
            "feature_name": current_feature,
            "code": list(current_code),
            "services": list(current_services),
            "help": current_help,
            "tests": list(current_tests),
        }

    return result


def get_feature_for_workspace(workspace_id: str) -> Optional[dict]:
    """Get feature metadata for a workspace."""
    return load_feature_registry().get(workspace_id)
