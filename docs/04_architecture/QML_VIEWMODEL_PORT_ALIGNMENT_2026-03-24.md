# QML ViewModel — Port-/Adapter-Angleichung (Abschlussbericht)

**Datum:** 2026-03-24  
**Ziel:** Nicht-Chat-QML-Domänen auf den Pfad *ViewModel → Presenter/Fassade → Port → Adapter → Service* bringen, ohne UI neu zu bauen.

---

## 1. Bestandsanalyse (Ist)

| Domäne | QML ViewModel | Presenter/Fassade (vorher) | Service-Zugriffe (vorher) | UI-Operationen (Kurz) |
|--------|---------------|----------------------------|---------------------------|------------------------|
| **Prompts** | `python_bridge/prompts/prompt_viewmodel.py` | `PromptPresenterFacade` | `get_prompt_service()` via Factory | Liste/Filter, CRUD, Versionen lesen |
| **Projects** | `python_bridge/projects/project_viewmodel.py` | — | `get_project_service`, `get_workflow_service`, `get_agent_service` | Projektliste, Inspector, Chats/WF/Agents/Dateien, aktiv setzen, anlegen/löschen |
| **Workflows** | `python_bridge/workflows/workflow_viewmodel.py` | — | `get_workflow_service()` | Liste, Graph laden/speichern, Runs listen, `start_run` |
| **Agents** | `python_bridge/agents/agent_viewmodel.py` | — | `get_agent_registry()` | Roster refresh, Auswahl, lokale Task-/Feed-UI (kein echter Backend-Task) |
| **Deployment** | `python_bridge/deployment/deployment_viewmodel.py` | — | `get_deployment_operations_service()` | Releases, Pipeline-Simulation, `update_release`, `record_rollout` |
| **Settings** | `python_bridge/settings/settings_viewmodel.py` | — | `get_infrastructure().settings` | Ledger über `AppSettings`, `save()`, `load()` |

**Read-only vs. Mutation (grob):** Listen/Details überwiegend read; Mutationen: Prompts save/create, Projects create/delete/set_active, Workflows save/run, Deployment update/rollout, Settings `saveSettings`.

---

## 2. Zielarchitektur pro Domäne

| Domäne | Port (neu) | Adapter (neu) | ViewModel nutzt |
|--------|------------|---------------|-----------------|
| Prompts | `QmlPromptShelfOperationsPort` | `ServiceQmlPromptShelfAdapter` | `PromptPresenterFacade(port=…)` |
| Projects | `QmlProjectWarRoomPort` | `ServiceQmlProjectWarRoomAdapter` | `ProjectViewModel(port=…)` |
| Workflows | `QmlWorkflowCanvasPort` | `ServiceQmlWorkflowCanvasAdapter` | `WorkflowStudioViewModel(port=…)` |
| Agents | `QmlAgentRosterPort` | `ServiceQmlAgentRosterAdapter` | `AgentViewModel(port=…)` |
| Deployment | `QmlDeploymentStudioPort` | `ServiceQmlDeploymentStudioAdapter` | `DeploymentViewModel(port=…)` |
| Settings | `QmlSettingsLedgerPort` | `ServiceQmlSettingsLedgerAdapter` | `SettingsViewModel(port=…)` |

**Bewusst nicht im Port:** Vollständiges `PromptStudioPort` (Widget-Workspace), ThemeManager-Aufrufe (bleiben im ViewModel bei `get_theme_manager()` nach Save), reine QML-Filterlogik in `PromptPresenterFacade`.

---

## 3. Port-/Adapter-Design

Neue Dateien unter `app/ui_application/ports/` und `app/ui_application/adapters/`:

- `qml_prompt_shelf_port.py` / `service_qml_prompt_shelf_adapter.py`
- `qml_project_war_room_port.py` / `service_qml_project_war_room_adapter.py`
- `qml_workflow_canvas_port.py` / `service_qml_workflow_canvas_adapter.py`
- `qml_agent_roster_port.py` / `service_qml_agent_roster_adapter.py`
- `qml_deployment_studio_port.py` / `service_qml_deployment_studio_adapter.py`
- `qml_settings_ledger_port.py` / `service_qml_settings_ledger_adapter.py`

Ports sind **schmal** und an die bestehenden ViewModel-Aufrufe angepasst; Adapter kapseln **ausschließlich** Delegation an bestehende Services/Registry.

---

## 4. Schrittweise Umsetzung (Reihenfolge A–F)

Umgesetzt in der vorgegebenen Reihenfolge: **A Prompts → B Projects → C Workflows → D Agents → E Deployment → F Settings.**

Geänderte ViewModels: alle unter `python_bridge/*/` für die genannten Domänen.  
Geänderte Tests: `tests/qml_*`, plus neue Architektur-/Unit-Tests.

---

## 5. Tests

| Test | Zweck |
|------|--------|
| `tests/architecture/test_qml_python_bridge_no_direct_services.py` | Verbietet `from app.services.*` in `python_bridge` (Ausnahme: `WorkflowNotFoundError` in `workflow_viewmodel.py`) |
| `tests/unit/ui_application/test_qml_port_adapters.py` | Delegation Prompt-Shelf-Adapter (Monkeypatch) |
| Bestehende QML-Smokes | `tests/qml_projects`, `qml_prompt_studio`, `qml_deployment`, `qml_agents`, `qml_settings`, `qml_chat` |

---

## 6. Abschlussbericht

### 6.1 Geänderte / neue Dateien

- **Neu:** alle Port-/Adapter-Dateien oben unter `app/ui_application/`
- **Geändert:** `python_bridge/prompts/prompt_presenter_facade.py`, `python_bridge/projects/project_viewmodel.py`, `python_bridge/workflows/workflow_viewmodel.py`, `python_bridge/agents/agent_viewmodel.py`, `python_bridge/deployment/deployment_viewmodel.py`, `python_bridge/settings/settings_viewmodel.py`
- **Geändert:** diverse `tests/qml_*` Stubs (Port statt Service-Factory)
- **Neu:** `tests/architecture/test_qml_python_bridge_no_direct_services.py`, `tests/unit/ui_application/test_qml_port_adapters.py`
- **Neu:** dieses Dokument

### 6.2 Domänenstatus vorher / nachher

| Domäne | Vorher | Nachher |
|--------|--------|---------|
| Prompts | Service-Factory in Fassade | Port in Fassade, Default-Adapter |
| Projects | 3 Service-Imports im VM | Ein War-Room-Port |
| Workflows | `get_workflow_service` im VM | Port (+ `WorkflowNotFoundError`-Import bleibt) |
| Agents | Registry-Factory im VM | `QmlAgentRosterPort` |
| Deployment | Service-Factory im VM | `QmlDeploymentStudioPort` |
| Settings | `get_infrastructure` im VM | `QmlSettingsLedgerPort` |

### 6.3 Eingeführte Ports/Adapter

Siehe §3; Namen entsprechen den Dateien.

### 6.4 Verbliebene direkte Zugriffe / Sonderfälle

- **`workflow_viewmodel.py`:** `from app.services.workflow_service import WorkflowNotFoundError` — nur Exception-Typ, kein Service-Locator (im Architekturtest explizit erlaubt).
- **`settings_viewmodel.py`:** `_try_apply_theme()` importiert weiterhin `app.gui.themes.get_theme_manager` — GUI-seitiger Theme-Apply nach Save (bewusst nicht in den Ledger-Port gezogen, um keine GUI-Abhängigkeit in `ui_application` zu erzwingen).

### 6.5 Risiken / nächste Schritte

- **Theme nach Settings-Save:** optional kleinen `ThemeApplyPort` in `ui_application` + Adapter unter `app/gui`, um auch diesen letzten GUI-Import aus dem ViewModel zu ziehen.
- **Workflow-Exception:** `WorkflowNotFoundError` nach `app.workflows` oder `ui_contracts` verlagern, um `app.services`-Import im Bridge vollständig zu entfernen.
- **Tests:** weitere Adapter-Unit-Tests (Projects/Workflow/Deployment) analog Prompt-Stub.

---

*Chat (`ChatQmlViewModel` → `ChatPresenter` → `ChatOperationsPort`) blieb unverändert Referenz.*
