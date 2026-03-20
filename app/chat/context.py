"""
Chat-Kontext – Projekt-, Chat- und Topic-Metadaten für Modell-Prompts.

Strukturiertes Objekt (ChatRequestContext) und Injektion in den Message-Flow.
Keine UI-Abhängigkeit, keine Provider-spezifische Logik.
Kontext aus ProjectService, ChatService – keine doppelte Wahrheit.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

_log = logging.getLogger(__name__)

from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
from app.chat.context_limits import (
    ChatContextRenderLimits,
    enforce_line_limit,
    truncate_text,
)


def _is_meaningless_field_value(value: str) -> bool:
    """
    True wenn Wert nach Truncation nutzlos ist (leer, nur Whitespace, nur "...").
    Regel: Feld weglassen statt "..."-Müll rendern.
    """
    if not value:
        return True
    s = value.strip()
    return not s or s == "..."


def _has_content_lines(lines: list[str]) -> bool:
    """True wenn mindestens eine Zeile mit Feld-Inhalt (beginnt mit '- ') existiert."""
    return any(ln.strip().startswith("- ") for ln in lines if ln.strip())


@dataclass(frozen=True)
class ChatContextRenderOptions:
    """Steuert welche Kontextfelder gerendert werden."""

    include_project: bool = True
    include_chat: bool = True
    include_topic: bool = True


@dataclass
class ChatRequestContext:
    """
    Request-/Conversation-Kontext für Modell-Anfragen.

    Klein gehalten, klar als Kontext für eine Chat-Anfrage gedacht.
    Wird aus chat_id über ProjectService und ChatService aufgebaut.
    """

    project_id: Optional[int] = None
    project_name: Optional[str] = None
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    is_global_chat: bool = False

    def is_empty(self) -> bool:
        """True wenn kein sinnvoller Kontext vorhanden (mindestens chat_title)."""
        return not self.chat_title

    def to_system_prompt_fragment(
        self,
        mode: ChatContextMode,
        detail_level: ChatContextDetailLevel = ChatContextDetailLevel.STANDARD,
        render_options: Optional["ChatContextRenderOptions"] = None,
        render_limits: Optional[ChatContextRenderLimits] = None,
        _overflow_info: Optional[Dict[str, bool]] = None,
        _failsafe_info: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Formatiert Kontext als System-Prompt-Block.

        mode: ChatContextMode.NEUTRAL | ChatContextMode.SEMANTIC
        detail_level: MINIMAL | STANDARD | FULL
        render_options: welche Felder gerendert werden; None = alle
        render_limits: Kürzungsregeln (project/chat/topic chars, max lines); None = keine
        _overflow_info: optional dict to populate with budget_overflow_prevented,
            budget_exhausted_before_optional_sources (instrumentation only)
        _failsafe_info: optional dict to populate when returning "" (trace only):
            reason: header_only_fragment_removed | empty_injection_prevented
        OFF darf hier nicht landen – Caller prüft vorher.
        Liefert "" wenn is_empty() oder kein Feld aktiv.
        """
        if self.is_empty():
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "empty_injection_prevented"
            return ""
        opts = render_options or ChatContextRenderOptions()
        if not opts.include_project and not opts.include_chat and not opts.include_topic:
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "empty_injection_prevented"
            return ""
        if mode == ChatContextMode.NEUTRAL:
            raw = self._to_neutral_fragment(detail_level, opts, render_limits)
        elif mode == ChatContextMode.SEMANTIC:
            raw = self._to_semantic_fragment(detail_level, opts, render_limits)
        else:
            raise ValueError("OFF darf hier nicht landen")

        if not raw.strip():
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "empty_injection_prevented"
            return ""

        lines = raw.splitlines()
        max_lines = render_limits.max_total_lines if render_limits else None
        limited = enforce_line_limit(lines, max_lines)
        overflow_prevented = max_lines is not None and len(limited) < len(lines)
        topic_is_optional = opts.include_topic and (
            detail_level != ChatContextDetailLevel.MINIMAL or bool(self.topic_name)
        )
        exhausted_before_optional = overflow_prevented and topic_is_optional
        if _overflow_info is not None:
            _overflow_info["budget_overflow_prevented"] = overflow_prevented
            _overflow_info["budget_exhausted_before_optional_sources"] = exhausted_before_optional

        if len(limited) <= 1:
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "header_only_fragment_removed"
            return ""
        if not _has_content_lines(limited):
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "header_only_fragment_removed"
            return ""
        result = "\n".join(limited) + "\n"
        if not result.strip():
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "empty_injection_prevented"
            return ""
        return result

    def _to_neutral_fragment(
        self,
        detail_level: ChatContextDetailLevel,
        opts: "ChatContextRenderOptions",
        render_limits: Optional[ChatContextRenderLimits] = None,
    ) -> str:
        limits = render_limits
        proj = truncate_text(
            self.project_name or "Unbekannt",
            limits.max_project_chars if limits else None,
        )
        chat = truncate_text(
            self.chat_title or "Unbekannt",
            limits.max_chat_chars if limits else None,
        )
        topic_val = self.topic_name or "—"
        topic = truncate_text(
            topic_val,
            limits.max_topic_chars if limits else None,
        )
        lines = ["Kontext:"]
        if opts.include_project and not _is_meaningless_field_value(proj):
            lines.append(f"- Projekt: {proj}")
        if opts.include_chat and not _is_meaningless_field_value(chat):
            lines.append(f"- Chat: {chat}")
        if opts.include_topic and detail_level != ChatContextDetailLevel.MINIMAL and self.topic_name and not _is_meaningless_field_value(topic):
            lines.append(f"- Topic: {topic}")
        if len(lines) <= 1:
            return ""
        return "\n".join(lines) + "\n"

    def _to_semantic_fragment(
        self,
        detail_level: ChatContextDetailLevel,
        opts: "ChatContextRenderOptions",
        render_limits: Optional[ChatContextRenderLimits] = None,
    ) -> str:
        limits = render_limits
        proj = truncate_text(
            self.project_name or "Unbekannt",
            limits.max_project_chars if limits else None,
        )
        chat = truncate_text(
            self.chat_title or "Unbekannt",
            limits.max_chat_chars if limits else None,
        )
        topic = truncate_text(
            self.topic_name or "—",
            limits.max_topic_chars if limits else None,
        )

        if detail_level == ChatContextDetailLevel.MINIMAL:
            lines = ["Arbeitskontext:"]
            if opts.include_project and not _is_meaningless_field_value(proj):
                lines.append(f"- Projekt: {proj}")
            if opts.include_chat and not _is_meaningless_field_value(chat):
                lines.append(f"- Chat: {chat}")
            if len(lines) <= 1:
                return ""
            return "\n".join(lines) + "\n"

        if detail_level == ChatContextDetailLevel.STANDARD:
            lines = ["Arbeitskontext:"]
            if opts.include_project and not _is_meaningless_field_value(proj):
                lines.append(f"- Projekt: {proj} (Themenbereich)")
            if opts.include_chat and not _is_meaningless_field_value(chat):
                lines.append(f"- Chat: {chat} (laufende Konversation)")
            if opts.include_topic and not _is_meaningless_field_value(topic):
                lines.append(f"- Topic: {topic}")
            if len(lines) <= 1:
                return ""
            return "\n".join(lines) + "\n"

        lines = ["Arbeitskontext:"]
        if opts.include_project and not _is_meaningless_field_value(proj):
            lines.append(f"- Projekt: {proj} (Themenbereich)")
        if opts.include_chat and not _is_meaningless_field_value(chat):
            lines.append(f"- Chat: {chat} (laufende Konversation)")
        if opts.include_topic and not _is_meaningless_field_value(topic):
            lines.append(f"- Topic: {topic} (fokussierter Bereich)")
        if len(lines) <= 1:
            return ""
        return "\n".join(lines) + "\n\n" + "Berücksichtige diesen Kontext bei der Antwort."


# Alias für Rückwärtskompatibilität
ChatContext = ChatRequestContext


def build_chat_context(chat_id: Optional[int]) -> ChatRequestContext:
    """
    Baut ChatRequestContext aus chat_id.

    Kontext aus Systemquellen: ProjectService, ChatService.
    Keine UI-Abhängigkeit, keine doppelte Wahrheit.
    """
    if not chat_id or not isinstance(chat_id, int) or chat_id <= 0:
        return ChatRequestContext()

    try:
        from app.services.chat_service import get_chat_service
        from app.services.project_service import get_project_service

        chat_svc = get_chat_service()
        proj_svc = get_project_service()

        info = chat_svc.get_chat_info(chat_id)
        if not info:
            return ChatRequestContext(chat_id=chat_id)

        chat_title = info.get("title") or "Neuer Chat"
        topic_id = info.get("topic_id")
        topic_name = info.get("topic_name")

        project_id = proj_svc.get_project_of_chat(chat_id)
        project_name = None
        is_global_chat = project_id is None
        if project_id:
            proj = proj_svc.get_project(project_id)
            project_name = proj.get("name") if proj else None

        return ChatRequestContext(
            project_id=project_id,
            project_name=project_name,
            chat_id=chat_id,
            chat_title=chat_title,
            topic_id=topic_id,
            topic_name=topic_name,
            is_global_chat=is_global_chat,
        )
    except Exception as e:
        _log.debug("build_chat_context failed for chat_id=%s: %s", chat_id, e)
        return ChatRequestContext(chat_id=chat_id)


CTX_MARKER = "[[CTX]]"


def get_context_fragment_stats(fragment: str) -> dict:
    """Strukturmetriken für ein Kontext-Fragment. Keine Tokenizer-Library."""
    if not fragment:
        return {"chars": 0, "lines": 0, "nonempty_lines": 0}
    s = str(fragment)
    lines = s.splitlines()
    nonempty = [ln for ln in lines if ln.strip()]
    return {
        "chars": len(s),
        "lines": len(lines),
        "nonempty_lines": len(nonempty),
    }


def inject_chat_context_into_messages(
    messages: List[Dict[str, Any]],
    fragment: str,
    _failsafe_info: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Injiziert ein Kontext-Fragment in die Message-Liste.

    - Marker [[CTX]] verhindert mehrfache Injection (idempotent)
    - Keine Systemnachricht: neue Systemnachricht an Position 0
    - Systemnachricht vorhanden: append mit sauberem Abstand (rstrip + \\n\\n)
    - Fail-safe bei leeren/malformed Inputs: Rückgabe original messages
    _failsafe_info: optional dict to populate when skipping injection (trace only):
        reason: empty_injection_prevented | marker_only_fragment_removed | header_only_fragment_removed
    """
    try:
        if not messages or not isinstance(messages, list):
            return messages if isinstance(messages, list) else []
        if not fragment or not str(fragment).strip():
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "empty_injection_prevented"
            return list(messages)
        if not _has_content_lines(str(fragment).splitlines()):
            if _failsafe_info is not None:
                _failsafe_info["reason"] = "marker_only_fragment_removed"
            return list(messages)

        marked = f"{CTX_MARKER}\n{fragment}"
        result = list(messages)
        first = result[0]

        if not isinstance(first, dict):
            return result

        if first.get("role") == "system":
            content = first.get("content", "") or ""
            if CTX_MARKER in str(content):
                return result
            merged = str(content).rstrip() + "\n\n" + marked
            result[0] = {"role": "system", "content": merged}
        else:
            result.insert(0, {"role": "system", "content": marked})

        return result
    except Exception:
        return list(messages) if isinstance(messages, list) else []
