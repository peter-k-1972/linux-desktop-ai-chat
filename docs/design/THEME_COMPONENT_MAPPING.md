# Komponenten → Token-Zuordnung

**Ergänzung zu:** [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md)  
**Audit-Referenz:** [docs/audits/THEME_COLOR_AUDIT.md](../audits/THEME_COLOR_AUDIT.md) §4, §5

Legende **Konflikt (Audit):** bekannte Ist-Probleme, die durch Migration zu schließen sind.

---

## MainWindow / Shell

| Komponente | Primäre Tokens | Zustände | Sonderregeln | Konflikt (Audit) |
|------------|----------------|----------|--------------|------------------|
| `QMainWindow` | `color.bg.app`, `color.fg.primary` | — | via globales QSS | OK mit Token-QSS |
| TopBar (`#topBar`) | `color.nav.bg` oder `color.bg.panel`, `color.border.subtle` | hover über Kind-Widgets | Shell-QSS | Legacy `get_theme_colors` mischt in manchen Views |

---

## Sidebar / Navigation

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `#navigationSidebar` | `color.nav.bg`, `color.border.default` | — | shell.qss | — |
| Nav-Items | `color.nav.fg`, `color.nav.hover_bg`, `color.nav.active_bg`, `color.nav.active_fg` | hover, selected | ObjectNames in QSS | — |
| `workspace_graph.py` | gemischt Token + Fallback-Hex | — | Migration: Fallback entfernen | Audit §3.4 |

---

## Header / Breadcrumbs

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `#breadcrumbBar` | `color.bg.surface_alt`, `color.border.subtle` | — | shell.qss | — |
| `#breadcrumbItem` | `color.fg.primary`, hover: `color.interaction.hover` | hover | | — |

---

## Statusbar / Footer

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QStatusBar` | `color.bg.panel`, `color.fg.muted`, `color.border.subtle` | — | base.qss / shell | Legacy main window eigene Styles |

---

## Workspace / Panels

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| Workspace-Host | `color.bg.app` | — | wenig eigenes QSS | — |
| Domain-Panels (generisch) | `color.bg.surface`, `color.border.default` | — | **kein** `white` hardcoded | Control Center: light-only Karten (§5.3) |
| Monitoring-Bereiche | `color.domain.monitoring.*` | — | ersetzt scattered overrides | Doppel-Definition palette_resolve vs Semantic (§5.9) |

---

## Cards / GroupBoxes

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `#basePanel` | `color.bg.surface`, `color.border.default` | — | base.qss | Viele Panels ignorieren mit eigenem QSS (§5.10) |
| `QGroupBox` (Inspector) | `color.fg.secondary`, Titel | — | zentraler Helper statt 20× copy-paste | Inspector-Cluster Hex (§3.5) |

---

## Buttons

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QPushButton` (default) | `color.button.secondary.*` | hover, pressed, disabled | base.qss | — |
| `#secondaryButton` | explizit sekundär | hover | base.qss | — |
| Primär (ObjectName) | `color.button.primary.*` | | fehlend → Spec ergänzen in QSS | Legacy styles.py eigene Accent-Werte (§5.12) |

---

## Inputs

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QLineEdit`, `QPlainTextEdit`, `QTextEdit` (composer) | `color.input.*` | focus, disabled | base.qss | — |
| `QComboBox` | `color.input.bg`, `color.input.border`, dropdown surface | hover, focus | | — |

---

## Tabellen

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QTableWidget` (Control Center) | `color.table.*` | selection | ersetzt `#fafafa` / gridline | Light-assumptiv (§4.4) |

---

## Trees / Listen

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QListWidget`, `QTreeWidget` | `color.table.bg` / surface, `color.interaction.hover`, `color.interaction.selected` | hover, selected | base.qss | `setForeground(QColor)` in Agent-Panels (§4.6) |

---

## Tabs

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QTabBar` / `QTabWidget` | `color.tab.*` | selected | base.qss | — |
| Workbench-Tab-Icon-Badge | `color.indicator.*` | per `ObjectStatus` | `canvas_tabs.py` RGB | Audit §3.6 |

---

## Dialoge

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QDialog` | `color.bg.window`, `color.border.default` | — | base.qss | — |
| Command Palette | Tokens (bereits) | — | `command_palette.py` | — |
| Workspace Graph Dialog | soll voll Token sein | — | Migration | Fallback-Hex (§3.4) |

---

## Tooltips / Menus

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| `QMenu` | `color.menu.*` | item:hover | | Markdown-Kontextmenü: Exception-Fallback dunkel (§5.11) |
| `QToolTip` | `color.tooltip.*` | — | plattformabhängig; Qt kann ignorieren | dokumentierte Ausnahme möglich |

---

## Chat

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| User-Bubble | `color.chat.user_*` | — | + HTML in Markdown | `get_theme_colors` + rgba (§4.5) |
| Assistant-Bubble | `color.chat.assistant_*` | — | | |
| System | `color.chat.system_*` | — | | |
| Composer / Input | `color.input.*`, Shell chrome | focus | | |

---

## Markdown-Renderer (HTML)

| Komponente | Tokens | Zustände | Sonderregeln | Konflikt |
|------------|--------|----------|--------------|----------|
| Body, headings, links | `color.markdown.*` | — | injiziert in `style=` sicher | feste rgba (§5.4) |
| Code, Tabellen, HR | `color.markdown.codeblock_*`, `table_*`, `hr` | — | | |

---

## Codeblöcke (Darstellung)

| Kontext | Tokens | Konflikt |
|---------|--------|----------|
| Chat-Bubble `<pre>` | `color.markdown.codeblock_bg/fg` | rgba unabhängig vom Theme |
| Hilfe-Browser | gleiche Tokens | gleich |

---

## Alerts / Banner (wenn eingeführt oder ad-hoc)

| Typ | Tokens |
|-----|--------|
| Info | `color.state.info`, `color.badge.info.*` |
| Success | `color.state.success`, `color.badge.success.*` |
| Warning | `color.state.warning`, `color.badge.warning.*` |
| Error | `color.state.error`, `color.badge.error.*` |

---

## Badges / Status-Chips

| Komponente | Tokens | Konflikt |
|------------|--------|----------|
| Ollama-Status, API-Labels | `color.badge.*` / `color.state.*` | gemischte Hex in `providers_panels` |
| `infrastructure_snapshot` | `color.state.success/warning/error` + `color.fg.muted` | aktuell feste Hex |

---

## Status-Indikatoren (Listen)

| Komponente | Tokens | Konflikt |
|------------|--------|----------|
| Agent-Task-Status | `color.state.*` + ggf. `color.fg.muted` für neutral | `QColor` Hex in `agent_status_panel` |
| Workflow-Node-Run | `color.graph.node.status.*` | komplett hardcoded |

---

## Charts / Custom Delegates

| Komponente | Tokens | Konflikt |
|------------|--------|----------|
| Agent Performance (QtCharts) | `color.chart.*` | `#0a0a14` hardcoded |
| Custom `paint` | immer `QColor(tokens[...])` | diverse |

---

## Icons / SVG

| Komponente | Tokens | Konflikt |
|------------|--------|----------|
| `IconManager` | `color.fg.primary` default; `color.domain.monitoring.text` für Monitoring-Icons | Fallback-Hex in Python |

---

## Dokumentensuche (`doc_search_panel`)

| Soll-Tokens | `color.bg.surface`, `color.fg.primary`, `color.button.primary.*`, `color.input.*` |  
| **Konflikt:** komplett Light-Palette (Audit §5.5) — Migration P3.

---

## Settings

| Bereich | Tokens | Konflikt |
|---------|--------|----------|
| API-Key-Status | `color.state.success/error` statt `green`/`#c44` | `settings_dialog.py` |

---

## Offene Konflikte (Audit → Mapping)

1. **Zwei Theme-APIs:** bis Entfernung `get_theme_colors` müssen alle gemappten Komponenten **direkt** `ResolvedTokenMap` nutzen.  
2. **Globales QSS vs. lokales setStyleSheet:** Mapping ist **Soll**; lokale Overrides sind zu entfernen, außer Allowlist.  
3. **Projekt-Panels (Glasmorphismus):** rgba durch Token ersetzen oder `color.bg.surface_elevated` + definierte Alpha-Tokens (Spec-Erweiterung falls nötig).
