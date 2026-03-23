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
    QTabWidget,
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
from app.gui.domains.control_center.panels.model_quota_policy_panel import ModelQuotaPolicyPanel
from app.gui.domains.control_center.panels.local_assets_panel import LocalModelAssetsPanel


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
        self._catalog: List[Dict[str, Any]] = []
        self._selected_model: str | None = None
        self._tabs: QTabWidget | None = None
        self._setup_ui()
        self._connect_signals()
        QTimer.singleShot(0, self._defer_load)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("modelsWorkspaceTabs")

        overview = QWidget()
        content_layout = QVBoxLayout(overview)
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
        scroll.setWidget(overview)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._tabs.addTab(scroll, "Modelle & Verbrauch")
        self._tabs.addTab(ModelQuotaPolicyPanel(self), "Quota-Richtlinien")
        self._tabs.addTab(LocalModelAssetsPanel(self), "Lokale Daten")

        layout.addWidget(self._tabs)

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
            from app.services.infrastructure import get_infrastructure
            from app.services.model_service import get_model_service
            from app.services.unified_model_catalog_service import get_unified_model_catalog_service

            settings = get_infrastructure().settings
            ucat = get_unified_model_catalog_service()
            catalog = await ucat.build_catalog_for_chat(settings)
            self._catalog = catalog
            rows = ucat.to_management_rows(catalog)
            self._models = rows
            default = get_model_service().get_default_model()
            if rows:
                self._list_panel.set_models(rows)
                self._status_panel.set_status(len(rows), default)
                if rows and not self._selected_model:
                    sk = rows[0].get("selection_key") or rows[0].get("name", "")
                    if sk:
                        self._on_model_selected(sk)
            else:
                self._list_panel.set_empty("Keine Einträge (Ollama/Registry/Assets).")
                self._status_panel.set_status(0, default)
                self._on_model_selected("")
        except Exception as e:
            self._list_panel.set_error(f"Fehler: {e!s}")
            self._status_panel.set_status(0, "—")
            self._on_model_selected("")

    def _catalog_entry(self, selection_id: str) -> Dict[str, Any] | None:
        for r in self._catalog:
            if r.get("selection_id") == selection_id:
                return r
        return None

    def _on_model_selected(self, model_name: str) -> None:
        self._selected_model = model_name or None
        if self._action_panel:
            can_default = bool(self._selected_model) and not (
                self._selected_model or ""
            ).startswith("local-asset:")
            self._action_panel.set_current_model(self._selected_model if can_default else None)
        m = self._find_model(model_name)
        cent = self._catalog_entry(model_name) if model_name else None
        if self._summary_panel:
            if m:
                size = _format_size(m.get("size"))
                try:
                    from app.services.model_service import get_model_service
                    default = get_model_service().get_default_model()
                except Exception:
                    default = ""
                prov = m.get("provider_label") or "Ollama"
                self._summary_panel.set_model(
                    name=model_name,
                    provider=prov,
                    size=size,
                    is_default=(model_name == default and not str(model_name).startswith("local-asset:")),
                )
                try:
                    from app.services.infrastructure import get_infrastructure
                    from app.services.model_usage_gui_service import get_model_usage_gui_service

                    bundle_model_id = model_name
                    if str(model_name).startswith("local-asset:"):
                        bundle_model_id = ""
                    bundle = None
                    if bundle_model_id:
                        bundle = get_model_usage_gui_service().get_model_operational_bundle(
                            bundle_model_id, get_infrastructure().settings
                        )
                    self._summary_panel.set_operational_bundle(bundle)
                    extra_parts: List[str] = []
                    if cent:
                        if cent.get("has_local_asset"):
                            extra_parts.append("Lokale Gewichtsdatei im Inventar")
                        if cent.get("storage_root_name"):
                            extra_parts.append(f"Storage: {cent['storage_root_name']}")
                        if cent.get("path_hint"):
                            extra_parts.append(cent["path_hint"])
                        if cent.get("assignment_state") == "unassigned":
                            extra_parts.append("Keine Zuordnung zu einem Chat-Modell")
                        if cent.get("runtime_ready") is False and cent.get("chat_selectable") is False:
                            extra_parts.append("Nicht für Chat auswählbar (kein Ollama-Runtime)")
                        for k in ("usage_summary", "quota_summary", "usage_quality_note"):
                            v = (cent.get(k) or "").strip()
                            if v and v != "—":
                                extra_parts.append(v)
                    if extra_parts:
                        self._summary_panel.set_catalog_route_suffix(" · ".join(extra_parts))
                except Exception:
                    self._summary_panel.set_operational_bundle(None)
            else:
                self._summary_panel.set_model("—", "—", "—", False)
                self._summary_panel.set_operational_bundle(None)
        self._refresh_inspector()

    def _find_model(self, selection_id: str) -> Dict[str, Any] | None:
        for m in self._models:
            if m.get("selection_key") == selection_id:
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
        from app.services.infrastructure import get_infrastructure
        from app.services.model_usage_gui_service import get_model_usage_gui_service

        m = self._find_model(self._selected_model or "")
        cent = self._catalog_entry(self._selected_model or "")
        cat_ctx: str | None = None
        if cent:
            bits: List[str] = []
            d = (cent.get("display_detail") or "").strip()
            if d:
                bits.append(d)
            if (cent.get("asset_type") or "").strip():
                bits.append(f"Asset-Typ: {cent['asset_type']}")
            for k in ("usage_summary", "quota_summary", "usage_quality_note"):
                v = (cent.get(k) or "").strip()
                if v and v != "—":
                    bits.append(v)
            cat_ctx = "\n\n".join(bits) if bits else None
        bundle = None
        bid = self._selected_model or ""
        if bid and not bid.startswith("local-asset:"):
            try:
                bundle = get_model_usage_gui_service().get_model_operational_bundle(
                    bid, get_infrastructure().settings
                )
            except Exception:
                bundle = None
        if m:
            size = _format_size(m.get("size"))
            self._inspector_host.set_content(
                ModelInspector(
                    model_name=self._selected_model or "—",
                    status=m.get("status_label") or "Bereit",
                    size=size,
                    model_type="Chat / Completion",
                    operational_bundle=bundle,
                    catalog_context=cat_ctx or None,
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
                    operational_bundle=None,
                ),
                content_token=content_token,
            )

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Model-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        self._refresh_inspector(content_token=content_token)
