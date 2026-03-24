"""QQmlComponent smoke: PromptStage + promptStudio context."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def qml_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "qml"
    assert root.is_dir()
    return root


def test_prompt_stage_qml_instantiates(qapplication, qml_root: Path) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent, QQmlEngine

    from python_bridge.prompts.prompt_viewmodel import build_prompt_viewmodel

    eng = QQmlEngine()
    eng.addImportPath(str(qml_root))
    eng.rootContext().setContextProperty("promptStudio", build_prompt_viewmodel())
    path = qml_root / "domains" / "prompts" / "PromptStage.qml"
    comp = QQmlComponent(eng, QUrl.fromLocalFile(str(path.resolve())))
    obj = comp.create()
    assert obj is not None, comp.errorString()


def test_prompt_viewmodel_select_and_save_roundtrip(qapplication, tmp_path, monkeypatch) -> None:
    from app.prompts.prompt_models import Prompt
    from app.prompts.prompt_service import PromptService, set_prompt_service

    db = tmp_path / "t.db"
    svc = PromptService(db_path=str(db))
    set_prompt_service(svc)
    try:
        from python_bridge.prompts.prompt_presenter_facade import PromptPresenterFacade
        from python_bridge.prompts.prompt_viewmodel import PromptViewModel

        class _Port:
            def list_prompts(self, filter_text: str = ""):
                return svc.list_all(filter_text=filter_text or "")

            def get_prompt(self, prompt_id: int):
                return svc.get(prompt_id)

            def create_prompt(self, prompt):
                return svc.create(prompt)

            def update_prompt(self, prompt):
                return svc.update(prompt)

            def list_prompt_versions(self, prompt_id: int):
                return svc.list_versions(prompt_id)

        vm = PromptViewModel(PromptPresenterFacade(port=_Port()))
        created = svc.create(
            Prompt(
                id=None,
                title="Alpha",
                category="code",
                description="d",
                content="Hello {user}",
                tags=["x"],
                prompt_type="user",
                scope="global",
                project_id=None,
                created_at=None,
                updated_at=None,
            )
        )
        assert created is not None and created.id is not None
        iid = int(created.id)
        vm.selectPrompt(iid)
        assert vm.selectedPrompt.title == "Alpha"
        vm.selectedPrompt.content = "Hi {user}"
        vm.savePrompt()
        vm.reload()
        vm.selectPrompt(iid)
        assert vm.selectedPrompt.content == "Hi {user}"
    finally:
        set_prompt_service(None)
