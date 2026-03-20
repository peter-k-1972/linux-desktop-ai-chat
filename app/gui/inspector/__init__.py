"""Inspector – kontextabhängiger rechter Bereich."""

from app.gui.inspector.inspector_host import InspectorHost
from app.gui.inspector.chat_context_inspector import ChatContextInspector
from app.gui.inspector.agent_tasks_inspector import AgentTasksInspector
from app.gui.inspector.knowledge_inspector import KnowledgeInspector
from app.gui.inspector.prompt_studio_inspector import PromptStudioInspector

__all__ = [
    "InspectorHost",
    "ChatContextInspector",
    "AgentTasksInspector",
    "KnowledgeInspector",
    "PromptStudioInspector",
]
