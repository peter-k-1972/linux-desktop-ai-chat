# `app.cli` — Split-Readiness (Welle 5)

**Projekt:** Linux Desktop Chat  
**Status:** **Architektur- und API-Vorbereitung** — **kein** ausgeführter Physical Split, **kein** Wellenstart, **keine** `pyproject.toml`-Änderung und **keine** Code-Umsetzung durch dieses Dokument.  
**Bezug:** [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.9 / §6.4, [`PACKAGE_MAP.md`](PACKAGE_MAP.md), [`docs/developer/PACKAGE_GUIDE.md`](../developer/PACKAGE_GUIDE.md), [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md) (Ist-Scan), [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py), [`segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py)

---

## 1. Zweck und Abgrenzung

### 1.1 Zweck

Dieses Dokument fasst die **Split-Readiness** des Segments **`app.cli`** zusammen — für eine spätere **eingebettete Distribution** (Arbeitsname `linux-desktop-chat-cli`, Importpfad unverändert **`app.cli`**, Variante **B** wie bei Features/UI-Contracts/Pipelines/Providers):

- Modul- und Verantwortungsumfang  
- **Direkte** und **transitive** Import- und Laufzeitflächen (insbesondere **`app.context.replay` → `app.context.engine` → `app.services.chat_service` → `app.chat` / `app.core`**)  
- Empfehlung **Public Surface** (**Submodule-first**)  
- Packaging-Annahme: **Wheel nur sinnvoll mit Host-Co-Installation**  
- **Vorbedingungen** vor einem späteren **`PACKAGE_CLI_CUT_READY.md`**  
- **Klare Nicht-Ziele**

### 1.2 Abgrenzung

| Thema | Wo anders |
|--------|-----------|
| Strategische Welle-5-Entscheidung | [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md) |
| Wellenplan / Zielbild `ldc-cli` | [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.9, §6.4 |
| Kanonische Paketlandkarte | [`PACKAGE_MAP.md`](PACKAGE_MAP.md) |
| **Definition of Ready for Cut**, SemVer, finale Consumer-Matrix | [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) (**kanonisch** für API, DoR, Blocker) |
| Packaging, `file:`, CI, Commit-Reihe | [`PACKAGE_CLI_PHYSICAL_SPLIT.md`](PACKAGE_CLI_PHYSICAL_SPLIT.md) |

**Hinweis:** **`PACKAGE_CLI_CUT_READY.md`** ist **kanonisch** für API, DoR und Blocker vor dem Cut; dieses Split-Ready bleibt die **Ist-Analyse** und die **Public-Surface-Empfehlung** (§4), die im Cut-Ready **verbindlich** festgelegt ist.

---

## 2. Aktueller Segmentumfang von `app.cli`

Logischer Importpfad: **`app.cli.*`**. Produktive Module (eine Ebene unter dem Paket):

| Modul | Rolle (kurz) |
|--------|----------------|
| [`__init__.py`](../../linux-desktop-chat-cli/src/app/cli/__init__.py) | Platzhalter — **kein** erweitertes `__all__` am Paketroot (Ist-Empfehlung: Submodule-first, siehe §4). |
| [`context_replay.py`](../../linux-desktop-chat-cli/src/app/cli/context_replay.py) | JSON → `ReplayInput` → `get_context_replay_service().replay()` → JSON; Einstieg `python -m app.cli.context_replay`. |
| [`context_repro_run.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_run.py) | Einzelner Repro-Case (`run_repro_case_from_file`); `python -m app.cli.context_repro_run`. |
| [`context_repro_batch.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_batch.py) | Verzeichnis mit `*.json`; `python -m app.cli.context_repro_batch`. |
| [`context_repro_registry_list.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_registry_list.py) | Registry lesen/listen; `python -m app.cli.context_repro_registry_list`. |
| [`context_repro_registry_rebuild.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_registry_rebuild.py) | Index aus Repro-Baum; `python -m app.cli.context_repro_registry_rebuild`. |
| [`context_repro_registry_set_status.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_registry_set_status.py) | Status am Artefakt; `python -m app.cli.context_repro_registry_set_status`. |

**Quellort im Monorepo (eingebettete Vorlage):** [`linux-desktop-chat-cli/src/app/cli/`](../../linux-desktop-chat-cli/src/app/cli/) — entspricht dem Zielbild **Variante B** (Distribution liefert `app.cli`, Host ohne duplizierten Baum nach Cut).

**Interne Grenzen:** Keine gegenseitigen Imports unter `app.cli.*`; gemeinsame Nutzung nur über **`app.context.replay.*`**.

---

## 3. Direkte und transitive Consumer-/Abhängigkeitsflächen

### 3.1 Statische `app.*`-Importe **innerhalb** `app.cli/**` (direkt)

Alle CLI-Module importieren **nur**:

- **`app.context.replay.*`** (z. B. `canonicalize`, `replay_service`, `repro_case_runner`, Registry-/Indexer-Services),  
- sowie **stdlib** (`json`, `logging`, `sys`, `pathlib`, `typing`).

**Explizit fehlend** in den CLI-Quellen (Ist-Prüfung):

- `app.gui`, `app.ui_application`, `app.ui_runtime`, `app.ui_themes`  
- `app.providers`  
- **direkte** Imports von `app.core`, `app.services`, `app.chat`, `app.workflows`

**Weitere Mechanismen in CLI:** kein `importlib`/`__import__` für Produktcode, kein `subprocess`, kein `argparse`/`typer`/`click` — Eingaben über **`sys.argv`** in `main()`.

### 3.2 Transitive Laufzeitkette (verbindlich zu dokumentieren)

Für **`context_replay`** (und damit für Pfade, die `get_context_replay_service()` → `ContextEngine` mit Replay-Flags nutzen) gilt **mindestens**:

```
app.cli → app.context.replay.replay_service
       → app.context.engine (get_context_engine)
       → app.services.chat_service (get_chat_service)
       → app.chat.* / app.core.* / app.context.explainability.*
```

Konkret: In [`app/context/engine.py`](../../app/context/engine.py) führt der Replay-Pfad zu **`from app.services.chat_service import get_chat_service`** und **`get_chat_service()._build_context_from_replay_input(...)`**; die Implementierung in [`app/services/chat_service.py`](../../app/services/chat_service.py) (`_build_context_from_replay_input`) bindet **`app.chat.context`**, **`app.chat.context_limits`**, **`app.chat.context_profiles`**, **`app.core.config.chat_context_enums`**, **`app.context.explainability.*`**, u. a.

**Bewertung:**

- **Kein Blocker** für das etablierte Muster **eingebettetes CLI-Wheel + vollständiger Host** (Rest-`app.*` installiert).  
- **Blocker** für die Vorstellung eines **einzigen** `pip install linux-desktop-chat-cli` ohne Host — **fehlende** Domäne und Services.

### 3.3 Consumer **außerhalb** `app.cli` (Host-Repo)

| Ort | Nutzung |
|-----|---------|
| [`tests/cli/test_context_replay_cli.py`](../../tests/cli/test_context_replay_cli.py) | `from app.cli.context_replay import run_replay` |
| [`tests/cli/test_context_repro_cli.py`](../../tests/cli/test_context_repro_cli.py) | `from app.cli.context_repro_run`, `context_repro_batch` |

**Doku / Handbuch:** u. a. [`docs/DEVELOPER_GUIDE.md`](../DEVELOPER_GUIDE.md) §5, [`docs/05_developer_guide/CLI_CONTEXT_TOOLS.md`](../05_developer_guide/CLI_CONTEXT_TOOLS.md).

### 3.4 Segment-Guards (Zielzustand / teils umgesetzt)

- **`FORBIDDEN_SEGMENT_EDGES`:** `(cli, gui)` — siehe [`segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py), [`PACKAGE_MAP.md`](PACKAGE_MAP.md) §7.  
- **`FORBIDDEN_IMPORT_RULES`:** `cli` → `gui`, `ui_application`, `ui_runtime` — [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py).  
- **Segment-AST-Tests** sollen den **installierten** `app.cli`-Quellbaum einbeziehen (analog `app.providers` / `app.pipelines`): synthetisches Präfix `cli/…` neben Host-`app/`.

---

## 4. Public-Surface-Empfehlung

### 4.1 Submodule-first (bevorzugt)

**Verbindliche Empfehlung** für Konsumenten **außerhalb** der CLI-Implementierung:

1. **`from app.cli.<submodul> import …`** mit **genau einer** Submodulebene, wobei `<submodul>` einer der folgenden Basenamen ist:  
   `context_replay`, `context_repro_run`, `context_repro_batch`, `context_repro_registry_list`, `context_repro_registry_rebuild`, `context_repro_registry_set_status`.  
2. Alternativ (gleichwertig): **`import app.cli.<submodul>`** für `-m`-Kontexte ist implizit; für Library-Imports Submodule nutzen.

**Nicht** empfohlen ohne Cut-Ready-Freigabe: tiefe Pfade unterhalb dieser Module (gibt es im Ist kaum); **keine** Abkürzung über private Symbole (`_*`).

### 4.2 Paketroot `app.cli`

- **Kein** Zwang zu einer großen `__all__`-Reexport-Fläche.  
- Optional können später **einzelne** stabile Funktionen (`run_replay`, `run_repro`, …) im Root re-exportiert werden — **Erhöhung der semver-Oberfläche**; nur in **Cut-Ready** festlegen.

### 4.3 Public-Surface-Guard (Zielzustand)

**Empfohlen:** pytest-Guard analog [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py) / [`test_providers_public_surface_guard.py`](../../tests/architecture/test_providers_public_surface_guard.py):

- Außerhalb der CLI-Quelle: nur **`app.cli`** oder **`app.cli.<kanonisches_submodul>`** — keine tieferen `app.cli.*.*`-Importe von außen.  
- Keine Imports von **`_*`**-Symbolen aus `app.cli` außerhalb des Pakets.  
- Optional: Zusatzprüfung, dass die CLI-Quelle die **`FORBIDDEN_IMPORT_RULES`** für Segment `cli` einhält.

**Cut-Ready** soll festhalten, ob der Guard **Voraussetzung für den physischen Cut** ist (empfohlen: **ja**, analog Welle 3–4).

---

## 5. Packaging-Annahme: eingebettetes Wheel + Host-Co-Installation

| Annahme | Inhalt |
|---------|--------|
| **Variante** | **B** — Distribution `linux-desktop-chat-cli` (Arbeitsname) liefert Paketbaum **`app/cli/`** im Wheel; Host entfernt nach Cut den duplizierten Baum unter `app/cli/` und deklariert **`linux-desktop-chat-cli @ file:./linux-desktop-chat-cli`** (oder später PyPI-Pin). |
| **Namespace** | Host-`app/__init__.py`: weiterhin **`pkgutil.extend_path`**, wie bei den anderen eingebetteten Paketen. |
| **Runtime** | **CLI-Wheel allein** reicht **nicht**: Laufzeit benötigt **`app.context`** und (über Engine/Replay) **`app.services`**, **`app.chat`**, **`app.core`** — also **Installation des Hosts** `linux-desktop-chat` (oder gleichwertiger Gesamtinstall). |
| **Abhängigkeiten im CLI-`pyproject.toml`** | Voraussichtlich **keine** zusätzlichen PyPI-Pakete über Stdlib hinaus für die CLI-Dateien selbst; **fachliche** Abhängigkeit ist **implizit über den Host**. |
| **PEP-621 / Features** | Aufnahme von `linux-desktop-chat-cli` in **`DependencyGroupDescriptor.python_packages`** der Gruppe **core** (Drift-Check) — analog Providers/Pipelines; Details im späteren Physical-Split-Dokument. |
| **CI** | Nach Cut: nach Host-Install zusätzlich **`pip install -e ./linux-desktop-chat-cli`** und Verify **`find_spec('app.cli')`** — analog bestehende Workflows für andere eingebettete Distributionen. |

---

## 6. Offene Blocker / Vorbedingungen vor Cut-Ready

Diese Liste ist **Vorbereitung** für **`PACKAGE_CLI_CUT_READY.md`**; die **verbindliche** Priorisierung erfolgt dort.

| Typ | Punkt |
|-----|--------|
| **Dokumentation** | Transitive Kette §3.2 in Cut-Ready und Physical-Split **wörtlich** übernehmen; „kein Standalone-Mikro-Wheel“ als Annahme festhalten. |
| **Governance** | Sicherstellen: `cli` in **`TARGET_PACKAGES`**, `FORBIDDEN_IMPORT_RULES` und Segment-AST decken **installierte** CLI-Quelle ab; **`EXTENDED_APP_TOP_PACKAGES`:** `cli` nicht doppelt. |
| **Public-Surface-Guard** | Implementierung und grüne Basis — **empfohlen als Cut-Voraussetzung** (siehe §4.3). |
| **Landmarken** | `REPO_LANDMARK_FILES` / `PACKAGE_MAP` / Physical-Split-Checkliste: Pfade zu `linux-desktop-chat-cli/pyproject.toml` und `src/app/cli/__init__.py`. |
| **Git-QA-Segmente** | `segments_from_changed_files`: Pfade `linux-desktop-chat-cli/src/app/cli/**` → Segment **cli** (analog andere eingebettete Bäume). |
| **Refactor (optional, nicht blockierend für eingebettetes Wheel)** | Langfristige Entkopplung Replay-Engine von **`ChatService`**, falls ein **schlankeres** CLI-Wheel gewünscht wird — **follow-up**, kein Split-Ready-Blocker für Variante B + Host. |

**Kein** analoges „Core↔Providers“-Problem: CLI importiert **nicht** direkt `app.providers` / `app.core`.

---

## 7. Definition of Ready für ein späteres `PACKAGE_CLI_CUT_READY.md`

Das folgende ist die **empfohlene DoR-Grundlage** für die **kanonische** Ausarbeitung in **`PACKAGE_CLI_CUT_READY.md`** (noch anzulegen):

1. **Public Surface** — Verbindliche Liste: Submodule-first (§4.1); optional Root-Reexports nur explizit benannt; semver-relevante Änderungen an diesen Oberflächen im Cut-Ready definieren.  
2. **Consumer-Matrix** — Tabelle aller Produkt- und Test-Importe von `app.cli` (inkl. nur erlaubter Pfade); keine unerwarteten tieferen Importe.  
3. **Guards** — `test_cli_public_surface_guard.py` (oder gleichwertig) **grün**; Abgleich `arch_guard_config` / `segment_dependency_rules` mit Ist-Code.  
4. **Transitive Abhängigkeit** — Cut-Ready enthält **expliziten** Abschnitt zu §3.2 (Engine → `chat_service` → `chat`/`core`); Akzeptanzkriterium: **Wheel + Host** ist das unterstützte Installationsmodell.  
5. **Kein GUI-Bezug** — Nachweis (statisch + Guard): keine direkten Imports `app.gui` / `ui_*` aus `app.cli`.  
6. **Einstiegspunkte** — Dokumentation: `python -m app.cli.<modul>`; optional später `[project.scripts]` im CLI-`pyproject` — **entweder/oder** Policy im Cut-Ready festlegen.  
7. **Post-Cut-Verifikation** — `find_spec("app.cli")`, Quellwurzel-Helfer (`app_cli_source_root()` o. ä.), minimale Smoke-Imports in CI wie bei anderen eingebetteten Paketen.  
8. **Blocker-Matrix** — Leere oder explizit erledigte Blocker vor „Go“ für Physical-Split-Ausführung.

---

## 8. Klare Nicht-Ziele

- **Keine** Code-Refactorings, **kein** Verschieben von Dateien und **kein** Anlegen oder Ändern von **`linux-desktop-chat-cli/`** oder Host-**`pyproject.toml`** **allein aufgrund** dieses Split-Ready.  
- **Kein** ausgeführter **Physical Split**, **kein** Entfernen von Host-`app/cli/` außerhalb eines separaten, freigegebenen Commit-Plans.  
- **Kein** Ersatz für [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md) oder [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) — dieses Dokument **ergänzt** die technische Split-Sicht.  
- **Keine** Scope-Ausweitung auf **`utils`**, **`ui_themes`**, **`agents`**, **`rag`**, …  
- **Kein** Anspruch, das CLI-Wheel **ohne** Host voll lauffähig zu machen — explizit **nicht** Ziel dieses Segments (§5).  
- **Kein** Start von **Welle 5 Execution** durch die Existenz dieses Dokuments allein.

---

## 9. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Split-Readiness `app.cli` — Umfang, direkte/transitive Flächen, Submodule-first, Packaging Co-Install, DoR-Vorgabe für Cut-Ready, Nicht-Ziele |
