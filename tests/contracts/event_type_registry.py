"""
EventType Contract Registry – Single Source of Truth für EventType-Werte.

Wird von Contract-Tests und Meta-Tests genutzt.
Bei neuem EventType: Hier eintragen + Contract-Test + docs/qa/REGRESSION_CATALOG.md.
"""

from app.debug.agent_event import EventType

# Erwartete EventType-Werte (Stabilität für Debug-Store, UI, Metrics)
EVENT_TYPE_CONTRACT = {
    EventType.TASK_CREATED: "task_created",
    EventType.TASK_STARTED: "task_started",
    EventType.TASK_COMPLETED: "task_completed",
    EventType.TASK_FAILED: "task_failed",
    EventType.AGENT_SELECTED: "agent_selected",
    EventType.MODEL_CALL: "model_call",
    EventType.TOOL_EXECUTION: "tool_execution",
    EventType.RAG_RETRIEVAL_FAILED: "rag_retrieval_failed",
}
