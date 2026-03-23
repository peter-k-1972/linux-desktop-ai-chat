# Icon Conflict Report

**Ziel:** Mehrdeutigkeiten und Lücken für die Bereinigung mit `ICON_MAPPING.md` + `icon_registry.py`.

**Cutover-Stand:** Mehrere frühere Konflikte sind produktiv bereinigt (siehe Abschnitt 5). Verbleibende Punkte betreffen Asset-Duplikate und optionale Feinjustierung.

---

## 1. Mehrere Bedeutungen (ein Icon, verschiedene Semantiken)

| Icon (Registry) | Konflikt |
|-----------------|----------|
| **shield** | ~~QA-Bereich **und** Runtime-QA-Workspaces~~ → **behoben:** Runtime nutzt `qa_runtime`; Governance bleibt `shield`. |
| **search** | ~~„Quelle öffnen“~~ → **open** für Öffnen; **search** für Suche/Chunks weiter sinnvoll. Command Palette bleibt **search**. |
| **system_graph** | Workflow-Workspace **und** Workspace-Map **und** Quick Actions — weiterhin dieselbe Glyphe, aber nur wo Graph-Semantik passt (siehe `ICON_CONFLICT_RESOLUTION.md`). |
| **data_stores** | ~~Deployment~~ → **deploy** für `operations_deployment`; `data_stores` nur Datenspeicher. |
| **add** | ~~Pin~~ → **pin** in `chat_details_panel`. |
| **activity** | ~~Workflows-Stat-Karte~~ → **system_graph** in `project_stats_panel`; **activity** bleibt Runtime-Hauptnav. |
| **logs** | ~~Markdown-Demo~~ → **sparkles** für `rd_markdown_demo`. |

---

## 2. Gleiche Bedeutung, verschiedene Quellen / Styles

| Thema | Befund |
|-------|--------|
| **Zwei Asset-Bäume** | `assets/icons/svg/…` (Registry) vs. `app/resources/icons/` (QRC) vs. flache `assets/icons/*.svg` — gleiche Aktionen (search, new, …) optisch/ strukturell uneinheitlich. |
| **Stroke** | Alte SVGs teils `stroke-width="2"`, neues Set `1.5` unter `resources/icons/`. |
| **Pfad-Duplikate** | `assets/icons/actions/*.svg` **und** `assets/icons/svg/actions/*.svg`; `runtime/` vs `svg/runtime/`. |

---

## 3. Fehlende oder nur implizite Icons

| Lücke | Vorschlag |
|-------|-----------|
| **Pin / Favorit** | Eigenes Registry-`pin` + SVG in `actions/` oder `objects/`. |
| **Deployment / Release** | Eigenes `deploy` (umgesetzt); Mapping in Nav von `data_stores` auf **deploy** für `operations_deployment`. |
| **Öffnen / externer Link** | `open` oder `link_out` statt **search** für Datei/URL. |
| **Hilfe** | `help` (umgesetzt in Registry + TopBar). |
| **Duplikat-Chat** | Legacy QRC; Migration auf `IconManager.get("add")` + Chat-Semantik. |

---

## 4. Empfohlene nächste Schritte (Code)

1. ~~`nav_mapping.py`: `operations_deployment` → **deploy**~~ — erledigt.  
2. ~~`chat_details_panel`: **pin**~~ — erledigt.  
3. ~~`source_details_panel`: **open**~~ — erledigt.  
4. ~~`project_stats_panel`: **system_graph**~~ — erledigt.  
5. ~~Legacy `sidebar_widget` / `main.py` / `project_chat_list_widget` / `chat_composer`~~ — auf `IconManager` umgestellt.  
6. Duplikat-Ordner unter `assets/icons/` konsolidieren (ein Baum) — **offen**.  
7. Externe URLs konsequent **link_out** zuweisen, wo semantisch passend — **teilweise offen**.

---

## 5. Produktiv bereinigte Konflikte (Referenz)

| Thema | Maßnahme |
|-------|----------|
| Deployment | `deploy`, nie `data_stores` für Release-Nav |
| Pin | eigenes `pin` |
| Open | `open` + Registry `link_out` für extern |
| Markdown-Demo | `sparkles` |
| Shield vs Runtime-QA | `shield` vs `qa_runtime` |
| Activity vs Workflows-Metrik | `system_graph` auf Stat-Karte |

*Detail:* `ICON_CONFLICT_RESOLUTION.md`, `ICON_BINDING_AUDIT.md`.

---

*Siehe `ICON_MAPPING.md` für Soll-Zuordnungen.*
