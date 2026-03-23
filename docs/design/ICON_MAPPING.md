# Icon Mapping (Soll)

Zuordnung **UI-Kontext → Registry-ID** (`IconManager.get` / `get_icon`).

## Hauptnavigation (`NavArea`)

| UI-Element | Registry-ID |
|------------|-------------|
| Kommandozentrale | `dashboard` |
| Operations | `chat` |
| Control Center | `control` |
| QA & Governance | `shield` |
| Runtime / Debug | `activity` |
| Settings | `gear` |

## Control Center Workspaces

| Workspace | Registry-ID |
|-----------|-------------|
| Models | `models` |
| Providers | `providers` |
| Agents | `agents` |
| Tools | `tools` |
| Data Stores | `data_stores` |

## Operations Workspaces

| Workspace | Registry-ID |
|-----------|-------------|
| Projects | `projects` |
| Chat | `chat` |
| Agent Tasks | `agents` |
| Knowledge | `knowledge` |
| Prompt Studio | `prompt_studio` |
| Workflows | `system_graph` |
| Deployment | `deploy` |
| Audit / Incidents | `incidents` |

## QA & Governance

| Workspace | Registry-ID |
|-----------|-------------|
| Test Inventory | `test_inventory` |
| Coverage Map | `coverage_map` |
| Gap Analysis | `gap_analysis` |
| Incidents | `incidents` |
| Replay Lab | `replay_lab` |

## Runtime / Debug

| Workspace | Registry-ID |
|-----------|-------------|
| Introspection | `system` |
| QA Cockpit / Observability | `qa_runtime` *(getrennt von Governance `shield`)* |
| Event Bus | `eventbus` |
| Logs | `logs` |
| Metrics | `metrics` |
| LLM Calls | `llm_calls` |
| Agent Activity | `agent_activity` |
| System Graph | `system_graph` |
| Markdown Demo | `sparkles` |
| Theme Visualizer | `appearance` |

## Settings

| Workspace | Registry-ID |
|-----------|-------------|
| Appearance | `appearance` |
| System | `system` |
| Models | `models` |
| Agents | `agents` |
| Advanced | `advanced` |

## Objekttypen (`get_icon_for_object`)

| type (String) | Registry-ID |
|---------------|-------------|
| agent, agents | `agents` |
| model, models | `models` |
| provider, providers | `providers` |
| tool, tools | `tools` |
| dataset, data_store, data_stores | `data_stores` |
| knowledge, collection | `knowledge` |
| prompt, prompt_studio | `prompt_studio` |
| project, projects | `projects` |
| workflow, workflows | `system_graph` |
| deployment, deploy | `deploy` |
| incident, incidents | `incidents` |
| test | `test_inventory` |
| coverage | `coverage_map` |
| gap | `gap_analysis` |
| replay | `replay_lab` |
| llm | `llm_calls` |
| metric | `metrics` |
| log | `logs` |
| event | `eventbus` |
| *default* | `projects` |

## Aktionen (`get_icon_for_action`)

| action | Registry-ID |
|--------|-------------|
| create, add, new | `add` |
| pin | `pin` |
| delete, remove | `remove` |
| edit, rename | `edit` |
| save | `save` |
| refresh, reload | `refresh` |
| search, find | `search` |
| open | `open` |
| link_out, external_link, open_external | `link_out` |
| filter | `filter` |
| run, execute, play | `run` |
| stop, cancel | `stop` |
| deploy, publish | `deploy` |
| help | `help` |
| send | `send` |

---

*Code:* `app/gui/icons/nav_mapping.py`, `app/gui/commands/bootstrap.py`, `palette_loader.py`, `icon_registry.py`.
