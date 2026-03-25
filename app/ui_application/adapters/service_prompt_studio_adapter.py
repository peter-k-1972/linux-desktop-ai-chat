"""
Adapter: PromptService → Prompt-Listen-View (Slice 1) + Detail-DTO (Slice 2).

Technische Schuld: ``last_prompt_list_models`` hält ``Prompt``-Objekte parallel zu ``rows`` für
``PromptListItem`` / Signale — nicht im Port spezifiziert.
"""

from __future__ import annotations

import logging
from typing import Any

from app.ui_contracts.workspaces.prompt_studio_detail import PromptDetailDto
from app.ui_contracts.workspaces.prompt_studio_editor import (
    PromptEditorPersistCommand,
    PromptEditorSaveResultState,
    PromptStudioPromptSnapshotDto,
    SavePromptVersionEditorCommand,
    UpdatePromptMetadataEditorCommand,
)
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult
from app.ui_contracts.workspaces.prompt_studio_library import PromptLibraryMutationResult
from app.ui_contracts.workspaces.prompt_studio_list import (
    PromptListEntryDto,
    PromptStudioListState,
)
from app.ui_contracts.workspaces.prompt_studio_templates import (
    CopyPromptTemplateCommand,
    CreatePromptTemplateCommand,
    DeletePromptTemplateCommand,
    PromptTemplateMutationResult,
    PromptTemplateRowDto,
    PromptTemplatesState,
    UpdatePromptTemplateCommand,
)
from app.ui_contracts.workspaces.prompt_studio_versions import (
    PromptVersionPanelState,
    PromptVersionRowDto,
)
from app.ui_contracts.common.errors import SettingsErrorInfo
from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    LoadPromptTestLabModelsCommand,
    LoadPromptTestLabPromptsCommand,
    LoadPromptTestLabVersionsCommand,
    PromptTestLabModelsState,
    PromptTestLabPromptRowDto,
    PromptTestLabPromptsState,
    PromptTestLabStreamChunkDto,
    PromptTestLabVersionRowDto,
    PromptTestLabVersionsState,
    RunPromptTestLabCommand,
)

logger = logging.getLogger(__name__)


def _format_last_modified(dt: object | None) -> str | None:
    if dt is None:
        return None
    try:
        if hasattr(dt, "isoformat"):
            return str(dt.isoformat())
        return str(dt)
    except Exception:
        return str(dt)


def _prompt_entity_to_snapshot(p: Any) -> PromptStudioPromptSnapshotDto:
    tags_raw = getattr(p, "tags", None) or []
    tags = tuple(str(t) for t in tags_raw)
    return PromptStudioPromptSnapshotDto(
        prompt_id=int(p.id),
        title=str(p.title or ""),
        content=str(p.content or ""),
        description=str(getattr(p, "description", "") or ""),
        category=str(getattr(p, "category", "") or "general"),
        scope=str(getattr(p, "scope", "") or "global"),
        project_id=getattr(p, "project_id", None),
        prompt_type=str(getattr(p, "prompt_type", "") or "user"),
        tags=tags,
    )


def _version_row_from_dict(d: dict[str, Any]) -> PromptVersionRowDto:
    created = d.get("created_at")
    iso: str | None = None
    if created is not None:
        try:
            if hasattr(created, "isoformat"):
                iso = str(created.isoformat())
            else:
                iso = str(created)
        except Exception:
            iso = str(created)
    return PromptVersionRowDto(
        version=int(d.get("version") or 0),
        title=str(d.get("title") or ""),
        content=str(d.get("content") or ""),
        created_at_iso=iso,
    )


class ServicePromptStudioAdapter:
    """Delegiert an ``get_prompt_service()``."""

    def __init__(self) -> None:
        self._last_prompt_list_models: list[Any] = []
        self._last_prompt_template_models: list[Any] = []

    @property
    def last_prompt_list_models(self) -> tuple[Any, ...]:
        return tuple(self._last_prompt_list_models)

    @property
    def last_prompt_template_models(self) -> tuple[Any, ...]:
        return tuple(self._last_prompt_template_models)

    def load_prompt_list(
        self,
        project_id: int | None,
        filter_text: str = "",
    ) -> PromptStudioListState:
        self._last_prompt_list_models = []
        ft = (filter_text or "").strip()
        try:
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            project_prompts: list = []
            if project_id is not None:
                project_prompts = svc.list_project_prompts(project_id, ft)
            global_prompts = svc.list_global_prompts(ft)
        except Exception as exc:
            logger.warning("Prompt-Liste laden fehlgeschlagen: %s", exc, exc_info=True)
            self._last_prompt_list_models = []
            return PromptStudioListState(
                phase="error",
                error=SettingsErrorInfo(
                    code="load_prompt_list_failed",
                    message="Prompts konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
            )

        if not project_prompts and not global_prompts:
            if project_id is None:
                hint = "Bitte Projekt auswählen."
            elif not ft:
                hint = "Keine Prompts. Klicken Sie auf + New Prompt."
            else:
                hint = "Keine Treffer für die Suche."
            return PromptStudioListState(phase="empty", empty_hint=hint)

        rows: list[PromptListEntryDto] = []
        models: list[Any] = []

        for p in project_prompts:
            pid = getattr(p, "id", None)
            if pid is None:
                continue
            vc = 1
            try:
                vc = max(1, int(svc.count_versions(int(pid))))
            except Exception:
                vc = 1
            rows.append(
                PromptListEntryDto(
                    prompt_id=int(pid),
                    list_section="project",
                    version_count=vc,
                ),
            )
            models.append(p)

        for p in global_prompts:
            pid = getattr(p, "id", None)
            if pid is None:
                continue
            vc = 1
            try:
                vc = max(1, int(svc.count_versions(int(pid))))
            except Exception:
                vc = 1
            rows.append(
                PromptListEntryDto(
                    prompt_id=int(pid),
                    list_section="global",
                    version_count=vc,
                ),
            )
            models.append(p)

        self._last_prompt_list_models = models
        return PromptStudioListState(phase="ready", rows=tuple(rows))

    def load_prompt_detail(self, prompt_id: str, project_id: str | None) -> PromptDetailDto:
        del project_id  # reserviert für spätere Scope-Prüfungen
        pid_str = (prompt_id or "").strip()
        if not pid_str:
            raise ValueError("prompt_id darf nicht leer sein.")
        try:
            pid_int = int(pid_str)
        except ValueError as exc:
            raise ValueError(f"Ungültige prompt_id: {prompt_id!r}") from exc

        try:
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            p = svc.get(pid_int)
        except Exception as exc:
            logger.warning("Prompt-Detail laden fehlgeschlagen: %s", exc, exc_info=True)
            raise RuntimeError("Prompt-Details konnten nicht geladen werden.") from exc

        if p is None:
            raise LookupError("Prompt wurde nicht gefunden.")

        vc = 1
        try:
            vc = max(1, int(svc.count_versions(pid_int)))
        except Exception:
            vc = 1

        lm = _format_last_modified(getattr(p, "updated_at", None) or getattr(p, "created_at", None))
        return PromptDetailDto(
            prompt_id=str(pid_int),
            name=p.title or "",
            content=p.content or "",
            version_count=vc,
            last_modified=lm,
        )

    def load_prompt_versions(self, prompt_id: int) -> PromptVersionPanelState:
        try:
            from app.prompts.prompt_service import get_prompt_service

            raw = get_prompt_service().list_versions(prompt_id)
        except Exception as exc:
            logger.warning("Prompt-Versionen laden fehlgeschlagen: %s", exc, exc_info=True)
            return PromptVersionPanelState(
                phase="error",
                prompt_id=prompt_id,
                error=SettingsErrorInfo(
                    code="load_prompt_versions_failed",
                    message="Versionen konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
            )

        if not raw:
            return PromptVersionPanelState(phase="empty", prompt_id=prompt_id)
        rows = tuple(_version_row_from_dict(x) for x in raw if isinstance(x, dict))
        return PromptVersionPanelState(phase="ready", prompt_id=prompt_id, rows=rows)

    def load_prompt_templates(
        self,
        project_id: int | None,
        filter_text: str = "",
    ) -> PromptTemplatesState:
        self._last_prompt_template_models = []
        ft = (filter_text or "").strip()
        try:
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            templates = svc.list_templates(project_id=project_id, filter_text=ft)
        except Exception as exc:
            logger.warning("Templates laden fehlgeschlagen: %s", exc, exc_info=True)
            self._last_prompt_template_models = []
            return PromptTemplatesState(
                phase="error",
                error=SettingsErrorInfo(
                    code="load_prompt_templates_failed",
                    message="Templates konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
            )

        if not templates:
            if project_id is None:
                hint = "Keine Templates. Projekt auswählen."
            elif not ft:
                hint = "Keine Templates. Erstellen Sie ein neues."
            else:
                hint = "Keine Treffer für die Suche."
            return PromptTemplatesState(phase="empty", empty_hint=hint)

        rows: list[PromptTemplateRowDto] = []
        models: list[Any] = []
        for p in templates:
            pid = getattr(p, "id", None)
            if pid is None:
                continue
            rows.append(PromptTemplateRowDto(prompt_id=int(pid)))
            models.append(p)

        self._last_prompt_template_models = models
        return PromptTemplatesState(phase="ready", rows=tuple(rows))

    def persist_prompt_editor(self, command: PromptEditorPersistCommand) -> PromptEditorSaveResultState:
        try:
            from app.prompts.prompt_models import Prompt
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            if isinstance(command, SavePromptVersionEditorCommand):
                p = svc.get(command.prompt_id)
                if p is None:
                    return PromptEditorSaveResultState(phase="error", error_message="Prompt nicht gefunden.")
                saved = svc.save_version(p, command.title, command.content)
                if saved is None:
                    return PromptEditorSaveResultState(phase="error", error_message="Speichern fehlgeschlagen.")
                return PromptEditorSaveResultState(phase="success", snapshot=_prompt_entity_to_snapshot(saved))

            assert isinstance(command, UpdatePromptMetadataEditorCommand)
            existing = svc.get(command.prompt_id)
            if existing is None:
                return PromptEditorSaveResultState(phase="error", error_message="Prompt nicht gefunden.")
            updated = Prompt(
                id=command.prompt_id,
                title=command.title,
                category=command.category,
                description=command.description,
                content=command.content,
                tags=list(getattr(existing, "tags", []) or []),
                prompt_type=getattr(existing, "prompt_type", "user"),
                scope=command.scope,
                project_id=command.project_id,
                created_at=existing.created_at,
                updated_at=None,
            )
            if not svc.update(updated):
                return PromptEditorSaveResultState(phase="error", error_message="Update fehlgeschlagen.")
            saved = svc.get(command.prompt_id)
            if saved is None:
                return PromptEditorSaveResultState(
                    phase="error",
                    error_message="Prompt nach Update nicht lesbar.",
                )
            return PromptEditorSaveResultState(phase="success", snapshot=_prompt_entity_to_snapshot(saved))
        except Exception as exc:
            logger.warning("Prompt-Editor persist fehlgeschlagen: %s", exc, exc_info=True)
            return PromptEditorSaveResultState(phase="error", error_message=str(exc).strip()[:200])

    def create_user_prompt_for_studio(
        self,
        title: str,
        content: str,
        *,
        scope: str,
        project_id: int | None,
    ) -> PromptStudioWorkspaceOpResult:
        try:
            from app.prompts.prompt_models import Prompt
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            prompt = Prompt(
                id=None,
                title=title,
                category="general",
                description="",
                content=content,
                tags=[],
                prompt_type="user",
                scope=scope,
                project_id=project_id,
                created_at=None,
                updated_at=None,
            )
            created = svc.create(prompt)
            if created is None:
                return PromptStudioWorkspaceOpResult(ok=False, error_message="Anlage fehlgeschlagen.")
            return PromptStudioWorkspaceOpResult(ok=True, snapshot=_prompt_entity_to_snapshot(created))
        except Exception as exc:
            logger.warning("Prompt-Studio create fehlgeschlagen: %s", exc, exc_info=True)
            return PromptStudioWorkspaceOpResult(ok=False, error_message=str(exc).strip()[:200])

    def open_prompt_snapshot_for_studio(self, prompt_id: int) -> PromptStudioWorkspaceOpResult:
        try:
            from app.prompts.prompt_service import get_prompt_service

            p = get_prompt_service().get(prompt_id)
            if p is None:
                return PromptStudioWorkspaceOpResult(ok=False, error_message="Prompt nicht gefunden.")
            return PromptStudioWorkspaceOpResult(ok=True, snapshot=_prompt_entity_to_snapshot(p))
        except Exception as exc:
            logger.warning("Prompt-Studio open fehlgeschlagen: %s", exc, exc_info=True)
            return PromptStudioWorkspaceOpResult(ok=False, error_message=str(exc).strip()[:200])

    def load_prompt_test_lab_prompts(
        self,
        command: LoadPromptTestLabPromptsCommand,
    ) -> PromptTestLabPromptsState:
        try:
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            project_id = command.project_id
            if project_id is not None:
                prompts = svc.list_project_prompts(project_id, "") + svc.list_global_prompts("")
            else:
                prompts = svc.list_global_prompts("")
        except Exception as exc:
            logger.warning("Test-Lab Prompts laden fehlgeschlagen: %s", exc, exc_info=True)
            return PromptTestLabPromptsState(
                phase="error",
                error_message=str(exc).strip()[:200],
            )

        rows: list[PromptTestLabPromptRowDto] = []
        for p in prompts:
            pid = getattr(p, "id", None)
            if pid is None:
                continue
            title = getattr(p, "title", "") or "Unbenannt"
            rows.append(PromptTestLabPromptRowDto(prompt_id=int(pid), display_title=str(title)))
        return PromptTestLabPromptsState(phase="ready", rows=tuple(rows))

    @staticmethod
    def _test_lab_version_display_label(v: dict[str, Any]) -> str:
        ver_num = int(v.get("version") or 0)
        created = v.get("created_at")
        date_str = "—"
        if created is not None:
            try:
                if hasattr(created, "strftime"):
                    date_str = created.strftime("%d.%m.%Y")
                else:
                    date_str = str(created)[:10]
            except Exception:
                pass
        return f"v{ver_num} ({date_str})"

    def load_prompt_test_lab_versions(
        self,
        command: LoadPromptTestLabVersionsCommand,
    ) -> PromptTestLabVersionsState:
        pid = int(command.prompt_id)
        try:
            from app.prompts.prompt_service import get_prompt_service

            raw = get_prompt_service().list_versions(pid)
        except Exception as exc:
            logger.warning("Test-Lab Versionen laden fehlgeschlagen: %s", exc, exc_info=True)
            return PromptTestLabVersionsState(
                phase="error",
                prompt_id=pid,
                error_message=str(exc).strip()[:200],
            )

        rows: list[PromptTestLabVersionRowDto] = []
        for item in raw or []:
            if not isinstance(item, dict):
                continue
            rows.append(
                PromptTestLabVersionRowDto(
                    version=int(item.get("version") or 0),
                    display_label=self._test_lab_version_display_label(item),
                    title=str(item.get("title") or ""),
                    content=str(item.get("content") or ""),
                ),
            )
        return PromptTestLabVersionsState(phase="ready", prompt_id=pid, rows=tuple(rows))

    async def load_prompt_test_lab_models(
        self,
        command: LoadPromptTestLabModelsCommand,
    ) -> PromptTestLabModelsState:
        del command
        try:
            from app.services.model_service import get_model_service

            ms = get_model_service()
            result = await ms.get_models()
            if not result.success:
                return PromptTestLabModelsState(
                    phase="error",
                    error_message=(result.error or "Modelle konnten nicht geladen werden.")[:200],
                )
            models = tuple(str(m) for m in (result.data or []))
            default = ms.get_default_model()
            return PromptTestLabModelsState(
                phase="ready",
                models=models,
                default_model=(str(default).strip() if default else None),
            )
        except Exception as exc:
            logger.warning("Test-Lab Modelle laden fehlgeschlagen: %s", exc, exc_info=True)
            return PromptTestLabModelsState(phase="unreachable", error_message=str(exc).strip()[:200])

    async def stream_prompt_test_lab_run(
        self,
        command: RunPromptTestLabCommand,
    ):
        """Async-Generator: Chat-Service-Chunks → DTOs (Test Lab)."""
        try:
            from app.services.chat_service import get_chat_service

            messages = [
                {"role": "system", "content": command.system_prompt_text},
                {"role": "user", "content": command.user_message_text},
            ]
            async for chunk in get_chat_service().chat(
                model=command.model_name,
                messages=messages,
                temperature=command.temperature,
                max_tokens=command.max_tokens,
                stream=True,
            ):
                err = chunk.get("error")
                if err:
                    yield PromptTestLabStreamChunkDto(content_delta="", stream_error=str(err))
                    return
                msg = chunk.get("message") or {}
                part = msg.get("content") or ""
                if part:
                    yield PromptTestLabStreamChunkDto(content_delta=str(part), stream_error=None)
        except Exception as exc:
            logger.warning("Test-Lab Chat-Stream fehlgeschlagen: %s", exc, exc_info=True)
            yield PromptTestLabStreamChunkDto(content_delta="", stream_error=str(exc).strip()[:500])

    def delete_prompt_library_entry(self, prompt_id: int) -> PromptLibraryMutationResult:
        try:
            from app.prompts.prompt_service import get_prompt_service

            ok = bool(get_prompt_service().delete(int(prompt_id)))
            return PromptLibraryMutationResult(
                ok=ok,
                error_message=None if ok else "Löschen fehlgeschlagen.",
            )
        except Exception as exc:
            logger.warning("Library-Prompt löschen fehlgeschlagen: %s", exc, exc_info=True)
            return PromptLibraryMutationResult(ok=False, error_message=str(exc).strip()[:200])

    def create_prompt_template(self, command: CreatePromptTemplateCommand) -> PromptTemplateMutationResult:
        try:
            from app.prompts.prompt_models import Prompt
            from app.prompts.prompt_service import get_prompt_service

            p = Prompt(
                id=None,
                title=command.title,
                category="general",
                description=command.description,
                content=command.content,
                tags=[],
                prompt_type="template",
                scope=command.scope,
                project_id=command.project_id,
                created_at=None,
                updated_at=None,
            )
            created = get_prompt_service().create(p)
            if created is None:
                return PromptTemplateMutationResult(ok=False, error_message="Anlage fehlgeschlagen.")
            return PromptTemplateMutationResult(ok=True)
        except Exception as exc:
            logger.warning("Template anlegen fehlgeschlagen: %s", exc, exc_info=True)
            return PromptTemplateMutationResult(ok=False, error_message=str(exc).strip()[:200])

    def update_prompt_template(self, command: UpdatePromptTemplateCommand) -> PromptTemplateMutationResult:
        try:
            from app.prompts.prompt_models import Prompt
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            existing = svc.get(command.template_id)
            if existing is None:
                return PromptTemplateMutationResult(ok=False, error_message="Template nicht gefunden.")
            updated = Prompt(
                id=command.template_id,
                title=command.title,
                category=getattr(existing, "category", "general"),
                description=command.description,
                content=command.content,
                tags=list(getattr(existing, "tags", []) or []),
                prompt_type="template",
                scope=getattr(existing, "scope", "global"),
                project_id=getattr(existing, "project_id", None),
                created_at=getattr(existing, "created_at", None),
                updated_at=None,
            )
            if not svc.update(updated):
                return PromptTemplateMutationResult(ok=False, error_message="Update fehlgeschlagen.")
            return PromptTemplateMutationResult(ok=True)
        except Exception as exc:
            logger.warning("Template aktualisieren fehlgeschlagen: %s", exc, exc_info=True)
            return PromptTemplateMutationResult(ok=False, error_message=str(exc).strip()[:200])

    def copy_template_to_user_prompt(self, command: CopyPromptTemplateCommand) -> PromptStudioWorkspaceOpResult:
        try:
            from app.prompts.prompt_models import Prompt
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            src = svc.get(command.source_template_id)
            if src is None:
                return PromptStudioWorkspaceOpResult(ok=False, error_message="Template nicht gefunden.")
            new_prompt = Prompt(
                id=None,
                title=f"Von Template: {src.title or 'Unbenannt'}",
                category=getattr(src, "category", "general"),
                description=getattr(src, "description", "") or "",
                content=getattr(src, "content", "") or "",
                tags=list(getattr(src, "tags", []) or []),
                prompt_type="user",
                scope=command.scope,
                project_id=command.project_id,
                created_at=None,
                updated_at=None,
            )
            created = svc.create(new_prompt)
            if created is None:
                return PromptStudioWorkspaceOpResult(ok=False, error_message="Prompt konnte nicht erstellt werden.")
            return PromptStudioWorkspaceOpResult(ok=True, snapshot=_prompt_entity_to_snapshot(created))
        except Exception as exc:
            logger.warning("Template → Prompt kopieren fehlgeschlagen: %s", exc, exc_info=True)
            return PromptStudioWorkspaceOpResult(ok=False, error_message=str(exc).strip()[:200])

    def delete_prompt_template(self, command: DeletePromptTemplateCommand) -> PromptTemplateMutationResult:
        try:
            from app.prompts.prompt_service import get_prompt_service

            ok = bool(get_prompt_service().delete(int(command.template_id)))
            return PromptTemplateMutationResult(
                ok=ok,
                error_message=None if ok else "Löschen fehlgeschlagen.",
            )
        except Exception as exc:
            logger.warning("Template löschen fehlgeschlagen: %s", exc, exc_info=True)
            return PromptTemplateMutationResult(ok=False, error_message=str(exc).strip()[:200])
