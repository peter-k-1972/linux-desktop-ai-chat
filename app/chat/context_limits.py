"""
Context Compression Rules – feste Kürzungsregeln für Kontext-Fragmente.

Greifen NACH der Auflösung der finalen Kontextkonfiguration, VOR der Injection.
Keine Tokenizer-Library, keine LLM-basierte Kürzung, keine semantische Bewertung.
Nur feste, nachvollziehbare Regeln.
"""

from dataclasses import dataclass

CHARS_PER_TOKEN = 4


@dataclass(frozen=True)
class ChatContextRenderLimits:
    """Harte Limits für gerenderte Kontext-Fragmente."""

    max_project_chars: int | None = None
    max_chat_chars: int | None = None
    max_topic_chars: int | None = None
    max_total_lines: int | None = None


DEFAULT_LIMITS = ChatContextRenderLimits(
    max_project_chars=80,
    max_chat_chars=80,
    max_topic_chars=60,
    max_total_lines=6,
)


def truncate_text(value: str, max_chars: int | None) -> str:
    """
    Regeln:
    - None => unverändert
    - leer => leer
    - wenn kürzer/gleich => unverändert
    - wenn länger => sauber gekürzt mit "..."
    """
    if max_chars is None:
        return value
    if not value:
        return value
    if len(value) <= max_chars:
        return value
    if max_chars <= 3:
        return value[:max_chars]
    return value[: max_chars - 3] + "..."


def enforce_line_limit(lines: list[str], max_total_lines: int | None) -> list[str]:
    """
    Regeln:
    - None => unverändert
    - line limit greift auf final gerenderte Zeilen
    - Überstand wird hart abgeschnitten
    """
    if max_total_lines is None:
        return lines
    return lines[:max_total_lines]


# Label overhead in chars (deterministic, no estimation)
_LABEL_HEADER_CHARS = len("Arbeitskontext:\n")
_LABEL_PROJECT_CHARS = len("- Projekt: ")
_LABEL_CHAT_CHARS = len("- Chat: ")
_LABEL_TOPIC_CHARS = len("- Topic: ")


def compute_budget_accounting(
    limits: ChatContextRenderLimits,
    include_project: bool,
    include_chat: bool,
    include_topic: bool,
    limits_source: str,
) -> dict:
    """
    Berechnet Token-Budget-Accounting aus Limits und Render-Optionen.

    Nur deterministische Werte, keine Heuristik außer chars/4.
    Returns dict mit: configured_budget_total, effective_budget_total,
    reserved_budget_system, reserved_budget_user, available_budget_for_context,
    budget_strategy, budget_source.
    """
    proj_chars = limits.max_project_chars or 0
    chat_chars = limits.max_chat_chars or 0
    topic_chars = limits.max_topic_chars or 0

    configured_chars = 0
    if include_project:
        configured_chars += proj_chars
    if include_chat:
        configured_chars += chat_chars
    if include_topic:
        configured_chars += topic_chars

    configured_tokens = configured_chars // CHARS_PER_TOKEN

    reserved_system_chars = _LABEL_HEADER_CHARS
    if include_project:
        reserved_system_chars += _LABEL_PROJECT_CHARS
    if include_chat:
        reserved_system_chars += _LABEL_CHAT_CHARS
    if include_topic:
        reserved_system_chars += _LABEL_TOPIC_CHARS
    reserved_system_tokens = reserved_system_chars // CHARS_PER_TOKEN

    reserved_user_tokens = 0

    effective_tokens = configured_tokens
    available_tokens = effective_tokens - reserved_system_tokens - reserved_user_tokens
    if available_tokens < 0:
        available_tokens = 0

    return {
        "configured_budget_total": configured_tokens,
        "effective_budget_total": effective_tokens,
        "reserved_budget_system": reserved_system_tokens,
        "reserved_budget_user": reserved_user_tokens,
        "available_budget_for_context": available_tokens,
        "budget_strategy": "per_field_and_lines",
        "budget_source": limits_source,
    }
