import datetime
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QSpacerItem, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
import os
from app.resources.styles import get_theme_colors

class MessageWidget(QWidget):
    def __init__(self, role, content, timestamp=None, theme="dark", avatar_path=None, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now().strftime("%H:%M")
        self.theme = theme
        self.avatar_path = avatar_path
        
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(10)

        # Bubble Container (Vertical for Bubble + Timestamp)
        bubble_container = QVBoxLayout()
        bubble_container.setSpacing(2)

        # The Text Bubble (QLabel supports HTML, links via setOpenExternalLinks)
        self.bubble = QLabel(self.content)
        self.bubble.setWordWrap(True)
        self.bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.bubble.setTextFormat(Qt.RichText)
        self.bubble.setOpenExternalLinks(True)
        
        # Style calculation based on role and theme (hell/dunkel)
        is_user = self.role == "user"
        is_system = self.role == "system"
        colors = get_theme_colors(self.theme)

        if self.theme == "light":
            user_bg = "#d0e8ff"
            assistant_bg = "#f0f0f0"
            system_bg = "#eeeeee"
            text_color = "#1a1a1a"
            border_color = "rgba(0, 0, 0, 0.1)"
        else:
            user_bg = "#3d5a80"
            assistant_bg = "#404040"
            system_bg = "#4a4a4a"
            text_color = "#e8e8e8"
            border_color = "#505050"

        if is_system:
            bg_color = system_bg
            border_color = "transparent"
            text_color = colors["muted"]
        else:
            bg_color = user_bg if is_user else assistant_bg
        
        self.bubble.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            border-radius: 20px;
            padding: 14px 18px;
            font-size: 11.5pt;
            border: 1px solid {border_color};
            line-height: 1.5;
        """)
        
        # Max width 85% of parent width
        self.bubble.setMaximumWidth(800)
        self.bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        # We'll use a spacer to push the bubble to the correct side

        # Timestamp
        time_label = QLabel(self.timestamp)
        time_label.setStyleSheet(f"font-size: 10px; color: {colors['muted']};")
        time_label.setAlignment(Qt.AlignRight if is_user else (Qt.AlignCenter if is_system else Qt.AlignLeft))

        bubble_container.addWidget(self.bubble)
        bubble_container.addWidget(time_label)

        # Avatar
        if is_system:
            # System messages don't need an avatar
            spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            main_layout.addItem(spacer)
            main_layout.addLayout(bubble_container)
            main_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            return

        avatar_label = QLabel()
        avatar_label.setFixedSize(36, 36)
        if self.avatar_path:
            if self.avatar_path.startswith(":/"):
                icon = QIcon(self.avatar_path)
            else:
                icon = QIcon(self.avatar_path)
            pixmap = icon.pixmap(36, 36)
            avatar_label.setPixmap(pixmap)
            avatar_label.setScaledContents(True)
        else:
            # Fallback text-based avatar if no icon
            avatar_label.setText("U" if is_user else "AI")
            avatar_label.setAlignment(Qt.AlignCenter)
            accent = colors["accent"]
            avatar_label.setStyleSheet(f"""
                background-color: {accent};
                color: white;
                border-radius: 18px;
                font-weight: bold;
                font-size: 10pt;
            """)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        if is_user:
            main_layout.addItem(spacer)
            main_layout.addLayout(bubble_container)
            main_layout.addWidget(avatar_label, alignment=Qt.AlignTop)
        else:
            main_layout.addWidget(avatar_label, alignment=Qt.AlignTop)
            main_layout.addLayout(bubble_container)
            main_layout.addItem(spacer)

    def set_content(self, content):
        self.content = content
        # HTML from markdown_to_html vs plain text during streaming
        if content.strip().startswith("<"):
            self.bubble.setTextFormat(Qt.RichText)
            self.bubble.setText(content)
        else:
            self.bubble.setTextFormat(Qt.PlainText)
            self.bubble.setText(content)
