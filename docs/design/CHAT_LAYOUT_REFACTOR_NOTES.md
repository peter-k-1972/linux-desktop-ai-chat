# Chat-Layout-Refactor — Datei-Audit (Phase 0)

Vor Umsetzung dokumentiert: harte Werte, geplante Ersetzung, Risiken.

---

## Betroffene Dateien

| Datei | Rolle |
|-------|--------|
| `app/gui/domains/operations/chat/panels/conversation_view.py` | Legacy-Chat: zentrierte Spalte, Margins |
| `app/gui/domains/operations/chat/panels/chat_composer_widget.py` | Legacy-Chat: Composer-Breite, Send-Button |
| `app/gui/domains/operations/chat/panels/chat_message_widget.py` | Legacy-Bubbles: `maxWidth` 1160 |
| `app/gui/domains/operations/chat/panels/conversation_panel.py` | **ChatWorkspace**-Verlauf (bereits 20/16) |
| `app/gui/domains/operations/chat/panels/input_panel.py` | **ChatWorkspace**-Eingabe: 48px Buttons |
| `app/gui/domains/operations/chat/panels/chat_message_bubble.py` | Workspace-Bubbles: Rand 12 |
| `app/gui/theme/design_metrics.py` | Neue Chat-Konstanten |
| `app/resources/styles.py` | `#chatContainer { max-width: 1200px }` (dark + light Theme-Strings) |
| `app/gui/legacy/chat_widget.py` | Host für ConversationView + ChatComposerWidget (keine Logik-Änderung) |

Nicht zwingend geändert: `chat_navigation_panel.py` (keine 1200/1000/48), `chat_workspace.py` (nur Zusammensetzung).

---

## Hardcoded Werte (alt) → Ziel

### `conversation_view.py`

| Alt | Neu / Strategie |
|-----|------------------|
| `setMinimumWidth(1200)` / `setMaximumWidth(1200)` | `minimumWidth` **0** (elastisch); `maximumWidth` `CHAT_CONTENT_MAX_WIDTH_PX` (800) |
| Margins `32, 40, 32, 40` | `PANEL_PADDING_PX` (20) — symmetrisch |
| Spacing `28` | `SPACE_LG_PX` (16) |

### `chat_composer_widget.py`

| Alt | Neu |
|-----|-----|
| Container `1000` min/max | Entfernt; elastisch, `maximumWidth` = `CHAT_CONTENT_MAX_WIDTH_PX` |
| Wrapper `24, 16, 24, 24` | `CHAT_COMPOSER_WRAPPER_MARGINS_LTRB` |
| Inner `16, 12, 12, 12` | `CHAT_COMPOSER_INNER_MARGINS_LTRB` |
| Send `44×44` | `CHAT_PRIMARY_SEND_*` (40) |
| ChatInput min `52` | An `INPUT_MD_HEIGHT_PX` + vertikales Padding (4px-Raster) |

### `chat_message_widget.py`

| Alt | Neu |
|-----|-----|
| `setMaximumWidth(1160)` | `CHAT_BUBBLE_MAX_WIDTH_PX` (720) |
| Vertikal `0, 12, 0, 12` | `0, SPACE_MD_PX, 0, SPACE_MD_PX` |

### `conversation_panel.py`

| Alt | Neu |
|-----|-----|
| `20, 20, 20, 20` / spacing `16` | Explizit `PANEL_PADDING_PX` / `SPACE_LG_PX` (gleiche Zahlen, eine Quelle) |

### `input_panel.py`

| Alt | Neu |
|-----|-----|
| Margins `16, 12, 16, 16` | `CARD_PADDING_PX` + `SPACE_MD_PX` / `CARD_PADDING_PX` |
| `_btn_prompt` / `_btn_send` `48` | Prompt **32** (`INPUT_MD_HEIGHT_PX`), Send **40** (`CHAT_PRIMARY_SEND_HEIGHT_PX`) |
| Ausrichtung | Buttons `AlignBottom` zur mehrzeiligen `QTextEdit` |

### `chat_message_bubble.py`

| Alt | Neu |
|-----|-----|
| `layout margins 12` | `SPACE_MD_PX` (unverändert 12, nur benannt) |

### `styles.py`

| Alt | Neu |
|-----|-----|
| `#chatContainer` in `styles.py` | Interpolation aus `design_metrics` (`CHAT_WIDTH_TOKENIZATION_REPORT.md`) |

---

## Token / Metrics

Alle genannten Ziele liegen in `design_metrics` (Präfix `CHAT_*` wo sinnvoll) bzw. bestehende `PANEL_PADDING_PX`, `SPACE_*`, `INPUT_MD_HEIGHT_PX`.

---

## Risiken

1. **Scroll / sehr schmale Fenster:** Zentrum schrumpft unter 800px; kein erzwungenes Mindestmaß der Spalte — horizontales Scrollen weiterhin aus (ScrollArea).
2. **Bubble-Breite:** 720 bei Spalte 800 lässt ~40px Seitenluft pro Seite im schmalsten Fall; lange URLs/Code umbrechen weiter über `wordWrap`.
3. **Composer mehrzeilig:** Höhe weiter dynamisch; Send 40px mit `AlignBottom`.
4. **Legacy QSS (#chatInput / #sendButton):** unverändert in diesem Schritt (kein Farb-/QSS-Refactor).
5. **Prompt 32 vs. Send 40:** bewusst asymmetrisch; optisch über `AlignBottom` gebündelt.

---

## Breiten-Entscheidung (720 / 800 / 960)

**Gewählt: 800px** für `CHAT_CONTENT_MAX_WIDTH_PX`.

- Liegt mittig im empfohlenen Korridor 720–960px.
- 800px ist durch 4 teilbar und harmoniert mit Raster.
- Begründung gegen 960: weniger „schwimmende“ extrem breite Zeilen auf Ultrawide.
- Begründung gegen 720: etwas mehr Platz für Markdown/Listen ohne unnötige Umbrüche.

`CHAT_BUBBLE_MAX_WIDTH_PX = 720`: etwas schmaler als die Spalte, damit Avatare und Außenluft sichtbar bleiben.
