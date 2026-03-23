# Icon Binding Audit (IST)

**Stand:** Cutover-Migration — Bindungsstellen im Python-Code.  
**Zielschicht:** `IconManager` + `app/gui/icons/icon_registry.py` (`get_icon*`).  
**Kanonische Assets:** `resources/icons/` (siehe `ICON_CANONICAL_SET.md`).

---

## Legende

| Priorität | Bedeutung |
|-----------|-----------|
| P0 | Globale Navigation / Shell / produktiver Einstieg |
| P1 | Domänen-UI (Operations, Control Center, …) |
| P2 | Legacy / nur Wartung |
| P3 | Sonderfall (Avatar, System-Standardpixmaps) |

---

## Zentrale Schicht (Ziel erreicht)

| Datei | Klasse/Funktion | Quelle | Ziel | P | Risiko |
|-------|-----------------|--------|------|---|--------|
| `app/gui/icons/icon_registry.py` | `get_icon`, `get_icon_for_*`, `get_icon_for_nav`, `get_icon_for_status` | Registry → Manager | Kanonisch | P0 | — |
| `app/gui/icons/manager.py` | `IconManager.get` | resources → assets fallback | Kanonisch | P0 | — |
| `app/gui/icons/nav_mapping.py` | `NAV_AREA_ICONS`, `*_WORKSPACE_ICONS` | Registry-Strings | Mapping-only | P0 | Mit `get_icon_for_nav` abgedeckt |

---

## Navigation & Shell

| Datei | Kontext | Bisher / Jetzt | Ziel | P | Konflikt |
|-------|-----------|----------------|------|---|----------|
| `app/gui/navigation/sidebar.py` | `NavSectionWidget` | `IconManager.get(item.icon)` + Fallback `get_icon_for_nav(nav_key)` | Registry | P0 | — |
| `app/gui/breadcrumbs/bar.py` | Breadcrumb-Buttons | `IconManager.get(item.icon)` | Registry | P0 | — |
| `app/gui/breadcrumbs/manager.py` | Pfadaufbau | `get_workspace_icon` → String | Mapping | P0 | — |
| `app/gui/shell/top_bar.py` | QAction-Icons | `IconManager` + `IconRegistry` | Registry | P0 | — |
| `app/gui/domains/*/*_nav.py` | Domain-Listen | `IconManager.get(icon_name)` aus Mapping | Registry | P1 | — |
| `app/gui/navigation/workspace_graph.py` | Graph-Knoten | `IconManager.get` | Registry | P1 | — |
| `app/gui/navigation/command_palette.py` | Befehle | `IconManager.get(cmd.icon)` | Registry | P1 | — |

---

## Aktionen & Panels (bereits Registry)

| Datei | Kontext | Quelle | P |
|-------|---------|--------|---|
| `.../chat_details_panel.py` | Pin, Edit | `IconRegistry` | P1 |
| `.../source_details_panel.py` | Open, Search chunks, … | `IconRegistry` | P1 |
| `.../project_overview_panel.py` | Run, Edit, Remove | `IconRegistry` | P1 |
| `.../chat_navigation_panel.py` | Add | `IconRegistry` | P1 |
| Weitere `IconManager.get(IconRegistry.*)` | diverse | Registry | P1 |

---

## Migriert in diesem Cutover

| Datei | Vorher | Nachher | P |
|-------|--------|---------|---|
| `app/main.py` | `QIcon(os.path.join(icons_path, *.svg))` | `IconManager` + `IconRegistry` (Hilfe, Gear, Agents, Dashboard) | P2 (Legacy-Modul, aber gebunden) |
| `app/gui/legacy/sidebar_widget.py` | QRC `:/icons/*.svg` | `IconManager` + `IconRegistry` | P2 |
| `app/gui/legacy/project_chat_list_widget.py` | QRC add/remove_chat | `IconManager` ADD/REMOVE | P2 |
| `app/gui/domains/operations/chat/panels/chat_composer_widget.py` | `icons_path/send.svg` | `IconManager` SEND | P1 |

---

## Sonderfälle (bewusst nicht Registry-UI-Icon)

| Datei | Kontext | Quelle | Ziel | P | Risiko |
|-------|---------|--------|------|---|--------|
| `app/gui/workbench/canvas/canvas_tabs.py` | Tab-Icon | `QStyle.StandardPixmap` + Status-Dot | Optional später Registry | P3 | Semantik „Canvas-Typ“, nicht identisch mit Nav-Registry |
| `app/gui/domains/operations/chat/panels/chat_message_widget.py` | Avatar | `QIcon(self.avatar_path)` Nutzerdatei | Kein Registry | P3 | — |
| `app/gui/legacy/message_widget.py` | Avatar | wie oben | Legacy | P3 | — |

---

## Legacy / noch zu beobachten

| Datei / Bereich | Befund | P |
|-----------------|--------|---|
| `app/gui/legacy/chat_widget.py` | `icons_path` an Composer durchgereicht (Composer ignoriert Pfad für Send jetzt) | P2 |
| `app/core/config/settings.py` | `icons_path` Default `assets/icons` | P2 | Historisch |
| `app/resources/icons/` + QRC | weiterhin für nicht migrierte QRC-Nutzer | P2 | Reduziert durch Legacy-Migration |
| Flache `assets/icons/*.svg` | Duplikat-Ebene | P2 | Siehe `ICON_CUTOVER_PLAN.md` |

---

## Prüfwerkzeug

| Tool | Geltungsbereich |
|------|-----------------|
| `tools/icon_usage_guard.py` | `app/**/*.py` + Root-`main.py`: QIcon/QPixmap-Literale, `load_icon(`, Strings mit `assets/icons`, `resources/icons`, `icons/`-Pfaden |
| `tools/icon_svg_guard.py` | `resources/icons/**/*.svg` |
| `tools/icon_registry_guard.py` | Registry ↔ Dateien, Orphans (Warnung), Nav-/Doku-Konflikte |
| `tools/run_icon_guards.py` | Alle drei + **`ICON_GUARD_REPORT.md`** |
| `.pre-commit-config.yaml` | optional `icon-guards` bei **pre-push** |

---

*Nächste Review:* bei neuen Widgets nur noch `get_icon*` / `IconManager` verwenden.
