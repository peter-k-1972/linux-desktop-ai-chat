"""
Agent Router – weist Tasks den passenden Agenten zu.

Routing basiert auf:
- Department (planning, research, development, media, automation, system)
- Capabilities
- assigned_model_role
- tool_hint des Tasks
"""

import logging
from typing import Dict, List, Optional

from app.agents.agent_profile import AgentProfile
from app.agents.agent_registry import AgentRegistry, get_agent_registry
from app.agents.departments import Department, department_from_str
from app.agents.task import Task

logger = logging.getLogger(__name__)

# Mapping: tool_hint / keyword -> Department
TOOL_HINT_TO_DEPARTMENT: Dict[str, str] = {
    "research": Department.RESEARCH.value,
    "code": Department.DEVELOPMENT.value,
    "image": Department.MEDIA.value,
    "audio": Department.MEDIA.value,
    "video": Department.MEDIA.value,
    "thumbnail": Department.MEDIA.value,
    "thumbnail_generator": Department.MEDIA.value,
    "comfyui_render": Department.AUTOMATION.value,
    "audio_pipeline": Department.MEDIA.value,
    "video_pipeline": Department.MEDIA.value,
    "media_planning": Department.MEDIA.value,
    "knowledge": Department.RESEARCH.value,
    "planning": Department.PLANNING.value,
}

# Mapping: tool_hint -> bevorzugter Agent-Slug
TOOL_HINT_TO_SLUG: Dict[str, str] = {
    "research": "research_agent",
    "code": "code_agent",
    "image": "image_agent",
    "audio": "voice_agent",
    "video": "video_agent",
    "thumbnail": "image_agent",
    "thumbnail_generator": "image_agent",
    "comfyui_render": "workflow_agent",
    "audio_pipeline": "voice_agent",
    "video_pipeline": "video_agent",
    "media_planning": "workflow_agent",
    "knowledge": "knowledge_agent",
    "planning": "planner_agent",
    "debug": "debugger_agent",
    "documentation": "documentation_agent",
    "script_generation": "script_agent",
    "music": "music_agent",
    "workflow_creation": "workflow_agent",
}


class AgentRouter:
    """
    Routet Tasks an den passenden Agenten.

    Nutzt Registry für Agenten-Lookup.
    """

    def __init__(self, registry: Optional[AgentRegistry] = None):
        self._registry = registry or get_agent_registry()

    def route(self, task: Task) -> Optional[AgentProfile]:
        """
        Ermittelt den besten Agenten für einen Task.

        Priorität:
        1. tool_hint -> Slug-Lookup
        2. Department aus Beschreibung/Keywords
        3. Capability-Match
        4. Planner Agent als Fallback

        Returns:
            AgentProfile oder None wenn kein passender Agent
        """
        # 1. Direktes Slug-Mapping über tool_hint
        if task.tool_hint:
            slug = TOOL_HINT_TO_SLUG.get(task.tool_hint.lower())
            if slug:
                profile = self._registry.get_by_slug(slug)
                if profile and profile.is_active:
                    return profile

            # Department-basiert
            dept = TOOL_HINT_TO_DEPARTMENT.get(task.tool_hint.lower())
            if dept:
                candidates = self._registry.list_by_department(
                    department_from_str(dept) or Department.PLANNING
                )
                if candidates:
                    return self._pick_best(candidates, task)

        # 2. Keyword-basierte Department-Erkennung
        dept = self._infer_department_from_description(task.description)
        if dept:
            candidates = self._registry.list_by_department(dept)
            if candidates:
                return self._pick_best(candidates, task)

        # 3. Capability-Match
        candidates = self._registry.list_active()
        for profile in candidates:
            if self._matches_capabilities(profile, task):
                return profile

        # 4. Fallback: Planner Agent
        return self._registry.get_by_slug("planner_agent") or (
            candidates[0] if candidates else None
        )

    def _infer_department_from_description(self, description: str) -> Optional[Department]:
        """Inferiert Department aus Task-Beschreibung."""
        desc_lower = description.lower()
        keyword_to_dept = [
            ("recherch", Department.RESEARCH),
            ("research", Department.RESEARCH),
            ("code", Department.DEVELOPMENT),
            ("programm", Department.DEVELOPMENT),
            ("script", Department.DEVELOPMENT),
            ("debug", Department.DEVELOPMENT),
            ("dokumentation", Department.DEVELOPMENT),
            ("documentation", Department.DEVELOPMENT),
            ("bild", Department.MEDIA),
            ("image", Department.MEDIA),
            ("audio", Department.MEDIA),
            ("voice", Department.MEDIA),
            ("video", Department.MEDIA),
            ("animation", Department.MEDIA),
            ("thumbnail", Department.MEDIA),
            ("musik", Department.MEDIA),
            ("music", Department.MEDIA),
            ("wissen", Department.RESEARCH),
            ("knowledge", Department.RESEARCH),
            ("plan", Department.PLANNING),
            ("planning", Department.PLANNING),
            ("workflow", Department.AUTOMATION),
            ("tool", Department.AUTOMATION),
            ("scheduler", Department.AUTOMATION),
            ("system", Department.SYSTEM),
            ("update", Department.SYSTEM),
            ("recovery", Department.SYSTEM),
            ("monitor", Department.SYSTEM),
        ]
        for kw, dept in keyword_to_dept:
            if kw in desc_lower:
                return dept
        return None

    def _matches_capabilities(self, profile: AgentProfile, task: Task) -> bool:
        """Prüft ob Profil-Capabilities zum Task passen."""
        desc_lower = (task.description or "").lower()
        for cap in profile.capabilities:
            if cap.lower() in desc_lower or desc_lower in cap.lower():
                return True
        return False

    def _pick_best(
        self,
        candidates: List[AgentProfile],
        task: Task,
    ) -> AgentProfile:
        """Wählt den besten Kandidaten (höchste priority, dann erstes Match)."""
        active = [c for c in candidates if c.is_active]
        if not active:
            return candidates[0]
        return max(active, key=lambda p: p.priority)
