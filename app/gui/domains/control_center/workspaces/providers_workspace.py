"""
ProvidersWorkspace – Verwaltung von Providern.

Provider List, Status, Endpoint, Runtime Availability.
Anbindung an Ollama über ChatBackend.
"""

import asyncio
from typing import Any, Dict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import QTimer

from app.gui.domains.control_center.workspaces.base_management_workspace import (
    BaseManagementWorkspace,
)
from app.gui.domains.control_center.panels.providers_panels import (
    ProviderListPanel,
    ProviderStatusPanel,
    ProviderSummaryPanel,
)
from app.gui.shared.layout_constants import CARD_SPACING, SCREEN_PADDING


class ProvidersWorkspace(BaseManagementWorkspace):
    """Workspace für Provider-Verwaltung."""

    def __init__(self, parent=None):
        super().__init__("cc_providers", parent)
        self._list_panel: ProviderListPanel | None = None
        self._status_panel: ProviderStatusPanel | None = None
        self._summary_panel: ProviderSummaryPanel | None = None
        self._ollama_info: Dict[str, Any] | None = None
        self._selected_provider: str | None = None
        self._setup_ui()
        self._connect_signals()
        QTimer.singleShot(0, self._defer_load)

    def _setup_ui(self):
        self.setObjectName("providersWorkspaceRoot")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            SCREEN_PADDING, SCREEN_PADDING, SCREEN_PADDING, SCREEN_PADDING
        )
        layout.setSpacing(CARD_SPACING)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._list_panel = ProviderListPanel(self)
        self._status_panel = ProviderStatusPanel(self)
        self._summary_panel = ProviderSummaryPanel(self)

        content_layout.addWidget(self._list_panel)
        content_layout.addWidget(self._status_panel)
        content_layout.addWidget(self._summary_panel)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def _connect_signals(self):
        if self._list_panel:
            self._list_panel.provider_selected.connect(self._on_provider_selected)
            self._list_panel.refresh_requested.connect(self._defer_load)
        if self._status_panel:
            pass  # Keine Signale nötig

    def _defer_load(self) -> None:
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._load_providers())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_load)

    async def _load_providers(self) -> None:
        if not self._list_panel or not self._status_panel:
            return
        self._list_panel.set_loading("Lade Provider…")
        try:
            from app.services.provider_service import get_provider_service
            result = await get_provider_service().get_provider_status()
            info = result.data if result.success and result.data else {}
            self._ollama_info = info

            online = info.get("online", False)
            version = info.get("version")
            model_count = info.get("model_count", 0)
            base_url = info.get("base_url", "http://localhost:11434")

            self._status_panel.set_status(online, version, model_count)

            providers = [
                {
                    "name": "Ollama",
                    "type": "Lokal",
                    "endpoint": base_url,
                    "status": "Online" if online else "Offline",
                },
            ]
            self._list_panel.set_providers(providers)

            if not self._selected_provider:
                self._on_provider_selected("Ollama")
        except Exception as e:
            self._list_panel.set_error(f"Fehler: {e!s}")
            self._status_panel.set_status(False, None, 0)
            self._on_provider_selected("")

    def _on_provider_selected(self, provider_name: str) -> None:
        self._selected_provider = provider_name or None
        info = self._ollama_info or {}
        if self._summary_panel:
            if provider_name == "Ollama":
                online = info.get("online", False)
                base_url = info.get("base_url", "http://localhost:11434")
                model_count = info.get("model_count", 0)
                usage_txt = ""
                try:
                    from app.services.model_usage_gui_service import get_model_usage_gui_service

                    s = get_model_usage_gui_service().provider_token_summary("local")
                    if s.get("db_error"):
                        usage_txt = f"Token-Ledger: {s['db_error']}"
                    else:
                        usage_txt = (
                            f"Erfasste Tokens (Ledger, Endpoint local): {int(s.get('total_tokens') or 0)} "
                            f"über {len(s.get('models') or [])} Modell-Einträge in der Aggregation."
                        )
                except Exception:
                    pass
                self._summary_panel.set_provider(
                    name="Ollama",
                    endpoint=base_url,
                    status="Online" if online else "Offline",
                    model_count=model_count,
                    usage_summary=usage_txt,
                )
            else:
                self._summary_panel.set_provider("—", "—", "—", 0, usage_summary="")
        self._refresh_inspector()

    def _refresh_inspector(self, content_token: int | None = None) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.provider_inspector import ProviderInspector
        info = self._ollama_info or {}
        if self._selected_provider == "Ollama":
            online = info.get("online", False)
            base_url = info.get("base_url", "http://localhost:11434")
            self._inspector_host.set_content(
                ProviderInspector(
                    provider="Ollama",
                    endpoint=base_url,
                    availability="Online" if online else "Offline",
                    error_status="—" if online else "Ollama nicht erreichbar",
                ),
                content_token=content_token,
            )
        else:
            self._inspector_host.set_content(
                ProviderInspector(
                    provider="(keine Auswahl)",
                    endpoint="—",
                    availability="—",
                    error_status="—",
                ),
                content_token=content_token,
            )

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Provider-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        self._refresh_inspector(content_token=content_token)
