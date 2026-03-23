# DOC UPDATE QUEUE

Abgeleitet aus `docs/DOC_DRIFT_REPORT.md`, `docs_manual/index/manual_index.json`, `docs/DOC_GAP_ANALYSIS.md`.  
Nur dateibezogene Aufgaben; nach Bearbeitung Drift-Check und ggf. `tools/build_manual_index.py` erneut ausführen.

---

## BLOCKER

### B-1 — Generierte Systemkarte vs. Dateisystem
- **Betroffene Datei:** `docs/SYSTEM_MAP.md`
- **Problem:** Drift-Report: fehlender Eintrag `app/diagnostics/`; historisch laut Gap-Analyse teils veraltete Einträge (z. B. kein `app/ui/`, kein Root-`app/settings.py`).
- **Zielzustand:** `SYSTEM_MAP.md` entspricht dem Ergebnis von `python3 tools/generate_system_map.py` nach Commit; keine nicht existierenden `app/`-Pfade in der Strukturliste.
- **Quelle im Code:** Ist-Baum unter `app/` (u. a. `app/diagnostics/`), Generator `tools/generate_system_map.py`.
- **Aufwand:** M

---

## HIGH

### H-1 — Fehlende Handbuch-Module (Drift + Index-Lücke)
- **Betroffene Dateien (neu anlegen):** `docs_manual/modules/core/README.md`, `docs_manual/modules/services/README.md`, `docs_manual/modules/pipelines/README.md`
- **Problem:** `DOC_DRIFT_REPORT.md` §3: große Pakete ohne `docs_manual/modules/<name>/README.md`; `manual_index.json` listet keine Units `core` / `services` / `pipelines` separat (nur indirekt über chains/gui).
- **Zielzustand:** Je eine README mit Verweis auf konkrete Code-Pfade (`app/core/`, `app/services/`, `app/pipelines/`) und auf `docs/FEATURES/` wo passend; danach `tools/build_manual_index.py` um Einträge für diese drei IDs erweitern und Index neu erzeugen.
- **Quelle im Code:** `app/core/`, `app/services/`, `app/pipelines/`
- **Aufwand:** L (3 Dateien + Index-Skript)

### H-2 — Produkt-Architektur vs. GUI/Core-Layout
- **Betroffene Datei:** `docs/01_product_overview/architecture.md`
- **Problem:** Laut `DOC_GAP_ANALYSIS.md` §3/§6: flache/veraltete `app/`-Darstellung; aktueller Schwerpunkt `app/gui/`, Settings unter `app/core/config/`.
- **Zielzustand:** Gleiche Fakten wie `docs/00_map_of_the_system.md` / Root-`README.md` Tabellen; keine Verweise auf nicht existierende Root-Module (`app/ui/`, Root-`settings.py`, …).
- **Quelle im Code:** `app/gui/`, `app/core/config/settings.py`, `docs/00_map_of_the_system.md`
- **Aufwand:** L

### H-3 — Developer-Setup zentral dokumentieren
- **Betroffene Datei (neu):** `docs/05_developer_guide/SETUP.md`
- **Problem:** `DOC_GAP_ANALYSIS.md` §3: kein durchgängiger Quickstart (venv, `pip install -r requirements.txt`, Ollama/ChromaDB, Startbefehl) im Developer-Guide.
- **Zielzustand:** Eine Datei mit konkreten Befehlen; explizit **beide** Startvarianten: `python main.py` und `python -m app` (wie `main.py`-Docstring / Root-README).
- **Quelle im Code:** `main.py`, `requirements.txt`, Root-`README.md`
- **Aufwand:** M

### H-4 — CLI / Context-Repro dokumentieren
- **Betroffene Datei (neu):** `docs/05_developer_guide/CLI_CONTEXT_TOOLS.md` (Name nach Teamkonvention anpassen ok)
- **Problem:** `DOC_GAP_ANALYSIS.md` §1/§9: kein Markdown zu `app/cli/`; `manual_index.json` → Unit `cli_tools` hat `related_help: []` und nur generische `related_docs`.
- **Zielzustand:** Tabelle oder Liste: Moduldatei → Zweck (ein Satz aus Docstring) → typischer Aufruf; Verweis auf `app/cli/*.py` und relevante Tests unter `tests/helpers/`.
- **Quelle im Code:** `app/cli/context_replay.py`, `app/cli/context_repro_*.py`, …
- **Aufwand:** M

### H-5 — Model-Cluster-Pfade in Architektur-Report
- **Betroffene Datei:** `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`
- **Problem:** Drift: Backticks zeigen auf `app/model_router.py` etc.; Ist liegt unter `app/core/models/router.py`, `registry.py`, `orchestrator.py`, `roles.py`, `escalation_manager.py`.
- **Zielzustand:** Alle Code-Zitate auf existierende Pfade unter `app/core/models/` (oder korrekte Service-Oberfläche) umbiegen.
- **Quelle im Code:** `app/core/models/*.py`, `app/services/model_service.py`
- **Aufwand:** M

### H-6 — Chat-Session-UI: falscher Panel-Dateiname
- **Betroffene Dateien:** `docs/04_architecture/DESIGN_SYSTEM_LIGHT.md`, `docs/06_operations_and_qa/CHAT_LIST_PROJECT_UX.md`, `docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md`, `docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md`
- **Problem:** Drift: `app/gui/domains/operations/chat/panels/session_explorer_panel.py` existiert nicht; Verzeichnis hat u. a. `conversation_panel.py`, `chat_navigation_panel.py`, …
- **Zielzustand:** Pro Datei den tatsächlich gemeinten Dateinamen setzen (nach inhaltlicher Zuordnung) oder Sätze auf „Session-Explorer / Chat-Navigation“ ohne falschen Pfad umstellen.
- **Quelle im Code:** `app/gui/domains/operations/chat/panels/*.py`
- **Aufwand:** S

### H-7 — Settings-Navigation: falscher Modulname
- **Betroffene Dateien:** `docs/04_architecture/SETTINGS_CONSOLIDATION_REPORT.md`, `docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md`
- **Problem:** Drift: `app/gui/domains/settings/settings_nav.py` existiert nicht; Implementierung: `app/gui/domains/settings/navigation.py`.
- **Zielzustand:** Backticks/Dateipfade auf `navigation.py` korrigieren.
- **Quelle im Code:** `app/gui/domains/settings/navigation.py`
- **Aufwand:** S

### H-8 — QA: Context-Explainability Test-Pfade
- **Betroffene Dateien:** `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`, `docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md`
- **Problem:** Drift: genannte Tests `tests/context/...`, `tests/scripts/...` u. a. fehlen oder weichen ab.
- **Zielzustand:** Jede genannte Testdatei existiert im Repo oder durch korrekten Pfad ersetzt (z. B. unter `tests/chat/`, `tests/context/` recherchieren).
- **Quelle im Code:** `tests/**/test_*context*.py` (Ist-Liste per `find`/`rg`)
- **Aufwand:** M

### H-9 — Platzhalter-Test in QA-Generator-Doku
- **Betroffene Dateien:** `docs/qa/architecture/coverage/QA_COVERAGE_MAP_GENERATOR.md`, `docs/qa/governance/incident_schemas/BINDINGS_JSON_FIELD_STANDARD.md`, `docs/qa/governance/incident_schemas/INCIDENT_YAML_FIELD_STANDARD.md`
- **Problem:** Drift: `tests/failure_modes/test_foo.py` existiert nicht.
- **Zielzustand:** Beispiel durch realen Testpfad ersetzen oder als rein illustratives Schema kennzeichnen ohne konkreten Pfad.
- **Quelle im Code:** `tests/failure_modes/*.py`
- **Aufwand:** S

---

## MEDIUM

### M-1 — Großer Refactor-Report: Root-Legacy-Pfade
- **Betroffene Datei:** `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`
- **Problem:** Drift: mehrere Backticks (`app/chat_widget.py`, `app/core/feature_registry_loader.py`, `app/file_explorer_widget.py`, `app/message_widget.py`, `app/project_chat_list_widget.py`, `app/sidebar_widget.py`, `app/web_search.py`, `app/settings.py`, …).
- **Zielzustand:** Sammelkorrektur auf Ist-Pfade (`app/gui/legacy/…`, `app/core/navigation/feature_registry_loader.py`, `app/core/config/settings.py`, `app/tools/web_search.py`, …) gemäß Drift-Tabelle §2.
- **Quelle im Code:** Zielpfade wie in `DOC_DRIFT_REPORT.md` Spalte „Probable actual path“.
- **Aufwand:** M

### M-2 — Weitere Architektur-/Guide-Dateien mit Legacy-Pfaden
- **Betroffene Dateien:** u. a. `docs/04_architecture/GUI_ARCHITECTURE_GUARDRAILS.md`, `docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md`, `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md`, `docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md`, `docs/05_developer_guide/PHASE1_CHANGES.md`, `docs/CHANGELOG_NORMALIZATION.md`, `docs/DOC_GAP_ANALYSIS.md`, `docs/FEATURES/providers.md` (siehe Drift §2/§6)
- **Problem:** Einzelne falsche Backtick-Pfade (siehe Drift-Report Zeilen 25–44, 84–129).
- **Zielzustand:** Pro Fundstelle Pfad korrigieren oder Fußnote „historisch“ wenn bewusst Migrationstext.
- **Quelle im Code:** wie Drift „Probable actual path“
- **Aufwand:** M

### M-3 — Icons: app/gui/icons/svg → assets
- **Betroffene Dateien:** `docs/05_developer_guide/PHASE1_CHANGES.md`, `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`, `docs/06_operations_and_qa/CONSOLIDATION_REPORT.md`, `docs/06_operations_and_qa/CONSOLIDATION_RULES.md`
- **Problem:** Drift: `app/gui/icons/svg` existiert nicht; kanonisch `assets/icons/svg/` laut Konsolidierungsdoku.
- **Zielzustand:** Backticks auf `assets/icons/svg/` vereinheitlichen, wo aktueller Ist-Zustand gemeint ist.
- **Quelle im Code:** `assets/icons/svg/`, Icon-Auflösung in Code (`get_icons_dir()` o. Ä. bei Bedarf nachziehen)
- **Aufwand:** S

### M-4 — UX-Bugfix-Dokument: project_context_manager
- **Betroffene Datei:** `docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md`
- **Problem:** Drift: `app/core/project_context_manager.py` → Ist `app/core/context/project_context_manager.py`
- **Zielzustand:** Pfad im Text anpassen.
- **Quelle im Code:** `app/core/context/project_context_manager.py`
- **Aufwand:** S

### M-5 — Refactoring-Analysen: fiktive GUI-Unterordner
- **Betroffene Dateien:** `docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md`, `docs/refactoring/PROJECT_UI_TO_GUI_ANALYSIS.md`, `docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md`
- **Problem:** Drift: `app/gui/domains/knowledge|project|prompts/` als Verzeichnis-Pfad; Ist nutzt u. a. `operations/knowledge`, `operations/projects`, `operations/prompt_studio` unter `app/gui/domains/`.
- **Zielzustand:** Pfade auf reale `app/gui/domains/operations/...`-Struktur korrigieren oder als historische Analyse klar markieren.
- **Quelle im Code:** `app/gui/domains/operations/`
- **Aufwand:** M

### M-6 — settings_backend-Pfad
- **Betroffene Dateien:** `docs/refactoring/GUI_POST_MIGRATION_AUDIT.md`, `docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md`
- **Problem:** Drift: `app/gui/settings_backend.py` → Ist `app/core/config/settings_backend.py`
- **Zielzustand:** Backticks korrigieren.
- **Quelle im Code:** `app/core/config/settings_backend.py`
- **Aufwand:** S

### M-7 — SETTINGS_AND_WORKSPACES_HARDENING_ANALYSIS: Zahl „2 Kategorien“
- **Betroffene Datei:** `docs/04_architecture/SETTINGS_AND_WORKSPACES_HARDENING_ANALYSIS.md`
- **Problem:** Drift §4: numerische Aussage „2 Settings-Kategorien“ vs. 8 Kategorien in `settings_workspace.py` / `navigation.py` (Heuristik-Flag).
- **Zielzustand:** Satz präzisieren (Workspaces vs. Kategorien) oder Zahl anpassen; mit `DEFAULT_CATEGORIES` in `app/gui/domains/settings/navigation.py` abgleichen.
- **Quelle im Code:** `app/gui/domains/settings/navigation.py`, `app/gui/domains/settings/settings_workspace.py`
- **Aufwand:** S

### M-8 — SETTINGS_ARCHITECTURE vs. Code (Gap-Matrix)
- **Betroffene Datei:** `docs/04_architecture/SETTINGS_ARCHITECTURE.md`
- **Problem:** `DOC_GAP_ANALYSIS.md` §4/§6 behauptet Abweichung zur Category-Registry (Stand Analyse 2026-03-20).
- **Zielzustand:** Datei Zeile für Zeile mit `_category_factories` / `DEFAULT_CATEGORIES` abgleichen; veraltete Abschnitte entfernen oder anpassen.
- **Quelle im Code:** `app/gui/domains/settings/settings_workspace.py`, `navigation.py`
- **Aufwand:** M (nach Stichprobe ggf. S)

### M-9 — Repro-Registry / CLI im Markdown auffindbar
- **Betroffene Dateien (neu oder erweitern):** z. B. `docs/05_developer_guide/CLI_CONTEXT_TOOLS.md` (kann H-4 erweitern) und/oder `docs_manual/modules/context/README.md`
- **Problem:** `DOC_GAP_ANALYSIS.md` §4: keine Treffer zu `repro_registry` / `context_repro` in Doku.
- **Zielzustand:** Kurzabschnitt mit Dateiliste `app/context/replay/repro_registry_*.py` + Link zu CLI-Doku.
- **Quelle im Code:** `app/context/replay/`, `app/cli/context_repro_*.py`
- **Aufwand:** S (wenn H-4 ohnehin erledigt)

### M-10 — help_index-Kategorien vs. help/-Ordnerstruktur
- **Betroffene Dateien:** `app/help/help_index.py` (Docstring/Kommentar), ggf. neue leere `help/<kategorie>/README.md` **oder** `docs/ARCHITECTURE.md` Abschnitt „Help-Fallback“
- **Problem:** `DOC_GAP_ANALYSIS.md` §4: Kategorien ohne Ordner unter `help/`.
- **Zielzustand:** Entweder Ordner/Stub-READMEs anlegen **oder** in zentraler Doku erklären, welche Kategorien nur über Fallback (`docs/`) gespeist werden — eine Variante wählen und konsistent halten.
- **Quelle im Code:** `app/help/help_index.py` (`HELP_CATEGORIES`)
- **Aufwand:** M

### M-11 — tests/help in Architekturvorschlag
- **Betroffene Datei:** `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`
- **Problem:** Drift: `tests/help/` existiert nicht.
- **Zielzustand:** Vorschlag aktualisieren (echtes Testlayout unter `tests/` referenzieren) oder als Zielbild kennzeichnen.
- **Quelle im Code:** `tests/` Ist-Struktur
- **Aufwand:** S

### M-12 — tools.py / Delegation-Doku (Chains)
- **Betroffene Datei:** `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md` (und ggf. `docs/FEATURES/chains.md`)
- **Problem:** Drift: `app/tools.py` ohne klaren Ersatz; Gap §1: „Chains“ nicht als separates Paket — Delegation über `app/commands/`, Workflows-Doku.
- **Zielzustand:** Verweis auf `app/commands/chat_commands.py` / `app/pipelines/` statt toten Root-Pfaden.
- **Quelle im Code:** `app/commands/`, `app/pipelines/`
- **Aufwand:** S

---

## LOW

### L-1 — Aggregat app/ui/ in aktiven Manuals
- **Betroffene Dateien:** siehe Drift §2 aggregierte Quellen (v. a. `docs/04_architecture/*MIGRATION*.md`, `docs_manual/**` falls betroffen)
- **Problem:** 101 Pfade unter entferntem `app/ui/`-Baum in Migrationstexten.
- **Zielzustand:** Für **aktiv genutzte** Einstiegsdokumente: Fußnote „historisch“ oder Pfad auf `app/gui/` ersetzen; reine Archiv-Reports optional unangetastet lassen mit Hinweis im Kopf.
- **Quelle im Code:** `app/gui/`
- **Aufwand:** L (bei Vollsubstitution), S (nur Kerndokumente)

### L-2 — DOC_GAP_ANALYSIS selbst aktualisieren
- **Betroffene Datei:** `docs/DOC_GAP_ANALYSIS.md`
- **Problem:** Teilweise veraltet (z. B. Root-README existiert; `introduction.md`-Link ggf. bereits `../02_user_manual/models.md`).
- **Zielzustand:** Matrix und §2–§8 mit Ist-Stand abgleichen nach Umsetzung der HIGH/MEDIUM-Punkte.
- **Quelle im Code:** Repo-Ist + neuen Drift-Report
- **Aufwand:** M

### L-3 — python vs. python3 in Doku
- **Betroffene Dateien:** diverse unter `docs/` (siehe Gap §5)
- **Problem:** Inkonsistente Aufrufe in Beispielen.
- **Zielzustand:** Pro Bereich eine Konvention (z. B. `python3` für Linux-Desktop-Chat) in `docs/05_developer_guide/SETUP.md` festlegen und Stichproben angleichen.
- **Quelle im Code:** —
- **Aufwand:** S

### L-4 — manual_index: CLI ohne Help-Links
- **Betroffene Datei:** `tools/build_manual_index.py` (Unit `cli_tools`)
- **Problem:** `manual_index.json`: `related_help` leer für `cli_tools`.
- **Zielzustand:** Nach H-4: optional `related_help` auf Troubleshooting oder Getting-started setzen, wenn sinnvoll; sonst bewusst leer lassen und in README des Index kommentieren.
- **Quelle im Code:** —
- **Aufwand:** S

### L-5 — USER_GUIDE / ai_studio an Workspaces anbinden
- **Betroffene Datei:** `docs/02_user_manual/ai_studio.md`
- **Problem:** `DOC_GAP_ANALYSIS.md` §4: Begriffe (Side-Panel, Toolbar) nicht eindeutig auf aktuelle Workspace-IDs gemappt.
- **Zielzustand:** Workspace-Namen aus `FEATURE_REGISTRY.md` / `manual_resolver.py` übernehmen.
- **Quelle im Code:** `app/gui/domains/`, `docs/FEATURE_REGISTRY.md`
- **Aufwand:** M

---

## BATCHES

### Batch 1 – Root / Einstieg
- Root-`README.md`: gegen `DOC_GAP_ANALYSIS.md` §8 Quick Win 1 abgleichen (fehlende Links ergänzen, falls noch Lücken).
- `docs/README.md`: Verweis auf `DOC_UPDATE_QUEUE.md` optional ergänzen.
- **H-3** `docs/05_developer_guide/SETUP.md`
- **L-3** Konvention `python`/`python3`

### Batch 2 – Settings / Context
- **M-7**, **M-8** Settings-Zahlen und SETTINGS_ARCHITECTURE
- **H-7** settings_nav → navigation
- **M-4** project_context_manager-Pfad
- `manual_index`: nach neuen Modulen **H-1** `core`/`services`/`pipelines` (Teil Kontext/Services)
- Gap: Endnutzer-Kontext — `help/settings/settings_chat_context.md` / `help/operations/chat_overview.md` mit Verweis auf `app/core/config/chat_context_enums.py` (DOC_GAP §8 Punkt 5)

### Batch 3 – GUI / Navigation
- **B-1** SYSTEM_MAP regenerieren
- **H-6** Chat-Panels
- **M-1**, **M-2** (GUI-relevante Teile: Legacy-Pfade, Icons **M-3**)
- **H-2** `docs/01_product_overview/architecture.md`
- **L-1** app/ui-Aggregat (nur aktive Docs)
- **L-5** ai_studio.md

### Batch 4 – CLI / QA Tools
- **H-4** CLI_CONTEXT_TOOLS.md
- **H-8**, **H-9** QA-Testpfade
- **M-9** repro_registry Querverweise
- **M-11** tests/help-Vorschlag

### Batch 5 – Generated Docs Refresh
- **B-1** abschließen: `python3 tools/generate_system_map.py` → Commit `docs/SYSTEM_MAP.md`
- Optional: `python3 tools/generate_trace_map.py`, `python3 tools/generate_feature_registry.py` wenn Code-/Help-Struktur geändert wurde
- `python3 tools/doc_drift_check.py` → `docs/DOC_DRIFT_REPORT.md` prüfen
- `python3 tools/build_manual_index.py` → `docs_manual/index/manual_index.json` + `.md` nach **H-1** / **L-4**

---

*Ende der Queue.*
