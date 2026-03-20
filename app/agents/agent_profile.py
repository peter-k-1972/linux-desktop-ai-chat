"""
Agent Profile – vollständiges Profil eines Agenten.

Basis für Verwaltung, Chat-Integration und spätere Erweiterungen
(RAG, Tools, ComfyUI, Multimedia).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.agents.departments import Department, department_from_str
from app.core.models.roles import ModelRole


class AgentStatus(str, Enum):
    """Status eines Agenten."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


@dataclass
class AgentProfile:
    """
    Vollständiges Agentenprofil mit allen verwaltbaren Metadaten.
    """

    id: Optional[str] = None
    project_id: Optional[int] = None
    name: str = ""
    display_name: str = ""
    slug: str = ""
    short_description: str = ""
    long_description: str = ""
    department: str = "general"
    role: str = ""
    status: str = "active"
    avatar_path: Optional[str] = None
    avatar_id: Optional[str] = None
    assigned_model: Optional[str] = None
    assigned_model_role: Optional[str] = None
    system_prompt: str = ""
    capabilities: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    knowledge_spaces: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Editor config
    memory_config: Optional[str] = None  # e.g. "short_term", "sliding_window", JSON
    limits_config: Optional[str] = None  # e.g. max_tokens, rate limits, JSON

    # Optional / vorbereitet
    personality_style: Optional[str] = None
    response_style: Optional[str] = None
    escalation_policy: Optional[str] = None
    fallback_model: Optional[str] = None
    ui_color: Optional[str] = None
    theme_hint: Optional[str] = None
    visibility_in_chat: bool = True
    priority: int = 0
    cloud_allowed: bool = False

    # Media / ComfyUI vorbereitung
    workflow_bindings: List[str] = field(default_factory=list)
    external_command_hooks: List[str] = field(default_factory=list)
    media_pipeline_capabilities: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)  # image, video, audio, etc.

    def get_department_enum(self) -> Optional[Department]:
        """Liefert die Department-Enum oder None."""
        return department_from_str(self.department)

    def get_model_role_enum(self) -> Optional[ModelRole]:
        """Liefert die ModelRole-Enum oder None."""
        if not self.assigned_model_role:
            return None
        try:
            return ModelRole(self.assigned_model_role)
        except ValueError:
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert das Profil für Persistenz."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "display_name": self.display_name or self.name,
            "slug": self.slug or self._slugify(self.name),
            "short_description": self.short_description,
            "long_description": self.long_description,
            "department": self.department,
            "role": self.role,
            "status": self.status,
            "avatar_path": self.avatar_path,
            "avatar_id": self.avatar_id,
            "assigned_model": self.assigned_model,
            "assigned_model_role": self.assigned_model_role,
            "system_prompt": self.system_prompt,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "knowledge_spaces": self.knowledge_spaces,
            "tags": self.tags,
            "created_at": self._dt_to_iso(self.created_at),
            "updated_at": self._dt_to_iso(self.updated_at),
            "memory_config": self.memory_config,
            "limits_config": self.limits_config,
            "personality_style": self.personality_style,
            "response_style": self.response_style,
            "escalation_policy": self.escalation_policy,
            "fallback_model": self.fallback_model,
            "ui_color": self.ui_color,
            "theme_hint": self.theme_hint,
            "visibility_in_chat": self.visibility_in_chat,
            "priority": self.priority,
            "cloud_allowed": self.cloud_allowed,
            "workflow_bindings": self.workflow_bindings,
            "external_command_hooks": self.external_command_hooks,
            "media_pipeline_capabilities": self.media_pipeline_capabilities,
            "output_types": self.output_types,
        }

    @staticmethod
    def _slugify(text: str) -> str:
        import re

        t = (text or "").strip().lower()
        t = re.sub(r"[^\w\s-]", "", t)
        t = re.sub(r"[-\s]+", "_", t)
        return t[:64] or "agent"

    @staticmethod
    def _dt_to_iso(dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentProfile":
        """Deserialisiert aus einem Dict."""
        created = cls._parse_dt(data.get("created_at"))
        updated = cls._parse_dt(data.get("updated_at"))

        def _list(val) -> List[str]:
            if val is None:
                return []
            if isinstance(val, list):
                return [str(x) for x in val]
            if isinstance(val, str):
                return [x.strip() for x in val.split(",") if x.strip()]
            return []

        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            name=data.get("name", ""),
            display_name=data.get("display_name", ""),
            slug=data.get("slug", ""),
            short_description=data.get("short_description", ""),
            long_description=data.get("long_description", ""),
            department=data.get("department", "general"),
            role=data.get("role", ""),
            status=data.get("status", "active"),
            avatar_path=data.get("avatar_path"),
            avatar_id=data.get("avatar_id"),
            assigned_model=data.get("assigned_model"),
            assigned_model_role=data.get("assigned_model_role"),
            system_prompt=data.get("system_prompt", ""),
            capabilities=_list(data.get("capabilities")),
            tools=_list(data.get("tools")),
            knowledge_spaces=_list(data.get("knowledge_spaces")),
            tags=_list(data.get("tags")),
            created_at=created,
            updated_at=updated,
            memory_config=data.get("memory_config"),
            limits_config=data.get("limits_config"),
            personality_style=data.get("personality_style"),
            response_style=data.get("response_style"),
            escalation_policy=data.get("escalation_policy"),
            fallback_model=data.get("fallback_model"),
            ui_color=data.get("ui_color"),
            theme_hint=data.get("theme_hint"),
            visibility_in_chat=data.get("visibility_in_chat", True),
            priority=int(data.get("priority", 0) or 0),
            cloud_allowed=bool(data.get("cloud_allowed", False)),
            workflow_bindings=_list(data.get("workflow_bindings")),
            external_command_hooks=_list(data.get("external_command_hooks")),
            media_pipeline_capabilities=_list(data.get("media_pipeline_capabilities")),
            output_types=_list(data.get("output_types")),
        )

    @staticmethod
    def _parse_dt(val) -> Optional[datetime]:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        s = str(val).replace("Z", "+00:00")
        try:
            if "T" in s or "+" in s:
                return datetime.fromisoformat(s)
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return None

    @property
    def is_active(self) -> bool:
        return self.status == AgentStatus.ACTIVE.value

    @property
    def effective_display_name(self) -> str:
        return self.display_name or self.name or "Unbenannt"
