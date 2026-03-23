"""
Catalog of conceptual node types (MVP): metadata only, no execution semantics.

Drag-and-drop and execution will consult this registry for ports and grouping.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AiNodeTypeMeta:
    type_id: str
    display_name: str
    group: str
    default_title: str


_AI_NODE_TYPES: tuple[AiNodeTypeMeta, ...] = (
    # Inputs
    AiNodeTypeMeta("prompt_input", "PromptInputNode", "Inputs", "Prompt"),
    AiNodeTypeMeta("file_input", "FileInputNode", "Inputs", "File"),
    AiNodeTypeMeta("context_input", "ContextInputNode", "Inputs", "Context"),
    # Runtime
    AiNodeTypeMeta("agent", "AgentNode", "Runtime", "Agent"),
    AiNodeTypeMeta("model", "ModelNode", "Runtime", "Model"),
    AiNodeTypeMeta("tool", "ToolNode", "Runtime", "Tool"),
    AiNodeTypeMeta("memory", "MemoryNode", "Runtime", "Memory"),
    # Knowledge
    AiNodeTypeMeta("rag", "RAGNode", "Knowledge", "RAG"),
    AiNodeTypeMeta("retriever", "RetrieverNode", "Knowledge", "Retriever"),
    AiNodeTypeMeta("embedding", "EmbeddingNode", "Knowledge", "Embedding"),
    # Logic
    AiNodeTypeMeta("condition", "ConditionNode", "Logic", "Condition"),
    AiNodeTypeMeta("router", "RouterNode", "Logic", "Router"),
    AiNodeTypeMeta("merge", "MergeNode", "Logic", "Merge"),
    # Outputs
    AiNodeTypeMeta("chat_output", "ChatOutputNode", "Outputs", "Chat Out"),
    AiNodeTypeMeta("file_output", "FileOutputNode", "Outputs", "File Out"),
    AiNodeTypeMeta("log_output", "LogOutputNode", "Outputs", "Log Out"),
)


def all_node_types() -> tuple[AiNodeTypeMeta, ...]:
    return _AI_NODE_TYPES


def meta_for_type(type_id: str) -> AiNodeTypeMeta | None:
    for m in _AI_NODE_TYPES:
        if m.type_id == type_id:
            return m
    return None
