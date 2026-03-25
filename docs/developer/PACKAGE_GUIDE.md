# Leitfaden: Pakete, Grenzen und Repo-Orientierung

Dieses Dokument ergänzt [`docs/DEVELOPER_GUIDE.md`](../DEVELOPER_GUIDE.md) um die **sichtbare Paketarchitektur**: wo neuer Code hingehört, wie Host vs. externe Plugins getrennt sind, und welche Checks die Struktur absichern.

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
| **Pipeline-Engine / Executors** (`app.pipelines`) anfasst | `linux-desktop-chat-pipelines/src/app/pipelines/` (Distribution `linux-desktop-chat-pipelines`; [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](../architecture/PACKAGE_PIPELINES_COMMIT2_LOCAL.md), Abschluss [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](../architecture/PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md)) |
| **RAG** implementierst | `app/rag/` (Abhängigkeit: Extra `rag` in `pyproject.toml`) |
| **Agenten** erweiterst | `app/agents/` |
| **kontext- oder chat-spezifische** Logik ohne Qt brauchst | `app/chat/`, `app/context/` |
| **kopflose** Werkzeuge schreibst | `app/cli/` |
| ein **externes** installierbares Plugin lieferst | eigenes Paket + Entry-Point `linux_desktop_chat.features` (siehe [`PLUGIN_AUTHORING_GUIDE.md`](PLUGIN_AUTHORING_GUIDE.md)) |

**Hinweis:** Nicht jedes sinnvolle Unterpaket ist bereits in `TARGET_PACKAGES` (`arch_guard_config.py`) für Import-Guards erfasst. Neue Top-Level-Pakete unter `app/` lösen einen Konsistenztest aus, bis sie in `app/packaging/landmarks.py` dokumentiert sind (siehe unten).

### Segment-Abhängigkeiten (Kern)

- **Erlaubt typischerweise:** `gui` importiert `services`, `core`, `features`, … (siehe Ist-Code); **nicht** direkt `providers`.  
- **Verboten (Guard):** u. a. `services`/`core`/Domänen-Segmente → `gui`; **Phase 2** Backbone → `gui`; **Phase 3A** `chat`, `chats`, `llm`, `cli` → `gui`; `features` → `gui` / `services` / `ui_application` / `ui_runtime`; `gui` → `providers`. Hybrid-Segmente (Ist/Soll je Segment, Root-Brücken `gui_registry`/`gui_bootstrap`/`gui_capabilities`): [SEGMENT_HYBRID_COUPLING_NOTES.md](../architecture/SEGMENT_HYBRID_COUPLING_NOTES.md).  
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
| `tests/architecture/test_package_map_contract.py` | Repo-Landmarken existieren; erweiterte `app/`-Pakete sind dokumentiert; Entry-Point-Gruppe konsistent |
| `tests/architecture/test_segment_dependency_rules.py` | Verbotskanten zwischen Segmenten + dokumentierte Ausnahmen (`segment_dependency_rules.py`) |
| `tests/architecture/test_app_package_guards.py` | Import-Richtungen, App-Root-Dateien, Navigation |
| `tests/architecture/test_ui_contracts_public_surface_guard.py` | Keine `_*`-Symbol-Imports aus `app.ui_contracts` im Repo-Tree außerhalb des Pakets (Submodule-Pfade bleiben erlaubt) |
| `tests/architecture/test_pipelines_public_surface_guard.py` | `app.pipelines`: nur Root oder `app.pipelines.{models,engine,services,executors,registry}` außerhalb des Paket-Quellsegments; keine `_*`-Imports von außen |
| `tests/architecture/test_architecture_map_contract.py` | Architecture Map Validator |

## CI und Editionen

Matrix und Validierung: `tools/ci/release_matrix_ci.py`, Workflows unter `.github/workflows/`. Edition-Umgebungsvariable: `LDC_EDITION` (siehe `app.features.edition_resolution`). In CI ist zusätzlich **`LDC_REPO_ROOT`** auf den Checkout-Root gesetzt (Details: [`PACKAGE_FEATURES_COMMIT3_CI.md`](../architecture/PACKAGE_FEATURES_COMMIT3_CI.md)).
