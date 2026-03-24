"""Mapper: ChatDetailsPanelState aus Port-Lesevorgängen."""

from __future__ import annotations

from typing import Any

from app.ui_application.mappers.chat_details_mapper import (
    build_chat_details_panel_state,
    format_chat_details_timestamp,
)
from app.ui_contracts.workspaces.chat import empty_chat_details_panel_state


class _FakePort:
    def get_chat_info(self, chat_id: int) -> dict[str, Any] | None:
        if chat_id == 0:
            return None
        return {
            "title": "My chat",
            "topic_id": 5,
            "topic_name": "Alpha",
            "created_at": "2024-06-01T12:00:00",
            "last_activity": "2024-06-02T08:00:00",
            "pinned": 1,
            "archived": 0,
        }

    def project_id_for_chat(self, chat_id: int) -> int | None:
        return 10

    def get_project_record(self, project_id: int) -> dict[str, Any] | None:
        return {"name": "Proj X"}

    def list_topic_rows_for_project(self, project_id: int) -> list[dict[str, Any]]:
        return [{"id": 5, "name": "Alpha"}, {"id": 6, "name": "Beta"}]

    def get_last_assistant_agent_for_chat(self, chat_id: int) -> str | None:
        return "agent-a"


def test_format_chat_details_timestamp_none():
    assert format_chat_details_timestamp(None) == "—"


def test_build_state_none_chat_id():
    p = _FakePort()
    st = build_chat_details_panel_state(p, None, model_label=None)
    assert st == empty_chat_details_panel_state()


def test_build_state_missing_info():
    p = _FakePort()
    assert build_chat_details_panel_state(p, 0, model_label="m") is None


def test_build_state_populates_topics_and_flags():
    p = _FakePort()
    st = build_chat_details_panel_state(p, 42, model_label="llama")
    assert st is not None
    assert st.chat_id == 42
    assert st.title == "My chat"
    assert st.project_id == 10
    assert st.project_name == "Proj X"
    assert st.selected_topic_id == 5
    assert st.is_pinned is True
    assert st.is_archived is False
    assert st.model_label == "llama"
    assert st.last_assistant_agent == "agent-a"
    labels = [o.label for o in st.topic_options]
    assert "Ungruppiert" in labels and "Alpha" in labels and "Beta" in labels
