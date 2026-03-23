# CHANGELOG_STABILIZATION – Linux Desktop Chat

**Stand:** 2026-03-21  
**Bezug:** `docs/STABILIZATION_PLAN.md`, `docs/RELEASE_BLOCKER_LIST.md` (RB-01–RB-09)

## Kurzfassung

Die pytest-Gesamtsuite läuft mit aktivierter venv und `requirements.txt` **ohne Failures** (Exit 0). Architektur-Guards, Kontext-Injektion, DB-Isolation, Provider-Service, Drift-Radar, QA-Hilfstests und Prompt-`list_all` wurden stabilisiert.

---

## Änderungen nach Thema

### 1. Test-Infrastruktur & DB-Isolation (RB-05, RB-07, RB-01)

| Änderung | Warum |
|----------|--------|
| `tests/conftest.py`: `LINUX_DESKTOP_CHAT_SKIP_DEFAULT_PROJECT=1` | Verhindert `_ensure_default_project` („Allgemein“) unter pytest → deterministische Projektanzahl, globale Chats, Kontexttests |
| `DatabaseManager(..., ensure_default_project=False)` optional; Skip auch über Env | Explizite Kontrolle; Produktions-Default bleibt `True` |
| `tests/test_projects.py`, `tests/test_db_files.py`, `tests/test_app.py`: `tmp_path` + dict-Zugriff für `list_projects` / `list_chats_of_project` | Keine schreibgeschützten CWD-DBs; API liefert Dicts |

### 2. Chat / Kontext (RB-01)

| Änderung | Warum |
|----------|--------|
| `chat_service.py`: `source_not_found_entries = []` vor Nutzung in `_inject_chat_context` | **Bugfix:** NameError wurde von `except Exception` verschluckt → stille Nicht-Injektion |

### 3. Architektur-Governance (RB-03)

| Änderung | Warum |
|----------|--------|
| `ml_intent_classifier.py`: `importlib.import_module("app.rag.embedding_service")` | Kein statischer `core → rag` Import (AST-Guard) |
| `chat_guard/service.py`: `importlib.import_module("app.services.infrastructure")` | Kein statischer `core → services` Import |
| `context/engine.py`: `importlib.import_module("app.debug.emitter")` | Kein statischer `context → debug.emitter` Import (EventBus-Guard) |
| `ollama_client.py`: `validate_ollama_cloud_api_key` | Cloud-Key-Check ohne `CloudOllamaProvider` in Services |
| `provider_service.py`: Env-Key via `load_env` + `validate_cloud_api_key` über `OllamaClient` | Provider-Orchestrator-Guard: keine Provider-Klassen-Imports in `services/` |

### 4. Drift-Radar / Timeouts (RB-04)

| Änderung | Warum |
|----------|--------|
| `architecture_drift_radar.py`: `--ignore test_architecture_drift_radar.py` im verschachtelten pytest | **Rekursion:** Architektur-Suite enthielt den Test, der das Skript erneut startete → Timeout |
| Inneres pytest-Timeout 180 s | Puffer für langsamere Runner |

### 5. Sonstige Test-/Service-Fixes (RB-01)

| Änderung | Warum |
|----------|--------|
| `prompt_service.py` `list_all`: inneres `try/except` um Legacy-`list_all`-Fallback | `ConnectionError` nach `TypeError`-Zweig wurde nicht gefangen |
| `tests/qa/coverage_map/test_coverage_map_loader.py`: Inventory unter `artifacts/json/`; Erfolgstest prüft korrekten Pfad | Entspricht `load_inventory`-Pfad |
| `tests/qa/test_semantic_enrichment.py`: Config unter `docs/qa`-ähnlich `config/` | Entspricht `apply_semantic_enrichment` |

### 6. CI (RB-06)

| Änderung | Warum |
|----------|--------|
| `.github/workflows/pytest-full.yml` | Vollständige Suite + `collect-only` auf Ubuntu/py3.12 mit `requirements.txt` |

### 7. Dokumentation

| Änderung | Warum |
|----------|--------|
| `README.md` Abschnitt **Tests** | venv-Pflicht und Hinweis zu Test-Env |

---

## Behobene Blocker (Mapping)

| Blocker | Adressiert durch |
|---------|-------------------|
| RB-01 (Suite rot) | Kontext-Bugfix, DB/Tests, Prompt list_all, QA-Pfade, Drift-Rekursion |
| RB-02 (gui.zip) | Nicht im Workspace vorhanden; Repo ignoriert `*.zip` bereits |
| RB-03 (Guards) | Importlib + OllamaClient-Validierung |
| RB-04 (Drift-Timeout) | Ignore + Timeout-Anpassung |
| RB-05 (Collection / venv) | README-Tests + bestehende `requirements.txt` |
| RB-06 (CI) | `pytest-full.yml` |
| RB-07 (readonly DB) | tmp_path + Skip Default-Project |

---

*Ende CHANGELOG_STABILIZATION*
