"""
AgentAvatarWidget – Avatar-Vorschau und -Verwaltung.

Placeholder bei fehlendem Avatar, Laden/Ändern/Entfernen.
"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont

from app.resources.styles import get_theme_colors


class AgentAvatarWidget(QWidget):
    """Avatar-Anzeige und -Auswahl."""

    avatar_changed = Signal(str)  # neuer Pfad oder ""
    avatar_removed = Signal()

    def __init__(self, theme: str = "dark", size: int = 80, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.size = size
        self._current_path: str | None = None
        self.init_ui()

    def init_ui(self):
        self.setObjectName("agentAvatarWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.frame = QFrame()
        self.frame.setObjectName("avatarFrame")
        self.frame.setFixedSize(self.size + 8, self.size + 8)
        self.frame.setStyleSheet(
            f"""
            QFrame#avatarFrame {{
                border: 2px solid {get_theme_colors(self.theme).get('top_bar_border', '#505050')};
                border-radius: {(self.size + 8) // 2}px;
                background-color: {get_theme_colors(self.theme).get('top_bar_bg', '#353535')};
            }}
            """
        )
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(4, 4, 4, 4)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(self.size, self.size)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setScaledContents(True)
        font = QFont()
        font.setPixelSize(self.size // 2)
        self.avatar_label.setFont(font)
        self.avatar_label.setStyleSheet("background: transparent; border: none;")
        frame_layout.addWidget(self.avatar_label)

        layout.addWidget(self.frame)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.change_btn = QPushButton("Ändern")
        self.change_btn.setObjectName("avatarChangeBtn")
        self.change_btn.clicked.connect(self._on_change)
        self.remove_btn = QPushButton("Entfernen")
        self.remove_btn.setObjectName("avatarRemoveBtn")
        self.remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self.change_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        self._show_placeholder()

    def set_avatar_path(self, path: str | None):
        """Setzt den Avatar-Pfad und aktualisiert die Anzeige."""
        self._current_path = path
        if path and os.path.isfile(path):
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(
                    self.size,
                    self.size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.avatar_label.setPixmap(scaled)
                self.avatar_label.setText("")
                return
        self._show_placeholder()

    def _show_placeholder(self):
        """Zeigt den Placeholder (Initialen oder Icon)."""
        self.avatar_label.setPixmap(QPixmap())
        self.avatar_label.setText("?")
        self.avatar_label.setStyleSheet(
            "color: #64748b; background: transparent; border: none;"
        )

    def _on_change(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Avatar auswählen",
            "",
            "Bilder (*.png *.jpg *.jpeg *.gif *.webp);;Alle Dateien (*)",
        )
        if path:
            self.set_avatar_path(path)
            self.avatar_changed.emit(path)

    def _on_remove(self):
        self._current_path = None
        self._show_placeholder()
        self.avatar_changed.emit("")
        self.avatar_removed.emit()

    def get_avatar_path(self) -> str | None:
        return self._current_path

    def refresh_theme(self, theme: str):
        self.theme = theme
        self.frame.setStyleSheet(
            f"""
            QFrame#avatarFrame {{
                border: 2px solid {get_theme_colors(theme).get('top_bar_border', '#505050')};
                border-radius: {(self.size + 8) // 2}px;
                background-color: {get_theme_colors(theme).get('top_bar_bg', '#353535')};
            }}
            """
        )
