"""PromptStudioInspector – Inspector-Inhalt für Prompt Studio."""

from typing import Callable, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox

from app.gui.domains.operations.prompt_studio.panels.prompt_version_panel import PromptVersionPanel


def _format_datetime(dt) -> str:
    """Formatiert Datum/Zeit lesbar."""
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
        return s
    except (ValueError, TypeError):
        return "—"


class PromptStudioInspector(QWidget):
    """Inspector für Prompt Studio: Projektkontext, Metadaten, Versionen."""

    def __init__(
        self,
        project_name: str | None = None,
        prompt=None,
        on_version_selected: Optional[Callable[[dict], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("promptStudioInspector")
        self._project_name = project_name
        self._prompt = prompt
        self._on_version_selected = on_version_selected
        self._version_panel: Optional[PromptVersionPanel] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        if self._project_name:
            proj_group = QGroupBox("Aktives Projekt")
            gl = QVBoxLayout(proj_group)
            label = QLabel(self._project_name)
            gl.addWidget(label)
            layout.addWidget(proj_group)

        if self._prompt is not None:
            self._add_prompt_details(layout)
        else:
            no_sel = QGroupBox("Auswahl")
            no_gl = QVBoxLayout(no_sel)
            label = QLabel("Wählen Sie einen Prompt aus.")
            label.setWordWrap(True)
            no_gl.addWidget(label)
            layout.addWidget(no_sel)

        layout.addStretch()

    def _add_prompt_details(self, layout: QVBoxLayout) -> None:
        p = self._prompt
        scope = getattr(p, "scope", "global")
        scope_label = "Projekt" if scope == "project" else "Global"
        project_id = getattr(p, "project_id", None)

        meta_group = QGroupBox("Prompt-Metadaten")
        gl = QVBoxLayout(meta_group)

        rows = [
            ("Name", p.title or "—"),
            ("Beschreibung", (p.description or "").strip() or "—"),
            ("Scope", scope_label),
            ("Kategorie", p.category or "general"),
            ("Projekt-ID", str(project_id) if project_id is not None else "—"),
            ("Erstellt", _format_datetime(p.created_at)),
            ("Geändert", _format_datetime(p.updated_at)),
        ]
        for key, val in rows:
            row = QLabel(f"<b>{key}:</b> {val}")
            row.setWordWrap(True)
            gl.addWidget(row)

        layout.addWidget(meta_group)

        if p.tags:
            tags_group = QGroupBox("Tags")
            tg = QVBoxLayout(tags_group)
            tags_label = QLabel(", ".join(p.tags))
            tags_label.setWordWrap(True)
            tg.addWidget(tags_label)
            layout.addWidget(tags_group)

        # Version panel – display versions, allow switching
        self._version_panel = PromptVersionPanel(self)
        self._version_panel.set_prompt(p.id)
        if self._on_version_selected:
            self._version_panel.version_selected.connect(self._on_version_selected)
        layout.addWidget(self._version_panel)

    def set_prompt(self, prompt) -> None:
        """Aktualisiert den angezeigten Prompt."""
        self._prompt = prompt
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._setup_ui()
