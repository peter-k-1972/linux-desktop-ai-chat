"""
Read-only Port für Operations-/Audit-Sicht in QML (Welle 7).

Kombiniert dieselben produktiven Quellen wie ``AuditIncidentsWorkspace`` (Widget-GUI):
Audit-Events (DB), Runtime-Incidents (DB), QA-Datei-Index (``OperationsAdapter``),
Audit-Follow-ups (AUDIT_REPORT.md), Platform Health (``build_platform_health_summary``).
"""

from __future__ import annotations

from typing import Any, Optional, Protocol


class QmlOperationsReadPort(Protocol):
    def list_audit_events(
        self,
        *,
        limit: int,
        event_type: Optional[str],
    ) -> list[dict[str, Any]]:
        """Flache Zeilen für Listen (occurred_at, event_type, summary, …)."""

    def list_runtime_incidents(
        self,
        *,
        status: Optional[str],
        limit: int,
    ) -> list[dict[str, Any]]:
        """Runtime-Incidents aus dem Incident-Service (wie IncidentsPanel)."""

    def get_runtime_incident(self, incident_id: int) -> Optional[dict[str, Any]]:
        """Detail-Dict oder ``None``."""

    def load_qa_incident_index_snapshot(self) -> dict[str, Any]:
        """
        Kompakte QA-Index-Daten (``incidents/index.json`` über :class:`OperationsAdapter`).
        Keys u. a.: ``hasData``, ``incidentCount``, ``openCount``, ``warnings``, ``incidents`` (Liste flacher Dicts).
        """

    def load_audit_followup_snapshot(self) -> dict[str, Any]:
        """AUDIT_REPORT-Follow-ups: ``hasData``, ``byCategory``, ``items`` (flache Dicts)."""

    def get_platform_health_snapshot(self) -> dict[str, Any]:
        """``overall``, ``checkedAt``, ``checks`` (Liste flacher Dicts)."""
