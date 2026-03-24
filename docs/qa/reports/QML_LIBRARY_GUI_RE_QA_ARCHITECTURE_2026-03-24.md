# Re-QA: QML Library GUI — Architektur nach Phase 3 (Port-/Adapter-Angleichung)

| Feld | Wert |
|------|------|
| **Projekt** | Linux Desktop Chat |
| **Berichtsdatum** | 2026-03-24 |
| **Gegenstand** | Erfolg der **Phase 3** (Ports/Adapter für QML-Domänen); Abgleich mit **erstem Audit** [`QML_LIBRARY_GUI_QA_AUDIT_2026-03-24.md`](QML_LIBRARY_GUI_QA_AUDIT_2026-03-24.md) |
| **Methodik** | Statische Code-Analyse (`python_bridge/`, `app/ui_application/ports|adapters`, `app/ui_runtime/qml/`); Abgleich mit Architekturdokument [`QML_VIEWMODEL_PORT_ALIGNMENT_2026-03-24.md`](../04_architecture/QML_VIEWMODEL_PORT_ALIGNMENT_2026-03-24.md); **kein** erneuter Laufzeit-/A11y-Labortest |

---

## 1. EXECUTIVE VERDICT

### Urteil: **ARCHITECTURE ISSUE CLOSED** *(für den Gegenstand Phase 3)*

**Begründung:** Die im ersten Audit zentrale **Architekturbeanstandung** — Nicht-Chat-QML-Domänen endeten in Python überwiegend auf **Service-Locator-/Service-Fassaden** statt auf dem Zielpfad **Port → Adapter → Service** — ist **substanziell behoben**. Die betroffenen ViewModels unter `python_bridge/` importieren **keine** `app.services.*`-Module mehr (eine dokumentierte Ausnahme: reiner **Exception-Import** im Workflow-ViewModel). Pro Domäne existieren **schmale QML-Ports** und **Service-Adapter**; die frühere pauschale Abweichung von der Chat-Referenz ist damit **fachlich geschlossen**.

**Abgrenzung:** Dieses Urteil betrifft **die Architekturangleichung Phase 3**, nicht die **Gesamtfreigabe** der alternativen GUI (siehe §10).

---

## 2. DELTA TO PREVIOUS AUDIT

| Thema | Erstes Audit (Stand) | Nach Phase 3 |
|--------|----------------------|--------------|
| **Presenter/Port-Pfad Nicht-Chat** | „Teilweise Verstoß“: Workflows, Projects, Deployment, Settings, Prompts, Agents über `get_*_service()` / Facade ohne `ui_application`-Ports | **Behoben:** dedizierte `qml_*_port.py` + `service_qml_*_adapter.py`; ViewModels hängen an **Port-Injection** (Default-Adapter) |
| **Evidenz Service in ViewModels** | z. B. `workflow_viewmodel`: `get_workflow_service`; `prompt_presenter_facade`: `get_prompt_service` | **Entfernt** aus ViewModels/Facade-Default-Pfad zugunsten Adapter |
| **Chat-Referenz** | unverändert sauber | **unverändert** (Regression nicht erkennbar aus Analyse) |
| **Shell-Bridge** | bereits „keine Services“ | **unverändert** (`ShellBridgeFacade` → `ShellPresenter`) |
| **QML↔Python-Kontext** | keine Service-Objekte auf QML-Context | **unverändert** (`QmlRuntime`-Regel) |
| **Governance (Manifest, Matrix, Registry, Switch)** | **BLOCKER** B-01–B04 | **Außerhalb Phase 3**; Status unverändert **relevant für Gesamtfreigabe**, nicht für „ist Port-Refactoring gelungen?“ |
| **Neu / geändert** | — | **Klein:** `WorkflowNotFoundError` weiter aus `app.services.workflow_service` importiert; Settings-VM ruft **`get_theme_manager()`** nach Save auf (GUI-Kopplung im ViewModel) |

**Fazit Delta:** Der **Architektur-Hinweis** aus §2/§4 des ersten Audits ist **nicht mehr in der gleichen Schärfe gültig**; verbleibende Punkte sind **Randcoupling** und **Governance**, nicht die fehlende Port-Schicht in sechs Domänen.

---

## 3. DOMAIN-BY-DOMAIN ARCHITECTURE STATUS

Legende: **clean** = entspricht Zielpfad; **mostly_clean** = kleine dokumentierte Ausnahme; **partial** = Lücken im Soll; **direct_service_dependency** = ViewModel importiert/ruft Service direkt; **unclear** = nicht nachvollziehbar.

| Domäne | ViewModel / Bridge | Presenter / Fassade | Port | Adapter | Servicezugriff | Gesamt |
|--------|-------------------|---------------------|------|---------|----------------|--------|
| **Chat** | `ChatQmlViewModel` + Port-Bindings | `ChatPresenter` | `ChatOperationsPort` | `ServiceChatPortAdapter` | nur im Adapter | **clean** (Referenz) |
| **Prompts** | `PromptViewModel` | `PromptPresenterFacade` | `QmlPromptShelfOperationsPort` | `ServiceQmlPromptShelfAdapter` | nur im Adapter | **clean** |
| **Projects** | `ProjectViewModel` | — (Port direkt) | `QmlProjectWarRoomPort` | `ServiceQmlProjectWarRoomAdapter` (Project + Workflow + Agent) | nur im Adapter | **mostly_clean** *(ein Port bündelt mehrere Services — bewusst, nicht 1:1-Service-Spiegel pro Datei)* |
| **Workflows** | `WorkflowStudioViewModel` | — | `QmlWorkflowCanvasPort` | `ServiceQmlWorkflowCanvasAdapter` | Adapter + **Exception-Typ** aus `workflow_service` im VM | **mostly_clean** |
| **Agents** | `AgentViewModel` | — | `QmlAgentRosterPort` | `ServiceQmlAgentRosterAdapter` | nur im Adapter (Registry) | **clean** |
| **Deployment** | `DeploymentViewModel` | — | `QmlDeploymentStudioPort` | `ServiceQmlDeploymentStudioAdapter` | nur im Adapter | **clean** |
| **Settings** | `SettingsViewModel` | — | `QmlSettingsLedgerPort` | `ServiceQmlSettingsLedgerAdapter` | Adapter + **`get_theme_manager()`** im VM nach Save | **mostly_clean** |

---

## 4. DIRECT SERVICE ACCESS CHECK

| Prüfung | Ergebnis |
|---------|----------|
| Importieren QML-ViewModels (`python_bridge/*_viewmodel.py`) direkt `app.services.*`? | **Nein** — `rg` über `python_bridge`: **kein** `from app.services` außer **`workflow_viewmodel.py` → `WorkflowNotFoundError`** (kein Locator, kein Serviceaufruf). |
| Nutzen Fassaden Service-Locator statt Ports? | **`PromptPresenterFacade`:** nein — nutzt **`QmlPromptShelfOperationsPort`** (Default-Adapter). |
| Liegen direkte Service-/Registry-Zugriffe nur in Adaptern? | **Ja** für die neuen QML-Adapter (`get_prompt_service`, `get_project_service`, `get_workflow_service`, `get_agent_registry`, `get_deployment_operations_service`, `get_infrastructure` nur in **`ServiceQmlSettingsLedgerAdapter`**). |

**Verbleibende explizite Nicht-Adapter-Serviceberührung in der Bridge-Schicht:**

| Ort | Art | Bewertung |
|-----|-----|-----------|
| `python_bridge/workflows/workflow_viewmodel.py` | `from app.services.workflow_service import WorkflowNotFoundError` | Technische Schichtenverletzung minimal; **kein** Serviceaufruf. |
| `python_bridge/settings/settings_viewmodel.py` | `_try_apply_theme()` → `from app.gui.themes import get_theme_manager` | **GUI-/Theme-Seiteneffekt im ViewModel**; Architektur-Restpunkt (siehe §9). |

**Hinweis:** `prompt_viewmodel` importiert **`app.prompts.prompt_models.Prompt`** in `createPrompt` — **Domänen-DTO**, kein Service; für Contract-Strenge akzeptabel, aber **kein** Port-DTO.

---

## 5. PORT / ADAPTER COVERAGE

**Vorhandene QML-Ports** (unter `app/ui_application/ports/qml_*.py`):

- `qml_prompt_shelf_port.py`
- `qml_project_war_room_port.py`
- `qml_workflow_canvas_port.py`
- `qml_agent_roster_port.py`
- `qml_deployment_studio_port.py`
- `qml_settings_ledger_port.py`

**Adapter** spiegeln jeweils die **tatsächlich vom ViewModel genutzten** Operationen (Listen, CRUD, Run, Rollout, Settings-Zugriff) — **keine** vollständige 1:1-Abbildung der jeweiligen Service-Oberfläche.

| Qualitätskriterium | Bewertung |
|--------------------|-----------|
| Schmal & UI-orientiert | **Erfüllt** — Methoden folgen ViewModel-Bedarf |
| Kapselung | **Erfüllt** — Services nur in Adaptern |
| Over-Engineering | **Gering** — ein zusammengefasster **War-Room-Port** für Projects vermeidet drei separate VM-Ports ohne neue Fachlogik |

---

## 6. PRESENTER / FACADE BOUNDARY CHECK

| Aspekt | Befund |
|--------|--------|
| ViewModels vs. Presenter | **Chat:** klassischer Presenter. **Andere:** überwiegend **ViewModel → Port** ohne separaten Presenter — **zulässig**, da Ziel „Port vor Service“ war, nicht „überall ein zweiter Presenter“. |
| **PromptPresenterFacade** | **Schlank:** Filter/Listenhilfen + Delegation an Port; **kein** QML-Typ; sinnvolle Zwischenlage zwischen VM und Port. |
| Logikverlagerung | **Keine** große Verschiebung von Fachlogik in QML; Workflow-Graph-Logik bleibt im ViewModel (wie zuvor) — **kein** neuer Architekturfehler, aber **weiterhin komplex** im VM. |
| Workaround? | Ports sind **keine** reinen Umbenennungen: Adapter kapseln echte Service-Aufrufe; **kein** „Fake-Port“ erkennbar. |

---

## 7. QML BRIDGE PURITY CHECK

| Prüfpunkt | Befund |
|------------|--------|
| Python direkt unter QML (Context-Objekte) frei von Serviceaufrufen? | **Ja** — domain ViewModels rufen **Ports** auf; keine `get_*_service()` in diesen Modulen (außer Exception-Import Workflow). |
| Neue Businesslogik in Bridge? | **Nein** — Refactoring ist **Verdrahtungsänderung**, keine neuen Fachregeln. |
| Property/Signal/Slot-Orientierung | **Erhalten** |
| **Shell** (`ShellBridgeFacade`) | **Unverändert** dokumentiert: keine Services, keine Domänenlogik; **Presenter** für Routing |

---

## 8. REGRESSION RISK CHECK

| Risiko | Einschätzung |
|--------|----------------|
| Chat beschädigt? | **Niedrig** — Chat-Pfad nicht Teil der Phase-3-Änderungen (Referenz unangetastet). |
| Domänen laden noch? | **Niedrig bis moderat** — bestehende QML-Smokes/Tests wurden in Phase 3 angepasst; statisch konsistent; **kein** Voll-E2E in diesem Re-QA. |
| Neue enge Kopplungen? | **Port-Typen** in ViewModels erhöhen Abhängigkeit zu `ui_application` — **beabsichtigt** und **stabiler** als direkte Service-Imports. |
| Zu viele Ports? | **Sechs** QML-Ports — **vertretbar**; Projects-Port bündelt absichtlich mehrere Backend-Fassaden. |

---

## 9. REMAINING ARCHITECTURE FINDINGS

| ID | Finding | Priorität |
|----|---------|-----------|
| **F-01** | `WorkflowNotFoundError` wird aus `app.services.workflow_service` im ViewModel importiert — **Schichtennagel**; sauberer wäre Exception an **Workflow-Domain** oder **Port-Vertrag** (z. B. eigene `WorkflowNotFoundError` in `app.workflows` / `ui_application`). | **Low** |
| **F-02** | `SettingsViewModel._try_apply_theme()` ruft **`get_theme_manager()`** direkt auf — **GUI-Service im QML-ViewModel**; widerspricht dem strengsten „nur Port“-Ideal. Abhilfe: kleiner **ThemeApplyPort** + GUI-Adapter (siehe Alignments-Dokument). | **Medium** |
| **F-03** | **Projects:** Ein Port deckt Project-, Workflow- und Agent-Zugriff für die War-Room-UI ab — **fachlich kohärent**, aber **höhere Adapter-Komplexität**; bei Wachstum ggf. in mehrere Ports splitten. | **Low** |

**Keine Critical/High-Architekturblocker** aus den obigen Punkten für „Ports statt Services in ViewModels“.

---

## 10. UPDATED RELEASE IMPACT

| Frage | Antwort |
|-------|---------|
| Wurde der **frühere Architekturhinweis** (Nicht-Chat ohne Port-Pfad) **substanziell reduziert?** | **Ja.** |
| Ist dieser Bereich noch **Release-Blocker** für „alternative GUI architektonisch akzeptabel“? | **Nein** — im Sinne des **ersten Audits §2/§4** ist die Beanstandung **nicht mehr blockierend**. |
| Verbleiben **primär Governance-Themen** (Phase 2)? | **Ja** — Manifest/Matrix/Registry/Switching bestimmen weiterhin die **formale Installationsfreigabe** laut erstem Audit (**BLOCKED** dort). |
| Gibt es **weitere Architektur-Blocker**? | **Nein** aus Sicht Phase 3; verbleibende Findings sind **Nachschärfungen** (§9). |

**Kurz:** **Architekturpfad für QML-Kerndomänen** ist für die Freigabeschiene **ausreichend**; **Produkt-/Governance-Freigabe** kann weiterhin **BLOCKED** sein, **ohne** Widerspruch zu diesem Re-QA.

---

## 11. QA DECISION

### Entscheidung: **ACCEPTED WITH FINDINGS**

**Begründung:**

- **Phase 3 (Port-/Adapter-Angleichung):** **erfolgreich** — die im ersten Audit benannte **Lücke zwischen Chat-Referenz und übrigen QML-Domänen** ist **geschlossen** im Sinne von: *ViewModels → Port → Adapter → Service*.
- **Findings:** **F-01–F-03** (§9) — **kein** Architektur-Blocker für „weiter in Richtung Release“, aber **nachverfolgbare** Restschärfe.
- **Gesamtbild Freigabe „Installation als alternative GUI“:** weiterhin abhängig von **Governance/Produktintegration** (erstes Audit **BLOCKED**); dieses Re-QA **hebt** diesen Status **nicht** auf, bewertet aber: **Architektur ist nicht mehr der Hauptgrund für Ablehnung.**

**Wenn nur die Architekturfrage „Phase 3 erfüllt?“ entschieden werden soll:** vereinfacht **ARCHITECTURE ISSUE CLOSED** (synonym zu §1).

---

*Ende des Re-QA-Berichts.*
