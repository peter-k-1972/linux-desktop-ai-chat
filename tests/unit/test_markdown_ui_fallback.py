"""Fallback-Pfad für apply_markdown_to_widget (ohne Qt-GUI)."""

from __future__ import annotations

from app.gui.shared.markdown.markdown_types import RenderTarget
from app.gui.shared.markdown_ui import apply_markdown_to_widget


class _BrokenWidget:
    def __init__(self) -> None:
        self.html_set = False
        self.plain_set: str | None = None
        self._font_calls: list = []

    def setHtml(self, html: str) -> None:
        self.html_set = True
        raise RuntimeError("simulated setHtml failure")

    def setPlainText(self, text: str) -> None:
        self.plain_set = text

    def toPlainText(self) -> str:
        return self.plain_set or ""

    def font(self):
        class F:
            def pointSize(self):
                return 11

        return F()

    def setFont(self, font) -> None:
        self._font_calls.append(font)


def test_apply_markdown_fallback_on_sethtml_error():
    w = _BrokenWidget()
    r = apply_markdown_to_widget(w, "Hello **world**", target=RenderTarget.CHAT_BUBBLE)
    assert w.plain_set is not None
    assert "Hello" in w.plain_set
    assert r.plain_text


def test_apply_markdown_plain_widget_ok():
    class _OkWidget(_BrokenWidget):
        def setHtml(self, html: str) -> None:
            self.html_set = True
            self._html = html

        def toPlainText(self) -> str:
            return "Hello world"

    w = _OkWidget()
    apply_markdown_to_widget(w, "Hello **world**", target=RenderTarget.CHAT_BUBBLE)
    assert w.html_set
