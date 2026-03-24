"""
Statische Agentenfarm-Definitionen (Vorbereitungsschicht).

Diese Modelle beschreiben geplante Rollen-Slots — unabhängig von ``AgentProfile`` / SQLite.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ScopeLevel(str, Enum):
    """Zuordnungsebene innerhalb der geplanten Agentenfarm."""

    GLOBAL_PORTFOLIO = "global_portfolio"
    PROJECT = "project"
    PRODUCTION_AREA = "production_area"


class FarmRoleKind(str, Enum):
    """Geplante Farm-Rollenart (fachlich, nicht identisch mit ``AgentProfile.role``)."""

    GLOBAL_BUTLER = "global_butler"
    PROJECT_BUTLER = "project_butler"
    AREA_BUTLER = "area_butler"
    SPECIALIST = "specialist"
    QA_REVIEW = "qa_review"
    KNOWLEDGE_DOCS = "knowledge_docs"
    REPORTING_CONTROLLING = "reporting_controlling"


class ActivationState(str, Enum):
    """Aktivierungszustand der Definition (noch keine Laufzeitorchestrierung)."""

    DRAFT = "draft"
    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass(frozen=True)
class AgentFarmRoleDefinition:
    """
    Deklarative Beschreibung einer Farm-Rolle.

    ``agent_role_id`` ist ein stabiler logischer Schlüssel (z. B. ``farm.project.butler``),
    nicht zwingend gleich ``AgentProfile.id`` in der Datenbank.
    """

    agent_role_id: str
    scope_level: ScopeLevel
    farm_role_kind: FarmRoleKind
    display_name: str
    functional_role: str
    responsibility_scope: str
    input_types: Tuple[str, ...]
    output_types: Tuple[str, ...]
    allowed_workflow_ids: Tuple[str, ...]
    escalation_target_role_id: Optional[str]
    activation: ActivationState
    is_standard: bool
