from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QMessageBox, QLabel)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class ProjectChatListWidget(QWidget):
    def __init__(self, db, project_id, chat_widget, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = project_id
        self.chat_widget = chat_widget
        
        # Get project name
        projects = self.db.list_projects()
        self.project_name = next((p[1] for p in projects if p[0] == project_id), "Unbekanntes Projekt")
        
        self.init_ui()

    def init_ui(self):
        self.setObjectName("projectChatListWidget")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

        # Header (Styling aus globalem Theme via #projectHeaderLabel)
        header_label = QLabel(f"Projekt: {self.project_name}")
        header_label.setObjectName("projectHeaderLabel")
        self.layout.addWidget(header_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.addChatBtn = QPushButton("Chat hinzufügen")
        self.addChatBtn.setObjectName("addChatBtn")
        self.addChatBtn.setIcon(QIcon(":/icons/add_chat.svg"))
        
        self.removeChatBtn = QPushButton("Chat entfernen")
        self.removeChatBtn.setObjectName("removeChatBtn")
        self.removeChatBtn.setIcon(QIcon(":/icons/remove_chat.svg"))
        
        self.backBtn = QPushButton("← Zurück zum Chat")
        self.backBtn.setObjectName("backBtn")
        self.backBtn.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(self.addChatBtn)
        btn_layout.addWidget(self.removeChatBtn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.backBtn)
        self.layout.addLayout(btn_layout)

        # Chat list
        self.chatListWidget = QListWidget()
        self.chatListWidget.setObjectName("chatListWidget")
        self.layout.addWidget(self.chatListWidget)

        # Signals
        self.addChatBtn.clicked.connect(self.add_chat_to_project)
        self.removeChatBtn.clicked.connect(self.remove_chat_from_project)
        self.chatListWidget.itemDoubleClicked.connect(self.load_chat)
        self.backBtn.clicked.connect(self.on_back)

        self.refresh_chat_list()

    def refresh_chat_list(self):
        self.chatListWidget.clear()
        chats = self.db.list_chats_of_project(self.project_id)
        for chat_id, title, created in chats:
            item = QListWidgetItem(f"{title} ({created})")
            item.setData(Qt.ItemDataRole.UserRole, chat_id)
            self.chatListWidget.addItem(item)

    def add_chat_to_project(self):
        # Wir brauchen die current_chat_id vom ChatWidget
        chat_id = self.chat_widget.chat_id
        if chat_id is None:
            QMessageBox.warning(self, "Kein Chat", "Bitte erst einen Chat starten oder öffnen.")
            return
        self.db.add_chat_to_project(self.project_id, chat_id)
        self.refresh_chat_list()

    def remove_chat_from_project(self):
        item = self.chatListWidget.currentItem()
        if not item: return
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        self.db.remove_chat_from_project(self.project_id, chat_id)
        self.refresh_chat_list()

    def load_chat(self, item):
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        self.on_back()
        # MainWindow Methode aufrufen (via parent)
        parent = self.parent()
        while parent:
            if hasattr(parent, 'open_chat'):
                parent.open_chat(chat_id)
                break
            parent = parent.parent()

    def on_back(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, 'show_chat_view'):
                parent.show_chat_view()
                break
            parent = parent.parent()
