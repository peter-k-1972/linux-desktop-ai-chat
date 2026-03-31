# Paket- und Repo-Landkarte (PACKAGE_MAP)

**Projekt:** Linux Desktop Chat  
**Status:** Kanonische Übersicht — evolutionär; **physischer** Multi-Repo-Split nicht umgesetzt, **Split-Readiness** verbindlich in [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)  
**Zweck:** Sichtbar machen, **welche logischen „Zielpakete“** das Produkt hat, **wo der Code heute liegt**, und **welche Brücken/Legacy-Pfade** bewusst bestehen.  
**Einheitliche Segment-Wahrheit:** Segmentnamen, Pfade und Guard-Zuordnung **hier**; unterstützende Dokumente verweisen auf dieses Dokument und dürfen keine abweichenden „Ist-Pfade“ behaupten.

**Verwandte Dokumente**

- Repo-Split-Readiness (Klassifikation, Matrix, Blocker, erste Welle): [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)  
- UI-Verträge (`app.ui_contracts`), Welle 2 — Public Surface, SemVer-/Stabilitätszonen (§9–11), ohne physischen Cut: [`PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](PACKAGE_UI_CONTRACTS_SPLIT_READY.md)  
- UI-Verträge — **Split-Vorbereitung** (Consumer-Matrix, Reifegrad, Extraktionsreihenfolge): [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md)  
- UI-Verträge — **Cut-Ready / Definition of Ready** (ohne physischen Cut): [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md)  
- UI-Verträge — **Physischer Split** (Packaging / Importpfad **Variante B**, ohne Ausführung): [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md)  
- Welle-1-Extraktionsvorbereitung (Checklisten, Consumer-Analyse): [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md)  
- `app.features` Cut-Ready (API, DoR, Guards): [`PACKAGE_FEATURES_CUT_READY.md`](PACKAGE_FEATURES_CUT_READY.md)  
- Physischer Split `app.features` (Packaging, Empfehlung B): [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md)  
- Commit-1-Vorlage (Distribution `linux-desktop-chat-features`): Verzeichnis [`linux-desktop-chat-features/`](../linux-desktop-chat-features/) im Repo-Root  
- Commit-1-Vorlage (Distribution `linux-desktop-chat-ui-contracts`, Import `app.ui_contracts`): Verzeichnis [`linux-desktop-chat-ui-contracts/`](../linux-desktop-chat-ui-contracts/) im Repo-Root — [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §0  
- Commit-1-Vorlage (Distribution `linux-desktop-chat-pipelines`, Import `app.pipelines`): Verzeichnis [`linux-desktop-chat-pipelines/`](../linux-desktop-chat-pipelines/) im Repo-Root — [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) §0  
- Commit 2 (Host-Dependency + Entfernen `app/ui_contracts/`, lokal): [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md)  
- Commit 3 (CI-Workflows + eingebettete Distributionen): [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md)  
- Commit 4 (Welle-2-Abschluss, Guards/QA): [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md)  
- Zielbild (Modul-Verantwortlichkeiten, Import-Regeln): [`docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md`](../04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md)  
- Ist-Bewertung: [`docs/04_architecture/APP_PACKAGE_ARCHITECTURE_ASSESSMENT.md`](../04_architecture/APP_PACKAGE_ARCHITECTURE_ASSESSMENT.md)  
- PEP-621 / Extras / Dependency-Gruppen: [`PEP621_OPTIONAL_DEPENDENCIES.md`](PEP621_OPTIONAL_DEPENDENCIES.md), [`DEPENDENCY_GROUPS_TO_EXTRAS.md`](DEPENDENCY_GROUPS_TO_EXTRAS.md)  
- Editionen & Release-Matrix (Code): `linux-desktop-chat-features/src/app/features/release_matrix.py`, `edition_resolution.py` (installiert als `app.features.*`); CI Features: [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md); CI UI-Contracts: [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md)  
- Architektur-Guards (Importe / App-Root): `tests/architecture/arch_guard_config.py`, `tests/architecture/test_app_package_guards.py`  
- Code-Landmarks für spätere Governance: `app/packaging/landmarks.py`  
- Entwickler-Leitfaden: [`docs/developer/PACKAGE_GUIDE.md`](../developer/PACKAGE_GUIDE.md)  
- Welle 3 — `app.pipelines`: Split-Readiness [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md); DoR [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md); **Physischer Split (Variante B):** [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md); Guard: [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py)
- Welle 4 — `app.providers`: Physischer Split [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md); Commit 2: [`PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`](PACKAGE_PROVIDERS_COMMIT2_LOCAL.md); Commit 3 CI: [`PACKAGE_PROVIDERS_COMMIT3_CI.md`](PACKAGE_PROVIDERS_COMMIT3_CI.md); **Commit 4 (Abschluss):** [`PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md`](PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md); Guard: [`test_providers_public_surface_guard.py`](../../tests/architecture/test_providers_public_surface_guard.py)
- Welle 5 — `app.cli` (**abgeschlossen**): technische Readiness [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md); Split-Readiness [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md); Cut-Ready [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md); Physischer Split [`PACKAGE_CLI_PHYSICAL_SPLIT.md`](PACKAGE_CLI_PHYSICAL_SPLIT.md); Decision Memo [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md); **eingebettete Distribution** [`linux-desktop-chat-cli/`](../linux-desktop-chat-cli/) (Import `app.cli`; Host `app/cli/` entfernt); Guard [`test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py); **Commit 4 (Abschluss):** [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md)
- Welle 6 — `app.utils` (**abgeschlossen**): Physischer Split [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](PACKAGE_UTILS_PHYSICAL_SPLIT.md); **eingebettete Distribution** [`linux-desktop-chat-utils/`](../linux-desktop-chat-utils/) (Import `app.utils`; Host `app/utils/` entfernt); Guard [`test_utils_public_surface_guard.py`](../../tests/architecture/test_utils_public_surface_guard.py); **`linux-desktop-chat-providers`** nutzt **`app.utils`** ohne Spiegel (kein `file:`-Eintrag in der Provider-`pyproject.toml` — pip/CWD; Host listet `utils` und `providers` getrennt; isoliert: [`linux-desktop-chat-providers/README.md`](../../linux-desktop-chat-providers/README.md)).
- Welle 7 — `app.ui_themes` (**abgeschlossen**): Physischer Split [`PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`](PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md); **eingebettete Distribution** [`linux-desktop-chat-ui-themes/`](../linux-desktop-chat-ui-themes/) (Import `app.ui_themes`; Host `app/ui_themes/` entfernt; Wheel **package-data** für `builtins/**`); Guard [`test_ui_themes_public_surface_guard.py`](../../tests/architecture/test_ui_themes_public_surface_guard.py).
- Welle 8 — `app.ui_runtime` (**abgeschlossen**): Physischer Split [`PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md); **eingebettete Distribution** [`linux-desktop-chat-ui-runtime/`](../linux-desktop-chat-ui-runtime/) (Import `app.ui_runtime`; Host `app/ui_runtime/` entfernt); Guard [`test_ui_runtime_public_surface_guard.py`](../../tests/architecture/test_ui_runtime_public_surface_guard.py).
- Welle 9 — `app.debug` / `app.metrics` / `app.tools` (**abgeschlossen**): Physischer Split [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](PACKAGE_INFRA_PHYSICAL_SPLIT.md); **eingebettete Distribution** [`linux-desktop-chat-infra/`](../linux-desktop-chat-infra/) (Importe unverändert; Host-`app/debug/`, `app/metrics/`, `app/tools/` entfernt); Guard [`test_infra_public_surface_guard.py`](../../tests/architecture/test_infra_public_surface_guard.py).
- Welle 10 — `app.runtime` / `app.extensions` (**abgeschlossen**): Physischer Split [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_RUNTIME_PHYSICAL_SPLIT.md); **eingebettete Distribution** [`linux-desktop-chat-runtime/`](../linux-desktop-chat-runtime/) (Importe unverändert; Host-`app/runtime/`, `app/extensions/` entfernt); Guard [`test_runtime_public_surface_guard.py`](../../tests/architecture/test_runtime_public_surface_guard.py).

---

## 1. Verteiltes Host-Paket vs. logische Segmente

| Ebene | Was es ist | Ort / Mechanismus |
|--------|------------|-------------------|
| **Host-Distribution** | Ein installierbares Python-Paket (`linux-desktop-chat`), ein `app*`-Tree | [`pyproject.toml`](../../pyproject.toml) (`[project]`, `optional-dependencies`, setuptools `include = ["app*"]`) |
| **Logische Produkt-Segmente** | Verantwortlichkeiten (GUI, Services, RAG, …) | Unterpakete von `app/` (siehe Abschnitt 2) |
| **Feature-Plattform** | Editionen, Registry, Discovery, Release-Matrix, PEP-621-Abgleich | Quelle: `linux-desktop-chat-features/src/app/features/` → Wheel/editable: `app.features` |
| **UI-Verträge** | Qt-freie DTOs/Commands/States zwischen Shell und Anwendungsrahmen | Quelle: `linux-desktop-chat-ui-contracts/src/app/ui_contracts/` → installiert als `app.ui_contracts` (Host-Tree `app/ui_contracts/` entfernt, Commit 2) — [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md) |
| **Externe Erweiterungen** | Plugin-Wheels, eigener Namespace | Entry-Point-Gruppe `linux_desktop_chat.features` (kein `app.*`-Import aus dem Host) |
| **Repo-Werkzeuge** | CI, Matrix-Generatoren, Skripte | `.github/workflows/`, `tools/ci/`, `scripts/` |

Eingebettete Distributionen (`linux-desktop-chat-features`, `linux-desktop-chat-ui-contracts`, `linux-desktop-chat-ui-runtime`, `linux-desktop-chat-ui-themes`, `linux-desktop-chat-pipelines`, `linux-desktop-chat-providers`, `linux-desktop-chat-utils`, `linux-desktop-chat-infra`, `linux-desktop-chat-runtime`, `linux-desktop-chat-cli`) sind **separate** setuptools-Projekte unter dem Repo-Root mit `file:./…` im Host-`pyproject.toml`; der sichtbare **`app.*`-Namespace** bleibt über `pkgutil.extend_path` zusammengefügt.

### Repo-Split-Readiness (Kurz)

Für eine spätere Aufteilung in mehrere GitHub-Repos gilt:

- **Verbindliche Einordnung** jedes produktiven Top-Level-Segments: Zielpaket vs. Host vs. Hybrid (vor Split bereinigen) — Tabelle und Begründungen in [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) § 2.
- **Zielpaket-Steckbriefe** (API, interne Teile, erlaubte Abhängigkeiten, Reifegrad) — § 3 dort.
- **Split-Matrix** (Pfad → Repo-Name, Deps, CI-Scope, Blocker) — § 4.
- **Hybrid-Segmente** (`global_overlay`, `workspace_presets`, `help`, `devtools`, `ui_application`) bleiben bis zur Port-/Facade-Bereinigung **Split-blockierend**; Details in [SEGMENT_HYBRID_COUPLING_NOTES.md](SEGMENT_HYBRID_COUPLING_NOTES.md). Maschinenlesbar: `HYBRID_PRODUCT_SEGMENTS` in `tests/architecture/segment_dependency_rules.py` (Vertrags-Tests) — **Übergang**, kein Freifahrtschein für neue Shell-Kopplungen.

Segment-Governance (`FORBIDDEN_SEGMENT_EDGES`, `arch_guard_config`) und Split-Readiness **ergänzen** sich: Guards sichern heute Import-Richtungen; der Split-Plan entscheidet, **wo** spätere Repos schneiden und **was** vorher entkoppelt wird.

---

## 2. Logische Ziel-Segmente → heutige Quellorte

Die Spalte **Guard-Set** bezieht sich auf `TARGET_PACKAGES` in `tests/architecture/arch_guard_config.py` (Import-Richtungen, App-Root-Policy). Segmente **ohne** Eintrag dort sind **produktiv**, aber noch nicht in dieselbe Guard-Matrix aufgenommen — siehe Abschnitt 5.

| Segment | Rolle | Primärer Codepfad | Guard-Set |
|--------|--------|-------------------|-----------|
| **Platform / Features** | `FeatureDescriptor`, Editionen, Registry, Discovery, Release-Matrix, Dependency-Packaging | `linux-desktop-chat-features/src/app/features/` (Import `app.features`) | ja (`features`) |
| **GUI** | PySide6-Shell, Domains, Workspaces, Navigation, Themes | `app/gui/` | ja (`gui`) |
| **Core** | Konfiguration, DB, Modelle, Navigation-Daten, Befehle (ohne Qt in der Zielvision) | `app/core/` | ja (`core`) |
| **Services** | Orchestrierung (Chat, Knowledge, Provider, …) | `app/services/` | ja (`services`) |
| **Agents** | Agenten, Tasks, Delegation | `app/agents/` | ja |
| **RAG** | Retrieval, Index (Extra `rag`) | `app/rag/` | ja |
| **Prompts** | Prompt-Speicher / Service | `app/prompts/` | ja |
| **Providers** | Ollama local/cloud | `app.providers` aus Distribution `linux-desktop-chat-providers/` (Welle 4 abgeschlossen; Host `app/providers/` entfernt) | ja |
| **LLM** | Completion-Pipeline | `app/llm/` | nein (siehe Zielbild: Teile in `core` vorgesehen) |
| **Pipelines** | Pipeline-Engine | `app.pipelines` aus Distribution (Vorlage `linux-desktop-chat-pipelines/`); Import `app.pipelines` | ja |
| **Debug / Metrics / Tools** | EventBus, Metriken, Hilfswerkzeuge | `app.debug` / `app.metrics` / `app.tools` aus Distribution `linux-desktop-chat-infra/` (**Welle 9**; Host `app/debug/`, `app/metrics/`, `app/tools/` entfernt) | ja |
| **Utils** | String-/Pfad-Helfer ohne Fachkopplung | `app.utils` aus Distribution `linux-desktop-chat-utils/` (**Welle 6**; Host `app/utils/` entfernt) | ja (`utils`) |
| **UI-Schichten (Entkopplung)** | Verträge, Runtime, Themes, Anwendungsrahmen | `app.ui_contracts` aus Distribution (Vorlage `linux-desktop-chat-ui-contracts/`); `app.ui_runtime` aus Distribution `linux-desktop-chat-ui-runtime/` (**Welle 8**; Host `app/ui_runtime/` entfernt); `app.ui_themes` aus Distribution `linux-desktop-chat-ui-themes/` (**Welle 7**); `app/ui_application/` | ja |
| **Chat / Kontext** | Kontext-Rendering, Profile, Chat-Domänenlogik | `app/chat/`, `app/chats/`, `app/context/` | nein |
| **Projekte / Persistenz** | Projekt-Lebenszyklus, Speicher | `app.projects` aus Distribution `linux-desktop-chat-projects/` (Host `app/projects/` entfernt, Commit 2); `app.persistence` aus Distribution `linux-desktop-chat-persistence/` (**physisch gesplittet**; Host `app/persistence/` entfernt) | nein |
| **Workflows** | DAG, Läufe | `app.workflows` aus Distribution `linux-desktop-chat-workflows/` (Host `app/workflows/` entfernt; Import `app.workflows`) | ja |
| **Global Overlay / Presets** | Overlay-Produktcode, Workspace-Presets | `app/global_overlay/`, `app/workspace_presets/` | nein |
| **QML / Alternativ-GUI (Validierung)** | Governance-Hilfen, nicht die primäre Shell | `app/qml_*.py` (Module), QML-Doku unter `docs/04_architecture/` | nein |
| **CLI** | Kopflose Werkzeuge (Kontext Replay/Repro) | `app.cli` aus Distribution `linux-desktop-chat-cli/` (**Welle 5 abgeschlossen**; Host `app/cli/` entfernt) | ja (`cli`) |
| **QA (In-App)** | QA-Artefakte, Panels | `app/qa/` | nein |
| **Runtime / Extensions** | Lifecycle, Modell-Invocation-DTOs, Extension-Root | `app.runtime` / `app.extensions` aus Distribution `linux-desktop-chat-runtime/` (**Welle 10**; Host-`app/runtime/`, `app/extensions/` entfernt) | ja (`runtime`, `extensions`) |
| **Help (App)** | Hilfe-Index, Doc-Loading | `app/help/` | nein |
| **DevTools** | Entwicklerwerkzeuge in der App | `app/devtools/` | nein |
| **Commands** | Kommando-/Palette-Erweiterungen (soweit nicht in core) | `app/commands/` | nein |
| **Host-interne Plugin-Hilfen** | Produktfreigabe, Konfiguration (nicht externe Wheels) | `app/plugins/` | nein |
| **Packaging-Landmarks** | Maschinenlesbare Repo-/Paketkonstanten für Guards und Doku | `app/packaging/` | nein |

**Reifegrad:** Die Spalte Guard-Set markiert, wo **automatisierbare Import-Grenzen** bereits im Test-Config verankert sind. Fehlen bedeutet **nicht** „experimentell“, sondern **noch nicht in `arch_guard_config` aufgenommen** (evolutionärer nächster Schritt). **`app.ui_contracts` (Welle 2):** dokumentierte Stabilitätszonen + Deprecation-Policy + Koordination mit `ui_application` — siehe [`PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](PACKAGE_UI_CONTRACTS_SPLIT_READY.md) §9–11. **Packaging:** nach Cut Wheel `linux-desktop-chat-ui-contracts` mit Import **`app.ui_contracts`** — [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §2.

---

## 3. Packaging, Release und CI (Repo-Spiegel)

| Thema | Pfad / Modul |
|--------|----------------|
| Optional dependencies / Extras | `pyproject.toml` → `[project.optional-dependencies]` |
| Abgleich PEP-621 ↔ Dependency-Gruppen | `linux-desktop-chat-features/src/app/features/dependency_packaging.py` (Modul `app.features.dependency_packaging`) |
| Release-Matrix (Edition × Extras × Smoke) | `linux-desktop-chat-features/src/app/features/release_matrix.py` (Modul `app.features.release_matrix`) |
| CI-Matrix-Validierung | `tools/ci/release_matrix_ci.py` |
| Edition-Smoke (GitHub Actions) | `.github/workflows/edition-smoke-matrix.yml` |
| Interne Plugin-Validierung | `.github/workflows/plugin-validation-smoke.yml` |

---

## 4. Plugins (extern)

| Thema | Ort |
|--------|-----|
| Entry-Point-Gruppe | `linux_desktop_chat.features` (`linux-desktop-chat-features/src/app/features/entry_point_contract.py` → `app.features.entry_point_contract`) |
| Beispiel-Plugin (Repo) | `examples/plugins/ldc_plugin_example/` |
| Autoren-Doku | [`docs/developer/PLUGIN_AUTHORING_GUIDE.md`](../developer/PLUGIN_AUTHORING_GUIDE.md) |

Externe Plugins sind **eigene Distributionen**; sie hängen über Metadata-Entry-Points am Host — nicht über `from app.plugins import …`.

---

## 5. Abgleich: `TARGET_PACKAGES` vs. weitere `app/`-Top-Level-Pakete

Diese Top-Level-Ordner unter `app/` haben ein `__init__.py` und sind **produktiv**, stehen aber **zusätzlich** zu `TARGET_PACKAGES`:

`chat`, `chats`, `commands`, `context`, `devtools`, `global_overlay`, `help`, `llm`, `packaging`, `persistence`, `plugins`, `projects`, `qa`, `workflows`, `workspace_presets`

**Hinweis (Welle 10):** `runtime` und `extensions` (Importe **`app.runtime`** / **`app.extensions`**) sind **keine** Host-Top-Level-Pakete mehr unter `app/`; sie liegen in der eingebetteten Distribution **`linux-desktop-chat-runtime`** (siehe Abschnitt 2 und [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_RUNTIME_PHYSICAL_SPLIT.md)).

**Konsequenz:** Neue Entwicklung soll diese Grenzen respektieren; wer ein **neues** Top-Level-Paket unter `app/` anlegt, muss es in **`app/packaging/landmarks.py`** (`EXTENDED_APP_TOP_PACKAGES`) und hier dokumentieren — sonst schlägt `tests/architecture/test_package_map_contract.py` fehl.

Unterordner **ohne** eigenes `app/<segment>/__init__.py` (z. B. `app/domain/model_usage/`) sind **kein** Top-Level-Segment, bis ein solches Paket angelegt und wie oben erfasst wird.

---

## 6. Brücken, Legacy und Root-Sonderfälle (bewusst)

| Art | Beispiele | Hinweis |
|-----|-----------|---------|
| **Repo-Root-Launcher** | `main.py`, `run_gui_shell.py` | Kanonische GUI: `python -m app`; siehe [`docs/04_architecture/ROOT_ENTRYPOINT_POLICY.md`](../04_architecture/ROOT_ENTRYPOINT_POLICY.md) |
| **Rollenklassifizierte App-Root-Module** | `app/application_release_info.py`, `app/gui_smoke_constants.py`, `app/gui_smoke_harness.py`, `app/qml_alternative_gui_validator.py`, `app/qml_theme_governance.py`, `app/critic.py` | In `TEMPORARILY_ALLOWED_ROOT_FILES` zugelassen; Rollen via `ROOT_FILE_ROLE_CLASSIFICATIONS` / `ROOT_APP_FILE_ROLES` statt pauschal als Rest-Shims |
| **Legacy-GUI** | `archive/run_legacy_gui.py` | Nur Wartung; nicht für neue Features |
| **Parallel-Paket `app/ui/`** | absichtlich nicht wiederbeleben | `FORBIDDEN_PARALLEL_PACKAGES` in `arch_guard_config.py` |
| **GUI-Designer-Assets** | `app/gui_designer_dummy/` | Kein Top-Level-Python-Paket (`__init__.py` fehlt); Designer-Ressourcen |

---

## 7. Segment Dependency Rules

**Zweck:** Kritische **Import-Richtungen** zwischen Top-Segmenten (`app/<segment>/…`) technisch absichern — **klein starten**, verbotsbasiert (`FORBIDDEN_SEGMENT_EDGES`), ohne Whitelist-Explosion.

| Artefakt | Pfad |
|----------|------|
| Regeln | `tests/architecture/segment_dependency_rules.py` — `FORBIDDEN_SEGMENT_EDGES`, `SEGMENT_IMPORT_EXCEPTIONS`, `KNOWN_PRODUCT_SEGMENTS`, `HYBRID_PRODUCT_SEGMENTS`, `IGNORED_SOURCE_SEGMENTS` |
| Test | `tests/architecture/test_segment_dependency_rules.py` (AST, nur absolute `app.*`-Importe) |

**Modell:** Wenn `(Quellsegment, Zielsegment)` in `FORBIDDEN_SEGMENT_EDGES` liegt, ist jeder entsprechende `app.*`-Import ein Verstoß — außer er ist durch `SEGMENT_IMPORT_EXCEPTIONS` (Schlüssel = **Quellmodul** `app….`, Werte = erlaubte Import-Präfixe) abgedeckt.

**Aktive Kern-Verbote (kanonisch im Code — Auszug):**

| Von | Nach | Intention |
|-----|------|-----------|
| services, core, providers, rag, agents, prompts, pipelines | gui | Keine Kopplung der Domäne/Orchestrierung an die PySide-Shell |
| tools, metrics, debug, persistence, workflows, projects, context | gui | Phase 2: Backbone (Hilfen, Telemetrie, Events, ORM, DAGs, Projektdaten, Kontext) bleibt ohne Shell |
| chat, chats, llm, cli | gui | Phase 3A: Domäne / Headless ohne PySide-Paket `app.gui` |
| global_overlay, workspace_presets, ui_application | gui | Hybrid-Restfälle nach Facade-/Port-Entkopplung ohne direkte `app.gui`-Kante |
| features | gui, services, ui_application, ui_runtime | Feature-Plattform bleibt UI-neutral und ohne direkte Service-Schicht |
| gui | providers | Shell nutzt **Services**, nicht direkt Provider (Governance) |

**Hybrid-Segmente:** [SEGMENT_HYBRID_COUPLING_NOTES.md](SEGMENT_HYBRID_COUPLING_NOTES.md) — **governed transition**: `help` und `devtools` bleiben mit dokumentierten GUI-Rändern hybrid; `global_overlay`, `workspace_presets` und `ui_application` bleiben im Hybrid-Katalog, obwohl direkte `app.gui`-Kanten jetzt verboten sind, weil ihr Split noch an Produktstart-/Theme-Verhalten hängt. Dieses Verhalten läuft jetzt kanonisch über `app.core.startup_contract`; zusätzliche Rand-Guards liegen in `test_ui_layer_guardrails.py`.

**Bewusst noch nicht auf „→ gui“ geprüft:** siehe unten **Phase 3 — Konsolidierung** (restliche neutrale Segmente).

### Phase 3 — Konsolidierung (Vorbereitung, Stand Analyse)

Ist-Prüfung: statische `from app.gui…` / `import app.gui…` unter `app/<segment>/` (ohne dynamische Imports).

| Segment | Einordnung | `app.gui.*` heute? | Hinweis für Guard / Modell |
|---------|------------|-------------------|----------------------------|
| chat | produktiv, Domäne | nein | **Phase 3A aktiv:** `(chat, gui)` |
| chats | produktiv | nein | **Phase 3A aktiv:** `(chats, gui)` |
| cli | infra, headless | nein | **Phase 3A aktiv:** `(cli, gui)` |
| commands | support (Befehle) | nein | Optional später; geringere Priorität als Domäne |
| devtools | support, **UI-nah** | **ja** (nur `app.gui.themes.*`) | Hybrid mit hartem Theme-Rand; Guard in `test_ui_layer_guardrails.py` |
| extensions | infra, Hooks | nein | Optional, nach Nutzungsbild |
| global_overlay | produktiv, **Shell-Brücken** | nein (direkte `app.gui.*` entfernt; Produktstart über `core.startup_contract`) | `(global_overlay, gui)` aktiv; Split-Blocker reduziert auf Produktstart-/Overlay-Ports |
| help | produktiv, **UI-hybrid** | **ja** (nur `help/ui_components.py`) | GUI-nahe Markdown-Schicht bleibt bewusst lokal begrenzt |
| llm | produktiv, Fähigkeit | nein | **Phase 3A aktiv:** `(llm, gui)` |
| plugins | host-intern | nein | Optional; Abgrenzung zu externen Plugins beachten |
| qa | support, Read-only-Adapter | nein | Mittlere Priorität |
| runtime | infra | nein | Kandidat mittlerer Priorität |
| workspace_presets | produktiv, **Workspace/GUI** | nein (direkte `app.gui.*` entfernt) | `(workspace_presets, gui)` aktiv; Produkt-Facade + `core.navigation` statt Shell-Modul |
| ui_contracts | UI-Schicht, Qt-frei | nein | Kandidat; Zielarchitektur: weiter ohne `gui` |
| ui_application | Presenter/Adapter | nein (Theme über `core.startup_contract`) | `(ui_application, gui)` aktiv; Presenter weiter ohne Shell-Widgets halten |
| ui_runtime | QML/Runtime | nein | Vorsicht: parallel zur PySide-Shell; Policy vor pauschalem `→ gui` |
| ui_themes | Assets | nein | Geringere Dringlichkeit |
| packaging | meta (Landmarks) | nein | Eher ignorieren oder nur Dokumentation |

**Phase 3A umgesetzt:** `(chat, gui)`, `(chats, gui)`, `(llm, gui)`, `(cli, gui)` — Ist-Scan ohne `app.gui`-Substring in diesen Bäumen; **keine** neuen `SEGMENT_IMPORT_EXCEPTIONS`.

**Hybrid-Härtung umgesetzt:** `(global_overlay, gui)`, `(workspace_presets, gui)`, `(ui_application, gui)` — direkte `app.gui.*`-Importe entfernt; produktweiter Startup-/Theme-Zugriff läuft kanonisch über `app.core.startup_contract`; zusätzliche Guardrails verbieten Rückfälle auf die entfernten Root-Shims `app.gui_bootstrap`, `app.gui_registry`, `app.gui_capabilities`.

**Bewusst hybrid mit schmalem GUI-Rand:** `devtools`, `help` — siehe [SEGMENT_HYBRID_COUPLING_NOTES.md](SEGMENT_HYBRID_COUPLING_NOTES.md).

**Status frueherer Ausnahmen:** Die fruehere Bruecke `app.core.context.project_context_manager` → `app.gui.events…` ist entfernt; Projektkontext-Events laufen kanonisch ueber `app.core.context.project_context_events`, waehrend `app.gui.events.project_events` nur den GUI-kompatiblen Adapterpfad behaelt. Der Projekt-Lookup laeuft fuer `ProjectContextManager` ausserdem ueber einen injizierbaren Core-Loader statt ueber direkten `app.services.project_service`-Import.

**Hinweis:** Zusätzlich gelten die feineren Regeln in `tests/architecture/arch_guard_config.py` / `test_app_package_guards.py`. Segment-Guard und Package-Guards **ergänzen** sich.

---

## 8. Git- und QA-Governance (Commit-Bezug)

Formal abnahmefähige Aussagen sollen **Commit und Branch** kennen; Dirty-Working-Trees werden sichtbar und downgraden starke Claims ohne lokale Arbeit zu blockieren — siehe [`GIT_QA_GOVERNANCE.md`](GIT_QA_GOVERNANCE.md), Code unter `app/qa/git_context.py`, `git_provenance.py`, `git_governance.py`.

---

## 9. Governance-Vorbereitung (nächste Schritte)

1. **Landmarks:** `app/packaging/landmarks.py` enthält maschinenlesbare Pfade und erweiterte Top-Pakete — Grundlage für strengere „allowed dependency“-Guards.  
2. **Repo-Split:** Vor physischem Cut [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) pflegen (Matrix, Blocker, Wellen); Hybrid-Segmente zuerst entblocken.  
3. **Erweiterung `TARGET_PACKAGES`:** Nur nach Architektur-Review und Ergänzung der Import-Regeln in `arch_guard_config.py`.  
4. **GitHub:** Labels/Boards können an Segmente aus Abschnitt 2 gekoppelt werden (Konvention, kein Zwang).

---

## 10. Änderungshistorie (manuell)

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste kanonische Landkarte; Verknüpfung mit `arch_guard_config`, `landmarks.py`, Plugin- und CI-Pfaden |
| 2026-03-25 | Segment-Dependency-Rules + AST-Test (`segment_dependency_rules.py`, `test_segment_dependency_rules.py`) |
| 2026-03-25 | Phase 2: Backbone-Segmente → `gui` ergänzt (`tools`, `metrics`, `debug`, `persistence`, `workflows`, `projects`, `context`); `tools` in `KNOWN_PRODUCT_SEGMENTS` |
| 2026-03-25 | Phase 3-Vorbereitung: Tabelle neutraler Segmente + Kandidaten (`chat`, `chats`, `llm`, `cli`) ohne neue `FORBIDDEN_SEGMENT_EDGES` |
| 2026-03-25 | Phase 3A: vier Kanten `chat|chats|llm|cli` → `gui`; Hybrid-Notiz `SEGMENT_HYBRID_COUPLING_NOTES.md`; `chats`/`cli`/`llm` in `KNOWN_PRODUCT_SEGMENTS` |
| 2026-03-25 | Hybrid-Notiz konkretisiert: Ist-Imports, Soll-Präfixe, Root-Brücken, Guard-Strategie (nur Doku) |
| 2026-03-29 | Hybrid-Härtung: kanonischer Produktvertrag `app.core.startup_contract`; `global_overlay`/`workspace_presets` ohne Root-Facades, `workspace_presets` auf `core.navigation.NavArea`, `ui_application` Theme über Core-Contract; Root-Dateien `gui_bootstrap`/`gui_registry`/`gui_capabilities` entfernt; neue Guardrails gegen Rückfälle auf die entfernten Root-Shims |
| 2026-03-25 | Repo-Split-Readiness: `PACKAGE_SPLIT_PLAN.md`, Kurzabschnitt in § 1, Verweise in § 9 / Verwandte Dokumente |
| 2026-03-25 | `PACKAGE_WAVE1_PREP.md`: konkrete Welle-1-Vorbereitung (features / ui_contracts) |
| 2026-03-25 | `PACKAGE_FEATURES_CUT_READY.md`: DoR und öffentliche API für `app.features` |
| 2026-03-25 | `PACKAGE_FEATURES_PHYSICAL_SPLIT.md`: verbindliche Pfad-/Packaging-Entscheidung für ersten Cut |
| 2026-03-25 | `linux-desktop-chat-features/`: eingebettete Repo-Vorlage Commit 1 |
| 2026-03-25 | `PACKAGE_UI_CONTRACTS_SPLIT_READY.md`: API-Stabilisierung `app.ui_contracts`, Guard `test_ui_contracts_public_surface_guard` |
| 2026-03-25 | `PACKAGE_UI_CONTRACTS_SPLIT_READY.md`: SemVer-/Stabilitätszonen, Deprecation-Policy, Kopplung `ui_application` (§9–11) |
| 2026-03-25 | `app.ui_contracts.common.errors.SettingsErrorInfo` — Fan-in-Blocker reduziert (siehe `PACKAGE_UI_CONTRACTS_SPLIT_READY.md` §7) |
| 2026-03-25 | UI-Contracts-Tests: Chat gegen Root-API entkoppelt wo möglich (`PACKAGE_UI_CONTRACTS_SPLIT_READY.md` §3.2) |
| 2026-03-25 | [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md): Welle-2-Split-Prep für `app.ui_contracts` |
| 2026-03-25 | [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md): Welle 3 — Split-Readiness `app.pipelines` (ohne physischen Cut) |
| 2026-03-25 | `test_pipelines_public_surface_guard.py`: kanonische `app.pipelines`-Importpfade; Verwandte-Dokumente angepasst |
| 2026-03-25 | [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md): Definition of Ready for Cut `app.pipelines` (ohne physischen Split) |
| 2026-03-25 | [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md): Packaging `linux-desktop-chat-pipelines` → `app.pipelines` (Variante B) |
| 2026-03-25 | `linux-desktop-chat-pipelines/`: Commit-1-Vorlage Welle 3; Verwandte-Dokumente §0 |
| 2026-03-25 | [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md): DoR für physischen Split `ui_contracts` |
| 2026-03-25 | [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md): verbindliche Packaging-/Importpfad-Entscheidung (Variante B) |
| 2026-03-25 | Welle 5: `app.cli` → `linux-desktop-chat-cli`; `TARGET_PACKAGES`/`cli`; [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md) |
| 2026-03-25 | Welle 5 **abgeschlossen**: Tabelle §2 CLI-Status; Verwandte-Dokumente §0 — [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md) |
| 2026-03-26 | Phase A: kanonische Segment-Wahrheit, `HYBRID_PRODUCT_SEGMENTS`, Hybrid-Doku als „governed transition“, Hinweis Unterordner ohne Top-Level-`__init__.py` |
| 2026-03-26 | Welle 6: `app.utils` → `linux-desktop-chat-utils`; Host-`app/utils/` entfernt; [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](PACKAGE_UTILS_PHYSICAL_SPLIT.md) |
| 2026-03-26 | Welle 7: `app.ui_themes` → `linux-desktop-chat-ui-themes`; Host-`app/ui_themes/` entfernt; [`PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`](PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md) |
| 2026-03-26 | Welle 8: `app.ui_runtime` → `linux-desktop-chat-ui-runtime`; Host-`app/ui_runtime/` entfernt; [`PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md) |
| 2026-03-26 | Welle 9: `app.debug` / `app.metrics` / `app.tools` → `linux-desktop-chat-infra`; Host-`app/debug/`, `app/metrics/`, `app/tools/` entfernt; [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](PACKAGE_INFRA_PHYSICAL_SPLIT.md) |
| 2026-03-26 | Welle 10: `app.runtime` / `app.extensions` → `linux-desktop-chat-runtime`; Host-`app/runtime/`, `app/extensions/` entfernt; [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_RUNTIME_PHYSICAL_SPLIT.md) |
