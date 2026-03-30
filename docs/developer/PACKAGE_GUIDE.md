# Leitfaden: Pakete, Grenzen und Repo-Orientierung

Dieses Dokument ergänzt [`docs/DEVELOPER_GUIDE.md`](../DEVELOPER_GUIDE.md) um die **sichtbare Paketarchitektur**: wo neuer Code hingehört, wie Host vs. externe Plugins getrennt sind, und welche Checks die Struktur absichern.

**Aktuelle Wahrheit (Segmente, Pfade, Guard-Zuordnung):** ausschließlich [`docs/architecture/PACKAGE_MAP.md`](../architecture/PACKAGE_MAP.md). Dieser Leitfaden und [`PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md) spiegeln dieselbe Story und ersetzen sie nicht.

### Host-Segmente, eingebettete Distributionen, Hybrid

| Kategorie | Was | Wo im Repo / Import |
|-----------|-----|---------------------|
| **Host** (`linux-desktop-chat`) | Produktcode unter `app/<segment>/`, der **nicht** in eine eingebettete Wheel-Quelle ausgelagert ist | z. B. `app/gui/`, `app/services/`, `app/core/`, erweiterte Segmente laut [`PACKAGE_MAP.md`](../architecture/PACKAGE_MAP.md) §5 |
| **Eingebettete Distributionen** | Eigene `pyproject.toml` unter Repo-Root, `file:./…` im Host; Namespace `app.*` per `pkgutil.extend_path` | `linux-desktop-chat-features` → `app.features`; `linux-desktop-chat-ui-contracts` → `app.ui_contracts`; `linux-desktop-chat-ui-runtime` → `app.ui_runtime`; `linux-desktop-chat-ui-themes` → `app.ui_themes`; `linux-desktop-chat-pipelines` → `app.pipelines`; `linux-desktop-chat-providers` → `app.providers`; `linux-desktop-chat-utils` → `app.utils`; `linux-desktop-chat-infra` → `app.debug` / `app.metrics` / `app.tools`; `linux-desktop-chat-runtime` → `app.runtime` / `app.extensions`; `linux-desktop-chat-cli` → `app.cli` |
| **Hybrid** (Übergang) | Bewusst erlaubte Nähe zu Produktstart-/Theme-Verhalten oder schmalen `app.gui.*`-Rändern **bis** Ports/Contracts nachziehen; **kein** Freifahrtschein für neue Shell-Kopplung | `ui_application`, `global_overlay`, `workspace_presets`, `help`, `devtools` — `ui_application` / `global_overlay` / `workspace_presets` haben **weder direkte `app.gui.*`-Importe noch verbliebene Root-Startup-Shims** und nutzen stattdessen `app.core.startup_contract`; `help` / `devtools` behalten einen dokumentierten GUI-Rand. Details: [`SEGMENT_HYBRID_COUPLING_NOTES.md`](../architecture/SEGMENT_HYBRID_COUPLING_NOTES.md); Katalog im Code: `HYBRID_PRODUCT_SEGMENTS` in `tests/architecture/segment_dependency_rules.py` |

## Kanonische Landkarte

- **Vollständige Übersicht (Segmente, CI, Plugins, Legacy):** [`docs/architecture/PACKAGE_MAP.md`](../architecture/PACKAGE_MAP.md)  
- **Repo-Split-Readiness (Klassifikation, Matrix, Blocker, Wellenplan):** [`docs/architecture/PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md)  
- **Welle 1 — Extraktionsvorbereitung (ohne physischen Cut):** [`docs/architecture/PACKAGE_WAVE1_PREP.md`](../architecture/PACKAGE_WAVE1_PREP.md)  
- **`app.features` — öffentliche API & Definition of Ready for Cut:** [`docs/architecture/PACKAGE_FEATURES_CUT_READY.md`](../architecture/PACKAGE_FEATURES_CUT_READY.md)  
- **Physischer Split von `app.features` (Packaging, Empfehlung):** [`docs/architecture/PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_FEATURES_PHYSICAL_SPLIT.md)  
- **Commit 3 — CI (Matrix, `LDC_REPO_ROOT`, Workflows):** [`docs/architecture/PACKAGE_FEATURES_COMMIT3_CI.md`](../architecture/PACKAGE_FEATURES_COMMIT3_CI.md)  
- **Commit 4 — Welle 1 Abschluss (Guards, Segment-Scan, QA-Segmente):** [`docs/architecture/PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](../architecture/PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md)  
- **Welle 2 — `app.ui_contracts` Public Surface + SemVer-/Stabilitätsmodell:** [`docs/architecture/PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](../architecture/PACKAGE_UI_CONTRACTS_SPLIT_READY.md) — Zonen §9, Änderungsregeln §10, gemeinsame Versionierung mit `ui_application` §11; querschnittlich `SettingsErrorInfo` in [`linux-desktop-chat-ui-contracts/src/app/ui_contracts/common/errors.py`](../../linux-desktop-chat-ui-contracts/src/app/ui_contracts/common/errors.py); Tests: bevorzugt `from app.ui_contracts import …` für Root-Chat-API (§3.2 dort)  
- **Welle 2 — Split-Vorbereitung `ui_contracts` (Consumer, Blocker, Extraktionsreihenfolge):** [`docs/architecture/PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](../architecture/PACKAGE_UI_CONTRACTS_WAVE2_PREP.md)  
- **`app.ui_contracts` — Cut-Ready / Definition of Ready (ohne physischen Cut):** [`docs/architecture/PACKAGE_UI_CONTRACTS_CUT_READY.md`](../architecture/PACKAGE_UI_CONTRACTS_CUT_READY.md)  
- **`app.ui_contracts` — Physischer Split (Packaging, Empfehlung B):** [`docs/architecture/PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) — Vorlage [`linux-desktop-chat-ui-contracts/`](../../linux-desktop-chat-ui-contracts/); **Commit 2:** [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](../architecture/PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md); **Commit 3 (CI):** [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](../architecture/PACKAGE_UI_CONTRACTS_COMMIT3_CI.md); **Commit 4 (Welle-2-Abschluss):** [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](../architecture/PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md)  
- **Welle 3 — `app.pipelines`:** Split-Analyse [`docs/architecture/PACKAGE_PIPELINES_SPLIT_READY.md`](../architecture/PACKAGE_PIPELINES_SPLIT_READY.md); DoR [`docs/architecture/PACKAGE_PIPELINES_CUT_READY.md`](../architecture/PACKAGE_PIPELINES_CUT_READY.md); **Packaging** [`docs/architecture/PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_PIPELINES_PHYSICAL_SPLIT.md); Vorlage [`linux-desktop-chat-pipelines/`](../linux-desktop-chat-pipelines/); **Commit 2 (Host):** [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](../architecture/PACKAGE_PIPELINES_COMMIT2_LOCAL.md); **Commit 3 (CI):** [`PACKAGE_PIPELINES_COMMIT3_CI.md`](../architecture/PACKAGE_PIPELINES_COMMIT3_CI.md); **Commit 4 (Welle-3-Abschluss):** [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](../architecture/PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md)  
- **Welle 4 — `app.providers`:** Split-/Packaging [`docs/architecture/PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md); Vorlage [`linux-desktop-chat-providers/`](../../linux-desktop-chat-providers/); **Commit 2:** [`PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`](../architecture/PACKAGE_PROVIDERS_COMMIT2_LOCAL.md); **Commit 3 (CI):** [`PACKAGE_PROVIDERS_COMMIT3_CI.md`](../architecture/PACKAGE_PROVIDERS_COMMIT3_CI.md); **Commit 4 (Abschluss):** [`PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md`](../architecture/PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md)  
- **Welle 5 — `app.cli`:** technische Readiness [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](../architecture/PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md); Split-/Cut-Ready [`PACKAGE_CLI_SPLIT_READY.md`](../architecture/PACKAGE_CLI_SPLIT_READY.md), [`PACKAGE_CLI_CUT_READY.md`](../architecture/PACKAGE_CLI_CUT_READY.md); Decision Memo [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](../architecture/PACKAGE_WAVE5_CLI_DECISION_MEMO.md); Vorlage [`linux-desktop-chat-cli/`](../../linux-desktop-chat-cli/); Abschluss [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](../architecture/PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md); Rahmen [`PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md) §6.4  
- **Welle 6 — `app.utils`:** Physischer Split [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_UTILS_PHYSICAL_SPLIT.md); Vorlage [`linux-desktop-chat-utils/`](../../linux-desktop-chat-utils/); Guard [`test_utils_public_surface_guard.py`](../../tests/architecture/test_utils_public_surface_guard.py); Rahmen [`PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md) §6.5  
- **Welle 7 — `app.ui_themes`:** Physischer Split [`PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md); Vorlage [`linux-desktop-chat-ui-themes/`](../../linux-desktop-chat-ui-themes/); Guard [`test_ui_themes_public_surface_guard.py`](../../tests/architecture/test_ui_themes_public_surface_guard.py); Rahmen [`PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md) §6.6  
- **Welle 8 — `app.ui_runtime`:** Physischer Split [`PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md); Vorlage [`linux-desktop-chat-ui-runtime/`](../../linux-desktop-chat-ui-runtime/); Guard [`test_ui_runtime_public_surface_guard.py`](../../tests/architecture/test_ui_runtime_public_surface_guard.py); Rahmen [`PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md) §6.7  
- **Welle 9 — `app.debug` / `app.metrics` / `app.tools`:** Physischer Split [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_INFRA_PHYSICAL_SPLIT.md); Vorlage [`linux-desktop-chat-infra/`](../../linux-desktop-chat-infra/); Guard [`test_infra_public_surface_guard.py`](../../tests/architecture/test_infra_public_surface_guard.py); Rahmen [`PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md) §6.8
- **Welle 10 — `app.runtime` / `app.extensions`:** Physischer Split [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_RUNTIME_PHYSICAL_SPLIT.md); Vorlage [`linux-desktop-chat-runtime/`](../../linux-desktop-chat-runtime/); Guard [`test_runtime_public_surface_guard.py`](../../tests/architecture/test_runtime_public_surface_guard.py); Rahmen [`PACKAGE_SPLIT_PLAN.md`](../architecture/PACKAGE_SPLIT_PLAN.md) §6.9  
- **Maschinenlesbare Landmarken:** `app/packaging/landmarks.py`  
- **Import- und Root-Datei-Guards:** `tests/architecture/arch_guard_config.py`, `tests/architecture/test_app_package_guards.py`  
- **Segment-Verbotskanten (AST):** `tests/architecture/segment_dependency_rules.py`, `tests/architecture/test_segment_dependency_rules.py` — Phase-3-Konsolidierung (Tabelle): [`docs/architecture/PACKAGE_MAP.md`](../architecture/PACKAGE_MAP.md) § „Segment Dependency Rules“ / „Phase 3“.  
- **Zielbild der Modul-Verantwortlichkeiten:** [`docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md`](../04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md)

## Wo platziere ich Code?

| Wenn du … | dann bevorzugt unter … |
|-----------|-------------------------|
| eine neue **GUI-Oberfläche** baust | `app/gui/` (Domains, Workspaces, Shell) |
| **Orchestrierung** zwischen DB, Providern und UI brauchst | `app/services/` |
| **Edition/Feature/Registry/Release-Matrix** anfasst | `linux-desktop-chat-features/src/app/features/` (Distribution `linux-desktop-chat-features`, Import `app.features`) |
| **Qt-freie UI-Verträge** (`app.ui_contracts`) anpasst | `linux-desktop-chat-ui-contracts/src/app/ui_contracts/` (Distribution `linux-desktop-chat-ui-contracts`; Host installiert per `file:` — siehe [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](../architecture/PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md)) |
| **Builtin-Theme-Assets** (Manifeste, QSS, Layout-JSON unter `app.ui_themes`) anfasst | `linux-desktop-chat-ui-themes/src/app/ui_themes/` (Distribution `linux-desktop-chat-ui-themes`, Import `app.ui_themes`; [`PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md)) |
| **QML-/Widget-UI-Runtime** (`app.ui_runtime`: Manifest-Validierung, `QmlRuntime`, Shell-Bridge, Chat-QML-VM) anfasst | `linux-desktop-chat-ui-runtime/src/app/ui_runtime/` (Distribution `linux-desktop-chat-ui-runtime`; [`PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md); Laufzeit braucht Host/`ui_contracts`/`ui_application`) |
| **Pipeline-Engine / Executors** (`app.pipelines`) anfasst | `linux-desktop-chat-pipelines/src/app/pipelines/` (Distribution `linux-desktop-chat-pipelines`; [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](../architecture/PACKAGE_PIPELINES_COMMIT2_LOCAL.md), Abschluss [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](../architecture/PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md)) |
| **Ollama-Provider / `OllamaClient`** (`app.providers`) anfasst | `linux-desktop-chat-providers/src/app/providers/` (Distribution `linux-desktop-chat-providers`; Abschluss [`PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md`](../architecture/PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md); **`app.utils`** separat aus `linux-desktop-chat-utils` — isolierte Provider-Dev: [`linux-desktop-chat-providers/README.md`](../../linux-desktop-chat-providers/README.md); Übergang: Root [`app/ollama_client.py`](../../app/ollama_client.py) re-exportiert weiterhin aus `app.providers`) |
| **RAG** implementierst | `app/rag/` (Abhängigkeit: Extra `rag` in `pyproject.toml`) |
| **Agenten** erweiterst | `app/agents/` |
| **kontext- oder chat-spezifische** Logik ohne Qt brauchst | `app/chat/`, `app/context/` — `app/chat` importiert weder `app.gui`/`app.ui_application` noch Qt; Guard: `tests/architecture/test_chat_domain_governance_guards.py`; Chat-Abschluss: `docs/04_architecture/CHAT_SEGMENT_CLOSEOUT.md` |
| **Pfad-/Datetime-/`.env`-Helfer** (`app.utils`) anfasst | `linux-desktop-chat-utils/src/app/utils/` (Distribution `linux-desktop-chat-utils`, Import `app.utils`; [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_UTILS_PHYSICAL_SPLIT.md)) |
| **kopflose** Werkzeuge schreibst | `linux-desktop-chat-cli/src/app/cli/` (Distribution `linux-desktop-chat-cli`, Import `app.cli`; technischer Report [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](../architecture/PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md)) |
| **EventBus / DebugStore / Metriken / FileSystemTools** (`app.debug`, `app.metrics`, `app.tools`) anfasst | `linux-desktop-chat-infra/src/app/{debug,metrics,tools}/` (Distribution `linux-desktop-chat-infra`; [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_INFRA_PHYSICAL_SPLIT.md); `app.metrics` braucht `app.utils`) |
| **Lifecycle / Modell-Invocation-DTOs / Extension-Root** (`app.runtime`, `app.extensions`) anfasst | `linux-desktop-chat-runtime/src/app/{runtime,extensions}/` (Distribution `linux-desktop-chat-runtime`; [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_RUNTIME_PHYSICAL_SPLIT.md); Shutdown-Pfad braucht Host `app.metrics` / `app.services`) |
| ein **externes** installierbares Plugin lieferst | eigenes Paket + Entry-Point `linux_desktop_chat.features` (siehe [`PLUGIN_AUTHORING_GUIDE.md`](PLUGIN_AUTHORING_GUIDE.md)) |

**Hinweis:** Nicht jedes sinnvolle Unterpaket ist bereits in `TARGET_PACKAGES` (`arch_guard_config.py`) für Import-Guards erfasst. Neue Top-Level-Pakete unter `app/` lösen einen Konsistenztest aus, bis sie in `app/packaging/landmarks.py` dokumentiert sind (siehe unten).

### Segment CLI (Welle 5, `app.cli`)

- **Distribution:** [`linux-desktop-chat-cli/`](../../linux-desktop-chat-cli/) (Host-Abhängigkeit `linux-desktop-chat-cli @ file:./linux-desktop-chat-cli` in [`pyproject.toml`](../../pyproject.toml)).  
- **Importpfad:** unverändert **`app.cli`** und Submodule (`app.cli.context_replay`, …); Namespace über `pkgutil.extend_path` im Host-[`app/__init__.py`](../../app/__init__.py).  
- **Public Surface / Consumer-Disziplin:** [`PACKAGE_CLI_CUT_READY.md`](../architecture/PACKAGE_CLI_CUT_READY.md) §3; automatischer Check: **`tests/architecture/test_cli_public_surface_guard.py`**.

### Segment-Abhängigkeiten (Kern)

- **Erlaubt typischerweise:** `gui` importiert `services`, `core`, `features`, … (siehe Ist-Code); **nicht** direkt `providers`.  
- **Verboten (Guard):** u. a. `services`/`core`/Domänen-Segmente → `gui`; **Phase 2** Backbone → `gui`; **Phase 3A** `chat`, `chats`, `llm`, `cli` → `gui`; **Hybrid-Härtung** `global_overlay`, `workspace_presets`, `ui_application` → `gui`; zusätzliche UI-Guardrails verbieten dort Rückfälle auf die entfernten Root-Shims `app.gui_bootstrap`, `app.gui_registry`, `app.gui_capabilities`; `features` → `gui` / `services` / `ui_application` / `ui_runtime`; `gui` → `providers`. Hybrid-Segmente (Ist/Soll je Segment, Core-Contract / schmale GUI-Ränder): [SEGMENT_HYBRID_COUPLING_NOTES.md](../architecture/SEGMENT_HYBRID_COUPLING_NOTES.md).  
- **Ausnahmen:** nur explizit in `SEGMENT_IMPORT_EXCEPTIONS` mit Modulpfad und Kommentar/Follow-up — keine stillen Ignores.

## Neues Top-Level-Unterpaket unter `app/`

1. Leg das Paket mit `__init__.py` an.  
2. Trage den Ordnernamen in `EXTENDED_APP_TOP_PACKAGES` in `app/packaging/landmarks.py` ein **oder** beantrage Aufnahme in `TARGET_PACKAGES` + passende `FORBIDDEN_IMPORT_RULES` in `arch_guard_config.py` (Architektur-Review).  
3. Erwähne das Segment kurz in [`docs/architecture/PACKAGE_MAP.md`](../architecture/PACKAGE_MAP.md) (Abschnitt 2 oder 5).  
4. `pytest tests/architecture/test_package_map_contract.py -q` muss grün sein.

## Host vs. externes Plugin

| Aspekt | Host (`linux-desktop-chat`) | Externes Plugin |
|--------|----------------------------|-----------------|
| Import | `app.*` | Eigener Namespace (`ldc_plugin_example`, …) |
| Aktivierung | Edition + eingebaute Registrare | setuptools-Entry-Point-Gruppe `linux_desktop_chat.features` |
| Freigabe | — | Produktfreigabe / Konfiguration (siehe Architektur-Doku zu Governance) |

## Git-Provenance für QA-/Release-Berichte

Siehe [`architecture/GIT_QA_GOVERNANCE.md`](../architecture/GIT_QA_GOVERNANCE.md): `capture_git_context()`, `build_qa_run_provenance()`, `evaluate_soft_gates()` — JSON-CLI: `python3 scripts/dev/print_git_qa_provenance.py`.

---

## Tests, die die Paketsichtbarkeit absichern

| Testmodul | Zweck |
|-----------|--------|
| `tests/architecture/test_package_map_contract.py` | Repo-Landmarken existieren; erweiterte `app/`-Pakete sind dokumentiert; Entry-Point-Gruppe konsistent; `KNOWN_PRODUCT_SEGMENTS` / `HYBRID_PRODUCT_SEGMENTS` konsistent mit Guard-Sets |
| `tests/architecture/test_segment_dependency_rules.py` | Verbotskanten zwischen Segmenten + dokumentierte Ausnahmen (`segment_dependency_rules.py`) |
| `tests/architecture/test_app_package_guards.py` | Import-Richtungen, App-Root-Dateien, Navigation |
| `tests/architecture/test_ui_layer_guardrails.py` | UI-/Hybrid-Ränder: `ui_application` / `global_overlay` / `workspace_presets` ohne direkte `app.gui`-Imports und ohne Root-GUI-Brücken; `help` nur über `help/ui_components.py`; `devtools` nur über `app.gui.themes.*` |
| `tests/architecture/test_ui_contracts_public_surface_guard.py` | Keine `_*`-Symbol-Imports aus `app.ui_contracts` im Repo-Tree außerhalb des Pakets (Submodule-Pfade bleiben erlaubt) |
| `tests/architecture/test_pipelines_public_surface_guard.py` | `app.pipelines`: nur Root oder `app.pipelines.{models,engine,services,executors,registry}` außerhalb des Paket-Quellsegments; keine `_*`-Imports von außen |
| `tests/architecture/test_providers_public_surface_guard.py` | `app.providers`: kanonische Submodule außerhalb des Paket-Quellsegments; keine `_*`-Imports von außen |
| `tests/architecture/test_cli_public_surface_guard.py` | `app.cli`: kanonische Submodule außerhalb des Paket-Quellsegments; keine `_*`-Imports von außen; Verbot `gui`/`ui_application`/`ui_runtime` aus CLI-Quelle |
| `tests/architecture/test_utils_public_surface_guard.py` | `app.utils`: nur Root oder `app.utils.{paths,datetime_utils,env_loader}` außerhalb des Pakets |
| `tests/architecture/test_ui_themes_public_surface_guard.py` | `app.ui_themes`: nur Paket-Root-Importpfad außerhalb des Theme-Pakets |
| `tests/architecture/test_ui_runtime_public_surface_guard.py` | `app.ui_runtime`: nur kanonische Submodule außerhalb des Runtime-Pakets |
| `tests/architecture/test_infra_public_surface_guard.py` | `app.debug` / `app.metrics` / `app.tools`: nur kanonische Submodule außerhalb des Infra-Pakets |
| `tests/architecture/test_runtime_public_surface_guard.py` | `app.runtime` / `app.extensions`: nur kanonische Submodule außerhalb des Runtime-Pakets |
| `tests/architecture/test_architecture_map_contract.py` | Architecture Map Validator |

## CI und Editionen

Matrix und Validierung: `tools/ci/release_matrix_ci.py`, Workflows unter `.github/workflows/`. Edition-Umgebungsvariable: `LDC_EDITION` (siehe `app.features.edition_resolution`). In CI ist zusätzlich **`LDC_REPO_ROOT`** auf den Checkout-Root gesetzt (Details: [`PACKAGE_FEATURES_COMMIT3_CI.md`](../architecture/PACKAGE_FEATURES_COMMIT3_CI.md)).
