# Repo-Split-Readiness und Zielpaketplan

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Vorbereitungs**doku — **kein** physischer Repo-Split, keine neuen GitHub-Repos  
**Bezug:** [`PACKAGE_MAP.md`](PACKAGE_MAP.md) (**kanonische** Segment-Identität und **aktuelle** Quellpfade), [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md) (konkrete Extraktions-Checkliste), [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md), `app/packaging/landmarks.py`, `tests/architecture/arch_guard_config.py`, `tests/architecture/segment_dependency_rules.py`

---

## 1. Zweck und Abgrenzung

Dieses Dokument beschreibt **Split-Fähigkeit**: welche Segmente später als eigene Repos/Pakete Sinn ergeben, welche im Host bleiben, und welche **Hybrid-Kopplungen** vor einem Cut bereinigt werden müssen. Es ergänzt die Segment-Governance um eine **operative Split-Matrix** und Blockerliste.

---

## 2. Verbindliche Paketklassifikation (produktive `app/`-Top-Level-Segmente)

Jedes Segment mit `app/<segment>/__init__.py` (inkl. `TARGET_PACKAGES` und `EXTENDED_APP_TOP_PACKAGES`) fällt in genau eine Klasse:

| Klasse | Bedeutung |
|--------|-----------|
| **A — Künftiges Zielpaket** | Eignet sich perspektivisch als **eigenes** installierbares Paket und/oder eigenes Repo (allein oder in einem Bündel). |
| **B — Produktintern / vorerst Host** | Bleibt im **Host** (`linux-desktop-chat`); Split lohnt sich nicht oder wäre rein organisatorisch ohne klare API. |
| **C — Hybrid / vor Split bereinigen** | Inhaltlich sinnvoll abgrenzbar, aber **Ist-Kopplung** an `gui`/Produktstartverhalten muss vor dem Cut auf Ports/Contracts reduziert werden (siehe Hybrid-Notiz). |

| Segment | Klasse | Kurzbegründung |
|---------|--------|----------------|
| `features` | **A** | Feature-Plattform, Entry-Point-Vertrag, bewusst UI-neutral (`features` → `gui` verboten). |
| `core` | **A** | Konfiguration, DB, Modelle, Navigationsdaten; Ziel: Qt-frei (Guards). |
| `gui` | **A** | PySide-Shell; größtes Paket, höchste Kopplung **nach innen** (viele Importe von außen). |
| `services` | **A** | Orchestrierung; darf `gui` nicht importieren (Governance). |
| `agents`, `rag`, `prompts`, `providers`, `pipelines` | **A** | Fähigkeits-Segmente mit klaren Rändern in `arch_guard_config`. |
| `llm` | **A** (Bündel mit `core` prüfen) | Zielbild: Teile nach `core`; eigenes Repo nur sinnvoll, wenn LLM-Schicht explizit versioniert werden soll. |
| `chat`, `chats`, `context` | **A** | Chat-/Kontext-Domäne; keine pauschale `→ gui`-Kante (Phase 3A). |
| `workflows`, `projects`, `persistence` | **A** | Daten-/Ablauf-Ebene; für Split oft **gemeinsam** mit `core`/`services` abstimmen. |
| `cli` | **A** | Headless; technisch gut abtrennbar. |
| `utils` | **A** | Blatt-Segment; Split technisch einfach, ökonomisch klein. |
| `ui_contracts` | **A** | Qt-frei; starke Kandidatin für frühe Extraktion. |
| `ui_themes` | **A** | Asset-Paket; wenig Python-Kopplung. |
| `ui_runtime` | **A** | QML/Runtime parallel zur Shell — eigenes Repo möglich, Policy vor breitem `gui`-Bezug klären. |
| `ui_application` | **C** | Presenter/Adapter; direkte `app.gui.themes`-Kante entfernt, Produkt-Theme jetzt ueber `app.core.startup_contract`, aber Presenter-/Produktgrenze bleibt Split-Thema. |
| `debug`, `metrics`, `tools` | **A** (phys. **Welle 9:** `linux-desktop-chat-infra`) | Eingebettete Distribution **`linux-desktop-chat-infra`** (`app.debug`, `app.metrics`, `app.tools`); Host-`app/debug/`, `app/metrics/`, `app/tools/` entfernt — [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](PACKAGE_INFRA_PHYSICAL_SPLIT.md). |
| `commands` | **B** | Erweiterungen der Kommandopalette; eng mit Nav/Core verbunden. |
| `extensions`, `runtime` | **A** (phys. **Welle 10**) | Eingebettete Distribution **`linux-desktop-chat-runtime`** (`app.runtime`, `app.extensions`); weiterhin kein eigenständiges Library-Publikum ohne Host. |
| `plugins` | **B** | **Interne** Plugin-Hilfen; externe Plugins bleiben **eigene** Distributionen (bereits modelliert). |
| `qa` | **B** | In-App-QA und Berichte; kann später mit Host-CI teilen, nicht als Library sinnvoll. |
| `packaging` | **B** | Meta (`landmarks`, Doku-Verweise); **muss** im Host (oder Build-Repo) bleiben. |
| `global_overlay` | **C** | Produktstart, Registry, Theme-Rescue; direkte `app.gui`-Kanten entfernt, jetzt ueber `app.core.startup_contract` gebuendelt. |
| `workspace_presets` | **C** | Persistenz/Validierung; `NavArea` auf `core.navigation` verschoben, Produktstart-/Theme-Zugriffe ueber `app.core.startup_contract`. |
| `help` | **C** | Nutzt `gui.components` / `shared.markdown` — fachlich „Help-UI“, nicht reine Library. |
| `devtools` | **C** | Bewusst nur `gui.themes.*`; Grenze muss **hart** bleiben. |

### 2.1 Phase-A-Reifeklassen (Doku- und Guard-Alignment)

Klassifikation für **Split-/Modulgrenzen** (nicht Feature-Vollständigkeit). Detailbegründungen: [`PACKAGE_MAP.md`](PACKAGE_MAP.md), Hybrid: [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md).

| Klasse | Segmente (Gruppen) |
|--------|-------------------|
| **READY** | `features`, `pipelines`, `providers`, `utils` (**Welle 6:** `linux-desktop-chat-utils`), `debug`, `metrics`, `tools` (**Welle 9:** `linux-desktop-chat-infra`), `runtime`, `extensions` (**Welle 10:** `linux-desktop-chat-runtime`), `packaging` (Meta) |
| **NEAR READY** | `ui_contracts`, `cli`, `services`, `agents`, `rag`, `prompts`, `ui_runtime`, `ui_themes`, Chat/Kontext (`chat`, `chats`, `context`), Workspace-Daten (`workflows`, `projects`, `persistence`, `llm`), Host-intern (`commands`, `plugins`, `qa`) |
| **NOT READY** | `core`, `gui` |
| **HYBRID** (transitional) | `ui_application`, `global_overlay`, `workspace_presets`, `help`, `devtools` — maschinenlesbar `HYBRID_PRODUCT_SEGMENTS` in `segment_dependency_rules.py` |

---

## 3. Künftige Zielpakete (logische Repos) — API, Interna, Abhängigkeiten, Reife

Namen sind **Arbeitsnamen** (PyPI/Repo-Name folgt Release-Policy). „Direkt erlaubt“ = fachlich und heute durch Guards/Struktur **tragbar**; keine Vollständigkeit aller transitiven Imports.

### 3.1 `ldc-features` ← `app/features`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Editionen, Feature-Registry, Discovery, Release-Matrix, PEP-621-Abgleich, Entry-Point-Gruppe für **externe** Plugins. |
| **Wahrscheinliche öffentliche API** | `FeatureDescriptor`, Registry-/Discovery-Funktionen, `ENTRY_POINT_GROUP`, Release-Matrix-Typen (stabil dokumentieren). |
| **Nicht exportieren** | Interne Validierungshelfer, CI-only Pfade, ad-hoc Skript-Schnittstellen. |
| **Direkt erlaubte Paketabhängigkeiten** | Stdlib + explizit deklarierte kleine Utilities; **kein** `gui`, `services`, `ui_application`, `ui_runtime` (Segment-Guard). |
| **Split-Reife** | **Hoch** |

### 3.2 `ldc-core` ← `app/core` (+ ggf. Teile von `app/llm`)

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Konfiguration, DB, Domänenmodelle, Navigations-**Daten**, Commands-Daten, Projekt-Kontext (ohne Qt). |
| **Öffentliche API** | Settings- und DB-Fassaden, ModelRegistry/Orchestrator-Schnittstellen, Navigation-IDs/DTOs (nach Konsolidierung). |
| **Nicht exportieren** | Einzelfunktionen mit bekannten Brücken (z. B. `project_context_manager` → `gui.events` — Follow-up Port). |
| **Direkt erlaubt** | `utils`; keine `gui`, `services`, `features`, `rag`, … (siehe `FORBIDDEN_IMPORT_RULES`). |
| **Split-Reife** | **Mittel** (Brücken + Umfang) |

### 3.3 `ldc-gui` ← `app/gui`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | PySide6-Shell, Domains, Workspaces, Themes, Navigation-UI, Registrierung eingebauter Features. |
| **Öffentliche API** | Minimal halten: gezielte Hooks für Host/Plugins (bereits Entry-Points); keine „alles aus `gui.domains`“. |
| **Nicht exportieren** | Interne Panel-Implementierungen, Workbench-Details (Konsumenten über Services/Contracts). |
| **Direkt erlaubt** | `core`, `services`, `agents`, `rag`, `prompts`, `features` (über Registrare, nicht umgekehrt), `utils`, `debug`, `metrics`, `tools`, `ui_contracts`/`ui_application`/`ui_runtime`/`ui_themes` je nach Produktentscheid. **Kein** direkter `providers` (Guard). |
| **Split-Reife** | **Niedrig** (Größe, Zentralität, viele eingehende Kanten) |

### 3.4 `ldc-services` ← `app/services`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Orchestrierung Chat/Knowledge/Modelle/Projekte/QA-Governance etc. |
| **Öffentliche API** | Kanonische Service-Module (`CANONICAL_SERVICE_MODULES` in `arch_guard_config`) als stabile Fassade. |
| **Nicht exportieren** | Experimentelle Adapter, GUI-spezifische Hacks (sollten null sein). |
| **Direkt erlaubt** | `core`, `agents`, `rag`, `prompts`, `providers`, `pipelines`, … **nicht** `gui`. |
| **Split-Reife** | **Mittel** |

### 3.5 `ldc-capabilities` (Bündel) ← `agents`, `rag`, `prompts`, `providers`, `pipelines`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Fachliche Fähigkeiten ohne Shell. |
| **Öffentliche API** | Provider-Interfaces, RAG-Service-Einstieg, Prompt-Repository-API, Pipeline-Engine-Front. |
| **Nicht exportieren** | Executor-Interna, Registry-Implementierungsdetails bis stabil. |
| **Direkt erlaubt** | Untereinander gemäß Guards; typisch `core`/`utils`; kein `gui`. |
| **Split-Reife** | **Mittel** (Aufteilung in mehrere Repos möglich, erhöht Release-Overhead) |

**Teilsegment `app.pipelines`:** technische Insel und Welle-3-Fokus — Analyse/Public Surface [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md); DoR [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md); **Physischer Split (Variante B):** [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) (`linux-desktop-chat-pipelines` → `app.pipelines`).

### 3.6 `ldc-chat-domain` ← `chat`, `chats`, `context`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Chat-/Kontext-Fachlogik ohne PySide. |
| **Öffentliche API** | Service-/DTO-Schnittstellen, die `services` und `gui` nutzen. |
| **Nicht exportieren** | Alles unter `context/devtools` o. Ä., was nur interne Diagnose ist. |
| **Direkt erlaubt** | `core`, `utils`; Richtung zu `gui` bewusst nicht in Segment-Verbotsliste für alle Unterpfade — Split-Design muss **explizite** API festlegen. |
| **Split-Reife** | **Mittel** |

### 3.7 `ldc-workspace-data` ← `workflows`, `projects`, `persistence`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | DAGs, Projekt-Lebenszyklus, ORM/Persistenz. |
| **Öffentliche API** | Repository-/Workflow-Runner-Interfaces. |
| **Nicht exportieren** | Ad-hoc SQL, GUI-getriebene Persistenzpfade. |
| **Direkt erlaubt** | `core`, `utils`; keine `gui` (Phase-2-Segment-Regel). |
| **Split-Reife** | **Mittel** |

### 3.8 `ldc-ui` ← `ui_contracts`, `ui_application`, `ui_runtime`, `ui_themes`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Verträge, Presenter, QML-Runtime, Theme-Assets. |
| **Öffentliche API** | `ui_contracts` öffentlich; `ui_application` Ports/Adapter selektiv; Runtime/Themes nach Consumer-Dokumentation. |
| **Nicht exportieren** | Alles, was direkt `gui.domains`/`shell` anfasst (Soll: vermeiden). |
| **Direkt erlaubt** | `ui_contracts`: am strengsten Qt-frei/feature-frei; `ui_application`: produktweiter Theme-/Startup-Zugriff jetzt über `app.core.startup_contract` — vor Split weiter verengen. |
| **Split-Reife** | **ui_contracts:** technische Extraktion **hoch**, Release-/Ökosystem für physischen Cut **mittel** ([`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md) §6); **Importpfad/Packaging entschieden** ([`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §2) · **ui_application: mittel (Hybrid)** · **ui_runtime/ui_themes: mittel** |

### 3.9 `ldc-cli` ← `app.cli` (Quelle: `linux-desktop-chat-cli/`)

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Kopflose Werkzeuge. |
| **Quellort** | Eingebettete Distribution [`linux-desktop-chat-cli/`](../linux-desktop-chat-cli/) — **kein** `app/cli/` mehr im Host-Tree; Namespace `app.cli` via `pkgutil.extend_path`. |
| **Öffentliche API** | CLI-Entry-Commands, stabile Flags. |
| **Nicht exportieren** | Interne Test-Harnesses. |
| **Direkt erlaubt** | `core`, `services`, Domänen — **nicht** `gui` (Phase 3A; siehe `FORBIDDEN_IMPORT_RULES` / Segment-Guard). |
| **Split-Reife** | **NEAR READY** — technisch extrahiert; vollständige Eigenständigkeit des Wheels hängt u. a. von Host-Modulen wie `app.context.replay.*` ab (siehe §6.4). |

### 3.10 `ldc-product-startup` (Arbeitsname) ← `global_overlay`, `workspace_presets`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Produktstart, Overlay, Preset-Persistenz, Theme-/GUI-ID-Kompatibilität. |
| **Öffentliche API** | Schmale Ports (`overlay_*_port`, Preset-APIs), keine direkte Exposition aller Dialoge. |
| **Nicht exportieren** | Watchdog-Interna, Diagnose-Dialoge als „öffentlich“ deklarieren. |
| **Direkt erlaubt** | `app.core.startup_contract`, geführter Theme-Zugriff; **Ziel:** kein `gui.navigation` aus Presets. |
| **Split-Reife** | **Niedrig** — zuerst Hybrid bereinigen. |

### 3.11 `ldc-help`, `ldc-devtools`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Eingebettete Hilfe bzw. Theme-Diagnose. |
| **Öffentliche API** | Minimal (Host öffnet Fenster); ggf. DTOs für Doc-Pfade. |
| **Nicht exportieren** | Widget-Interna. |
| **Direkt erlaubt** | Help: nur dokumentierte `gui.components`/`shared.markdown`-Schicht; DevTools: nur `gui.themes.*`. |
| **Split-Reife** | **Help: mittel** · **Devtools: mittel–niedrig** (solange Grenze schmal bleibt) |

### 3.12 Host-Bündel (kein eigenes „Produkt-Library“-Repo in Welle 1)

`debug`, `metrics`, `tools` — **Welle 9:** eingebettete Distribution **`linux-desktop-chat-infra`** (Importe `app.debug`, `app.metrics`, `app.tools`); siehe [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](PACKAGE_INFRA_PHYSICAL_SPLIT.md). **`runtime`**, **`extensions`** — **Welle 10:** eingebettete Distribution **`linux-desktop-chat-runtime`** (Importe `app.runtime`, `app.extensions`); siehe [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_RUNTIME_PHYSICAL_SPLIT.md). **`commands`**, **`plugins`**, **`qa`**, **`packaging`** bleiben **im Host-Repo** oder wandern erst in **spätere** Wellen. **`packaging`** bleibt notwendigerweise beim Build/Host.

---

## 4. Repo-Split-Matrix (Ist-Pfade → Ziel)

| Segment / Bündel | Heutiger Pfad | Künftiger Repo-/Paketname (Arbeit) | Direkte Paketabhängigkeiten (Zielbild) | CI-/Testscope (pragmatisch) | Bemerkungen / Blocker |
|------------------|---------------|-------------------------------------|----------------------------------------|-----------------------------|------------------------|
| `features` | `linux-desktop-chat-features/src/app/features/` → `app.features` | `ldc-features` | stdlib + kleine, explizit gelistete Deps; keine UI/Services | `pytest tests/architecture/` (Guards) + Feature-/Edition-Matrix (`edition-smoke-matrix`, `release_matrix_ci`) | **Geringer Blocker**; API-Dokumentation für öffentliche Symbole |
| `utils` | `linux-desktop-chat-utils/src/app/utils/` → `app.utils` | `linux-desktop-chat-utils` / `ldc-utils` | stdlib only (Guard) | Unit-Tests + `test_utils_public_surface_guard` | **Welle 6** umgesetzt; [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](PACKAGE_UTILS_PHYSICAL_SPLIT.md) |
| `ui_contracts` | `linux-desktop-chat-ui-contracts/src/app/ui_contracts/` → `app.ui_contracts` | **`linux-desktop-chat-ui-contracts`** | stdlib / typing-only wo möglich | Architekturtests + Verbraucher-Tests in `ui_application` | **Wenig technische Blocker**; Cut-Ready: [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md); Packaging: [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) |
| `ui_themes` | `linux-desktop-chat-ui-themes/src/app/ui_themes/` → `app.ui_themes` | `linux-desktop-chat-ui-themes` | keine Python-Deps (Assets + package-data) | Architekturtests + `test_ui_themes_public_surface_guard` | **Welle 7** umgesetzt; [`PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`](PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md) |
| `ui_runtime` | `linux-desktop-chat-ui-runtime/src/app/ui_runtime/` → `app.ui_runtime` | `linux-desktop-chat-ui-runtime` | `jsonschema`, `PySide6`; Laufzeit: Host (`ui_contracts`, `core`, `ui_application`) | Architekturtests + `test_ui_runtime_public_surface_guard` + QML-Smokes | **Welle 8** umgesetzt; [`PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md) |
| `cli` | `linux-desktop-chat-cli/src/app/cli/` → `app.cli` | `linux-desktop-chat-cli` / `ldc-cli` | `core`, `services`, Domänen (Host); **nicht** `gui` | CLI-Smoke falls vorhanden; `test_cli_public_surface_guard` | Laufzeit u. a. `app.context.replay.*` auf Host — siehe §6.4 |
| `core` | `app/core/` | `ldc-core` | `utils`; ggf. `llm` intern | Breite `tests/unit/**` + Architektur | **project_context_manager → gui** (Port) |
| `llm` | `app/llm/` | Teil von `ldc-core` oder eigenes Paket | Abstimmung mit Zielbild APP_TARGET_PACKAGE | Unit-Tests + Guards | Duplikation mit `core/llm` im Zielbild beachten |
| `services` | `app/services/` | `ldc-services` | `core`, Fähigkeits-Pakete | Service-Unit-Tests, Architektur | Stabile Fassaden dokumentieren |
| `providers`, `rag`, `prompts`, `agents`, `pipelines` | `rag`, `prompts`, `agents`: `app/{rag,prompts,agents}/`; `providers`: `linux-desktop-chat-providers/…` → `app.providers`; `pipelines`: `linux-desktop-chat-pipelines/…` → `app.pipelines` | `ldc-capabilities` (mono) oder 2–3 Repos | gemäß `FORBIDDEN_IMPORT_RULES` | Fach-Tests pro Bereich + Architektur | Aufteilung = Release-Mehraufwand; **`pipelines`/`providers`** bereits als Wheels — [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md), [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) |
| `chat`, `chats`, `context` | `app/chat/`, `chats/`, `context/` | `ldc-chat-domain` | `core`, `utils` | `tests/` mit Markern je nach Suite | Öffentliche Domänen-API definieren |
| `workflows`, `projects`, `persistence` | `app/workflows/`, `projects/`, `persistence/` | `ldc-workspace-data` | `core`, `utils` | Persistenz-/Workflow-Tests | Migration/ORM an Host-Editionen |
| `gui` | `app/gui/` | `ldc-gui` | `core`, `services`, `features`-Registrare, `ui_*`, … | `tests/ui/`, GUI-Smokes, Architektur-Domänen-Guards | **Größter Blocker**: Zentralität, Legacy, Ressourcen |
| `ui_application`, `ui_runtime`, `ui_themes` | Host: `app/ui_application/`; eingebettet: `linux-desktop-chat-ui-runtime/src/app/ui_runtime/` → `app.ui_runtime` (**Welle 8**); `linux-desktop-chat-ui-themes/src/app/ui_themes/` → `app.ui_themes` (**Welle 7**) | `ldc-ui` (Arbeitsname; Runtime/Themes bereits extrahiert) | `ui_contracts`; **kein** breites `gui` nach Bereinigung | Presenter-/QML-Tests | `ui_application` nutzt Produkt-Theme jetzt ueber `app.core.startup_contract` |
| `global_overlay` | `app/global_overlay/` | `ldc-product-startup` (mit Presets) | `app.core.startup_contract` + Theme-/GUI-Port | Smoke/Startup-Tests, Watchdog | direkte `app.gui`-Kanten und Root-Facades entfernt; Produkt-Orchestrierung bleibt Blocker |
| `workspace_presets` | `app/workspace_presets/` | (wie oben) | `app.core.startup_contract`, `core.navigation`; **nicht** `gui.navigation` | Preset-/Settings-Tests | direkte `app.gui`-Kanten und Root-Facades entfernt; Aktivierungslogik bleibt Blocker |
| `help` | `app/help/` | `ldc-help` | schmale `gui.components` oder Port | UI-Tests falls vorhanden | Abhängigkeit von Shell-Widgets |
| `devtools` | `app/devtools/` | `ldc-devtools` | nur `gui.themes.*` | Theme-/Visualizer-Tests | Jeder neue Import außerhalb `themes` = Blocker |
| `debug`, `metrics`, `tools` | `linux-desktop-chat-infra/src/app/{debug,metrics,tools}/` → `app.{debug,metrics,tools}` | `linux-desktop-chat-infra` | `PySide6`; Laufzeit: `app.utils` (Host/utils-Wheel) | Architektur + EventBus-Guards + `test_infra_public_surface_guard` | **Welle 9** — [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](PACKAGE_INFRA_PHYSICAL_SPLIT.md) |
| `runtime`, `extensions` | `linux-desktop-chat-runtime/src/app/{runtime,extensions}/` → `app.runtime`, `app.extensions` | `linux-desktop-chat-runtime` | `PySide6`; Laufzeit: `app.metrics`, `app.services` (lazy, Host) | Architektur + `test_runtime_public_surface_guard` + Lifecycle-Guards | **Welle 10** — [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_RUNTIME_PHYSICAL_SPLIT.md) |
| `commands`, `plugins`, `qa` | jeweils `app/.../` | Host | produktintern | Architektur + QA-Workflows | Kein klares externes Publikum |
| `packaging` | `app/packaging/` | **Host-only** | stdlib | `test_package_map_contract` | **Landmarks** nur ein „Source of truth“-Repo |

---

## 5. Wichtigste Split-Blocker (Schwerpunkt)

### 5.1 `global_overlay`

- Direkte `app.gui.*`-Importe entfernt; produktive Kopplung jetzt über **`app.core.startup_contract`** plus Overlay-Ports.
- **Rest-Blocker:** Overlay bleibt Produkt-Orchestrierung und nutzt weiter Startup-/Theme-Ports; kein verbleibender Root-Shim.

### 5.2 `workspace_presets`

- **`NavArea`** im Startpfad auf **`app.core.navigation.nav_areas`** umgestellt.
- Root-/Theme-/Capability-Zugriffe laufen jetzt direkt über **`app.core.startup_contract`**.
- **Rest-Blocker:** Presets bleiben produktnah wegen Aktivierungs-/Persistenzlogik, nicht mehr wegen Root-Brücken.

### 5.3 `ui_application`

- Direkter Zugriff auf **`get_theme_manager`** / `theme_id_utils` entfernt.
- `service_settings_adapter.py` liest Theme-Metadaten jetzt über `app.core.startup_contract`.
- **Rest-Blocker:** Theme-Read-Port ist produktweit in Core verankert; `ui_application` bleibt wegen Presenter-/Produktkopplung Hybrid, nicht wegen Root-Brücken.

### 5.4 `help`

- GUI-Anbindung auf **`app.help.ui_components`** gebündelt.
- **Rest-Blocker:** für eigenes Repo braucht es entweder **ausgelagerte, wiederverwendbare** UI-Bausteine im `ldc-ui`-Paket oder eine sehr schmale Host-interne Hilfe-Schicht.

### 5.5 `devtools`

- Aktuell **nur** `gui.themes.*`; Guard in `test_ui_layer_guardrails.py` fixiert diesen Rand.
- **Blocker:** **Regressions-Risiko** — jeder neue Import in Richtung `domains`/`shell` macht ein separates Repo sofort unhaltbar.

### 5.6 `packaging`

- **`landmarks.py`** und Vertragstests verbinden Doku + Repo-Pfade.
- **Blocker:** kein zweites Repo ohne **duplizierte oder generierte** Landmarken-Quelle; sinnvoll: immer beim **Host-Build** bleiben oder später generiert aus einem `build-metadata`-Repo.

### 5.7 Querschnitt (alle Wellen)

- Die bisherigen App-Root-Brücken (`gui_registry`, `gui_bootstrap`, `gui_capabilities`) sind entfernt; produktive Hybrid-Segmente laufen direkt über `app.core.startup_contract`.
- **`core` → `gui`** Ausnahme (`project_context_manager` → Events) widerspricht strenger Library-Grenze.
- **Einzelnes PyPI-Wheel** heute (`include = ["app*"]`) — Multi-Repo erzwingt **explizite** Paketgrenzen in `pyproject.toml` pro Repo.

---

## 6. Empfehlung: erste Split-Welle

**Detail-Stufenplan, Consumer-Matrix, `pyproject`-Skizzen und vor/während/nach-Checklisten:** [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md).  
**`app.features` cut-fähig (API, DoR, Oberflächen-Guard):** [`PACKAGE_FEATURES_CUT_READY.md`](PACKAGE_FEATURES_CUT_READY.md).  
**Physischer Cut (Packaging, Host/CI, Execution Plan):** [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md).

1. **`app/features` → eigenes Paket/Repo (`linux-desktop-chat-features` / Arbeitspaket `ldc-features`)**  
   - Höchster **Split-Reifegrad**: Entry-Point `linux_desktop_chat.features`, keine `app.features`→`gui`-Imports, CI-Matrix vorhanden.  
   - Vorbereitung im Monorepo: Host-Importe auf **`app.features`-Root (`__all__`)** wo möglich; `nav_binding`/CI-Module als Host-API dokumentieren; private Test-Importe (`_iter_*`) adressieren.

2. **Optional dieselbe Welle oder unmittelbar danach: `app/ui_contracts`**  
   - Qt-frei, nur interne `ui_contracts.*`-Kanten; große **flächige** Consumer-Fläche in `gui` und `ui_application` — siehe [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md).

3. **Nicht** in Welle 1: `gui`, `services`, `global_overlay`, `workspace_presets`, `ui_application` (ohne Port), `packaging`.

Nach Welle 1: Hybrid-Bereinigung für **`workspace_presets`** und **`ui_application`** ist direkt verbessert (`NavArea` in `core.navigation`, Theme-Zugriff über Produkt-Facade). Nächster Split-Schritt ist jetzt die Extraktion dieser Facaden in explizite Startup-/Theme-Contracts für **`ldc-ui`** bzw. **`ldc-product-startup`**.

### 6.1 Stand Wellen 1–2 (abgeschlossen)

| Welle | Segment | Abschluss / Verweis |
|-------|---------|---------------------|
| 1 | `app.features` | [`PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md) |
| 2 | `app.ui_contracts` | [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md) |

Hybrid-Themen (`workspace_presets`, `ui_application`↔Themes) bleiben für **spätere** UI-/Startup-Pakete relevant; sie sind **kein** harter Vorbedarf für die nächste **Fähigkeits-Insel** unter `app/`.

### 6.2 Welle 3 — empfohlener nächster Kandidat (Ist-basiert)

| Priorität | Segment | Kurzbegründung |
|-----------|---------|----------------|
| **Primär** | **`pipelines`** | **Ist:** `app.pipelines` aus **`linux-desktop-chat-pipelines`** (Host ohne `app/pipelines/`); Implementierung importiert nur `app.pipelines.*` (kein `core`, `services`, `gui`, `utils`). **Guards:** `FORBIDDEN_IMPORT_RULES` + Public-Surface-Guard; **Consumer:** u. a. `app.services.pipeline_service`, `app/workflows/execution/node_executors/tool_call.py`. **Abschluss Monorepo:** [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md). |
| **Alternative** | **`providers`** | Sehr klein, fachlich klar (Ollama-Adapter), intern nur `app.utils` + innerhalb `app.providers.*`. **Aber:** dokumentierte Architektur-Ausnahme **`app.core.models.orchestrator` → `app.providers`** — beim physischen Cut Abhängigkeitsrichtung `ldc-core`↔Provider-Paket oder Modul-Verschiebung explizit festlegen; mehr Governance-/Service-Tests als bei `pipelines`. |
| **Zurückgestellt** | **`agents`** | Kopplung an **`app.core`** (`llm_complete`, `ModelRole`) und **`app.debug`** (EventBus); breite GUI-/Service-/Contract-Testfläche. Split-Reife **niedrig–mittel**. |
| **Zurückgestellt** | **`rag`** | `RAGService` nutzt **`app.debug`**; Produkt-Extra `rag`; viele Integrations-/UI-Tests. Split-Reife **mittel**, höherer CI-/Dep-Overhead. |
| **Zurückgestellt** | **`prompts`** | Intern schlank (`utils` + `sqlite3`), **aber** sehr breite Consumer-Fläche in `gui`, `ui_application`, `python_bridge` — DoR/Public-Surface-Aufwand vergleichbar mit Welle 2, ohne die technische Isolation von `pipelines`. |
| **Zurückgestellt** | **`core` (Teilung)** | Brücken (u. a. `project_context_manager`→`gui`), Umfang; Zielbild `ldc-core` laut §3.2 **mittel** — kein nächster kleiner Schritt. |
| ~~Zurückgestellt~~ **erledigt (Welle 6)** | **`utils`** | Physische Extraktion `linux-desktop-chat-utils` — [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](PACKAGE_UTILS_PHYSICAL_SPLIT.md). |

**Hinweis:** Welle 3 ist **Vorbereitung** im Sinne des etablierten Monorepo-Musters (eingebettete Distribution, `extend_path`, Quell-Wurzel in Guards/QA wie Wellen 1–2) — **ohne** in diesem Dokumentlauf Umsetzung oder Commit-1-Start.

**`app.pipelines` (Welle 3):** [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md) · [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md) · [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) (**Variante B**).

### 6.3 Welle 4 — abgeschlossen (`app.providers`)

| Welle | Segment | Abschluss / Verweis |
|-------|---------|---------------------|
| 4 | `app.providers` | [`PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md`](PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md) · strategisches Memo: [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md) |

### 6.4 Welle 5 — CLI-Extraktion (`app.cli`)

**Entscheidung:** Primärkandidat **`cli`** — [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md).

**Technische Vorbereitung / Host-Cut (Monorepo, Variante B):**

| Thema | Inhalt |
|--------|--------|
| **Distribution** | `linux-desktop-chat-cli` (eingebettet, `file:./linux-desktop-chat-cli` im Host-`pyproject.toml`) |
| **Importpfad** | Unverändert **`app.cli`** und Submodule (`context_replay`, `context_repro_*`, …) |
| **Host** | Verzeichnis **`app/cli/`** entfernt; Namespace über Host-`app/__init__.py` (`extend_path`) |
| **Guards** | `TARGET_PACKAGES` + `FORBIDDEN_IMPORT_RULES` für `cli` → `gui` / `ui_application` / `ui_runtime`; Public-Surface [`test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py); Segment-AST inkl. Quelle [`app_cli_source_root()`](../../tests/architecture/app_cli_source_root.py) |
| **PEP-621 / core** | `linux-desktop-chat-cli` in **`DependencyGroupDescriptor.python_packages`** der Gruppe **core** |
| **Ist-Report** | [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md) |

**Hinweis:** Die CLI-Module hängen zur Laufzeit von **`app.context.replay.*`** (Host) ab; das CLI-Wheel ist keine vollständig eigenständige Produkt-Distribution ohne Host.

**Weitere Kandidaten (nicht Welle 5):**

| Priorität | Segment | Kurz |
|-----------|---------|------|
| ~~Sekundär~~ | **`utils`** | **Erledigt:** Welle 6 (`linux-desktop-chat-utils`). |
| ~~Sekundär~~ | **`ui_themes`** | **Erledigt (Welle 7):** `linux-desktop-chat-ui-themes` — [`PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`](PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md). |
| ~~Sekundär~~ | **`ui_runtime`** | **Erledigt (Welle 8):** `linux-desktop-chat-ui-runtime` — [`PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md). |
| ~~Sekundär~~ | **`debug` / `metrics` / `tools`** | **Erledigt (Welle 9):** `linux-desktop-chat-infra` — [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](PACKAGE_INFRA_PHYSICAL_SPLIT.md). |
| ~~Sekundär~~ | **`runtime` / `extensions`** | **Erledigt (Welle 10):** `linux-desktop-chat-runtime` — [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_RUNTIME_PHYSICAL_SPLIT.md). |
| **Zurückgestellt** | **`agents`**, **`rag`**, **`prompts`**, **`core`**, **`gui`**, **`services`**, **Hybrid-Segmente** | §6.2 / §5. |

### 6.5 Welle 6 — `app.utils` (`linux-desktop-chat-utils`)

| Thema | Inhalt |
|--------|--------|
| **Distribution** | `linux-desktop-chat-utils` (eingebettet, `file:./linux-desktop-chat-utils` im Host-`pyproject.toml`) |
| **Importpfad** | Unverändert **`app.utils`** und Submodule `paths`, `datetime_utils`, `env_loader` |
| **Host** | Verzeichnis **`app/utils/`** entfernt; Namespace über `extend_path` |
| **Provider-Vorlage** | **Kein** `src/app/utils/`-Spiegel mehr; **keine** `file:`-Abhängigkeit auf `utils` in `pyproject.toml` (pip/CWD — siehe [`linux-desktop-chat-providers/README.md`](../../linux-desktop-chat-providers/README.md)); Host bindet beides |
| **Guards** | Public-Surface [`test_utils_public_surface_guard.py`](../../tests/architecture/test_utils_public_surface_guard.py); Quelle [`app_utils_source_root()`](../../tests/architecture/app_utils_source_root.py); Segment-AST ergänzt |
| **Doku** | [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](PACKAGE_UTILS_PHYSICAL_SPLIT.md) |

### 6.6 Welle 7 — `app.ui_themes` (`linux-desktop-chat-ui-themes`)

| Thema | Inhalt |
|--------|--------|
| **Distribution** | `linux-desktop-chat-ui-themes` (eingebettet, `file:./linux-desktop-chat-ui-themes` im Host-`pyproject.toml`) |
| **Importpfad** | Unverändert **`app.ui_themes`** — nur `__init__.py`; Theme-Assets unter `builtins/**` via **package-data** |
| **Host** | Verzeichnis **`app/ui_themes/`** entfernt; Namespace über `extend_path` |
| **Runtime** | `app.ui_runtime.theme_registry.default_builtin_registry()` bindet `builtins/` über `import app.ui_themes` |
| **Guards** | Public-Surface [`test_ui_themes_public_surface_guard.py`](../../tests/architecture/test_ui_themes_public_surface_guard.py); Quelle [`app_ui_themes_source_root()`](../../tests/architecture/app_ui_themes_source_root.py); Segment-AST ergänzt |
| **Doku** | [`PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md`](PACKAGE_UI_THEMES_PHYSICAL_SPLIT.md) |

### 6.7 Welle 8 — `app.ui_runtime` (`linux-desktop-chat-ui-runtime`)

| Thema | Inhalt |
|--------|--------|
| **Distribution** | `linux-desktop-chat-ui-runtime` (eingebettet, `file:./linux-desktop-chat-ui-runtime` im Host-`pyproject.toml`) |
| **Importpfad** | Unverändert **`app.ui_runtime`** und kanonische Submodule (Guard: `test_ui_runtime_public_surface_guard.py`) |
| **Host** | Verzeichnis **`app/ui_runtime/`** entfernt; Namespace über `extend_path` |
| **Wheel-Deps** | `jsonschema`, `PySide6` — **keine** verschachtelte `file:`-Abhängigkeit auf `ui_contracts` (pip/CWD); vollständiges Produkt installiert Host + eingebettete Distributionen |
| **Guards** | Public-Surface [`test_ui_runtime_public_surface_guard.py`](../../tests/architecture/test_ui_runtime_public_surface_guard.py); Quelle [`app_ui_runtime_source_root()`](../../tests/architecture/app_ui_runtime_source_root.py); Segment-AST ergänzt |
| **Doku** | [`PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_UI_RUNTIME_PHYSICAL_SPLIT.md) |

### 6.8 Welle 9 — `app.debug` / `app.metrics` / `app.tools` (`linux-desktop-chat-infra`)

| Thema | Inhalt |
|--------|--------|
| **Distribution** | `linux-desktop-chat-infra` (eingebettet, `file:./linux-desktop-chat-infra` im Host-`pyproject.toml`) |
| **Importpfad** | Unverändert **`app.debug`**, **`app.metrics`**, **`app.tools`** und kanonische Submodule (Guard: `test_infra_public_surface_guard.py`) |
| **Host** | Verzeichnisse **`app/debug/`**, **`app/metrics/`**, **`app/tools/`** entfernt; Namespace über `extend_path` |
| **Wheel-Deps** | `PySide6` (QA-Cockpit); **keine** `file:`-Abhängigkeit auf `linux-desktop-chat-utils` — `app.metrics` braucht utils zur Laufzeit (Host bindet beides) |
| **Guards** | Public-Surface [`test_infra_public_surface_guard.py`](../../tests/architecture/test_infra_public_surface_guard.py); Quelle [`app_infra_segment_source_root()`](../../tests/architecture/app_infra_source_root.py); Import-/EventBus-Tests inkl. Embedded-Pfade |
| **Doku** | [`PACKAGE_INFRA_PHYSICAL_SPLIT.md`](PACKAGE_INFRA_PHYSICAL_SPLIT.md) |

### 6.9 Welle 10 — `app.runtime` / `app.extensions` (`linux-desktop-chat-runtime`)

| Thema | Inhalt |
|--------|--------|
| **Distribution** | `linux-desktop-chat-runtime` (eingebettet, `file:./linux-desktop-chat-runtime` im Host-`pyproject.toml`) |
| **Importpfad** | Unverändert **`app.runtime`** (Submodule `lifecycle`, `model_invocation`) und **`app.extensions`** (Guard: `test_runtime_public_surface_guard.py`) |
| **Host** | Verzeichnisse **`app/runtime/`**, **`app/extensions/`** entfernt; Namespace über `extend_path` |
| **Wheel-Deps** | `PySide6`; **keine** `file:`-Abhängigkeit auf Infra — Shutdown-Pfad importiert `app.metrics` / `app.services` lazy (Host bindet alles) |
| **Guards** | Public-Surface [`test_runtime_public_surface_guard.py`](../../tests/architecture/test_runtime_public_surface_guard.py); Quelle [`app_runtime_source_root.py`](../../tests/architecture/app_runtime_source_root.py); Segment-AST + Package-Guards inkl. Embedded-Pfade |
| **Doku** | [`PACKAGE_RUNTIME_PHYSICAL_SPLIT.md`](PACKAGE_RUNTIME_PHYSICAL_SPLIT.md) |

---

## 7. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Klassifikation, Zielpaketsteckbriefe, Matrix, Blocker, Welle-1-Empfehlung |
| 2026-03-25 | Verweis auf `PACKAGE_WAVE1_PREP.md`; § 6 mit konkreten Prep-Schritten ergänzt |
| 2026-03-25 | Verweis auf `PACKAGE_FEATURES_CUT_READY.md` (Welle-1 features) |
| 2026-03-25 | Verweis auf `PACKAGE_FEATURES_PHYSICAL_SPLIT.md` |
| 2026-03-25 | `ui_contracts`: Split-Reife in §3.8 präzisiert; Matrix + §6 → `PACKAGE_UI_CONTRACTS_WAVE2_PREP.md` |
| 2026-03-25 | `ui_contracts`: Cut-Ready / DoR — [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md) |
| 2026-03-25 | `ui_contracts`: physische Split-Entscheidung — [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md); Matrix-Spalte „Ziel“ auf Wheel-Namen angepasst |
| 2026-03-25 | §6.1–6.2: Stand Wellen 1–2; Welle-3-Empfehlung **`pipelines`** (primär), **`providers`** (Alternative), bewusst zurückgestellt: `agents`, `rag`, `prompts`, `core`-Teilung, `utils` |
| 2026-03-25 | Verweis [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md) unter §6.2 und §3.5 (Welle 3 `app.pipelines`) |
| 2026-03-25 | [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md) — DoR for Cut `app.pipelines`; Verweise §3.5 / §6.2 ergänzt |
| 2026-03-25 | [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) — Variante B, Matrix-Zeile `pipelines`, §6.2 / §3.5 |
| 2026-03-25 | Welle 3: Commit-1-Vorlage [`linux-desktop-chat-pipelines/`](../linux-desktop-chat-pipelines/); `PACKAGE_PIPELINES_PHYSICAL_SPLIT.md` §0/Status |
| 2026-03-25 | §6.3–6.4: Welle 4 (`providers`) abgeschlossen; Welle 5 Primärkandidat **`cli`**; Memo [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md) |
| 2026-03-25 | §6.4 erweitert: technische CLI-Extraktion `linux-desktop-chat-cli`; Report [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md) |
| 2026-03-26 | Phase A: Matrix/§3.9 an eingebettete Distributionen; §2.1 Reifeklassen; Verweis PACKAGE_MAP als kanonische Pfade |
| 2026-03-26 | Welle 6: `app.utils` → `linux-desktop-chat-utils`; §6.5; Matrix/READY; Provider-Vorlage ohne `utils`-Spiegel |
| 2026-03-26 | Provider-Vorlage: keine `file:`-Abhängigkeit Host→`utils` (pip/CWD); Doku/README angepasst |
| 2026-03-26 | Welle 7: `app.ui_themes` → `linux-desktop-chat-ui-themes`; §6.6; Sekundärkandidat `ui_themes` erledigt |
| 2026-03-26 | Welle 8: `app.ui_runtime` → `linux-desktop-chat-ui-runtime`; §6.7; Matrix; Sekundärkandidat `ui_runtime` erledigt |
| 2026-03-26 | Welle 9: `app.debug` / `app.metrics` / `app.tools` → `linux-desktop-chat-infra`; §6.8; Matrix §4; §3.12 Host-Bündel angepasst |
| 2026-03-26 | Welle 10: `app.runtime` / `app.extensions` → `linux-desktop-chat-runtime`; §6.9; Matrix §4; §3.12; §6.4 Sekundärkandidaten |
| 2026-03-29 | Hybrid-Härtung: kanonischer Produktvertrag `app.core.startup_contract`; `global_overlay`/`workspace_presets` ohne lokale Root-Facades, `workspace_presets` auf `core.navigation.NavArea`, `ui_application` Theme ueber Core-Contract; Root-Brücken entfernt; Guard-/QA-Status angepasst |
