"""
Modal command palette (VSCode-style) with search and keyboard-first navigation.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut, QShowEvent
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from app.gui.workbench.command_palette.command_context import WorkbenchCommandContext
from app.gui.workbench.command_palette.command_item import CommandDefinition
from app.gui.workbench.command_palette.command_registry import WorkbenchCommandRegistry


class CommandPaletteDialog(QDialog):
    def __init__(
        self,
        registry: WorkbenchCommandRegistry,
        context: WorkbenchCommandContext,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchCommandPalette")
        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.resize(600, 440)
        self._registry = registry
        self._context = context

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 16)
        root.setSpacing(14)

        title = QLabel("Run command")
        title.setObjectName("workbenchPaletteTitle")
        root.addWidget(title)

        self._hint = QLabel("Type to filter · ↑↓ in list · Enter to run · Esc to close")
        self._hint.setObjectName("workbenchPaletteHint")
        root.addWidget(self._hint)

        self._edit = QLineEdit(self)
        self._edit.setObjectName("workbenchPaletteSearch")
        self._edit.setPlaceholderText("Search commands…")
        self._edit.setClearButtonEnabled(True)
        root.addWidget(self._edit)

        self._list = QListWidget(self)
        self._list.setObjectName("workbenchPaletteList")
        self._list.setAlternatingRowColors(False)
        root.addWidget(self._list, 1)

        self._edit.textChanged.connect(self._refresh_list)
        self._list.itemActivated.connect(self._on_item_activated)
        self._list.itemDoubleClicked.connect(self._on_item_activated)

        ret = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        ret.activated.connect(self._run_current)
        ret2 = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        ret2.activated.connect(self._run_current)

        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self.reject)

        self._refresh_list()
        self._edit.setFocus()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        pw = self.parentWidget()
        if pw is not None:
            geo = self.frameGeometry()
            geo.moveCenter(pw.frameGeometry().center())
            self.move(geo.topLeft())

    def _refresh_list(self) -> None:
        self._list.clear()
        q = self._edit.text()
        for cmd in self._registry.filter_commands(q, self._context):
            item = QListWidgetItem(cmd.label)
            item.setToolTip(f"{cmd.category.value} · {cmd.id}\n{cmd.label}")
            item.setData(Qt.ItemDataRole.UserRole, cmd)
            self._list.addItem(item)
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _current_command(self) -> CommandDefinition | None:
        item = self._list.currentItem()
        if item is None:
            return None
        data = item.data(Qt.ItemDataRole.UserRole)
        return data if isinstance(data, CommandDefinition) else None

    def _run_current(self) -> None:
        cmd = self._current_command()
        if cmd is None and self._list.count() > 0:
            self._list.setCurrentRow(0)
            cmd = self._current_command()
        if cmd is None:
            return
        self._execute(cmd)

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, CommandDefinition):
            self._execute(data)

    def _execute(self, cmd: CommandDefinition) -> None:
        cmd.handler(self._context)
        self.accept()
