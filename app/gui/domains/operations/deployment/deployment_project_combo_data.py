"""
Projektliste für Deployment-Dialogs (Ziel/Release).

Zentraler Lesezugriff, damit Dialoge keinen ``get_project_service`` mehr enthalten müssen.
"""

from __future__ import annotations


def list_project_label_id_pairs() -> list[tuple[str, int]]:
    """``(Anzeigename, project_id)`` für Projekt-Combos in Deployment-Dialogen."""
    try:
        from app.services.project_service import get_project_service

        out: list[tuple[str, int]] = []
        for p in get_project_service().list_projects():
            pid = p.get("project_id")
            if pid is None:
                continue
            label = (p.get("name") or "").strip() or f"Projekt {pid}"
            out.append((label, int(pid)))
        return out
    except Exception:
        return []
