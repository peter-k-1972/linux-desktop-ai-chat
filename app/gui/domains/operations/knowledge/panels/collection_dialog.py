"""
CollectionDialog – Dialogs for create, rename, and assign sources to collections.
"""

from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
)
from PySide6.QtCore import Qt


class CreateCollectionDialog(QDialog):
    """Dialog to create a new collection (name only)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Collection")
        self.setMinimumWidth(320)
        self._name: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Collection name:"))
        self._edit = QLineEdit()
        self._edit.setPlaceholderText("e.g. Research, Code, Documentation")
        self._edit.setStyleSheet("padding: 8px; font-size: 13px;")
        self._edit.returnPressed.connect(self._on_ok)
        layout.addWidget(self._edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._on_ok)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_ok(self) -> None:
        name = self._edit.text().strip()
        if name:
            self._name = name
            self.accept()

    def get_name(self) -> Optional[str]:
        return self._name


class RenameCollectionDialog(QDialog):
    """Dialog to rename an existing collection."""

    def __init__(self, current_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Collection")
        self.setMinimumWidth(320)
        self._name: Optional[str] = None
        self._current_name = current_name
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("New name:"))
        self._edit = QLineEdit()
        self._edit.setText(self._current_name)
        self._edit.setPlaceholderText("Collection name")
        self._edit.setStyleSheet("padding: 8px; font-size: 13px;")
        self._edit.selectAll()
        self._edit.returnPressed.connect(self._on_ok)
        layout.addWidget(self._edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._on_ok)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_ok(self) -> None:
        name = self._edit.text().strip()
        if name:
            self._name = name
            self.accept()

    def get_name(self) -> Optional[str]:
        return self._name


class AssignSourcesDialog(QDialog):
    """
    Dialog to assign sources to a collection.
    Multi-select list of sources. Selection = assign to collection.
    """

    def __init__(
        self,
        sources: List[Dict],
        collection: Dict,
        assigned_paths: List[str],
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Assign Sources to {collection.get('name', 'Collection')}")
        self.setMinimumSize(400, 350)
        self._sources = sources
        self._collection_id = collection.get("id", "")
        self._assigned_paths = set(assigned_paths)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        hint = QLabel("Select sources to assign to this collection:")
        hint.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(hint)

        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._list.setStyleSheet("""
            QListWidget {
                padding: 4px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #dbeafe;
            }
        """)
        for s in self._sources:
            path = s.get("path", "")
            name = s.get("name", path.split("/")[-1] if path else "?")
            item = QListWidgetItem(name[:60] + ("…" if len(name) > 60 else ""))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self._list.addItem(item)
            if path in self._assigned_paths:
                item.setSelected(True)
        layout.addWidget(self._list, 1)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_selected_paths(self) -> List[str]:
        """Paths of selected (assigned) sources."""
        paths = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.isSelected():
                path = item.data(Qt.ItemDataRole.UserRole)
                if path:
                    paths.append(path)
        return paths
