"""
Legacy-Standalone-Fenster mit eingebetteten Strings.

Kanoniche Prüfstation: Runtime / Debug → **Markdown Demo** (app/gui/devtools/, app/resources/demo_markdown/).
Siehe docs/implementation/MARKDOWN_DEMO_PANEL.md

Start:  python3 -m app.gui.components.markdown_rendering_demo
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.gui.components.markdown_widgets import MarkdownDocumentView, MarkdownMessageWidget, MarkdownView


DEMO_HELP_ARTICLE = """# Hilfeartikel (Beispiel)

Kurzer **fetter** Text mit `inline code` und [Link](https://example.org).

## Liste

- Punkt eins
- Punkt zwei

> Ein wichtiges Zitat.

---

## ASCII

```
+-------+-------+
|  A    |   B   |
+-------+-------+
```

## Code

```python
def hello():
    return "world"
```
"""

DEMO_CHAT_REPLY = """Hier ist die Antwort.

```text
$ kubectl get pods
NAME    READY
web-0   1/1
```

Baum:

```
src/
├── main.py
└── lib/
```
"""

DEMO_MIXED = """## Überschrift

Fließtext mit **Markdown**.

```
ASCII block
  indented
```

- Liste
"""


class MarkdownRenderingDemoDialog(QDialog):
    """Tabs: Hilfe-Ansicht, Chat-Blase, generische MarkdownView."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Markdown-Rendering-Demo")
        self.resize(920, 640)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Gleiche Parser-/Renderer-Pipeline (RenderTarget HELP vs. CHAT). "
                "ASCII und Code: Monospace / pre-wrap."
            )
        )
        tabs = QTabWidget()
        # Hilfe
        w_help = QWidget()
        hl = QVBoxLayout(w_help)
        doc = MarkdownDocumentView()
        doc.set_markdown(DEMO_HELP_ARTICLE)
        hl.addWidget(doc)
        tabs.addTab(w_help, "Hilfe (MarkdownDocumentView)")
        # Chat
        w_chat = QWidget()
        cl = QVBoxLayout(w_chat)
        cl.addWidget(QLabel("Chat-Blase (MarkdownMessageWidget):"))
        msg = MarkdownMessageWidget()
        msg.set_markdown(DEMO_CHAT_REPLY)
        # In einer echten Blase setzt das Parent-Layout die Breite
        msg.setMinimumWidth(480)
        cl.addWidget(msg)
        cl.addStretch()
        tabs.addTab(w_chat, "Chat (MarkdownMessageWidget)")
        # Generisch
        mv = MarkdownView(title="MarkdownView", parent=None)
        mv.set_markdown(DEMO_MIXED)
        tabs.addTab(mv, "MarkdownView + Titel")
        # Liste + Zitat isoliert
        w_lq = QWidget()
        lql = QVBoxLayout(w_lq)
        lq = MarkdownDocumentView()
        lq.set_markdown(
            "### Liste + Zitat\n\n- eins\n- zwei\n\n> Zitatzeile\n"
        )
        lql.addWidget(lq)
        tabs.addTab(w_lq, "Liste + Zitat")
        layout.addWidget(tabs)


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    d = MarkdownRenderingDemoDialog()
    d.exec()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
