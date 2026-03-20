"""
Service Layer – zentrale Schicht zwischen GUI und Backend.

Die GUI spricht ausschließlich mit Services, nicht mit Providern, DB oder Chroma direkt.

Services:
- ChatService: Sessions, Nachrichten senden, Chat-Kontext
- ModelService: verfügbare Modelle, Standardmodell, Modellstatus
- ProviderService: Providerliste, Ollama-Status, Erreichbarkeit
- KnowledgeService: Collections, Quellen, Retrieval
- AgentService: Agentenliste, Agent starten, Agentstatus
- TopicService: Topics pro Projekt
- ProjectService: Projekte, Zuordnungen, Statistiken
- QAGovernanceService: QA-Artefakte (Test Inventory, Coverage, Incidents)
"""

from app.services.result import ServiceResult, OperationStatus
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.model_service import ModelService, get_model_service
from app.services.provider_service import ProviderService, get_provider_service
from app.services.knowledge_service import KnowledgeService, get_knowledge_service
from app.services.agent_service import AgentService, get_agent_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.qa_governance_service import (
    QAGovernanceService,
    get_qa_governance_service,
)
from app.services.pipeline_service import (
    get_pipeline_service,
    set_pipeline_service,
)

__all__ = [
    "ServiceResult",
    "OperationStatus",
    "ChatService",
    "get_chat_service",
    "set_chat_service",
    "ModelService",
    "get_model_service",
    "ProviderService",
    "get_provider_service",
    "KnowledgeService",
    "get_knowledge_service",
    "AgentService",
    "get_agent_service",
    "TopicService",
    "get_topic_service",
    "set_topic_service",
    "ProjectService",
    "get_project_service",
    "set_project_service",
    "QAGovernanceService",
    "get_qa_governance_service",
    "get_pipeline_service",
    "set_pipeline_service",
]
