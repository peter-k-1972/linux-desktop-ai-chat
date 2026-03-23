"""
OperationsContext – Pending context für Navigation in Operations (und angrenzende Bereiche).

Wenn z. B. **Operations → Projekte**, die Kommandopalette oder ein Deep-Link zu einem Workspace
wechselt und dabei ein bestimmtes Objekt fokussieren soll (Chat, Prompt, Quelle, Run, Tab),
wird der Kontext hier gesetzt. Der Ziel-Workspace konsumiert ihn in ``show_workspace`` / ``open_with_context``.

Konvention (Workflow-Ops O4 / R1, von OperationsScreen.show_workspace konsumiert):
- ``workflow_ops_scope`` (str): ``"project"`` → WorkflowsWorkspace legt die Run-Liste
  auf „Aktives Projekt“ und aktualisiert die Runs.
- ``workflow_ops_run_id`` (str): Run in der Workflow-Run-Tabelle fokussieren (R1).
- ``workflow_ops_workflow_id`` (str, optional): zugehörigen Workflow laden, wenn der Editor
  nicht dirty ist; sonst wird die Run-Liste auf „Alle Runs“ gestellt.

Weitere Keys (Chat / Prompt Studio / Knowledge):
- ``chat_id``, ``prompt_id``, ``source_path``

R2 (Agent Operations / Monitoring light):
- ``workflow_ops_select_workflow_id`` (str): WorkflowsWorkspace lädt diese Definition
  (nach ``workflow_ops_scope`` / Run-Handling), wenn der Editor nicht dirty ist.
- ``audit_incidents_tab`` (str): ``activity`` | ``incidents`` | ``platform`` —
  Ziel-Tab im Betrieb-Workspace.
- ``agent_ops_focus_agent_id`` (str): AgentTasksWorkspace wählt diesen Agenten in der
  Betriebsliste (nach Refresh).
- ``agent_ops_subtab`` (str): ``betrieb`` | ``tasks`` — welcher Haupt-Tab aktiv ist.
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
