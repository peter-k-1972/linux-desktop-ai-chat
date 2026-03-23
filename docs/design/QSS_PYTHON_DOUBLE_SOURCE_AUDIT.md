# QSS ↔ Python — Doppelquellen-Audit

**Methode:** gezielte Code- und QSS-Durchsicht (kein Voll-AST).  
**Stand:** Cleanup-Pass 2026-03 — siehe `QSS_PYTHON_DOUBLE_SOURCE_CLEANUP_REPORT.md`.

---

## Legende

| Winner | Bedeutung |
|--------|-----------|
| **QSS** | Stylesheet setzt maßgeblich; Python soll nicht derselben Property widersprechen. |
| **Python** | Layout-Code setzt maßgeblich; QSS soll generisch/neutral bleiben. |
| **Unklar** | Beide setzen ein; Priorität plattformsabhängig oder undocumented. |
| **Hybrid** | Bewusst: Python Struktur, QSS Oberfläche — ohne gleiche Property doppelt. |

---

## A — Standard-Controls (Workbench-Theme: `base.qss` + Loader)

| file / widget | property | Python-Quelle | QSS-Quelle | Winner | Risk | Owner-Empfehlung |
|----------------|----------|---------------|------------|--------|------|------------------|
| `input_panel.py` `modelCombo` | min-height | ~~`setMinimumHeight(32)`~~ entfernt | `QComboBox { min-height: 32px; }` `base.qss` | QSS | niedrig | **QSS** |
| `base.qss` generisch `QPushButton` | implizite Höhe | diverse `setFixedHeight` in Domains | padding `spacing_md`/`lg` | Unklar | mittel | **QSS** für Standard; Python nur für Ausnahme-IDs |
| `base.qss` `QLineEdit` | padding/Höhe | `sidebar_widget` `setMinimumHeight` auf `QLineEdit` | padding tokens | Hybrid | mittel | **QSS** ideal; Legacy-Sidebar: Python bis QSS-ID vereinheitlicht |
| `settings_dialog.py` | `prompt_dir_btn` `setFixedWidth(36)` | Python | ggf. globales QToolButton-Styling | Python | niedrig | **Python** (spezifische Square-Action) oder Token `icon_box+padding` |

---

## B — Legacy `app/resources/styles.py` + `sidebar_widget.py`

| file / widget | property | Python | QSS | Winner | Risk | Owner-Empfehlung |
|----------------|----------|--------|-----|--------|------|------------------|
| `#newChatBtn` | Höhe | `setMinimumHeight` (jetzt `PANEL_HEADER_HEIGHT_PX`) | `padding: 14px`, große Schrift | Unklar | mittel | Langfristig **QSS**-Owner; Python nur Mindestgröße wenn nötig |
| `#saveChatBtn` | Größe | `setFixedSize(CHAT_PRIMARY_SEND_*)` | `padding: 12px` | Unklar | niedrig | **Python** für quadratische Nebenaktion konsistent mit Chat-Send |
| `#searchEdit` | min-height | `INPUT_MD + SPACE_SM` | `padding: 10px 14px` `styles.py` | Hybrid | niedrig | **QSS** sobald Legacy an Theme-Tokens angeglichen |
| `ConversationView` / `styles.py` `#chatContainer` | max-width | `design_metrics` | interpoliert aus `design_metrics` | Python | niedrig | **Python/Metrik** kanonisch |

---

## C — Workbench `workbench.qss`

| file / widget | property | Python | QSS | Winner | Risk | Owner-Empfehlung |
|----------------|----------|--------|-----|--------|------|------------------|
| `#workbenchPaletteList::item` | min-height | — | 32px | QSS | niedrig | **QSS** |
| `#workbenchNodeLibrary::item` | min-height | — | 28px | QSS | niedrig | **QSS** (dense explorer — dokumentiert in LAYOUT_SYSTEM_RULES) |
| `#workbenchToolbar` | icon-size | — | 18px hard in qss | QSS | niedrig | Tokenisierung Folgeschritt |
| `PanelHeader` `panel_header.py` | margins | `apply_header_profile_margins` | `#workbenchPanelHeader*` in qss | Hybrid | niedrig | **Python** Margins; **QSS** Typo/Farbe |

---

## D — Chat (nach Layout-Refactor)

| file / widget | property | Python | QSS | Winner | Risk | Owner-Empfehlung |
|----------------|----------|--------|-----|--------|------|------------------|
| `ChatInputPanel` `chatInput` `QTextEdit` | min/max height | 60 / 120 | — in Theme-Pfad selten | Python | niedrig | **Python** (Inhaltseditor) |
| `ChatInputPanel` Send/Prompt | fixed height | `CHAT_*` / `INPUT_MD` | `#sendButton` in `styles.py` (Legacy) | Unklar | mittel | **Python** für Operations-Chat; Legacy-QSS separater Pfad |
| `chat_message_widget.py` | bubble padding | `setStyleSheet` mit px | — | Python | niedrig | Folge: Bubble-Styling nach ThemeToken oder QSS-ID |

---

## E — Control Center / Dashboard / Dialoge (Stichprobe)

| file | property | Python | QSS | Winner | Risk |
|------|----------|--------|-----|--------|------|
| `providers_panels.py` | `setMinimumHeight` auf Panels | 180, 100, 120 | — | Python | niedrig — **Struktur/Empty-State** |
| `dashboard` `*panel.py` | min-height 140 | Python | — | Python | niedrig |
| `project_edit_dialog.py` | min width / desc max height | Python | — | Python | niedrig |

---

## F — Scrollbars / Sonderfälle

| Quelle | property | Hinweis |
|--------|----------|---------|
| `base.qss` `QScrollBar::handle:vertical` | min-height 48px | Scroll-Handle, nicht Input-Control — kein Konflikt mit Button-32-Regel; optional später tokenisieren |

---

## Zusammenfassung Konfliktarten

1. **Gleiche Control-Klasse:** QSS `min-height` + Python `setMinimumHeight` (Combo, LineEdit, Button).  
2. **Legacy vs. Workbench:** `styles.py` vs. `base.qss` — zwei App-Pfade.  
3. **Inline `setStyleSheet` in Python** mit Layout-Pixeln (Padding, radius) parallel zu globalem QSS.  
4. **Spezial-IDs** (`#newChatBtn`) mit sowohl padding in QSS als auch Mindestmaß in Python.  
5. **Listenzeilen:** nur QSS, aber unterschiedliche min-height (28 vs 32) — keine Python-Doppelung, aber **Inkonsistenz** zwischen Listen.

---

*Weiter:* [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md), [QSS_PYTHON_CANONICAL_CASES.md](./QSS_PYTHON_CANONICAL_CASES.md).
