"""
CommandPaletteDialog – Overlay-Dialog für schnelle Aktionen.

VSCode-inspiriert: Suchfeld, gefilterte Liste, Tastatursteuerung.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QWidget,
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QKeyEvent

from app.gui.commands.model import Command
from app.gui.commands.registry import CommandRegistry
from app.gui.icons import IconManager


class CommandPaletteDialog(QDialog):
    """
    Command Palette – Overlay mit Suchfeld und Action-Liste.

    Öffnet sich zentriert im Parent. Filtert bei Eingabe.
    Enter führt ausgewählten Command aus.
    """

    command_executed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("commandPaletteDialog")
        self.setWindowTitle("Befehl ausführen")
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._setup_ui()
        self._apply_theme_styles()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container mit Schatten
        container = QFrame()
        container.setObjectName("commandPaletteContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)

        # Suchfeld
        self._search = QLineEdit()
        self._search.setObjectName("commandPaletteSearch")
        self._search.setPlaceholderText("Befehl eingeben...")
        self._search.textChanged.connect(self._on_search_changed)
        self._search.returnPressed.connect(self._execute_selected)
        self._search.installEventFilter(self)
        container_layout.addWidget(self._search)

        # Liste
        self._list = QListWidget()
        self._list.setObjectName("commandPaletteList")
        self._list.setMinimumHeight(200)
        self._list.setMaximumHeight(320)
        self._list.itemDoubleClicked.connect(lambda _: self._execute_selected())
        self._list.currentRowChanged.connect(self._on_selection_changed)
        self._list.installEventFilter(self)
        container_layout.addWidget(self._list)

        layout.addWidget(container)

        # D38: Explicit tab order – Search → List (Tab), List → Search (Shift+Tab)
        self._search.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        QWidget.setTabOrder(self._search, self._list)

        self._populate_list("")
        self._search.setFocus()

    def _apply_theme_styles(self):
        """Wendet Theme-Styles an (via objectName)."""
        try:
            from app.gui.themes import get_theme_manager
            tokens = get_theme_manager().get_tokens()
            bg = tokens.get("color_bg_surface", "#ffffff")
            border = tokens.get("color_border", "#e2e8f0")
            text = tokens.get("color_text", "#1f2937")
            self.setStyleSheet(f"""
                #commandPaletteDialog {{
                    background: transparent;
                }}
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

    def _populate_list(self, query: str) -> None:
        """Füllt die Liste mit gefilterten Commands."""
        self._list.clear()
        commands = CommandRegistry.search(query)
        for cmd in commands:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, cmd.id)
            # Icon + Titel + Beschreibung
            icon = IconManager.get(cmd.icon, size=18) if cmd.icon else None
            if icon and not icon.isNull():
                item.setIcon(icon)
            item.setText(cmd.title)
            if cmd.description:
                item.setToolTip(cmd.description)
            self._list.addItem(item)
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _on_search_changed(self, text: str) -> None:
        """Filtert die Liste bei Eingabe."""
        self._populate_list(text)

    def _on_selection_changed(self, row: int) -> None:
        """Reagiert auf Auswahländerung."""
        pass

    def _execute_selected(self) -> None:
        """Führt den ausgewählten Command aus."""
        item = self._list.currentItem()
        if not item:
            return
        cmd_id = item.data(Qt.ItemDataRole.UserRole)
        if cmd_id:
            CommandRegistry.execute(cmd_id)
            self.command_executed.emit(cmd_id)
            self.accept()

    def eventFilter(self, obj, event) -> bool:
        """Pfeiltasten: Von Search zu List und zurück."""
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
        """Tastatursteuerung: Escape schließt."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    def showEvent(self, event) -> None:
        """Zentriert im Parent und fokussiert Suchfeld."""
        super().showEvent(event)
        if self.parent():
            geo = self.parent().geometry()
            self.setFixedWidth(min(520, geo.width() - 48))
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + (geo.height() - self.height()) // 4
            self.move(x, y)
        self._search.setFocus()
        self._search.clear()
        self._populate_list("")
