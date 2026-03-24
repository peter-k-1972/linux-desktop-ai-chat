"""
ModelSettingsPanel – Modell-Einstellungen als Studio-Panel.
Sauberes Formular mit Sektionen: Modellzuweisung, Routing, Rollen, Provider, Erweitert.

Hauptpfad: Presenter → SettingsOperationsPort → Adapter.
Legacy: ohne ``model_routing_port`` — Persistenz nur über ``ServiceSettingsAdapter`` (kein direktes ``save()`` auf ``self.settings``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QFormLayout,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtGui import QFont

from app.core.models.roles import ModelRole, get_role_display_name, all_roles, get_default_model_for_role
from app.gui.domains.settings.settings_model_routing_sink import SettingsModelRoutingSink
from app.gui.shared.panel_constants import _PROMPTS_PANEL_FIXED_WIDTH
from app.resources.styles import get_theme_colors
from app.ui_application.presenters.settings_model_routing_presenter import SettingsModelRoutingPresenter
from app.ui_contracts.workspaces.settings_model_routing import (
    ApplyModelRoutingStudioPatchCommand,
    LoadModelRoutingStudioCommand,
    ModelRoutingStudioWritePatch,
)

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


def _section_title(text: str, colors: dict) -> str:
    return f"""
        color: {colors['fg']};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    """


def _card_style(colors: dict) -> str:
    return f"""
        background-color: {colors.get('surface', colors.get('fg', '#3d3d3d'))};
        border-radius: 12px;
        padding: 16px;
        border: 1px solid {colors.get('border', colors.get('top_bar_border', '#505050'))};
    """


class SectionCard(QFrame):
    """Karten-Sektion mit Überschrift."""

    def __init__(self, title: str, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setObjectName("sectionCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        layout.addWidget(self.content)

        self._apply_theme()

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        surface = "#3d3d3d" if self.theme == "dark" else "#ffffff"
        border = colors.get("top_bar_border", "#505050" if self.theme == "dark" else "#cccccc")
        fg = colors.get("fg", "#e8e8e8" if self.theme == "dark" else "#1a1a1a")
        self.setStyleSheet(f"""
            QFrame#sectionCard {{
                background-color: {surface};
                border-radius: 12px;
                border: 1px solid {border};
            }}
            QLabel#sectionTitle {{
                color: {fg};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
        """)

    def add_row(self, label: str, widget: QWidget):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(90)
        lbl.setStyleSheet("color: inherit;")
        row.addWidget(lbl)
        row.addWidget(widget, 1)
        self.content_layout.addLayout(row)

    def add_widget(self, widget: QWidget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()


class ModelSettingsPanel(QWidget):
    """
    Modell-Einstellungen als Studio-Panel.
    Bindet an AppSettings und ModelOrchestrator.
    """

    settings_changed = Signal()

    def __init__(
        self,
        settings,
        orchestrator=None,
        theme: str = "dark",
        parent=None,
        *,
        model_routing_port: SettingsOperationsPort | None = None,
        usage_hint_port=None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.orchestrator = orchestrator
        self.theme = theme
        self._model_list: list = []
        self._model_routing_port = model_routing_port
        self._routing_sink: SettingsModelRoutingSink | None = None
        self._routing_presenter: SettingsModelRoutingPresenter | None = None
        self._usage_hint_port = usage_hint_port
        self._usage_hint_presenter = None
        self.init_ui()
        if model_routing_port is not None:
            self._routing_sink = SettingsModelRoutingSink(
                self.assistant_combo,
                self.auto_routing_check,
                self.cloud_check,
                self.cloud_via_local_check,
                self.web_search_check,
                self.overkill_check,
                self.default_role_combo,
                self.temp_spin,
                self.top_p_spin,
                self.max_tokens_spin,
                self.timeout_spin,
                self.retry_check,
                self.stream_check,
            )
            self._routing_presenter = SettingsModelRoutingPresenter(self._routing_sink, model_routing_port)
            self._routing_presenter.handle_command(LoadModelRoutingStudioCommand())
        else:
            self._load_routing_legacy()

    def init_ui(self):
        self.setObjectName("modelSettingsPanel")
        w = _PROMPTS_PANEL_FIXED_WIDTH()
        self.setMinimumWidth(w)
        self.setMaximumWidth(w)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(12, 12, 12, 24)
        main_layout.setSpacing(12)

        col_left = QVBoxLayout()
        col_left.setSpacing(16)
        col_right = QVBoxLayout()
        col_right.setSpacing(16)

        # A. Grundlegende Modellzuweisung
        card1 = SectionCard("Modellzuweisung", self.theme)
        self.assistant_combo = QComboBox()
        self.assistant_combo.setMinimumWidth(180)
        self.thinking_combo = QComboBox()
        self.vision_combo = QComboBox()
        self.code_combo = QComboBox()
        self.overkill_combo = QComboBox()
        card1.add_row("Assistant", self.assistant_combo)
        card1.add_row("Thinking", self.thinking_combo)
        card1.add_row("Vision (opt.)", self.vision_combo)
        card1.add_row("Code (opt.)", self.code_combo)
        card1.add_row("Overkill (opt.)", self.overkill_combo)
        col_left.addWidget(card1)

        # B. Routing / Verhalten
        card2 = SectionCard("Routing & Verhalten", self.theme)
        self.auto_routing_check = QCheckBox("Auto-Routing aktiv")
        self.auto_routing_check.setToolTip("Modell nach Prompt-Inhalt wählen")
        self.cloud_check = QCheckBox("Cloud-Eskalation aktiv")
        self.cloud_via_local_check = QCheckBox("Cloud über lokales Ollama")
        self.cloud_via_local_check.setToolTip(
            "Alternative zum API-Key: Cloud-Modelle über localhost.\n"
            "Voraussetzung: 1) ollama signin  2) ollama pull <modell>:cloud (z.B. ollama pull glm-5:cloud)"
        )
        self.web_search_check = QCheckBox("Websuche aktiv")
        self.overkill_check = QCheckBox("Eskalationsmodus aktiv")
        self.default_role_combo = QComboBox()
        for role in all_roles():
            self.default_role_combo.addItem(get_role_display_name(role), role)
        card2.add_widget(self.auto_routing_check)
        card2.add_widget(self.cloud_check)
        card2.add_widget(self.cloud_via_local_check)
        card2.add_widget(self.web_search_check)
        card2.add_widget(self.overkill_check)
        card2.add_row("Standardrolle", self.default_role_combo)
        col_right.addWidget(card2)

        # C. Rollenzuweisung (kompakt)
        card3 = SectionCard("Rollen → Modell", self.theme)
        self.role_combos: dict = {}
        for role in all_roles():
            combo = QComboBox()
            combo.setMinimumWidth(180)
            combo.setProperty("role", role)
            self.role_combos[role] = combo
            card3.add_row(get_role_display_name(role), combo)
        col_left.addWidget(card3)

        # D. Provider-Info (vorbereitet)
        card4 = SectionCard("Provider & Status", self.theme)
        self.provider_status_label = QLabel("Lokal / Cloud")
        self.provider_status_label.setWordWrap(True)
        self.api_key_label = QLabel("API-Key: —")
        self.model_available_label = QLabel("Modell: —")
        self.last_error_label = QLabel("Letzter Fehler: —")
        self.last_error_label.setWordWrap(True)
        self.last_error_label.setStyleSheet("color: #a05050; font-size: 11px;")
        card4.add_widget(self.provider_status_label)
        card4.add_widget(self.api_key_label)
        card4.add_widget(self.model_available_label)
        card4.add_widget(self.last_error_label)
        self._usage_sidebar_hint = QLabel("")
        self._usage_sidebar_hint.setWordWrap(True)
        self._usage_sidebar_hint.setStyleSheet("color: #64748b; font-size: 11px;")
        card4.add_widget(self._usage_sidebar_hint)
        if self._usage_hint_port is not None:
            from app.gui.domains.settings.model_usage_sidebar_sink import ModelUsageSidebarSink
            from app.ui_application.presenters.model_usage_sidebar_presenter import (
                ModelUsageSidebarHintPresenter,
            )

            _sink = ModelUsageSidebarSink(self._usage_sidebar_hint)
            self._usage_hint_presenter = ModelUsageSidebarHintPresenter(_sink, self._usage_hint_port)
        col_right.addWidget(card4)

        # E. Erweiterte Einstellungen
        card5 = SectionCard("Erweitert", self.theme)
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.05)
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(0, 32768)
        self.max_tokens_spin.setToolTip(
            "Max. Tokens pro Antwort. Bei Thinking-Modellen (z.B. GPT-OSS) zählen "
            "Thinking-Tokens mit – höhere Werte (4096+) empfehlenswert."
        )
        self.stream_check = QCheckBox("Streaming aktiv")
        self.stream_check.setToolTip("Antworten während der Generierung anzeigen. Deaktivieren bei Darstellungsproblemen.")
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(0, 300)
        self.timeout_spin.setSpecialValueText("—")
        self.retry_check = QCheckBox("Retry / Fallback")
        card5.add_row("Temperatur", self.temp_spin)
        card5.add_row("Top-p", self.top_p_spin)
        card5.add_row("Max Tokens", self.max_tokens_spin)
        card5.add_row("Timeout", self.timeout_spin)
        card5.add_widget(self.stream_check)
        card5.add_widget(self.retry_check)
        col_left.addWidget(card5)

        col_left.addStretch()
        col_right.addStretch()
        main_layout.addLayout(col_left, 1)
        main_layout.addLayout(col_right, 1)
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        self._connect_signals()
        self._refresh_usage_sidebar_hint()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._refresh_usage_sidebar_hint()

    def _refresh_usage_sidebar_hint(self) -> None:
        if self._usage_hint_presenter is not None:
            from app.ui_contracts.workspaces.model_usage_sidebar import (
                RefreshModelUsageSidebarHintCommand,
            )

            self._usage_hint_presenter.handle_command(RefreshModelUsageSidebarHintCommand())
            return
        try:
            from app.ui_application.adapters.service_model_usage_gui_adapter import (
                ServiceModelUsageGuiAdapter,
            )

            self._usage_sidebar_hint.setText(ServiceModelUsageGuiAdapter().quick_sidebar_hint())
        except Exception:
            self._usage_sidebar_hint.setText("")

    def _use_model_routing_path(self) -> bool:
        return self._routing_presenter is not None and self._routing_sink is not None

    @staticmethod
    def _legacy_routing_adapter():
        from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter

        return ServiceSettingsAdapter()

    def _load_routing_legacy(self) -> None:
        try:
            st = self._legacy_routing_adapter().load_model_routing_studio_state()
            SettingsModelRoutingSink(
                self.assistant_combo,
                self.auto_routing_check,
                self.cloud_check,
                self.cloud_via_local_check,
                self.web_search_check,
                self.overkill_check,
                self.default_role_combo,
                self.temp_spin,
                self.top_p_spin,
                self.max_tokens_spin,
                self.timeout_spin,
                self.retry_check,
                self.stream_check,
            ).apply_full_state(st)
        except Exception:
            pass

    def _connect_signals(self):
        self.assistant_combo.currentTextChanged.connect(self._on_model_changed)
        self.auto_routing_check.stateChanged.connect(self._on_routing_changed)
        self.cloud_check.stateChanged.connect(self._on_cloud_changed)
        self.cloud_via_local_check.stateChanged.connect(self._on_cloud_via_local_changed)
        self.web_search_check.stateChanged.connect(self._on_web_search_changed)
        self.overkill_check.stateChanged.connect(self._on_overkill_changed)
        self.default_role_combo.currentIndexChanged.connect(self._on_default_role_changed)
        self.temp_spin.valueChanged.connect(self._on_temp_changed)
        self.top_p_spin.valueChanged.connect(self._on_top_p_changed)
        self.max_tokens_spin.valueChanged.connect(self._on_max_tokens_changed)
        self.timeout_spin.valueChanged.connect(self._on_timeout_changed)
        self.retry_check.stateChanged.connect(self._on_retry_changed)
        self.stream_check.stateChanged.connect(self._on_stream_changed)
        for role, combo in self.role_combos.items():
            combo.currentTextChanged.connect(lambda t, r=role: self._on_role_model_changed(r, t))

    def _on_model_changed(self, _text: str):
        from PySide6.QtCore import Qt

        model_id = self.assistant_combo.currentData(Qt.ItemDataRole.UserRole)
        if not model_id or model_id == "Keine Modelle":
            return
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(ModelRoutingStudioWritePatch(model=model_id)),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(model=model_id),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_routing_changed(self, _):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(auto_routing=self.auto_routing_check.isChecked()),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(auto_routing=self.auto_routing_check.isChecked()),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_cloud_changed(self, _):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(cloud_escalation=self.cloud_check.isChecked()),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(cloud_escalation=self.cloud_check.isChecked()),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_cloud_via_local_changed(self, _):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(cloud_via_local=self.cloud_via_local_check.isChecked()),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(cloud_via_local=self.cloud_via_local_check.isChecked()),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_web_search_changed(self, _):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(web_search=self.web_search_check.isChecked()),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(web_search=self.web_search_check.isChecked()),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_overkill_changed(self, _):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(overkill_mode=self.overkill_check.isChecked()),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(overkill_mode=self.overkill_check.isChecked()),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_default_role_changed(self, _):
        role = self.default_role_combo.currentData()
        if not role:
            return
        val = role.value if hasattr(role, "value") else str(role)
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(ModelRoutingStudioWritePatch(default_role=val)),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(default_role=val),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_temp_changed(self, v: float):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(ModelRoutingStudioWritePatch(temperature=v)),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(temperature=v),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_top_p_changed(self, v: float):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(ModelRoutingStudioWritePatch(top_p=v)),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(top_p=v),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_max_tokens_changed(self, v: int):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(ModelRoutingStudioWritePatch(max_tokens=v)),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(max_tokens=v),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_timeout_changed(self, v: int):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(llm_timeout_seconds=v),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(llm_timeout_seconds=v),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_retry_changed(self, _):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(retry_without_thinking=self.retry_check.isChecked()),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(
                        retry_without_thinking=self.retry_check.isChecked(),
                    ),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def _on_role_model_changed(self, role: ModelRole, model_id: str):
        # Vorbereitet: Rollen-Mapping in Settings/Registry persistieren
        # Aktuell nutzt die App das Registry-Default-Mapping
        self.settings_changed.emit()

    def _on_stream_changed(self, _):
        if self._use_model_routing_path():
            assert self._routing_presenter is not None
            self._routing_presenter.handle_command(
                ApplyModelRoutingStudioPatchCommand(
                    ModelRoutingStudioWritePatch(chat_streaming_enabled=self.stream_check.isChecked()),
                ),
            )
        else:
            try:
                self._legacy_routing_adapter().persist_model_routing_studio(
                    ModelRoutingStudioWritePatch(chat_streaming_enabled=self.stream_check.isChecked()),
                )
            except Exception:
                pass
        self.settings_changed.emit()

    def set_model_list(self, model_entries: list):
        """Modelle für alle Combos setzen. Erwartet [{"id", "display", "cloud"}, ...]."""
        self._model_list = model_entries
        for combo in [
            self.assistant_combo,
            self.thinking_combo,
            self.vision_combo,
            self.code_combo,
            self.overkill_combo,
        ] + list(self.role_combos.values()):
            combo.blockSignals(True)
            combo.clear()
            if self._model_list:
                for entry in self._model_list:
                    combo.addItem(entry["display"], entry["id"])
            else:
                combo.addItem("Keine Modelle")
            combo.blockSignals(False)
        self._sync_combos_from_settings()
        self._refresh_usage_sidebar_hint()

    def _find_model_index(self, combo, model_id: str) -> int:
        """Findet den Combo-Index für eine Modell-ID."""
        from PySide6.QtCore import Qt
        for i in range(combo.count()):
            if combo.itemData(i, Qt.ItemDataRole.UserRole) == model_id:
                return i
            if combo.itemText(i) == model_id:
                return i
        return -1

    def _sync_combos_from_settings(self):
        """Synchronisiert Combos mit aktueller Settings."""
        from PySide6.QtCore import Qt
        model = getattr(self.settings, "model", "")
        if model:
            idx = self._find_model_index(self.assistant_combo, model)
            if idx >= 0:
                self.assistant_combo.setCurrentIndex(idx)
        for role, combo in self.role_combos.items():
            default_id = get_default_model_for_role(role)
            if default_id:
                idx = self._find_model_index(combo, default_id)
                if idx >= 0:
                    combo.setCurrentIndex(idx)

    def update_provider_status(self, local_ok: bool, cloud_ok: bool, api_key: bool):
        """Provider-Status aktualisieren."""
        parts = []
        if local_ok:
            parts.append("Lokal ✓")
        else:
            parts.append("Lokal ✗")
        if cloud_ok:
            parts.append("Cloud ✓")
        else:
            parts.append("Cloud ✗")
        self.provider_status_label.setText(" / ".join(parts))
        self.api_key_label.setText("API-Key: ✓" if api_key else "API-Key: —")

    def refresh_theme(self, theme: str):
        self.theme = theme
        for child in self.findChildren(SectionCard):
            child.refresh_theme(theme)
