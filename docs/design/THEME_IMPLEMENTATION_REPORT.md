# Theme-Implementierung — Umsetzungsbericht

**Bezug:** [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md), [THEME_MIGRATION_PLAN.md](./THEME_MIGRATION_PLAN.md), [THEME_TARGET_MODEL.md](./THEME_TARGET_MODEL.md)  
**Datum:** Implementationsstand nach Phase-1–6-Stücken (inkrementell, lauffähig).

---

## 1. Architekturentscheidung (Abweichung von Beispielpfaden)

Die Spezifikation nannte Beispielpfade `app/theme/` und `app/themes/`. **Umgesetzt** ist die Erweiterung des **bestehenden** Pakets `app/gui/themes/`, damit:

- kein zweiter `ThemeManager` entsteht,
- `run_gui_shell.py`, Settings und Registry unverändert weiterarbeiten,
- der Audit-Pfad (`ThemeManager` + `assets/themes/base/*.qss`) die Single Source of Truth bleibt.

Neue Module liegen unter `app/gui/themes/`.

---

## 2. Neue / zentral geänderte Dateien

| Datei | Zweck |
|-------|--------|
| `app/gui/themes/canonical_token_ids.py` | `ThemeTokenId` — alle kanonischen Namen aus THEME_TOKEN_SPEC (nur Strings); `flat_key()`, `all_flat_color_keys()`, `all_canonical_color_token_ids()` |
| `app/gui/themes/resolved_spec_tokens.py` | `expand_token_dict_to_full_spec()` — leitet **alle** Spec-Flat-Keys aus dem bestehenden `ThemeTokens`-Dict ab (keine neuen Produktiv-Farben) |
| `app/gui/themes/control_center_styles.py` | Wiederverwendbare token-basierte Styles für Control-Center-Karten |
| `app/gui/themes/definition.py` | `get_tokens_dict()` ruft nach `merge_semantic_aliases_for_qss` zusätzlich `expand_token_dict_to_full_spec()` auf |
| `app/gui/themes/manager.py` | `color(token)` — Auflösung kanonisch (`color.fg.primary`) oder flach (`color_fg_primary`) |
| `app/gui/themes/__init__.py` | Export: `ThemeTokenId`, `flat_key`, `all_flat_color_keys` |
| `app/resources/styles.py` | `get_theme_colors()`: bei laufender `QApplication` Werte aus `ThemeManager.get_tokens()` (sonst Legacy-Fallback) |
| `app/gui/shared/markdown/markdown_renderer.py` | Farben für Pre/Tabellen/Quote/HR/Malformed aus Token-Map (ohne feste `rgba`) |
| `app/gui/components/markdown_widgets.py` | Kontextmenü: Token-Keys `color_menu_*` / Fallback über `ThemeRegistry` statt fester Hex |
| `app/gui/icons/manager.py` | Keine statischen Default-Hex mehr; Fallback über `light_default`-Registry |
| `app/gui/domains/control_center/panels/providers_panels.py` | Vollständig auf `control_center_styles` migriert (kein lokales Hex mehr) |
| `app/gui/domains/operations/workflows/canvas/workflow_edge_item.py` | Kantenfarbe: `ThemeTokenId.GRAPH_EDGE` |
| `app/gui/domains/operations/workflows/canvas/workflow_node_item.py` | Alle Node-/Status-/Textfarben über Graph-Tokens |
| `app/gui/workbench/canvas/canvas_tabs.py` | Status-Punkte: `ThemeTokenId.INDICATOR_*` |
| `app/gui/workbench/ai_canvas/ai_canvas_scene.py` | Node-Rahmen/-Füllung: Graph-Tokens |
| `app/gui/domains/control_center/agents_ui/agent_performance_tab.py` | Chart: `CHART_BG`, Monitoring-Text/Muted |
| `tests/regression/test_settings_theme_tokens.py` | + `test_builtin_themes_have_full_spec_color_keys` |
| `tests/ui/test_theme_tokens.py` | Manager, Vollständigkeit, Kanonisch/Flat |
| `tests/ui/test_theme_loading.py` | QSS-Substitution |
| `tests/ui/test_theme_switch.py` | Stylesheet-Wechsel |
| `tools/theme_consistency_check.py` | Heuristik-Scan (optional `--strict`) |

---

## 3. Entfernte / ersetzte Hardcodings (Auszug)

- **providers_panels.py:** `white`, `#e2e8f0`, Tailwind-Indigo-Button, Tabellen- und Label-Hex → Tokens.
- **markdown_renderer.py:** `rgba(0,0,0,…)`, `rgba(128,128,128,…)` für Code/Tabellen/Quote/HR → Theme-Tokens.
- **workflow_node_item / edge / ai_canvas / canvas_tabs / agent_performance_tab:** direkte `#…` / RGB → `ThemeManager.color(...)`.
- **markdown_widgets / icons:** Fallback-Hex-Strings entfernt zugunsten Registry-`light_default`.

---

## 4. QA-Ergebnis

- `pytest tests/regression/test_settings_theme_tokens.py tests/ui/test_theme_tokens.py tests/ui/test_theme_loading.py tests/ui/test_theme_switch.py` — **grün**
- `pytest tests/unit/test_markdown_pipeline.py tests/unit/test_markdown_ui_fallback.py` — **grün**

---

## 5. Offene Sonderfälle (bewusst nicht Big-Bang)

| Bereich | Stand |
|---------|--------|
| Weitere Control-Center-Panels (`models_panels`, `data_stores_panels`, …) | Noch lokales Hex — Muster: `control_center_styles` / `ThemeManager.color` |
| Inspector-Cluster (`*_inspector.py`) | Unverändert; nächste Migrationswelle |
| Operations / Knowledge / QA-Panels | Unverändert |
| `app/main.py` + `get_stylesheet` | Legacy-QSS unverändert; `get_theme_colors` nutzt bei QApp ThemeManager |
| QSS-Dateien | Weiterhin `{{color_text}}` etc.; neue Spec-Keys (`color_fg_primary`) stehen zusätzlich im Dict — schrittweise QSS-Umstellung möglich |
| `tools/theme_consistency_check.py` | Meldet noch viele Treffer in `domains/` / `inspector/` — erwartet bis Migration fortgeschritten |

---

## 6. Nutzung für Entwickler

```python
from app.gui.themes import get_theme_manager, ThemeTokenId

mgr = get_theme_manager()
hex_color = mgr.color(ThemeTokenId.FG_PRIMARY)
# oder
hex_color = mgr.color("color_fg_primary")
```

QSS: Platzhalter `{{color_fg_primary}}` funktionieren, sobald die Keys in `assets/themes/base/*.qss` verwendet werden (Legacy-Platzhalter bleiben gültig).

---

## 7. Nächste Schritte (laut Migrationsplan)

1. `models_panels` / `data_stores_panels` / `tools_panels` auf `control_center_styles` umstellen.  
2. Inspector-Helper mit gemeinsamen Token-Styles.  
3. Kontrast-Tests aus [THEME_CONTRAST_RULES.md](./THEME_CONTRAST_RULES.md) anbinden.  
4. Duplikat `app/gui/themes/base/*.qss` vs. `assets/themes/base/` bereinigen.
