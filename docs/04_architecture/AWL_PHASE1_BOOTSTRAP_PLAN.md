# AWL Phase 1 — Inhaltlicher Bootstrap-Plan (Startpaket 0.1)

**Status:** Planungsdokument — **kein** angelegtes AWL-Repository, **keine** Implementierung, **keine** JSON-/Schema-Artefakte in diesem Schritt.  
**Bezug:** [AGENT_WORKFLOW_LIBRARY_REPO_DESIGN.md](./AGENT_WORKFLOW_LIBRARY_REPO_DESIGN.md), [CURSOR_LIGHT_BASELINE_SYSTEM.md](./CURSOR_LIGHT_BASELINE_SYSTEM.md), [CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md](./CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md), [ADR: AWL-Konsumptionsmodell](../architecture/adr/ADR_AWL_CONSUMPTION_MODEL.md).

---

## 1. Kurzbericht

**Startpaket 0.1** fokussiert **eine Domäne** (`software-development`) und liefert einen **kleinen, konsistenten Kern**: sechs **Agenten-Templates** (entsprechend der kanonischen Basisfamilie), fünf **Workflow-Templates** (Baseline-Ketten), sieben **Tool-Spezifikationen** (`cl.*`), ein **Bundle** `cursor-light-core` sowie einen **zweistufigen Feature-Baum** für die Produktlinie „Desktop-Chat / Dev-Assist“. Damit ist AWL **sofort** als versionierbare Bibliothek denkbar, ohne Medien-, Business- oder Farm-Erweiterungen. **Playbooks** sind optional **Schritt 2**.

---

## 2. Zielbild Phase 1

| Ziel | Beschreibung |
|------|--------------|
| **Umfang** | Minimal, aber **kohärent**: alle IDs referenzierbar, Bundle und Feature-Baum ohne Lücken. |
| **Mehrwert** | Ein Konsument (z. B. Linux Desktop Chat) kann Phase 1 importieren und erhält **eine** abgestimmte Sicht auf Dev-Assist: Rollen, typische DAG-Muster, Tool-Anforderungen, Freischaltlogik. |
| **Version** | Bibliotheks-Tag **`awl-v0.1.0`** (oder gleichwertige Konvention) — SemVer der **Gesamtbibliothek**; Einzeldefinitionen starten bei `0.1.0` oder `1.0.0` je nach Teamregel (hier: **Definition `1.0.0`** bei stabiler Erstveröffentlichung des Pakets). |
| **Nicht-Ziele** | Keine zweite Domäne, keine Git-Schreib-Tools, keine Runtime-Features jenseits der dokumentierten `required_runtime_features`. |

---

## 3. Domäne: `software-development`

| Feld | Wert |
|------|------|
| **domain-id** | `software-development` |
| **Zweck** | Cursor-light, Code-Arbeit, Review, Tests, Repo-Orientierung — gemäß Baseline-Dokumenten. |
| **Phase-1-Begründung** | Höchster strategischer Wert für Linux Desktop Chat und „Cursor-Ersatz light“; reduziert Review- und Validierungsaufwand. |
| **Abhängigkeiten** | Keine andere AWL-Domäne. |
| **Spätere Artefakte** | Zusätzliche Templates (z. B. CI-Integration), zweites Bundle „`enterprise-dev-governance`“, Erweiterungs-Feature-Bäume. |

---

## 4. Agenten-Templates (6)

Jedes Template **referenziert** die kanonische Rolle und ein **empfohlenes Seed-Mapping** für Linux Desktop Chat (Slug). Die eigentlichen Profile bleiben im Produkt; AWL liefert die **semantische** Schablone.

| ID | Name (Anzeige) | Typ | Zweck | Warum Phase 1 | Abhängigkeiten | Spätere Artefakte |
|----|----------------|-----|-------|---------------|----------------|-------------------|
| `agent.software-development.planner` | Planner (Template) | `agent_template` | Aufgaben zerlegen, Delegation vorbereiten | Kern der Orchestrierung; deckt Basistyp **Planner** ab | — | Spezialisierungen für PM-domänenübergreifend |
| `agent.software-development.analyst-quality` | Analyst / Quality (Template) | `agent_template` | Kritik, Vollständigkeit, Review | Basistyp **Analyst/Quality**; Mapping zu Critic (ggf. Monitor) | — | Separates Template „monitoring-readonly“ |
| `agent.software-development.research-knowledge` | Research & Knowledge (Template) | `agent_template` | Fakten, RAG, Wissensräume | Ein Template für **beide** Seeds (Research + Knowledge), um Phase 1 klein zu halten; Unterscheidung über `variant_hints` (konzeptionell) | Optional: `tool.rag`, `tool.web_search` (Produkt) | Split in zwei Templates in v0.2 |
| `agent.software-development.developer` | Developer (Template) | `agent_template` | Code, Debug | Basistyp **Developer**; Slugs `code_agent`, `debugger_agent` | `tool.cl.*` sobald implementiert | Script-Spezialist als Extension-Template |
| `agent.software-development.author` | Author / Documentation (Template) | `agent_template` | Technische Dokumentation | Basistyp **Author** | `tool.cl.file.read` für Ist-Stand | API-Doc-Generator-Playbook (später) |
| `agent.software-development.automation-integration` | Automation & Integration (Template) | `agent_template` | Tool-Koordination, Pipeline-Denkweise | Basistyp für **Tool/Workflow/Scheduler**-Seeds; zentral für `tool_call`-Nutzung | Workflow-Engine mit `tool_call` | Medien-Pipelines ausgeschlossen in Phase 1 |

**Empfohlenes Seed-Mapping (nur dokumentarisch im Template-Text, nicht als Code):**

| Template-ID | Primärer Seed-Slug (LCD-Chat) |
|-------------|-------------------------------|
| `…planner` | `planner_agent` |
| `…analyst-quality` | `critic_agent` |
| `…research-knowledge` | `research_agent` / `knowledge_agent` |
| `…developer` | `code_agent`, `debugger_agent` |
| `…author` | `documentation_agent` |
| `…automation-integration` | `tool_agent` (primär) |

---

## 5. Workflow-Templates (5)

Abstrakte DAG-Muster; Knotentypen entsprechen der Engine (`start`, `end`, `noop`, `prompt_build`, `agent`, `tool_call`, `context_load`, `chain_delegate`).

| ID | Name | Typ | Zweck | Warum Phase 1 | Abhängigkeiten | Spätere Artefakte |
|----|------|-----|-------|---------------|----------------|-------------------|
| `workflow.software-development.prepare-execute-review` | Prepare → Execute → Review | `workflow_template` | Qualitätsgesicherte Einzelaufgabe | Kern für Dev+Review | ≥2 Agent-Rollen, optional `tool_call` | Variante mit automatischem Test-Knoten |
| `workflow.software-development.analyze-decide-document` | Analyze → Decide → Document | `workflow_template` | Analyse, Entscheidung, Doku | Planungs- und Doku-Pfad | Mehrstufige `prompt_build` + `agent` | Branches/Conditions wenn Engine erweitert |
| `workflow.software-development.context-inspect` | Context Inspect | `workflow_template` | Chat-Kontext transparent machen | Support, Debugging, Trust | `context_load` | Anreicherung mit `cl.git.status` |
| `workflow.software-development.tool-run-pipeline` | Tool Run Pipeline | `workflow_template` | Deterministische Schritte + Tools | Träger für **alle** `cl.*`-Executions | `tool_call`, Tool-Spezifikationen | Multi-Tool-Ketten |
| `workflow.software-development.delegate-orchestrate` | Delegate / Orchestrate | `workflow_template` | TaskPlanner / Execution ohne Chat-UI | Große Aufgaben | `chain_delegate` | Feinjustierung `plan_only` vs. `execute` |

---

## 6. Tool-Spezifikationen (7)

Inhaltliche **Spiegelung** von [CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md](./CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md); IDs im AWL-Namensraum.

| ID | Name | Typ | Zweck | Warum Phase 1 | Abhängigkeiten | Spätere Artefakte |
|----|------|-----|-------|---------------|----------------|-------------------|
| `tool.cl.file.read` | Workspace-Datei lesen | `tool_spec` | Ground Truth aus Repo | Phase A Cursor-light | Executor `cursor_light_tool` (später) | Byte-Modus, große Dateien |
| `tool.cl.file.write` | Datei vollständig schreiben | `tool_spec` | Materialisieren von Änderungen | Phase B | Policy `workspace_write` | Partielles Schreiben |
| `tool.cl.file.patch` | Patch anwenden | `tool_spec` | Gezielte Änderungen | Phase B | Policy `workspace_write` | Hunk-basierte API |
| `tool.cl.repo.search` | Repo-Suche | `tool_spec` | Navigation | Phase A | — | Semantische Suche |
| `tool.cl.test.run` | Tests ausführen | `tool_spec` | Verifikation | Phase B | Allowlist, Timeout | Coverage-Report |
| `tool.cl.git.status` | Git-Status | `tool_spec` | Überblick | Phase A | Git im Workspace | — |
| `tool.cl.git.diff` | Git-Diff lesen | `tool_spec` | Review-Input | Phase A | Git im Workspace | Umfangreichere Scopes |

**Explizit nicht in Phase 1:** `vcs_write`, Shell-frei ohne Allowlist, Medien-Tools.

---

## 7. Bundle: `cursor-light-core`

| Feld | Wert |
|------|------|
| **ID** | `bundle.cursor-light-core` |
| **Name** | Cursor light — Kern |
| **Typ** | `bundle` |
| **Zweck** | Standardpaket für software-development Assistenz im Sinne der Baseline |
| **Warum Phase 1** | Einziger zusammengeführter Einstiegspunkt für Konsumenten und QA |
| **Enthält (referenziert)** | Alle 6 Agenten-Templates, alle 5 Workflow-Templates, alle 7 Tool-Spezifikationen |
| **Abhängigkeiten** | Keine weiteren Bundles (transitiv leer) |
| **Spätere Artefakte** | `bundle.cursor-light-extended` (Lint, Formatter), `bundle.qa-gate-minimal` |

**Optionales Metadatum (konzeptionell):** `safety_profile: conservative` — empfiehlt Phase-A-Tools als Default-Aktivierung im Produkt, Phase-B nur mit Freigabe.

---

## 8. Erster Feature-Baum

| Feld | Wert |
|------|------|
| **ID** | `tree.product.desktop-chat-dev-assist` |
| **Name** | Desktop Chat — Dev Assist |
| **Typ** | `feature_tree` |
| **Zweck** | Zweistufige Freischaltung: Basis-Chat-Assist vs. erweiterter Repo-Arbeitsplatz |
| **Warum Phase 1** | Macht aus dem Bundle ein **produktstrategisch erklärbares** Gebilde ohne Komplexität einer großen Pyramide |

**Knoten (logisch):**

| node_id | Bezeichnung | `provides` / verknüpft | Abhängigkeit |
|---------|-------------|-------------------------|--------------|
| `root` | Dev Assist (Wurzel) | — | — |
| `foundation` | **Dev Assist — Basis** | Aktiviert Teilmenge: Planner, Analyst, Research-Knowledge, Author + Workflows ohne `tool_call` auf `cl.*` | `root` |
| `workspace` | **Dev Assist — Workspace** | Vollständiges `bundle.cursor-light-core` inkl. Tool-Specs und Tool-Run-Pipeline | `foundation` |

**`required_runtime_features` (Beispiele, konzeptionell):**

- Basis: `chat.agent_select`, `workflow.editor` (falls Workflows genutzt), `context_load` für Context-Inspect-Template.
- Workspace: zusätzlich `workflow.tool_call`, Policy-Engine für `cl.*` (sobald vorhanden).

**Spätere Artefakte:** Dritter Ast „Delegation Pro“, Medien-Ast (anderes Bundle).

---

## 9. Bewusst nicht in Phase 1

| Kategorie | Beispiele | Begründung |
|-----------|-----------|------------|
| **Weitere Domänen** | `media-production`, `business-admin`, `infrastructure` | Fokus und Validierungsaufwand |
| **Playbooks / Patterns** | Markdown-Abläufe, Checklisten | Schritt 2 — kein Blocker für Bundle/Tree |
| **Farm-/Butler-Rollen** | `farm.*` aus `default_catalog.json` | Meta-Ebene, separates Bundle später |
| **Zusätzliche Agenten-Templates** | Script-only, reine Monitor-Persona | Redundanz vermeiden bis Bedarf |
| **Weitere Bundles** | QA-Enterprise, Doku-only | Nach Erst-Import-Erfahrung |
| **JSON-Exports** | Konkrete `WorkflowDefinition`-Dateien | Können aus Templates im **Produkt** generiert werden; AWL Phase 1 bleibt **logisch** |
| **Implementierte Executors** | — | Außerhalb AWL (Pipeline-/App-Repo) |

---

## 10. Empfohlene Reihenfolge der tatsächlichen Anlage (im AWL-Repo)

Wenn das Repository physisch befüllt wird, empfiehlt sich diese **Abfolge**, um Referenzfehler zu vermeiden:

| Schritt | Inhalt | Begründung |
|---------|--------|------------|
| **1** | Tool-Spezifikationen `tool.cl.*` | Keine inward dependencies; definieren Sicherheits- und Input/Output-Verträge |
| **2** | Agenten-Templates | Referenzieren nur externe Slugs / Capabilities; optional `required_tools` |
| **3** | Workflow-Templates | Referenzieren Knotentypen + logische Rollen; optional `required_tools` pro Muster |
| **4** | Bundle `bundle.cursor-light-core` | Aggregiert alle IDs; Validator prüft Vollständigkeit |
| **5** | Feature-Baum `tree.product.desktop-chat-dev-assist` | Referenziert Bundle + Stufen |
| **6 (optional)** | Playbooks unter `domains/software-development/playbooks/` | Onboarding „Wann welches Template?“ |

**Zweiter Schritt nach 0.1 (inhaltlich):** Playbooks + Aufspaltung Research/Knowledge bei Bedarf + erstes **Referenzbeispiel** unter `examples/` (weiterhin ohne Pflicht für Phase-1-Tag).

---

## 11. Abhängigkeitsgraph (Überblick)

```
tool.cl.*          (7, untereinander unabhängig)
       ↑
agent.*            (6, optional required_tools → tool.cl.*)
       ↑
workflow.*         (5, optional required_tools / required_agent_types)
       ↑
bundle.cursor-light-core
       ↑
tree.product.desktop-chat-dev-assist
```

---

## 12. Änderungshistorie

| Datum | Änderung |
|-------|----------|
| 2026-03-25 | Erstfassung: Startpaket 0.1 inkl. IDs, Bundle, Feature-Baum, Reihenfolge, Ausschlüsse |
