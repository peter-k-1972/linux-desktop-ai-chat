# Color Usage Map

**Zweck:** Welche Farbrollen (Background, Text, Accent, Semantic) pro UI-Komponente sinnvoll sind — abgeleitet aus Token-Spec, QSS (`app/gui/themes/base/*.qss`) und Ist-Styles.  
**Format:** Component | Background | Text | Accent | Semantic | Notes

Legende **Text:** primary = `color.fg.primary`, secondary = `color.fg.secondary`, muted = `color.fg.muted`.  
Legende **Accent:** Marken-/Fokusfarbe (`color.state.accent*`, `color.button.primary*`, `color.tab.indicator`, Fokus-Ränder, Links).

---

| Component | Background | Text | Accent | Semantic | Notes |
|-----------|------------|------|--------|----------|-------|
| **QMainWindow (Shell)** | neutral (`color.bg.app`) | primary | none | none | Globales Canvas |
| **Top Bar** | neutral nav (`color.nav.bg`) | primary | optional (Hover Project Switcher Border) | none | Kein durchgehendes Accent-Flächenfill |
| **Project Switcher** | neutral hover surface | primary | border/hover accent möglich | none | `#projectSwitcherButton:hover` nutzt `color_accent` als Border — sparsam |
| **Breadcrumb Bar** | neutral muted (`color.bg.surface_alt` / `color_bg_muted`) | primary / secondary | hover link-artig auf Items | none | `#breadcrumbItem:hover` → `color_accent` |
| **Main Navigation Sidebar** | neutral (`color.nav.bg`) | primary | **active item** (`nav.active_*`) | none | Selektion = klarer Accent-Kanal |
| **Domain Nav (Operations / Settings)** | neutral nav | primary | **selected** (`nav.active_*`) | none | Wie Haupt-Sidebar |
| **Domain Nav (Control Center)** | neutral nav | primary | **selected** (`nav.active_*` / `color_nav_selected_*`) | none | Vereinheitlicht mit Haupt-Sidebar (kein zweites Accent-Paar) |
| **Domain Nav (QA & Governance)** | neutral nav | primary | **selected** (wie global, `nav.active_*`) | none | Resolver setzt `qa_nav` = `nav_selected` — ein Kanal |
| **Runtime / Debug Nav** | monitoring neutral (`color.domain.monitoring.bg/surface`) | monitoring text | **selected** (`domain.monitoring.accent*`) | optional | Visuell eigener „Raum“, weiterhin überwiegend neutral |
| **Workspace Host** | neutral (`color.bg.app`) | primary | none | none | Inhalt trägt Akzente |
| **Workspace Title / Subtitle** | transparent | primary / secondary | none | none | Typografie-Hierarchie |
| **Inspector Host** | neutral muted | secondary (Inspector-Labels) | optional focus | none | `#inspectorPrimaryValue` → primary text |
| **Dock Title Bar** | neutral nav-like | primary | none | none | `QDockWidget::title` |
| **Bottom Panel Host** | neutral muted | primary / secondary | **tab active** (via tab tokens) | none | Pane = `color.bg.surface` |
| **Bottom Panel Tabs** | neutral | primary | **active tab** / indicator | none | An Tab-Tokens koppeln |
| **Cards / #basePanel** | neutral surface | primary | none | none | Nur Rahmen, kein Brand-Fill |
| **Settings Panel / #settingsPanel** | neutral surface | primary / secondary | none | none | |
| **Empty State** | neutral muted oder transparent (compact) | primary / secondary / muted | none | none | |
| **Section Card / Panel Header** | neutral | primary | none | none | |
| **QGroupBox (allgemein)** | transparent | primary | none | none | |
| **QGroupBox (Inspector)** | transparent | secondary | none | none | Zurückhaltend |
| **Default QPushButton** | neutral secondary button | primary | optional | none | Primär-CTA separat stylen |
| **#secondaryButton** | neutral muted | secondary | none | none | |
| **Primary CTA** (z. B. `#chatNavNewChatButton`) | **accent** | on-accent / inverse | hover/pressed | none | Gezielter Accent |
| **#chatNavNewTopicButton** | neutral secondary | inverse | none | none | Ist secondary-gray — konsistent halten |
| **QLineEdit / QComboBox** | input bg | primary | **focus border** | none | `color.input.border_focus` / `color.border.focus` |
| **QPlainTextEdit / Composer** | input bg | primary | focus | none | |
| **QCheckBox / QRadioButton** | transparent | secondary | focus ring | none | |
| **QListWidget / QTreeWidget (generisch)** | transparent oder surface | primary | **selection** | none | `interaction.selected` / `selection.*` |
| **QTableWidget** | table bg | table fg | **selection** | optional | Header neutrale Abstufung |
| **QTabWidget (generisch)** | neutral | primary | **active tab + indicator** | none | Tokens `color.tab.*` |
| **Canvas Tabs** | neutral | primary | active | none | |
| **Scroll Bars** | transparent track | muted | hover subtle | none | |
| **Menus** | menu bg | menu fg | hover bg | none | |
| **Tooltips** | tooltip bg | tooltip fg | none | none | |
| **Command Palette** | overlay / surface | primary | **selection + focus** | none | Modales „Werkzeug“ |
| **Dialogs (QDialog)** | window / surface | primary | primary actions | optional | Destruktive Aktionen → semantic |
| **Chat User Bubble** | chat user bg | user fg | border subtle | none | Rollenunterscheidung neutral-schief |
| **Chat Assistant Bubble** | assistant bg | assistant fg | none | none | |
| **Chat System Bubble** | system bg | system fg | none | **optional** | System-/Meta: dezente semantic-tint erlaubt |
| **Markdown Body** | inherited / surface | body | **links** | none | `color.markdown.link` = Accent-Kanal |
| **Markdown Headings / Code** | surfaces | heading / code fg | none | none | |
| **Markdown Blockquote** | — | quote | border | none | |
| **Console / Log Views** | console bg | plain | optional | **success/warn/error** | `color.console.*` |
| **Syntax Highlighting** | code bg | plain + token colors | keyword/string/etc. | none | Lesbarkeit, nicht Marketing-Accent |
| **Badges** | semantic bg | on-badge fg | none | **success/warn/error/info** | `color.badge.*` |
| **Status Indicators** | — | — | running/pending | **ready/failed/indexing** | `color.indicator.*` |
| **Workflow Graph Nodes** | node fill neutral | node text | **selected border** | **status fills** | `graph.node.status.*` = semantic |
| **Workflow Edges** | — | — | edge neutral | none | |
| **Charts** | chart bg | axis | series 1–3 | none | Serienfarben ≠ überall Brand-Accent streuen |
| **Dashboard KPI Cards** | surface | primary | optional sparkline | optional health | Semantic nur bei echtem Status |
| **Theme Visualizer** | dev surface | primary | swatches | none | Nur Dev-Tool |
| **Legacy ChatWidget** | gemischt Theme-Helper | primary | accent wie Spec | optional | Migration zu Token-QSS |

---

## Aggregierte Lesart

- **Neutral:** App-, Fenster-, Panel-, Surface-, Inspector-muted-, Tabellen-Grundflächen und der Großteil der Typografie.  
- **Accent:** Auswahl in Nav, aktive Tabs, Fokus, primäre CTAs, Links (Markdown + Breadcrumb-Hover), Graph-Auswahl, Focus-Ringe.  
- **Semantic:** Badges, Validierung, Fehler/Erfolg in Logs, Workflow-Node-Status, Indikatoren — nicht für „schöne“ Flächen.

---

*Siehe auch [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md) und [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md).*
