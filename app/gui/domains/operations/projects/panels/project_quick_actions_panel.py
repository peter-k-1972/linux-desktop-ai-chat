"""
ProjectQuickActionsPanel – Quick Actions für den Project Overview.

New Chat, Add Source, New Prompt, Open Agents.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt, Signal

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


class ProjectQuickActionsPanel(QFrame):
    """Panel mit Quick Actions."""

    new_chat_requested = Signal()
    add_source_requested = Signal()
    new_prompt_requested = Signal()
    open_agents_requested = Signal()
    open_knowledge_requested = Signal()
    open_prompt_studio_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectQuickActionsPanel")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Quick Actions")
        title.setStyleSheet("font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 8px;")
        layout.addWidget(title)

        btn_layout = QGridLayout()
        btn_layout.setSpacing(8)

        actions = [
            ("Neuer Chat", IconRegistry.CHAT, self.new_chat_requested),
            ("Quelle hinzufügen", IconRegistry.KNOWLEDGE, self.add_source_requested),
            ("Neuer Prompt", IconRegistry.PROMPT_STUDIO, self.new_prompt_requested),
            ("Knowledge", IconRegistry.KNOWLEDGE, self.open_knowledge_requested),
            ("Prompt Studio", IconRegistry.PROMPT_STUDIO, self.open_prompt_studio_requested),
            ("Agents", IconRegistry.AGENTS, self.open_agents_requested),
        ]
        for i, (label, icon_name, signal) in enumerate(actions):
            btn = QPushButton(label)
            btn.setIcon(IconManager.get(icon_name, size=18))
            btn.setObjectName("quickActionButton")
            btn.setStyleSheet("""
                #quickActionButton {
                    background: rgba(139, 92, 246, 0.2);
                    border: 1px solid rgba(139, 92, 246, 0.4);
                    border-radius: 8px;
                    padding: 10px 16px;
                    color: #e9d5ff;
                    font-size: 13px;
                    font-weight: 500;
                }
                #quickActionButton:hover {
                    background: rgba(139, 92, 246, 0.35);
                    border-color: rgba(139, 92, 246, 0.6);
                }
            """)
            btn.clicked.connect(signal.emit)
            btn_layout.addWidget(btn, i // 3, i % 3)

        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            #projectQuickActionsPanel {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 16px;
            }
        """)
