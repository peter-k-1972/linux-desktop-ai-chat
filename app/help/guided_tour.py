"""
GuidedTour – Schritt-für-Schritt-Anleitungen (Guided Tours).

Touren: Erste Schritte, Chat, Agenten, Prompts, Medien.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.resources.styles import get_theme_colors


@dataclass
class TourStep:
    """Ein Schritt einer Guided Tour."""

    title: str
    content: str
    target_widget: Optional[str] = None  # ObjectName des zu highlightenden Widgets
    hint: Optional[str] = None  # Zusätzlicher Hinweis


# Vordefinierte Touren
TOUR_GETTING_STARTED: List[TourStep] = [
    TourStep(
        "Willkommen",
        "Willkommen beim Linux Desktop Chat! Diese Tour führt Sie durch die Grundlagen.",
    ),
    TourStep(
        "Neuer Chat",
        "Klicken Sie in der Sidebar auf 'Neuer Chat', um eine neue Konversation zu starten.",
        target_widget=None,
    ),
    TourStep(
        "Eingabe",
        "Geben Sie Ihre Nachricht in das Eingabefeld ein und klicken Sie auf Senden.",
        target_widget="chatInput",
    ),
    TourStep(
        "Modell wählen",
        "Im Header können Sie das Modell und die Rolle (Schnell, Denken, Code, …) wählen.",
        target_widget="headerModelCombo",
    ),
    TourStep(
        "Fertig",
        "Sie sind bereit! Nutzen Sie /think für komplexe Aufgaben oder /code für Programmierfragen.",
    ),
]

TOUR_CHAT: List[TourStep] = [
    TourStep("Chat-Grundlagen", "Der Chat unterstützt Slash-Commands und verschiedene Modi."),
    TourStep(
        "Slash-Commands",
        "Probieren Sie: /think für Analyse, /code für Programmierung, /research für Recherche.",
        hint="Beispiel: /think Erkläre Quantencomputing",
    ),
    TourStep(
        "RAG aktivieren",
        "Aktivieren Sie die RAG-Checkbox, um Kontext aus indexierten Dokumenten zu nutzen.",
        target_widget="headerRAG",
    ),
    TourStep(
        "Agenten",
        "Wählen Sie einen Agenten im Dropdown für spezialisierte Personas (z.B. Code Agent).",
        target_widget="headerAgentCombo",
    ),
]

TOUR_AGENTS: List[TourStep] = [
    TourStep("Agenten-System", "Agenten sind spezialisierte Personas mit eigenem System-Prompt und Modell."),
    TourStep(
        "Agenten verwalten",
        "Öffnen Sie 'Agenten verwalten' in der Toolbar, um Agenten zu erstellen und zu bearbeiten.",
    ),
    TourStep(
        "Agent auswählen",
        "Wählen Sie im Chat-Header einen Agenten. Der System-Prompt wird automatisch gesendet.",
        target_widget="headerAgentCombo",
    ),
    TourStep(
        "Delegation",
        "Mit /delegate starten Sie die Agenten-Orchestrierung für komplexe Aufgaben.",
        hint="Beispiel: /delegate Erstelle ein Video über KI",
    ),
]

TOUR_PROMPTS: List[TourStep] = [
    TourStep("Prompt-System", "Prompts sind wiederverwendbare Vorlagen für System- oder User-Nachrichten."),
    TourStep(
        "Prompt-Manager",
        "Im Side-Panel finden Sie den Prompt-Manager. Öffnen Sie das Prompts-Tab.",
        target_widget="promptManagerPanel",
    ),
    TourStep(
        "Prompt anwenden",
        "Klicken Sie 'Anwenden', um einen Prompt als System-Nachricht in den Chat zu übernehmen.",
    ),
    TourStep(
        "In Composer",
        "Oder wählen Sie 'In Composer', um den Prompt-Text in die Eingabezeile zu übernehmen.",
    ),
]

TOUR_MEDIA: List[TourStep] = [
    TourStep("Medien-Generierung", "Image-, Video- und Audio-Agenten sind für Medien-Workflows vorbereitet."),
    TourStep(
        "Image Agent",
        "Wählen Sie den Image Agent für Bildgenerierung. Externe Pipelines sind in design_system.json konfigurierbar.",
    ),
    TourStep(
        "Workflow Agent",
        "Der Workflow Agent orchestriert ComfyUI und Medien-Pipelines.",
    ),
]


class GuidedTourDialog(QDialog):
    """Dialog für eine Guided Tour mit Schritten."""

    step_changed = Signal(int)

    def __init__(self, steps: List[TourStep], title: str = "Guided Tour", theme: str = "dark", parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current_index = 0
        self.theme = theme
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.init_ui()
        self.apply_theme()
        self._show_step(0)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Fortschritt
        self.progress = QProgressBar()
        self.progress.setMaximum(len(self.steps))
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Inhalt
        self.title_label = QLabel()
        self.title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(self.title_label)

        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setMinimumHeight(80)
        layout.addWidget(self.content_label)

        self.hint_label = QLabel()
        self.hint_label.setStyleSheet("color: #888; font-style: italic;")
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Zurück")
        self.back_btn.clicked.connect(self._on_back)
        btn_layout.addWidget(self.back_btn)

        self.next_btn = QPushButton("Weiter →")
        self.next_btn.clicked.connect(self._on_next)
        btn_layout.addWidget(self.next_btn)

        self.finish_btn = QPushButton("Fertig")
        self.finish_btn.clicked.connect(self.accept)
        self.finish_btn.hide()
        btn_layout.addWidget(self.finish_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _show_step(self, index: int):
        self.current_index = index
        self.progress.setValue(index + 1)
        step = self.steps[index]
        self.title_label.setText(step.title)
        self.content_label.setText(step.content)
        self.hint_label.setText(step.hint or "")
        self.hint_label.setVisible(bool(step.hint))
        self.back_btn.setEnabled(index > 0)
        is_last = index >= len(self.steps) - 1
        self.next_btn.setVisible(not is_last)
        self.finish_btn.setVisible(is_last)
        self.step_changed.emit(index)

    def _on_back(self):
        if self.current_index > 0:
            self._show_step(self.current_index - 1)

    def _on_next(self):
        if self.current_index < len(self.steps) - 1:
            self._show_step(self.current_index + 1)

    def apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        self.setStyleSheet(f"QDialog {{ color: {fg}; }} QLabel {{ color: {fg}; }}")


class GuidedTour:
    """Hilfsklasse zum Starten von Guided Tours."""

    TOURS = {
        "getting_started": ("Erste Schritte", TOUR_GETTING_STARTED),
        "chat": ("Chat verwenden", TOUR_CHAT),
        "agents": ("Agenten erstellen", TOUR_AGENTS),
        "prompts": ("Prompts verwalten", TOUR_PROMPTS),
        "media": ("Medien generieren", TOUR_MEDIA),
    }

    @classmethod
    def run(cls, tour_id: str, theme: str = "dark", parent=None) -> GuidedTourDialog:
        """Startet eine Guided Tour."""
        if tour_id not in cls.TOURS:
            tour_id = "getting_started"
        title, steps = cls.TOURS[tour_id]
        dialog = GuidedTourDialog(steps, title=title, theme=theme, parent=parent)
        return dialog
