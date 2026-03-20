"""
ModelsWorkspace – Verwaltung von Modellen.

Installed Models, Status, Details, Action-Fläche.
Anbindung an Ollama über ChatBackend.
"""

import asyncio
from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer

from app.gui.domains.control_center.workspaces.base_management_workspace import (
    BaseManagementWorkspace,
)
from app.gui.domains.control_center.panels.models_panels import (
    ModelListPanel,
    ModelSummaryPanel,
    ModelStatusPanel,
    ModelActionPanel,
)


def _format_size(size_bytes: int | float | None) -> str:
    if size_bytes is None:
        return "—"
    try:
        n = float(size_bytes)
        if n >= 1e9:
            return f"{n / 1e9:.1f} GB"
        if n >= 1e6:
            return f"{n / 1e6:.1f} MB"
        if n >= 1e3:
            return f"{n / 1e3:.1f} KB"
        return f"{n:.0f} B"
    except (TypeError, ValueError):
        return "—"


class ModelsWorkspace(BaseManagementWorkspace):
    """Workspace für Model-Verwaltung."""

    def __init__(self, parent=None):
        super().__init__("cc_models", parent)
        self._list_panel: ModelListPanel | None = None
        self._summary_panel: ModelSummaryPanel | None = None
        self._status_panel: ModelStatusPanel | None = None
        self._action_panel: ModelActionPanel | None = None
        self._models: List[Dict[str, Any]] = []
        self._selected_model: str | None = None
        self._setup_ui()
        self._connect_signals()
        QTimer.singleShot(0, self._defer_load)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._list_panel = ModelListPanel(self)
        self._status_panel = ModelStatusPanel(self)
        self._summary_panel = ModelSummaryPanel(self)
        self._action_panel = ModelActionPanel(self)

        content_layout.addWidget(self._list_panel)
        content_layout.addWidget(self._status_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._summary_panel)
        splitter.addWidget(self._action_panel)
        splitter.setSizes([300, 200])
        content_layout.addWidget(splitter)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def _connect_signals(self):
        if self._list_panel:
            self._list_panel.model_selected.connect(self._on_model_selected)
            self._list_panel.refresh_requested.connect(self._defer_load)
        if self._action_panel:
            self._action_panel.set_default_requested.connect(self._on_set_default)

    def _defer_load(self) -> None:
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._load_models())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_load)

    async def _load_models(self) -> None:
        if not self._list_panel or not self._status_panel:
            return
        self._list_panel.set_loading("Lade Modelle…")
        try:
            from app.services.model_service import get_model_service
            svc = get_model_service()
            result = await svc.get_models_full()
            models = result.data if result.success else []
            default = svc.get_default_model()
            self._models = models
            if models:
                self._list_panel.set_models(models)
                self._status_panel.set_status(len(models), default)
                if models and not self._selected_model:
                    name = models[0].get("name") or models[0].get("model", "")
                    if name:
                        self._on_model_selected(name)
            else:
                self._list_panel.set_empty("Keine Modelle – ist Ollama gestartet?")
                self._status_panel.set_status(0, default)
                self._on_model_selected("")
        except Exception as e:
            self._list_panel.set_error(f"Fehler: {e!s}")
            self._status_panel.set_status(0, "—")
            self._on_model_selected("")

    def _on_model_selected(self, model_name: str) -> None:
        self._selected_model = model_name or None
        if self._action_panel:
            self._action_panel.set_current_model(self._selected_model)
        m = self._find_model(model_name)
        if self._summary_panel:
            if m:
                size = _format_size(m.get("size"))
                try:
                    from app.services.model_service import get_model_service
                    default = get_model_service().get_default_model()
                except Exception:
                    default = ""
                self._summary_panel.set_model(
                    name=model_name,
                    provider="Ollama",
                    size=size,
                    is_default=(model_name == default),
                )
            else:
                self._summary_panel.set_model("—", "—", "—", False)
        self._refresh_inspector()

    def _find_model(self, name: str) -> Dict[str, Any] | None:
        for m in self._models:
            if (m.get("name") or m.get("model", "")) == name:
                return m
        return None

    def _on_set_default(self, model_name: str) -> None:
        if not model_name:
            return
        try:
            from app.services.model_service import get_model_service
            result = get_model_service().set_default_model(model_name)
            if not result.success:
                raise ValueError(result.error)
            self._on_model_selected(model_name)
            if self._status_panel:
                self._status_panel.set_status(len(self._models), model_name)
        except Exception as e:
            if self._list_panel:
                self._list_panel.set_error(f"Standard setzen fehlgeschlagen: {e!s}")

    def _refresh_inspector(self, content_token: int | None = None) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.model_inspector import ModelInspector
        m = self._find_model(self._selected_model or "")
        if m:
            size = _format_size(m.get("size"))
            self._inspector_host.set_content(
                ModelInspector(
                    model_name=self._selected_model or "—",
                    status="Bereit",
                    size=size,
                    model_type="Chat / Completion",
                ),
                content_token=content_token,
            )
        else:
            self._inspector_host.set_content(
                ModelInspector(
                    model_name="(keine Auswahl)",
                    status="—",
                    size="—",
                    model_type="—",
                ),
                content_token=content_token,
            )

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Model-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        self._refresh_inspector(content_token=content_token)
