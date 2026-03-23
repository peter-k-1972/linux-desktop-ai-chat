"""
ThemeSelectionPanel – Theme-Auswahl mit Liste.

Nutzt ThemeManager und ThemeRegistry.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, Signal

from app.gui.themes import get_theme_manager
from app.gui.themes.theme_id_utils import theme_id_to_legacy_light_dark


class ThemeSelectionPanel(QFrame):
    """Theme-Auswahl: Liste verfügbarer Themes, Name, Beschreibung."""

    theme_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("themeSelectionPanel")
        self._setup_ui()
        self._connect_signals()

    THEME_DESCRIPTIONS: dict[str, str] = {
        "light_default": "Helles Standard-Theme. Klar und lesbar.",
        "dark_default": "Dunkles Theme. Schonend für die Augen.",
        "workbench": "Modernes Workbench-Chrome (IDE-ähnlich); nutzt dieselbe QSS-Pipeline inkl. workbench.qss.",
    }

    def _setup_ui(self):
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

        self._list = QListWidget()
        self._list.setObjectName("themeList")
        self._list.setSpacing(4)
        self._list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list, 1)

        self._populate_themes()

    def _populate_themes(self) -> None:
        """Füllt die Liste aus der ThemeRegistry."""
        manager = get_theme_manager()
        themes = manager.list_themes()
        current = manager.get_current_id()

        self._list.clear()
        for theme_id, theme_name in themes:
            item = QListWidgetItem(f"  {theme_name}")
            item.setData(Qt.ItemDataRole.UserRole, theme_id)
            if theme_id == current:
                item.setText(f"  {theme_name}  ✓")
            desc = self.THEME_DESCRIPTIONS.get(theme_id)
            if desc:
                item.setToolTip(desc)
            self._list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        theme_id = item.data(Qt.ItemDataRole.UserRole)
        if theme_id:
            manager = get_theme_manager()
            if manager.set_theme(theme_id):
                self._persist_theme(theme_id)
                self.theme_selected.emit(theme_id)
                self._refresh_list()

    def _persist_theme(self, theme_id: str) -> None:
        """Persistiert Theme in AppSettings für Neustart."""
        try:
            from app.services.infrastructure import get_infrastructure
            settings = get_infrastructure().settings
            settings.theme_id = theme_id
            settings.theme = theme_id_to_legacy_light_dark(theme_id)
            settings.save()
        except Exception:
            pass

    def _refresh_list(self) -> None:
        """Aktualisiert die Liste (z.B. nach Theme-Wechsel)."""
        try:
            self._populate_themes()
        except RuntimeError:
            pass  # Widget bereits zerstört (z.B. nach Screen-Wechsel)

    def _connect_signals(self) -> None:
        """Verbindet ThemeManager theme_changed mit Refresh."""
        get_theme_manager().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _theme_id: str) -> None:
        """Callback bei Theme-Wechsel. Robust gegen zerstörtes Widget."""
        try:
            self._refresh_list()
        except RuntimeError:
            pass
