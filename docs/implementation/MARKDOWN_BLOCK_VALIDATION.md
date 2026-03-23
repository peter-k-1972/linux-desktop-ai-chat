# Markdown: Block-Validierung und Darstellungs-Fallbacks

Diese Seite beschreibt die **zentrale Pipeline** (Parser → Block-AST → `RenderSegment` → HTML) für **Chat**, **Hilfe** und alle anderen QText*-Einstiege über `render_markdown` / `markdown_to_html`.

## Erkannte Blocktypen (AST, `markdown_types`)

| Block | Bedeutung |
|-------|-----------|
| `CodeFenceBlock` | Fenced ``` … ```; `fence_complete=False`, wenn die schließende Zeile fehlt |
| `IndentedCodeBlock` | Vier-Leerzeichen-/Tab-Code |
| `TableBlock` | Zeilen mit führendem/trailing `\|`; `stable`, `structural_warnings`, `raw_lines` |
| `AsciiBlock` | Aus Absätzen promotete ASCII-/CLI-/Diagramm-Inhalte (`promote_ascii_paragraphs`) |
| `ParagraphBlock`, `ListBlock`, … | unverändert |

Validierungslogik für Tabellen: `app/gui/shared/markdown/markdown_block_validation.py`.

## Render-Segmente (`markdown_segment_types`)

| Segment | `kind` | Verwendung |
|---------|--------|------------|
| `CodeBlockSegment` | `code_block` | Vollständige Fences; `fence_complete` (nur bei vollständigem Fence) |
| `MalformedBlockSegment` | `malformed_block` | Unvollständiges Fence: Inhalt bleibt erhalten, **Preformatted** + Hinweis-Attribut |
| `TableBlockSegment` | `table_block` | Nur wenn `TableBlock.stable is True` → HTML-`<table>` |
| `PreformattedBlockSegment` | `preformatted_block` | Instabile/unklare Tabellen: Rohzeilen, `source="table_fallback"` |
| `AsciiBlockSegment` | `ascii_block` | Promoted ASCII; **niemals** proportional als Fließtext |
| `PlainBlockSegment` / `ParagraphSegment` | … | wie zuvor |

Konvertierung: `markdown_segment_builder.blocks_to_render_segments`.

## Tabellenstrategie

1. Der Parser sammelt aufeinanderfolgende `|…|`-Zeilen, überspringt eine **Separator-Zeile** (`|---|`).
2. `evaluate_table_stability` setzt `stable=False`, wenn mindestens eines zutrifft:
   - keine Separator-Zeile erkannt (`missing_separator`)
   - unterschiedliche Spaltenanzahl (`column_mismatch`)
   - ASCII-Rahmen in Rohzeilen, z. B. `+---+` (`ascii_frame_mix`)
3. **Stabil** → `TableBlockSegment` → Renderer baut eine **`<table>`** mit Monospace in den Zellen und festen Rändern (Ausrichtung).
4. **Instabil** → **kein** „Schönrechnen“: `PreformattedBlockSegment` mit **Original-`raw_lines`**, Darstellung wie Code/ASCII (`<pre>`).

## Codeblock-Strategie

1. Öffnende Zeile mit ` ``` ` startet einen Fence-Block; Sprache ist **optional** (Info-String nach den Backticks).
2. Schließende Zeile (nur Backticks + Whitespace) → `fence_complete=True`.
3. Datei/Stream endet vor Schließung → `fence_complete=False`, Body trotzdem als Text vorhanden.
4. Segmentierung: vollständig → `CodeBlockSegment`; unvollständig → `MalformedBlockSegment` (weiterhin `<pre><code>`, zusätzlich `data-md-malformed='incomplete_fence'` und optische Kennzeichnung).
5. Eingerückter Code → `CodeBlockSegment` mit `fenced=False`.

## ASCII / Pseudotabellen

- **Nicht** als GFM-Tabelle erkannte Strukturen (z. B. Zeilen mit `+---+` ohne durchgängige `|…|`-Parser-Kette) bleiben Absätze und werden über `paragraph_looks_like_ascii_art` zu **`AsciiBlock`** promotet → `AsciiBlockSegment` → Monospace.
- Eine **Mischform** (äußerlich `|…|`, aber Rahmen-Zeilen) wird in `TableBlock.raw_lines` erkannt und über `ascii_frame_mix` auf **Preformatted** zurückgestuft.

## Fallback-Regeln (kurz)

| Situation | Verhalten |
|-----------|-----------|
| Tabelle strukturell unsicher | `PreformattedBlockSegment` (`table_fallback`) |
| Fence defekt | `MalformedBlockSegment` / Preformatted |
| ASCII/CLI/Diagramm | `AsciiBlock` bzw. `AsciiBlockSegment` |
| Keine riskante Umwandlung | Kein erzwungenes Umbrechen von Spalten oder Zellen |

`block_requires_monospace_font` in `markdown_rules.py` behandelt **instabile** `TableBlock`s wie Monospace-Pflicht (Ausrichtung im Layout).

## Tests

- `tests/unit/test_markdown_block_validation.py` — Tabellen stabil/instabil, Fences, Mischdokumente, CLI/ASCII
- `tests/unit/test_markdown_segments_api.py` — Segmenttypen inkl. `MalformedBlockSegment`
- Weitere Pipeline-Tests: `test_markdown_pipeline.py`, `test_markdown_ui_fallback.py`

## Verwandte Dateien

- `markdown_parser.py` — Fence- und Tabellen-Erkennung
- `markdown_block_validation.py` — Tabellen-Stabilität
- `markdown_segment_builder.py` — Block → Segment
- `markdown_renderer.py` — Segment → HTML
