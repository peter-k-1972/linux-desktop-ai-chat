# Markdown-Demo-Panel (intern)

## Zweck

Dauerhafte **manuelle Prüfstation** für die zentrale Markdown-Pipeline: gleiche Logik wie **Chat** und **Hilfe**, inklusive **ASCII-** und **Code-Monospace**, ohne duplizierten Parser.

Typische Fragen, die man hier sofort beantwortet:

- Sind Überschriften und Listen korrekt?
- Bleiben **Codeblöcke** monospace?
- Bleiben **ASCII-Diagramme** stabil?
- Ist **gemischter** Inhalt lesbar?
- Verhalten sich **Hilfe**- und **Chat-Target** konsistent (zwei Vorschau-Tabs)?

## Fundort / Aufruf

1. **Navigation:** Hauptbereich **Runtime / Debug** → in der linken Liste **„Markdown Demo“**.
2. **Kommandopalette:** Befehl **„Markdown-Demo öffnen“** (`nav.rd_markdown_demo`).

## Technik

| Teil | Ort |
|------|-----|
| Panel-UI | `app/gui/devtools/markdown_demo_panel.py` |
| Sample-Metadaten | `app/gui/devtools/markdown_demo_samples.py` |
| Markdown-Quellen | `app/resources/demo_markdown/*.md` |
| Vorschau-Widgets | `MarkdownDocumentView` (Hilfe), `MarkdownMessageWidget` (Chat) — beide nutzen `render_markdown` / `apply_markdown_to_widget` |

**Keine** Parsing-Logik in der Demo: nur Laden von Text, Anzeige, `render_markdown`, `render_segments` für die Diagnosebox.

## Enthaltene Beispiele

| Datei | Inhalt |
|--------|--------|
| `basic.md` | Überschriften, Absatz, UL/OL, Zitat |
| `code_blocks.md` | Fence + Inline-Code |
| `ascii_tree.md` | Verzeichnisbaum |
| `ascii_boxes.md` | Boxdiagramm |
| `cli_output.md` | Shell-/Fehlerzeilen |
| `mixed.md` | Text + Liste + Code + ASCII + Zitat |
| `broken_markdown.md` | offenes Fence, holprige Listen, Tabs |
| `help_like.md` | hilfeartige Struktur |
| `chat_like.md` | assistant-ähnliche Antwort |

## UI-Kurzbedienung

- **Beispiel:** Liste links — wechselt die geladene `.md`-Datei.
- **Quelltext:** standardmäßig read-only; „Quelltext bearbeiten“ für lokale Experimente.
- **Neu laden (Datei):** verwirft Änderungen und liest die Datei vom Datenträger erneut.
- **Rendering aktualisieren:** wendet den aktuellen Editorinhalt auf **beide** Vorschauen an.
- **Render-Info:** `ContentProfile`, `RenderMode`, Segmentanzahl, Zähler für `code_block` / `ascii_block`, Segmentarten.

## Was visuell prüfen?

- Tab **Vorschau (Hilfe):** `RenderTarget.HELP_BROWSER` (Fließtext, Absatzumbrüche wie Handbuch).
- Tab **Vorschau (Chat):** `RenderTarget.CHAT_BUBBLE`, schmale Spalte wie Bubble — Zeilenumbrüche wie im Chat.
- Bei Zweifel: mit **kaputtem** Beispiel prüfen, ob **Fallback** (Plain/Monospace) greifen würde (siehe `markdown_ui.apply_markdown_to_widget`).

## Hinweis: Standalone-Demo

`python3 -m app.gui.components.markdown_rendering_demo` ist ein älteres **separates** Fenster mit eingebetteten Strings. Die **kanonische** Prüfstation ist dieses **Runtime/Debug-Panel** mit den Dateien unter `app/resources/demo_markdown/`.

## Siehe auch

- `docs/implementation/MARKDOWN_RENDERING_INTEGRATION.md`
- `docs/architecture/MARKDOWN_RENDERING_ARCHITECTURE.md`
