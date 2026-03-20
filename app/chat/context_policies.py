"""
Chat-Kontext – Policies (Use-Case-Zuordnung).

Explizite Policy → Profil. Keine automatische Erkennung, keine UI-Logik.
Jede Policy definiert ein festes Render-Budget.
"""

from enum import Enum

from app.core.config.settings import ChatContextProfile
from app.chat.context_limits import ChatContextRenderLimits


class ChatContextPolicy(str, Enum):
    """Use-Case-Policy für Kontextkonfiguration."""

    DEFAULT = "default"
    ARCHITECTURE = "architecture"
    DEBUG = "debug"
    EXPLORATION = "exploration"


_POLICY_TO_PROFILE = {
    ChatContextPolicy.DEFAULT: ChatContextProfile.BALANCED,
    ChatContextPolicy.ARCHITECTURE: ChatContextProfile.FULL_GUIDANCE,
    ChatContextPolicy.DEBUG: ChatContextProfile.STRICT_MINIMAL,
    ChatContextPolicy.EXPLORATION: ChatContextProfile.BALANCED,
}

_POLICY_TO_LIMITS = {
    ChatContextPolicy.DEFAULT: ChatContextRenderLimits(
        max_project_chars=80,
        max_chat_chars=80,
        max_topic_chars=60,
        max_total_lines=6,
    ),
    ChatContextPolicy.ARCHITECTURE: ChatContextRenderLimits(
        max_project_chars=100,
        max_chat_chars=100,
        max_topic_chars=80,
        max_total_lines=8,
    ),
    ChatContextPolicy.DEBUG: ChatContextRenderLimits(
        max_project_chars=60,
        max_chat_chars=60,
        max_topic_chars=40,
        max_total_lines=4,
    ),
    ChatContextPolicy.EXPLORATION: ChatContextRenderLimits(
        max_project_chars=80,
        max_chat_chars=80,
        max_topic_chars=60,
        max_total_lines=6,
    ),
}


def resolve_profile_for_policy(policy: ChatContextPolicy) -> ChatContextProfile:
    """Leitet Profil aus Policy ab. Unbekannte Policies → BALANCED."""
    return _POLICY_TO_PROFILE.get(policy, ChatContextProfile.BALANCED)


def resolve_limits_for_policy(policy: ChatContextPolicy) -> ChatContextRenderLimits:
    """Leitet Render-Budget aus Policy ab. Unbekannte Policies → DEFAULT-Limits."""
    return _POLICY_TO_LIMITS.get(policy, _POLICY_TO_LIMITS[ChatContextPolicy.DEFAULT])
