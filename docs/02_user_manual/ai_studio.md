# AI Studio

Der Begriff fasst im Handbuch die **verteilten** Oberflächen zusammen, die Modellwahl, Agenten, Prompts und Wissens-RAG abdecken. Es gibt keine eigene Screen-ID „AI Studio“ in der Shell; die Funktionen liegen in **Operations** und **Control Center**.

Aus Nutzersicht ist das bewusst so gelöst: Statt eines einzigen überladenen Bildschirms finden Sie verwandte Aufgaben dort, wo sie den Arbeitsfluss am wenigsten unterbrechen — etwa Modellstatus im Control Center, laufende Konversation im Chat, wiederkehrende Textbausteine im Prompt Studio und Dokumentenkontext unter Knowledge. Für die Navigation in der Hilfe und in diesem Kapitel dient „AI Studio“ nur als **Sammelbegriff**, nicht als Menüpunkt.

## Modell

- **Control Center → Models** — Modellliste, Standardmodell, Status (`app/gui/domains/control_center/workspaces/models_workspace.py`).  
- **Settings → AI / Models** — globale Modell- und Generierungsparameter (`AIModelsCategory`).  
- **Chat-Workspace** — Modellauswahl im Eingabebereich/Kopfzeile je nach UI-Stand.

## Agenten

- **Control Center → Agents** — Verwaltung der Agentenprofile.  
- **Operations → Agent Tasks** — Aufgaben-Workspace.  
- **Chat** — Agentenwahl im Chat-Kopf, soweit die Oberfläche sie anbietet.

## Prompts

- **Operations → Prompt Studio** — `prompt_studio_workspace.py`.

## Workflows (gespeicherte DAGs)

- **Operations → Workflows** — Editor, Validierung, Test-Run, Run-Historie (`workflows`-Paket, `workflow_workspace.py`). Siehe [Workflows](workflows.md) im Handbuch; kein Sammelbegriff „AI Studio“ in der Navigation.

## RAG / Wissen

- **Operations → Knowledge** — Quellen und Index (`knowledge_workspace.py`).  
- Konfigurationsschlüssel: `help/settings/settings_rag.md` und `docs/02_user_manual/rag.md`.

## Pipelines (Code)

Ausführung definierter Schrittfolgen: Paket `app/pipelines/` (Engine, Definitionen, Executors). UI-Anbindung ist nicht Gegenstand dieser Kurzbeschreibung; siehe `docs/FEATURES/chains.md` Abschnitt Pipeline-Engine.
