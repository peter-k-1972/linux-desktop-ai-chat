# Markdown-Rendering-Integration (Chat & Hilfe)

## Ziel

Eine **gemeinsame** Markdown-Pipeline (`app.gui.shared.markdown`) für alle relevanten Textansichten; **kein Parsing in den Widgets**. Monospace nur für **Code-** und **ASCII-Blöcke** (Renderer), Fließtext sans-serif.

## Schichten

| Schicht | Modul / Komponente |
|--------|---------------------|
| Parser, Segmente, HTML | `app.gui.shared.markdown.*` |
| Qt-Anbindung + Fallback | `app.gui.shared.markdown_ui.apply_markdown_to_widget` |
| Wiederverwendbare Views | `app.gui.components.markdown_widgets` |

## Widgets

- **`MarkdownMessageWidget`** (`QTextEdit`, read-only): Chat-Blasen. Ruft `set_markdown()` → `apply_markdown_to_widget(..., CHAT_BUBBLE)`. Wachsende Höhe, Scrollbars aus (wie zuvor `_MessageContentEdit`).
- **`MarkdownDocumentView`** (`QTextBrowser`): Hilfe, Seitenleiste, HelpWindow. `set_markdown()` → `HELP_BROWSER`.
- **`MarkdownView`**: `QFrame` mit optionalem Titel + `MarkdownDocumentView` (Demo, Inspector-ähnliche Einbettung).

## Integration (Stand)

| Ort | Verwendung |
|-----|------------|
| `ChatMessageBubbleWidget` | `MarkdownMessageWidget` mit `objectName` `messageContent` (Theme `shell.qss`) |
| `HelpPanel` | `MarkdownDocumentView` statt bare `QTextBrowser` |
| `HelpWindow` | `MarkdownDocumentView`; `set_markdown()` für Dateien/Welcome; Topics weiterhin `markdown_to_html` + Link-Nachbearbeitung + `setHtml` |
| `AgentResultPanel` | `QTextEdit` + `apply_markdown_to_widget(..., GENERIC_HTML)` (Scrollbar, kein Bubble-`sizeHint`) |

`apply_to_qtext_edit` / `apply_to_qtext_browser` in `app.gui.shared.markdown` laden **`markdown_ui.apply_markdown_to_widget`** verzögert (Zirkularimport vermeiden). Direktimport: `from app.gui.shared.markdown_ui import apply_markdown_to_widget`.

## Fallback

Wenn `setHtml` fehlschlägt oder das Dokument leer bleibt obwohl Quelltext nicht leer ist: **Plaintext** aus der Pipeline + **Monospace-Schrift**, damit ASCII/Code nicht „verschwinden“.

## Demo / Prüfstation

**Empfohlen (GUI-intern):** **Runtime / Debug** → **Markdown Demo** — siehe [MARKDOWN_DEMO_PANEL.md](MARKDOWN_DEMO_PANEL.md).

Optional (Legacy-Dialog mit eingebetteten Strings):

```bash
python3 -m app.gui.components.markdown_rendering_demo
```

## Tests

- Bestehende Chat-UI-Tests (`content_widget` ist weiterhin `QTextEdit`-Subklasse).
- Optional: `tests/unit/test_markdown_ui_fallback.py` (Mock-Widget ohne Qt).

## Siehe auch

- `docs/architecture/MARKDOWN_RENDERING_ARCHITECTURE.md` – Datenfluss, Segmente, RenderModi.
