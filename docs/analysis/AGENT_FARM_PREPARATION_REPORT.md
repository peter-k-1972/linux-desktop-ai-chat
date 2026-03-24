# Agentenfarm — Vorbereitungsschicht (Technischer Bericht)

**Datum:** 2026-03-23  
**Ziel:** Deklarative, nicht produktiv erzwungene Definitionsschicht für mehrstufige Agentenfarmen (Portfolio / Projekt / Produktionsbereich).

---

## 0. Bestehende agentenbezogene Strukturen (IST-Fundstellen)

Vor der neuen Schicht existieren im Projekt bereits folgende Anknüpfungspunkte (keine Duplikation dieser Schicht, nur Kontext):

| Bereich | Pfad / Artefakt | Rolle |
|---------|-----------------|--------|
| Persistente Profile | `app/agents/agent_repository.py` → Tabelle `agents` | Laufzeit-Agenten: u. a. `project_id`, `department`, `role` (Freitext), `workflow_bindings`, `knowledge_spaces`, `escalation_policy` (JSON-Listen/Text) |
| Profil-Dataclass | `app/agents/agent_profile.py` | In-Memory-/Transportmodell zum Repository |
| Registry (DB-gestützt) | `app/agents/agent_registry.py` | Lookup nach id/slug/name, Abteilung, Status |
| Organisationstaxonomie | `app/agents/departments.py` → `Department` | Enum + Beschreibungen (planning, research, development, media, automation, system) — **nicht** identisch mit Farm-`scope_level` |
| LLM-Routing-Rollen | `app/core/models/roles.py` → `ModelRole` | Semantik **Modellauswahl**, nicht Organisationsrolle / Farm-Rolle |
| Workflow-Knoten „agent“ | `app/workflows/registry/node_registry.py` (Validierung), Executor-Pfad unter `app/workflows/execution/` | Verweis auf `agent_id` / `agent_slug` in der **Graph-Definition** |
| Agent-Router / Fabrik | `app/agents/agent_router.py`, `app/agents/agent_factory.py` | Nutzung der Registry zur Auswahl |
| Seed-Daten | `app/agents/seed_agents.py` | Anlage/Initialisierung von Profilen (falls genutzt) |
| GUI | Operations „Agent Tasks“, Control Center „Agents“ — `app/core/navigation/navigation_registry.py` | Kein Bezug zum Farm-Katalog (bewusst) |

**Konventionen, die eingehalten wurden:** JSON für strukturierte Listen in der bestehenden Welt; Trennung **deklarative Spezifikation** (neu: Farm-Katalog) vs. **operative Identität** (`agents.id` UUID). Die Farm-Schicht nutzt **`agent_role_id`** als logischen Schlüssel, um nicht mit DB-IDs zu kollidieren.

---

## 1. Wo angebunden wurde

| Artefakt | Pfad |
|----------|------|
| Datenmodelle (Enums + Dataclass) | `app/agents/farm/models.py` |
| JSON-Loader + Singleton-Cache + Validierung | `app/agents/farm/loader.py` |
| Standard-Katalog (Beispiel-/Referenzdefinitionen) | `app/agents/farm/default_catalog.json` |
| Öffentliche API | `app/agents/farm/__init__.py` (`get_agent_farm_catalog`, …) |
| Tests | `tests/unit/agents/test_agent_farm_catalog.py` |

**Nicht angebunden:** `AgentRegistry` / `AgentRepository` (SQLite), GUI, Workflow-Executor, `AgentService`-Laufzeitpfade.

---

## 2. Warum dort

- **`app/agents/`** ist bereits der Ort für Agentenprofile, Abteilungen (`departments.py`), Routing und die **bestehende, DB-gestützte** `AgentRegistry`. Die neue Schicht sitzt **daneben** als **statische, versionsierbare** Spezifikation — ohne Konflikt mit persistierten `AgentProfile`-Datensätzen.
- **JSON** entspricht den üblichen Mustern im Projekt (Listen/Metadaten als JSON in SQLite und in Repositories). Kein zusätzlicher Parser-Pfad nötig; **PyYAML** wäre möglich, wurde hier nicht genutzt, um eine klare Single-Source-Datei ohne Einrückungsfallen zu haben.
- **Explizite Validierung im Loader** (statt nur JSON Schema) hält die Fehlermeldungen nah am Code und vermeidet doppelte Wahrheit (Schema-Datei vs. Python) in dieser minimalen Phase.

---

## 3. Welche Agententypen bereits definierbar sind

Über das Feld **`farm_role_kind`** (Enum) sind folgende Rollenarten erlaubt:

| `farm_role_kind` | Bedeutung (fachlich) |
|------------------|----------------------|
| `global_butler` | Portfolio-/Global-Butler |
| `project_butler` | Projekt-Butler |
| `area_butler` | Bereichs-/Produktions-Butler |
| `specialist` | Fachagent |
| `qa_review` | QA-/Review-Agent |
| `knowledge_docs` | Doku-/Wissens-Agent |
| `reporting_controlling` | Reporting-/Controlling-Agent |

Zuordnung zur **Ebene** über **`scope_level`:** `global_portfolio` | `project` | `production_area`.

Weitere pro Rolle definierbare Felder im Katalog:

- `agent_role_id` (stabiler logischer Schlüssel, nicht gleich DB-UUID)
- `display_name`, `functional_role`, `responsibility_scope`
- `input_types`, `output_types` (Listen freier Strings)
- `allowed_workflow_ids` (Strings; Konvention `["*"]` = uneingeschränkt dokumentiert im Katalog)
- `escalation_target_role_id` (optional, verweist auf andere `agent_role_id`)
- `activation`: `draft` | `enabled` | `disabled`
- `is_standard`: Standard- vs. optionale Rolle

Der mitgelieferte **`default_catalog.json`** enthält je **eine** Referenzzeile pro gewünschter Rollenart (alle `activation: draft`).

---

## 4. Was bewusst noch NICHT implementiert wurde

- Keine **Zuordnung** Farm-Rolle → konkretes `AgentProfile` / keine Migration in die Tabelle `agents`.
- Keine **Orchestrierung** (wer ruft wen auf, Queues, Butler-Pipeline).
- Keine **GUI**-Anzeige oder -Bearbeitung des Katalogs.
- Keine **Aktivierung** anhand von `activation` in der Laufzeit (Feld ist nur deklarativ gespeichert und validiert).
- Keine **Referenzprüfung** von `escalation_target_role_id` oder `allowed_workflow_ids` gegen existierende Workflows (bewusst locker, um keine harte Kopplung zu erzwingen).
- Keine **Mehrsprachigkeit** / Lokalisierung der Texte im Katalog.

---

## 5. Nächste Schritte (fachlich vorbereitet, nicht umgesetzt)

1. **Mapping-Layer:** Tabelle oder Konfiguration „`agent_role_id` → `agents.slug` / UUID“, sobald Profile existieren sollen.
2. **Orchestrierung:** Butler-Ketten aus `escalation_target_role_id` und `scope_level` auswerten (nach Freigabe der Produktlogik).
3. **Workflow-Governance:** `allowed_workflow_ids` gegen `workflows.workflow_id` validieren (optional, konfigurierbar).
4. **Zusätzliche Katalogdateien:** `load_agent_farm_catalog(catalog_path=…)` oder Zusammenführung mehrerer JSON-Dateien, falls Teams eigene Kataloge pflegen.
5. **Editor-/CI-Validierung:** Bei Bedarf `jsonschema` aus dem Projekt nutzen, um dieselbe Datei in CI zu prüfen (redundant zum Python-Loader, aber für Nicht-Python-Tooling hilfreich).

---

## 6. API-Kurzreferenz

```python
from app.agents.farm import get_agent_farm_catalog, ScopeLevel, FarmRoleKind

cat = get_agent_farm_catalog()
for role in cat.roles:
    if role.scope_level == ScopeLevel.PROJECT:
        ...
idx = cat.by_role_id()
```

Pfad der Standarddatei: `default_catalog_path()` aus `app.agents.farm`.

---

*Ende des Berichts.*
