from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QListWidget, QListWidgetItem, QLabel, QFrame,
                             QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
                             QTabWidget)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal
from .file_explorer_widget import FileExplorerWidget

class SidebarWidget(QWidget):
    new_chat_clicked = Signal()
    save_chat_clicked = Signal()
    search_text_changed = Signal(str)
    chat_selected = Signal(int)

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setObjectName("sidebarWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(15)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("sidebarTabs")
        # Tab-Styling kommt aus dem globalen Theme (get_stylesheet)
        layout.addWidget(self.tabs)

        # Tab 1: Chats & Projekte
        self.workspace_tab = QWidget()
        workspace_layout = QVBoxLayout(self.workspace_tab)
        workspace_layout.setContentsMargins(8, 8, 8, 8)
        workspace_layout.setSpacing(10)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.newChatBtn = QPushButton("  Neuer Chat")
        self.newChatBtn.setObjectName("newChatBtn")
        self.newChatBtn.setIcon(QIcon(":/icons/new.svg"))
        self.newChatBtn.setMinimumHeight(44)
        
        self.saveChatBtn = QPushButton()
        self.saveChatBtn.setObjectName("saveChatBtn")
        self.saveChatBtn.setIcon(QIcon(":/icons/save.svg"))
        self.saveChatBtn.setToolTip("Chat speichern")
        self.saveChatBtn.setFixedSize(44, 44)
        
        btn_layout.addWidget(self.newChatBtn, stretch=1)
        btn_layout.addWidget(self.saveChatBtn)
        workspace_layout.addLayout(btn_layout)

        # Search
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        self.searchEdit = QLineEdit()
        self.searchEdit.setObjectName("searchEdit")
        self.searchEdit.setPlaceholderText("Chats suchen...")
        self.searchEdit.setMinimumHeight(40)
        
        self.searchBtn = QPushButton()
        self.searchBtn.setObjectName("searchBtn")
        self.searchBtn.setIcon(QIcon(":/icons/search.svg"))
        self.searchBtn.setFixedSize(40, 40)
        
        search_layout.addWidget(self.searchEdit)
        search_layout.addWidget(self.searchBtn)
        workspace_layout.addLayout(search_layout)

        # Chat List
        self.chatListWidget = QListWidget()
        self.chatListWidget.setObjectName("chatListWidget")
        chat_label = QLabel("Chats")
        chat_label.setStyleSheet("font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 10px;")
        workspace_layout.addWidget(chat_label)
        workspace_layout.addWidget(self.chatListWidget)

        # Project Toolbar
        project_header_layout = QHBoxLayout()
        project_label = QLabel("Projekte")
        project_label.setStyleSheet("font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 10px;")
        project_header_layout.addWidget(project_label)
        project_header_layout.addStretch()
        
        self.newProjectBtn = QPushButton()
        self.newProjectBtn.setObjectName("newProjectBtn")
        self.newProjectBtn.setFixedSize(28, 28)
        self.newProjectBtn.setIcon(QIcon(":/icons/new_project.svg"))
        self.newProjectBtn.setToolTip("Neues Projekt")
        
        self.renameProjectBtn = QPushButton()
        self.renameProjectBtn.setObjectName("renameProjectBtn")
        self.renameProjectBtn.setFixedSize(28, 28)
        self.renameProjectBtn.setIcon(QIcon(":/icons/rename.svg"))
        self.renameProjectBtn.setToolTip("Projekt umbenennen")
        
        self.deleteProjectBtn = QPushButton()
        self.deleteProjectBtn.setObjectName("deleteProjectBtn")
        self.deleteProjectBtn.setFixedSize(28, 28)
        self.deleteProjectBtn.setIcon(QIcon(":/icons/delete.svg"))
        self.deleteProjectBtn.setToolTip("Projekt löschen")
        
        project_header_layout.addWidget(self.newProjectBtn)
        project_header_layout.addWidget(self.renameProjectBtn)
        project_header_layout.addWidget(self.deleteProjectBtn)
        workspace_layout.addLayout(project_header_layout)

        # Project Search
        project_search_layout = QHBoxLayout()
        self.projectSearchEdit = QLineEdit()
        self.projectSearchEdit.setObjectName("projectSearchEdit")
        self.projectSearchEdit.setPlaceholderText("Projekte suchen...")
        self.projectSearchEdit.setMinimumHeight(34)
        
        self.projectSearchBtn = QPushButton()
        self.projectSearchBtn.setObjectName("projectSearchBtn")
        self.projectSearchBtn.setIcon(QIcon(":/icons/search.svg"))
        self.projectSearchBtn.setFixedSize(34, 34)
        
        project_search_layout.addWidget(self.projectSearchEdit)
        project_search_layout.addWidget(self.projectSearchBtn)
        workspace_layout.addLayout(project_search_layout)

        # Project Tree
        self.projectTreeWidget = QTreeWidget()
        self.projectTreeWidget.setObjectName("projectTreeWidget")
        self.projectTreeWidget.setHeaderHidden(True)
        workspace_layout.addWidget(self.projectTreeWidget)

        self.tabs.addTab(self.workspace_tab, "Workspace")

        # Tab 2: Dateien
        self.file_explorer = FileExplorerWidget(self.db)
        self.tabs.addTab(self.file_explorer, "Dateien")

        # Signals
        self.newChatBtn.clicked.connect(self.new_chat_clicked.emit)
        self.saveChatBtn.clicked.connect(self.save_chat_clicked.emit)
        self.searchEdit.textChanged.connect(self.search_text_changed.emit)
        self.searchBtn.clicked.connect(lambda: self.search_text_changed.emit(self.searchEdit.text()))
        self.chatListWidget.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.newProjectBtn.clicked.connect(self.on_new_project)
        self.renameProjectBtn.clicked.connect(self.on_rename_project)
        self.deleteProjectBtn.clicked.connect(self.on_delete_project)
        self.projectSearchBtn.clicked.connect(lambda: self.refresh_project_tree(self.projectSearchEdit.text()))
        self.projectSearchEdit.textChanged.connect(self.refresh_project_tree)
        self.projectTreeWidget.itemDoubleClicked.connect(self.on_project_selected)

        self.update_chat_list()
        self.refresh_project_tree()

    def on_new_project(self):
        name, ok = QInputDialog.getText(self, "Neues Projekt", "Projektname:")
        if ok and name:
            self.db.create_project(name)
            self.refresh_project_tree()

    def on_rename_project(self):
        item = self.projectTreeWidget.currentItem()
        if not item: return
        project_id = item.data(0, Qt.ItemDataRole.UserRole)
        new_name, ok = QInputDialog.getText(self, "Projekt umbenennen", "Neuer Name:", text=item.text(0))
        if ok and new_name:
            self.db.rename_project(project_id, new_name)
            self.refresh_project_tree()

    def on_delete_project(self):
        item = self.projectTreeWidget.currentItem()
        if not item: return
        project_id = item.data(0, Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Projekt löschen",
                                     f"Projekt '{item.text(0)}' und alle seine Chat-Zuweisungen löschen?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_project(project_id)
            self.refresh_project_tree()

    def on_project_selected(self, item, column):
        project_id = item.data(0, Qt.ItemDataRole.UserRole)
        # Wir nehmen an, dass MainWindow eine Methode display_project hat
        # Da SidebarWidget oft in einem QDockWidget steckt, müssen wir evtl. höher suchen
        parent = self.parent()
        while parent:
            if hasattr(parent, 'display_project'):
                parent.display_project(project_id)
                break
            parent = parent.parent()

    def refresh_project_tree(self, filter_text=""):
        self.projectTreeWidget.clear()
        projects = self.db.list_projects(filter_text)
        for p_id, name, created in projects:
            node = QTreeWidgetItem([name])
            node.setData(0, Qt.ItemDataRole.UserRole, p_id)
            self.projectTreeWidget.addTopLevelItem(node)

    def _on_item_double_clicked(self, item):
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        self.chat_selected.emit(chat_id)

    def update_chat_list(self, filter_text=""):
        chats = self.db.list_chats(filter_text)
        self.chatListWidget.clear()
        for chat in chats:
            item = QListWidgetItem(f"{chat['title']}")
            # Optional: Datum hinzufügen
            # item = QListWidgetItem(f"{chat['title']} ({chat['created_at']})")
            item.setData(Qt.ItemDataRole.UserRole, chat['id'])
            self.chatListWidget.addItem(item)
