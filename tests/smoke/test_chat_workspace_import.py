"""Smoke: Chat-Workspace importiert mit Presenter/Port-Stack (kein GUI-Start)."""


def test_chat_workspace_module_imports():
    from app.gui.domains.operations.chat.chat_workspace import ChatWorkspace

    assert ChatWorkspace.__name__ == "ChatWorkspace"
