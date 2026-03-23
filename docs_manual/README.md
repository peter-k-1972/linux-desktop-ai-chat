# docs_manual

Dieses Verzeichnis enthält das **strukturierte Handbuch** parallel zum freien `docs/`-Baum: Module, Rollen, Workflows und Vorlagen. Die Tabellen unten verweisen auf die Unterordner; ausführliche Architektur bleibt in [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

**Navigation:** [Dokumentations-Index (`docs/`)](../docs/README.md) · [Benutzerhandbuch](../docs/USER_GUIDE.md) · [In-App-Hilfe (Artikel)](../help/README.md) · [FEATURES](../docs/FEATURES/)

## Wurzel

| Pfad | Rolle |
|------|--------|
| [architecture.md](architecture.md) | Architektur-Anker |
| [standards.md](standards.md) | Standards-Anker |
| [modules/](modules/) | Modulbezogene Kapitel |
| [roles/](roles/) | Rollenbezogene Kapitel |
| [workflows/](workflows/) | Ablaufkapitel |
| [templates/](templates/) | Vorlagen |

Die Modul- und Rollenkapitel folgen einheitlichen README-Strukturen; Workflows sind schrittweise formuliert.

## modules/

In jedem Unterordner beschreibt **`README.md`** das Modul (Fach-, Prozess-, Interaktions-, Fehler-, Begriffs-, Perspektivsicht) anhand der Codebasis.

| Verzeichnis |
|-------------|
| [chat/](modules/chat/) |
| [context/](modules/context/) |
| [settings/](modules/settings/) |
| [providers/](modules/providers/) |
| [agents/](modules/agents/) |
| [rag/](modules/rag/) |
| [chains/](modules/chains/) |
| [prompts/](modules/prompts/) |
| [gui/](modules/gui/) |

## roles/

Pro Rolle: **`README.md`** = Rollen-Handbuch (Aufgaben, Workflows, Module, Risiken, Best Practices).

| Rolle |
|-------|
| [fachanwender](roles/fachanwender/README.md) |
| [admin](roles/admin/README.md) |
| [entwickler](roles/entwickler/README.md) |
| [business](roles/business/README.md) |

## workflows/

Endnutzer-Workflows (Schritt-für-Schritt): Ziel, Voraussetzungen, Schritte, Varianten, Fehlerfälle, Tipps.

| Workflow |
|----------|
| [chat_usage.md](workflows/chat_usage.md) |
| [context_control.md](workflows/context_control.md) |
| [agent_usage.md](workflows/agent_usage.md) |
| [settings_usage.md](workflows/settings_usage.md) |

## templates/

| Datei |
|-------|
| [module_template.md](templates/module_template.md) |
| [role_template.md](templates/role_template.md) |
| [workflow_template.md](templates/workflow_template.md) |
