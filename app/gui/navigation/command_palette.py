"""
Command Palette – universal navigation (VSCode-style).

Search and navigate: Workspaces, Features, Help, Settings, Commands.
Shortcut: Ctrl+K
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QLabel,
)
from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QKeyEvent

from app.core.command_registry import CommandRegistry, PaletteCommand, CATEGORY_ORDER
from app.gui.icons import IconManager


class CommandPalette(QDialog):
    """
    Command Palette – overlay with search and results.

    - Fuzzy search
    - Keyboard navigation (↑/↓, Enter, Escape)
    - Enter to execute
    - Escape to close
    """

    command_executed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("commandPalette")
        self.setWindowTitle("Befehl ausführen")
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QFrame()
        container.setObjectName("commandPaletteContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)

        # Search input
        self._search = QLineEdit()
        self._search.setObjectName("commandPaletteSearch")
        self._search.setPlaceholderText("Befehl suchen... (z.B. Chat, Help, Settings)")
        self._search.textChanged.connect(self._on_search_changed)
        self._search.returnPressed.connect(self._execute_selected)
        self._search.installEventFilter(self)
        container_layout.addWidget(self._search)

        # Results list
        self._list = QListWidget()
        self._list.setObjectName("commandPaletteList")
        self._list.setMinimumHeight(240)
        self._list.setMaximumHeight(360)
        self._list.itemDoubleClicked.connect(lambda _: self._execute_selected())
        self._list.installEventFilter(self)
        container_layout.addWidget(self._list)

        layout.addWidget(container)

        self._search.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._populate("")
        self._search.setFocus()

    def _apply_theme(self) -> None:
        try:
            from app.gui.themes import get_theme_manager
            tokens = get_theme_manager().get_tokens()
            bg = tokens.get("color_bg_surface", "#ffffff")
            border = tokens.get("color_border", "#e2e8f0")
            text = tokens.get("color_text", "#1f2937")
            self.setStyleSheet(f"""
                #commandPalette {{ background: transparent; }}
                #commandPaletteContainer {{
                    background: {bg};
                    border: 1px solid {border};
                    border-radius: 12px;
                }}
                #commandPaletteSearch {{
                    background: {tokens.get('color_bg_input', '#ffffff')};
                    border: 1px solid {border};
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 14px;
                    color: {text};
                }}
                #commandPaletteList {{
                    background: transparent;
                    border: none;
                    outline: none;
                }}
                #commandPaletteList::item {{
                    padding: 10px 12px;
                    border-radius: 6px;
                }}
                #commandPaletteList::item:selected {{
                    background: {tokens.get('color_bg_selected', '#dbeafe')};
                }}
                #commandPaletteList::item:hover {{
                    background: {tokens.get('color_bg_hover', '#e2e8f0')};
                }}
            """)
        except Exception:
            pass

    def _populate(self, query: str) -> None:
        """Populate list with ranked search results."""
        self._list.clear()
        results = CommandRegistry.search(query)

        # Group by category
        by_cat: dict[str, list[PaletteCommand]] = {}
        for cmd, _ in results:
            cat = cmd.category or "Command"
            by_cat.setdefault(cat, []).append(cmd)

        for cat in CATEGORY_ORDER:
            if cat not in by_cat:
                continue
            for cmd in by_cat[cat]:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, cmd.id)
                if cmd.icon:
                    icon = IconManager.get(cmd.icon, size=18)
                    if not icon.isNull():
                        item.setIcon(icon)
                item.setText(cmd.title)
                if cmd.description:
                    item.setToolTip(cmd.description)
                item.setData(Qt.ItemDataRole.UserRole + 1, cmd.category)
                self._list.addItem(item)

        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _on_search_changed(self, text: str) -> None:
        self._populate(text)

    def _execute_selected(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        cmd_id = item.data(Qt.ItemDataRole.UserRole)
        if cmd_id:
            CommandRegistry.execute(cmd_id)
            try:
                self.command_executed.emit(cmd_id)
            except (AttributeError, RuntimeError):
                pass
            self.accept()

    def eventFilter(self, obj, event) -> bool:
        """Arrow keys: Search <-> List navigation."""
        if event is None or obj is None:
            return False
        try:
            if event.type() == QEvent.Type.KeyPress:
                if obj == self._search:
                    if event.key() == Qt.Key.Key_Down and self._list.count() > 0:
                        self._list.setFocus()
                        self._list.setCurrentRow(0)
                        return True
                elif obj == self._list:
                    if event.key() == Qt.Key.Key_Up and self._list.currentRow() == 0:
                        self._search.setFocus()
                        return True
        except (AttributeError, RuntimeError):
            pass
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self.parent():
            geo = self.parent().geometry()
            self.setFixedWidth(min(560, geo.width() - 48))
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + (geo.height() - self.height()) // 6
            self.move(x, y)
        self._search.setFocus()
        self._search.clear()
        self._populate("")
