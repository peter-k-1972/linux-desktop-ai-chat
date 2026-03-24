"""
ThemeSelectionPanel – Theme-Auswahl mit Liste.

Hauptpfad: Presenter → SettingsOperationsPort → Adapter; ThemeManager nur im Sink.
Legacy: direkter ThemeManager + Persistenz im Panel (ohne injizierten Port).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.gui.domains.settings.settings_appearance_sink import SettingsAppearanceSink
from app.gui.themes import get_theme_manager
from app.gui.themes.theme_installer import ThemeInstallError, ThemeInstaller
from app.ui_application.presenters.settings_appearance_presenter import SettingsAppearancePresenter
from app.ui_contracts.workspaces.settings_appearance import LoadAppearanceSettingsCommand, SelectThemeCommand

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class ThemeSelectionPanel(QFrame):
    """Theme-Auswahl: Liste verfügbarer Themes, Name, Beschreibung."""

    theme_selected = Signal(str)

    def __init__(self, parent=None, *, appearance_port: SettingsOperationsPort | None = None):
        self._appearance_port = appearance_port
        self._sink: SettingsAppearanceSink | None = None
        self._presenter: SettingsAppearancePresenter | None = None
        super().__init__(parent)
        self.setObjectName("themeSelectionPanel")
        self._setup_ui()
        if appearance_port is not None:
            self._sink = SettingsAppearanceSink(
                self._list,
                self._error_label,
                self.THEME_DESCRIPTIONS,
            )
            self._presenter = SettingsAppearancePresenter(
                self._sink,
                appearance_port,
                on_theme_choice_committed=lambda tid: self.theme_selected.emit(tid),
            )
            self._presenter.handle_command(LoadAppearanceSettingsCommand())
        else:
            self._populate_themes_legacy()
        self._connect_signals()

    THEME_DESCRIPTIONS: dict[str, str] = {
        "light_default": "Helles Standard-Theme. Klar und lesbar.",
        "dark_default": "Dunkles Theme. Schonend für die Augen.",
        "workbench": "Modernes Workbench-Chrome (IDE-ähnlich); nutzt dieselbe QSS-Pipeline inkl. workbench.qss.",
    }

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Theme Selection")
        title.setObjectName("settingsPanelTitle")
        layout.addWidget(title)

        desc = QLabel(
            "Wähle ein Theme für die Anwendung. Die Änderung wird sofort angewendet."
        )
        desc.setObjectName("settingsPanelDescription")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._btn_import_theme = QPushButton("Theme importieren")
        self._btn_import_theme.setObjectName("importThemeButton")
        self._btn_import_theme.clicked.connect(self._on_import_theme)
        layout.addWidget(self._btn_import_theme)

        self._list = QListWidget()
        self._list.setObjectName("themeList")
        self._list.setSpacing(4)
        self._list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list, 1)

        self._error_label = QLabel("")
        self._error_label.setObjectName("themeSelectionError")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

    def _use_port_path(self) -> bool:
        return self._appearance_port is not None and self._presenter is not None

    def _populate_themes_legacy(self) -> None:
        """Füllt die Liste aus dem ThemeManager (Legacy ohne Port)."""
        manager = get_theme_manager()
        themes = manager.list_themes()
        current = manager.get_current_id()

        self._list.clear()
        for theme_id, theme_name in themes:
            item = QListWidgetItem(f"  {theme_name}")
            item.setData(Qt.ItemDataRole.UserRole, theme_id)
            if theme_id == current:
                item.setText(f"  {theme_name}  ✓")
            tdesc = self.THEME_DESCRIPTIONS.get(theme_id)
            if tdesc:
                item.setToolTip(tdesc)
            self._list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        theme_id = item.data(Qt.ItemDataRole.UserRole)
        if not theme_id:
            return
        if self._use_port_path():
            assert self._presenter is not None
            self._presenter.handle_command(SelectThemeCommand(str(theme_id)))
            return
        manager = get_theme_manager()
        if manager.set_theme(theme_id):
            self._persist_theme_legacy(theme_id)
            self.theme_selected.emit(theme_id)
            self._refresh_list_legacy()

    def _persist_theme_legacy(self, theme_id: str) -> None:
        """Persistiert Theme für Neustart (Legacy ohne injizierten Port — nur Adapter, kein get_infrastructure im Widget)."""
        try:
            from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter
            from app.ui_contracts.workspaces.settings_appearance import SettingsAppearancePortError

            ServiceSettingsAdapter().persist_theme_choice(theme_id)
        except SettingsAppearancePortError:
            pass
        except Exception:
            pass

    def _refresh_list_legacy(self) -> None:
        """Aktualisiert die Liste (z.B. nach Theme-Wechsel), Legacy-Pfad."""
        try:
            self._populate_themes_legacy()
        except RuntimeError:
            pass

    def _on_import_theme(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Theme-Datei wählen",
            "",
            "Theme JSON (*.json);;Alle Dateien (*)",
        )
        if not path:
            return
        try:
            ThemeInstaller().install_theme(path)
            get_theme_manager().reload_themes()
            if self._use_port_path():
                assert self._presenter is not None
                self._presenter.handle_command(LoadAppearanceSettingsCommand())
            else:
                self._populate_themes_legacy()
        except ThemeInstallError as exc:
            QMessageBox.warning(self, "Theme-Import", str(exc))

    def _connect_signals(self) -> None:
        get_theme_manager().theme_changed.connect(self._on_theme_changed_unified)

    def _on_theme_changed_unified(self, _theme_id: str) -> None:
        try:
            if self._use_port_path():
                assert self._presenter is not None
                self._presenter.handle_command(LoadAppearanceSettingsCommand())
            else:
                self._refresh_list_legacy()
        except RuntimeError:
            pass
