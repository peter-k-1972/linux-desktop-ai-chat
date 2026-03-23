"""
ChatMessageWidget – Moderne Message-Bubbles für AI-Chat.
Assistant links, User rechts, klare visuelle Hierarchie.
"""

import datetime
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from app.resources.styles import get_theme_colors
from app.gui.theme import design_metrics as dm


class ChatMessageWidget(QWidget):
    """Moderne Chat-Nachricht als Bubble mit Avatar und Timestamp."""

    def __init__(
        self,
        role: str,
        content: str,
        timestamp=None,
        theme: str = "dark",
        avatar_path=None,
        parent=None,
    ):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now().strftime("%H:%M")
        self.theme = theme
        self.avatar_path = avatar_path
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, dm.SPACE_MD_PX, 0, dm.SPACE_MD_PX)
        main_layout.setSpacing(0)

        is_user = self.role == "user"
        is_system = self.role == "system"
        colors = get_theme_colors(self.theme)

        # Bubble-Container
        bubble_container = QVBoxLayout()
        bubble_container.setSpacing(4)

        # Text-Bubble
        self.bubble = QLabel(self.content)
        self.bubble.setWordWrap(True)
        self.bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.bubble.setTextFormat(Qt.RichText)
        self.bubble.setOpenExternalLinks(True)
        self.bubble.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        # Farben je nach Rolle und Theme
        if self.theme == "light":
            user_bg = "#e3f2fd"
            assistant_bg = "#f5f5f5"
            system_bg = "#fafafa"
            text_color = "#1a1a1a"
            bubble_border = "transparent"
        else:
            user_bg = "#2d4a6f"
            assistant_bg = "#3a3a3a"
            system_bg = "#404040"
            text_color = "#e8e8e8"
            bubble_border = "rgba(255,255,255,0.06)"

        if is_system:
            bg_color = system_bg
            bubble_border = "transparent"
            text_color = colors["muted"]
        else:
            bg_color = user_bg if is_user else assistant_bg

        self.bubble.setStyleSheet(
            f"""
            background-color: {bg_color};
            color: {text_color};
            border-radius: 16px;
            padding: 14px 18px;
            font-size: 15px;
            line-height: 1.5;
            border: 1px solid {bubble_border};
        """
        )

        # Max-Breite: Policy CHAT_BUBBLE_MAX_WIDTH_PX (schmaler als CHAT_CONTENT_MAX_WIDTH_PX).
        self.bubble.setMaximumWidth(dm.CHAT_BUBBLE_MAX_WIDTH_PX)

        # Timestamp – dezent, klein
        time_label = QLabel(self.timestamp)
        time_label.setStyleSheet(
            f"font-size: 11px; color: {colors['muted']}; font-weight: 400;"
        )

        bubble_container.addWidget(self.bubble)
        bubble_container.addWidget(time_label)

        # Avatar (nur bei user/assistant)
        if is_system:
            main_layout.addStretch()
            main_layout.addLayout(bubble_container, 1)
            main_layout.addStretch()
            time_label.setAlignment(Qt.AlignCenter)
            return

        avatar_label = QLabel()
        avatar_label.setFixedSize(32, 32)
        if self.avatar_path:
            icon = QIcon(self.avatar_path)
            pixmap = icon.pixmap(32, 32)
            avatar_label.setPixmap(pixmap)
            avatar_label.setScaledContents(True)
        else:
            avatar_label.setText("U" if is_user else "A")
            avatar_label.setAlignment(Qt.AlignCenter)
            avatar_label.setStyleSheet(
                f"""
                background-color: {colors["accent"]};
                color: white;
                border-radius: 16px;
                font-weight: 600;
                font-size: 12px;
            """
            )

        if is_user:
            time_label.setAlignment(Qt.AlignRight)
            main_layout.addStretch()
            main_layout.addLayout(bubble_container, 1)
            main_layout.addWidget(avatar_label, 0, Qt.AlignTop | Qt.AlignRight)
        else:
            time_label.setAlignment(Qt.AlignLeft)
            main_layout.addWidget(avatar_label, 0, Qt.AlignTop | Qt.AlignLeft)
            main_layout.addLayout(bubble_container, 1)
            main_layout.addStretch()

    def set_content(self, content: str):
        """Aktualisiert den Inhalt (Streaming oder final)."""
        self.content = content
        if content.strip().startswith("<"):
            self.bubble.setTextFormat(Qt.RichText)
            self.bubble.setText(content)
        else:
            self.bubble.setTextFormat(Qt.PlainText)
            self.bubble.setText(content)
