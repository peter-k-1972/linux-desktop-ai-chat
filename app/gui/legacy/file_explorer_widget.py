import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeView, QFileSystemModel, 
                             QMenu, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt, QDir, Signal

class FileExplorerWidget(QWidget):
    file_added_to_chat = Signal(str, str) # path, name
    file_added_to_project = Signal(str, str, int) # path, name, project_id

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        
        self.tree = QTreeView()
        self.tree.setObjectName("fileExplorerTree")
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.homePath()))
        
        # Nur Namen anzeigen, andere Spalten verstecken
        for i in range(1, self.model.columnCount()):
            self.tree.hideColumn(i)
            
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.tree)

    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return

        path = self.model.filePath(index)
        name = self.model.fileName(index)
        is_dir = self.model.isDir(index)

        menu = QMenu()
        
        add_to_chat_action = menu.addAction("Dem aktuellen Chat hinzufügen")
        add_to_project_menu = menu.addMenu("Einem Projekt zuweisen")
        
        projects = self.db.list_projects()
        project_actions = {}
        for p_id, p_name, _ in projects:
            action = add_to_project_menu.addAction(p_name)
            project_actions[action] = p_id

        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        
        if action == add_to_chat_action:
            self.file_added_to_chat.emit(path, name)
        elif action in project_actions:
            self.file_added_to_project.emit(path, name, project_actions[action])
