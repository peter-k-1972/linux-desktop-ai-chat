# GUI Semantik, IA, Usability (Phase 3)

Struktur pro Befund: **Problem** · **Fundstelle** · **Auswirkung** · **Schweregrad** · **Verbesserungsvorschlag**

---

## 1. Navigation & Hierarchie

| Problem | Fundstelle | Auswirkung | Schweregrad | Verbesserungsvorschlag |
|---------|------------|------------|-------------|------------------------|
| Zwei „Kommandozentralen“-Logiken: kompaktes **Dashboard** vs. vollständiger **CommandCenterView**-Stack | `DashboardScreen` (`dashboard_screen.py`); `CommandCenterView` nur in Legacy `app/main.py` | Nutzer des Standard-Produkts erhalten **nicht** dieselbe vertikale Tiefe wie Legacy-Nutzer; Text im Dashboard verweist auf „Command Center“-Drilldowns, die im Shell **nicht** am selben Ort liegen | **Hoch** | `CommandCenterView` in Shell einbetten, oder Dashboard primär als **Einstieg** mit sichtbaren Buttons zu den gleichen Drilldown-Views; Legacy isolieren/umbenennen |
| QA-Inhalte an **drei** Stellen: **QUALITY**-Sidebar, **OBSERVABILITY** (QA Cockpit / Observability), Dashboard-Karten | `navigation_registry.py` § OBSERVABILITY + QUALITY; `qa_governance_screen.py`; `runtime_debug_screen.py` | Rollenunklarkeit: „Wo ist die Wahrheit?“ | **Mittel–Hoch** | IA-Regel dokumentieren (z. B. QUALITY = arbeiten, OBSERVABILITY = live; Dashboard = Executive Summary) + Navigation labels angleichen |
| Runtime-Workspaces **Markdown Demo** / **Theme Visualizer** fehlen in zentraler `navigation_registry` Sidebar | `runtime_debug_nav.py` (dynamische Liste); `navigation_registry.py` (keine `rd_markdown_demo` / `rd_theme_visualizer`) | Kein Widerspruch für Nutzer, die nur Sidebar lesen — aber **Inkonsistenz** der „Single Source of Truth“ für alle Navigationskonsumenten | **Mittel** | Registry um Dev/QA-Einträge erweitern (ausblendbar) **oder** Registry explizit als „nur primäre Sidebar“ definieren und Workspace-Graph/Palette dokumentieren |
| „Betrieb“ unter WORKSPACE vs. „Incidents“ unter QUALITY | `NavEntry("operations_audit_incidents", "Betrieb", …)`; `qa_incidents` | Fachlich verwandt, unterschiedlich gruppiert | **Mittel** | Breadcrumb-Hilfe oder Querverlinkung zwischen den Views |

---

## 2. Begriffe & Sprache

| Problem | Fundstelle | Auswirkung | Schweregrad | Verbesserungsvorschlag |
|---------|------------|------------|-------------|------------------------|
| **DE**-UI vs. **EN**-Tooltips (z. B. Workspace Map) | `top_bar.py` — „Workspace Graph – visual map…“ | Professioneller Mix wirkt unfertig | **Niedrig–Mittel** | TopBar-Strings auf eine Arbeitssprache vereinheitlichen oder i18n-Keys |
| **Control Center** (engl.) als Bereichstitel neben deutschsprachigen Einträgen | `bootstrap.py` — Registrierungstitel „Control Center“ | Kleine semantische Reibung | **Niedrig** | Einheitlich „Kontrollzentrum“ oder bewusst englische Produktbegriffe global setzen |

---

## 3. Panel-Logik (Übersicht → Detail → Aktion)

| Problem | Fundstelle | Auswirkung | Schweregrad | Verbesserungsvorschlag |
|---------|------------|------------|-------------|------------------------|
| **Inspector** abhängig vom Workspace; leere Zustände ohne Erklärung möglich | `operations_screen.py` `_on_workspace_changed` | Nutzer verstehen nicht, warum rechts leer ist | **Mittel** | Einheitliche Empty-State-Hints im InspectorHost |
| **ActiveWorkPanel** erklärt bewusst, dass keine Live-Metriken gebündelt werden | `active_work_panel.py` | Gut für Ehrlichkeit; schwach für „Kommandozentrale“-Erwartung | **Mittel** | Entweder echte Mini-Metriken oder Umbenennung in „Hinweise“ / „Orientierung“ |

---

## 4. Aktionen & Toolbars

| Problem | Fundstelle | Auswirkung | Schweregrad | Verbesserungsvorschlag |
|---------|------------|------------|-------------|------------------------|
| **Status**-Icon in TopBar springt zu Runtime/Debug (laut Tooltip) — nicht z. B. zu Dashboard | `top_bar.py` `action_status` | Semantische Lücke zwischen „globaler Status“ und technischem Monitor | **Mittel** | Status → Dashboard oder Untermenü „Übersicht / Live“ |
| Starke Entlastung über **Command Palette** — Entdeckbarkeit abhängig von Shortcut-Hinweis | `top_bar.py` Ctrl+K Tooltip | Power-User gut; Casual-User unternutzen Palette | **Mittel** | Erste-Lauf-Hinweis oder Menü „Gehe zu …“ |

---

## 5. Status, Feedback, Fehler

| Problem | Fundstelle | Auswirkung | Schweregrad | Verbesserungsvorschlag |
|---------|------------|------------|-------------|------------------------|
| Platzhalter-Texte in produktiven Workspaces (**Knowledge**, **Prompt**, **Agent Tasks**) | `docs/PLACEHOLDER_INVENTORY.md` | Vertrauensverlust („ist das echt?“) | **Mittel** | Daten anbinden oder UI auf „Noch nicht verfügbar“ mit Erklärung ohne Pseudo-Metriken |
| `QAStatusPanel`/`IncidentsPanel` zeigen Fehlertext bei Adapter-Ausfall | `qa_status_panel.py`, `incidents_panel.py` | Gut sichtbar | **Niedrig** | — |

---

## 6. Help & Learnability

| Problem | Fundstelle | Auswirkung | Schweregrad | Verbesserungsvorschlag |
|---------|------------|------------|-------------|------------------------|
| Help-Fenster ist **umfangreich** (TOC, semantische Suche, Tours) | `help_window.py` | Positiv | — | Sicherstellen, dass **CLI-only**-Workflows (Replay/Repro) einen Help-Artikel haben |
| Quick Guides decken Kern-Themen ab | `help_window.py` Zeilen ~136–146 | Positiv | **Niedrig** | „QA & Governance“ / „Runtime“ ergänzen wenn IA komplex bleibt |

---

*Ende GUI_SEMANTIC_USABILITY_REVIEW.md*
