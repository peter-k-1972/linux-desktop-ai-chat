"""
Chat max-width: Legacy-QSS aus app/resources/styles.py muss design_metrics nutzen (keine zweite Quelle).
"""

from __future__ import annotations

from pathlib import Path

from app.gui.theme import design_metrics as dm
from app.resources.styles import get_stylesheet


def _styles_py_text() -> str:
    root = Path(__file__).resolve().parents[3]
    return (root / "app" / "resources" / "styles.py").read_text(encoding="utf-8")


def test_styles_py_has_no_literal_chat_max_width_800px():
    """Kein festes 800px mehr am Chat-Container in der Quelle."""
    src = _styles_py_text()
    assert "max-width: 800px" not in src
    assert "_dm.CHAT_CONTENT_MAX_WIDTH_PX" in src


def test_stylesheet_chat_container_max_width_matches_design_metrics():
    """Erzeugtes QSS enthält max-width aus derselben Metrik wie die Widgets."""
    expected = f"max-width: {dm.CHAT_CONTENT_MAX_WIDTH_PX}px"
    assert expected in get_stylesheet("dark")
    assert expected in get_stylesheet("light")


def test_no_regression_chat_layout_metrics(qapplication):
    """ConversationView maxWidth bleibt an derselben Konstante wie das QSS."""
    from app.gui.domains.operations.chat.panels.conversation_view import ConversationView

    view = ConversationView(theme="dark")
    assert view.message_container.maximumWidth() == dm.CHAT_CONTENT_MAX_WIDTH_PX
