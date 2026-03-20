"""
OperationsContext – Pending context für Hub→Workspace-Navigation.

Wenn der Project Hub zu einem Workspace navigiert und ein bestimmtes Objekt
öffnen möchte (Chat, Prompt, Quelle), wird der Kontext hier gesetzt.
Der Ziel-Workspace konsumiert ihn beim Anzeigen.
"""

_pending_context: dict = {}


def set_pending_context(ctx: dict | None) -> None:
    """Setzt den ausstehenden Kontext (z.B. vor show_area)."""
    global _pending_context
    _pending_context.clear()
    if ctx:
        _pending_context.update(ctx)


def consume_pending_context() -> dict:
    """Liefert und löscht den ausstehenden Kontext."""
    global _pending_context
    ctx = dict(_pending_context)
    _pending_context.clear()
    return ctx


def get_pending_context() -> dict:
    """Liefert den Kontext ohne zu löschen (für Prüfung)."""
    return dict(_pending_context)
