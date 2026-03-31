"""ServiceProjectsOverview*Adapter — Slice 1 Basismapping."""

from __future__ import annotations

from app.ui_application.adapters.service_projects_overview_command_adapter import (
    ServiceProjectsOverviewCommandAdapter,
)
from app.ui_application.adapters.service_projects_overview_read_adapter import (
    ServiceProjectsOverviewReadAdapter,
)


class _FakeProjectService:
    def __init__(self) -> None:
        self._active_project_id = 2
        self._active_project = {
            "project_id": 2,
            "name": "Aktiv",
            "lifecycle_status": "active",
        }
        self._projects = [
            {
                "project_id": 2,
                "name": "Aktiv",
                "description": "Desc",
                "status": "active",
                "lifecycle_status": "active",
                "updated_at": "2026-03-31T10:15:00+00:00",
                "created_at": "2026-03-01T08:00:00+00:00",
                "customer_name": "Acme",
                "internal_code": "AC-1",
                "default_context_policy": "architecture",
                "budget_amount": 10,
                "budget_currency": "EUR",
                "estimated_effort_hours": 5,
            }
        ]
        self.set_active_calls: list[int | None] = []
        self.clear_calls = 0

    def list_projects(self, filter_text: str = ""):
        if not filter_text:
            return list(self._projects)
        ft = filter_text.lower()
        return [p for p in self._projects if ft in str(p.get("name", "")).lower()]

    def get_project(self, project_id: int):
        for p in self._projects:
            if int(p["project_id"]) == int(project_id):
                return dict(p)
        return None

    def get_active_project_id(self):
        return self._active_project_id

    def get_active_project(self):
        return dict(self._active_project)

    def count_workflows_of_project(self, project_id: int) -> int:
        return 4

    def count_chats_of_project(self, project_id: int) -> int:
        return 5

    def count_agents_of_project(self, project_id: int) -> int:
        return 6

    def count_files_of_project(self, project_id: int) -> int:
        return 7

    def count_prompts_of_project(self, project_id: int) -> int:
        return 8

    def get_project_monitoring_snapshot(self, project_id: int):
        return {
            "last_activity_at": "2026-03-30T12:00:00+00:00",
            "message_count_7d": 3,
            "message_count_30d": 4,
            "active_chats_30d": 2,
            "last_workflow_run_at": "2026-03-29T09:00:00+00:00",
            "last_workflow_run_status": "completed",
            "failed_workflow_runs_30d": 1,
            "source_count": 2,
        }

    def get_recent_project_activity(self, project_id: int, chat_limit: int = 5, prompt_limit: int = 5):
        class _Prompt:
            id = 11
            title = "Prompt A"
            updated_at = None
            created_at = None

        return {
            "recent_chats": [
                {"chat_id": 9, "title": "Chat A", "updated_at": "2026-03-31T11:00:00+00:00"},
            ],
            "recent_prompts": [_Prompt()],
            "sources": [{"source_path": "/tmp/spec.md", "status": "ready"}],
        }

    def list_project_milestones(self, project_id: int):
        return [
            {"milestone_id": 1, "name": "Kickoff", "target_date": "2026-04-15", "status": "open"},
        ]

    def set_active_project(self, project_id=None, project=None):
        del project
        self.set_active_calls.append(project_id)

    def clear_active_project(self):
        self.clear_calls += 1


def test_read_adapter_load_project_list(monkeypatch) -> None:
    fake = _FakeProjectService()
    monkeypatch.setattr(
        "app.ui_application.adapters.service_projects_overview_read_adapter.get_project_service",
        lambda: fake,
    )
    ad = ServiceProjectsOverviewReadAdapter()
    result = ad.load_project_list("", active_project_id=2, selected_project_id=2)
    assert len(result.items) == 1
    assert result.items[0].is_active is True
    assert result.items[0].is_selected is True


def test_read_adapter_load_project_overview(monkeypatch) -> None:
    fake = _FakeProjectService()
    monkeypatch.setattr(
        "app.ui_application.adapters.service_projects_overview_read_adapter.get_project_service",
        lambda: fake,
    )
    ad = ServiceProjectsOverviewReadAdapter()
    state = ad.load_project_overview(2)
    assert state is not None
    assert state.stats.workflow_count == 4
    assert state.activity.has_any_activity is True
    assert state.controlling.budget_label == "10 EUR"


def test_command_adapter_set_active(monkeypatch) -> None:
    fake = _FakeProjectService()
    monkeypatch.setattr(
        "app.ui_application.adapters.service_projects_overview_command_adapter.get_project_service",
        lambda: fake,
    )
    ad = ServiceProjectsOverviewCommandAdapter()
    result = ad.set_active_project(2)
    assert result.ok is True
    assert fake.set_active_calls == [2]


def test_command_adapter_clear_active(monkeypatch) -> None:
    fake = _FakeProjectService()
    monkeypatch.setattr(
        "app.ui_application.adapters.service_projects_overview_command_adapter.get_project_service",
        lambda: fake,
    )
    ad = ServiceProjectsOverviewCommandAdapter()
    result = ad.set_active_project(None)
    assert result.ok is True
    assert fake.clear_calls == 1
