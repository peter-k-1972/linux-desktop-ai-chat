# Workbench-Layout-Konsistenz (global vs. Domains)

**Fragen:** Gleiche App? Domains außerhalb des Rasters? Sonderabstände? Legacy-Flächen?

---

## 1. Zwei Haupt-Schalen

| Schale | Einstieg | Struktur |
|--------|----------|----------|
| **Shell MainWindow** | `shell/main_window.py` | TopBar (QToolBar) → BreadcrumbBar → WorkspaceHost; Docks: Nav, Inspector, Bottom. |
| **MainWorkbench** | `workbench/main_workbench.py` | MenuBar + Toolbar → ContextActionBar → CanvasTabs; Docks: Explorer, Inspector, Console. |

**Befund:** Zwei **parallele** Hauptfenster-Philosophien — **erwartbar** (Kommandozentrale vs. Workbench), aber **kein gemeinsamer Layout-Helper** für „zentrale Spalte + drei Docks“.

---

## 2. Navigation

| Variante | Breite / Dichte | Dateien |
|----------|-----------------|---------|
| Shell Haupt-Sidebar | 240 (min 180, max 320) | `shell/layout_constants.py`, `docking_config.py` |
| Domain-Navs (Ops/CC/Runtime/QA) | 180–220 | `operations_nav.py`, `control_center_nav.py`, … |
| Workspace Graph (Dialog) | eigene Margins 16/12 | `workspace_graph.py` |

**Konsistenz:** Domain-Navs sind **schmaler** als Shell-Hauptnav — **absichtlich** (sekundäre Ebene). Visuell einheitlich **wenn** gleiche Item-Padding/QSS.

**Inkonsistenz:** Runtime-Nav nutzt **eigenes** Farb- und Typo-QSS (bereits Theme-Audit) — **fühlt sich wie Sub-App an** (gewollt für Monitoring, aber Dichte/Typo sollten dem Raster folgen).

---

## 3. Workspace Host vs. Canvas

| Bereich | Rand-Policy |
|---------|-------------|
| Shell `WorkspaceHost` | Stack wechselt Screens; viele Screens setzen **eigene** äußere Margins. |
| Workbench `CanvasTabs` | `canvas_base.py` **24px** auf Canvas-Root — klares, einheitliches Raster **innerhalb** Workbench. |

**Fazit:** **Workbench-Canvas** ist konsistenter als **Shell-Workspaces**.

---

## 4. Inspector

| Kontext | Innenabstand | Leer-Zustand |
|---------|----------------|--------------|
| Shell `InspectorHost` | diverse 12px Inspektoren | — |
| Workbench `InspectorPanel` | **10px** + PanelHeader | `EmptyStateWidget` 24/28 |

**Drift:** Workbench-Inspector enger + anderer Empty-State als Shell-`empty_state_widget` (16/24 Konstanten).

---

## 5. Bottom Panel

| Shell | Workbench |
|-------|-----------|
| `BOTTOM_PANEL_HEIGHT` 200 | `Console` Dock min-height gleicher Konstante-**Satz** in `shell/layout_constants` (auch Workbench importiert daraus) | aligned |

---

## 6. Domains mit Sonderstruktur

| Domain | Abweichung |
|--------|------------|
| **Chat** | Fixe 1200px Conversation + 48px Buttons — stärkster Bruch zum flexiblen Raster. |
| **Dashboard** | 32px Außen — luftiger als Operations (8–16). |
| **Prompt Studio** | Viele horizontale Splitter, feste Panel-Breiten (`prompt_manager_panel` fixed width) — Editor-typisch, ok. |
| **Deployment Releases** | Mehrfach `QSplitter` verschachtelt — eigene räumliche Logik. |
| **Legacy** | `legacy/*` — andere Margins (12, 24) und Button-Höhen. |

---

## 7. Legacy-Flächen

- `legacy/chat_widget.py`, `sidebar_widget.py`, `project_chat_list_widget.py` — **parallel** zur neuen Chat/Ops-Struktur.  
- Sichtbar wenn noch routing-mäßig erreichbar — visuell **andere Dichte** (spacing 15, 16, 24).

---

## 8. Antworten auf die Leitfragen

| Frage | Kurzantwort |
|-------|-------------|
| Fühlt sich alles wie eine App an? | **Größtenteils** — Ausnahmen: Monitoring-Farbraum, Chat-Fixbreite, Dashboard-Luft. |
| Domains außerhalb des Rasters? | **Chat (Breite/Höhe), Dashboard (32), Legacy**. |
| Sonderabstände/-höhen? | **6,10,14,28,40px** Spacing/Margins; **48px** Chat-Buttons; **10px** Workbench-Inspector. |
| Legacy abweichend? | **Ja** — klar abgrenzen oder migrieren. |

---

*Nächste Schritte:* [LAYOUT_PROBLEM_CLASSES.md](./LAYOUT_PROBLEM_CLASSES.md), [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md).
