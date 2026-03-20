# App Model Cluster Dependency Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Analyse – keine physischen Moves  
**Referenz:** APP_MOVE_MATRIX.md, APP_TARGET_PACKAGE_ARCHITECTURE.md

---

## 1. Executive Summary

Der Model-Cluster besteht aus fünf Root-Dateien:

| Datei | Zeilen | Zweck |
|-------|--------|-------|
| `app/model_orchestrator.py` | ~220 | Modell-Orchestrierung, Provider-Zuordnung, Chat-Aufrufe |
| `app/model_registry.py` | ~300 | Modell-Registry, Metadaten, Rollen-Mapping |
| `app/model_roles.py` | ~70 | ModelRole-Enum, Default-Mapping, Display-Namen |
| `app/model_router.py` | ~150 | Heuristik-basierte Rollenwahl aus Prompt |
| `app/escalation_manager.py` | ~75 | Eskalationslogik zwischen Modellen |

**Fazit:** Der Cluster hat **keine GUI-Abhängigkeiten**. Er wird von GUI, Services, Agents und Legacy importiert. Ein Move nach `app/core/models/` ist **möglich**, sofern die Provider-Abhängigkeit akzeptiert wird (providers ist kein GUI-Package).

**Empfehlung:** Cluster als Ganzes nach `app/core/models/` verschieben. Keine Zerlegung nötig. Vorbedingung: Import-Pfade in ~20 Dateien aktualisieren.

---

## 2. Datei pro Datei

### 2.1 app/model_roles.py

| Aspekt | Befund |
|--------|--------|
| **Imports** | Keine app-Imports (nur stdlib: enum, typing) |
| **GUI** | Keine |
| **Services** | Keine |
| **Provider** | Keine |
| **Legacy-Root** | Keine |

**Exporte:** `ModelRole`, `DEFAULT_ROLE_MODEL_MAP`, `ROLE_DISPLAY_NAMES`, `get_role_display_name`, `get_default_model_for_role`, `all_roles`

**Bewertung:** Reines Datenmodul. Ideal für core.

---

### 2.2 app/model_router.py

| Aspekt | Befund |
|--------|--------|
| **Imports** | `app.model_roles` (ModelRole) |
| **GUI** | Keine |
| **Services** | Keine |
| **Provider** | Keine |

**Exporte:** `route_prompt`, `CODE_KEYWORDS`, `THINK_KEYWORDS`, …

**Bewertung:** Reine Heuristik-Logik. Nur model_roles. Ideal für core.

---

### 2.3 app/model_registry.py

| Aspekt | Befund |
|--------|--------|
| **Imports** | `app.model_roles` (ModelRole) |
| **GUI** | Keine |
| **Services** | Keine |
| **Provider** | Keine |

**Exporte:** `ModelEntry`, `ModelRegistry`, `get_registry`

**Bewertung:** Reine Daten/Registry-Logik. Ideal für core.

---

### 2.4 app/escalation_manager.py

| Aspekt | Befund |
|--------|--------|
| **Imports** | `app.model_roles`, `app.model_registry` |
| **GUI** | Keine |
| **Services** | Keine |
| **Provider** | Keine |

**Exporte:** `get_next_escalation_role`, `get_escalation_model`, `LOCAL_ESCALATION_MAP`, `CLOUD_ESCALATION_MAP`

**Bewertung:** Reine Eskalationslogik. Ideal für core.

---

### 2.5 app/model_orchestrator.py

| Aspekt | Befund |
|--------|--------|
| **Imports** | `app.model_roles`, `app.model_registry`, `app.model_router`, `app.escalation_manager`, `app.providers` |
| **GUI** | Keine |
| **Services** | Keine |
| **Provider** | `LocalOllamaProvider`, `CloudOllamaProvider`, `BaseChatProvider` |

**Exporte:** `ModelOrchestrator`

**Bewertung:** Abhängigkeit von `app.providers` – erlaubt laut Zielarchitektur: core darf providers nicht importieren, aber **model_orchestrator** liegt aktuell im Root. Nach Move: `app.core.models` importiert `app.providers`. Laut APP_TARGET_PACKAGE_ARCHITECTURE: core darf nur utils importieren. **Konflikt.**

**Lösung:** Entweder (a) providers als erlaubte core-Abhängigkeit für models definieren, oder (b) ModelOrchestrator in `app/services/` belassen und nur model_roles, model_registry, model_router, escalation_manager nach core/models verschieben. Option (b) zerreißt den Cluster. Option (a) erfordert Architektur-Anpassung: „core/models darf providers importieren (für Orchestrierung)“.

**Empfehlung:** Architektur-Regel erweitern: `core/models` darf `providers` importieren (Orchestrierung ist Kernlogik, Provider sind Infrastruktur).

---

## 3. Interne Abhängigkeiten

```
model_roles (Blatt)
    ↑
model_router ──→ model_roles
model_registry ──→ model_roles
escalation_manager ──→ model_roles, model_registry
model_orchestrator ──→ model_roles, model_registry, model_router, escalation_manager, providers
```

**Zirkuläre Abhängigkeiten:** Keine.

**Reihenfolge für Move:** model_roles → model_router, model_registry → escalation_manager → model_orchestrator (oder alle gemeinsam, da keine Zyklen).

---

## 4. Externe Abhängigkeiten

### 4.1 Wer importiert den Model-Cluster?

| Importeur | Importiert |
|-----------|------------|
| **app/chat_widget.py** (Legacy) | ModelRole, ModelOrchestrator |
| **app/main.py** (Legacy) | ModelOrchestrator, get_registry |
| **app/ui/settings_dialog.py** | get_registry |
| **app/ui/chat/chat_header_widget.py** | ModelRole, get_role_display_name, all_roles |
| **app/ui/sidepanel/model_settings_panel.py** | ModelRole, get_role_display_name, all_roles, get_default_model_for_role |
| **app/ui/agents/agent_form_widgets.py** | all_roles, get_role_display_name, ModelRole |
| **app/core/commands/chat_commands.py** | ModelRole |
| **app/agents/agent_service.py** | ModelRole, all_roles |
| **app/agents/agent_profile.py** | ModelRole |
| **app/agents/seed_agents.py** | ModelRole |
| **app/help/doc_generator.py** | ModelRole, ROLE_DISPLAY_NAMES, DEFAULT_ROLE_MODEL_MAP |
| **app/critic.py** | ModelRole |

### 4.2 Kategorisierung

| Kategorie | Dateien | Aktion bei Move |
|----------|---------|-----------------|
| **GUI** | ui/settings_dialog, ui/chat/chat_header_widget, ui/sidepanel/model_settings_panel, ui/agents/agent_form_widgets | Import-Pfad: `app.model_*` → `app.core.models.*` |
| **Legacy-Root** | main.py, chat_widget.py | Import-Pfad aktualisieren |
| **core** | core/commands/chat_commands | Import-Pfad: `app.model_roles` → `app.core.models.roles` |
| **agents** | agent_service, agent_profile, seed_agents | Import-Pfad aktualisieren |
| **help** | doc_generator | Import-Pfad aktualisieren |
| **Root** | critic.py | Import-Pfad aktualisieren |

---

## 5. Zirkuläre Risiken

- **core → providers:** model_orchestrator importiert providers. Laut strikter Regel: core darf providers nicht importieren. **Ausnahme nötig** oder ModelOrchestrator außerhalb core belassen.
- **help → model_roles:** help/doc_generator importiert model_roles. help ist GUI-nah (Doc-Generator für UI). Kein Zyklus.

---

## 6. Empfohlene Move-Gruppen

**Gruppe 1 (einheitlich):** Alle fünf Dateien gemeinsam nach `app/core/models/`

| Quell | Ziel |
|-------|------|
| app/model_roles.py | app/core/models/roles.py |
| app/model_router.py | app/core/models/router.py |
| app/model_registry.py | app/core/models/registry.py |
| app/escalation_manager.py | app/core/models/escalation_manager.py |
| app/model_orchestrator.py | app/core/models/orchestrator.py |

**Re-Exports:** `app/core/models/__init__.py` exportiert alle öffentlichen Symbole. Optional: `app/model_roles.py` etc. als Re-Export-Dateien im Root belassen (Rückwärtskompatibilität) – erhöht Wartungsaufwand, daher **nicht empfohlen**. Besser: alle Imports einmalig aktualisieren.

---

## 7. Vorbedingungen für Move nach app/core/models/

1. **Architektur-Regel:** `core/models` darf `providers` importieren (oder ModelOrchestrator in services belassen – dann Cluster zerlegt).
2. **Import-Updates:** ~15–20 Dateien (siehe Abschnitt 4.1).
3. **arch_guard_config:** `FORBIDDEN_IMPORT_RULES` – falls core→providers verboten: Ausnahme für `core/models/` oder Regel anpassen.
4. **Tests:** tests/unit/test_router.py, tests/test_escalation.py, tests/test_model_router.py, tests/test_agent_hr.py, tests/test_slash_commands.py – Import-Pfade aktualisieren.

---

## 8. Risiko-Bewertung

| Risiko | Stufe | Mitigation |
|--------|-------|------------|
| Import-Updates vergessen | Mittel | Grep nach `app.model_`, `app.escalation` |
| core→providers Regelverletzung | Mittel | Architektur-Regel explizit erweitern |
| Tests brechen | Niedrig | Pytest nach Move; bekannte Test-Dateien prüfen |

---

## 9. Zusammenfassung

| Frage | Antwort |
|-------|---------|
| **Kann der Cluster als Ganzes nach app/core/models/?** | Ja, unter Vorbehalt: core→providers-Regel anpassen. |
| **Zerlegung nötig?** | Nein. |
| **GUI-Abhängigkeiten im Cluster?** | Keine. |
| **Legacy-Root-Abhängigkeiten?** | Ja – main.py, chat_widget.py importieren. Nach Move: Pfade aktualisieren. |
| **Vorbedingungen?** | Architektur-Regel core→providers; Import-Updates; Guard-Config prüfen. |
