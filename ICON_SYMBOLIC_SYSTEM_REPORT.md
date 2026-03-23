# Icon Symbolic System Report

Stand: Einführung eines state- und token-basierten symbolischen Icon-Systems (PySide6 / Obsidian Core).

---

## Neue Dateien

| Pfad | Zweck |
|------|--------|
| `docs/design/ICON_STATE_MODEL.md` | Semantik der Icon-Zustände |
| `docs/design/ICON_COLOR_RULES.md` | Token-Zuordnung pro State |
| `docs/design/ICON_MIGRATION_PLAN.md` | Cutover von Legacy-Pfaden |
| `app/gui/icons/icon_states.py` | State-Normalisierung + `ICON_STATE_TO_TOKEN` |
| `resources/icons/actions/pin.svg` | Pin-Glyphe (`currentColor`) |
| `resources/icons/actions/open.svg` | Öffnen / extern (`currentColor`) |
| `resources/icons/monitoring/qa_runtime.svg` | Runtime-QA/Observability (nicht Governance-Shield) |
| `assets/icons/svg/actions/pin.svg` | Fallback-Pfad für `IconRegistry` |
| `assets/icons/svg/actions/open.svg` | Fallback-Pfad für `IconRegistry` |
| `assets/icons/svg/runtime/qa_runtime.svg` | Fallback-Pfad für `IconRegistry` |
| `assets/icons/svg/ai/sparkles.svg` | Fallback für Markdown-Demo-Icon |
| `tests/unit/gui/test_icon_registry.py` | Registry- und Pfad-Tests |
| `tests/unit/gui/test_icon_manager.py` | State, Cache, Theme, Fallback |

---

## Geänderte Dateien

| Pfad | Änderung |
|------|-----------|
| `app/gui/icons/manager.py` | `state`, `color_token` optional; Cache `(theme_id, name, size, state, color_token, resolved_color)`; zentrale Farbauflösung; Notfall-Tint `#6b7280` wenn kein Token |
| `app/gui/icons/icon_registry.py` | Registry-Einträge `pin`, `open`, `sparkles`, `qa_runtime`; `open`-Aktion → `open`; `get_icon` / `get_icon_for_*` mit `state` |
| `app/gui/icons/registry.py` | `IconRegistry`-Konstanten und Pfade für `PIN`, `OPEN`, `QA_RUNTIME`, `SPARKLES` |
| `app/gui/icons/nav_mapping.py` | Runtime QA → `qa_runtime`; Markdown-Demo → `sparkles` |
| `app/gui/domains/operations/chat/panels/chat_details_panel.py` | Pin-Button → `PIN` |
| `app/gui/domains/operations/knowledge/panels/source_details_panel.py` | Öffnen-Button → `OPEN` |
| `app/gui/domains/operations/projects/panels/project_stats_panel.py` | Workflows-Karte → `SYSTEM_GRAPH` |
| `docs/design/ICON_MAPPING.md` | Runtime-, Demo- und Aktions-Zuordnungen aktualisiert |

---

## Eingeführte Zustände (`IconState`)

`default`, `primary`, `active`, `selected`, `disabled`, `success`, `warning`, `error`

API: `IconManager.get(..., state="default")`, `get_icon(..., state="default")`, `get_icon_for_object` / `get_icon_for_action` mit gleichem Parameter.

---

## Bereinigte / adressierte Konflikte (laut `ICON_CONFLICT_REPORT.md`)

| Thema | Maßnahme |
|-------|-----------|
| Deployment vs. `data_stores` | War bereits `deploy` in `nav_mapping`; unverändert bestätigt |
| Pin vs. `add` | Eigenes `pin` + Nutzung im Chat-Details-Panel |
| Open vs. `search` | Eigenes `open` + Mapping der Aktion `open`; Quelle öffnen nutzt `OPEN` |
| Markdown-Demo vs. `logs` | `rd_markdown_demo` → `sparkles` |
| Shield QA/Governance vs. Runtime | Governance-Nav bleibt `shield`; Runtime QA Workspaces → `qa_runtime` |

Hinweis: `system_graph`-Mehrdeutigkeit und `activity`-Overload bleiben dokumentiert; nur die Workflows-Stat-Karte wurde auf `system_graph` gestellt.

---

## Offene Legacy-Reste

- `app/resources/icons/` und QRC-gebundene Icons in älteren Einstiegen
- Flache `assets/icons/*.svg` und parallele Ordner ohne `svg/`
- Weitere Call-Sites können bei Bedarf `state="primary"` setzen, wenn nach Umstellung auf `default` → `color.fg.secondary` zu dezent wirkt

---

## Teststatus

```text
pytest tests/unit/gui/test_icon_registry.py tests/unit/gui/test_icon_manager.py -q
```

11 Tests, alle grün (lokal mit `python3 -m pytest`).

---

## SVG-Tinting

- Glyphen bleiben mit `stroke`/`fill` = `currentColor`
- Laufzeit: Ersetzung von `currentColor` durch aufgelöste Token-Farbe; Ergebnis als `QPixmap`/`QIcon` gecacht

---

*Design-Referenz: `ICON_STYLE_GUIDE.md`, `THEME_TOKEN_SPEC.md`.*
