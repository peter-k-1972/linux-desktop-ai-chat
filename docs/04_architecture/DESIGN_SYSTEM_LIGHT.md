# Designsystem Light – UI-Regelwerk

## Übersicht

Kleines verbindliches Regelwerk für konsistente UI-Werte. Kein großes Redesign, keine Komponentenbibliothek – nur zentrale Konstanten und wiederverwendbare Layout-Helfer.

---

## 1. Zentrale Konstanten

### Ort
`app/gui/shared/layout_constants.py`

### Spacing (Base: 4px)
| Konstante | Wert | Verwendung |
|-----------|------|------------|
| MARGIN_XS | 4 | Minimale Abstände |
| MARGIN_SM | 8 | Kleine Abstände |
| MARGIN_MD | 12 | Standard-Abstände |
| MARGIN_LG | 16 | Größere Abstände |
| MARGIN_XL | 24 | Screen-Padding, Settings |
| MARGIN_2XL | 32 | Große Leerräume |

### Content-Bereiche
| Konstante | Wert | Verwendung |
|-----------|------|------------|
| PANEL_PADDING | 20 | Standard-Panel-Innenabstand |
| SECTION_SPACING | 24 | Abstand zwischen Sektionen |
| CARD_SPACING | 16 | Abstand in Karten |
| WIDGET_SPACING | 12 | Abstand zwischen Widgets |
| WORKSPACE_PADDING | 20 | Workspace-Content |
| WORKSPACE_SPACING | 16 | Workspace-intern |
| SIDEBAR_PADDING | 12 | Sidebar, Explorer, Listen |
| SIDEBAR_SPACING | 10 | Sidebar-intern |
| HEADER_PADDING_V | 10 | Projekt-Header vertikal |
| HEADER_PADDING_H | 12 | Projekt-Header horizontal |

### Controls
| Konstante | Wert | Verwendung |
|-----------|------|------------|
| CONTROL_HEIGHT | 32 | Buttons, Inputs |
| BUTTON_PADDING_H | 12 | Button horizontal |
| BUTTON_PADDING_V | 8 | Button vertikal |

### Empty State
| Konstante | Wert |
|-----------|------|
| EMPTY_STATE_PADDING | 24 |
| EMPTY_STATE_PADDING_COMPACT | 16 |
| EMPTY_STATE_PADDING_COMPACT_V | 24 |
| EMPTY_STATE_SPACING | 12 |
| EMPTY_STATE_SPACING_COMPACT | 6 |

---

## 2. Layout-Helfer

```python
from app.gui.shared import (
    apply_panel_layout,      # Hauptinhalte (PANEL_PADDING, WIDGET_SPACING)
    apply_sidebar_layout,    # Listen, Explorer (SIDEBAR_PADDING, SIDEBAR_SPACING)
    apply_workspace_layout,  # Workspace-Content (WORKSPACE_PADDING, WORKSPACE_SPACING)
    apply_header_layout,     # Projekt-Header (HEADER_PADDING_H/V)
    apply_settings_layout,   # Settings-Kategorien (SCREEN_PADDING, CARD_SPACING)
)
```

### Verwendung
```python
# Standard-Panel
layout = QVBoxLayout(self)
apply_panel_layout(layout)

# Sidebar (Explorer, Listen)
layout = QVBoxLayout(self)
apply_sidebar_layout(layout)

# Projekt-Header
header_layout = QVBoxLayout(header_frame)
apply_header_layout(header_layout)

# Workspace-Content
center_layout = QVBoxLayout(center)
apply_workspace_layout(center_layout)
```

---

## 3. Abgestimmung mit ThemeTokens

`app/gui/themes/tokens.py` enthält QSS-Strings (z.B. `"20px"`). Die Layout-Konstanten sind Integer (z.B. `20`) für Python-Layout-Code.

| ThemeToken | layout_constants |
|------------|------------------|
| spacing_xs "4px" | MARGIN_XS 4 |
| spacing_sm "8px" | MARGIN_SM 8 |
| spacing_md "12px" | MARGIN_MD 12 |
| spacing_lg "16px" | MARGIN_LG 16 |
| spacing_xl "24px" | MARGIN_XL 24 |
| panel_padding "20px" | PANEL_PADDING 20 |
| section_spacing "24px" | SECTION_SPACING 24 |
| card_spacing "16px" | CARD_SPACING 16 |
| widget_spacing "12px" | WIDGET_SPACING 12 |

---

## 4. Betroffene Dateien

| Datei | Änderung |
|-------|----------|
| `app/gui/shared/layout_constants.py` | Erweitert: Konstanten, Helfer |
| `app/gui/shared/__init__.py` | Export layout_constants |
| `app/ui/widgets/empty_state_widget.py` | Nutzt EMPTY_STATE_* |
| `app/gui/domains/operations/chat/panels/session_explorer_panel.py` | apply_sidebar_layout, apply_header_layout |
| `app/gui/domains/operations/prompt_studio/panels/library_panel.py` | apply_sidebar_layout, apply_header_layout |
| `app/gui/domains/operations/knowledge/panels/knowledge_source_explorer_panel.py` | apply_sidebar_layout, apply_header_layout |
| `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` | apply_workspace_layout |
| `app/gui/domains/operations/agent_tasks/agent_tasks_workspace.py` | apply_workspace_layout |
| `app/gui/domains/operations/knowledge/knowledge_workspace.py` | apply_workspace_layout |
| `app/ui/settings/categories/project_category.py` | apply_settings_layout |
| `app/ui/settings/categories/workspace_category.py` | apply_settings_layout |

---

## 5. Reduzierte Inkonsistenzen

| Vorher | Nachher |
|--------|---------|
| 12 vs 10 vs 16 vs 20 vs 24 für Panel-Padding | SIDEBAR_PADDING (12), WORKSPACE_PADDING (20), SCREEN_PADDING (24) |
| 10 vs 12 vs 16 für Spacing | SIDEBAR_SPACING (10), WORKSPACE_SPACING (16), WIDGET_SPACING (12) |
| Header (12, 10, 12, 10) verstreut | apply_header_layout() |
| Magic Numbers in EmptyStateWidget | EMPTY_STATE_* Konstanten |

---

## 6. Warum "Designsystem Light" und kein Großumbau

- **Kein Massenrefactor**: Nur 10 Dateien angepasst, Rest unverändert
- **Keine Umbenennungen**: Bestehende Strukturen bleiben
- **Keine neue Framework-Schicht**: Nur Konstanten + 5 kleine Helfer
- **Bestehendes genutzt**: layout_constants existierte bereits, wurde erweitert
- **ThemeTokens unverändert**: QSS nutzt weiterhin Tokens
- **shell/layout_constants unverändert**: Shell-Dimensionen bleiben separat

---

## 7. Hinweise für künftige Entwickler

1. **Neue Panels**: `apply_sidebar_layout()` für Listen/Explorer, `apply_panel_layout()` für Content
2. **Neue Workspaces**: `apply_workspace_layout()` für zentrale Bereiche
3. **Neue Settings-Kategorien**: `apply_settings_layout()`
4. **Magic Numbers vermeiden**: Konstanten aus `layout_constants` importieren
5. **ThemeTokens (QSS)**: Für Farben, Fonts, Radien – `tokens.py`
6. **Layout (Python)**: Für Margins, Spacing – `layout_constants.py`
