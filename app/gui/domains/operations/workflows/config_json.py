"""JSON-Hilfen für Workflow-Node-config (GUI, ohne Qt)."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple


def parse_node_config_json(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Parst config-JSON. Leerer Text -> {}.
    Returns:
        (dict, None) bei Erfolg, (None, fehlermeldung) bei Fehler.
    """
    raw = (text or "").strip()
    if not raw:
        return {}, None
    try:
        val = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"JSON: {e}"
    if not isinstance(val, dict):
        return None, "Die Konfiguration muss ein JSON-Objekt sein."
    return val, None


def format_node_config_json(config: Dict[str, Any]) -> str:
    """Formatiert config für Anzeige (sort_keys für Stabilität)."""
    if not config:
        return ""
    return json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True)
