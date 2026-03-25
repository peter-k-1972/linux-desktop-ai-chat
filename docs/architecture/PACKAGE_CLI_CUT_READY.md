# `app.cli` — Definition of Ready for Cut (Welle 5)

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **API-, Stabilitäts- und Reife-Definition** für das Segment `app.cli` — **ohne** physischen Split, **ohne** Wellenstart, **ohne** Codeänderungen oder `pyproject.toml`-Anpassungen durch dieses Dokument.  
**Bezug:** [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md), [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.9 / §6.4, [`PACKAGE_MAP.md`](PACKAGE_MAP.md), [`docs/developer/PACKAGE_GUIDE.md`](../developer/PACKAGE_GUIDE.md), [`tests/architecture/arch_guard_config.py`](../../tests/architecture/arch_guard_config.py), [`tests/architecture/segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py), [`tests/architecture/test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py), [`tests/architecture/app_cli_source_root.py`](../../tests/architecture/app_cli_source_root.py)

**Ergänzung (Packaging / Umsetzung):** [`PACKAGE_CLI_PHYSICAL_SPLIT.md`](PACKAGE_CLI_PHYSICAL_SPLIT.md) (Packaging- und Commit-Plan); Abschluss nach Umsetzung [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md) — verbindliche **Variante B** (Distribution **`linux-desktop-chat-cli`**, Importpfad **`app.cli`**), Host-`file:`, Landmarken/CI — **ohne** dieses Cut-Ready zu ersetzen (API/SemVer/Consumer bleiben hier).

---

## 1. Zweck und Abgrenzung

### 1.1 Zweck

Dieses Dokument ist die **verbindliche Grundlage** für einen späteren **Physical Split** von `app.cli`:

- **finaler Segmentumfang** (Host-/Wheel-Quellbaum `app/cli/`),  
- **verbindliche öffentliche Oberfläche** (**Submodule-first**),  
- **SemVer-/Stabilitätszonen**,  
- **Consumer-Matrix** und Abgleich mit **Architektur-Guards**,  
- **transitive Laufzeitabhängigkeiten** (ohne Verschönerung — **kein** Standalone-Mikro-Wheel),  
- **Definition of Ready** sowie **Blocker** bis zur Ausführung von Welle 5.

Damit können Physical-Split-Planung und Umsetzung **ohne erneute API-Discovery** angebunden werden — analog zu [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) und [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md).

### 1.2 Abgrenzung

| Thema | Wo |
|--------|-----|
| Ist-Analyse, Split-Readiness, Public-Surface-**Empfehlung** (wird hier **verbindlich**) | [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) |
| Strategische Welle-5-Entscheidung | [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md) |
| Wellenplan, Zielbild `ldc-cli` | [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.9, §6.4 |
| Kanonische Paketlandkarte | [`PACKAGE_MAP.md`](PACKAGE_MAP.md) |
| Wheel-Name, `pyproject`, Host-Cut, CI, Commit-Reihe | [`PACKAGE_CLI_PHYSICAL_SPLIT.md`](PACKAGE_CLI_PHYSICAL_SPLIT.md) / [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md) |

---

## 2. Finaler Segmentumfang

**Logischer Importpfad:** `app.cli.*`  
**Quellort (eingebettete Vorlage / Ziel-Wheel):** [`linux-desktop-chat-cli/src/app/cli/`](../../linux-desktop-chat-cli/src/app/cli/) — **Variante B**; nach Cut: Host entfernt den duplizierten Baum unter `app/cli/` und bindet die Distribution per `file:` (oder Pin).

| Modul | Rolle (kurz) |
|--------|----------------|
| [`__init__.py`](../../linux-desktop-chat-cli/src/app/cli/__init__.py) | Paketmarker — **kein** erweitertes `__all__` / keine Root-Reexports im **Ist-Cut-Ready** (siehe §3.3). |
| [`context_replay.py`](../../linux-desktop-chat-cli/src/app/cli/context_replay.py) | JSON → Replay-Service; Einstieg `python -m app.cli.context_replay`. |
| [`context_repro_run.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_run.py) | Einzelner Repro-Case; `python -m app.cli.context_repro_run`. |
| [`context_repro_batch.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_batch.py) | Verzeichnis mit `*.json`; `python -m app.cli.context_repro_batch`. |
| [`context_repro_registry_list.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_registry_list.py) | Registry lesen/listen; `python -m app.cli.context_repro_registry_list`. |
| [`context_repro_registry_rebuild.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_registry_rebuild.py) | Index aus Repro-Baum; `python -m app.cli.context_repro_registry_rebuild`. |
| [`context_repro_registry_set_status.py`](../../linux-desktop-chat-cli/src/app/cli/context_repro_registry_set_status.py) | Status am Artefakt; `python -m app.cli.context_repro_registry_set_status`. |

**Interne Grenzen:** Keine gegenseitigen Imports unter `app.cli.*`; gemeinsame Nutzung nur über **`app.context.replay.*`** (unverändert [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) §2).

---

## 3. Verbindliche Public Surface

### 3.1 Submodule-first (verbindlich)

Konsumenten **außerhalb** des Pakets `app.cli` dürfen `app.cli` nur wie folgt importieren:

1. **`from app.cli import …`** — **nur**, sobald in einem späteren Release explizite Root-Reexports in [`__init__.py`](../../linux-desktop-chat-cli/src/app/cli/__init__.py) und eine **Aktualisierung dieses Cut-Ready** §3.3 dokumentiert sind. **Ist-Zustand:** keine stabilen Root-Symbole.  
2. **`from app.cli.<submodul> import …`** mit **genau einer** Submodulebene, wobei `<submodul>` **ausschließlich** einer der folgenden Basenamen ist:  
   `context_replay`, `context_repro_run`, `context_repro_batch`, `context_repro_registry_list`, `context_repro_registry_rebuild`, `context_repro_registry_set_status`.

**Gleichwertig für Laufzeit:** `python -m app.cli.<submodul>` (kein Library-Import nötig).

### 3.2 Erlaubte Importpfade (kanonische Modulnamen)

Außerhalb der Implementierung von `app/cli/**` und außerhalb von `linux-desktop-chat-cli/src/app/cli/**` sind **nur** diese **absoluten** Modulpfade für `ImportFrom` zulässig:

| Modulpfad | Öffentliche programmatische API (Ist) |
|-----------|----------------------------------------|
| `app.cli.context_replay` | `run_replay` |
| `app.cli.context_repro_run` | `run_repro` |
| `app.cli.context_repro_batch` | `run_repro_batch` |
| `app.cli.context_repro_registry_list` | `run_registry_list` |
| `app.cli.context_repro_registry_rebuild` | `run_registry_rebuild` |
| `app.cli.context_repro_registry_set_status` | `run_registry_set_status` |

Die Funktionen `main()` in den Submodule sind **Einstiegspunkte für `-m`** (siehe §4); **keine** Empfehlung für Imports aus Host- oder Testcode außerhalb der CLI-Implementierung.

### 3.3 Root-Exports (`app.cli`)

- **Ist:** Kein `__all__`, keine Re-Exports — nur Paketmarker-Kommentar.  
- **Policy:** Jede künftige Erweiterung der Root-Oberfläche ist **semver-relevant** und erfordert **Cut-Ready-Update** + Release-Notizen (analog anderen Wellen).

### 3.4 Explizit verbotene Importmuster

| Muster | Grund |
|--------|--------|
| `app.cli.<sub>.<tiefer>` (zweite Ebene unter `app.cli`) | Nicht kanonisch; umgeht Public-Surface-Disziplin. |
| `from app.cli… import _*` bzw. jedes Symbol mit führendem `_` | Private Implementierung. |
| `from app.cli import *` | Nicht abgrenzbar gegenüber Root-Erweiterungen. |
| Direkte Imports von `app.gui`, `app.ui_application`, `app.ui_runtime` aus `app.cli` | Verboten durch `FORBIDDEN_IMPORT_RULES` (`cli` → …); siehe §7. |

---

## 4. Stabilitäts- / SemVer-Zonen

| Zone | Geltung | SemVer |
|------|---------|--------|
| **Z1 — Öffentliche Submodule** | Die in §3.2 genannten Module und **`run_*`-Funktionen** | **Stabil** für Aufrufkonventionen und Rückgabeformate, die von Tests/Doku abgedeckt sind; Breaking nur **major** + Deprecation-Pfad (sobald Wheel-Versionierung gilt). |
| **Z2 — Interne CLI-Implementierung** | Hilfsfunktionen, Konstanten, `main()`, Modul-interne Details unter `app/cli/**` | **Keine** Stabilitätsgarantie nach außen. |
| **Transitional** | *Keine* gesonderten Brückenmodule analog `app/ollama_client.py` für CLI nötig | — |

**Hinweis:** Änderungen an JSON-Schemas der Replay-/Repro-Pfade sind fachlich gebunden an **`app.context.replay.*`** und transitive Ketten (§6) — nicht als „Entkopplung vom Host“ interpretierbar.

---

## 5. Consumer-Matrix

**Zweck:** Formaler Anker für Public-Surface-Guard, SemVer und Reviews.

**Legende Importpfad-Typ**

| Typ | Bedeutung |
|-----|-----------|
| **submodule** | `from app.cli.<modul> import …` |
| **root** | `from app.cli import …` (derzeit **keine** stabilen Symbole — §3.3) |
| **string / doc** | Nur Dokumentation, Skript-Metadaten, keine statischen Imports |

**Legende Stabilitätszone**

| Zone | Bedeutung |
|------|-----------|
| **public** | Entspricht Z1 (§4) |
| **internal** | Implementierung / nicht für Außen-Imports vorgesehen |

| Ort | Importpfad-Typ | importierte Symbole | Stabilitätszone | Bemerkung |
|-----|------------------|---------------------|-----------------|-----------|
| [`tests/cli/test_context_replay_cli.py`](../../tests/cli/test_context_replay_cli.py) | **submodule** | `run_replay` (`app.cli.context_replay`) | **public** | Kanonischer Konsument |
| [`tests/cli/test_context_repro_cli.py`](../../tests/cli/test_context_repro_cli.py) | **submodule** | `run_repro`, `run_repro_batch` | **public** | Kanonischer Konsument |

**Kein** produktiver Host-Code außerhalb `app/cli/**` importiert aktuell `app.cli` (statische Analyse; Stand Cut-Ready).  
**Weitere Verweise (ohne Library-Import):** u. a. [`docs/DEVELOPER_GUIDE.md`](../DEVELOPER_GUIDE.md), [`docs/05_developer_guide/CLI_CONTEXT_TOOLS.md`](../05_developer_guide/CLI_CONTEXT_TOOLS.md), [`scripts/dev/architecture_map.py`](../../scripts/dev/architecture_map.py), [`tools/auto_explain_manual.py`](../../tools/auto_explain_manual.py) — **string / doc**.

---

## 6. Transitive Abhängigkeiten (verbindlich)

Die folgende Kette ist **unverkürzt** aus [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) §3.2 zu übernehmen — **keine** künstliche Entkopplung und **keine** Behauptung eines lauffähigen CLI-Wheels **ohne** Host-Domäne.

```
app.cli
  → app.context.replay.*  (z. B. replay_service, Repro-/Registry-Services)
  → app.context.engine (get_context_engine, Replay-Pfade)
  → app.services.chat_service (get_chat_service, _build_context_from_replay_input, …)
  → app.chat.* / app.core.* / app.context.explainability.*  (u. a.)
```

**Verbindliche Folgerungen:**

| Aussage | Inhalt |
|---------|--------|
| **`linux-desktop-chat-cli` ist kein Standalone-Mikro-Wheel** | Die Distribution **`linux-desktop-chat-cli`** allein (ohne installierten Host `linux-desktop-chat` bzw. gleichwertige Gesamtinstallation mit `app.context`, Services, Chat, Core) **deckt die Laufzeitkette nicht ab**. |
| **Host-Co-Installation ist Voraussetzung** | Unterstütztes Modell: **`linux-desktop-chat-cli` eingebettet oder per `file:`/`pip` neben dem Host** (Variante B), wie in [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) §5. |
| **Direkte CLI-Imports (Ist)** | Nur `app.context.replay.*` + stdlib in den CLI-Modulen — **keine** direkten `app.core` / `app.services` / `app.chat` / `app.workflows` in CLI-Quellen; die obige Kette ist **transitiv**. |

---

## 7. Guard-Abgleich / Public-Surface-Guard

### 7.1 `KNOWN_IMPORT_EXCEPTIONS` (Package-Guards)

**Quelle:** [`tests/architecture/arch_guard_config.py`](../../tests/architecture/arch_guard_config.py) → `KNOWN_IMPORT_EXCEPTIONS`.

**Ergebnis für Segment `cli`:** Es sind **keine** Einträge erforderlich, die speziell `app.cli` oder Pfade unter `cli/` als Quelle ausnehmen. CLI konsumiert **nicht** die in `KNOWN_IMPORT_EXCEPTIONS` typischerweise adressierten Ziele auf eine Weise, die eine neue Ausnahme nötig macht.

**Pflicht:** Nach Änderungen an CLI-Importen **1:1-Abgleich** mit `KNOWN_IMPORT_EXCEPTIONS` — bei Bedarf nur **Hinzufügen**, wenn zukünftig eine bewusste, review-pflichtige Verletzung einer `FORBIDDEN_IMPORT_RULES`-Kante entsteht (derzeit **nicht** der Fall).

### 7.2 `FORBIDDEN_IMPORT_RULES` und Segment-Kanten

- **`FORBIDDEN_IMPORT_RULES`:** `("cli", "gui")`, `("cli", "ui_application")`, `("cli", "ui_runtime")` — siehe `arch_guard_config.py`.  
- **`FORBIDDEN_SEGMENT_EDGES`:** `("cli", "gui")` — siehe [`tests/architecture/segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py).

### 7.3 Public-Surface-Guard (verbindlich)

[`tests/architecture/test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py) ist **Voraussetzung** für die Freigabe des Physical Split (analog `test_providers_public_surface_guard.py` / `test_pipelines_public_surface_guard.py`).

Die CLI-Quelle wird über [`app_cli_source_root.py`](../../tests/architecture/app_cli_source_root.py) (`app_cli_source_root()` → installierter / eingebetteter Baum) mit den Architektur-Regeln abgeglichen.

| Test | Regel |
|------|--------|
| `test_cli_imports_use_canonical_public_modules_only` | Außerhalb der CLI-Implementierung: `ImportFrom` auf `app.cli` nur wenn `modul ∈ { app.cli } ∪ { app.cli.<kanonisches_submodul aus §3.2> }` — **keine** tieferen `app.cli.*.*`-Pfade. |
| `test_no_private_cli_symbols_imported_outside_package` | Keine Imports von Symbolen mit führendem `_` aus `app.cli` außerhalb des Pakets (Scan: `app/` ohne `cli`, `tests/`, `tools/`, `examples/`, `scripts/` mit definierten Ausnahmen). |
| `test_cli_package_respects_arch_guard_forbidden_imports` | Alle `*.py` unter dem von `app_cli_source_root()` gelieferten `app/cli`-Baum: keine Kante, die `FORBIDDEN_IMPORT_RULES` für Quelle `cli` verletzt (§7.2). |

**Scan-Quellen:** Konfiguration im Testmodul — u. a. `APP_ROOT`, `PROJECT_ROOT / "tests"`, `tools`, `examples`, `scripts` (siehe Implementierung).

---

## 8. Definition of Ready für Physical Split

### 8.1 Dokumentation und Policy (Cut-Ready — dieses Dokument)

- [x] Split-Ready liegt vor ([`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md)).  
- [x] Cut-Ready: Segmentumfang §2, Public Surface §3, SemVer §4, Consumer §5, Transitive Abhängigkeiten §6, Guard-Abgleich / Public-Surface §7.  
- [x] [`PACKAGE_CLI_PHYSICAL_SPLIT.md`](PACKAGE_CLI_PHYSICAL_SPLIT.md) — verbindliche Packaging-/Commit-Skizze **Variante B** (Wheel-Name, Host-`file:`, CI, Landmarken) **liegt vor**.  
- [x] **`test_cli_public_surface_guard.py`** — **grün** im CI/ lokal (nach Welle-5-Umsetzung; siehe [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md) §5).  
- [x] **`KNOWN_IMPORT_EXCEPTIONS`:** kein CLI-spezifischer Zusatz nötig (§7.1); Abgleich bei künftigen Änderungen wiederholen.  
- [x] **Segment-AST / installierte Quelle:** `app_cli_source_root()` und `test_segment_dependency_rules` konsistent mit **installiertem** `app.cli` (Muster Wellen 3–4).  
- [x] **`find_spec("app.cli")`**, Dependency-Group-Drift (`linux-desktop-chat-cli` in **core**-`python_packages` — [`builtins.py`](../../linux-desktop-chat-features/src/app/features/dependency_groups/builtins.py)).  
- [ ] **Release-Notes / API-Hinweis** für §3.2-Symbole bei erstem **PyPI**-Wheel-Release (sobald relevant).

### 8.2 Ausführung (Welle 5 — nach Abschluss Commits 1–4)

- [x] Eingebettetes Repo / Vorlage `linux-desktop-chat-cli/` vollständig angebunden (Host-Abhängigkeit, keine doppelte Quelle).  
- [x] Host: Entfernen des duplizierten `app/cli/` im Host nach Cut-Plan.  
- [x] CI: Install + Verify `find_spec('app.cli')` nach Muster anderer eingebetteter Pakete.  
- [x] `app/packaging/landmarks.py`, `test_package_map_contract`, Git-QA-Segmente für `linux-desktop-chat-cli/src/app/cli/**` — wie in [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) §6 skizziert.

---

## 9. Blocker-Historie / Rest nach Welle 5

**Stand nach Abschluss Welle 5 (Commits 1–4):** Die folgenden ehemaligen Blocker sind im Monorepo **umgesetzt** — Details [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md).

| Thema (ehem. Blocker) | Nach Abschluss |
|------------------------|----------------|
| Physical Split Commits 1–4 | Erledigt gemäß [`PACKAGE_CLI_PHYSICAL_SPLIT.md`](PACKAGE_CLI_PHYSICAL_SPLIT.md) §5. |
| Public-Surface-Guard | [`test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py) im Pflichtpfad (lokal/CI mit installiertem `linux-desktop-chat-cli`). |
| Host/CI/Landmarken | `file:`, `find_spec`, Segment-AST, Git-QA — wie Closeout §2–§3. |

**Ohne Wellenabschluss-Blocker, aber Follow-up:** PyPI-Pin statt `file:`, Release-Notes beim ersten Index-Release (§8.1 letzte Checkbox), ggf. veraltete Pfade in älteren Handbüchern — siehe Closeout §4.

---

## 10. Klare Nicht-Ziele

- **Keine** Code-Refactorings, **kein** Verschieben von Dateien und **keine** Änderung von **`pyproject.toml`** **allein aufgrund** dieses Dokuments.  
- **Kein** Physical Split, **kein** Entfernen von Host-`app/cli/` außerhalb eines freigegebenen Commit-Plans.  
- **Kein** Start von **Welle 5 Execution** durch die Existenz dieses Cut-Ready allein.  
- **Keine** Scope-Ausweitung auf andere Segmente (`utils`, `ui_themes`, `agents`, `rag`, …).  
- **Kein** Ziel, **`linux-desktop-chat-cli`** oder `app.cli` **ohne** Host voll lauffähig zu machen — ausdrücklich **nicht** (§6).  
- **Keine** künstliche Entkopplung der Replay-Kette von `ChatService` / `app.chat` / `app.core` als Voraussetzung für Variante B + Host.

---

## 11. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Cut-Ready Welle 5 — Submodule-first verbindlich, Consumer-Matrix, transitive Kette, Guards, DoR, Blocker, Nicht-Ziele |
| 2026-03-25 | Gliederung auf 11 Abschnitte: §7 Guard-Abgleich + Public-Surface-Guard zusammengeführt; **`linux-desktop-chat-cli`** als Nicht-Standalone-Mikro-Wheel in §6 explizit benannt; Verweis Closeout / Physical-Split-Doku ergänzt |
| 2026-03-25 | [`PACKAGE_CLI_PHYSICAL_SPLIT.md`](PACKAGE_CLI_PHYSICAL_SPLIT.md) liegt vor — DoR-Checkbox §8.1; Blocker §9 auf Ausführung der Commits fokussiert |
| 2026-03-25 | §8.1/§8.2 nach Abschluss Welle 5 abgehakt; §9 Blocker-Historie / Restpunkte |
