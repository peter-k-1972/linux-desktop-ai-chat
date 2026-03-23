# GUI-Navigationsanalyse — Linux Desktop Chat

**Datum:** 2026-03-22  
**Basis:** `navigation_registry.py`, `sidebar_config.py` / `sidebar.py`, Domain-Navs, `top_bar.py`, `workspace_host.py`, `breadcrumb`-Integration; Audit `PROJECT_GUI_UX_REVIEW_2026-03-22.md`.

---

## Navigationsstruktur (Ist)

### Ebene 1: Globale Sidebar

**Sektionen** (Reihenfolge laut `navigation_registry.py` → `_SECTIONS`):

1. **PROJECT** — Systemübersicht (Kommandozentrale), Projekte  
2. **WORKSPACE** — Chat, Knowledge, Prompt Studio, Workflows, Deployment, Betrieb, Agent Tasks  
3. **SYSTEM** — Control Center: Models, Providers, Agents, Tools, Data Stores  
4. **OBSERVABILITY** — Runtime/Debug: Introspection, QA Cockpit, QA Observability, EventBus, Logs, LLM Calls, Agent Activity, Metrics, System Graph *(Standard: eingeklappt laut `default_expanded=False`)*  
5. **QUALITY** — QA & Governance: Test Inventory, Coverage, Gaps, Incidents, Replay *(eingeklappt)*  
6. **SETTINGS** — acht Kategorien *(eingeklappt)*  

**Mechanik:** `NavigationSidebar` + `NavSectionWidget` — kollabierbare Header, Klick auf Eintrag emittiert `navigate_requested(area_id, workspace_id)` (`sidebar.py`).

### Ebene 2: Area-interne Subnavigation

- **Operations:** `OperationsNav` — feste Liste `WORKSPACES`, deutsch (`operations_nav.py`).  
- **Control Center:** englische Labels (`control_center_nav.py`).  
- **Runtime/Debug:** erweiterte Liste inkl. Markdown Demo, optional Theme Visualizer (`runtime_debug_nav.py`).  
- **QA & Governance:** englische Labels (`qa_governance_nav.py`).  
- **Settings:** eigene Kategorienavigation (`settings_workspace.py` + `SettingsNavigation`).

### Globale Shortcuts / sekundäre Einstiege

- **TopBar:** Status → Runtime/Debug; Workspace Map; **Befehle** → Command Palette; Hilfe (`top_bar.py`).  
- **Breadcrumbs:** Pfad Area/Workspace (`main_window.py` / Breadcrumb-Manager — indirekt über Audit).  

---

## Bewertung: Klarheit, Konsistenz, Hierarchie

| Kriterium | Note | Kommentar |
|-----------|------|-----------|
| **Klarheit** | B− | Hierarchie der **Areas** ist lernbar; **OBSERVABILITY** ist lang und technisch. |
| **Konsistenz** | C+ | Sidebar-Sektionstitel **englisch** (PROJECT, WORKSPACE), Operations-Subnav **deutsch**, Control Center/QA **englisch**. |
| **Hierarchie** | B | Trennung Operations vs. System vs. Settings ist **fachlich sinnvoll**. |

---

## Problemstellen

1. **Sprachbruch** zwischen Registry-Sektionen (engl. Großbuchstaben) und deutschsprachigen Operations-Labels — Nutzer müssen **zwei Konventionen** akzeptieren.  
2. **QA doppelt:** Sidebar-Einträge unter **QUALITY** (qa_test_inventory, …) **und** unter **OBSERVABILITY** (rd_qa_cockpit, rd_qa_observability) mit ähnlichen Tooltips („QA health…“) — **Navigationelle Redundanz** (`navigation_registry.py`).  
3. **Runtime/Debug Überlänge:** Viele Einträge gleicher „Monitoring“-Familie; **Introspection** vs. **System Graph** ohne erklärende Gruppierung in der UI (nur flache Liste).  
4. **Zwei Paletten** (Shell vs. Workbench) — siehe UX-Review; Navigation riskiert **inkonsistente** Power-User-Pfade.  
5. **Dashboard-Text** „Command Center“ vs. UI „Kommandozentrale“ / `command_center` — leichte **Begriffsverwirrung** (`dashboard_screen.py`).

---

## Klickpfade (qualitativ)

| Ziel | Typischer Pfad | Klicks (ca.) |
|------|----------------|--------------|
| Chat starten | Sidebar WORKSPACE → Chat | 1–2 (+ ggf. Sektion aufklappen) |
| Modellwechsel (global) | SYSTEM → Models **oder** im Chat Eingabe-/Header-Bereich | 2+ (je nach UI-Element) |
| Kontext (Chat) | Chat → Kontextleiste / Kontextmenü; **tiefere** Einstellungen: SETTINGS | 1–3 + Bereichswechsel |
| Workflows | WORKSPACE → Workflows | 1–2 |
| Projekt wechseln | TopBar Project Switcher **oder** Operations → Projekte | 1–2 |
| Hilfe | TopBar Hilfe (kontextbezogen) | 1 |

**Fazit:** Kernpfade sind **kurz**; **Reibung** entsteht bei **Einstellungen vs. Operations** und bei **doppelten QA-Einstiegen**.

---

## Sackgassen

- Keine evidenzbasierte **totale** Sackgasse in der Registry.  
- **Semantische** Sackgasse möglich: Nutzer erwartet **Workbench-Inspector-Funktionen**, findet **Stubs** (separater Pfad, nicht Sidebar-Standard).

---

## Verbesserungsvorschläge

1. **Ein Sprachmodell** für alle **sichtbaren** Nav-Labels (mindestens Subnavs angleichen).  
2. **QA in der Navigation benennen:** z. B. „QA (Governance)“ vs. „QA (Live)“ oder **ein** Bereich mit Tabs statt zwei Sidebar-Cluster.  
3. **OBSERVABILITY gruppieren** oder **„Erweitert“** auslagern (Markdown Demo, Theme Visualizer nur bei DevTools-Flag — teils schon).  
4. **Single Command Palette**-Story in Hilfe und TopBar-Tooltip textlich absichern.  
5. **Dashboard-Hinweis** an UI-Begriffe anbinden (Kommandozentrale statt „Command Center“).

---

*Ende Navigationsanalyse.*
