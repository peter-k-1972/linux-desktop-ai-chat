# Feature: Agenten

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Konfiguration](#konfiguration)
- [Beispiel](#beispiel)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Chat](chat.md) · [Architektur – Agenten und Delegation](../ARCHITECTURE.md#23-agenten-und-delegation)  
- [Benutzerhandbuch – Delegation](../USER_GUIDE.md#55-delegation)

**Typische Nutzung**

- [Agenten (Workflow)](../../docs_manual/workflows/agent_usage.md)  
- [Hilfe: Agenten](../../help/operations/agents_overview.md) · [Control Center – Agents](../../help/control_center/control_center_agents.md)

## Zweck

Spezialisierte Rollen (Profile) für Aufgaben, Agent-Tasks und Orchestrierung – inklusive Delegation über `/delegate`.

## Funktionsweise

- **Paket:** `app/agents/` – Profile, Registry, Repository, Planner, Delegation Engine, Execution Engine, Task Runner.  
- **Services:** `app/services/agent_service.py`, Zugriff über `agents` in der Service-Infrastruktur.  
- **UI:**  
  - Operations → **Agent Tasks**  
  - Control Center → **Agents**  
- **Seed-Daten:** `app/agents/seed_agents.py` – wird vom Help-Generator (`app/help/doc_generator.py`) für die Tabelle „Agentenprofile“ genutzt.  
- **Slash-Command:** `/delegate <Prompt>` setzt `use_delegation=True` in `SlashCommandResult` (`app/core/commands/chat_commands.py`); die weitere Ausführung liegt im Chat-/Agentenpfad.

## Konfiguration

Agenten sind persistiert (Datenbank/Repository). Modellzuweisung pro Profil über Felder wie `assigned_model` / Rollen (siehe Agenten-Modelle in `app/agents/agent_profile.py`).

## Beispiel

**Beispiel** — Profil und Delegation:

1. Control Center → Agents – Profil ansehen oder bearbeiten.  
2. Im Chat `/delegate Fasse die letzten drei Commits zusammen` senden.

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| Leeres Agent-Dropdown | Repository nicht initialisiert oder DB leer – Neustart, Seed prüfen |
| Delegation reagiert nicht | Kein Text nach `/delegate`; oder Fehler im Agent-Pfad (Logs Runtime Debug) |
