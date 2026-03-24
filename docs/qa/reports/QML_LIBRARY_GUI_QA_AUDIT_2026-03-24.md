# QA-Audit: QML Library GUI (Alternative Oberfläche)

| Feld | Wert |
|------|------|
| **Projekt** | Linux Desktop Chat |
| **Audit-Datum** | 2026-03-24 |
| **Gegenstand** | Qt Quick / QML Shell unter `qml/`, Runtime `app/ui_runtime/qml/`, ViewModels `python_bridge/` + `chat_qml_viewmodel` |
| **Ziel des Laufs** | Freigabeentscheidung: *Installation als alternative GUI* |
| **Methodik** | Statische Repo-Analyse (Architektur, Struktur, Manifeste, Entrypoints); **kein** Laufzeit-Benchmark, **kein** manueller A11y-Labortest in dieser Session |

**Referenz-Governance:** `docs/04_architecture/ALTERNATIVE_GUI_THEME_RELEASE_GOVERNANCE.md` (Erwartung: Theme-Manifest mit Teilversionen, Kompatibilitätsmatrix, Registry).

---

## 1. EXECUTIVE VERDICT

### Urteil: **BLOCKED**

**Kurzbegründung:** Die QML-Shell ist strukturell vorhanden und technisch startbar (`run_qml_shell.py`, `QmlRuntime`), die Navigations- und Stage-Pipeline ist konsistent implementiert, und QML greift nicht direkt auf Python-Services zu. Für die **formale Freigabe „Installation als alternative GUI“** im Sinne des Governance-Ziels fehlen jedoch **verpflichtende** Artefakte: ein **QML-spezifisches Theme-Manifest** mit Teilversionen (Foundation, Shell, Bridge, Domains) sowie dokumentierte **Kompatibilität zu App-, Backend-, Contract- und Bridge-Versionen**; zudem fehlt die **Produktintegration** (GUI-Registry / Umschaltung / Rollback innerhalb des Hauptprogramms). Bis diese Punkte geschlossen sind, ist der Status **BLOCKED** — nicht „FAILED“ im Sinne eines kaputten Builds, sondern **Freigabe blockiert durch Release-Gates**.

---

## 2. ARCHITECTURE COMPLIANCE

| Regel | Befund | Bewertung |
|-------|--------|-----------|
| QML greift nicht direkt auf Services zu | Keine Service-Imports in `.qml`; Kontextobjekte (`chat`, `promptStudio`, …) werden in `QmlRuntime.activate` gesetzt. | **Konform** |
| Keine Businesslogik in QML | QML enthält primär Layout/Bindings; Domänenlogik liegt in Python-ViewModels/Presentern. | **Überwiegend konform** |
| Bridge trennt UI von Backend | `ShellBridgeFacade` delegiert Navigation an `ShellPresenter`; Docstring: keine Services in der Shell-Bridge. | **Konform (Shell)** |
| Stapel: Presenter → Port → Adapter → Service | **Chat:** `ChatQmlViewModel` nutzt `ChatPresenter` + `ChatOperationsPort` + `ServiceChatPortAdapter` — **Referenzimplementierung**. **Andere Domänen:** `python_bridge/*_viewmodel` und `PromptPresenterFacade` rufen überwiegend **`get_*_service()` / Fassaden** auf, **ohne** die `ui_application`-Ports. | **Teilweise Verstoß gegen Zielarchitektur** |

**Verstöße / Abweichungen (relevant für Governance):**

- **Workflows, Projects, Deployment, Settings, Prompts, Agents:** Datenpfad endet typischerweise in **Services** (oder `PromptService`), nicht durchgängig in **Ports/Adapters** wie beim Chat. Das ist **kein** direkter QML-Verstoß, widerspricht aber der vom Auftraggeber genannten Soll-Kette und erschwert **Contract-Versionierung** und **kompatibilitätsgeprüfte** Freigaben.

**Evidenz (Auszug):**

- `app/ui_runtime/qml/qml_runtime.py`: explizite Regel „No service objects on the QML context.“
- `app/ui_runtime/qml/chat/chat_qml_viewmodel.py`: Port + Presenter.
- `python_bridge/workflows/workflow_viewmodel.py`: `get_workflow_service`
- `python_bridge/prompts/prompt_presenter_facade.py`: `get_prompt_service`

---

## 3. QML STRUCTURE ANALYSIS

| Bereich | Pfad / Artefakt | Befund |
|---------|-----------------|--------|
| **Shell** | `qml/shell/` (`AppChrome`, `NavRail`, `StageHost`, `OverlayHost`) | Klare Trennung; `StageHost` lädt Stages per `Loader` aus `shell.stageUrl`. |
| **Domains** | `qml/domains/*` | Pro Hauptbühne eigener Ordner (`chat`, `projects`, `prompts`, `workflows`, `agents`, `deployment`, `settings`). |
| **Foundation** | `qml/foundation/` | Token-Schichten (Farben, Surfaces, Spacing, Typo, …). |
| **Themes** | `qml/themes/` (`LibraryTheme.qml`, `Theme.qml`, `ThemeRegistry.qml`) | Zentrale semantische Token-Zusammenführung. |
| **Bridge** | Python: `ShellBridgeFacade`, Domain-ViewModels auf Root-Context | Sichtbare Grenze Python→QML über Kontextproperties. |

**Modularisierung:** **Ja** — Importpfade nutzen Module (`themes 1.0`, `foundation/layout`) statt tiefer Cross-Domain-Vermischung.

**Domain-Trennung:** **Ja** — Navigation wird zentral über `shell_navigation_state.py` auf **eine** Stage-Datei pro Domain gemappt.

**Cross-Domain-Abhängigkeiten in QML:** In der Stichprobe **keine** fachlichen Imports zwischen Domain-Ordnern gefunden; Stages sind über Shell-Loader entkoppelt.

**Hinweis:** Unter `qml/domains/` existieren zusätzliche **Placeholder-Dateien** (`prompt_studio/`, `agent_tasks/`, `deployment/…Placeholder`) — sie sind für die **aktive** Navigation laut `shell_navigation_state.py` **nicht** die geladenen Stages (z. B. `prompt_studio` → `domains/prompts/PromptStage.qml`). Das ist **kein** Laufzeitfehler, aber **Wartungs-/Review-Risiko** (doppelte Metapher „Prompt Studio“ vs. `prompts/`).

---

## 4. BRIDGE / PRESENTER BOUNDARY

| Prüfpunkt | Befund |
|-----------|--------|
| Bridge ruft Presenter (Shell) | **Ja** — `ShellBridgeFacade.requestDomainChange` → `ShellPresenter.navigate_to`. |
| Keine Backendlogik in QML | **Ja** (QML-seitig). |
| Keine Datenbankzugriffe aus QML | **Ja** — keine SQL/QML-Schicht. |
| Keine Services direkt „im Theme“ (QML) | **Ja**. |
| Domain-Bridge-Objekte | ViewModels in Python; **teilweise** Service-Zugriff **in** Python ohne Port (siehe §2). |

**Fazit:** Die **UI-Grenze** (QML vs. Python) ist sauber. Die **Architekturgrenze** Presenter/Port vs. Service ist **nur im Chat** vorbildlich; andere Domänen sind als **technische Schulden** gegenüber dem Soll-Stack zu dokumentieren, nicht als QML-Blocker.

---

## 5. DOMAIN STAGE STATUS

Quelle der Stage-Zuordnung: `app/ui_runtime/qml/shell_navigation_state.py` (`_STAGE_QML_PATH`).

| Domäne (Nav-ID) | Stage-QML | Status | Anmerkung |
|-----------------|-----------|--------|------------|
| **Chat** | `domains/chat/ChatStage.qml` | **implemented** | Port-basierter Pfad; Streaming/Sessions über `ChatQmlViewModel`. |
| **Projects** | `domains/projects/ProjectStage.qml` | **implemented** | `ProjectWorkspace` / Listen / Inspector; Service-Zugriff im ViewModel. |
| **Workflows** | `domains/workflows/WorkflowStage.qml` | **implemented** | Liste, Canvas, Inspector, Run-Historie; komplexe Logik im `workflow_viewmodel`. |
| **Prompts** (Nav: `prompt_studio`) | `domains/prompts/PromptStage.qml` | **implemented** | Vollständige Studio-Metapher (Regal, Katalog, Lesepult); Anbindung über `promptStudio`. |
| **Agents** (Nav: `agent_tasks`) | `domains/agents/AgentStage.qml` | **implemented** | Roster / Tasks / Inspector; ViewModel ohne Port-Schicht. |
| **Deployment** | `domains/deployment/DeploymentStage.qml` | **implemented** | Anbindung `deploymentStudio` + `deployment_operations_service`. |
| **Settings** | `domains/settings/SettingsStage.qml` | **implemented** | Ledger/Katalog; `AppSettings`-basiert. |

**Hinweis „partial“:** Einzelne UX- oder Fachtiefe-Aspekte wurden **nicht** end-to-end gegen Produkt-SLA geprüft (nur Code-Stand). Für Freigabe wäre ein **manueller** Domain-Matrix-Test erforderlich.

---

## 6. FOUNDATION / THEME CONSISTENCY

| Prüfpunkt | Befund |
|-----------|--------|
| Theme-Tokens existieren | **Ja** — `LibraryTheme.qml` bündelt Foundation-Module (`SemanticColors`, `SemanticSurfaces`, …). |
| Keine hart codierten `#RRGGBB` in QML | Stichprobe: **keine** `color: '#…'`; Akzenttransparenz über `Qt.rgba(Theme.accentPrimary.r, …)` in mehreren Komponenten. |
| Spacing / Typography | Über `Theme.spacing`, `Theme.typography` etc. |
| Surface-Rollen | Verwendung von `Theme.surfaces.*`, `Theme.surfaceWork`, `Theme.colors.*` in Stichproben (`ChatReadingTable`, `NavRail`, Stages). |

**Bewertung:** **Konsistent** im Sinne einer Design-Token-Schicht; vollständiger visueller Audit (alle 68 QML-Dateien) wurde **nicht** zeilenweise durchgeführt.

---

## 7. NAVIGATION / ROUTING ANALYSIS

| Prüfpunkt | Befund |
|-----------|--------|
| Navigation Rail | `NavRail.qml` bindet `shellBridge.domainNavModel`; Klick → `requestDomainChange`. |
| StageHost | `Loader.source` = `shellBridge.stageUrl`; Synchronität mit `activeDomain` in Delegates. |
| Domänenwechsel | `ShellPresenter` validiert Domain-ID, löst Pfad via `stage_relative_path`, setzt Zustand über `apply_shell_state`. |
| Routing-Chaos | **Kein** paralleler zweiter Router in QML erkennbar; **eine** Wahrheit über Python-State + QUrl. |

**Risiko:** `StageHost` nutzt `asynchronous: false` — große Stages können den UI-Thread beim Wechsel blockieren (siehe §8).

---

## 8. PERFORMANCE RISK CHECK

| Risiko | Befund | Schwere |
|--------|--------|---------|
| Binding-Loops | **Nicht** systematisch per Profiler nachgewiesen; statisch keine offensichtlichen Selbstreferenz-Bindings in Stichproben. | **Unbekannt / nachverfolgen** |
| Heavy Repaints | Workflow-Canvas (`WorkflowCanvas`/`WorkflowGraph`) kann bei vielen Knoten teuer werden. | **Medium** |
| ListViews | Viele `ListView`-Nutzer (Chat, Projekte, Prompts, Deployment, …). Qt listet typischerweise nur sichtbare Delegates — für **sehr große** Chat-Historien dennoch Lasttests empfohlen. | **Medium** (Chat-Langläufer) |
| Stage-Loader | `asynchronous: false` in `StageHost.qml` | **Medium** |
| Animationen | `MotionTokens` vorhanden; keine globale Überprüfung auf übermäßige Parallel-Animationen. | **Low** |

**Empfehlung für Freigabe:** Profiler-Lauf (Qt Quick Profiler) auf **Chat** (lange Sessions) und **Workflows** (große Graphen).

---

## 9. UX / USABILITY CHECK

| Prüfpunkt | Befund (Code-/Strukturreview) |
|-----------|-------------------------------|
| Navigation logisch | Reihenfolge und Labels entsprechen der Architekturkarte (`shell_navigation_state.py`); Einstieg **Chat**. |
| Fokus sichtbar | Rail nutzt `Theme.states.focusRing` für Auswahlzustände; **vollständige** Tastaturbedienung **nicht** verifiziert. |
| Kontrast | Token-basiert; **kein** Messprotokoll (Kontrastmeter) in diesem Audit. |
| „Dashboard-Hölle“ | Bibliotheksmetapher mit klar getrennten Stages — **strukturell** plausibel. |
| Bibliotheksmetapher | Mit `QML_GUI_VISUAL_ARCHITECTURE_MAP.md` konsistent (Chat / Projects / Workflows / …). |

**Bewertung:** **Konzeptionell stimmig**; **operativ** für Freigabe sind manuelle UX- und A11y-Tests erforderlich.

---

## 10. VERSIONING & COMPATIBILITY CHECK

| Anforderung | Befund | Gate |
|-------------|--------|------|
| Theme-Version (gesamt) für QML Library GUI | Es existiert **kein** separates Manifest unter `qml/` mit `theme_version` gemäß Governance; `run_qml_shell.py` lädt **`app/ui_themes/builtins/light_default/manifest.json`**. | **BLOCKER** |
| Teilversionen (Foundation, Shell, Bridge, Domains) | **Nicht** im Repo als Manifest-Felder für die QML-Lieferung abgebildet. | **BLOCKER** |
| Kompatible App-Version dokumentiert | `min_app_compat` im genutzten Manifest ist **`0.0.0`** — keine belastbare Aussage. | **BLOCKER** |
| Kompatible Backend-Version dokumentiert | **Fehlt** im Manifest. | **BLOCKER** |
| Kompatible Contract-/Port-Version dokumentiert | **Fehlt** (bestehendes Schema `manifest_models.py` kennt `min_app_compat`, kein `compatible_contract_versions`). | **BLOCKER** |
| Bridge-Version / Schnittstellenversion | **Nicht** explizit versioniert und gegen App-Release gebunden. | **BLOCKER** |

**Hinweis:** Das vorhandene `ThemeManifest` (`app/ui_runtime/manifest_models.py`) ist auf **Widget-Runtime + Packs** ausgelegt (`runtime.primary`: `pyside6_widgets`); `secondary` kann `qt_quick` enthalten, erfüllt aber **nicht** die geforderte **QML-Theme-Release- und Kompatibilitätsprotokollierung**.

**Abgleich Governance-Dokument:** Die dort definierten Pflichtfelder (`foundation_version`, `shell_version`, `bridge_version`, `domain_versions`, `compatible_contract_versions`, …) sind für die **QML Library GUI** aktuell **nicht operationalisiert**.

---

## 11. INSTALLABILITY AS ALTERNATIVE GUI

| Prüfpunkt | Befund |
|-----------|--------|
| Parallel zur Standard-GUI | Separater Entrypoint **`run_qml_shell.py`**; setzt standardmäßig `LINUX_DESKTOP_CHAT_SINGLE_INSTANCE=0` — erleichtert parallelen Betrieb **prozessseitig**. |
| Hauptprogramm `run_gui_shell.py` | **Keine** QML-/Registry-Integration gefunden — Standard-GUI bleibt eigenständiger Pfad. |
| Aktivierung durch Nutzer im gleichen Produkt | **Fehlt** (kein documented GUI-Registry-Schalter / kein Theme-Id für „QML Shell“ im Hauptfenster). |
| Rollback auf Standard-GUI | Im **selben Prozess** nicht gegeben, da alternative GUI ein **anderer Startpfad** ist; Rollback = Standard-Entrypoint starten. |

**Bewertung:** **Technisch parallel startbar**, aber **nicht** „installiert als alternative GUI“ im Sinne einer **produktintegrierten, umschaltbaren** Oberfläche mit Registry und Fail-Closed-Kompatibilitätsprüfung.

---

## 12. BLOCKER LIST

| ID | Beschreibung | Betroffene Komponente | Empfohlene Lösung |
|----|--------------|------------------------|-------------------|
| **B-01** | Kein QML-/Theme-Release-Manifest mit Gesamt- und Teilversionen (Foundation, Shell, Bridge, Domains). | `qml/`, Release-Artefakte, ggf. neues Manifest neben QML-Root | Manifest einführen und in CI validieren; Versionen bumpen nach Governance. |
| **B-02** | Keine dokumentierte Kompatibilität zu **UI-Contracts/Ports** und **Backend**; `min_app_compat` am genutzten Manifest ist trivial (`0.0.0`). | `app/ui_themes/.../manifest.json` (aktuell falscher Kontext), `manifest_models.py` | Schema erweitern oder separates `qml_theme_manifest.json`; Kompatibilitätsmatrix pflegen. |
| **B-03** | Keine **gegenseitige** Registrierung: App-Registry listet zulässige QML-Themes / Bridge-Interface-Version nicht. | `run_gui_shell.py` / zukünftige Registry | GUI-Registry implementieren (Konzept §8 Governance). |
| **B-04** | **Produkt-Freigabe „Installation als alternative GUI“** nicht erfüllt: fehlende Umschaltung und definierter Rollback **im Hauptprogramm**. | Produkt-Bootstrap | Settings- oder CLI-Flag + sicherer Fallback auf Widget-GUI. |

---

## 13. REQUIRED REMEDIATIONS

| Priorität | Maßnahme | Bezug |
|-----------|----------|--------|
| **Critical** | QML-Theme-Manifest + validierte Felder für Versionen und Kompatibilität (App, Backend, Contracts, Bridge). | §10, B-01–B-02 |
| **Critical** | GUI-Registry + Runtime-Check vor Aktivierung der QML-GUI. | §11, B-03 |
| **Critical** | Integrierter Schalter + Rollback-Pfad zur Standard-GUI (ein Produktbinary oder klar dokumentierte gleichwertige Installationsvariante). | §11, B-04 |
| **High** | Domain-ViewModels schrittweise auf **Ports + Adapter** alignen (Vorbild Chat), um Contract-Versionierung durchsetzbar zu machen. | §2, §4 |
| **Medium** | Performance-Profiling (Chat-Langläufer, Workflow-Graph, Stage-Wechsel); ggf. `Loader.asynchronous: true` evaluieren. | §8 |
| **Medium** | Manuelle UX/A11y-Gates laut Governance ausführen und im QA-Bericht referenzieren. | §5, §9 |
| **Low** | Placeholder-Dateien unter `qml/domains/` bereinigen oder klar als „nicht routend“ kennzeichnen, um Verwechslung zu vermeiden. | §3 |

---

## 14. QA DECISION

### Entscheidung: **BLOCKED**

**Begründung:** Die QML Library GUI erfüllt **wesentliche** architektonische Mindestanforderungen auf der **QML↔Python-Grenze** und weist eine **saubere Shell-/Domain-Struktur** auf. Die für diese Freigabestufe geforderten **Versions- und Kompatibilitätsnachweise** sowie die **produktseitige Installierbarkeit als alternative GUI** (Registry, Umschaltung, Rollback im Hauptprogramm) sind **nicht** erbracht. Entsprechend ist die Freigabe **BLOCKED**, bis die Blocker **B-01–B-04** und die Critical-Remediation umgesetzt und erneut belegt sind.

### Nachgelagerter möglicher Status (ohne erneutes Audit in diesem Dokument)

- Nach Schließung der **Critical**-Punkte, bei verbleibenden dokumentierten Findings: **ACCEPTED WITH FINDINGS**.
- Nach vollständiger Matrix + UX/A11y + Performance-Nachweis: **READY FOR INSTALLATION AS ALTERNATIVE GUI**.

---

*Ende des Berichts.*
