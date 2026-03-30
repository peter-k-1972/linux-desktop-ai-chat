# Release-Arbeitspakete — Linux Desktop Chat

**Rollen:** Staff Engineer, Cursor-Implementierungsplaner.  
**Grundlage:** `release_decision.md`, `release_remediation_plan.md`, `architecture_status.md`, `dead_systems.md`, `feature_maturity_matrix.md`.  
**Zielversion:** `0.9.1` (laut Release-Entscheidung).  
**Reihenfolge:** zuerst Architekturblocker → Geister-Pakete → LEVEL-3-Transparenz (nur Reifegrad **3** laut Matrix).

---

## Phase A — Architekturblocker (vor Tag `v0.9.1`)

### WP-A1 — Root-Entrypoint: `run_workbench_demo.py` erlauben

| Feld | Inhalt |
|------|--------|
| **Titel** | Root-Entrypoint-Governance für Workbench-Demo |
| **Ziel** | `test_root_entrypoint_scripts_are_allowed` wird grün (`release_decision.md` B2). |
| **Betroffene Dateien** | `tests/architecture/arch_guard_config.py` (`ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS` um `"run_workbench_demo.py"` erweitern). `docs/04_architecture/ROOT_ENTRYPOINT_POLICY.md` (kurzer Absatz: Zweck des Skripts, Aufruf `python run_workbench_demo.py`). Optional: eine Zeile in `README.md` unter „Entwicklung / Demos“, falls dort Einträge gepflegt werden. |
| **Konkrete Änderungen** | 1) String `run_workbench_demo.py` in `ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS` aufnehmen. 2) In `ROOT_ENTRYPOINT_POLICY.md` dokumentieren: Workbench-Demo ist genehmigter Root-Entrypoint, analog `run_gui_shell.py`. **Kein** Verschieben des Skripts in diesem Paket (würde weitere Referenzen erfordern). |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_root_entrypoint_guards.py::test_root_entrypoint_scripts_are_allowed` |
| **Akzeptanzkriterien** | Obiger Test grün; Policy-Datei erwähnt das Skript namentlich; kein weiterer unbekannter `.py`-Entrypoint im Root ohne Policy-Eintrag. |
| **Abhängigkeiten** | Keine. |

---

### WP-A2 — Services: keine direkten Provider-Klassen-Imports

| Feld | Inhalt |
|------|--------|
| **Titel** | Provider-Orchestrierung aus `model_orchestrator_service` / `unified_model_catalog_service` entschlacken |
| **Status-Update 2026-03-30** | **Im Kern erledigt.** Direkte Provider-Klassen-Imports wurden aus `app/services/model_orchestrator_service.py` und `app/services/unified_model_catalog_service.py` entfernt; der Guard `pytest tests/architecture/test_provider_orchestrator_governance_guards.py::test_services_do_not_import_provider_classes` ist im gezielten Lauf grün. Phase A bleibt insgesamt offen, weil WP-A1, WP-A3, WP-A4 und WP-A5 weiter ausstehen. |
| **Ziel** | `test_services_do_not_import_provider_classes` grün (`architecture_status.md` §6). |
| **Betroffene Dateien** | `app/services/model_orchestrator_service.py`, `app/services/unified_model_catalog_service.py`, ggf. `app/providers/ollama_client.py` oder kleine Factory in `app/providers/` (nur wenn nötig), ggf. `app/services/chat_service.py` / Aufrufer. |
| **Konkrete Änderungen** | Entferne `from app.providers import LocalOllamaProvider`, `CloudOllamaProvider` (bzw. gleichwertige Imports) aus beiden Service-Dateien. Ersetze durch: Zugriff über **bereits vorhandene** `OllamaClient`- oder Infrastructure-APIs, oder delegiere an eine **einzige** Hilfsfunktion in `app/providers/` (kein `LocalOllamaProvider`-Typ im Service-Modultop-Level). Keine Ausweitung von `ALLOWED_PROVIDER_STRING_FILES` ohne separates Governance-Ticket. |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_provider_orchestrator_governance_guards.py::test_services_do_not_import_provider_classes`; bei Logikänderung zusätzlich `pytest tests/integration/test_model_settings_chat.py` |
| **Akzeptanzkriterien** | Kein Import von `LocalOllamaProvider` / `CloudOllamaProvider` in `app/services/*.py` außerhalb von Dateien, die der Guard explizit erlaubt (aktuell laut Audit: keine — daher null Treffer). Verhalten Models/Provider-UI unverändert aus Nutzersicht (manuelle Smoke: Control Center → Models/Providers). |
| **Abhängigkeiten** | Keine (parallel zu WP-A1 möglich). |

---

### WP-A3 — `ModelOrchestrator`: kein `app.services`-Import

| Feld | Inhalt |
|------|--------|
| **Titel** | Instrumentierungs-/Runtime-Pfad aus `core/models/orchestrator.py` herausziehen |
| **Ziel** | `test_no_forbidden_import_directions` und Paketregel `core`→`services` erfüllt (`architecture_status.md` §6). |
| **Betroffene Dateien** | `app/core/models/orchestrator.py` (Lazy-Imports `app.services.infrastructure`, `app.services.model_chat_runtime` entfernen). `app/services/model_chat_runtime.py` und/oder `app/services/chat_service.py` (oder anderer **einziger** Aufrufer des instrumentierten Streams), ggf. `app/services/chat_service.py` wo `ModelOrchestrator` genutzt wird. |
| **Konkrete Änderungen** | Alle Zeilen, die `get_infrastructure` / `stream_instrumented_model_chat` aus `orchestrator.py` laden, in eine **Service-Schicht** verlagern: z. B. nach dem Aufruf von `ModelOrchestrator`-Methoden wrappt `ChatService` (oder `model_chat_runtime`) die Instrumentierung. `orchestrator.py` importiert **nur** noch `app.core.*` und erlaubte `app.providers.*` laut bestehender Ausnahme. |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_app_package_guards.py::test_no_forbidden_import_directions`; `pytest tests/contracts/test_llm_stream_contract.py` und `pytest tests/integration/test_chat_streaming_behavior.py` (falls im Projekt vorhanden und üblich grün) |
| **Akzeptanzkriterien** | In `orchestrator.py` existiert kein `app.services`-Import (AST/Review). Streaming-Chat und Metriken-Pfad weiterhin ausführbar (Smoke: ein Kurz-Chat mit Mock/Ollama je nach Projektstandard). |
| **Abhängigkeiten** | Keine Pflicht gegenüber WP-A1/A2; empfohlen: nach WP-A2 mergen, falls beide `model_orchestrator_service` und Orchestrator berühren — dann Reihenfolge A2 vor A3 wählen, um Konflikte zu minimieren. |

---

### WP-A4 — `AppSettings`: kein `app.gui`-Import

| Feld | Inhalt |
|------|--------|
| **Titel** | Theme-ID-Normalisierung ohne GUI-Schicht in `core` |
| **Ziel** | `test_core_no_gui_imports`, `test_feature_packages_no_gui_imports`, relevante `test_no_forbidden_import_directions`-Treffer beseitigt (`architecture_status.md` §6). |
| **Betroffene Dateien** | `app/core/config/settings.py` (Import `app.gui.themes.theme_id_utils` entfernen). Neu: z. B. `app/core/config/builtin_theme_ids.py` mit `frozenset` der eingebauten Theme-IDs (`light_default`, `dark_default`, … — mit den tatsächlich in `ui_themes`/Registry vorkommenden IDs abgleichen). Optional: `run_gui_shell.py` / `app/services/infrastructure.py` oder Theme-Bootstrap: nach Laden von `AppSettings` einmalige Validierung gegen **live** `ThemeRegistry`, ohne Import aus `settings.py`. |
| **Konkrete Änderungen** | `_normalize_theme_id` prüft gegen die **kernseitige** Allowlist und Fallback `light_default`/`dark_default` wie bisher; **kein** `is_registered_theme_id` aus `gui`. Wenn installierte Themes dynamisch sein sollen: optionaler Parameter `AppSettings(..., theme_id_validator: Optional[Callable[[str], bool]] = None)` der nur vom GUI-Bootstrap gesetzt wird — dann darf `settings.py` weiterhin **keinen** `app.gui`-Import enthalten. |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_app_package_guards.py::test_core_no_gui_imports`, `::test_no_forbidden_import_directions`, `::test_feature_packages_no_gui_imports`; `pytest tests/integration/test_model_settings_chat.py`, `pytest tests/regression/test_settings_theme_tokens.py` |
| **Akzeptanzkriterien** | `settings.py` enthält keinen `app.gui`-String in Import-Statements. Persistenz von `theme_id` unverändert für bestehende Nutzerdaten (Regressionstests grün). |
| **Abhängigkeiten** | Keine; nach WP-A1–A3 empfohlen (letzter Arch-Fix vor Gesamtlauf). |

---

### WP-A5 — Architektur-Suite Gesamtabnahme

| Feld | Inhalt |
|------|--------|
| **Titel** | Release-Gate: vollständige `tests/architecture` |
| **Ziel** | `release_decision.md` B1 erfüllt; keine weiteren roten Tests in dieser Suite. |
| **Betroffene Dateien** | Keine Produktcode-Änderung, sofern WP-A1–A4 vollständig sind; sonst Nacharbeit an den genannten Stellen. |
| **Konkrete Änderungen** | Lokal/CI: vollständiger Lauf. Bei neuen Fehlern: einzelne Folge-PRs, **kein** Sammel-„Fix alles“. |
| **Tests, die grün werden müssen** | `pytest tests/architecture -q` (Exit-Code 0) |
| **Akzeptanzkriterien** | 0 Failures, 0 Errors; Ergebnis im MR/Release-Notiz vermerkt. |
| **Abhängigkeiten** | **Muss nach** WP-A1, WP-A2, WP-A3, WP-A4 abgeschlossen sein. |

---

## Phase B — Geister-Pakete (`dead_systems.md`, Klasse A)

### WP-B1 — Verzeichnis `app/models/` entfernen

| Feld | Inhalt |
|------|--------|
| **Titel** | Leeres Paket `app/models` bereinigen |
| **Ziel** | Kein leerer Top-Level-Ordner ohne Modul (`dead_systems.md`). |
| **Betroffene Dateien** | `app/models/` (komplett löschen inkl. `__pycache__`, falls nur Cache). |
| **Konkrete Änderungen** | Ordner löschen. Repo-weit: `rg 'app\.models|from app import models'` — Erwartung: **0** Treffer in Produktcode (Audit: bereits 0). |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_app_package_guards.py::test_app_root_only_allowed_files` (unverändert grün); Stichprobe `pytest tests/smoke/test_app_startup.py -q` |
| **Akzeptanzkriterien** | `app/models` existiert nicht mehr; keine neuen Importfehler. |
| **Abhängigkeiten** | **Nach** WP-A5 (stabiles Gate, klarer Baseline-Branch). |

---

### WP-B2 — Verzeichnis `app/diagnostics/` entfernen

| Feld | Inhalt |
|------|--------|
| **Titel** | Leeres Paket `app/diagnostics` bereinigen |
| **Ziel** | Kein Geister-Paket ohne `.py` (`dead_systems.md`). |
| **Betroffene Dateien** | `app/diagnostics/` |
| **Konkrete Änderungen** | Ordner löschen. `rg 'app\.diagnostics'` → 0 Treffer. |
| **Tests, die grün werden müssen** | `pytest tests/smoke/test_app_startup.py -q`; `pytest tests/architecture/test_app_package_guards.py -q` (Stichprobe) |
| **Akzeptanzkriterien** | Verzeichnis entfernt; CI grün. |
| **Abhängigkeiten** | **Nach** WP-B1 (sequenzielle, kleine Reviews). |

---

### WP-B3 — Leeren Domain-Ordner `app/gui/domains/project_hub/` entfernen

| Feld | Inhalt |
|------|--------|
| **Titel** | Ungenutzten `project_hub`-Domain-Stub entfernen |
| **Ziel** | Kein leerer GUI-Domain-Ordner (`dead_systems.md`). |
| **Betroffene Dateien** | `app/gui/domains/project_hub/` (nur `__pycache__` / leer) |
| **Konkrete Änderungen** | Ordner löschen. `rg 'project_hub'` im Repo — nur erlaubte Treffer (0 im `app/`-Produktcode laut Audit). |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_gui_governance_guards.py -q` (Stichprobe); `pytest tests/ui/test_command_center_dashboard.py -q` optional |
| **Akzeptanzkriterien** | Pfad existiert nicht mehr. |
| **Abhängigkeiten** | **Nach** WP-B2. |

---

## Phase C — LEVEL-3-Transparenz (`feature_maturity_matrix.md`)

*Ein Paket pro LEVEL-3-Zeile; Fokus: Hilfe + Navigation + minimaler Test, wo die Matrix „Tests: —“ oder fehlendes Help moniert.*

### WP-C1 — Settings: Privacy („nur informativ“ sichtbar machen)

| Feld | Inhalt |
|------|--------|
| **Titel** | Privacy-Workspace: Hilfe + Nav + ehrlicher Panel-Titel |
| **Ziel** | Nutzer sehen, dass keine vollwertigen Privacy-Schalter existieren (`feature_maturity_matrix.md`, `dead_systems.md`). |
| **Betroffene Dateien** | `help/settings/settings_privacy.md` (neu, mit YAML-Frontmatter: `id: settings_privacy`, `workspace: settings_privacy`, `category: settings`, `title`, `order`). `app/core/navigation/navigation_registry.py` — `NavEntry` für `settings_privacy`: fünftes Argument nach `description` ist `help_topic_id` → `"settings_privacy"` setzen (Parameterreihenfolge `help_topic_id` laut Dataclass). `app/gui/domains/settings/categories/privacy_category.py` — Titel- oder Beschreibungszeile um Formulierung **„Hinweis: keine Schalter — lokale Daten“** ergänzen (konkret 1–2 Sätze). `app/help/help_index.py` nur falls neue Kategorie/Mapping nötig (meist automatisch über `help/`). |
| **Konkrete Änderungen** | Markdown-Datei anlegen; Nav `help_topic_id` setzen; Panel-Beschreibung präzisieren. |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_gui_governance_guards.py::test_nav_entries_help_topic_ids_exist_in_help_index` |
| **Akzeptanzkriterien** | Kontexthilfe öffnet für Privacy ein Thema; Guard oben grün. |
| **Abhängigkeiten** | **Nach** WP-B3 (optional parallel zu B, wenn Help unabhängig — empfohlen **nach** Phase B, um Merge-Konflikte mit Arch-Fixes zu vermeiden). |

---

### WP-C2 — Control Center: Providers — Smoke-Test

| Feld | Inhalt |
|------|--------|
| **Titel** | Minimale Testabdeckung für `providers_workspace` |
| **Ziel** | LEVEL-3-Lücke „dünne Registry-Tests“ adressieren (`feature_maturity_matrix.md`). |
| **Betroffene Dateien** | Neu: `tests/unit/gui/test_providers_workspace_smoke.py` |
| **Konkrete Änderungen** | Test: `ProvidersWorkspace` (oder zentrale Workspace-Klasse aus `app/gui/domains/control_center/workspaces/providers_workspace.py`) mit `qtbot`/`QWidget`-Parent instanziieren, `show()` optional, keine Exceptions. Muster analog `tests/unit/gui/test_deployment_workspace.py` o. ä. aus dem Repo. |
| **Tests, die grün werden müssen** | `pytest tests/unit/gui/test_providers_workspace_smoke.py -q` |
| **Akzeptanzkriterien** | Genau eine neue Datei, ein klarer Smoke-Test, Laufzeit &lt; 10 s. |
| **Abhängigkeiten** | Nach WP-C1 oder parallel, wenn keine Dateikonflikte. |

---

### WP-C3 — QA: Gap Analysis — Hilfe + Nav

| Feld | Inhalt |
|------|--------|
| **Titel** | Hilfethema für `qa_gap_analysis` |
| **Ziel** | Registry/Nav: Help für „Gaps“ (`feature_maturity_matrix.md`). |
| **Betroffene Dateien** | Neu: `help/qa_governance/gap_analysis.md` (`id: qa_gap_analysis`, `workspace: qa_gap_analysis`, `category: qa_governance`). `app/core/navigation/navigation_registry.py` — Eintrag `qa_gap_analysis`: `help_topic_id="qa_gap_analysis"` setzen. |
| **Konkrete Änderungen** | Frontmatter + kurzer Text: Zweck (Lückenanalyse, Bezug zu Autopilot/Coverage), Beta-Hinweis. |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_gui_governance_guards.py::test_nav_entries_help_topic_ids_exist_in_help_index` |
| **Akzeptanzkriterien** | Hilfe aus Kontext der Nav öffnet; Guard grün. |
| **Abhängigkeiten** | Nach WP-C2 (lineare Review-Kette) oder unabhängig parallel. |

---

### WP-C4 — QA: Incidents — Hilfe + Nav + Smoke-Test

| Feld | Inhalt |
|------|--------|
| **Titel** | Incidents: Help, Nav-Verknüpfung, ein GUI-Smoke |
| **Ziel** | „Registry Tests: —“ teilweise geschlossen (`feature_maturity_matrix.md`). |
| **Betroffene Dateien** | Neu: `help/qa_governance/qa_incidents.md` (`id: qa_incidents`, `workspace: qa_incidents`). `app/core/navigation/navigation_registry.py` — `qa_incidents`: `help_topic_id="qa_incidents"`. Neu: `tests/unit/gui/test_qa_incidents_workspace_smoke.py` — `IncidentsWorkspace` instanziieren wie bei WP-C2. |
| **Konkrete Änderungen** | Help-Text: Liste, Detail, Inspector kurz erklären. |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_gui_governance_guards.py::test_nav_entries_help_topic_ids_exist_in_help_index`; `pytest tests/unit/gui/test_qa_incidents_workspace_smoke.py -q` |
| **Akzeptanzkriterien** | Beide Tests grün. |
| **Abhängigkeiten** | Nach WP-C3 empfohlen. |

---

### WP-C5 — QA: Replay Lab — Hilfe + Nav

| Feld | Inhalt |
|------|--------|
| **Titel** | Hilfethema für `qa_replay_lab` |
| **Ziel** | Help-Lücke schließen (`feature_maturity_matrix.md`). |
| **Betroffene Dateien** | Neu: `help/qa_governance/replay_lab.md` (`id: qa_replay_lab`, `workspace: qa_replay_lab`). `app/core/navigation/navigation_registry.py` — `qa_replay_lab`: `help_topic_id="qa_replay_lab"`. |
| **Konkrete Änderungen** | Verweis auf interne Doku `docs/qa/architecture/incident_replay/` als „weiterführend“ (Markdown-Link). |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_gui_governance_guards.py::test_nav_entries_help_topic_ids_exist_in_help_index` |
| **Akzeptanzkriterien** | Kontexthilfe für Replay funktioniert. |
| **Abhängigkeiten** | Nach WP-C4 empfohlen. |

---

### WP-C6 — Runtime: Logs-Workspace — Smoke-Test

| Feld | Inhalt |
|------|--------|
| **Titel** | `rd_logs` Workspace minimal testen |
| **Ziel** | Dünne Testanbindung laut Matrix (neben `runtime_overview`-Help). |
| **Betroffene Dateien** | Neu: `tests/unit/gui/test_rd_logs_workspace_smoke.py`; Klassenpfad aus `app/gui/domains/runtime_debug/workspaces/logs_workspace.py` (oder tatsächlicher Modulname im Tree). |
| **Konkrete Änderungen** | Eine Instanziierung + kein Crash. Kein neues Help-File nötig (Nav verweist bereits auf `runtime_overview` laut `navigation_registry.py`). |
| **Tests, die grün werden müssen** | `pytest tests/unit/gui/test_rd_logs_workspace_smoke.py -q` |
| **Akzeptanzkriterien** | Test grün. |
| **Abhängigkeiten** | Nach WP-C5 empfohlen. |

---

### WP-C7 — Runtime: Agent Activity — Hilfe + Nav

| Feld | Inhalt |
|------|--------|
| **Titel** | Hilfethema für `rd_agent_activity` |
| **Ziel** | Help + Nav; Matrix monierte fehlende Tests/Help — Help hier, Tests optional später (`feature_maturity_matrix.md`). |
| **Betroffene Dateien** | Neu: `help/runtime_debug/agent_activity.md` (`id: rd_agent_activity`, `workspace: rd_agent_activity`, `category: runtime_debug`). `app/core/navigation/navigation_registry.py` — `rd_agent_activity`: `help_topic_id="rd_agent_activity"`. |
| **Konkrete Änderungen** | Kurzbeschreibung Stream/Status/Detail-Panels. |
| **Tests, die grün werden müssen** | `pytest tests/architecture/test_gui_governance_guards.py::test_nav_entries_help_topic_ids_exist_in_help_index` |
| **Akzeptanzkriterien** | Hilfe erreichbar; Guard grün. |
| **Abhängigkeiten** | Nach WP-C6 empfohlen. |

---

## Reihenfolge-Übersicht (Cursor)

```
WP-A1 → WP-A2 → WP-A3 → WP-A4 → WP-A5 → WP-B1 → WP-B2 → WP-B3 → WP-C1 … → WP-C7
```

- **A2 vor A3** empfohlen, falls beide `model_orchestrator_service` und Streaming-Pfad berühren.  
- **A4 zuletzt** in der Arch-Gruppe, wenn Theme- und Chat-Pfade getrennt reviewt werden sollen.  
- **Phase C** strikt nacheinander, um Hilfe-/Nav-Reviews klein zu halten.

---

## Nach `0.9.1` (nicht Teil dieser Paketkette)

Themen aus `release_remediation_plan.md` P1/P2: `ui_application`-Adapter ohne `gui`, `app/llm`-Shim, Prompt-Studio-Duplikat, `agents/farm`, `FEATURE_REGISTRY`-Generator, pytest-Marker `context_observability` — **eigene Arbeitspakete** nach Tagging.

---

*Ende der Arbeitspakete — Umsetzung stoppt hier für den definierten Release-Zyklus bis WP-C7; `docs/FEATURE_REGISTRY.md` nach Help-/Nav-Änderungen regenerieren (`tools/generate_feature_registry.py`), sobald das Projekt das im Workflow vorsieht.*
