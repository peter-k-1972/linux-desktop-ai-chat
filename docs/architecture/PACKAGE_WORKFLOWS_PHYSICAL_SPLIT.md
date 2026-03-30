# Physischer Split `app.workflows` (Runbook / Referenz)

**Projekt:** Linux Desktop Chat  
**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.7 (`ldc-workspace-data`), Split-Readiness-Guards [`tests/architecture/test_workflows_split_readiness_guards.py`](../../tests/architecture/test_workflows_split_readiness_guards.py) (Quellwurzel per `find_spec`).

**Status dieses Dokuments:** Physischer Cut **umgesetzt** — kanonische Quelle [`linux-desktop-chat-workflows/src/app/workflows/`](../../linux-desktop-chat-workflows/src/app/workflows/); Host-Verzeichnis `app/workflows/` entfernt; Host bindet `linux-desktop-chat-workflows @ file:./linux-desktop-chat-workflows`. Guards, SYSTEM_MAP und kanonische Architektur-Doku **nachgezogen**. Das Dokument bleibt als **Runbook und Referenz** gültig.

---

## 1. Zielbild des Splits

| Feld | Inhalt |
|------|--------|
| **Ziel** | Kanonische **Python-Quelle** von `app.workflows` liegt im Monorepo unter **`linux-desktop-chat-workflows/src/app/workflows/`**; das Host-Verzeichnis **`app/workflows/`** entfällt. |
| **Produkt** | Eingebettete Distribution **`linux-desktop-chat-workflows`** (PEP 621), gebunden im Host per `file:./linux-desktop-chat-workflows` (später optional PyPI-Pin). |
| **Einordnung** | Zweiter Baustein von **`ldc-workspace-data`** neben bereits gesplittetem [`app.projects`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md); **`app.persistence`** bleibt **außerhalb** dieser Welle. |
| **Nicht-Ziel** | Keine Umbenennung des Paketnamens, keine Erweiterung der Root-Public-Surface, keine Refactors der Executor-Logik aus „Split-Komfort“-Gründen. |

---

## 2. Zielstruktur des neuen Wheels

| | Pfad / Vorgabe |
|---|----------------|
| **Monorepo-Root** | `linux-desktop-chat-workflows/` (Top-Level, analog [`linux-desktop-chat-projects/`](../../linux-desktop-chat-projects/)) |
| **Quellbaum** | `linux-desktop-chat-workflows/src/app/workflows/**/*.py` (1:1 Inhalt aus heutigem `app/workflows/`) |
| **Build** | `[tool.setuptools.packages.find]` mit `where = ["src"]`, `include = ["app*"]` |
| **Begleitdateien** | `pyproject.toml`, `README.md`; optional `tests/` nur wenn Wheel-eigene Smoke-Tests gewünscht (Host-`tests/unit/workflows/` bleiben primär im Monorepo-Host) |

---

## 3. Import- und Namespace-Invariante

| Regel | Inhalt |
|-------|--------|
| **Variante B** | Alle Importstrings bleiben **`from app.workflows…`** / **`import app.workflows`** — **kein** Präfixwechsel. |
| **Namespace** | Host-[`app/__init__.py`](../../app/__init__.py) behält **`pkgutil.extend_path`**; das Wheel erweitert denselben **`app`‑Namespace**. |
| **Root-Re-Exports** | [`linux-desktop-chat-workflows/src/app/workflows/__init__.py`](../../linux-desktop-chat-workflows/src/app/workflows/__init__.py) **`__all__`** bleibt mit [`test_workflows_split_readiness_guards.py`](../../tests/architecture/test_workflows_split_readiness_guards.py) (`_EXPECTED_ROOT_EXPORTS`) abgeglichen. |

---

## 4. Bekannte erlaubte Außenkanten

Nur diese **`app.*`‑Module** (außerhalb `app.workflows`) sind im **Ist-Code** vorgesehen und in **`_DOCUMENTED_EXTERNAL_IMPORTS`** der Guards erfasst — **Erweiterungen nur** mit Code-Review **und** Guard-Update:

| Modul | Rolle (kurz) |
|-------|----------------|
| `app.services.workflow_context_adapter` | Kontext-Bundle für `context_load` |
| `app.services.workflow_orchestration_adapter` | Orchestrierung `chain_delegate` |
| `app.services.workflow_agent_adapter` | Agent-Lauf `agent` |
| `app.pipelines` / `app.pipelines.executors` | Tool-/Step-Ausführung, Registry-Validierung |
| `app.prompts.prompt_service` | Lazy: Prompt-Auflösung `prompt_build` |
| `app.agents.agent_service` | Lazy: Agent-Service `agent` |
| `app.chat.context_policies` / `app.chat.request_context_hints` | Enum-/Hint-Vertrag in `registry/node_registry.py` |

**Zusatz-Guard:** `registry/node_registry.py` — nur die dort dokumentierte Teilmenge (`_NODE_REGISTRY_DOCUMENTED_EXTERNAL_IMPORTS`).

**Verboten (unverändert):** `app.gui`, `app.ui_application`, Qt (`PySide*`).

---

## 5. Notwendige Packaging-Abhängigkeiten

| Abhängigkeit | Begründung |
|--------------|------------|
| **`linux-desktop-chat-pipelines @ file:./linux-desktop-chat-pipelines`** (oder gleichwertiger Pin wie im Host) | `app.workflows` importiert **`app.pipelines`** / **`app.pipelines.executors`** statisch oder in Validatoren; ohne installiertes Pipelines-Wheel ist der Importgraph des Workflows-Pakets nicht konsistent. |
| **Host-Module** (`app.services.workflow_*`, `app.chat.*`, `app.prompts.*`, `app.agents.*`) | **Keine** zusätzlichen PEP-508-Zeilen zwingend, sofern der **Host** (oder weitere Namespace-Segmente) diese Pfade zur Laufzeit bereitstellt — analog Restkante bei [`app.projects`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md) §4. |

**Governance:** Abhängigkeitsliste im Wheel-`pyproject.toml` mit [`PACKAGE_MAP.md`](PACKAGE_MAP.md) / Release-Matrix bei Cut abgleichen.

---

## 6. Host-`pyproject.toml`‑Nachzug

- Eintrag in **`[project].dependencies`:**  
  `"linux-desktop-chat-workflows @ file:./linux-desktop-chat-workflows"`  
  (Reihenfolge konsistent zu anderen `file:`-Einträgen; **nach** oder **nebeneinander** mit `linux-desktop-chat-pipelines` — beides muss installierbar sein.)
- Sicherstellen, dass **`app/workflows/`** im Host-Tree **nicht** mehr ins Host-Distribution-Layout fällt (Verzeichnis nach Cut **entfernt** bzw. aus `packages.find` implizit weg).

---

## 7. Guard-Nachzug

| Aufgabe | Vorgabe |
|---------|---------|
| **Quellpfad** | [`test_workflows_split_readiness_guards.py`](../../tests/architecture/test_workflows_split_readiness_guards.py) darf **`APP_ROOT / "workflows"`** nach dem Cut **nicht** mehr als einzige Wahrheit nutzen. |
| **Hilfsmodul** | Neues Modul analog [`tests/architecture/app_projects_source_root.py`](../../tests/architecture/app_projects_source_root.py): `app_workflows_source_root()` via `importlib.util.find_spec("app.workflows")` → `Path(spec.submodule_search_locations[0])`. |
| **Tests anpassen** | `_iter_workflows_python_files()` und Pfade zu `__init__.py` / `node_registry.py` auf **`app_workflows_source_root()`** umstellen. |
| **Fehlermeldung** | Bei fehlendem Spec: Hinweis auf `pip install -e ./linux-desktop-chat-workflows`. |

---

## 8. SYSTEM_MAP-Nachzug

- In [`tools/generate_system_map.py`](../../tools/generate_system_map.py) **`_inject_embedded_app_namespace_lines`** um eine Zeile ergänzen, analog Projekte:  
  `linux-desktop-chat-workflows/src/app/workflows/   # Import app.workflows`  
  (Einfügeanker konsistent zu bestehenden `linux-desktop-chat-*`‑Zeilen wählen.)
- **`python3 tools/generate_system_map.py`** ausführen und `docs/SYSTEM_MAP.md` committen, sodass **Drift-Checks** (`doc_drift_check` / generierte Karte) nicht regressieren.

---

## 9. Doku-Nachzug (kanonisch + Streu)

| Dokument | Anpassung |
|----------|-----------|
| [`PACKAGE_MAP.md`](PACKAGE_MAP.md) | Tabellenzeile **Workflows**: Quellpfad auf eingebettetes Wheel / `src/app/workflows/`; „physisch gesplittet“ analog `projects`. |
| [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) | Matrix §3.7 / Zeile `workflows`: Ist-Pfad und Verweis auf **dieses Runbook**. |
| [`PACKAGE_PROJECTS_PHYSICAL_SPLIT.md`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md) | Checkbox „Folgewelle“ `app/workflows/` abhaken, sobald Cut erfolgt. |
| Streu-Doku | Pfade `app/workflows/` in FEATURES/operations/Archiv: schrittweise auf **logischen Importpfad** oder **Wheel-Pfad** vereinheitlichen (kein Blocker für Cut, aber Release-Drift minimieren). |

---

## 10. Validierungs- und Abnahmekriterien

Nach `pip install -e .` am **Monorepo-Root** (Host + alle `file:`-Dependencies inkl. neuem Wheel):

| # | Kriterium |
|---|-----------|
| V1 | `python3 -c "import importlib.util as u; assert u.find_spec('app.workflows')"` |
| V2 | Kurzimport: `from app.workflows import WorkflowDefinition, GraphValidator` (Root-`__all__`) |
| V3 | `pytest tests/architecture/test_workflows_split_readiness_guards.py -q` **grün** |
| V4 | Stichprobe: `pytest tests/unit/workflows/test_workflow_service.py tests/unit/workflows/test_graph_validator.py -q` (Cut-PR um weitere Suites erweitern) |
| V5 | Mindestens ein Consumer-Pfad: Import aus `app.services.workflow_service` bzw. `python_bridge` ohne `ModuleNotFoundError` |
| V6 | Regeneriertes **`docs/SYSTEM_MAP.md`** zeigt eingebetteten Workflows-Pfad |

**Abnahme READY:** V1–V4 erfüllt; V5–V6 im Cut-PR dokumentiert.

---

## 11. Empfohlene Commit-Reihenfolge

1. **Scaffold:** `linux-desktop-chat-workflows/` mit `pyproject.toml`, `README.md`, leerer oder kopierter `src/app/workflows/` (noch ohne Host-Löschung), Dependencies inkl. **Pipelines** gesetzt.  
2. **Verschiebung:** Quellbaum final nach `src/app/workflows/`; **`app/workflows/`** im Host entfernen; Host-`pyproject.toml` um **`file:./linux-desktop-chat-workflows`** ergänzen.  
3. **Guards:** `app_workflows_source_root.py` + Anpassung `test_workflows_split_readiness_guards.py`.  
4. **SYSTEM_MAP:** Generator-Patch + Regeneration `docs/SYSTEM_MAP.md`.  
5. **Doku:** `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md`, dieses Runbook §0 „Ist“ auf **umgesetzt** drehen; `PACKAGE_PROJECTS_PHYSICAL_SPLIT.md` Folgewelle aktualisieren.  
6. **CI / Matrix:** falls `tools/ci/release_matrix_ci.py` oder Edition-Smokes das neue Paket explizit listen müssen — Nachzug im selben oder Folge-PR.

---

## Verify-Kommandos (Kurz, für den Cut-PR)

```bash
# Projekt-Root, editable Host
python3 -c "import importlib.util as u; assert u.find_spec('app.workflows'); print('app.workflows ok')"
pytest tests/architecture/test_workflows_split_readiness_guards.py -q
python3 tools/generate_system_map.py
```

Optional im Wheel-Verzeichnis:

```bash
cd linux-desktop-chat-workflows && python3 -m pip install -e ".[dev]" && python3 -m build
```

---

## Verweise (minimal)

- Gesamtplan: [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.7.  
- Analogiemodell physisch: [`PACKAGE_PROJECTS_PHYSICAL_SPLIT.md`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md).  
- Pipelines-Konsument: [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md) (Tool-Call-Executor).
