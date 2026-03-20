"""
AgentListItem – Single agent entry in the Agent Library.

Displays: name, model, prompt (preview), number of tools.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

from app.agents.agent_profile import AgentProfile


def _truncate(text: str, max_len: int = 60) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return "—"
    text = str(text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


class AgentListItem(QFrame):
    """Single agent entry showing name, model, prompt preview, tool count."""

    clicked = Signal(object)  # AgentProfile

    def __init__(self, profile: AgentProfile, active: bool = False, parent=None):
        super().__init__(parent)
        self.profile = profile
        self._active = active
        self.setObjectName("agentListItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Name
        name = self.profile.effective_display_name or "Unbenannt"
        name_label = QLabel(name)
        name_label.setObjectName("agentItemName")
        name_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #1f2937;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Meta row: model, tools count
        meta = QHBoxLayout()
        meta.setSpacing(12)

        model = self.profile.assigned_model or "—"
        model_label = QLabel(f"Model: {model}")
        model_label.setObjectName("agentItemModel")
        model_label.setStyleSheet("font-size: 11px; color: #64748b;")
        model_label.setWordWrap(True)
        meta.addWidget(model_label)

        tools_count = len(self.profile.tools) if self.profile.tools else 0
        tools_label = QLabel(f"{tools_count} tools")
        tools_label.setObjectName("agentItemTools")
        tools_label.setStyleSheet("font-size: 11px; color: #64748b;")
        meta.addWidget(tools_label)
        meta.addStretch()
        layout.addLayout(meta)

        # Prompt preview
        prompt = self.profile.system_prompt or ""
        prompt_preview = _truncate(prompt, 80)
        prompt_label = QLabel(prompt_preview)
        prompt_label.setObjectName("agentItemPrompt")
        prompt_label.setStyleSheet("font-size: 11px; color: #94a3b8; font-style: italic;")
        prompt_label.setWordWrap(True)
        layout.addWidget(prompt_label)

    def _apply_style(self) -> None:
        if self._active:
            self.setStyleSheet("""
                #agentListItem {
                    background: #eff6ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                #agentListItem {
                    background: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                }
                #agentListItem:hover {
                    background: #f9fafb;
                    border-color: #d1d5db;
                }
            """)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.profile)
        super().mousePressEvent(event)
