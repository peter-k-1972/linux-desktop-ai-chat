"""ServicePromptStudioAdapter — Slice 1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _P:
    id: int
    title: str = "T"


class _Backend:
    def list_project_prompts(self, project_id: int, filter_text: str = ""):  # noqa: ANN001
        del filter_text
        if project_id == 1:
            return [_P(10)]
        return []

    def list_global_prompts(self, filter_text: str = ""):  # noqa: ANN001
        del filter_text
        return [_P(20)]


class _Svc:
    def __init__(self) -> None:
        self._b = _Backend()

    def list_project_prompts(self, project_id: int, filter_text: str = ""):  # noqa: ANN001
        return self._b.list_project_prompts(project_id, filter_text)

    def list_global_prompts(self, filter_text: str = ""):  # noqa: ANN001
        return self._b.list_global_prompts(filter_text)

    def count_versions(self, pid: int) -> int:  # noqa: ANN001
        return 2 if pid == 10 else 1


def test_adapter_empty_when_no_prompts(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    class _Empty:
        def list_project_prompts(self, *a, **k):  # noqa: ANN002
            return []

        def list_global_prompts(self, *a, **k):  # noqa: ANN002
            return []

        def count_versions(self, pid: int) -> int:  # noqa: ANN001
            return 1

    monkeypatch.setattr(
        "app.prompts.prompt_service.get_prompt_service",
        lambda: _Empty(),
    )
    ad = ServicePromptStudioAdapter()
    v = ad.load_prompt_list(None, "")
    assert v.phase == "empty"
    assert "Projekt" in (v.empty_hint or "")
    assert ad.last_prompt_list_models == ()


def test_adapter_ready_rows_and_models(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    monkeypatch.setattr(
        "app.prompts.prompt_service.get_prompt_service",
        lambda: _Svc(),
    )
    ad = ServicePromptStudioAdapter()
    v = ad.load_prompt_list(1, "")
    assert v.phase == "ready"
    assert len(v.rows) == 2
    assert v.rows[0].list_section == "project"
    assert v.rows[0].version_count == 2
    assert v.rows[1].list_section == "global"
    assert all(r.version_count >= 1 for r in v.rows)
    assert len(ad.last_prompt_list_models) == 2


def test_adapter_error(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    def _boom():
        raise RuntimeError("x")

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", _boom)
    v = ServicePromptStudioAdapter().load_prompt_list(1, "")
    assert v.phase == "error"
    assert v.error is not None


def test_adapter_load_prompt_versions(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    class _S:
        def list_versions(self, pid: int):  # noqa: ANN001
            assert pid == 9
            return [{"version": 1, "title": "a", "content": "b", "created_at": None}]

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    st = ServicePromptStudioAdapter().load_prompt_versions(9)
    assert st.phase == "ready"
    assert len(st.rows) == 1
    assert st.rows[0].version == 1


def test_adapter_load_prompt_versions_empty(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    class _S:
        def list_versions(self, pid: int):  # noqa: ANN001
            return []

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    st = ServicePromptStudioAdapter().load_prompt_versions(1)
    assert st.phase == "empty"


def test_adapter_load_prompt_templates(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    @dataclass
    class _Tpl:
        id: int = 55
        title: str = "Tpl"

    class _S:
        def list_templates(self, project_id=None, filter_text=""):  # noqa: ANN001
            return [_Tpl()]

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    ad = ServicePromptStudioAdapter()
    st = ad.load_prompt_templates(1, "")
    assert st.phase == "ready"
    assert len(st.rows) == 1
    assert ad.last_prompt_template_models[0].id == 55


@dataclass
class _PromptEnt:
    id: int
    title: str = "T"
    content: str = ""
    description: str = ""
    category: str = "general"
    scope: str = "global"
    project_id: int | None = None
    prompt_type: str = "user"
    tags: list | None = None
    created_at: object | None = None
    updated_at: object | None = None

    def __post_init__(self) -> None:
        if self.tags is None:
            object.__setattr__(self, "tags", [])


def test_adapter_persist_save_version(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_editor import SavePromptVersionEditorCommand

    p0 = _PromptEnt(id=7, title="old", content="x")

    class _S:
        def get(self, pid: int):  # noqa: ANN001
            return p0 if pid == 7 else None

        def save_version(self, p, title, content):  # noqa: ANN001
            return _PromptEnt(id=7, title=title, content=content)

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    ad = ServicePromptStudioAdapter()
    r = ad.persist_prompt_editor(SavePromptVersionEditorCommand(prompt_id=7, title="n", content="c"))
    assert r.phase == "success"
    assert r.snapshot is not None
    assert r.snapshot.title == "n"


def test_adapter_persist_update_metadata(monkeypatch) -> None:
    from app.prompts.prompt_models import Prompt
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_editor import UpdatePromptMetadataEditorCommand

    existing = _PromptEnt(id=3, title="a", content="b", tags=["t"])
    current: list = [existing]

    class _S:
        def get(self, pid: int):  # noqa: ANN001
            if pid != 3:
                return None
            return current[0]

        def update(self, p: Prompt) -> bool:  # noqa: ANN001
            current[0] = _PromptEnt(
                id=p.id,
                title=p.title,
                content=p.content,
                description=p.description,
                category=p.category,
                scope=p.scope,
                project_id=p.project_id,
                prompt_type=p.prompt_type,
                tags=list(p.tags or []),
            )
            return True

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    ad = ServicePromptStudioAdapter()
    cmd = UpdatePromptMetadataEditorCommand(
        prompt_id=3,
        title="n",
        content="nc",
        description="d",
        category="code",
        scope="global",
        project_id=None,
    )
    r = ad.persist_prompt_editor(cmd)
    assert r.phase == "success"
    assert r.snapshot is not None
    assert r.snapshot.title == "n"


def test_adapter_create_and_open_workspace(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    created = _PromptEnt(id=99, title="new", content="body")

    class _S:
        def create(self, p):  # noqa: ANN001
            return created

        def get(self, pid: int):  # noqa: ANN001
            return created if pid == 99 else None

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    ad = ServicePromptStudioAdapter()
    cr = ad.create_user_prompt_for_studio("new", "body", scope="global", project_id=None)
    assert cr.ok and cr.snapshot is not None
    assert cr.snapshot.prompt_id == 99
    op = ad.open_prompt_snapshot_for_studio(99)
    assert op.ok and op.snapshot is not None


def test_adapter_test_lab_prompts(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_test_lab import LoadPromptTestLabPromptsCommand

    monkeypatch.setattr(
        "app.prompts.prompt_service.get_prompt_service",
        lambda: _Svc(),
    )
    ad = ServicePromptStudioAdapter()
    st = ad.load_prompt_test_lab_prompts(LoadPromptTestLabPromptsCommand(1))
    assert st.phase == "ready"
    assert len(st.rows) == 2
    assert {r.prompt_id for r in st.rows} == {10, 20}


def test_adapter_test_lab_versions(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_test_lab import LoadPromptTestLabVersionsCommand

    class _S:
        def list_versions(self, pid: int):  # noqa: ANN001
            return [{"version": 1, "title": "t", "content": "c", "created_at": None}]

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    ad = ServicePromptStudioAdapter()
    st = ad.load_prompt_test_lab_versions(LoadPromptTestLabVersionsCommand(5))
    assert st.phase == "ready"
    assert len(st.rows) == 1
    assert st.rows[0].content == "c"


async def test_adapter_test_lab_models_ready(monkeypatch) -> None:
    from app.services.result import ServiceResult
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_test_lab import LoadPromptTestLabModelsCommand

    class _MS:
        async def get_models(self):  # noqa: ANN001
            return ServiceResult(success=True, data=["a", "b"])

        def get_default_model(self) -> str:
            return "b"

    monkeypatch.setattr(
        "app.services.model_service.get_model_service",
        lambda: _MS(),
    )
    ad = ServicePromptStudioAdapter()
    st = await ad.load_prompt_test_lab_models(LoadPromptTestLabModelsCommand())
    assert st.phase == "ready"
    assert st.models == ("a", "b")
    assert st.default_model == "b"


def test_adapter_delete_prompt_library_entry(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter

    class _S:
        def __init__(self) -> None:
            self.deleted: list[int] = []

        def delete(self, pid: int) -> bool:  # noqa: ANN001
            self.deleted.append(pid)
            return True

    svc = _S()
    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: svc)
    ad = ServicePromptStudioAdapter()
    r = ad.delete_prompt_library_entry(3)
    assert r.ok
    assert svc.deleted == [3]


def test_adapter_create_update_delete_prompt_template(monkeypatch) -> None:
    from app.prompts.prompt_models import Prompt
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_templates import (
        CreatePromptTemplateCommand,
        DeletePromptTemplateCommand,
        UpdatePromptTemplateCommand,
    )

    store: dict[int, _PromptEnt] = {
        1: _PromptEnt(
            id=1,
            title="old",
            content="c",
            description="d",
            prompt_type="template",
            scope="project",
            project_id=5,
        ),
    }

    class _S:
        def create(self, p: Prompt):  # noqa: ANN001
            assert p.prompt_type == "template"
            ent = _PromptEnt(
                id=99,
                title=p.title,
                content=p.content or "",
                description=p.description or "",
                prompt_type="template",
                scope=p.scope,
                project_id=p.project_id,
            )
            store[99] = ent
            return ent

        def get(self, pid: int):  # noqa: ANN001
            return store.get(pid)

        def update(self, p: Prompt) -> bool:  # noqa: ANN001
            if p.id not in store:
                return False
            store[p.id] = _PromptEnt(
                id=p.id,
                title=p.title,
                content=p.content or "",
                description=p.description or "",
                category=p.category,
                prompt_type="template",
                scope=p.scope,
                project_id=p.project_id,
                tags=list(p.tags or []),
                created_at=store[p.id].created_at,
            )
            return True

        def delete(self, pid: int) -> bool:  # noqa: ANN001
            return store.pop(pid, None) is not None

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    ad = ServicePromptStudioAdapter()
    cr = ad.create_prompt_template(
        CreatePromptTemplateCommand("n", "d", "body", "project", 5),
    )
    assert cr.ok
    up = ad.update_prompt_template(
        UpdatePromptTemplateCommand(1, "t2", "d2", "c2"),
    )
    assert up.ok
    assert store[1].title == "t2"
    dl = ad.delete_prompt_template(DeletePromptTemplateCommand(99))
    assert dl.ok
    assert 99 not in store


def test_adapter_copy_template_to_user_prompt(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_templates import CopyPromptTemplateCommand

    src = _PromptEnt(id=7, title="Src", content="body", prompt_type="template")

    class _S:
        def get(self, pid: int):  # noqa: ANN001
            return src if pid == 7 else None

        def create(self, p):  # noqa: ANN001
            return _PromptEnt(id=12, title=p.title, content=p.content, prompt_type="user")

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    ad = ServicePromptStudioAdapter()
    r = ad.copy_template_to_user_prompt(
        CopyPromptTemplateCommand(source_template_id=7, scope="global", project_id=None),
    )
    assert r.ok and r.snapshot is not None
    assert r.snapshot.prompt_id == 12


async def test_adapter_stream_prompt_test_lab_run(monkeypatch) -> None:
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_contracts.workspaces.prompt_studio_test_lab import (
        PromptTestLabStreamChunkDto,
        RunPromptTestLabCommand,
    )

    class _CS:
        async def chat(self, **kwargs):  # noqa: ANN003
            yield {"message": {"content": "a"}}
            yield {"error": "e1"}

    monkeypatch.setattr(
        "app.services.chat_service.get_chat_service",
        lambda: _CS(),
    )
    ad = ServicePromptStudioAdapter()
    out: list[PromptTestLabStreamChunkDto] = []
    async for dto in ad.stream_prompt_test_lab_run(
        RunPromptTestLabCommand("m", "sys", "user", 0.5, 100),
    ):
        out.append(dto)
    assert len(out) == 2
    assert out[0].content_delta == "a"
    assert out[1].stream_error == "e1"
