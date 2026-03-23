# GUI Review – Source Map (Phase 0)

**Review-Stichtag:** 2026-03-22  
**Methodik:** Statische Code- und Doku-Analyse im Workspace (`app/gui/`, `app/core/navigation/`, `app/services/`, `app/cli/`, `docs/`, `help/`, Root-Reports). Kein interaktives E2E-Testen der laufenden App in dieser Session.

---

## 1. Primäre Ist-Basis (Code)

| Quelle | Rolle | Fundstellen |
|--------|--------|-------------|
| **Navigation (SSoT)** | Welche Bereiche/Workspaces existieren formal | `app/core/navigation/navigation_registry.py` |
| **Sidebar** | Ableitung aus Registry | `app/gui/navigation/sidebar_config.py` → `get_sidebar_sections()` |
| **Screen-Bootstrap** | area → Screen-Klassen | `app/gui/bootstrap.py` |
| **Operations** | Workspace-Stack | `app/gui/domains/operations/operations_screen.py` |
| **Control Center** | Workspace-Stack | `app/gui/domains/control_center/control_center_screen.py` |
| **QA & Governance** | Workspace-Stack | `app/gui/domains/qa_governance/qa_governance_screen.py` |
| **Runtime / Debug** | Workspace-Stack inkl. bedingter Devtools | `app/gui/domains/runtime_debug/runtime_debug_screen.py`, `runtime_debug_nav.py` |
| **Settings** | Kategorien-Registry | `app/gui/domains/settings/settings_workspace.py` |
| **Kommandozentrale (Shell)** | Dashboard-Karten | `app/gui/domains/dashboard/dashboard_screen.py`, `dashboard/panels/*.py` |
| **Kommandozentrale (Legacy-Stack-UI)** | Vollständiger QA-/Ops-Stack | `app/gui/domains/command_center/command_center_view.py` — **nur** eingebunden über `app/main.py` (Legacy `MainWindow`), **nicht** über `run_gui_shell.py` |
| **Hilfe** | In-App-Hilfe + semantische Doku-Suche | `app/help/help_window.py`, `app/gui/components/doc_search_panel.py` |
| **Command Palette** | Globale Navigation/Aktionen | `app/gui/commands/bootstrap.py`, `palette_loader.py` |
| **Infrastruktur-Snapshots** | Live-Zeilen für Tools/Data Stores | `app/services/infrastructure_snapshot.py` (Konsumenten: u. a. `tools_panels.py`, `data_stores_panels.py`, `system_status_panel.py`) |

---

## 2. Produkt- und Architektur-Dokumentation (Soll-/Ist-Abgleich)

| Dokument | Nutzen für dieses Review | Bekannte Drift |
|----------|--------------------------|----------------|
| `README.md` | Feature-Überblick, CLI-Hinweis, Shell vs. Legacy | Aktuell: Tools/Data Stores als Live-Snapshots beschrieben — **stimmt** mit aktuellem Code überein |
| `docs/01_product_overview/introduction.md` | Erwartete Kernfunktionen, Startbefehle | Verweist auf CLI für Ollama/Setup |
| `docs/ARCHITECTURE.md`, `docs/00_map_of_the_system.md` | Schichtenmodell | Querschnitt zu GUI-Modulen |
| `docs/STATUS_AUDIT.md` (2026-03-20) | Frühere GUI-Lücken | **Teilweise überholt:** Control-Center-Tools/Data-Stores und `SystemStatusPanel` sind im Code an `infrastructure_snapshot` angebunden; Dashboard-Karten QA/Incidents nutzen `QADashboardAdapter` |
| `docs/PLACEHOLDER_INVENTORY.md` (2026-03-20) | Platzhalter-Inventar | **Teilweise überholt** für CC Tools/Data Stores und System-Status — weiterhin relevant für Knowledge/Prompt/Agent-Task-Teilpanels und Settings Project/Workspace |
| `docs/qa/architecture/COMMAND_CENTER_DASHBOARD_UNIFICATION.md` | Soll: Zusammenführung Legacy-`CommandCenterView` und Shell-Dashboard | **Weiterhin strategisch relevant:** Standard-Shell nutzt `DashboardScreen`, **ohne** Einbettung von `CommandCenterView` |
| `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md` | QA-Drilldown-Views | Pfade/Verweise teils historisch (`app/ui/`) — siehe `docs/STATUS_AUDIT.md` |
| `docs/design/UI_GOVERNANCE_RULES.md` | Verbindliche UI-Regeln | Modernisierungs-Leitplanke |
| Weitere Design-Audits | Color/Icon/Layout | `docs/design/*`, Root-Reports (`DESIGN_TOKEN_SYSTEM_REPORT.md`, `LAYOUT_SPACING_AUDIT_REPORT.md`, …) |
| `help/**/*.md` | In-App-Help-Themen | Abgleich mit `help_topic_id` in Registry |

---

## 3. QA-, Test- und Operations-Artefakte

| Quelle | Rolle |
|--------|--------|
| `docs/REGRESSION_TEST_MATRIX.md`, `tests/AUDIT_MATRIX.md` | Erwartete Abdeckung |
| `docs/TEST_GAP_REPORT.md`, `docs/STATUS_AUDIT.md` | Collection-/CI-Risiko (`pytest --collect-only` — nicht in dieser Session wiederholt) |
| `docs/RELEASE_MANUAL_CHECKLIST.md` | Release ohne GUI? |
| `app/qa/dashboard_adapter.py` | Lesende QA-Zusammenfassung für Dashboard-Karten |

---

## 4. CLI und nicht-GUI-Pfade

| Quelle | Rolle |
|--------|--------|
| `app/cli/*.py` | Context Replay, Repro-Registry (ohne UI, laut Moduldocstrings) |
| `README.md` § Quickstart | `pip`, `ollama`, `python -m app` |

---

## 5. Explizit keine separate „Backup“-Codebasis

Im geprüften Tree keine zweite vollständige GUI-Kopie unter `backup/` o. Ä. als eigener Laufzeitpfad. **Legacy-Pfad:** `archive/run_legacy_gui.py` / `app/main.py` (explizit als LEGACY markiert).

---

## 6. Verbleibende Unsicherheiten

1. **Laufzeitverhalten** einzelner Workspaces (Fehlerbehandlung, leere DB, fehlende `docs/qa`-Dateien) ohne manuelle App-Session.
2. **Vollständige pytest-Collection** in CI — nur aus Doku referenziert, nicht erneut ausgeführt.
3. **DocSearchService / Chroma** für semantische Hilfe: benötigt aufgebauten Index; Fehlkonfiguration = degradierte Hilfe ohne dass der Review das live verifiziert.
4. **`app/critic.py`**: offenes TODO im Platzhalter-Inventar; keine vertiefende Nutzungsanalyse in diesem Review.
5. **Theme Visualizer:** Sichtbarkeit abhängig von `LINUX_DESKTOP_CHAT_DEVTOOLS` / `is_theme_visualizer_available()` — Umgebungsabhängig.

---

*Ende GUI_REVIEW_SOURCE_MAP.md*
