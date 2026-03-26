"""Einheitliches Ergebnisformat für Cursor-light Tools."""

from __future__ import annotations

from typing import Any, Dict, Optional


def tool_result(
    success: bool,
    *,
    data: Any = None,
    error: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Kanonisches Format für tool_call-Ausgabe (cursor_light).

    error: bei Misserfolg dict mit mindestens code + message (strukturiert).
    """
    return {
        "success": success,
        "data": data,
        "error": error,
        "metadata": metadata or {},
    }


def err(code: str, message: str, **details: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"code": code, "message": message}
    if details:
        out["details"] = details
    return out
