# Repo-Split-Readiness und Zielpaketplan

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Vorbereitungs**doku — **kein** physischer Repo-Split, keine neuen GitHub-Repos  
**Bezug:** [`PACKAGE_MAP.md`](PACKAGE_MAP.md), [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md) (konkrete Extraktions-Checkliste), [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md), `app/packaging/landmarks.py`, `tests/architecture/arch_guard_config.py`, `tests/architecture/segment_dependency_rules.py`

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
| **C — Hybrid / vor Split bereinigen** | Inhaltlich sinnvoll abgrenzbar, aber **Ist-Kopplung** an `gui`/Root-Brücken muss vor dem Cut auf Ports/Contracts reduziert werden (siehe Hybrid-Notiz). |

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
| `ui_application` | **C** | Presenter/Adapter; **direkt** `app.gui.themes` (siehe Hybrid-Notiz). |
| `debug`, `metrics`, `tools` | **B** (Host oder später **Infra-Bündel**) | Querschnitt; oft Host-nah. Ausnahme: bewusstes `ldc-infra`-Repo in späterer Welle. |
| `commands` | **B** | Erweiterungen der Kommandopalette; eng mit Nav/Core verbunden. |
| `extensions`, `runtime` | **B** | Host-Laufzeit-Hooks; kein klarer externer Verbraucher außer dem Produkt. |
| `plugins` | **B** | **Interne** Plugin-Hilfen; externe Plugins bleiben **eigene** Distributionen (bereits modelliert). |
| `qa` | **B** | In-App-QA und Berichte; kann später mit Host-CI teilen, nicht als Library sinnvoll. |
| `packaging` | **B** | Meta (`landmarks`, Doku-Verweise); **muss** im Host (oder Build-Repo) bleiben. |
| `global_overlay` | **C** | Produktstart, Registry, Theme-Rescue; viele Root- und `gui.themes`-Touchpoints. |
| `workspace_presets` | **C** | Persistenz/Validierung + **`gui.navigation.nav_areas`** (Ausreißer). |
| `help` | **C** | Nutzt `gui.components` / `shared.markdown` — fachlich „Help-UI“, nicht reine Library. |
| `devtools` | **C** | Bewusst nur `gui.themes.*`; Grenze muss **hart** bleiben. |

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
| **Direkt erlaubt** | `ui_contracts`: am strengsten Qt-frei/feature-frei; `ui_application`: aktuell **Übergang** zu `gui.themes` — vor Split reduzieren. |
| **Split-Reife** | **ui_contracts:** technische Extraktion **hoch**, Release-/Ökosystem für physischen Cut **mittel** ([`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md) §6); **Importpfad/Packaging entschieden** ([`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §2) · **ui_application: mittel (Hybrid)** · **ui_runtime/ui_themes: mittel** |

### 3.9 `ldc-cli` ← `app/cli`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Kopflose Werkzeuge. |
| **Öffentliche API** | CLI-Entry-Commands, stabile Flags. |
| **Nicht exportieren** | Interne Test-Harnesses. |
| **Direkt erlaubt** | `core`, `services`, Domänen — **nicht** `gui` (Phase 3A). |
| **Split-Reife** | **Hoch** (sobald Host-Abhängigkeiten geklärt) |

### 3.10 `ldc-product-startup` (Arbeitsname) ← `global_overlay`, `workspace_presets`

| Feld | Inhalt |
|------|--------|
| **Verantwortung** | Produktstart, Overlay, Preset-Persistenz, Theme-/GUI-ID-Kompatibilität. |
| **Öffentliche API** | Schmale Ports (`overlay_*_port`, Preset-APIs), keine direkte Exposition aller Dialoge. |
| **Nicht exportieren** | Watchdog-Interna, Diagnose-Dialoge als „öffentlich“ deklarieren. |
| **Direkt erlaubt** | `gui_registry`, `gui_bootstrap`, `gui_capabilities`, geführter Theme-Zugriff; **Ziel:** kein `gui.navigation` aus Presets. |
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

`debug`, `metrics`, `tools`, `commands`, `extensions`, `runtime`, `plugins`, `qa`, `packaging` bleiben **im Host-Repo** oder wandern erst in **spätere** Wellen als `ldc-infra` o. Ä. **`packaging`** bleibt notwendigerweise beim Build/Host.

---

## 4. Repo-Split-Matrix (Ist-Pfade → Ziel)

| Segment / Bündel | Heutiger Pfad | Künftiger Repo-/Paketname (Arbeit) | Direkte Paketabhängigkeiten (Zielbild) | CI-/Testscope (pragmatisch) | Bemerkungen / Blocker |
|------------------|---------------|-------------------------------------|----------------------------------------|-----------------------------|------------------------|
| `features` | `app/features/` | `ldc-features` | stdlib + kleine, explizit gelistete Deps; keine UI/Services | `pytest tests/architecture/` (Guards) + Feature-/Edition-Matrix (`edition-smoke-matrix`, `release_matrix_ci`) | **Geringer Blocker**; API-Dokumentation für öffentliche Symbole |
| `utils` | `app/utils/` | `ldc-utils` oder in `ldc-core` | stdlib only (Guard) | Unit-Tests unter `tests/unit/**` bei vorhandenen Modulen + Architekturtests | Sehr klein; Repo-Overhead vs. Nutzen |
| `ui_contracts` | `app/ui_contracts/` | **`linux-desktop-chat-ui-contracts`** (liefert `app.ui_contracts`) | stdlib / typing-only wo möglich | Architekturtests + Verbraucher-Tests in `ui_application` | **Wenig technische Blocker**; Cut-Ready: [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md); Packaging: [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) |
| `cli` | `app/cli/` | `ldc-cli` | `core`, `services`, Domänen | CLI-Smoke falls vorhanden; sonst gezielte `pytest tests/...` | Packaging/Entry-Points im Host klären |
| `core` | `app/core/` | `ldc-core` | `utils`; ggf. `llm` intern | Breite `tests/unit/**` + Architektur | **project_context_manager → gui** (Port) |
| `llm` | `app/llm/` | Teil von `ldc-core` oder eigenes Paket | Abstimmung mit Zielbild APP_TARGET_PACKAGE | Unit-Tests + Guards | Duplikation mit `core/llm` im Zielbild beachten |
| `services` | `app/services/` | `ldc-services` | `core`, Fähigkeits-Pakete | Service-Unit-Tests, Architektur | Stabile Fassaden dokumentieren |
| `providers`, `rag`, `prompts`, `agents`, `pipelines` | `app/{providers,rag,prompts,agents,pipelines}/` | `ldc-capabilities` (mono) oder 2–3 Repos | gemäß `FORBIDDEN_IMPORT_RULES` | Fach-Tests pro Bereich + Architektur | Aufteilung = Release-Mehraufwand; **`pipelines` isoliert (Welle 3):** Wheel **`linux-desktop-chat-pipelines`**, Import **`app.pipelines`** — [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) |
| `chat`, `chats`, `context` | `app/chat/`, `chats/`, `context/` | `ldc-chat-domain` | `core`, `utils` | `tests/` mit Markern je nach Suite | Öffentliche Domänen-API definieren |
| `workflows`, `projects`, `persistence` | `app/workflows/`, `projects/`, `persistence/` | `ldc-workspace-data` | `core`, `utils` | Persistenz-/Workflow-Tests | Migration/ORM an Host-Editionen |
| `gui` | `app/gui/` | `ldc-gui` | `core`, `services`, `features`-Registrare, `ui_*`, … | `tests/ui/`, GUI-Smokes, Architektur-Domänen-Guards | **Größter Blocker**: Zentralität, Legacy, Ressourcen |
| `ui_application`, `ui_runtime`, `ui_themes` | `app/ui_application/` … | `ldc-ui` (Subpakete) | `ui_contracts`; **kein** breites `gui` nach Bereinigung | Presenter-/QML-Tests | **ui_application → gui.themes** entkoppeln |
| `global_overlay` | `app/global_overlay/` | `ldc-product-startup` (mit Presets) | Registry/Bootstrap/Capabilities + Theme-Port | Smoke/Startup-Tests, Watchdog | **Verstreute `get_theme_manager`-Calls** |
| `workspace_presets` | `app/workspace_presets/` | (wie oben) | Bootstrap, Registry, `theme_id_utils`; **nicht** `gui.navigation` | Preset-/Settings-Tests | **`NavArea`-Import** → Contract |
| `help` | `app/help/` | `ldc-help` | schmale `gui.components` oder Port | UI-Tests falls vorhanden | Abhängigkeit von Shell-Widgets |
| `devtools` | `app/devtools/` | `ldc-devtools` | nur `gui.themes.*` | Theme-/Visualizer-Tests | Jeder neue Import außerhalb `themes` = Blocker |
| `debug`, `metrics`, `tools` | `app/debug/` … | Host oder `ldc-infra` | gemäß Guards | Voll-Suite (`pytest-full`) | Querschnitt, EventBus-Policies |
| `commands`, `extensions`, `runtime`, `plugins`, `qa` | jeweils `app/.../` | Host | produktintern | Architektur + QA-Workflows | Kein klares externes Publikum |
| `packaging` | `app/packaging/` | **Host-only** | stdlib | `test_package_map_contract` | **Landmarks** nur ein „Source of truth“-Repo |

---

## 5. Wichtigste Split-Blocker (Schwerpunkt)

### 5.1 `global_overlay`

- Abhängigkeit von **`app.gui_registry`**, **`app.gui_bootstrap`**, **`app.gui_capabilities`** und **verteilt** `app.gui.themes` / `get_theme_manager`.
- **Blocker:** Theme-Zugriff nicht über **eine** Facade (`overlay_theme_port` o. ä.) gebündelt → schwer versionierbar.

### 5.2 `workspace_presets`

- **`app.gui.navigation.nav_areas` (`NavArea`)** im Startpfad — bricht die sonst „Bootstrap-only“-Kopplung.
- **Blocker:** Navigationstyp muss als **ID/Contract** (`ui_contracts` oder `core.navigation`) vorliegen, nicht als Shell-Modul.

### 5.3 `ui_application`

- Direkter Zugriff auf **`get_theme_manager`** / `theme_id_utils`.
- **Blocker:** Theme-**Read-Port** oder DTO von `gui`/`themes` trennen, sonst hängt „Presenter-Paket“ am Qt-Singleton.

### 5.4 `help`

- Kopplung an **`gui.components.markdown_widgets`**, **`doc_search_panel`**, **`shared.markdown`**.
- **Blocker:** für eigenes Repo braucht es entweder **ausgelagerte, wiederverwendbare** UI-Bausteine im `ldc-ui`-Paket oder eine sehr schmale Host-interne Hilfe-Schicht.

### 5.5 `devtools`

- Aktuell **nur** `gui.themes.*` — gut.
- **Blocker:** **Regressions-Risiko** — jeder neue Import in Richtung `domains`/`shell` macht ein separates Repo sofort unhaltbar.

### 5.6 `packaging`

- **`landmarks.py`** und Vertragstests verbinden Doku + Repo-Pfade.
- **Blocker:** kein zweites Repo ohne **duplizierte oder generierte** Landmarken-Quelle; sinnvoll: immer beim **Host-Build** bleiben oder später generiert aus einem `build-metadata`-Repo.

### 5.7 Querschnitt (alle Wellen)

- **App-Root-Brücken** (`gui_registry`, `gui_bootstrap`, `gui_capabilities`) und **TEMPORARILY_ALLOWED_ROOT_FILES** — verschieben die „echte“ Grenze nach außen.
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

Nach Welle 1: Hybrid-Bereinigung für **`workspace_presets` (`NavArea`)** und **`ui_application` (Theme-Read-Port)** — das entblockt spätere Cuts im **`ldc-ui`- / `ldc-product-startup`-Umfeld** (nicht identisch mit Wellen 1–2).

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
| **Zurückgestellt** | **`utils`** | Technisch trivial, ökonomisch geringer Gewinn (Matrix §4). |

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
| **Sekundär** | **`utils`** | Eher mit **`ldc-core`** oder spätere Welle. |
| **Sekundär** | **`ui_themes`** | **`ldc-ui`-Kontext** (`ui_runtime`, Theme-Grenzen). |
| **Zurückgestellt** | **`agents`**, **`rag`**, **`prompts`**, **`core`**, **`gui`**, **`services`**, Querschnitt, **Hybrid-Segmente** | §6.2 / §5. |

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
