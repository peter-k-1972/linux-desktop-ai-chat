"""
Chat-Kontext – Profile (Presets).

Regelbasierte Auflösung von Profil → mode/detail/fields.
Keine Heuristik, keine LLM-Entscheidung.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode

if TYPE_CHECKING:
    from app.context.explainability.context_explanation import ContextExplanation
from app.core.config.settings import ChatContextProfile
from app.chat.request_context_hints import RequestContextHint


@dataclass(frozen=True)
class ResolvedChatContextConfig:
    """Aufgelöste Kontext-Konfiguration aus einem Profil."""

    mode: ChatContextMode
    detail: ChatContextDetailLevel
    include_project: bool
    include_chat: bool
    include_topic: bool


_PROFILE_MAP = {
    ChatContextProfile.STRICT_MINIMAL: ResolvedChatContextConfig(
        mode=ChatContextMode.SEMANTIC,
        detail=ChatContextDetailLevel.MINIMAL,
        include_project=True,
        include_chat=False,
        include_topic=False,
    ),
    ChatContextProfile.BALANCED: ResolvedChatContextConfig(
        mode=ChatContextMode.SEMANTIC,
        detail=ChatContextDetailLevel.STANDARD,
        include_project=True,
        include_chat=True,
        include_topic=False,
    ),
    ChatContextProfile.FULL_GUIDANCE: ResolvedChatContextConfig(
        mode=ChatContextMode.SEMANTIC,
        detail=ChatContextDetailLevel.FULL,
        include_project=True,
        include_chat=True,
        include_topic=True,
    ),
}


def resolve_chat_context_profile(profile: ChatContextProfile) -> ResolvedChatContextConfig:
    """Löst ein Profil in mode/detail/fields auf. Unbekannte Profile → BALANCED."""
    return _PROFILE_MAP.get(profile, _PROFILE_MAP[ChatContextProfile.BALANCED])


_HINT_TO_PROFILE = {
    RequestContextHint.GENERAL_QUESTION: ChatContextProfile.BALANCED,
    RequestContextHint.ARCHITECTURE_WORK: ChatContextProfile.FULL_GUIDANCE,
    RequestContextHint.TOPIC_FOCUS: ChatContextProfile.BALANCED,
    RequestContextHint.LOW_CONTEXT_QUERY: ChatContextProfile.STRICT_MINIMAL,
}


def resolve_profile_for_request_hint(hint: RequestContextHint) -> ChatContextProfile:
    """Leitet Profil aus explizitem Hint ab. Unbekannte Hints → BALANCED."""
    return _HINT_TO_PROFILE.get(hint, ChatContextProfile.BALANCED)


@dataclass(frozen=True)
class ChatContextResolutionTrace:
    """Nachvollziehbarer Trace der Kontext-Auflösung. Keine Hidden Decisions."""

    source: str  # individual_settings | profile | policy | chat_policy | project_policy | request_hint
    profile: Optional[str] = None
    mode: str = ""
    detail: str = ""
    fields: List[str] = field(default_factory=list)
    policy: Optional[str] = None
    hint: Optional[str] = None
    chat_policy: Optional[str] = None
    project_policy: Optional[str] = None
    profile_enabled: bool = False
    limits_source: str = "default"
    max_project_chars: Optional[int] = None
    max_chat_chars: Optional[int] = None
    max_topic_chars: Optional[int] = None
    max_total_lines: Optional[int] = None
    explanation: Optional["ContextExplanation"] = None
