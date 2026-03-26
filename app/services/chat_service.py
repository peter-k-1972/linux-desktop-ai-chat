"""
ChatService – Sessions, Nachrichten, Chat-Senden.

Verantwortlich für:
- Chat-Sessions (Liste, Erstellen, Laden)
- Nachrichten speichern
- Chat an Modell senden (delegiert an Ollama)
- Modellliste für Chat-Kontext (delegiert an ModelService bei Bedarf)

GUI spricht nur mit ChatService, nicht mit DB oder Ollama direkt.
"""

import dataclasses
import logging
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Optional

from app.services.infrastructure import get_infrastructure

if TYPE_CHECKING:
    from app.chat.context_policies import ChatContextPolicy
    from app.chat.request_context_hints import RequestContextHint
    from app.context.replay.replay_models import ReplayInput

_log = logging.getLogger(__name__)


def _build_context_sources(
    fragment: str,
    context: Any,
    render_options: Any,
    render_limits: Optional[Any],
) -> List[Any]:
    """Build ContextSourceEntry list with per-source budget accounting.

    Sources appended in resolver processing order only: project (1), chat (2), topic (3).
    No sorting applied later; list order must be preserved by formatter and serializer.
    """
    from app.chat.context_limits import truncate_text
    from app.context.explainability.context_explanation import ContextSourceEntry

    proj_raw = context.project_name or "Unbekannt"
    chat_raw = context.chat_title or "Unbekannt"
    topic_raw = context.topic_name or "—"
    proj_after = truncate_text(
        proj_raw,
        render_limits.max_project_chars if render_limits else None,
    )
    chat_after = truncate_text(
        chat_raw,
        render_limits.max_chat_chars if render_limits else None,
    )
    topic_after = truncate_text(
        topic_raw,
        render_limits.max_topic_chars if render_limits else None,
    )

    proj_in_frag = "- Projekt:" in fragment
    chat_in_frag = "- Chat:" in fragment
    topic_in_frag = "- Topic:" in fragment

    def _entry(
        source_type: str,
        identifier: str,
        wanted: bool,
        in_fragment: bool,
        chars_before: int,
        chars_after: int,
        budget_allocated: Optional[int],
        selection_order: int,
    ) -> Any:
        included = wanted and in_fragment
        if wanted and not in_fragment:
            reason = "budget_exhausted"
        elif included and chars_before > chars_after:
            reason = "truncated_to_budget"
        else:
            reason = ""
        budget_used = chars_after if included else 0
        budget_dropped = (
            (chars_before - chars_after) if included else (chars_before if wanted else 0)
        )
        return ContextSourceEntry(
            source_type=source_type,
            identifier=identifier,
            included=included,
            chars_before=chars_before,
            chars_after=chars_after,
            chars=chars_after if included else None,
            lines=None,
            budget_allocated=budget_allocated,
            budget_used=budget_used,
            budget_dropped=budget_dropped,
            selection_order=selection_order,
            reason=reason,
        )

    limits = render_limits
    return [
        _entry(
            "project",
            context.project_name or "",
            render_options.include_project,
            proj_in_frag,
            len(proj_raw),
            len(proj_after),
            limits.max_project_chars if limits else None,
            1,
        ),
        _entry(
            "chat",
            context.chat_title or "",
            render_options.include_chat,
            chat_in_frag,
            len(chat_raw),
            len(chat_after),
            limits.max_chat_chars if limits else None,
            2,
        ),
        _entry(
            "topic",
            context.topic_name or "",
            render_options.include_topic,
            topic_in_frag,
            len(topic_raw),
            len(topic_after),
            limits.max_topic_chars if limits else None,
            3,
        ),
    ]


CHARS_PER_TOKEN = 4


def _build_dropped_context_report(
    sources: List[Any],
    compressions: List[Any],
    warnings: List[Any],
    trace: Any,
    render_options: Any,
) -> tuple:
    """
    Build dropped context report from sources, compressions, warnings, trace.
    Returns (dropped_by_source, dropped_total_tokens, dropped_reasons).
    Reuses existing accounting; no duplicate token counting. Metadata only.
    """
    from app.context.explainability.context_explanation import ContextDroppedEntry

    dropped_entries: List[Any] = []
    reasons_seen: List[str] = []
    total = 0

    def _add_reason(r: str) -> None:
        if r and r not in reasons_seen:
            reasons_seen.append(r)

    def _tokens_from_chars(chars: int) -> int:
        return chars // CHARS_PER_TOKEN if chars else 0

    resolution_source = getattr(trace, "source", "") or ""

    for s in sources:
        chars_before = s.chars_before or 0
        chars_after = s.chars_after or 0
        budget_dropped = s.budget_dropped or 0
        source_id = s.identifier if s.identifier else None

        if s.included:
            if s.reason == "truncated_to_budget":
                dt = _tokens_from_chars(chars_before - chars_after)
                dropped_entries.append(
                    ContextDroppedEntry(
                        source_type=s.source_type,
                        reason="compression",
                        dropped_tokens=dt,
                        source_id=source_id,
                    )
                )
                total += dt
                _add_reason("compression")
        else:
            if s.reason == "budget_exhausted":
                dt = _tokens_from_chars(budget_dropped)
                dropped_entries.append(
                    ContextDroppedEntry(
                        source_type=s.source_type,
                        reason="token_budget_exhaustion",
                        dropped_tokens=dt,
                        source_id=source_id,
                    )
                )
                total += dt
                _add_reason("token_budget_exhaustion")
            else:
                if resolution_source == "individual_settings":
                    reason = "field_disabled"
                elif resolution_source == "profile":
                    reason = "profile_restriction"
                elif resolution_source in ("policy", "chat_policy", "project_policy"):
                    reason = "policy_exclusion"
                else:
                    reason = "profile_restriction"
                dt = _tokens_from_chars(chars_before)
                dropped_entries.append(
                    ContextDroppedEntry(
                        source_type=s.source_type,
                        reason=reason,
                        dropped_tokens=dt,
                        source_id=source_id,
                    )
                )
                total += dt
                _add_reason(reason)

    for w in warnings:
        wt = getattr(w, "warning_type", "")
        eff = getattr(w, "effect", None)
        if wt == "failsafe" or wt in (
            "header_only_fragment_removed",
            "marker_only_fragment_removed",
            "empty_injection_prevented",
        ) or eff in ("removed_fragment", "skipped_injection"):
            _add_reason("failsafe_cleanup")
            # Every failsafe must create a dropped entry (no silent cleanup)
            failsafe_tokens = getattr(w, "dropped_tokens", None)
            if failsafe_tokens is None and compressions:
                c0 = compressions[0]
                failsafe_tokens = getattr(c0, "after_tokens", None)
            dropped_entries.append(
                ContextDroppedEntry(
                    source_type="context",
                    reason="failsafe_cleanup",
                    dropped_tokens=failsafe_tokens,
                    source_id=None,
                )
            )
            total += failsafe_tokens or 0
            break

    # Guarantee: dropped_total_tokens == sum(dropped_entries.dropped_tokens)
    dropped_total = sum(e.dropped_tokens or 0 for e in dropped_entries)
    if not dropped_entries:
        dropped_total = None
    elif dropped_total == 0 and any(e.dropped_tokens is None for e in dropped_entries):
        dropped_total = 0  # failsafe-only case
    return (dropped_entries, dropped_total, reasons_seen)


class ChatService:
    """
    Service für Chat: Sessions, Nachrichten, Modellaufrufe.
    """

    def __init__(self):
        self._infra = get_infrastructure()

    # --- Sessions ---

    def list_chats(
        self,
        filter_text: str = "",
        project_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Liste Chats. project_id: nur Chats dieses Projekts; None: alle."""
        return self._infra.database.list_chats(filter_text, project_id)

    def list_chats_for_project(
        self,
        project_id: Optional[int],
        filter_text: str = "",
        topic_id: Optional[int] = None,
        pinned_only: Optional[bool] = None,
        archived_only: Optional[bool] = None,
        recent_days: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Chats: project_id=None = alle Chats (global); sonst nur Projekt-Chats."""
        if project_id is not None:
            return self._infra.database.list_chats_for_project_with_activity(
                project_id,
                filter_text,
                topic_id=topic_id,
                pinned_only=pinned_only,
                archived_only=archived_only,
                recent_days=recent_days,
            )
        raw = self._infra.database.list_chats(filter_text, project_id=None)
        enriched = self._enrich_chats_for_display(raw)
        if recent_days is not None and recent_days > 0:
            enriched = self._filter_by_recent_days(enriched, recent_days)
        return enriched

    def _enrich_chats_for_display(
        self, raw: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fügt topic_id, pinned, archived, last_activity hinzu (für globale Liste)."""
        result = []
        for c in raw:
            result.append({
                **dict(c),
                "topic_id": None,
                "topic_name": None,
                "pinned": 0,
                "archived": 0,
                "last_activity": c.get("created_at") or c.get("last_activity"),
            })
        return result

    def _filter_by_recent_days(
        self, chats: List[Dict[str, Any]], days: int
    ) -> List[Dict[str, Any]]:
        """Filtert Chats auf die letzten N Tage (last_activity/created_at)."""
        from datetime import datetime, timedelta

        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        result = []
        for c in chats:
            ts = c.get("last_activity") or c.get("created_at") or ""
            if ts and ts[:10] >= cutoff:
                result.append(c)
        return result

    def create_chat(self, title: str = "Neuer Chat") -> int:
        """Erstellt einen neuen Chat. Gibt chat_id zurück."""
        return self._infra.database.create_chat(title)

    def create_chat_in_project(
        self,
        project_id: int,
        title: str = "Neuer Chat",
        topic_id: Optional[int] = None,
    ) -> int:
        """Erstellt einen Chat und ordnet ihn dem Projekt (und optional Topic) zu."""
        chat_id = self._infra.database.create_chat(title)
        self._infra.database.add_chat_to_project(project_id, chat_id, topic_id)
        return chat_id

    def load_chat(self, chat_id: int) -> List[tuple]:
        """Lädt Nachrichten eines Chats. (role, content, timestamp)."""
        return self._infra.database.load_chat(chat_id)

    def save_message(
        self,
        chat_id: int,
        role: str,
        content: str,
        *,
        model: Optional[str] = None,
        agent: Optional[str] = None,
        completion_status: Optional[str] = None,
    ) -> None:
        """Speichert eine Nachricht. completion_status: 'complete'|'possibly_truncated'|'interrupted'|'error'."""
        self._infra.database.save_message(
            chat_id, role, content, model=model, agent=agent, completion_status=completion_status
        )

    def save_chat_title(self, chat_id: int, title: str) -> None:
        """Aktualisiert den Chat-Titel. Wirft bei Fehler."""
        self._infra.database.save_chat_title(chat_id, title)

    def move_chat_to_topic(
        self,
        project_id: int,
        chat_id: int,
        topic_id: Optional[int] = None,
    ) -> None:
        """Ordnet Chat einem Topic zu. topic_id=None = Ungrouped."""
        self._infra.database.set_chat_topic(project_id, chat_id, topic_id)

    def get_chat_info(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Chat-Infos inkl. last_activity."""
        return self._infra.database.get_chat_info(chat_id)

    def get_last_assistant_agent_for_chat(self, chat_id: int) -> Optional[str]:
        """Agent-Kennung der letzten Assistant-Nachricht, falls in der DB gespeichert."""
        return self._infra.database.get_last_assistant_agent_for_chat(chat_id)

    def set_chat_pinned(
        self, project_id: int, chat_id: int, pinned: bool
    ) -> None:
        """Pin oder Unpin eines Chats im Projekt."""
        self._infra.database.set_chat_pinned(project_id, chat_id, pinned)

    def set_chat_archived(
        self, project_id: int, chat_id: int, archived: bool
    ) -> None:
        """Archiviert oder reaktiviert einen Chat im Projekt."""
        self._infra.database.set_chat_archived(project_id, chat_id, archived)

    def duplicate_chat(
        self, chat_id: int, project_id: int, topic_id: Optional[int] = None
    ) -> Optional[int]:
        """Dupliziert Chat inkl. Nachrichten. Gibt neue chat_id zurück."""
        return self._infra.database.duplicate_chat(chat_id, project_id, topic_id)

    def delete_chat(self, chat_id: int) -> None:
        """Löscht Chat inkl. Nachrichten und Zuordnungen. Nur genau dieser Chat."""
        if not isinstance(chat_id, int) or chat_id <= 0:
            return
        self._infra.database.delete_chat(chat_id)

    # --- Chat (Modellaufruf) ---

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        chat_id: Optional[int] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = True,
        request_context_hint: Optional["RequestContextHint"] = None,
        context_policy: Optional["ChatContextPolicy"] = None,
        *,
        cloud_via_local: Optional[bool] = None,
        usage_type: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Sendet Chat an Ollama. Streamt Chunks.
        Chat Guard v1/v2: Bewertet letzte User-Nachricht, härtet Prompt bei Bedarf.
        chat_id: Optional – wenn gesetzt, wird Projekt-/Chat-/Topic-Kontext injiziert.
        request_context_hint: Optional – expliziter Hint für Profil-Wahl.
        context_policy: Optional – Use-Case-Policy (Vorrang vor Hint, nach profile_enabled).
        Chunk-Format: {"message": {"content": "...", "thinking": "..."}, "done": bool} oder {"error": "..."}
        """
        messages = await self._apply_chat_guard(messages)
        if chat_id:
            try:
                from app.context.devtools.request_capture import capture
                from app.services.project_service import get_project_service
                project_id = get_project_service().get_project_of_chat(chat_id)
                capture(
                    chat_id=chat_id,
                    messages=messages,
                    project_id=project_id,
                    request_context_hint=request_context_hint.value if request_context_hint else None,
                    context_policy=context_policy.value if context_policy else None,
                )
            except Exception:
                pass
            messages = self._inject_chat_context(
                messages, chat_id, request_context_hint, context_policy
            )

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("Streaming: %s", "ON" if stream else "OFF")

        from app.chat.think_payload import resolve_think_payload_for_ollama
        from app.persistence.enums import UsageType
        from app.services.model_chat_runtime import stream_instrumented_model_chat
        from app.services.model_orchestrator_service import get_model_orchestrator

        settings = self._infra.settings
        cloud_via = (
            settings.cloud_via_local if cloud_via_local is None else bool(cloud_via_local)
        )
        ut = usage_type if usage_type is not None else UsageType.CHAT.value
        orch = get_model_orchestrator()
        think_param = resolve_think_payload_for_ollama(settings)

        chunk_count = 0
        async for chunk in stream_instrumented_model_chat(
            orch,
            settings=settings,
            model_id=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            think=think_param,
            cloud_via_local=cloud_via,
            chat_id=chat_id,
            usage_type=ut,
        ):
            chunk_count += 1
            yield chunk

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("Chunks received: %d", chunk_count)

    async def _apply_chat_guard(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Wendet Chat Guard v1/v2 an: Intent-Bewertung, optional ML, Prompt-Härtung."""
        if not messages:
            return messages
        last_content = None
        for m in reversed(messages):
            if m.get("role") == "user":
                last_content = m.get("content") or ""
                break
        if not last_content or not last_content.strip():
            return messages
        try:
            from app.core.chat_guard.service import get_chat_guard_service
            guard = get_chat_guard_service()
            result = await guard.assess_async(last_content)
            return guard.apply_to_messages(messages, result)
        except Exception:
            return messages

    def _resolve_context_configuration(
        self,
        request_context_hint: Optional["RequestContextHint"] = None,
        context_policy: Optional["ChatContextPolicy"] = None,
        chat_context_policy: Optional["ChatContextPolicy"] = None,
        project_context_policy: Optional["ChatContextPolicy"] = None,
        *,
        invalid_override_sources: Optional[List[str]] = None,
        invalid_override_inputs: Optional[List[tuple[str, str]]] = None,
    ) -> tuple[Any, Any, Any, Any]:
        """
        Löst finale Kontext-Konfiguration auf. Liefert (mode, detail, render_options, trace).
        Priorität: profile_enabled > context_policy > chat > project > request_hint > individual_settings.
        """
        from app.chat.context import ChatContextRenderOptions
        from app.chat.context_limits import DEFAULT_LIMITS, compute_budget_accounting
        from app.chat.context_profiles import (
            ChatContextResolutionTrace,
            resolve_chat_context_profile,
            resolve_profile_for_request_hint,
        )
        from app.chat.context_policies import resolve_profile_for_policy, resolve_limits_for_policy
        from app.context.explainability.context_explanation import (
            ContextDecisionEntry,
            ContextExplanation,
            ContextIgnoredInputEntry,
            ContextResolvedSettingEntry,
            ContextSettingCandidate,
            ContextWarningEntry,
        )

        settings = self._infra.settings
        profile_enabled = getattr(settings, "chat_context_profile_enabled", False)
        policy_str = context_policy.value if context_policy else None
        hint_str = request_context_hint.value if request_context_hint else None
        chat_policy_str = chat_context_policy.value if chat_context_policy else None
        project_policy_str = project_context_policy.value if project_context_policy else None

        _PRIORITY_SOURCES = [
            "profile_enabled",
            "explicit_context_policy",
            "chat_default_context_policy",
            "project_default_context_policy",
            "request_context_hint",
            "individual_settings",
        ]

        def _value_for_source(idx: int) -> Optional[tuple]:
            """Returns (mode, detail, profile, include_project, include_chat, include_topic) or None if not present."""
            if idx == 0:
                if not profile_enabled:
                    return None
                prof = settings.get_chat_context_profile()
                res = resolve_chat_context_profile(prof)
                return (res.mode.value, res.detail.value, prof.value, res.include_project, res.include_chat, res.include_topic)
            if idx == 1:
                if context_policy is None:
                    return None
                prof = resolve_profile_for_policy(context_policy)
                res = resolve_chat_context_profile(prof)
                return (res.mode.value, res.detail.value, prof.value, res.include_project, res.include_chat, res.include_topic)
            if idx == 2:
                if chat_context_policy is None:
                    return None
                prof = resolve_profile_for_policy(chat_context_policy)
                res = resolve_chat_context_profile(prof)
                return (res.mode.value, res.detail.value, prof.value, res.include_project, res.include_chat, res.include_topic)
            if idx == 3:
                if project_context_policy is None:
                    return None
                prof = resolve_profile_for_policy(project_context_policy)
                res = resolve_chat_context_profile(prof)
                return (res.mode.value, res.detail.value, prof.value, res.include_project, res.include_chat, res.include_topic)
            if idx == 4:
                if request_context_hint is None:
                    return None
                prof = resolve_profile_for_request_hint(request_context_hint)
                res = resolve_chat_context_profile(prof)
                return (res.mode.value, res.detail.value, prof.value, res.include_project, res.include_chat, res.include_topic)
            if idx == 5:
                m = settings.get_chat_context_mode()
                d = settings.get_chat_context_detail_level()
                inc_p = getattr(settings, "chat_context_include_project", True)
                inc_c = getattr(settings, "chat_context_include_chat", True)
                inc_t = getattr(settings, "chat_context_include_topic", False)
                return (m.value, d.value, None, inc_p, inc_c, inc_t)
            return None

        def _build_resolved_settings(
            winning_idx: int,
            mode_val: str,
            detail_val: str,
            profile_val: Optional[str],
            include_project: bool,
            include_chat: bool,
            include_topic: bool,
        ) -> List[Any]:
            """Build ContextResolvedSettingEntry for each effective setting."""
            setting_names = ["mode", "detail_level", "policy", "project_enabled", "chat_enabled", "topic_enabled"]
            final_values = [mode_val, detail_val, profile_val, include_project, include_chat, include_topic]

            def _get_val(vals: Optional[tuple], i: int):
                if vals is None:
                    return None
                return vals[i]

            result = []
            for s_idx, (name, final) in enumerate(zip(setting_names, final_values)):
                candidates = []
                for p_idx in range(6):
                    vals = _value_for_source(p_idx)
                    val = _get_val(vals, s_idx) if vals else None
                    applied = p_idx == winning_idx
                    if applied:
                        skipped = None
                    elif vals is None:
                        skipped = "source_not_present"
                    else:
                        skipped = "higher_priority_won"
                    candidates.append(
                        ContextSettingCandidate(
                            priority_index=p_idx,
                            source=_PRIORITY_SOURCES[p_idx],
                            value=val,
                            applied=applied,
                            skipped_reason=skipped,
                        )
                    )
                result.append(
                    ContextResolvedSettingEntry(
                        setting_name=name,
                        final_value=final,
                        winning_source=_PRIORITY_SOURCES[winning_idx],
                        candidates=candidates,
                        fallback_used=(winning_idx == 5),
                    )
                )
            return result

        def _add_disabled_field_entries(
            ignored: List[ContextIgnoredInputEntry],
            include_project: bool,
            include_chat: bool,
            include_topic: bool,
            winning_source: str,
        ) -> List[ContextIgnoredInputEntry]:
            """Add ignored_inputs for disabled fields (excluded by profile or settings)."""
            result = list(ignored)
            src = "settings" if winning_source == "individual_settings" else winning_source
            reason = "disabled_by_profile" if winning_source in (
                "profile", "explicit_context_policy", "chat_default_context_policy",
                "project_default_context_policy", "request_context_hint",
            ) else "field_disabled"
            if not include_project:
                result.append(
                    ContextIgnoredInputEntry(
                        input_name="project",
                        input_source=src,
                        raw_value=False,
                        reason=reason,
                        resolution_effect="field_disabled",
                    )
                )
            if not include_chat:
                result.append(
                    ContextIgnoredInputEntry(
                        input_name="chat",
                        input_source=src,
                        raw_value=False,
                        reason=reason,
                        resolution_effect="field_disabled",
                    )
                )
            if not include_topic:
                result.append(
                    ContextIgnoredInputEntry(
                        input_name="topic",
                        input_source=src,
                        raw_value=False,
                        reason=reason,
                        resolution_effect="field_disabled",
                    )
                )
            return result

        def _check_invalid_settings(ignored: List[ContextIgnoredInputEntry]) -> List[ContextIgnoredInputEntry]:
            """Add ignored entries for invalid mode/detail in individual_settings."""
            backend = getattr(settings, "_backend", None)
            if not backend:
                return ignored
            valid_mode = {"off", "neutral", "semantic"}
            valid_detail = {"minimal", "standard", "full"}
            raw_mode = (backend.value("chat_context_mode", "semantic") or "semantic").strip().lower()
            raw_detail = (backend.value("chat_context_detail_level", "standard") or "standard").strip().lower()
            result = list(ignored)
            if raw_mode not in valid_mode:
                result.append(
                    ContextIgnoredInputEntry(
                        input_name="mode",
                        input_source="settings",
                        raw_value=raw_mode,
                        reason="invalid_value",
                        resolution_effect="fallback_used",
                    )
                )
            if raw_detail not in valid_detail:
                result.append(
                    ContextIgnoredInputEntry(
                        input_name="detail_level",
                        input_source="settings",
                        raw_value=raw_detail,
                        reason="invalid_value",
                        resolution_effect="fallback_used",
                    )
                )
            return result

        def _explanation_with_budget(
            decisions,
            limits,
            include_project,
            include_chat,
            include_topic,
            limits_source,
            resolved_settings=None,
            fallback_used=False,
            invalid_override_sources=None,
            invalid_override_inputs=None,
            ignored_inputs_base=None,
            winning_source=None,
        ):
            budget = compute_budget_accounting(
                limits, include_project, include_chat, include_topic, limits_source
            )
            warnings = []
            if limits_source == "default":
                warnings.append(
                    ContextWarningEntry("budget_missing_fallback_used", "limits_source=default")
                )
            if fallback_used:
                warnings.append(
                    ContextWarningEntry(
                        "resolution_fallback_used",
                        "all higher-priority candidates were missing; using individual_settings",
                    )
                )
            for src in invalid_override_sources or []:
                warnings.append(
                    ContextWarningEntry(
                        "override_source_invalid",
                        f"expected override source '{src}' was present but invalid and skipped",
                    )
                )
            ignored = list(ignored_inputs_base or [])
            if invalid_override_inputs:
                for name, raw in invalid_override_inputs:
                    ignored.append(
                        ContextIgnoredInputEntry(
                            input_name=name,
                            input_source="request",
                            raw_value=raw,
                            reason="invalid_value",
                            resolution_effect="ignored",
                        )
                    )
            if fallback_used and winning_source == "individual_settings":
                ignored = _check_invalid_settings(ignored)
            ignored = _add_disabled_field_entries(
                ignored, include_project, include_chat, include_topic, winning_source or "individual_settings"
            )
            return ContextExplanation(
                decisions=decisions,
                resolved_settings=resolved_settings or [],
                ignored_inputs=ignored,
                configured_budget_total=budget["configured_budget_total"],
                effective_budget_total=budget["effective_budget_total"],
                reserved_budget_system=budget["reserved_budget_system"],
                reserved_budget_user=budget["reserved_budget_user"],
                available_budget_for_context=budget["available_budget_for_context"],
                budget_strategy=budget["budget_strategy"],
                budget_source=budget["budget_source"],
                warnings=warnings,
            )

        if profile_enabled:
            profile = settings.get_chat_context_profile()
            resolved = resolve_chat_context_profile(profile)
            limits = DEFAULT_LIMITS
            fields = []
            if resolved.include_project:
                fields.append("project")
            if resolved.include_chat:
                fields.append("chat")
            if resolved.include_topic:
                fields.append("topic")
            decisions = [
                ContextDecisionEntry("policy", "profile_enabled", "none"),
                ContextDecisionEntry("profile", "profile", profile.value),
                ContextDecisionEntry("request_hint", "hint", hint_str or "none"),
                ContextDecisionEntry("field", "project", "included" if resolved.include_project else "excluded"),
                ContextDecisionEntry("field", "chat", "included" if resolved.include_chat else "excluded"),
                ContextDecisionEntry("field", "topic", "included" if resolved.include_topic else "excluded"),
            ]
            resolved_settings = _build_resolved_settings(
                0, resolved.mode.value, resolved.detail.value, profile.value,
                resolved.include_project, resolved.include_chat, resolved.include_topic,
            )
            explanation = _explanation_with_budget(
                decisions, limits, resolved.include_project, resolved.include_chat, resolved.include_topic, "default",
                resolved_settings=resolved_settings,
                fallback_used=False,
                invalid_override_sources=invalid_override_sources,
                invalid_override_inputs=invalid_override_inputs,
                winning_source="profile",
            )
            trace = ChatContextResolutionTrace(
                source="profile",
                profile=profile.value,
                mode=resolved.mode.value,
                detail=resolved.detail.value,
                fields=fields,
                policy=policy_str,
                hint=hint_str,
                chat_policy=chat_policy_str,
                project_policy=project_policy_str,
                profile_enabled=profile_enabled,
                limits_source="default",
                max_project_chars=limits.max_project_chars,
                max_chat_chars=limits.max_chat_chars,
                max_topic_chars=limits.max_topic_chars,
                max_total_lines=limits.max_total_lines,
                explanation=explanation,
            )
            render_options = ChatContextRenderOptions(
                include_project=resolved.include_project,
                include_chat=resolved.include_chat,
                include_topic=resolved.include_topic,
            )
            return (resolved.mode, resolved.detail, render_options, trace, limits)

        if context_policy is not None:
            profile = resolve_profile_for_policy(context_policy)
            resolved = resolve_chat_context_profile(profile)
            limits = resolve_limits_for_policy(context_policy)
            fields = []
            if resolved.include_project:
                fields.append("project")
            if resolved.include_chat:
                fields.append("chat")
            if resolved.include_topic:
                fields.append("topic")
            decisions = [
                ContextDecisionEntry("policy", "context_policy", policy_str or "none"),
                ContextDecisionEntry("profile", "policy", profile.value),
                ContextDecisionEntry("request_hint", "hint", hint_str or "none"),
                ContextDecisionEntry("field", "project", "included" if resolved.include_project else "excluded"),
                ContextDecisionEntry("field", "chat", "included" if resolved.include_chat else "excluded"),
                ContextDecisionEntry("field", "topic", "included" if resolved.include_topic else "excluded"),
            ]
            resolved_settings = _build_resolved_settings(
                1, resolved.mode.value, resolved.detail.value, profile.value,
                resolved.include_project, resolved.include_chat, resolved.include_topic,
            )
            explanation = _explanation_with_budget(
                decisions, limits, resolved.include_project, resolved.include_chat, resolved.include_topic, "policy",
                resolved_settings=resolved_settings,
                fallback_used=False,
                invalid_override_sources=invalid_override_sources,
                invalid_override_inputs=invalid_override_inputs,
                winning_source="explicit_context_policy",
            )
            trace = ChatContextResolutionTrace(
                source="policy",
                profile=profile.value,
                mode=resolved.mode.value,
                detail=resolved.detail.value,
                fields=fields,
                policy=policy_str,
                hint=hint_str,
                chat_policy=chat_policy_str,
                project_policy=project_policy_str,
                profile_enabled=profile_enabled,
                limits_source="policy",
                max_project_chars=limits.max_project_chars,
                max_chat_chars=limits.max_chat_chars,
                max_topic_chars=limits.max_topic_chars,
                max_total_lines=limits.max_total_lines,
                explanation=explanation,
            )
            render_options = ChatContextRenderOptions(
                include_project=resolved.include_project,
                include_chat=resolved.include_chat,
                include_topic=resolved.include_topic,
            )
            return (resolved.mode, resolved.detail, render_options, trace, limits)

        if chat_context_policy is not None:
            profile = resolve_profile_for_policy(chat_context_policy)
            resolved = resolve_chat_context_profile(profile)
            limits = resolve_limits_for_policy(chat_context_policy)
            fields = []
            if resolved.include_project:
                fields.append("project")
            if resolved.include_chat:
                fields.append("chat")
            if resolved.include_topic:
                fields.append("topic")
            decisions = [
                ContextDecisionEntry("policy", "chat_policy", chat_policy_str or "none"),
                ContextDecisionEntry("profile", "chat_policy", profile.value),
                ContextDecisionEntry("request_hint", "hint", hint_str or "none"),
                ContextDecisionEntry("field", "project", "included" if resolved.include_project else "excluded"),
                ContextDecisionEntry("field", "chat", "included" if resolved.include_chat else "excluded"),
                ContextDecisionEntry("field", "topic", "included" if resolved.include_topic else "excluded"),
            ]
            resolved_settings = _build_resolved_settings(
                2, resolved.mode.value, resolved.detail.value, profile.value,
                resolved.include_project, resolved.include_chat, resolved.include_topic,
            )
            explanation = _explanation_with_budget(
                decisions, limits, resolved.include_project, resolved.include_chat, resolved.include_topic, "chat_policy",
                resolved_settings=resolved_settings,
                fallback_used=False,
                invalid_override_sources=invalid_override_sources,
                invalid_override_inputs=invalid_override_inputs,
                winning_source="chat_default_context_policy",
            )
            trace = ChatContextResolutionTrace(
                source="chat_policy",
                profile=profile.value,
                mode=resolved.mode.value,
                detail=resolved.detail.value,
                fields=fields,
                policy=policy_str,
                hint=hint_str,
                chat_policy=chat_policy_str,
                project_policy=project_policy_str,
                profile_enabled=profile_enabled,
                limits_source="chat_policy",
                max_project_chars=limits.max_project_chars,
                max_chat_chars=limits.max_chat_chars,
                max_topic_chars=limits.max_topic_chars,
                max_total_lines=limits.max_total_lines,
                explanation=explanation,
            )
            render_options = ChatContextRenderOptions(
                include_project=resolved.include_project,
                include_chat=resolved.include_chat,
                include_topic=resolved.include_topic,
            )
            return (resolved.mode, resolved.detail, render_options, trace, limits)

        if project_context_policy is not None:
            profile = resolve_profile_for_policy(project_context_policy)
            resolved = resolve_chat_context_profile(profile)
            limits = resolve_limits_for_policy(project_context_policy)
            fields = []
            if resolved.include_project:
                fields.append("project")
            if resolved.include_chat:
                fields.append("chat")
            if resolved.include_topic:
                fields.append("topic")
            decisions = [
                ContextDecisionEntry("policy", "project_policy", project_policy_str or "none"),
                ContextDecisionEntry("profile", "project_policy", profile.value),
                ContextDecisionEntry("request_hint", "hint", hint_str or "none"),
                ContextDecisionEntry("field", "project", "included" if resolved.include_project else "excluded"),
                ContextDecisionEntry("field", "chat", "included" if resolved.include_chat else "excluded"),
                ContextDecisionEntry("field", "topic", "included" if resolved.include_topic else "excluded"),
            ]
            resolved_settings = _build_resolved_settings(
                3, resolved.mode.value, resolved.detail.value, profile.value,
                resolved.include_project, resolved.include_chat, resolved.include_topic,
            )
            explanation = _explanation_with_budget(
                decisions, limits, resolved.include_project, resolved.include_chat, resolved.include_topic, "project_policy",
                resolved_settings=resolved_settings,
                fallback_used=False,
                invalid_override_sources=invalid_override_sources,
                invalid_override_inputs=invalid_override_inputs,
                winning_source="project_default_context_policy",
            )
            trace = ChatContextResolutionTrace(
                source="project_policy",
                profile=profile.value,
                mode=resolved.mode.value,
                detail=resolved.detail.value,
                fields=fields,
                policy=policy_str,
                hint=hint_str,
                chat_policy=chat_policy_str,
                project_policy=project_policy_str,
                profile_enabled=profile_enabled,
                limits_source="project_policy",
                max_project_chars=limits.max_project_chars,
                max_chat_chars=limits.max_chat_chars,
                max_topic_chars=limits.max_topic_chars,
                max_total_lines=limits.max_total_lines,
                explanation=explanation,
            )
            render_options = ChatContextRenderOptions(
                include_project=resolved.include_project,
                include_chat=resolved.include_chat,
                include_topic=resolved.include_topic,
            )
            return (resolved.mode, resolved.detail, render_options, trace, limits)

        if request_context_hint is not None:
            profile = resolve_profile_for_request_hint(request_context_hint)
            resolved = resolve_chat_context_profile(profile)
            limits = DEFAULT_LIMITS
            fields = []
            if resolved.include_project:
                fields.append("project")
            if resolved.include_chat:
                fields.append("chat")
            if resolved.include_topic:
                fields.append("topic")
            decisions = [
                ContextDecisionEntry("policy", "request_hint", "none"),
                ContextDecisionEntry("profile", "request_hint", profile.value),
                ContextDecisionEntry("request_hint", "hint", hint_str or "none"),
                ContextDecisionEntry("field", "project", "included" if resolved.include_project else "excluded"),
                ContextDecisionEntry("field", "chat", "included" if resolved.include_chat else "excluded"),
                ContextDecisionEntry("field", "topic", "included" if resolved.include_topic else "excluded"),
            ]
            resolved_settings = _build_resolved_settings(
                4, resolved.mode.value, resolved.detail.value, profile.value,
                resolved.include_project, resolved.include_chat, resolved.include_topic,
            )
            explanation = _explanation_with_budget(
                decisions, limits, resolved.include_project, resolved.include_chat, resolved.include_topic, "default",
                resolved_settings=resolved_settings,
                fallback_used=False,
                invalid_override_sources=invalid_override_sources,
                invalid_override_inputs=invalid_override_inputs,
                winning_source="request_context_hint",
            )
            trace = ChatContextResolutionTrace(
                source="request_hint",
                profile=profile.value,
                mode=resolved.mode.value,
                detail=resolved.detail.value,
                fields=fields,
                policy=policy_str,
                hint=hint_str,
                chat_policy=chat_policy_str,
                project_policy=project_policy_str,
                profile_enabled=profile_enabled,
                limits_source="default",
                max_project_chars=limits.max_project_chars,
                max_chat_chars=limits.max_chat_chars,
                max_topic_chars=limits.max_topic_chars,
                max_total_lines=limits.max_total_lines,
                explanation=explanation,
            )
            render_options = ChatContextRenderOptions(
                include_project=resolved.include_project,
                include_chat=resolved.include_chat,
                include_topic=resolved.include_topic,
            )
            return (resolved.mode, resolved.detail, render_options, trace, limits)

        mode = settings.get_chat_context_mode()
        detail = settings.get_chat_context_detail_level()
        include_project = getattr(settings, "chat_context_include_project", True)
        include_chat = getattr(settings, "chat_context_include_chat", True)
        include_topic = getattr(settings, "chat_context_include_topic", False)
        limits = DEFAULT_LIMITS
        fields = []
        if include_project:
            fields.append("project")
        if include_chat:
            fields.append("chat")
        if include_topic:
            fields.append("topic")
        decisions = [
            ContextDecisionEntry("policy", "individual_settings", "none"),
            ContextDecisionEntry("profile", "individual_settings", "none"),
            ContextDecisionEntry("request_hint", "hint", hint_str or "none"),
            ContextDecisionEntry("field", "project", "included" if include_project else "excluded"),
            ContextDecisionEntry("field", "chat", "included" if include_chat else "excluded"),
            ContextDecisionEntry("field", "topic", "included" if include_topic else "excluded"),
        ]
        resolved_settings = _build_resolved_settings(
            5, mode.value, detail.value, None,
            include_project, include_chat, include_topic,
        )
        explanation = _explanation_with_budget(
            decisions, limits, include_project, include_chat, include_topic, "default",
            resolved_settings=resolved_settings,
            fallback_used=True,
            invalid_override_sources=invalid_override_sources,
            invalid_override_inputs=invalid_override_inputs,
            winning_source="individual_settings",
        )
        trace = ChatContextResolutionTrace(
            source="individual_settings",
            profile=None,
            mode=mode.value,
            detail=detail.value,
            fields=fields,
            policy=policy_str,
            hint=hint_str,
            chat_policy=chat_policy_str,
            project_policy=project_policy_str,
            profile_enabled=profile_enabled,
            limits_source="default",
            max_project_chars=limits.max_project_chars,
            max_chat_chars=limits.max_chat_chars,
            max_topic_chars=limits.max_topic_chars,
            max_total_lines=limits.max_total_lines,
            explanation=explanation,
        )
        render_options = ChatContextRenderOptions(
            include_project=include_project,
            include_chat=include_chat,
            include_topic=include_topic,
        )
        return (mode, detail, render_options, trace, limits)

    def _inject_chat_context(
        self,
        messages: List[Dict[str, str]],
        chat_id: int,
        request_context_hint: Optional["RequestContextHint"] = None,
        context_policy: Optional["ChatContextPolicy"] = None,
    ) -> List[Dict[str, str]]:
        """Injiziert Projekt-/Chat-/Topic-Kontext in die Message-Liste (abhängig von chat_context_mode)."""
        try:
            from app.chat.context import (
                build_chat_context,
                get_context_fragment_stats,
                inject_chat_context_into_messages,
            )
            from app.chats.models import get_chat_context_policy
            from app.context.debug.context_debug import (
                format_context_debug_blocks,
                format_context_injection_summary,
            )
            from app.context.explainability.context_explanation import (
                ContextCompressionEntry,
                ContextExplanation,
                ContextWarningEntry,
            )
            from app.core.config.settings import ChatContextMode
            from app.services.project_service import get_project_service

            chat_context_policy = None
            project_context_policy = None
            if chat_id:
                chat_info = self._infra.database.get_chat_info(chat_id)
                chat_context_policy = get_chat_context_policy(chat_info)
                project_context_policy = get_project_service().get_project_context_policy_for_chat(
                    chat_id
                )

            mode, detail, render_options, trace, render_limits = self._resolve_context_configuration(
                request_context_hint,
                context_policy,
                chat_context_policy,
                project_context_policy,
            )

            base_explanation = trace.explanation or ContextExplanation()

            def _failsafe_warning(
                warning_type: str,
                message: str = "",
                *,
                source_type: Optional[str] = None,
                source_id: Optional[str] = None,
                effect: Optional[str] = None,
                dropped_tokens: Optional[int] = None,
            ):
                return ContextWarningEntry(
                    warning_type=warning_type,
                    message=message,
                    source_type=source_type,
                    source_id=source_id,
                    effect=effect,
                    dropped_tokens=dropped_tokens,
                )

            def _attach_explanation(
                sources=None,
                compressions=None,
                warnings=None,
                ignored_inputs_extra=None,
                empty_result=None,
                empty_result_reason=None,
            ):
                src = sources if sources is not None else base_explanation.sources
                comp = compressions if compressions is not None else base_explanation.compressions
                warn = warnings if warnings is not None else base_explanation.warnings
                ignored = list(base_explanation.ignored_inputs)
                if ignored_inputs_extra:
                    ignored.extend(ignored_inputs_extra)
                dropped_by, dropped_total, dropped_reasons = _build_dropped_context_report(
                    src, comp, warn, trace, render_options
                )
                # Guarantee: total_tokens_after == sum(source.budget_used // 4) for included sources
                total_tokens_after_val = sum(
                    (s.budget_used or 0) // CHARS_PER_TOKEN
                    for s in src
                    if s.included
                ) if src else None
                failsafe_types = (
                    "failsafe",
                    "header_only_fragment_removed",
                    "marker_only_fragment_removed",
                    "empty_injection_prevented",
                )
                failsafe_triggered = any(
                    getattr(w, "warning_type", "") in failsafe_types
                    or getattr(w, "effect", None) in ("removed_fragment", "skipped_injection")
                    for w in warn
                )
                new_expl = dataclasses.replace(
                    base_explanation,
                    sources=src,
                    compressions=comp,
                    warnings=warn,
                    ignored_inputs=ignored,
                    dropped_by_source=dropped_by,
                    dropped_total_tokens=dropped_total,
                    dropped_reasons=dropped_reasons,
                    total_tokens_after=total_tokens_after_val,
                    warning_count=len(warn),
                    failsafe_triggered=failsafe_triggered,
                    empty_result=empty_result if empty_result is not None else base_explanation.empty_result,
                    empty_result_reason=empty_result_reason if empty_result_reason is not None else base_explanation.empty_result_reason,
                )
                return dataclasses.replace(trace, explanation=new_expl)

            if mode == ChatContextMode.OFF:
                trace = _attach_explanation(
                    warnings=base_explanation.warnings
                    + [_failsafe_warning("empty_injection_prevented", "mode=off", effect="skipped_injection")],
                    empty_result=True,
                    empty_result_reason="disabled_mode",
                )
                if _log.isEnabledFor(logging.DEBUG):
                    try:
                        from app.context.debug.context_debug_flag import is_context_debug_enabled
                        if is_context_debug_enabled():
                            for line in format_context_debug_blocks(trace):
                                _log.debug("%s", line)
                    except Exception:
                        pass
                return messages

            context = build_chat_context(chat_id)
            if context.is_empty():
                trace = _attach_explanation(
                    warnings=base_explanation.warnings
                    + [_failsafe_warning("empty_injection_prevented", "context_empty", effect="skipped_injection")],
                    empty_result=True,
                    empty_result_reason="no_sources",
                )
                if _log.isEnabledFor(logging.DEBUG):
                    try:
                        from app.context.debug.context_debug_flag import is_context_debug_enabled
                        if is_context_debug_enabled():
                            for line in format_context_debug_blocks(trace):
                                _log.debug("%s", line)
                    except Exception:
                        pass
                return messages

            overflow_info: Dict[str, bool] = {}
            failsafe_info: Dict[str, str] = {}
            fragment = context.to_system_prompt_fragment(
                mode,
                detail,
                render_options,
                render_limits,
                _overflow_info=overflow_info,
                _failsafe_info=failsafe_info,
            )
            overflow_warnings = []
            if overflow_info.get("budget_overflow_prevented"):
                overflow_warnings.append(
                    ContextWarningEntry("budget_overflow_prevented", "line_limit_truncated")
                )
            if overflow_info.get("budget_exhausted_before_optional_sources"):
                overflow_warnings.append(
                    ContextWarningEntry(
                        "budget_exhausted_before_optional_sources",
                        "topic_cut_by_line_limit",
                    )
                )
            if not fragment.strip():
                reason = failsafe_info.get("reason", "empty_injection_prevented")
                all_excluded = (
                    not render_options.include_project
                    and not render_options.include_chat
                    and not render_options.include_topic
                )
                budget_related = overflow_info.get("budget_exhausted_before_optional_sources") or overflow_info.get(
                    "budget_overflow_prevented"
                )
                if all_excluded:
                    empty_reason = "excluded_by_policy"
                elif budget_related:
                    empty_reason = "budget_exhausted"
                else:
                    empty_reason = "failsafe_cleanup"
                trace = _attach_explanation(
                    warnings=base_explanation.warnings
                    + overflow_warnings
                    + [_failsafe_warning(reason, "fragment_empty", effect="removed_fragment")],
                    empty_result=True,
                    empty_result_reason=empty_reason,
                )
                if _log.isEnabledFor(logging.DEBUG):
                    try:
                        from app.context.debug.context_debug_flag import is_context_debug_enabled
                        if is_context_debug_enabled():
                            for line in format_context_debug_blocks(trace):
                                _log.debug("%s", line)
                    except Exception:
                        pass
                return messages

            sources = _build_context_sources(fragment, context, render_options, render_limits)

            proj_raw = context.project_name or "Unbekannt"
            chat_raw = context.chat_title or "Unbekannt"
            topic_raw = context.topic_name or "—"
            stats = get_context_fragment_stats(fragment)
            before_chars = sum([
                len(proj_raw) if render_options.include_project else 0,
                len(chat_raw) if render_options.include_chat else 0,
                len(topic_raw) if render_options.include_topic else 0,
            ])
            after_chars = stats["chars"]
            before_tokens = before_chars // 4 if before_chars else None
            after_tokens = after_chars // 4 if after_chars else None
            dropped_tokens = (
                (before_tokens - after_tokens)
                if before_tokens and after_tokens and before_tokens > after_tokens
                else None
            )

            compressions = [
                ContextCompressionEntry(
                    operation="truncate",
                    original_chars=before_chars,
                    final_chars=after_chars,
                    before_tokens=before_tokens,
                    after_tokens=after_tokens,
                    dropped_tokens=dropped_tokens,
                    reason="limits",
                ),
            ]

            inject_failsafe_info: Dict[str, str] = {}
            source_not_found_entries: List[Any] = []
            result = inject_chat_context_into_messages(
                messages, fragment, _failsafe_info=inject_failsafe_info
            )
            all_warnings = base_explanation.warnings + overflow_warnings
            ignored_extra = source_not_found_entries if source_not_found_entries else None
            if result == messages and messages and fragment.strip():
                reason = inject_failsafe_info.get("reason", "marker_only_fragment_removed")
                trace = _attach_explanation(
                    sources=sources,
                    compressions=compressions,
                    warnings=all_warnings
                    + [_failsafe_warning(reason, "injection_skipped", effect="skipped_injection")],
                    ignored_inputs_extra=ignored_extra,
                )
            else:
                trace = _attach_explanation(
                    sources=sources,
                    compressions=compressions,
                    warnings=all_warnings,
                    ignored_inputs_extra=ignored_extra,
                )

            if _log.isEnabledFor(logging.DEBUG):
                try:
                    from app.context.debug.context_debug_flag import is_context_debug_enabled
                    if is_context_debug_enabled():
                        fields_parts = []
                        if render_options.include_project:
                            fields_parts.append("project")
                        if render_options.include_chat:
                            fields_parts.append("chat")
                        if render_options.include_topic:
                            fields_parts.append("topic")
                        stats = get_context_fragment_stats(fragment)
                        for line in format_context_debug_blocks(trace):
                            _log.debug("%s", line)
                        for line in format_context_injection_summary(
                            stats["chars"], stats["lines"], fields_parts
                        ):
                            _log.debug("%s", line)
                except Exception:
                    pass

            return result
        except Exception:
            return messages

    def get_context_explanation(
        self,
        chat_id: int,
        request_context_hint: Optional["RequestContextHint"] = None,
        context_policy: Optional["ChatContextPolicy"] = None,
        *,
        return_trace: bool = False,
        return_fragment: bool = False,
        invalid_override_sources: Optional[List[str]] = None,
        invalid_override_inputs: Optional[List[tuple[str, str]]] = None,
    ):
        """
        Liefert die Kontext-Erklärung für einen Chat (ohne Side Effects).

        Keine Injection, keine DB-Änderung. Nur Lesen und Berechnen.
        return_trace: wenn True, liefert ChatContextResolutionTrace statt ContextExplanation.
        return_fragment: wenn True, liefert zusätzlich (fragment, context, render_options) als Tuple.
                         Vermeidet doppelte Auflösung bei Inspection (ein Aufruf für Trace + Payload).
        """
        from app.chat.context import build_chat_context, get_context_fragment_stats
        from app.chats.models import get_chat_context_policy
        from app.context.explainability.context_explanation import (
            ContextCompressionEntry,
            ContextExplanation,
            ContextWarningEntry,
        )
        from app.core.config.settings import ChatContextMode
        from app.services.project_service import get_project_service

        chat_context_policy = None
        project_context_policy = None
        if chat_id:
            chat_info = self._infra.database.get_chat_info(chat_id)
            chat_context_policy = get_chat_context_policy(chat_info)
            project_context_policy = get_project_service().get_project_context_policy_for_chat(
                chat_id
            )

        mode, detail, render_options, trace, render_limits = self._resolve_context_configuration(
            request_context_hint,
            context_policy,
            chat_context_policy,
            project_context_policy,
            invalid_override_sources=invalid_override_sources,
            invalid_override_inputs=invalid_override_inputs,
        )

        base_explanation = trace.explanation or ContextExplanation()

        def _ensure_trace_has_explanation(t: Any) -> Any:
            """Guarantee trace.explanation is not None when return_trace=True. Creates minimal fallback if missing."""
            if t.explanation is not None:
                return t
            from app.context.explainability.context_explanation import (
                ContextResolvedSettingEntry,
                ContextSettingCandidate,
            )
            _src = t.source or "explanation_fallback"
            _cand = ContextSettingCandidate(priority_index=0, source=_src, value=None, applied=True, skipped_reason=None)
            minimal = ContextExplanation(
                resolved_settings=[
                    ContextResolvedSettingEntry("mode", t.mode, _src, [_cand], False),
                    ContextResolvedSettingEntry("detail_level", t.detail, _src, [_cand], False),
                    ContextResolvedSettingEntry("policy", t.policy, _src, [_cand], False),
                ],
                empty_result=True,
                empty_result_reason="explanation_fallback",
            )
            return dataclasses.replace(t, explanation=minimal)

        def _failsafe_warning(
            warning_type: str,
            message: str = "",
            *,
            source_type: Optional[str] = None,
            source_id: Optional[str] = None,
            effect: Optional[str] = None,
            dropped_tokens: Optional[int] = None,
        ):
            return ContextWarningEntry(
                warning_type=warning_type,
                message=message,
                source_type=source_type,
                source_id=source_id,
                effect=effect,
                dropped_tokens=dropped_tokens,
            )

        def _attach_explanation(
            sources=None,
            compressions=None,
            warnings=None,
            ignored_inputs_extra=None,
            empty_result=None,
            empty_result_reason=None,
        ):
            src = sources if sources is not None else base_explanation.sources
            comp = compressions if compressions is not None else base_explanation.compressions
            warn = warnings if warnings is not None else base_explanation.warnings
            ignored = list(base_explanation.ignored_inputs)
            if ignored_inputs_extra:
                ignored.extend(ignored_inputs_extra)
            dropped_by, dropped_total, dropped_reasons = _build_dropped_context_report(
                src, comp, warn, trace, render_options
            )
            total_tokens_after_val = sum(
                (s.budget_used or 0) // CHARS_PER_TOKEN
                for s in src
                if s.included
            ) if src else None
            failsafe_types = (
                "failsafe",
                "header_only_fragment_removed",
                "marker_only_fragment_removed",
                "empty_injection_prevented",
            )
            failsafe_triggered = any(
                getattr(w, "warning_type", "") in failsafe_types
                or getattr(w, "effect", None) in ("removed_fragment", "skipped_injection")
                for w in warn
            )
            new_expl = dataclasses.replace(
                base_explanation,
                sources=src,
                compressions=comp,
                warnings=warn,
                ignored_inputs=ignored,
                dropped_by_source=dropped_by,
                dropped_total_tokens=dropped_total,
                dropped_reasons=dropped_reasons,
                total_tokens_after=total_tokens_after_val,
                warning_count=len(warn),
                failsafe_triggered=failsafe_triggered,
                empty_result=empty_result if empty_result is not None else base_explanation.empty_result,
                empty_result_reason=empty_result_reason if empty_result_reason is not None else base_explanation.empty_result_reason,
            )
            return dataclasses.replace(trace, explanation=new_expl)

        if mode == ChatContextMode.OFF:
            trace = _attach_explanation(
                warnings=base_explanation.warnings
                + [_failsafe_warning("empty_injection_prevented", "mode=off", effect="skipped_injection")],
                empty_result=True,
                empty_result_reason="disabled_mode",
            )
            result = _ensure_trace_has_explanation(trace) if return_trace else trace.explanation
            if return_fragment:
                return (result, None, None, render_options)
            return result

        context = build_chat_context(chat_id)
        if context.is_empty():
            from app.context.explainability.context_explanation import ContextIgnoredInputEntry
            trace = _attach_explanation(
                warnings=base_explanation.warnings
                + [_failsafe_warning("empty_injection_prevented", "context_empty", effect="skipped_injection")],
                ignored_inputs_extra=[
                    ContextIgnoredInputEntry(
                        input_name="context",
                        input_source="chat",
                        raw_value=None,
                        reason="empty_source",
                        resolution_effect="ignored",
                    ),
                ],
                empty_result=True,
                empty_result_reason="no_sources",
            )
            result = _ensure_trace_has_explanation(trace) if return_trace else trace.explanation
            if return_fragment:
                return (result, None, context, render_options)
            return result

        source_not_found_entries = []
        if context.project_id is not None and not (context.project_name or "").strip():
            source_not_found_entries.append(
                ContextIgnoredInputEntry(
                    input_name="project",
                    input_source="project",
                    raw_value=str(context.project_id),
                    reason="source_not_found",
                    resolution_effect="ignored",
                )
            )
        if context.topic_id is not None and not (context.topic_name or "").strip():
            source_not_found_entries.append(
                ContextIgnoredInputEntry(
                    input_name="topic",
                    input_source="topic",
                    raw_value=str(context.topic_id),
                    reason="source_not_found",
                    resolution_effect="ignored",
                )
            )

        overflow_info: Dict[str, bool] = {}
        failsafe_info: Dict[str, str] = {}
        fragment = context.to_system_prompt_fragment(
            mode,
            detail,
            render_options,
            render_limits,
            _overflow_info=overflow_info,
            _failsafe_info=failsafe_info,
        )
        overflow_warnings = []
        if overflow_info.get("budget_overflow_prevented"):
            overflow_warnings.append(
                ContextWarningEntry("budget_overflow_prevented", "line_limit_truncated")
            )
        if overflow_info.get("budget_exhausted_before_optional_sources"):
            overflow_warnings.append(
                ContextWarningEntry(
                    "budget_exhausted_before_optional_sources",
                    "topic_cut_by_line_limit",
                )
            )
        if not fragment.strip():
            from app.context.explainability.context_explanation import ContextIgnoredInputEntry
            empty_entries = source_not_found_entries + [
                ContextIgnoredInputEntry(
                    input_name="context_fragment",
                    input_source="render",
                    raw_value="",
                    reason="empty_source",
                    resolution_effect="ignored",
                ),
            ]
            reason = failsafe_info.get("reason", "empty_injection_prevented")
            all_excluded = (
                not render_options.include_project
                and not render_options.include_chat
                and not render_options.include_topic
            )
            budget_related = overflow_info.get("budget_exhausted_before_optional_sources") or overflow_info.get(
                "budget_overflow_prevented"
            )
            if all_excluded:
                empty_reason = "excluded_by_policy"
            elif budget_related:
                empty_reason = "budget_exhausted"
            else:
                empty_reason = "failsafe_cleanup"
            trace = _attach_explanation(
                warnings=base_explanation.warnings
                + overflow_warnings
                + [_failsafe_warning(reason, "fragment_empty", effect="removed_fragment")],
                ignored_inputs_extra=empty_entries,
                empty_result=True,
                empty_result_reason=empty_reason,
            )
            result = _ensure_trace_has_explanation(trace) if return_trace else trace.explanation
            if return_fragment:
                return (result, fragment, context, render_options)
            return result

        sources = _build_context_sources(fragment, context, render_options, render_limits)

        proj_raw = context.project_name or "Unbekannt"
        chat_raw = context.chat_title or "Unbekannt"
        topic_raw = context.topic_name or "—"
        stats = get_context_fragment_stats(fragment)
        before_chars = sum([
            len(proj_raw) if render_options.include_project else 0,
            len(chat_raw) if render_options.include_chat else 0,
            len(topic_raw) if render_options.include_topic else 0,
        ])
        after_chars = stats["chars"]
        before_tokens = before_chars // 4 if before_chars else None
        after_tokens = after_chars // 4 if after_chars else None
        dropped_tokens = (
            (before_tokens - after_tokens)
            if before_tokens and after_tokens and before_tokens > after_tokens
            else None
        )

        compressions = [
            ContextCompressionEntry(
                operation="truncate",
                original_chars=before_chars,
                final_chars=after_chars,
                before_tokens=before_tokens,
                after_tokens=after_tokens,
                dropped_tokens=dropped_tokens,
                reason="limits",
            ),
        ]

        trace = _attach_explanation(
            sources=sources,
            compressions=compressions,
            warnings=base_explanation.warnings + overflow_warnings,
        )
        result = _ensure_trace_has_explanation(trace) if return_trace else trace.explanation
        if return_fragment:
            return (result, fragment, context, render_options)
        return result

    def _build_context_from_replay_input(
        self,
        replay_input: "ReplayInput",
        *,
        return_trace: bool = False,
        return_fragment: bool = False,
    ) -> Any:
        """
        Build context from ReplayInput. No DB access. Deterministic.

        Uses same fragment-building logic as get_context_explanation.
        """
        from app.chat.context import (
            ChatRequestContext,
            get_context_fragment_stats,
        )
        from app.chat.context_limits import ChatContextRenderLimits
        from app.chat.context_profiles import ChatContextResolutionTrace
        from app.context.replay.replay_models import ReplayInput
        from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode

        inp = replay_input
        context = ChatRequestContext(
            project_id=inp.project_id,
            project_name=inp.project_name,
            chat_id=inp.chat_id,
            chat_title=inp.chat_title,
            topic_id=inp.topic_id,
            topic_name=inp.topic_name,
            is_global_chat=inp.is_global_chat,
        )
        mode = ChatContextMode(inp.mode) if inp.mode else ChatContextMode.SEMANTIC
        detail = ChatContextDetailLevel(inp.detail) if inp.detail else ChatContextDetailLevel.STANDARD
        from app.chat.context import ChatContextRenderOptions

        render_options = ChatContextRenderOptions(
            include_project=inp.include_project,
            include_chat=inp.include_chat,
            include_topic=inp.include_topic,
        )
        render_limits = ChatContextRenderLimits(
            max_project_chars=inp.max_project_chars,
            max_chat_chars=inp.max_chat_chars,
            max_topic_chars=inp.max_topic_chars,
            max_total_lines=inp.max_total_lines,
        )
        from app.context.explainability.context_explanation import (
            ContextCompressionEntry,
            ContextExplanation,
            ContextIgnoredInputEntry,
            ContextWarningEntry,
        )

        trace = ChatContextResolutionTrace(
            source=inp.source,
            profile=inp.profile,
            mode=inp.mode,
            detail=inp.detail,
            fields=list(inp.fields),
            policy=inp.policy,
            hint=inp.hint,
            chat_policy=inp.chat_policy,
            project_policy=inp.project_policy,
            profile_enabled=inp.profile_enabled,
            limits_source=inp.limits_source,
            max_project_chars=inp.max_project_chars,
            max_chat_chars=inp.max_chat_chars,
            max_topic_chars=inp.max_topic_chars,
            max_total_lines=inp.max_total_lines,
            explanation=None,
        )
        base_explanation: Any = getattr(inp, "base_explanation", None) or trace.explanation or ContextExplanation()

        def _ensure_trace_has_explanation(t: Any) -> Any:
            """Guarantee trace.explanation is not None when return_trace=True."""
            if t.explanation is not None:
                return t
            from app.context.explainability.context_explanation import (
                ContextResolvedSettingEntry,
                ContextSettingCandidate,
            )
            _src = t.source or "explanation_fallback"
            _cand = ContextSettingCandidate(priority_index=0, source=_src, value=None, applied=True, skipped_reason=None)
            minimal = ContextExplanation(
                resolved_settings=[
                    ContextResolvedSettingEntry("mode", t.mode, _src, [_cand], False),
                    ContextResolvedSettingEntry("detail_level", t.detail, _src, [_cand], False),
                    ContextResolvedSettingEntry("policy", t.policy, _src, [_cand], False),
                ],
                empty_result=True,
                empty_result_reason="explanation_fallback",
            )
            return dataclasses.replace(t, explanation=minimal)

        def _failsafe_warning(
            warning_type: str,
            message: str = "",
            *,
            source_type: Optional[str] = None,
            source_id: Optional[str] = None,
            effect: Optional[str] = None,
            dropped_tokens: Optional[int] = None,
        ):
            return ContextWarningEntry(
                warning_type=warning_type,
                message=message,
                source_type=source_type,
                source_id=source_id,
                effect=effect,
                dropped_tokens=dropped_tokens,
            )

        def _attach_explanation(
            sources=None,
            compressions=None,
            warnings=None,
            ignored_inputs_extra=None,
            empty_result=None,
            empty_result_reason=None,
        ):
            src = sources if sources is not None else base_explanation.sources
            comp = compressions if compressions is not None else base_explanation.compressions
            warn = warnings if warnings is not None else base_explanation.warnings
            ignored = list(base_explanation.ignored_inputs)
            if ignored_inputs_extra:
                ignored.extend(ignored_inputs_extra)
            dropped_by, dropped_total, dropped_reasons = _build_dropped_context_report(
                src, comp, warn, trace, render_options
            )
            total_tokens_after_val = sum(
                (s.budget_used or 0) // CHARS_PER_TOKEN
                for s in src
                if s.included
            ) if src else None
            failsafe_types = (
                "failsafe",
                "header_only_fragment_removed",
                "marker_only_fragment_removed",
                "empty_injection_prevented",
            )
            failsafe_triggered = any(
                getattr(w, "warning_type", "") in failsafe_types
                or getattr(w, "effect", None) in ("removed_fragment", "skipped_injection")
                for w in warn
            )
            new_expl = dataclasses.replace(
                base_explanation,
                sources=src,
                compressions=comp,
                warnings=warn,
                ignored_inputs=ignored,
                dropped_by_source=dropped_by,
                dropped_total_tokens=dropped_total,
                dropped_reasons=dropped_reasons,
                total_tokens_after=total_tokens_after_val,
                warning_count=len(warn),
                failsafe_triggered=failsafe_triggered,
                empty_result=empty_result if empty_result is not None else base_explanation.empty_result,
                empty_result_reason=empty_result_reason if empty_result_reason is not None else base_explanation.empty_result_reason,
            )
            return dataclasses.replace(trace, explanation=new_expl)

        if context.is_empty():
            trace = _attach_explanation(
                warnings=base_explanation.warnings
                + [_failsafe_warning("empty_injection_prevented", "context_empty", effect="skipped_injection")],
                empty_result=True,
                empty_result_reason="no_sources",
            )
            result = _ensure_trace_has_explanation(trace) if return_trace else trace.explanation
            if return_fragment:
                return (result, None, context, render_options)
            return result

        source_not_found_entries = []
        if context.project_id is not None and not (context.project_name or "").strip():
            source_not_found_entries.append(
                ContextIgnoredInputEntry(
                    input_name="project",
                    input_source="project",
                    raw_value=str(context.project_id),
                    reason="source_not_found",
                    resolution_effect="ignored",
                )
            )
        if context.topic_id is not None and not (context.topic_name or "").strip():
            source_not_found_entries.append(
                ContextIgnoredInputEntry(
                    input_name="topic",
                    input_source="topic",
                    raw_value=str(context.topic_id),
                    reason="source_not_found",
                    resolution_effect="ignored",
                )
            )

        overflow_info: Dict[str, bool] = {}
        failsafe_info: Dict[str, str] = {}
        fragment = context.to_system_prompt_fragment(
            mode,
            detail,
            render_options,
            render_limits,
            _overflow_info=overflow_info,
            _failsafe_info=failsafe_info,
        )
        overflow_warnings = []
        if overflow_info.get("budget_overflow_prevented"):
            overflow_warnings.append(
                ContextWarningEntry("budget_overflow_prevented", "line_limit_truncated")
            )
        if overflow_info.get("budget_exhausted_before_optional_sources"):
            overflow_warnings.append(
                ContextWarningEntry(
                    "budget_exhausted_before_optional_sources",
                    "topic_cut_by_line_limit",
                )
            )
        if not fragment.strip():
            empty_entries = source_not_found_entries + [
                ContextIgnoredInputEntry(
                    input_name="context_fragment",
                    input_source="render",
                    raw_value="",
                    reason="empty_source",
                    resolution_effect="ignored",
                ),
            ]
            reason = failsafe_info.get("reason", "empty_injection_prevented")
            all_excluded = (
                not render_options.include_project
                and not render_options.include_chat
                and not render_options.include_topic
            )
            budget_related = overflow_info.get("budget_exhausted_before_optional_sources") or overflow_info.get(
                "budget_overflow_prevented"
            )
            if all_excluded:
                empty_reason = "excluded_by_policy"
            elif budget_related:
                empty_reason = "budget_exhausted"
            else:
                empty_reason = "failsafe_cleanup"
            trace = _attach_explanation(
                warnings=base_explanation.warnings
                + overflow_warnings
                + [_failsafe_warning(reason, "fragment_empty", effect="removed_fragment")],
                ignored_inputs_extra=empty_entries,
                empty_result=True,
                empty_result_reason=empty_reason,
            )
            result = _ensure_trace_has_explanation(trace) if return_trace else trace.explanation
            if return_fragment:
                return (result, fragment, context, render_options)
            return result

        sources = _build_context_sources(fragment, context, render_options, render_limits)
        proj_raw = context.project_name or "Unbekannt"
        chat_raw = context.chat_title or "Unbekannt"
        topic_raw = context.topic_name or "—"
        stats = get_context_fragment_stats(fragment)
        before_chars = sum([
            len(proj_raw) if render_options.include_project else 0,
            len(chat_raw) if render_options.include_chat else 0,
            len(topic_raw) if render_options.include_topic else 0,
        ])
        after_chars = stats["chars"]
        before_tokens = before_chars // 4 if before_chars else None
        after_tokens = after_chars // 4 if after_chars else None
        dropped_tokens = (
            (before_tokens - after_tokens)
            if before_tokens and after_tokens and before_tokens > after_tokens
            else None
        )
        compressions = [
            ContextCompressionEntry(
                operation="truncate",
                original_chars=before_chars,
                final_chars=after_chars,
                before_tokens=before_tokens,
                after_tokens=after_tokens,
                dropped_tokens=dropped_tokens,
                reason="limits",
            ),
        ]
        trace = _attach_explanation(
            sources=sources,
            compressions=compressions,
            warnings=base_explanation.warnings + overflow_warnings,
        )
        result = _ensure_trace_has_explanation(trace) if return_trace else trace.explanation
        if return_fragment:
            return (result, fragment, context, render_options)
        return result

    def get_context_payload_fragment(
        self,
        chat_id: int,
        request_context_hint: Optional["RequestContextHint"] = None,
        context_policy: Optional["ChatContextPolicy"] = None,
    ) -> tuple[Optional[str], Optional[Any], Optional[Any]]:
        """
        Liefert das assemblierte Kontext-Fragment für Preview (read-only).

        Returns:
            (fragment, context, render_options) oder (None, None, None) wenn leer/off.
        """
        from app.chat.context import build_chat_context
        from app.chats.models import get_chat_context_policy
        from app.core.config.settings import ChatContextMode
        from app.services.project_service import get_project_service

        chat_context_policy = None
        project_context_policy = None
        if chat_id:
            chat_info = self._infra.database.get_chat_info(chat_id)
            chat_context_policy = get_chat_context_policy(chat_info)
            project_context_policy = get_project_service().get_project_context_policy_for_chat(
                chat_id
            )

        mode, detail, render_options, _trace, render_limits = self._resolve_context_configuration(
            request_context_hint,
            context_policy,
            chat_context_policy,
            project_context_policy,
        )

        if mode == ChatContextMode.OFF:
            return (None, None, None)

        context = build_chat_context(chat_id)
        if context.is_empty():
            return (None, context, render_options)

        fragment = context.to_system_prompt_fragment(
            mode, detail, render_options, render_limits
        )
        if not fragment or not fragment.strip():
            return (None, context, render_options)

        return (fragment, context, render_options)

    async def close(self) -> None:
        """Schließt den Ollama-Client."""
        await self._infra.ollama_client.close()


_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Liefert den globalen ChatService."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


def set_chat_service(service: Optional[ChatService]) -> None:
    """Setzt den ChatService (beim App-Start oder für Tests)."""
    global _chat_service
    _chat_service = service
