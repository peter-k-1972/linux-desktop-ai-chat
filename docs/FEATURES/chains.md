# Feature: Ketten (Chains)

Im Repository gibt es **kein** eigenes Produktpaket „chains“ im Sinne von LangChain. „Ketten“ bezeichnet hier drei **getrennte**, im Code vorhandene Abläufe.

## Inhalt

- [1. Kontext-Override-Kette (Chat)](#1-kontext-override-kette-chat)
- [2. Policy-Chain (Erklärbarkeit)](#2-policy-chain-erklärbarkeit)
- [3. Delegation-Kette (Agenten)](#3-delegation-kette-agenten)
- [4. Pipeline-Engine (Medien / generische Schritte)](#4-pipeline-engine-medien--generische-schritte)
- [5. Abgrenzung: Workflow-Editor (Operations)](#5-abgrenzung-workflow-editor-operations)

**Siehe auch**

- [Feature: Context](context.md) · [Feature: Agenten](agents.md) · [Feature: Workflows](workflows.md) · [Architektur – Datenfluss](../ARCHITECTURE.md#2-datenfluss)  
- [Handbuch-Modul Chains](../../docs_manual/modules/chains/README.md)

---

## 1. Kontext-Override-Kette (Chat)

**Zweck:** Die effektive Kontext-Konfiguration aus mehreren Quellen wählen.

**Funktionsweise:** `ChatService._resolve_context_configuration()` in `app/services/chat_service.py` definiert die feste Priorität:

1. `profile_enabled`  
2. `explicit_context_policy`  
3. `chat_default_context_policy`  
4. `project_default_context_policy`  
5. `request_context_hint`  
6. `individual_settings`

**Konfiguration:** Siehe `FEATURES/context.md`.

**Beispiel:** Profil-Modus an → Einträge aus `chat_context_profile` setzen Mode/Detail/Felder unabhängig von den manuellen Schiebern, bis eine höherpriore Policy greift.

**Typischer Fehler:** Erwarteter manueller Mode wirkt nicht, weil Policy oder Profil-Modus oben in der Kette steht.

---

## 2. Policy-Chain (Erklärbarkeit)

**Zweck:** Nachvollziehbare Auflistung, welche Regeln und Limits bei der Kontextauflösung angewandt wurden.

**Funktionsweise:** Serialisierung in `app/context/explainability/` (z. B. `policy_chain` in `context_explanation_serializer.py`); Daten kommen aus `ChatService` / `context_explain_service.py`.

**Konfiguration:** Keine Endnutzer-UI ausschließlich für die Chain; sichtbar in Debug-/QA-Kontexten.

**Typischer Fehler:** JSON-Drift in Golden Files – siehe QA-Dokus unter `docs/qa/`.

---

## 3. Delegation-Kette (Agenten)

**Zweck:** Nutzeranfrage über Planner, Task-Graph, Delegation und Execution auf Agenten zu verteilen.

**Funktionsweise:** Einstieg über `/delegate` (`app/core/commands/chat_commands.py`); Ausführung in `app/agents/` (Planner, `delegation_engine.py`, `execution_engine.py`, …).

**Beispiel:** `/delegate Erstelle eine Übersicht der Module unter app/services`.

**Typischer Fehler:** Leerer `/delegate`-Aufruf – Parser liefert nur die Verwendungsmeldung, keine Ausführung.

---

## 4. Pipeline-Engine (Medien / generische Schritte)

**Zweck:** Ausführung definierter Pipelines mit Schritt-Executors (Shell, Python, Platzhalter für weitere Medien-Backends).

**Funktionsweise:** Paket `app/pipelines/` – Engine, Registry, `PipelineDefinition`, `PipelineRun` (siehe `app/pipelines/__init__.py`).

**Konfiguration:** über Pipeline-Definitionen und Services unter `app/pipelines/services/`.

**Typischer Fehler:** Executor nicht registriert oder Schritt-Definition inkonsistent – Laufzeitfehler in der Pipeline-Engine.

---

## 5. Abgrenzung: Workflow-Editor (Operations)

**Workflow-Editor** unter **Operations → Workflows** ist ein **eigenes** Produktobjekt: gespeicherte DAG-Definitionen, `WorkflowService`, SQLite-Runs. Er nutzt u. a. die Pipeline-Engine für den Knotentyp **`tool_call`**, ist aber **nicht** identisch mit den obigen Chat-Ketten oder mit `/delegate`.

Kurzdoku: [workflows.md](workflows.md) und [Benutzerhandbuch – Workflows](../02_user_manual/workflows.md).
