# Kanonische Fälle — Owner, Begründung, Dateien

Kurzreferenz für wiederkehrende UI-Muster. Ergänzungen nur mit Ownership-Eintrag.

---

## 1. Standard Input Height (32px)

| | |
|--|--|
| **Owner** | **QSS** — `assets/themes/base/base.qss` → `QComboBox { min-height: 32px; }`; `QLineEdit` über Padding. |
| **Begründung** | Einheitliche Control-Chrome über Theme; Workbench lädt `base.qss`. |
| **Python** | Kein `setMinimumHeight(32)` auf Standard-Combo (Chat `modelCombo` bereinigt). |
| **Ausnahme** | Legacy-Pfad ohne diese QSS-Regel — dann explizit Python oder QSS in `styles.py` nachziehen. |

---

## 2. Primary / prominente Button-Höhe (Chat Send 40px)

| | |
|--|--|
| **Owner** | **Python** + `design_metrics.CHAT_PRIMARY_SEND_HEIGHT_PX`. |
| **Begründung** | Domänenregel „prominente Aktion max. 40“; nicht jedes Theme braucht global 40px-Buttons. |
| **Dateien** | `input_panel.py`, `chat_composer_widget.py`. |
| **Ausnahme** | Legacy `styles.py` `#sendButton` — separater Pfad; visuell angleichen bei Theme-Vereinigung. |

---

## 3. Tab-Höhe

| | |
|--|--|
| **Owner** | **QSS** (Padding + Border an `QTabBar::tab`). |
| **Python** | Keine festen Tab-Höhen setzen außer Host-Layout (z. B. `QTabWidget` Größe). |
| **Referenz** | `LAYOUT_SYSTEM_RULES.md` §8. |

---

## 4. List Row Height (32 vs 28)

| | |
|--|--|
| **Owner** | **QSS** pro Listen-ID. |
| **Begründung** | `workbenchPaletteList` 32px; `workbenchNodeLibrary` 28px (dense) — bewusst unterschiedlich, nicht Python. |
| **Ausnahme** | Explorer-Zeilen, die in Python `setMinimumHeight` auf Custom-Widget setzen — Owner **Python** für Custom-Row-Widget. |

---

## 5. Panel Padding (20 / 16 / 12)

| | |
|--|--|
| **Owner** | **Python** — `layout_constants` / `design_metrics` (`PANEL_PADDING_PX`, `CARD_PADDING_PX`, `apply_panel_layout`). |
| **QSS** | `#basePanel` nutzt Token `{{panel_padding}}` für Karten; nicht zusätzlich doppeltes Python-Padding auf denselben Inhalt ohne Karte. |

---

## 6. Dialog Inner Padding

| | |
|--|--|
| **Owner** | **Python** — `apply_dialog_scroll_content_layout`, `DIALOG_PADDING_PX`. |
| **QSS** | Dialog-Chrome Farbe/Radius; kein zweites „24px“-Padding im Python-String. |

---

## 7. Max-Width Content (Chat)

| | |
|--|--|
| **Owner** | **Python** — `CHAT_CONTENT_MAX_WIDTH_PX`; Legacy-QSS `#chatContainer` interpoliert aus derselben Metrik in `styles.py`. |

---

## 8. Toolbar Icon Size

| | |
|--|--|
| **Owner** | **QSS** (`workbench.qss` `icon-size: 18px` am Toolbar) — Folgeschritt: Token statt Literal. |
| **Python** | `setIconSize` nur wenn QSS keine Toolbar-Regel trifft oder spezielle Dichte. |

---

## 9. Header Profiles (12,10 / 12,8 / 8,6)

| | |
|--|--|
| **Owner** | **Python** — `apply_header_profile_margins` + `design_metrics.HEADER_*`. |
| **QSS** | Nur Typografie/Farbe am `#workbenchPanelHeader*`. |

---

## 10. Bubble / Message Content Width

| | |
|--|--|
| **Owner** | **Python** — `CHAT_BUBBLE_MAX_WIDTH_PX`, Layout der Spalte. |
| **QSS** | Kein zweites `max-width` für dieselbe Bubble-Klasse im Theme bis vereinheitlicht. |

---

*Guard:* `tools/layout_double_source_guard.py` (heuristische Hinweise).
