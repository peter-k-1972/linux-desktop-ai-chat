"""
Platform Health – R2 Monitoring light.

Synchron, ohne Persistenz, ohne GUI. Bündelt bestehende Probes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.qa.operations_models import HealthCheckResult, PlatformHealthSummary
from app.services.infrastructure_snapshot import (
    build_data_store_rows,
    build_tool_snapshot_rows,
    probe_ollama_localhost,
)


def _rank(sev: str) -> int:
    return {"error": 2, "warning": 1, "ok": 0}.get(sev, 0)


def _merge_overall(checks: List[HealthCheckResult]) -> str:
    best = "ok"
    for c in checks:
        if _rank(c.severity) > _rank(best):
            best = c.severity
    return best


def build_platform_health_summary() -> PlatformHealthSummary:
    """Führt lokale Basischecks aus und aggregiert den Gesamtstatus."""
    checked_at = datetime.now(timezone.utc).isoformat()
    checks: List[HealthCheckResult] = []

    rows = build_data_store_rows()
    for r in rows:
        sev = "ok"
        if r.state in ("Fehler", "Keine Datei"):
            sev = "error"
        elif r.state in ("Leer", "Kein Index", "Modul fehlt"):
            sev = "warning"
        elif r.state in ("Fehlt",):
            sev = "warning"
        checks.append(
            HealthCheckResult(
                check_id=f"datastore:{r.store}",
                severity=sev,
                title=r.store,
                detail=f"{r.state}: {r.connection}",
            )
        )

    ollama_ok, ollama_detail = probe_ollama_localhost()
    checks.append(
        HealthCheckResult(
            check_id="provider:ollama_local",
            severity="ok" if ollama_ok else "error",
            title="Ollama (lokal)",
            detail=ollama_detail if ollama_ok else f"Nicht erreichbar: {ollama_detail}",
        )
    )

    try:
        tool_rows = build_tool_snapshot_rows()
        for tr in tool_rows:
            sev = "ok"
            low = (tr.status or "").lower()
            if "fehlt" in low and "optional" not in low:
                sev = "warning"
            checks.append(
                HealthCheckResult(
                    check_id=f"tool:{tr.tool_id}",
                    severity=sev,
                    title=f"Tool: {tr.tool_id}",
                    detail=tr.status,
                )
            )
    except Exception as exc:
        checks.append(
            HealthCheckResult(
                check_id="tool:snapshot",
                severity="warning",
                title="Tool-Übersicht",
                detail=f"Konnte nicht ermittelt werden: {exc}",
            )
        )

    return PlatformHealthSummary(
        overall=_merge_overall(checks),
        checked_at=checked_at,
        checks=checks,
    )
