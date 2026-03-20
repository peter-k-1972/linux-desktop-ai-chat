"""
LEGACY: Alte App-Einstiegspunkte (MainWindow, ChatWidget, CommandCenterView).

Diese Module sind deprecated. Standard-Startpunkt ist die neue GUI-Shell (run_gui_shell).
Legacy-GUI starten: python run_legacy_gui.py

NICHT als Standard nutzen. Für neue GUI: python main.py oder python -m app
"""

import sys
import warnings
import asyncio
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QDockWidget, QInputDialog, QStackedWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize, Qt
from qasync import QEventLoop
from app.gui.legacy import ChatWidget, SidebarWidget, ProjectChatListWidget
from app.gui.domains.command_center import CommandCenterView
from app.providers.ollama_client import OllamaClient
from app.core.config.settings import AppSettings
from app.core.db import DatabaseManager
from app.gui.domains.settings.settings_dialog import SettingsDialog
from app.resources.styles import get_stylesheet
from app.core.models.orchestrator import ModelOrchestrator
from app.providers import LocalOllamaProvider, CloudOllamaProvider
from app.rag.service import RAGService
from app.metrics import get_metrics_collector
try:
    from app import resources_rc
except ImportError:
    pass

class MainWindow(QMainWindow):
    def __init__(self, client: OllamaClient, orchestrator: ModelOrchestrator, settings: AppSettings = None):
        super().__init__()
        self.client = client
        self.orchestrator = orchestrator
        self.settings = settings or AppSettings()  # InMemoryBackend wenn keine Settings übergeben
        self.db = DatabaseManager()
        
        self.setWindowTitle("Ollama Linux Desktop Chat")
        self.setMinimumSize(800, 600)
        
        rag_service = RAGService()
        self.chat_widget = ChatWidget(
            self.client, self.settings, self.db, self.orchestrator,
            rag_service=rag_service,
        )
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.chat_widget)
        self.command_center = CommandCenterView(theme=self.settings.theme)
        self.command_center.back_to_chat_requested.connect(self.show_chat_view)
        self.stacked_widget.addWidget(self.command_center)
        self.setCentralWidget(self.stacked_widget)
        
        self.init_sidebar()
        self.init_toolbar()
        self.apply_theme()
        get_metrics_collector()

        # Statusleiste für Debug-/Ollama-Infos
        self.statusBar().showMessage("Ollama-Status wird geprüft ...")
        # Fenstergröße aus Layout ableiten, dann nicht mehr veränderbar
        QTimer.singleShot(50, self._lock_window_size)
        # Debug-Check erst starten, wenn die Event-Loop läuft (wie bei ChatWidget.load_models)
        QTimer.singleShot(0, lambda: asyncio.create_task(self.init_ollama_debug_status()))

    async def init_ollama_debug_status(self):
        """
        Holt beim Start Debug-Informationen zur Ollama-Instanz und zeigt sie
        in der Statusleiste an.
        """
        try:
            # Harter Timeout, damit die Statusleiste nicht "hängen" bleibt,
            # falls Ollama gar nicht oder nur sehr träge antwortet.
            info = await asyncio.wait_for(self.client.get_debug_info(), timeout=5.0)
        except asyncio.TimeoutError:
            self.statusBar().showMessage(
                f"Ollama: Timeout bei der Statusabfrage ({self.client.base_url})"
            )
            return
        except Exception as e:
            self.statusBar().showMessage(f"Ollama-Debugfehler: {e}")
            return

        if not info.get("online"):
            self.statusBar().showMessage(
                f"Ollama: offline oder nicht erreichbar ({info.get('base_url')})"
            )
            return

        version = info.get("version") or "unbekannt"
        model_count = info.get("model_count", 0)
        vram = info.get("vram_used_mib")
        vram_str = f"{vram} MiB VRAM" if vram is not None else "VRAM: n/a"

        # Kurzen Überblick über laufende Prozesse
        processes = info.get("processes") or []
        running_models = ", ".join({p.get("name", "?") for p in processes}) if processes else "keine aktiv"

        msg = (
            f"Ollama: online @ {info.get('base_url')} | "
            f"Version: {version} | "
            f"Modelle: {model_count} | "
            f"Laufende Modelle: {running_models} | "
            f"{vram_str}"
        )
        self.statusBar().showMessage(msg)

    def _lock_window_size(self):
        """Fenstergröße aus Layout ableiten und dann fixieren."""
        self.adjustSize()
        self.setFixedSize(self.size())

    def init_sidebar(self):
        self.sidebar_dock = QDockWidget("Chats", self)
        self.sidebar_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.sidebar_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        self.sidebar = SidebarWidget(self.db, self)
        self.sidebar_dock.setWidget(self.sidebar)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock)

        # Connect Sidebar Signals
        self.sidebar.new_chat_clicked.connect(self.new_chat)
        self.sidebar.save_chat_clicked.connect(self.save_chat)
        self.sidebar.search_text_changed.connect(self.sidebar.update_chat_list)
        self.sidebar.chat_selected.connect(self.open_chat)
        
        # Connect File Explorer Signals
        self.sidebar.file_explorer.file_added_to_chat.connect(self.add_file_to_current_chat)
        self.sidebar.file_explorer.file_added_to_project.connect(self.add_file_to_project)

    def add_file_to_current_chat(self, path, name):
        if not self.chat_widget.chat_id:
            # Falls kein Chat offen ist, erstellen wir einen neuen
            chat_id = self.db.create_chat(f"Chat mit {name}")
            self.chat_widget.chat_id = chat_id
            self.sidebar.update_chat_list()

        # Typ der Ressource bestimmen (Datei vs. Verzeichnis)
        if os.path.isdir(path):
            file_type = "directory"
        elif os.path.isfile(path):
            file_type = "file"
        else:
            file_type = None

        file_id = self.db.get_or_create_file(path, name, file_type)
        self.db.add_file_to_chat(self.chat_widget.chat_id, file_id)
        self.chat_widget.add_message("system", f"Datei '{name}' wurde diesem Chat hinzugefügt.")
        self.show_chat_view()

    def add_file_to_project(self, path, name, project_id):
        if os.path.isdir(path):
            file_type = "directory"
        elif os.path.isfile(path):
            file_type = "file"
        else:
            file_type = None

        file_id = self.db.get_or_create_file(path, name, file_type)
        self.db.add_file_to_project(project_id, file_id)
        # Informiere Benutzer (einfaches Message Box oder Statusbar wäre gut, aber hier einfach Print/Log)
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Datei hinzugefügt", f"Datei '{name}' wurde dem Projekt hinzugefügt.")

    def new_chat(self):
        self.chat_widget.clear_chat()
        self.sidebar.chatListWidget.clearSelection()

    def save_chat(self):
        if not self.chat_widget.chat_id:
            return
            
        title, ok = QInputDialog.getText(self, "Chat speichern", "Titel für den Chat:", text=f"Chat {self.chat_widget.chat_id}")
        if ok and title:
            self.db.save_chat(self.chat_widget.chat_id, title)
            self.sidebar.update_chat_list()

    def open_chat(self, chat_id):
        self.chat_widget.chat_id = chat_id
        self.chat_widget.load_history()
        self.show_chat_view()

    def display_project(self, project_id):
        # Falls bereits ein ProjectChatListWidget existiert, entfernen wir es
        if self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
            
        self.project_chat_list_widget = ProjectChatListWidget(self.db, project_id, self.chat_widget, self)
        self.stacked_widget.addWidget(self.project_chat_list_widget)
        self.stacked_widget.setCurrentWidget(self.project_chat_list_widget)

    def show_chat_view(self):
        self.stacked_widget.setCurrentWidget(self.chat_widget)

    def show_command_center(self):
        self.command_center.refresh()
        self.command_center.refresh_theme(self.settings.theme)
        self.stacked_widget.setCurrentWidget(self.command_center)

    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        help_icon = QIcon(os.path.join(self.settings.icons_path, "help.svg"))
        help_action = QAction(help_icon, "Hilfe", self)
        help_action.setToolTip("Hilfe und Dokumentation öffnen")
        help_action.triggered.connect(self.open_help)
        toolbar.addAction(help_action)

        settings_icon = QIcon(os.path.join(self.settings.icons_path, "settings.svg"))
        settings_action = QAction(settings_icon, "Einstellungen", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

        agents_icon = QIcon(os.path.join(self.settings.icons_path, "model.svg"))
        agents_action = QAction(agents_icon, "Agenten verwalten (HR)", self)
        agents_action.triggered.connect(self.open_agent_manager)
        toolbar.addAction(agents_action)

        dashboard_icon = QIcon(os.path.join(self.settings.icons_path, "info.svg"))
        dashboard_action = QAction(dashboard_icon, "Kommandozentrale", self)
        dashboard_action.setToolTip("QA-Dashboard und App-Übersicht")
        dashboard_action.triggered.connect(self.show_command_center)
        toolbar.addAction(dashboard_action)

    def open_help(self):
        from app.help.help_window import HelpWindow
        win = HelpWindow(theme=self.settings.theme, parent=self)
        win.exec()

    def open_agent_manager(self):
        from app.gui.domains.control_center.agents_ui import AgentManagerDialog
        from app.core.models.registry import get_registry
        model_ids = [e.id for e in get_registry().list_all()]
        dialog = AgentManagerDialog(
            theme=self.settings.theme,
            model_ids=model_ids,
            parent=self,
        )
        dialog.agent_selected_for_chat.connect(self._on_agent_selected_for_chat)
        dialog.exec()

    def _on_agent_selected_for_chat(self, profile):
        """Agent wurde in der HR für Chat ausgewählt."""
        if self.chat_widget and self.chat_widget.header and self.chat_widget.header.agent_combo:
            idx = self.chat_widget.header.agent_combo.findData(profile.id)
            if idx >= 0:
                self.chat_widget.header.agent_combo.setCurrentIndex(idx)

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self.orchestrator, self)
        if dialog.exec():
            self.apply_theme()
            self.chat_widget.set_current_model(self.settings.model)
            self.chat_widget.temperature = self.settings.temperature
            self.chat_widget.max_tokens = self.settings.max_tokens
            self.chat_widget.set_icons()
            self.chat_widget._apply_routing_settings()
            self.chat_widget.refresh_prompt_backend()

    def apply_theme(self):
        self.setStyleSheet(get_stylesheet(self.settings.theme))
        self.chat_widget.refresh_theme()
        self.command_center.refresh_theme(self.settings.theme)

    def closeEvent(self, event):
        self.db.commit()
        # MainWindow schließt nicht mehr den Client direkt, das macht main()
        super().closeEvent(event)

async def main():
    warnings.warn(
        "app.main ist LEGACY. Nutze python main.py oder python -m app für die neue GUI.",
        DeprecationWarning,
        stacklevel=2,
    )
    # .env früh laden, damit OLLAMA_API_KEY für Cloud-Provider verfügbar ist
    from app.utils.env_loader import load_env
    from app.providers.cloud_ollama_provider import get_ollama_api_key
    load_env()

    app = QApplication(sys.argv)
    app.setApplicationName("ollama-desktop-chat")
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Infrastructure mit QSettings-Backend (GUI implementiert core-Abstraktion)
    from app.services.infrastructure import init_infrastructure
    from app.gui.qsettings_backend import create_qsettings_backend
    init_infrastructure(settings_backend=create_qsettings_backend())

    settings = AppSettings()
    raw_key = (settings.ollama_api_key or "").strip() or get_ollama_api_key()
    api_key = (raw_key or "").strip() or None

    client = OllamaClient()
    local_provider = LocalOllamaProvider(client=client)
    cloud_provider = CloudOllamaProvider(api_key=api_key)
    orchestrator = ModelOrchestrator(
        local_provider=local_provider,
        cloud_provider=cloud_provider,
    )
    win = MainWindow(client, orchestrator, settings=settings)
    win.show()

    try:
        # qasync context manager runs the loop until the application exits
        with loop:
            loop.run_forever()
    finally:
        await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(main())
