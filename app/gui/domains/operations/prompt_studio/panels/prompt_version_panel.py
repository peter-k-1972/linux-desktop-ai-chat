"""
PromptVersionPanel – Displays prompt versions and allows switching.

Shows: v1, v2, v3, … with created date.
Switching loads the version into the editor.

Batch 2: optional ``prompt_studio_port`` → Presenter/Port/Adapter; ``versions=``-Pfad unverändert.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Signal, Qt

from app.gui.domains.operations.prompt_studio.prompt_studio_versions_sink import PromptStudioVersionsSink
from app.ui_application.presenters.prompt_studio_versions_presenter import PromptStudioVersionsPresenter
from app.ui_contracts.workspaces.prompt_studio_versions import (
    LoadPromptVersionsCommand,
    PromptVersionPanelState,
    PromptVersionRowDto,
)

if TYPE_CHECKING:
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort


def _format_date(dt: Any) -> str:
    """Format date for display."""
    if not dt:
        return "—"
    try:
        if hasattr(dt, "strftime"):
            return dt.strftime("%d.%m.%Y %H:%M")
        s = str(dt)
        if "T" in s:
            from datetime import datetime
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return d.strftime("%d.%m.%Y %H:%M")
        return s[:16] if len(s) >= 16 else s
    except (ValueError, TypeError):
        return "—"


def _version_dto_to_widget_dict(dto: PromptVersionRowDto) -> dict[str, Any]:
    return {
        "version": dto.version,
        "title": dto.title,
        "content": dto.content,
        "created_at": dto.created_at_iso,
    }


class VersionItemWidget(QFrame):
    """Single version entry: vN, created date."""

    def __init__(self, version_data: dict, active: bool = False, parent=None):
        super().__init__(parent)
        self.version_data = version_data
        self._active = active
        self.setObjectName("versionItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        version_num = self.version_data.get("version", 0)
        title = QLabel(f"v{version_num}")
        title.setObjectName("versionItemLabel")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #1f2937;")
        layout.addWidget(title)

        created = self.version_data.get("created_at")
        date_label = QLabel(_format_date(created))
        date_label.setObjectName("versionItemDate")
        date_label.setStyleSheet("font-size: 11px; color: #64748b;")
        layout.addWidget(date_label)

    def _apply_style(self) -> None:
        if self._active:
            self.setStyleSheet("""
                #versionItem {
                    background: #eff6ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                #versionItem {
                    background: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                }
                #versionItem:hover {
                    background: #f9fafb;
                    border-color: #d1d5db;
                }
            """)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()


class PromptVersionPanel(QFrame):
    """
    Displays prompt versions (v1, v2, v3, …).

    - Version metadata: created date, author (optional later)
    - Switching loads the version into the editor (emits version_selected)
    """

    version_selected = Signal(dict)  # {version, title, content, created_at}

    def __init__(self, parent=None, *, prompt_studio_port: Optional[PromptStudioPort] = None):
        super().__init__(parent)
        self.setObjectName("promptVersionPanel")
        self.setMinimumWidth(180)
        self._prompt_id: Optional[int] = None
        self._active_version: Optional[int] = None
        self._version_widgets: dict = {}
        self._versions_sink: PromptStudioVersionsSink | None = None
        self._versions_presenter: PromptStudioVersionsPresenter | None = None
        if prompt_studio_port is not None:
            self._versions_sink = PromptStudioVersionsSink(self)
            self._versions_presenter = PromptStudioVersionsPresenter(
                self._versions_sink,
                prompt_studio_port,
            )
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Versionen")
        title.setObjectName("versionPanelTitle")
        title.setStyleSheet("font-weight: 600; font-size: 14px; color: #374151;")
        layout.addWidget(title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._list_content = QWidget()
        self._list_layout = QVBoxLayout(self._list_content)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._scroll.setWidget(self._list_content)
        layout.addWidget(self._scroll, 1)

        self._empty_label = QLabel("Keine Versionen.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 16px;")
        self._empty_label.hide()

        self.setStyleSheet("""
            #promptVersionPanel {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)

    def set_prompt(self, prompt_id: Optional[int], *, versions: Optional[list[dict]] = None) -> None:
        """Load versions for the given prompt (service) or use ``versions`` when provided."""
        self._prompt_id = prompt_id
        self._active_version = None
        if versions is not None:
            self._render_versions(versions)
        elif self._use_port_path() and prompt_id is not None and self._versions_presenter is not None:
            self._versions_presenter.handle_command(LoadPromptVersionsCommand(prompt_id))
        else:
            self._load_versions_from_service()

    def _use_port_path(self) -> bool:
        return self._versions_presenter is not None

    def apply_prompt_version_panel_state(self, state: PromptVersionPanelState) -> None:
        """Sink: Versionen aus Contract-Zustand (Batch 2)."""
        if state.phase == "loading":
            while self._list_layout.count():
                item = self._list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self._version_widgets.clear()
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText("Versionen werden geladen …")
            self._empty_label.show()
            return

        if state.phase == "error":
            while self._list_layout.count():
                item = self._list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self._version_widgets.clear()
            msg = state.error.message if state.error else "Fehler."
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText(msg)
            self._empty_label.show()
            return

        if state.phase == "empty":
            self._render_versions([])
            return

        dict_rows = [_version_dto_to_widget_dict(r) for r in state.rows]
        self._render_versions(dict_rows)

    def _load_versions_from_service(self) -> None:
        """Load and display versions from PromptService."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._version_widgets.clear()

        if self._prompt_id is None:
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText("Prompt auswählen.")
            self._empty_label.show()
            return

        try:
            from app.prompts.prompt_service import get_prompt_service
            versions = get_prompt_service().list_versions(self._prompt_id)
        except Exception:
            versions = []

        self._render_versions(versions)

    def _render_versions(self, versions: list[dict]) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._version_widgets.clear()

        if self._prompt_id is None and not versions:
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText("Prompt auswählen.")
            self._empty_label.show()
            return

        if not versions:
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText("Keine Versionen.")
            self._empty_label.show()
            return

        self._empty_label.hide()
        for v in versions:
            self._add_version_item(v)

        self._list_layout.addStretch()

    def _add_version_item(self, version_data: dict) -> None:
        version_num = version_data.get("version", 0)
        active = version_num == self._active_version
        item = VersionItemWidget(version_data, active, self)

        def _on_press(e, vd=version_data):
            if e.button() == Qt.MouseButton.LeftButton:
                self._on_version_clicked(vd)

        item.mousePressEvent = _on_press
        self._version_widgets[version_num] = item
        self._list_layout.addWidget(item)

    def _on_version_clicked(self, version_data: dict) -> None:
        """Switching loads the version into the editor."""
        version_num = version_data.get("version", 0)
        self._active_version = version_num
        for wid in self._version_widgets.values():
            wid.set_active(wid.version_data.get("version") == version_num)
        self.version_selected.emit(version_data)

    def refresh(self) -> None:
        """Reload versions (e.g. after save)."""
        if self._prompt_id is None:
            self._load_versions_from_service()
            return
        if self._use_port_path() and self._versions_presenter is not None:
            self._versions_presenter.handle_command(LoadPromptVersionsCommand(self._prompt_id))
        else:
            self._load_versions_from_service()

    def set_active_version(self, version_num: Optional[int]) -> None:
        """Set the active version without emitting."""
        self._active_version = version_num
        for wid in self._version_widgets.values():
            wid.set_active(wid.version_data.get("version") == version_num)
