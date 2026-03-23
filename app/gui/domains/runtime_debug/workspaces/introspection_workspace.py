"""
IntrospectionWorkspace – live internal diagnostics and transparency view.

Shows: Navigation, UI, Runtime, Service, and Recent Events state.
Uses existing sources: WorkspaceHost, ProjectContext, InspectorHost, EventBus, DebugStore.
"""

from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QTimer
from typing import Any

from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace


def _find_workspace_host(widget: QWidget):
    """Walk up to find WorkspaceHost."""
    p = widget.parent()
    while p:
        if p.__class__.__name__ == "WorkspaceHost":
            return p
        p = p.parent()
    return None


def _find_main_window(widget: QWidget):
    """Get top-level MainWindow."""
    w = widget.window()
    return w if w and "MainWindow" in w.__class__.__name__ else None


def _collect_navigation_state(workspace_host) -> dict[str, Any]:
    """Navigation state from WorkspaceHost and BreadcrumbManager."""
    out = {}
    try:
        out["current_area"] = getattr(workspace_host, "_current_area_id", "") or "—"
        out["current_workspace"] = getattr(workspace_host, "_current_workspace_id", "") or "—"
    except Exception:
        out["current_area"] = out["current_workspace"] = "—"
    try:
        from app.gui.breadcrumbs import get_breadcrumb_manager
        mgr = get_breadcrumb_manager()
        path = mgr.get_path() if mgr else []
        out["breadcrumb"] = " / ".join(p.title for p in path) if path else "—"
    except Exception:
        out["breadcrumb"] = "—"
    try:
        from app.core.navigation.help_topic_resolver import resolve_help_topic_with_title
        ws_id = workspace_host.get_current_workspace_id()
        resolved = resolve_help_topic_with_title(ws_id)
        out["help_topic"] = resolved[1] if resolved else "—"
    except Exception:
        out["help_topic"] = "—"
    try:
        from app.core.context.project_context_manager import get_project_context_manager
        proj = get_project_context_manager().get_active_project()
        out["active_project"] = proj.get("name", "—") if proj and isinstance(proj, dict) else "—"
    except Exception:
        out["active_project"] = "—"
    return out


def _collect_ui_state(main_window) -> dict[str, Any]:
    """UI state from MainWindow docks and theme."""
    out = {"inspector": "—", "bottom_panel": "—", "theme": "—"}
    if not main_window:
        return out
    try:
        inspector_dock = getattr(main_window, "_inspector_dock", None)
        out["inspector"] = "visible" if inspector_dock and inspector_dock.isVisible() else "hidden"
    except Exception:
        pass
    try:
        from PySide6.QtWidgets import QDockWidget
        docks = main_window.findChildren(QDockWidget) if main_window else []
        bottom = next((d for d in docks if d.objectName() == "bottomDock"), None)
        out["bottom_panel"] = "visible" if bottom and bottom.isVisible() else "hidden"
    except Exception:
        pass
    try:
        from app.gui.themes import get_theme_manager
        mgr = get_theme_manager()
        out["theme"] = mgr.get_current_id() or "—"
    except Exception:
        pass
    return out


def _collect_runtime_state() -> dict[str, Any]:
    """Runtime state from DebugStore."""
    out = {}
    try:
        from app.debug.debug_store import get_debug_store
        store = get_debug_store()
        tasks = store.get_active_tasks()
        running = [t for t in tasks if t.status == "running"]
        out["active_tasks"] = len(running)
        status = store.get_agent_status()
        out["agent_status"] = "; ".join(f"{k}: {v}" for k, v in list(status.items())[:5]) if status else "—"
    except Exception:
        out["active_tasks"] = "—"
        out["agent_status"] = "—"
    try:
        from app.debug.debug_store import get_debug_store
        store = get_debug_store()
        usage = store.get_model_usage()
        out["llm_calls_recent"] = sum(u.call_count for u in usage[:5]) if usage else 0
    except Exception:
        out["llm_calls_recent"] = "—"
    return out


def _collect_service_state() -> dict[str, Any]:
    """Service state from infrastructure and providers."""
    out = {}
    try:
        from app.services.infrastructure import get_infrastructure
        infra = get_infrastructure()
        out["db"] = "ready" if infra.database else "—"
    except Exception:
        out["db"] = "—"
    try:
        from app.services.knowledge_service import get_knowledge_service
        svc = get_knowledge_service()
        out["rag"] = "available" if svc else "—"
    except Exception:
        out["rag"] = "—"
    try:
        from app.services.infrastructure import get_infrastructure
        infra = get_infrastructure()
        out["ollama"] = "connected" if infra.ollama_client else "—"
    except Exception:
        out["ollama"] = "—"
    return out


def _collect_recent_events() -> list[str]:
    """Recent events from DebugStore."""
    try:
        from app.debug.debug_store import get_debug_store
        store = get_debug_store()
        events = store.get_event_history()[:10]
        return [f"{e.event_type}: {(e.message or '')[:50]}" for e in events]
    except Exception:
        return []


class IntrospectionWorkspace(BaseMonitoringWorkspace):
    """Live diagnostics: Navigation, UI, Runtime, Service, Recent Events."""

    def __init__(self, parent=None):
        super().__init__("rd_introspection", parent)
        self._card_labels: dict = {}
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._nav_card = self._make_card("Navigation State", [])
        self._ui_card = self._make_card("UI State", [])
        self._runtime_card = self._make_card("Runtime State", [])
        self._service_card = self._make_card("Service State", [])
        self._events_card = self._make_card("Recent Events", [])

        content_layout.addWidget(self._nav_card)
        content_layout.addWidget(self._ui_card)
        content_layout.addWidget(self._runtime_card)
        content_layout.addWidget(self._service_card)
        content_layout.addWidget(self._events_card)

        self._inspect_btn = QPushButton("Inspect Last Context")
        self._inspect_btn.setObjectName("inspectLastContextBtn")
        self._inspect_btn.setToolTip("Show context inspection for the last chat request (dev only)")
        self._inspect_btn.clicked.connect(self._on_inspect_last_context)
        content_layout.addWidget(self._inspect_btn)

        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._refresh()

    def _make_card(self, title: str, rows: list[tuple[str, str]]) -> QGroupBox:
        g = QGroupBox(title)
        g.setObjectName("introspectionCard")
        gl = QVBoxLayout(g)
        labels = {}
        for k, v in rows:
            row = QLabel(f"{k}: {v}")
            row.setObjectName("introspectionRow")
            row.setWordWrap(True)
            gl.addWidget(row)
            labels[k] = row
        self._card_labels[title] = (labels, gl)
        return g

    def _update_card(self, card: QGroupBox, title: str, rows: list[tuple[str, str]]):
        if title not in self._card_labels:
            return
        labels_dict, gl = self._card_labels[title]
        row_keys = [r[0] for r in rows]
        for k, v in rows:
            if k in labels_dict:
                labels_dict[k].setText(f"{k}: {v}")
                labels_dict[k].show()
            else:
                row = QLabel(f"{k}: {v}")
                row.setObjectName("introspectionRow")
                row.setWordWrap(True)
                gl.addWidget(row)
                labels_dict[k] = row
        for k in list(labels_dict.keys()):
            if k not in row_keys:
                labels_dict[k].hide()

    def _is_dev_mode(self) -> bool:
        """True when debug panel and context debug are enabled."""
        try:
            from app.context.debug.context_debug_flag import is_context_debug_enabled
            from app.services.infrastructure import get_infrastructure
            s = get_infrastructure().settings
            return (
                getattr(s, "debug_panel_enabled", True)
                and is_context_debug_enabled()
            )
        except Exception:
            return False

    def _on_inspect_last_context(self) -> None:
        """Open context inspection panel for last request. Dev mode only."""
        if not self._is_dev_mode():
            return
        try:
            from app.context.devtools.request_capture import get_last_request
            from app.gui.domains.debug import ContextInspectionPanel
            from app.services.context_explain_service import ContextExplainRequest

            last = get_last_request()
            if last is None:
                return

            request = ContextExplainRequest(
                chat_id=last["chat_id"],
                request_context_hint=last.get("request_context_hint"),
                context_policy=last.get("context_policy"),
            )

            dlg = QDialog(self.window())
            dlg.setWindowTitle("Context Inspection – Last Request")
            dlg.setMinimumSize(520, 480)
            dlg_layout = QVBoxLayout(dlg)
            dlg_layout.setContentsMargins(0, 0, 0, 0)
            panel = ContextInspectionPanel()
            panel.set_request(request)
            dlg_layout.addWidget(panel)
            dlg.exec()
        except Exception:
            pass

    def _refresh(self):
        if hasattr(self, "_inspect_btn"):
            self._inspect_btn.setVisible(self._is_dev_mode())
        wh = _find_workspace_host(self)
        mw = _find_main_window(self)

        nav = _collect_navigation_state(wh) if wh else {}
        nav_rows = [
            ("Area", nav.get("current_area", "—")),
            ("Workspace", nav.get("current_workspace", "—")),
            ("Breadcrumb", nav.get("breadcrumb", "—")),
            ("Help topic", nav.get("help_topic", "—")),
            ("Active project", nav.get("active_project", "—")),
        ]
        self._update_card(self._nav_card, "Navigation State", nav_rows)

        ui = _collect_ui_state(mw)
        ui_rows = [
            ("Inspector", ui.get("inspector", "—")),
            ("Bottom panel", ui.get("bottom_panel", "—")),
            ("Theme", ui.get("theme", "—")),
        ]
        self._update_card(self._ui_card, "UI State", ui_rows)

        rt = _collect_runtime_state()
        rt_rows = [
            ("Active tasks", str(rt.get("active_tasks", "—"))),
            ("Agent status", rt.get("agent_status", "—") or "—"),
            ("LLM calls (recent)", str(rt.get("llm_calls_recent", "—"))),
        ]
        self._update_card(self._runtime_card, "Runtime State", rt_rows)

        svc = _collect_service_state()
        svc_rows = [
            ("Database", svc.get("db", "—")),
            ("RAG / Chroma", svc.get("rag", "—")),
            ("Ollama", svc.get("ollama", "—")),
        ]
        self._update_card(self._service_card, "Service State", svc_rows)

        events = _collect_recent_events()
        ev_rows = [(f"Event {i+1}", e) for i, e in enumerate(events[:8])] or [("—", "No recent events")]
        self._update_card(self._events_card, "Recent Events", ev_rows)
