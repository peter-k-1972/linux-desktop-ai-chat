# Release-Remediation-Plan — Linux Desktop Chat

**Rollen:** Principal Software Architect, Release Remediation Planner.  
**Eingabe:** ausschließlich die vorhandenen Audit-Artefakte unter `docs/release_audit/` (Ground Truth), insbesondere `release_decision.md`, `architecture_status.md`, `dead_systems.md`, `release_readiness.md`, `feature_maturity_matrix.md`, `version_strategy.md`, `test_inventory.md`, `system_inventory.md`.  
**Ziel:** Umsetzbare, strikt priorisierte Arbeitspakete für den nächsten Release-Zyklus (**Zielversion laut Entscheidung: `0.9.1`**).

---

## Legende

| Priorität | Bedeutung |
|-----------|-----------|
| **P0** | Muss vor Tag **`v0.9.1`** erledigt sein (entspricht `release_decision.md` §3, sofern Arch-Gate verbindlich). |
| **P1** | Hohe Priorität; **darf** unmittelbar nach `0.9.1` folgen (Hotfix- oder `0.9.2`-Strang). |
| **P2** | Hygiene, Architekturverbesserung, Sichtbarkeits-/Dokumentationskorrekturen; kein Release-Blocker für `0.9.1`, sofern P0 erfüllt. |

---

## P0 — vor `0.9.1` (Blocker)

### P0-1: Verbotener Import `core` → `gui` in `AppSettings`

| Feld | Inhalt |
|------|--------|
| **Problem** | `app.core` importiert `app.gui.themes.theme_id_utils` — verletzt `FORBIDDEN_IMPORT_RULES` und scheitert an `test_core_no_gui_imports` / `test_no_forbidden_import_directions` / `test_feature_packages_no_gui_imports` (`architecture_status.md` §6). |
| **Betroffene Dateien / Module** | `app/core/config/settings.py` (`_normalize_theme_id`); indirekt genutzt: `app/gui/themes/theme_id_utils.py` (API `is_registered_theme_id`). Guards/Config: `tests/architecture/arch_guard_config.py` (`KNOWN_IMPORT_EXCEPTIONS` nur nach Review). |
| **Zielzustand** | Kein `app.gui.*`-Import aus `app/core/config/settings.py`; Theme-ID-Validierung ohne GUI-Layer oder über zur Laufzeit injizierte Strategie / reines `core`-Modul. |
| **Minimale akzeptable Lösung** | Lazy-Import entfernen und durch **kernseitige** Prüfung ersetzen (z. B. feste Allowlist bekannter IDs aus `core`, oder Callback/Validator, der vom **Bootstrap** aus `gui` registriert wird, ohne dass `settings.py` `app.gui` importiert). Alternativ: **eintrag in `KNOWN_IMPORT_EXCEPTIONS`** + dokumentierte Begründung in `SERVICE_GOVERNANCE_POLICY.md` / Guard-Review — nur wenn explizit beschlossen (widerspricht sonst „nicht verhandelbar“-Gate). |
| **Empfohlene Tests / QA-Nachweise** | `pytest tests/architecture/test_app_package_guards.py::test_core_no_gui_imports` grün; `test_no_forbidden_import_directions` grün; Smoke: `tests/smoke/test_app_startup.py` / `tests/integration/test_model_settings_chat.py` falls Theme-Persistenz berührt. |
| **Release-Relevanz** | **Blocker** für verbindliches Arch-Gate (`release_decision.md` B1). |

---

### P0-2: Verbotener Import `core` → `services` im Model-Orchestrator

| Feld | Inhalt |
|------|--------|
| **Problem** | `app/core/models/orchestrator.py` importiert `app.services.infrastructure` und `app.services.model_chat_runtime` (instrumentierter Pfad) — `("core","services")` verboten; `test_no_forbidden_import_directions` schlägt fehl (`architecture_status.md` §6). |
| **Betroffene Dateien / Module** | `app/core/models/orchestrator.py`; ggf. Aufrufer der instrumentierten Pfade; `app/services/model_chat_runtime.py`, `app/services/infrastructure.py` (Abhängigkeitsrichtung). |
| **Zielzustand** | Orchestrierung bleibt in `core` testbar; **kein** direkter Import von `app.services` aus `orchestrator.py`, ohne dass Guards aktualisiert werden. |
| **Minimale akzeptable Lösung** | Instrumentierung in **Service- oder Adapter-Schicht** verschieben (z. B. `ChatService` / Fassade ruft Orchestrator und danach Runtime-Instrumentierung auf), oder **explizite Ausnahme** in `KNOWN_IMPORT_EXCEPTIONS` mit Architektur-Review und Policy-Update. |
| **Empfohlene Tests / QA-Nachweise** | `pytest tests/architecture/test_app_package_guards.py::test_no_forbidden_import_directions` grün; bestehende Chat-/Streaming-Tests (`tests/contracts/test_llm_stream_contract.py`, `tests/integration/test_chat_streaming_behavior.py` — laut `system_inventory` / bestehende Suites) erneut grün. |
| **Release-Relevanz** | **Blocker** für B1. |

---

### P0-3: Services importieren konkrete Provider-Klassen

| Feld | Inhalt |
|------|--------|
| **Problem** | `test_services_do_not_import_provider_classes` schlägt fehl: direkte Imports von `LocalOllamaProvider` / `CloudOllamaProvider` in Services (`architecture_status.md` §6). |
| **Betroffene Dateien / Module** | `app/services/model_orchestrator_service.py`; `app/services/unified_model_catalog_service.py`; Referenzpolicy: `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md`; Guard: `tests/architecture/test_provider_orchestrator_governance_guards.py`. |
| **Zielzustand** | Services nutzen **OllamaClient / Infrastructure-Fassaden**, keine direkten Provider-Klassen-Imports, sofern Policy nicht durch **erlaubte** Dateiliste ausgenommen ist. |
| **Minimale akzeptable Lösung** | Provider-Erzeugung in `app/providers/` oder über bereits erlaubte Module kapseln; oder Policy + `ALLOWED_PROVIDER_STRING_FILES` / Guard-Liste **erweitern** — nur mit formalem Governance-Beschluss (Audit empfiehlt technische Bereinigung). |
| **Empfohlene Tests / QA-Nachweise** | `pytest tests/architecture/test_provider_orchestrator_governance_guards.py::test_services_do_not_import_provider_classes` grün; `tests/architecture/test_provider_orchestrator_governance_guards.py` (übrige Tests); `tests/integration/test_model_settings_chat.py` bei Berührung von Modellliste. |
| **Release-Relevanz** | **Blocker** für B1; schneidet **Control Center — Models/Providers** (`feature_maturity_matrix.md`, `release_decision.md` §2). |

---

### P0-4: Root-Entrypoint-Governance (`run_workbench_demo.py`)

| Feld | Inhalt |
|------|--------|
| **Problem** | `test_root_entrypoint_scripts_are_allowed` schlägt fehl: `run_workbench_demo.py` liegt im Repo-Root, ist aber nicht in `ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS` (`architecture_status.md` §5–6, `dead_systems.md` #13). |
| **Betroffene Dateien / Module** | Repo-Root `run_workbench_demo.py`; `tests/architecture/arch_guard_config.py` (`ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS`); `docs/04_architecture/ROOT_ENTRYPOINT_POLICY.md` (falls Referenz); README / `main.py`-Hinweise bei Verschiebung. |
| **Zielzustand** | Kein Verstoß gegen Root-Entrypoint-Guard: entweder Skript **explizit erlaubt und dokumentiert** oder **außerhalb des Roots** mit aktualisierten Pfaden. |
| **Minimale akzeptable Lösung** | **A)** `run_workbench_demo.py` in Allowlist aufnehmen + `ROOT_ENTRYPOINT_POLICY.md` / Release-Notes ergänzen, **oder** **B)** nach `scripts/workbench_demo.py` (o. ä.) verschieben und alle Referenzen (Doku, ggf. Desktop-Dateien) anpassen. |
| **Empfohlene Tests / QA-Nachweise** | `pytest tests/architecture/test_root_entrypoint_guards.py` grün; manuell: `python run_workbench_demo.py` bzw. neuer Pfad startet `MainWorkbench` (`dead_systems.md`). |
| **Release-Relevanz** | **Blocker** für `release_decision.md` **B2**; unabhängig von B1, aber für „releasekonformes Tagging“ verbindlich laut Entscheidungsvorlage. |

---

### P0-5: Gesamt-Gate `tests/architecture`

| Feld | Inhalt |
|------|--------|
| **Problem** | Bei letztem Audit **5** fehlgeschlagene Tests in **224** gesammelten Architekturtests — Gate nicht grün (`release_readiness.md`, `architecture_status.md`). |
| **Betroffene Dateien / Module** | Gesamtsuite `tests/architecture/`; die vier konkreten Ursachen sind P0-1–P0-4; keine weiteren Failures akzeptiert ohne neuen Beschluss. |
| **Zielzustand** | `pytest tests/architecture -q` Exit-Code **0** in der Release-CI (oder lokal identisch). |
| **Minimale akzeptable Lösung** | Alle genannten Einzelfixes; keine zusätzlichen roten Tests in derselben Suite zum Zeitpunkt des Tags. |
| **Empfohlene Tests / QA-Nachweise** | Vollständiger Lauf `pytest tests/architecture`; optional Drift-Radar laut `architecture_status.md` §5 (orthogonal, aber konsistent halten). |
| **Release-Relevanz** | **Meta-Blocker B1** (`release_decision.md` §3). |

---

## P1 — hohe Priorität (direkt nach `0.9.1` / `0.9.2`)

### P1-1: Geister-Packages und leerer Domain-Ordner

| Feld | Inhalt |
|------|--------|
| **Problem** | Leere bzw. nicht genutzte Strukturen verwirren Navigations- und Paketmodell; Klasse **A** in `dead_systems.md`. |
| **Betroffene Dateien / Module** | `app/models/` (ohne `.py`); `app/diagnostics/` (nur Cache); `app/gui/domains/project_hub/` (leer). |
| **Zielzustand** | Keine leeren Top-Level-Packages ohne Zweck; keine toten Domain-Ordner unter `gui/domains`. |
| **Minimale akzeptable Lösung** | Verzeichnisse entfernen **oder** minimales `README`/Platzhalter-Modul + Ticket für echte Implementierung. |
| **Empfohlene Tests / QA-Nachweise** | `pytest tests/architecture/test_app_package_guards.py` (App-Root-Dateien unverändert betroffen?); Volltext-Suche nach `app.models` / `app.diagnostics` / `project_hub` = 0 unbeabsichtigte Treffer. |
| **Release-Relevanz** | Laut `release_decision.md` §4 **verschiebbar** für `0.9.1`; laut `release_readiness.md` Checkliste **P1** — sollte **früh in `0.9.2`** landen, um Hygiene zu sichern. |

---

### P1-2: `ui_application` → `gui` im Settings-Adapter (Theme)

| Feld | Inhalt |
|------|--------|
| **Problem** | `service_settings_adapter.py` importiert `app.gui.themes` — weicht von Zielbild „Adapter ohne direkte GUI“ ab (`architecture_status.md` §1.8); `version_strategy.md` M2. |
| **Betroffene Dateien / Module** | `app/ui_application/adapters/service_settings_adapter.py`; ggf. neue schmale Schnittstelle in `ui_themes` / `core`. |
| **Zielzustand** | Theme-IDs / Legacy-Mapping ohne `app.gui`-Import aus `ui_application`; kanonischer Produktzugriff über `app.core.startup_contract`. |
| **Minimale akzeptable Lösung** | Theme-Hilfen über `app.core.startup_contract` oder klaren produktweiten Contract statt direkter GUI-Kopplung. |
| **Empfohlene Tests / QA-Nachweise** | Bestehende Settings-Presenter-Tests (`tests/unit/ui_application/test_settings_*` laut `test_inventory.md`); `pytest tests/architecture/test_ui_layer_guardrails.py` unverändert grün; ggf. neuer Contract-Test für Adapter-Imports. |
| **Release-Relevanz** | **Nicht** in den 5 Arch-Failures genannt — **nach** `0.9.1` zur Reduktion technischer Schuld (`version_strategy.md` M2). |

---

### P1-3: Privacy-Settings — fachliche Klärung

| Feld | Inhalt |
|------|--------|
| **Problem** | `settings_privacy`: Platzhalter-UI, keine Registry-Tests/`Help` (`dead_systems.md` #14, `feature_maturity_matrix.md`). |
| **Betroffene Dateien / Module** | `app/gui/domains/settings/categories/privacy_category.py`; Navigation/Registry; `docs/FEATURE_REGISTRY.md` (Regenerierung). |
| **Zielzustand** | Entweder echte steuerbare Privacy-Funktion **oder** klare „nur informativ“-Kommunikation + ggf. reduzierte Sichtbarkeit. |
| **Minimale akzeptable Lösung** | Produktentscheid dokumentieren; UI-Text/Nav anpassen; minimal ein Smoke- oder UI-Test, falls Eintrag sichtbar bleibt. |
| **Empfohlene Tests / QA-Nachweise** | Nach Implementierung: dedizierter Test unter `tests/unit/gui/` oder `tests/ui/`; sonst: Release Notes gemäß `release_decision.md` §5. |
| **Release-Relevanz** | `release_readiness.md` P1; für `0.9.1` nur nötig, wenn Marketing „Privacy“ als Feature bewirbt — sonst **P1** direkt nach Release. |

---

### P1-4: LEVEL-3-Features — Tests, Help oder „Preview“

| Feld | Inhalt |
|------|--------|
| **Problem** | Sieben Bereiche auf **LEVEL 3** (`feature_maturity_matrix.md`): u. a. `cc_providers`, `qa_gap_analysis`, `qa_incidents`, `qa_replay_lab`, `rd_logs`, `rd_agent_activity`, `settings_privacy` (Überschneidung P1-3). Registry teils **`Tests | —`**. |
| **Betroffene Dateien / Module** | Jeweilige `*_workspace.py` / Panels unter `app/gui/domains/...`; `help/`; `tools/generate_feature_registry.py` / `docs/FEATURE_REGISTRY.md`. |
| **Zielzustand** | Kein irreführendes „fertiges“ Produktbild: **mindestens** Help-Stubs oder einheitliche **Preview**-Kennzeichnung in UI + Notes (`version_strategy.md` M3). |
| **Minimale akzeptable Lösung** | Pro Workspace: **ein** gezielter Test **oder** Help-Artikel **oder** Nav-Label „Preview“ + Changelog-Hinweis. |
| **Empfohlene Tests / QA-Nachweise** | Bestehende Suites erweitern (`tests/unit/gui`, `tests/qa`, `tests/context` je nach Feature); Registry regenerieren. |
| **Release-Relevanz** | **Nach** `0.9.1` priorisieren, es sei denn, externe Kommunikation verspricht „fertige“ QA-/Runtime-Flächen — dann Teilmenge in Hotfix ziehen. |

---

## P2 — Hygiene / Architektur / Sichtbarkeit

### P2-1: Kompat-Paket `app/llm/`

| Feld | Inhalt |
|------|--------|
| **Problem** | Re-Export nach `app.core.llm` ohne nachgewiesene Consumer `from app.llm` (`dead_systems.md` #5). |
| **Betroffene Dateien / Module** | `app/llm/*`; Doku, die noch `app.llm` nennt. |
| **Zielzustand** | Ein kanonischer Importpfad `app.core.llm`. |
| **Minimale akzeptable Lösung** | Deprecation-Kommentar + Entfernung nach grep-gesichertem Nullverbrauch. |
| **Empfohlene Tests / QA-Nachweise** | Volltext-Repo-Suche; `pytest tests/` Smoke auf betroffene LLM-Pipelines. |
| **Release-Relevanz** | `0.9.2+`; keine Blocker für `0.9.1`. |

---

### P2-2: Prompt Studio — Duplikatpfad und Re-Export

| Feld | Inhalt |
|------|--------|
| **Problem** | `prompt_studio_detail_sink.py` re-exportiert; paralleles Mini-Package `app/gui/domains/prompt_studio/` vs. `operations/prompt_studio/` (`dead_systems.md` #6–7). |
| **Betroffene Dateien / Module** | `app/gui/domains/operations/prompt_studio/prompt_studio_detail_sink.py`; `app/gui/domains/prompt_studio/prompt_detail_sink.py`; Importe in Panels/Tests. |
| **Zielzustand** | Eine kanonische Moduladresse für `PromptDetailSink`. |
| **Minimale akzeptable Lösung** | Importe vereinheitlichen, Re-Export-Datei entfernen, Guardrails-Tests grün halten (`test_prompt_*_guardrails`). |
| **Empfohlene Tests / QA-Nachweise** | `pytest tests/architecture` (Prompt-Studio-Guardrails); `tests/smoke/test_prompt_studio_*`; `tests/unit/gui/test_prompt_detail_sink.py`. |
| **Release-Relevanz** | `0.9.2+`. |

---

### P2-3: `agents/farm` — Integration oder Archiv

| Feld | Inhalt |
|------|--------|
| **Problem** | Katalog ohne Produkt-Integration; nur Unit-Test (`dead_systems.md` #4). |
| **Betroffene Dateien / Module** | `app/agents/farm/*`; `tests/unit/agents/test_agent_farm_catalog.py`; Agent-Registry/GUI. |
| **Zielzustand** | Entweder angebunden oder aus `app/` heraus konsistent archiviert. |
| **Minimale akzeptable Lösung** | Archiv-Ordner + README **oder** ein GUI/Service-Hook — fachlich entscheiden (`version_strategy.md` M4). |
| **Empfohlene Tests / QA-Nachweise** | Bestehender Unit-Test beibehalten oder mitziehen; bei Integration: Golden-Path/Contract. |
| **Release-Relevanz** | `0.9.2+` / Backlog. |

---

### P2-4: QML-Runtime-Skelett

| Feld | Inhalt |
|------|--------|
| **Problem** | `QmlRuntime` als Architektur-Skelett ohne Produktionsintegration (`dead_systems.md` #12). |
| **Betroffene Dateien / Module** | `app/ui_runtime/qml/qml_runtime.py`; `tests/ui/test_theme_manifest_and_registry.py` (laut Audit-Kontext). |
| **Zielzustand** | Klar kommunizierter Lieferumfang: **nicht ausgeliefert** **oder** integrierter Pfad. |
| **Minimale akzeptable Lösung** | Ein Absatz in `docs/04_architecture/` oder `ui_runtime`-README + Changelog. |
| **Empfohlene Tests / QA-Nachweise** | Bestehende Tests unverändert; keine neuen Pflichten außer Doku. |
| **Release-Relevanz** | Niedrig; Transparenz für Contributors. |

---

### P2-5: Dokumentationsdrift `app.ui` vs. `app/gui`

| Feld | Inhalt |
|------|--------|
| **Problem** | `ARCHITECTURE_GUARD_RULES.md` beschreibt noch `app.ui`-Migration, obwohl kein Top-Level-`app/ui` mehr existiert (`architecture_status.md` §2, `system_inventory.md`). |
| **Betroffene Dateien / Module** | `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md`; ggf. weitere Migration-Docs. |
| **Zielzustand** | Dokumentation entspricht dem Ist-Dateibaum. |
| **Minimale akzeptable Lösung** | Kapitel anpassen oder als „historisch“ markieren mit Verweis auf `app/gui`. |
| **Empfohlene Tests / QA-Nachweise** | Optional `tools/doc_drift_check.py` (falls Pfade gepflegt). |
| **Release-Relevanz** | Onboarding/Review-Qualität; kein Binär-Gate. |

---

### P2-6: Pytest-Marker `context_observability` ohne Verwendung

| Feld | Inhalt |
|------|--------|
| **Problem** | `pytest.ini` definiert `context_observability`, aber keine `@pytest.mark.context_observability` in `tests/` (`test_inventory.md`). |
| **Betroffene Dateien / Module** | `pytest.ini`; passende Tests unter `tests/context/`. |
| **Zielzustand** | Marker entweder genutzt **oder** entfernt/ersetzt, um CI-Verhalten nicht zu täuschen. |
| **Minimale akzeptable Lösung** | Marker auf relevante Context-Tests anwenden **oder** aus `pytest.ini` streichen mit Kommentar. |
| **Empfohlene Tests / QA-Nachweise** | `pytest -m context_observability` (sinnvolle Teilmenge) oder N/A nach Entfernung. |
| **Release-Relevanz** | QA-Hygiene; `0.9.2+`. |

---

### P2-7: Root-Shims und Legacy-GUI (langfristig)

| Feld | Inhalt |
|------|--------|
| **Problem** | `app/db.py`, `app/ollama_client.py`, `app/critic.py` temporär im App-Root erlaubt; `app/main.py` + `gui/legacy` halten Test- und Legacy-Pfade (`dead_systems.md` #9–11). |
| **Betroffene Dateien / Module** | Genannte Root-Module; `tests/**` mit `from app.db`; `arch_guard_config.TEMPORARILY_ALLOWED_ROOT_FILES`. |
| **Zielzustand** | Kanonische Pfade unter `app/core/`, `app/providers/`, etc.; Legacy isoliert. |
| **Minimale akzeptable Lösung** | Schrittweise Import-Migration + Entfernung aus Allowlist (`version_strategy.md` / `release_readiness.md` Pfad zu 1.0). |
| **Empfohlene Tests / QA-Nachweise** | Voll-`pytest` nach Migrationswellen; Architektur-Guards. |
| **Release-Relevanz** | **Epic** über mehrere Minor-Releases; nicht P0 für `0.9.1`. |

---

### P2-8: FEATURE_REGISTRY — fehlende Runtime-Workspaces

| Feld | Inhalt |
|------|--------|
| **Problem** | `rd_introspection`, `rd_qa_cockpit`, `rd_qa_observability` in `GUI_SCREEN_WORKSPACE_MAP`, aber nicht als Features im Registry-Export (`feature_maturity_matrix.md` „Not in FEATURE_REGISTRY“). |
| **Betroffene Dateien / Module** | `tools/generate_feature_registry.py`; `docs/FEATURE_REGISTRY.md`; Nav/Screen-Code. |
| **Zielzustand** | Traceability Code ↔ Doku ↔ Tests konsistent. |
| **Minimale akzeptable Lösung** | Registry-Generator erweitern und einmal regenerieren. |
| **Empfohlene Tests / QA-Nachweise** | Manuelle Prüfung; optional `app.core.navigation.feature_registry_loader` Smoke. |
| **Release-Relevanz** | Operative Transparenz; `0.9.2+`. |

---

### P2-9: Chat-Panels — direkte Service-Aufrufe (Architekturziel)

| Feld | Inhalt |
|------|--------|
| **Problem** | Viele `get_*_service()`-Aufrufe in Chat-Panels statt durchgängig Presenter/Port (`architecture_status.md` §4). **Kein** fehlgeschlagener Guard — technisches Zielbild. |
| **Betroffene Dateien / Module** | u. a. `app/gui/domains/operations/chat/panels/chat_item_context_menu.py`, `chat_navigation_panel.py`, `topic_actions.py`. |
| **Zielzustand** | Schrittweise Angleichung an MVP-Sink/Port, wo sinnvoll. |
| **Minimale akzeptable Lösung** | Keine für `0.9.1`; für spätere Releases gezielte Refactor-Slices + Tests. |
| **Empfohlene Tests / QA-Nachweise** | Bestehende Chat-UI-/Contract-Tests; keine Regression. |
| **Release-Relevanz** | Langfristige Wartbarkeit; **P2**. |

---

## Abnahme-Checkliste (Cursor / CI)

1. **P0:** `pytest tests/architecture` → **0 Failures**.  
2. **P0:** Root-Entrypoint-Policy erfüllt (P0-4).  
3. **P1/P2:** Tickets aus diesem Dokument im Tracker mit **P0/P1/P2**-Label versehen; `0.9.1` enthält nur abgeschlossene **P0** (sofern keine Ausnahmebeschluss-Datei existiert).

---

*Dieses Dokument leitet sich ausschließlich aus den genannten Audit-Artefakten ab. Nach Umsetzung von P0 die Artefakte `architecture_status.md` / `release_readiness.md` aktualisieren oder neu erfassen.*
