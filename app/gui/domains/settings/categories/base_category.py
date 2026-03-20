"""Base class for settings category components."""

from PySide6.QtWidgets import QWidget


class BaseSettingsCategory(QWidget):
    """Base for extendable settings category components."""

    def __init__(self, category_id: str, parent=None):
        super().__init__(parent)
        self._category_id = category_id
        self.setObjectName(f"{category_id}Category")

    @property
    def category_id(self) -> str:
        return self._category_id
