# Projects & Headers — Layout-Bestandsaufnahme (Phase 2, Phase 0)

## `project_list_panel.py`

| Aspekt | Ist (vor Refactor) | Zielregel |
|--------|-------------------|-----------|
| Panel margins | 12×12 | Compact panel **12** ✓ |
| VBox spacing | 8 | **12** (`WIDGET_SPACING`) |
| `QListWidget` spacing | 2 | **4** (`SPACE_XS`) — einheitlich „feine Liste“ |
| `::item` padding | 10×12 | **8×12** + `min-height: 32` |
| Inline QSS | viele Magic px + Hex | Zahlen aus `design_metrics`; Farben vorerst unverändert |

## `project_overview_panel.py`

| Aspekt | Ist | Ziel |
|--------|-----|------|
| Outer margins | 20 | **20** (`PANEL_PADDING`) |
| Outer / content spacing | 20 | **16** (`CARD_SPACING`) |
| Monitoring/Controlling QSS padding | 14px | **16** (`CARD_PADDING_PX`) |
| Actions row spacing | 12 | `WIDGET_SPACING` ✓ |
| Middle row | 16 | `CARD_SPACING` ✓ |
| Separator `margin-top` | 8px | `SPACE_SM` (8) explizit |

## `project_stats_panel.py`

| Aspekt | Ist | Ziel |
|--------|-----|------|
| Stat card QSS padding | 14×16 asymmetrisch | **16** (`CARD_PADDING_PX`) |
| Stat card layout margins | 14,12,14,12 | **16** (`apply_card_inner_layout`) |
| HBox spacing in card | 10 | **12** (`WIDGET_SPACING`) |
| Outer `outer` spacing | 10 | **12** |
| Typo px | 20 / 11 | `TEXT_XL_PX` / `TEXT_XS_PX` |
| Icon | 20 | `ICON_MD_PX` |

## `project_edit_dialog.py`

| Aspekt | Ist | Ziel |
|--------|-----|------|
| Root layout | `QFormLayout(self)` ohne Außenrand | **24** Dialog-Padding, Form-Policy |
| ButtonBox | `addRow` im Form | eigene Zeile / `apply_dialog_button_bar_layout` |
| Form spacing | Default | 12 / 8 Policy |

## Workbench Header

| Datei | Ist margins | Profil |
|-------|-------------|--------|
| `panel_header.py` | 12,10,12,**8** | **standard** 12,10,12,10 |
| `workflow_header.py` | 12,8,12,8 | **compact** ✓ |
| `context_action_bar.py` | 8,6,8,6 | **ultra** ✓ |

Alle über `apply_header_profile_margins` + `design_metrics.HEADER_*`.

## Inkonsistenzen (überführt)

- 14px Padding (Stats, Overview-Frames) → 16px Karte.
- 10px Spacing (Stats outer, List-Row-Gaps) → 12px wo „Block“-Abstand.
- Listen `spacing(2)` vs. QSS — auf **4** + klare Item-`min-height` **32**.
