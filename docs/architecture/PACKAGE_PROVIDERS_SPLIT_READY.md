# `app.providers` — Split-Readiness (Vorbereitung Welle 4)

**Projekt:** Linux Desktop Chat  
**Status:** **Architektur-Vorbereitung** (Ist-Segment, Consumer, Blocker-Übersicht) — **`PACKAGE_PROVIDERS_CUT_READY.md`** und **`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`** liegen vor; noch **kein** Physical Split ausgeführt, **kein** Wellenstart, **keine** Code-Umsetzung.  
**Bezug:** [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md), [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md), [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md), [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md), [`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.5 / §6.3, [`PACKAGE_MAP.md`](PACKAGE_MAP.md), [`docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md`](../04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md), `tests/architecture/arch_guard_config.py`, `tests/architecture/test_provider_orchestrator_governance_guards.py`

---

## 1. Zweck und Abgrenzung

### 1.1 Zweck

Dieses Dokument fasst den **Ist-Zustand** des Segments **`app.providers`** zusammen — ergänzend zu **[`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md)** (verbindliche API, SemVer, Consumer-Matrix, DoR) und **[`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md)** (Packaging Variante **B**, `linux-desktop-chat-providers/`, Commits) **ohne erneute Discovery** der Importfläche:

- Modul- und Verantwortungsumfang  
- Consumer und Importflächen (inkl. tiefer Pfade)  
- Kandidaten für eine **stabile öffentliche Oberfläche** (`__all__` / Submodule)  
- **Blocker-Übersicht** (Detail: [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §8)  
- **Abhängigkeit** von der **Core↔Providers-Grenzentscheidung**

### 1.2 Abgrenzung

| Thema | Wo anders |
|--------|-----------|
| **Ob** `providers` nächste Welle ist | [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.3 |
| **Core ↔ providers Schichtung** | [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) |
| **Packaging / `file:` / CI** | [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) (analog `PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`) |
| **SemVer-Zonen, Public Surface, Consumer-Policy** | [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §3–5 |

**Hinweis:** Stabilitäts- und SemVer-Regeln sind in **Cut-Ready** §3–4 **verbindlich** festgelegt; dieses Split-Ready behält die **Ist-Analyse** und frühen Blocker-Hinweise zur Nachvollziehbarkeit.

---

## 2. Aktueller Segmentumfang (`app/providers`)

| Modul (unter `app/providers/`) | Rolle (kurz) |
|--------------------------------|--------------|
| [`__init__.py`](../../app/providers/__init__.py) | Re-Exports, [`__all__`](../../app/providers/__init__.py) |
| [`base_provider.py`](../../app/providers/base_provider.py) | `BaseChatProvider` — abstrakte Chat-Provider-Schnittstelle |
| [`ollama_client.py`](../../app/providers/ollama_client.py) | `OllamaClient`, `OLLAMA_URL`, Streaming-Helfer (`iter_ndjson_dicts`, …) |
| [`local_ollama_provider.py`](../../app/providers/local_ollama_provider.py) | `LocalOllamaProvider` |
| [`cloud_ollama_provider.py`](../../app/providers/cloud_ollama_provider.py) | `CloudOllamaProvider`, u. a. `get_ollama_api_key` |
| [`orchestrator_provider_factory.py`](../../app/providers/orchestrator_provider_factory.py) | `create_default_orchestrator_providers`, `fetch_cloud_chat_model_names` — **Wiring** für Orchestrator/Services |

**Architektur-Insel (Package-Guards):** `providers` darf **nicht** `gui`, `agents`, `rag`, `prompts`, `services`, `debug`, `metrics`, `ui` importieren (`FORBIDDEN_IMPORT_RULES`). **Kein** `app.core`-Import unter `app/providers/` (Ist-Stand).

### 2.1 Laufzeit- / Wheel-Abhängigkeiten (Ist, für späteres Packaging)

Für einen physischen Cut muss die **Distribution** `linux-desktop-chat-providers` (Arbeitsname) ihre **deklarierten** Abhängigkeiten tragen. **Ist-relevant** unter `app/providers/` (ohne Anspruch auf Vollständigkeit weiterer transitive Abhängigkeiten):

| Modul / Nutzung | Beispiel-Abhängigkeit |
|-----------------|------------------------|
| [`ollama_client.py`](../../app/providers/ollama_client.py) | **`aiohttp`** (HTTP-Client, Streaming) |

Weitere Imports sind überwiegend **stdlib**; Cut-Ready / Physical-Split prüfen beim Extrahieren erneut gegen `pyproject.toml` des Ziel-Wheels.

---

## 3. Bekannte Consumer und Importflächen

### 3.1 Produktcode außerhalb `app/providers/**`

| Bereich | Import(e) (Ist) | Anmerkung |
|---------|-----------------|-----------|
| [`app/core/models/orchestrator.py`](../../app/core/models/orchestrator.py) | Provider-neutraler Contract aus `app.core.models.provider_contracts` | `core` importiert `providers` nicht mehr; Verdrahtung erfolgt außerhalb von `core` |
| [`app/services/model_orchestrator_service.py`](../../app/services/model_orchestrator_service.py) | `cloud_ollama_provider.get_ollama_api_key`, `orchestrator_provider_factory.create_default_orchestrator_providers` | Tiefer Pfad + Factory |
| [`app/services/unified_model_catalog_service.py`](../../app/services/unified_model_catalog_service.py) | `get_ollama_api_key`, `fetch_cloud_chat_model_names` (lazy innerhalb Methode) | Tiefer Pfad + Factory |
| [`app/services/infrastructure.py`](../../app/services/infrastructure.py) | `ollama_client.OllamaClient` | Infrastruktur-Bootstrap |
| [`app/services/model_chat_runtime.py`](../../app/services/model_chat_runtime.py) | `get_ollama_api_key` | Tiefer Pfad |
| [`app/main.py`](../../app/main.py) | `OllamaClient`; Root-Provider-Klassen; `get_ollama_api_key` | Root-Launcher; Governance: **GUI** importiert `providers` nicht direkt — `main` ist Sonderfall |
| [`app/ollama_client.py`](../../app/ollama_client.py) (App-Root) | Re-Export `OLLAMA_URL`, `OllamaClient` | Brücke; `KNOWN_IMPORT_EXCEPTIONS` (`ollama_client.py`, `providers`) |

**Root-Brücke `app.ollama_client` (indirekte Anbindung an `app.providers`):** Produktcode importiert kanonisch aus `app.providers.ollama_client` oder über diese Datei. **Tests**, die **weiterhin die Brücke** nutzen (Ist):

| Testmodul | Import |
|-----------|--------|
| [`tests/live/test_agent_execution.py`](../../tests/live/test_agent_execution.py) | `from app.ollama_client import OllamaClient` |
| [`tests/live/test_ollama.py`](../../tests/live/test_ollama.py) | `from app.ollama_client import OllamaClient` |
| [`tests/smoke/test_app_startup.py`](../../tests/smoke/test_app_startup.py) | `from app.ollama_client import OllamaClient` |

**Cut-Ready:** kanonischen Importpfad festlegen (Brücke beibehalten vs. Migration auf `app.providers.ollama_client`) und Tests/Doku angleichen.

**`KNOWN_IMPORT_EXCEPTIONS` (`tests/architecture/arch_guard_config.py`):** Einträge **1:1** gegen den **aktuellen** Quellcode abgleichen (Pflicht laut [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §6): jede Zeile muss noch einen **tatsächlichen** Import rechtfertigen oder wird entfernt/angepasst (z. B. `core/models/orchestrator.py`, `main.py`, `ollama_client.py`, `gui/domains/settings/settings_dialog.py` — letzterer ggf. Legacy).

### 3.2 Tests und Smoke (Auszug)

| Ort | Nutzung |
|-----|---------|
| `tests/unit/test_ollama_ndjson_stream.py`, `test_ollama_stream_chat_simulation.py` | `ollama_client.iter_ndjson_dicts` |
| `tests/architecture/test_provider_orchestrator_governance_guards.py` | Nur-`orchestrator` in `core` importiert `providers`; `providers` nicht `gui` |
| `tests/architecture/test_service_governance_guards.py` | u. a. Sentinel „GUI importiert `providers` nicht“ |
| `tests/architecture/test_registry_governance_guards.py` | Provider-Klassen für Registry-Tests |
| `tests/smoke/test_context_experiment_smoke.py` | String-Pfad auf `OllamaClient.chat` |

### 3.3 Segment-AST

`FORBIDDEN_SEGMENT_EDGES` enthält **`(gui, providers)`** und **`(providers, gui)`**-relevante Regeln über Package-Guards; **keine** explizite Segment-Kante `core` → `providers` — die Kante wird über **`test_app_package_guards`** / `KNOWN_IMPORT_EXCEPTIONS` geführt.

---

## 4. Public-Surface-Kandidaten für `app.providers`

### 4.1 Bereits im Paket-Root (`__all__`)

Aus [`app/providers/__init__.py`](../../app/providers/__init__.py):

| Symbol | Kategorie |
|--------|-----------|
| `BaseChatProvider` | Abstraktion |
| `LocalOllamaProvider`, `CloudOllamaProvider` | konkrete Implementierungen |
| `OllamaClient`, `OLLAMA_URL` | Low-Level-Client / Konstante |

**Verbindlich im Cut-Ready:** Diese Menge ist **Mindest-Root-API** — siehe [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §3.1; Änderungen **semver-relevant**.

### 4.2 Häufig genutzte Symbole **außerhalb** `__all__` (Kandidaten für Aufnahme oder Submodule-Policy)

| Symbol / Modul | Verwendung | Option für Cut-Ready |
|------------------|------------|----------------------|
| `orchestrator_provider_factory.create_default_orchestrator_providers` | `model_orchestrator_service` | Explizit **öffentlich** machen (Root oder `app.providers.factories`) oder als **intern** dokumentieren und Services als einzigen Caller festlegen |
| `orchestrator_provider_factory.fetch_cloud_chat_model_names` | `unified_model_catalog_service` | wie oben |
| `cloud_ollama_provider.get_ollama_api_key` | mehrere Services, `main` | Entweder in **Root** re-exportieren oder **stabile** Hilfs-API unter dokumentiertem Submodule |
| `ollama_client.iter_ndjson_dicts` | `cloud_ollama_provider`, Unit-Tests | Entweder **öffentlich** (Streaming-API) oder als Implementierungsdetail kennzeichnen |

**Noch kein** verbindlicher Public-Surface-Guard analog `test_pipelines_public_surface_guard.py` — **offene Umsetzung**; siehe [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §3.3, §7–8.

---

## 5. Offene Blocker (Ist-Übersicht; Detail in Cut-Ready / Physical Split)

Die **verbindliche** Priorisierung steht in [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §8; Packaging und Commit-Reihe: [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md). Hier die **ursprüngliche** Sammlung zur Nachverfolgung:

| Blocker | Beschreibung |
|---------|--------------|
| **Core↔Providers** | [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md): Zielvariante wählen oder **explizit** Übergang **A** mit Exit-Kriterium — Cut-Ready §1.3. |
| **Öffentliche API / Submodule** | Policy in Cut-Ready §3.2; ggf. Re-Exports. |
| **Public-Surface-Guard (pytest)** | Noch **nicht** implementiert — Cut-Ready §3.3, §7–8. |
| **Landmarken / `find_spec`** | Nach Host-Cut: Physical Split §6; `app_providers_source_root()`. |
| **PEP-621 / `builtins.core`** | Physical Split §5.3. |
| **CI** | Physical Split §7. |
| **`KNOWN_IMPORT_EXCEPTIONS`** | **1:1-Abgleich** — §3.1; Cut-Ready §6. |

---

## 6. Abhängigkeit zur Core↔Providers-Grenzentscheidung

- **Split-Ready** (dieses Dokument) kann **unabhängig** gelesen werden; **Cut-Ready** und **Physical Split** **dürfen** die Kante `core.models.orchestrator` → `app.providers` **nicht** ignorieren.  
- Kanonische Analyse: [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) §3–4.  
- **Empfohlene Zielrichtung** dort: langfristig **kein** `core`→`providers`; Refactoring über **Services** / **Injektion** / Verschiebung der Orchestrierung.  
- Solange die Kante besteht, muss ein **Physical-Split** entweder **Abhängigkeit `ldc-core` → `ldc-providers`** explizit erlauben oder **Refactoring vor dem Cut** einplanen.

---

## 7. Cut-Ready und Physical Split (liegen vor)

Das **verbindliche** Definition-of-Ready und die Checklisten für die **physische Ausführung** befinden sich nicht mehr hier, sondern in:

- **[`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md)** — Public Surface, SemVer, Consumer-Matrix, Guards, **§7 DoR for Physical Split**, **§8 Blocker**.  
- **[`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md)** — Variante **B**, `linux-desktop-chat-providers/`, Host-`file:`, Landmarken, CI, Commit-Reihe 1–4, Core↔Providers-Vorbedingung §9.

Die frühere Checkbox-Liste dieses Abschnitts ist in **Cut-Ready §7** übernommen und dort fortzuschreiben.

---

## 8. Klare Nicht-Ziele

- **Keine** Code-Änderungen, **kein** neues eingebettetes Repo, **kein** Entfernen von `app/providers/` im Host.  
- **Kein** **ausgeführter** Physical Split und **kein** Release-/PyPI-Plan durch dieses Split-Ready — Planung: [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md).  
- **Kein** Start von **Welle 4** durch dieses Dokument.  
- **Keine** Lösung der Hybrid-Themen (`global_overlay`, `workspace_presets`, `ui_application`↔Themes) — außerhalb des `providers`-Segments.  
- **Kein** Ersatz für [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) — dieses Split-Ready **ergänzt** nur die Provider-Sicht.

---

## 9. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Split-Readiness `app.providers` (Architektur only) |
| 2026-03-25 | Nachzieh-Runde: Root-Brücke `app.ollama_client` + betroffene Tests; §2.1 Wheel-Runtime (`aiohttp`); SemVer-Pflichtsatz für Cut-Ready; KNOWN_IMPORT_EXCEPTIONS 1:1 + Blockerzeile; DoR §7 um SemVer erweitert |
| 2026-03-25 | Doku-Kohärenz: Cut-Ready + Physical Split liegen vor; Status/Bezug/§1/§5/§7/§8 angepasst; Verweise [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md), [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) |
