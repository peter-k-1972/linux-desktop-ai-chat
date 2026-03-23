# Chat-Layout-Policy

Der Chat (Operations **ChatWorkspace** + Legacy **ChatWidget**) nutzt dieselben Rasterregeln wie die übrige Workbench. Zahlenquelle: `app/gui/theme/design_metrics.py` (Präfix `CHAT_*` und allgemeine Konstanten).

**QSS ↔ Python:** Standard-`QComboBox`-Höhe im Workbench-Theme ist **QSS-Owner** (`base.qss`); `ChatInputPanel` setzt die Modell-Combo-Höhe nicht mehr in Python. Allgemeine Regeln: [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md).

---

## 1. Content-Spalte (max-width)

| Konstante | Wert | Anwendung |
|-----------|------|-----------|
| `CHAT_CONTENT_MAX_WIDTH_PX` | **800** | Obere Grenze der zentrierten Nachrichten-/Composer-Spalte (Legacy `ConversationView`, `ChatComposerWidget`). |

**Strategie:** Elastische Breite bis zur Maximalbreite — kein `minimumWidth` auf 1200 oder ähnliche Zwänge. Auf schmalen Fenstern schrumpft die Spalte mit dem Viewport.

**Begründung 800px (statt 720 oder 960):** Mittig im Lesekorridor 720–960px; 4px-Raster; Kompromiss zwischen zu breiten Zeilen auf Ultrawide und genug Platz für Markdown-Zeilen.

**QSS (Legacy-Pfad):** `app/resources/styles.py` interpoliert `max-width: …px` aus **`design_metrics.CHAT_CONTENT_MAX_WIDTH_PX`** (kein Literal in der Datei). Siehe `CHAT_WIDTH_TOKENIZATION_NOTES.md`.

---

## 2. Bubble-Breite (Legacy `ChatMessageWidget`)

| Konstante | Wert |
|-----------|------|
| `CHAT_BUBBLE_MAX_WIDTH_PX` | **720** |

Etwas schmaler als `CHAT_CONTENT_MAX_WIDTH_PX`, damit Avatare, Rolle und Außenluft sichtbar bleiben.

**ChatWorkspace:** `ChatMessageBubbleWidget` + `MarkdownMessageWidget` — kein festes `maximumWidth`; Breite folgt dem Scroll-Content mit Panel-Padding (`PANEL_PADDING_PX`).

---

## 3. Composer-Höhe

| Bereich | Regel |
|---------|--------|
| Mehrzeiliges Eingabefeld (`ChatInput`) | Dynamische Höhe; Minimum aus `INPUT_MD_HEIGHT_PX` + kleinem vertikalen Puffer (4px-Raster). |
| Send-Icon-Button (`ChatComposerWidget`) | `CHAT_PRIMARY_SEND_HEIGHT_PX` / `CHAT_PRIMARY_SEND_WIDTH_PX` = **40** (prominente Aktion, Obergrenze Layout-Regeln). |
| **ChatWorkspace** `ChatInputPanel` | Prompt-Button **32** (`INPUT_MD_HEIGHT_PX`); Senden **40** (`CHAT_PRIMARY_SEND_HEIGHT_PX`); Ausrichtung unten zur `QTextEdit`. |
| Modell-Combo | `INPUT_MD_HEIGHT_PX` Mindesthöhe **32**. |

---

## 4. Außen- und Innenabstände

| Kontext | Konstanten |
|---------|------------|
| Nachrichtenliste (Workspace) | `PANEL_PADDING_PX` (20), vertikaler Abstand zwischen Bubbles `SPACE_LG_PX` (16). |
| Legacy Conversation-Spalte | gleich: `PANEL_PADDING_PX`, `SPACE_LG_PX`. |
| Bubble-Rahmen (`ChatMessageBubbleWidget`) | `SPACE_MD_PX` (12) — kompaktes Kartengefühl. |
| Composer-Wrapper / -Innen (Legacy) | `CHAT_COMPOSER_WRAPPER_MARGINS_LTRB`, `CHAT_COMPOSER_INNER_MARGINS_LTRB`. |
| ChatInputPanel | Oben `SPACE_MD_PX`, seitlich/unten `CARD_PADDING_PX`; Zeilenabstand `SPACE_SM_PX` / `FORM_ROW_GAP_PX`. |

---

## 5. Chat-spezifische Ausnahmen (bewusst)

1. **Send-Button 40px** statt 32px — einzige primäre Chat-Aktion im Legacy-Composer und im Workspace-Input; entspricht „prominente Aktion max. 40px“.
2. **Bubble-Innenpadding in QSS** (`ChatMessageWidget` setzt weiterhin `padding: 14px 18px` im Stylesheet-String) — kein Farb-/Stil-Refactor in diesem Schritt; nur Layout-Zahlen ausgelagert wo Python das Layout setzt.
3. **Zwei Chat-Pfade:** Workspace (Markdown-Bubbles) vs. Legacy (QLabel-Bubbles) — unterschiedliche Widgets, gemeinsame Metriken für Breiten/Höhen wo sinnvoll.

---

## 6. Einordnung ins globale Layoutsystem

- **Workspace-Content:** 20px (`PANEL_PADDING_PX`) am Verlauf; Legacy-Spalte identisch.
- **Karten/kompakt:** 16px / 12px über `CARD_PADDING_PX` und `SPACE_MD_PX`.
- **Raster:** 4px; Abstände bevorzugt aus `SPACE_*` und `FORM_ROW_GAP_PX`.

Weitere Historie: `docs/design/CHAT_LAYOUT_REFACTOR_NOTES.md`, Abschluss `docs/design/CHAT_LAYOUT_REFACTOR_REPORT.md`.
