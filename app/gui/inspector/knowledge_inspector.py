"""KnowledgeInspector – Inspector-Inhalt für Knowledge / RAG."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class KnowledgeInspector(QWidget):
    """Inspector für Knowledge: Projekt, Collection, Quelle, Status, Retrieval."""

    def __init__(
        self,
        space: str = "(keine)",
        source: str = "(keine)",
        source_name: str | None = None,
        source_type: str | None = None,
        source_status: str | None = None,
        chunk_count: int = 0,
        last_query: str = "",
        project_name: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("knowledgeInspector")
        self._space = space
        self._source = source
        self._source_name = source_name
        self._source_type = source_type
        self._source_status = source_status
        self._chunk_count = chunk_count
        self._last_query = last_query
        self._project_name = project_name
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        if self._project_name:
            group_proj = QGroupBox("Projekt")
            group_proj.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl_proj = QVBoxLayout(group_proj)
            lbl_proj = QLabel(self._project_name)
            lbl_proj.setStyleSheet("color: #6b7280; font-size: 12px;")
            gl_proj.addWidget(lbl_proj)
            layout.addWidget(group_proj)

        group_space = QGroupBox("Collection")
        group_space.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        gl = QVBoxLayout(group_space)
        lbl = QLabel(self._space)
        lbl.setStyleSheet("color: #6b7280; font-size: 12px;")
        lbl.setWordWrap(True)
        gl.addWidget(lbl)
        layout.addWidget(group_space)

        group_source = QGroupBox("Ausgewählte Quelle")
        group_source.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        gl2 = QVBoxLayout(group_source)
        name_str = self._source_name or "(keine)"
        lbl_name = QLabel(f"Name: {name_str}")
        lbl_name.setStyleSheet("color: #6b7280; font-size: 12px;")
        gl2.addWidget(lbl_name)
        if self._source_type:
            lbl_type = QLabel(f"Typ: {self._source_type}")
            lbl_type.setStyleSheet("color: #6b7280; font-size: 12px;")
            gl2.addWidget(lbl_type)
        if self._source_status:
            lbl_status = QLabel(f"Status: {self._source_status}")
            lbl_status.setStyleSheet("color: #6b7280; font-size: 12px;")
            gl2.addWidget(lbl_status)
        path_label = QLabel(f"Pfad: {self._source}")
        path_label.setWordWrap(True)
        path_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        gl2.addWidget(path_label)
        layout.addWidget(group_source)

        group_retrieval = QGroupBox("Letzter Retrieval")
        group_retrieval.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        gl3 = QVBoxLayout(group_retrieval)
        query_text = self._last_query or "(keine Anfrage)"
        lbl3 = QLabel(f"Query: {query_text}")
        lbl3.setStyleSheet("color: #6b7280; font-size: 12px;")
        lbl3.setWordWrap(True)
        gl3.addWidget(lbl3)
        lbl4 = QLabel(f"Treffer: {self._chunk_count}")
        lbl4.setStyleSheet("color: #6b7280; font-size: 12px;")
        gl3.addWidget(lbl4)
        layout.addWidget(group_retrieval)

        layout.addStretch()
