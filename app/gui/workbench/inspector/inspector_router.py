"""
Selects an inspector widget for the active canvas tab.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.gui.workbench.ai_canvas.ai_canvas_widget import AiFlowEditorCanvas
from app.gui.workbench.canvas.canvas_base import (
    AgentEditorCanvas,
    ChatCanvas,
    FileViewerCanvas,
    StubFeatureCanvas,
    WorkflowEditorCanvas,
    WorkbenchCanvasBase,
)
from app.gui.workbench.ui import SectionCard
from app.gui.workbench.workflows.agent_test_canvas import AgentTestCanvas
from app.gui.workbench.workflows.knowledge_base_canvas import KnowledgeBaseWorkflowCanvas
from app.gui.workbench.workflows.model_compare_canvas import ModelCompareCanvas
from app.gui.workbench.workflows.prompt_dev_canvas import PromptDevelopmentCanvas
from app.gui.workbench.workflows.workflow_builder_canvas import WorkflowBuilderCanvas


def _hint_label() -> QLabel:
    h = QLabel(
        "When domain panels are embedded, this area will show live metadata, "
        "runtime state, and editable configuration."
    )
    h.setObjectName("workbenchInspectorHint")
    h.setWordWrap(True)
    return h


def _inspector_card_column(
    cards: list[tuple[str, str]],
    parent: QWidget | None = None,
) -> QWidget:
    page = QWidget(parent)
    lay = QVBoxLayout(page)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)
    for title, body in cards:
        card = SectionCard(title)
        body_lbl = QLabel(body)
        body_lbl.setObjectName("workbenchInspectorBody")
        body_lbl.setWordWrap(True)
        card.body_layout().addWidget(body_lbl)
        lay.addWidget(card)
    lay.addWidget(_hint_label())
    lay.addStretch(1)
    return page


def _page_with_card(card_title: str, body: str, parent: QWidget | None = None) -> QWidget:
    page = QWidget(parent)
    lay = QVBoxLayout(page)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)
    card = SectionCard(card_title)
    body_lbl = QLabel(body)
    body_lbl.setObjectName("workbenchInspectorBody")
    body_lbl.setWordWrap(True)
    card.body_layout().addWidget(body_lbl)
    lay.addWidget(card)
    lay.addWidget(_hint_label())
    lay.addStretch(1)
    return page


class AgentInspector(QWidget):
    def __init__(self, canvas: AgentEditorCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        body = (
            f"Agent id: {canvas.agent_id!r}\n\n"
            "This placeholder will be replaced with tools, prompts, and run controls."
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(_page_with_card("Agent", body, self))


class WorkflowInspector(QWidget):
    def __init__(self, canvas: WorkflowEditorCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        body = f"Workflow id: {canvas.workflow_id!r}\n\nSchedules, inputs, and run history will appear here."
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(_page_with_card("Workflow", body, self))


class ChatInspector(QWidget):
    def __init__(self, canvas: ChatCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        body = f"Session: {canvas.session_key!r}\n\nModel, context, and attachments will surface here."
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(_page_with_card("Chat", body, self))


class FileInspector(QWidget):
    def __init__(self, canvas: FileViewerCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        body = f"Path:\n{canvas.file_path}"
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(_page_with_card("File", body, self))


class GenericInspector(QWidget):
    def __init__(self, canvas: WorkbenchCanvasBase, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        body = f"Canvas kind: {canvas.canvas_kind.name}"
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(_page_with_card("Overview", body, self))


class StubFeatureInspector(QWidget):
    def __init__(self, canvas: StubFeatureCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        body = (
            f"Route: {canvas.feature_key!r}\n\n"
            "This stub opens from the explorer until the real workspace view is embedded."
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(_page_with_card("Feature", body, self))


class AgentTestInspector(QWidget):
    def __init__(self, canvas: AgentTestCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(
            _inspector_card_column(
                [
                    (
                        "Configuration",
                        f"Agent: {canvas.agent_id!r}\nModel, tool policy, and safety rails will bind here.",
                    ),
                    ("Runtime", "Last run state, latency, and error channel (stub)."),
                    ("Context", "Token budget, RAG sources, and session variables (stub)."),
                    ("Tools", "Callable tools and JSON schemas (stub)."),
                    ("Memory", "Long-term recall / summary slots (stub)."),
                ],
                parent=self,
            )
        )


class KnowledgeBaseInspector(QWidget):
    def __init__(self, canvas: KnowledgeBaseWorkflowCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(
            _inspector_card_column(
                [
                    (
                        "Embedding model",
                        "Choose embedding model and dimensions; persisted per knowledge base (stub).",
                    ),
                    (
                        "Chunking strategy",
                        "Size, overlap, and document-type presets (stub).",
                    ),
                    (
                        "Retriever config",
                        "Top-k, MMR, filters, and hybrid sparse+dense toggles (stub).",
                    ),
                ],
                parent=self,
            )
        )


class PromptDevInspector(QWidget):
    def __init__(self, canvas: PromptDevelopmentCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(
            _inspector_card_column(
                [
                    ("Draft", f"Prompt id: {canvas.prompt_id!r}"),
                    ("Model", "Primary model id and fallbacks (stub)."),
                    ("Temperature", "Sampling temperature and top-p (stub)."),
                    ("Max tokens", "Output cap and stop sequences (stub)."),
                    ("Context policy", "How much history / RAG to inject per test (stub)."),
                ],
                parent=self,
            )
        )


class ModelCompareInspector(QWidget):
    def __init__(self, canvas: ModelCompareCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        n = canvas.model_column_count()
        lay.addWidget(
            _inspector_card_column(
                [
                    ("Comparison", f"{n} model column(s). Run Comparison fills responses in parallel (stub)."),
                    ("Results", "Export as Markdown/JSON once runs complete (stub)."),
                ],
                parent=self,
            )
        )


class WorkflowBuilderInspector(QWidget):
    def __init__(self, canvas: WorkflowBuilderCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        doc = canvas.graph_document()
        nid = canvas.selected_node_id()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        c_graph = SectionCard("Workflow graph")
        g1 = QLabel(
            f"{len(doc.nodes)} nodes · {len(doc.edges)} edges · key {canvas.workflow_key!r}\n"
            "Validate checks structure; Run will execute via orchestrator (stub)."
        )
        g1.setObjectName("workbenchInspectorBody")
        g1.setWordWrap(True)
        c_graph.body_layout().addWidget(g1)
        lay.addWidget(c_graph)

        c_sel = SectionCard("Selection")
        sel_txt = f"Selected node id:\n{nid}" if nid else "No node selected — click a block on the canvas."
        g2 = QLabel(sel_txt)
        g2.setObjectName("workbenchInspectorBody")
        g2.setWordWrap(True)
        c_sel.body_layout().addWidget(g2)
        lay.addWidget(c_sel)

        lay.addWidget(_hint_label())
        lay.addStretch(1)


class AiFlowInspector(QWidget):
    def __init__(self, canvas: AiFlowEditorCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        doc = canvas.graph_document()
        nid = canvas.selected_node_id()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        c_graph = SectionCard("Graph")
        g1 = QLabel(f"{len(doc.nodes)} nodes · {len(doc.edges)} edges (edges are data-only in MVP).")
        g1.setObjectName("workbenchInspectorBody")
        g1.setWordWrap(True)
        c_graph.body_layout().addWidget(g1)
        lay.addWidget(c_graph)

        c_sel = SectionCard("Selection")
        sel_txt = f"Selected node id:\n{nid}" if nid else "No node selected — click a block on the canvas."
        g2 = QLabel(sel_txt)
        g2.setObjectName("workbenchInspectorBody")
        g2.setWordWrap(True)
        c_sel.body_layout().addWidget(g2)
        lay.addWidget(c_sel)

        lay.addWidget(_hint_label())
        lay.addStretch(1)


class InspectorRouter:
    """Builds a fresh inspector widget for the given canvas (panel owns lifecycle)."""

    def inspector_for_canvas(
        self, canvas: WorkbenchCanvasBase | None, parent: QWidget | None = None
    ) -> QWidget | None:
        if canvas is None:
            return None
        if isinstance(canvas, AgentTestCanvas):
            return AgentTestInspector(canvas, parent=parent)
        if isinstance(canvas, AgentEditorCanvas):
            return AgentInspector(canvas, parent=parent)
        if isinstance(canvas, KnowledgeBaseWorkflowCanvas):
            return KnowledgeBaseInspector(canvas, parent=parent)
        if isinstance(canvas, PromptDevelopmentCanvas):
            return PromptDevInspector(canvas, parent=parent)
        if isinstance(canvas, ModelCompareCanvas):
            return ModelCompareInspector(canvas, parent=parent)
        if isinstance(canvas, WorkflowBuilderCanvas):
            return WorkflowBuilderInspector(canvas, parent=parent)
        if isinstance(canvas, WorkflowEditorCanvas):
            return WorkflowInspector(canvas, parent=parent)
        if isinstance(canvas, ChatCanvas):
            return ChatInspector(canvas, parent=parent)
        if isinstance(canvas, FileViewerCanvas):
            return FileInspector(canvas, parent=parent)
        if isinstance(canvas, StubFeatureCanvas):
            return StubFeatureInspector(canvas, parent=parent)
        if isinstance(canvas, AiFlowEditorCanvas):
            return AiFlowInspector(canvas, parent=parent)
        return GenericInspector(canvas, parent=parent)
