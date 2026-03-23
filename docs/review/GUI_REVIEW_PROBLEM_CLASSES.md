# GUI Review – Top-Level Problemklassen (Phase 5)

Konsolidierung aller Phasen in **harte Hauptklassen** (mit typischen Fundstellen).

---

## K1 — Feature- und Tiefen-Lücken (implementiert, aber nicht im Standard-Produktpfad)

- **Vollständiger QA-/Ops-Dashboard-Stack** (`CommandCenterView` mit Drilldowns) existiert im Code und in Tests, ist aber an den **Legacy-`MainWindow`** (`app/main.py`) gebunden, **nicht** an `ShellMainWindow` / `DashboardScreen`.  
- **Folge:** Standardnutzer sehen ein **anderes** Kommandozentrale-Erlebnis als der Code maximal hergibt.

*Querschnitt:* `app/gui/domains/command_center/command_center_view.py`, `app/main.py`, `dashboard_screen.py`, `docs/qa/architecture/COMMAND_CENTER_DASHBOARD_UNIFICATION.md`.

---

## K2 — Doppelte oder überlappende Informationsarchitektur

- **QA** gleichzeitig unter Sidebar-**QUALITY**, unter **OBSERVABILITY** (QA Cockpit / Observability) und auf dem **Dashboard**.  
- **Betrieb** (Operations) vs. **Incidents** (QA) — verwandte Themen, unterschiedliche Sektionen ohne erklärbare Nutzerregel in der UI.

*Querschnitt:* `app/core/navigation/navigation_registry.py`, `qa_governance_screen.py`, `runtime_debug_screen.py`.

---

## K3 — Halbintegrationen und ehrliche Platzhalter

- **Knowledge / Prompt Studio / Agent Tasks:** Teil-UI mit expliziten Platzhalter-Strings (siehe `docs/PLACEHOLDER_INVENTORY.md`).  
- **Workflows:** Backend-Executors für ComfyUI/Media bewusst nicht implementiert (`placeholder_executors.py`).  
- **Settings:** Project/Workspace-Kategorien als Empty States.

*Risiko:* Nutzer können nicht zuverlässig unterscheiden, was „noch nicht da“ vs. „live“ ist.

---

## K4 — Registry- und Navigations-Inkonsistenzen

- **Zentrale Navigation Registry** listet nicht alle Runtime-Workspaces (z. B. Markdown Demo, Theme Visualizer), während **RuntimeDebugNav** und **RuntimeDebugScreen** sie führen.  
- **Folge:** „Single source of truth“ ist für die Sidebar korrekt, für **alle** Navigationsziele nicht.

---

## K5 — CLI- und Umgebungsabhängigkeiten für nicht-triviale Aufgaben

- Setup (pip, Ollama) bleibt außerhalb der App.  
- **Context Replay / Repro-Registry** nur `app/cli/`.  
- **Devtools** (Theme Visualizer) env-gated.  
- **pytest**/CI für Qualitätssicherung.

*Teilweise gerechtfertigt*, muss aber **kommuniziert** werden, um keine „versteckten Pfad“-Wahrnehmung zu erzeugen.

---

## K6 — Legacy- und Dokumentationsaltlasten

- `agents_panels.py` (Demo) vs. `AgentManagerPanel` (kanonisch).  
- Ältere Architektur-Dokumente mit `app/ui/`-Pfaden (siehe `docs/STATUS_AUDIT.md`).  
- `PLACEHOLDER_INVENTORY.md` / Teile von `STATUS_AUDIT.md` **teilweise veraltet** bzgl. CC Tools/Data Stores und System-Status.

---

## K7 — Modernitäts- und Visual-Depth-Defizite (nach funktionaler Klarheit)

- Lokale Stylesheets und Hex-Farben in einzelnen CC-Panels neben globalem Token-System.  
- Fehlende oder uneinheitliche **Empty States** im Inspector.  
- DE/EN-Gemisch in Chrome (TopBar).

---

*Ende GUI_REVIEW_PROBLEM_CLASSES.md*
