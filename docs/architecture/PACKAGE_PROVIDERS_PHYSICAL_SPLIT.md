# `app.providers` — Physischer Split (Variante B, Monorepo)

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Importpfad- und Packaging-Planung** für Welle 4 — **keine** ausgeführten Commits in diesem Dokument; eingebettete Vorlage **`linux-desktop-chat-providers/`** ist zum Zeitpunkt der Erstellung **noch anzulegen**.  
**Bezug:** [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md), [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md), [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md), [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md), [`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.3, [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) / [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) (Analogiemodell), [`app/__init__.py`](../../app/__init__.py) (`pkgutil.extend_path`)

**Ausführungs-Dokumente (Arbeitsnamen, analog Wellen 1–3):** nach Commit 1 ff. z. B. `PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`, `PACKAGE_PROVIDERS_COMMIT3_CI.md`, `PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md` — **nicht** Gegenstand dieses Abschnitts.

---

## 1. Ziel und Abgrenzung

### 1.1 Ziel

Dieses Dokument legt fest:

- welche **Packaging-Variante** für die Distribution **`linux-desktop-chat-providers`** gilt,  
- wie die **eingebettete Vorlage** im Monorepo aussehen soll,  
- welche **Host-`, Guard-, Landmarken- und CI-Anpassungen** bei Ausführung nötig sind,  
- wie **`app/ollama_client.py`** und die **Core↔Providers-Entscheidung** in die Umsetzung einbezogen werden,  
- eine **Commit-Reihenfolge** analog der vorherigen Wellen.

### 1.2 Abgrenzung

| Thema | Wo |
|--------|-----|
| API, SemVer, Consumer-Matrix, DoR | [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) |
| Ist-Segment, Brücken-Tests | [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) |
| Core↔Providers-Varianten **A / B / C / D** (inhaltlich) | [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) |
| **Kein** Code, **kein** Ordnerwechsel, **kein** neues Repo in diesem Schritt | nur dieses Dokument |

---

## 2. Empfohlene Split-Variante

### 2.1 Kurzvergleich (analog Pipelines / UI-Contracts)

| Variante | Kurz |
|----------|------|
| **A — neuer Import-Root** (z. B. `ldc_providers`) | Massenwechsel aller `from app.providers` in Host, Services, Core, Tests, Guards; nur sinnvoll bei globalem „kein `app.*` aus Drittwheels“. |
| **B — `app.providers` bleibt** | Wheel liefert Namespace-Paket **`app.providers`** unter `src/app/providers/`; Host entfernt **`app/providers/`**; **`pkgutil.extend_path`** im Host-`app` bleibt ausreichend (wie Features, UI-Contracts, Pipelines). |
| **B′ — Namespace + Shim** | Doppelte Wahrheit, höherer Fehleraufwand; nur wenn **B** organisatorisch abgelehnt wird — dann eher **A** mit einmaligem Bump. |

### 2.2 Verbindliche Empfehlung

**Variante B:** Die Distribution **`linux-desktop-chat-providers`** liefert das Python-Paket **`app.providers`** (Baum `app/providers/` im Wheel, Quelle z. B. `linux-desktop-chat-providers/src/app/providers/`). Der Host **entfernt** nach dem Cut das Verzeichnis **`app/providers/`** und deklariert **`linux-desktop-chat-providers>=…`** in `[project] dependencies` (Monorepo zunächst `file:./linux-desktop-chat-providers`).

**Begründung (kurz):**

- **Null Breaking** für die dokumentierte Importfläche ([`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §5): `core`, `services`, Legacy-`main`, Tests.  
- Konsistenz mit **`linux-desktop-chat-features`**, **`linux-desktop-chat-ui-contracts`**, **`linux-desktop-chat-pipelines`**.  
- **SemVer** und Public Surface bleiben auf **`app.providers`**.

---

## 3. Zielstruktur des eingebetteten Repos `linux-desktop-chat-providers/`

**Hinweis:** Verzeichnis und Dateien werden **erst mit Commit 1** angelegt — hier nur **Zielbild**.

```text
linux-desktop-chat-providers/          # Monorepo-Vorlage (später eigenes Git-Repo optional)
  pyproject.toml
  README.md
  MIGRATION_CUT_LIST.md                # Parallelphase Host-Tree vs. Vorlage bis Commit 2 (analog Pipelines)
  src/
    app/
      providers/
        __init__.py
        base_provider.py
        ollama_client.py
        local_ollama_provider.py
        cloud_ollama_provider.py
        orchestrator_provider_factory.py
  tests/                               # Paket-eigene Mindesttests + ggf. aus Host verschobene Unit-Tests (Policy in Commit 1)
```

- **`src/`-Layout** — keine unbeabsichtigten Imports aus dem Repo-Root ohne Installation.  
- **Nur** der Teilbaum **`app/providers/`** — kein weiterer Host-`app/*`-Inhalt im Wheel.  
- **`MIGRATION_CUT_LIST.md`:** dokumentiert Sync-Regeln zwischen Host-`app/providers/` und Vorlage **bis** Host-Cut (Commit 2), analog [`linux-desktop-chat-pipelines/MIGRATION_CUT_LIST.md`](../../linux-desktop-chat-pipelines/MIGRATION_CUT_LIST.md).

---

## 4. Host-Anpassungen im Monorepo

| Bereich | Maßnahme (bei Ausführung) |
|---------|----------------------------|
| **[`pyproject.toml`](../../pyproject.toml)** | Zeile ergänzen: `linux-desktop-chat-providers @ file:./linux-desktop-chat-providers` (Kommentar wie bei Pipelines); Pin-Range sobald Versionierung steht. |
| **`app/providers/`** | **Entfernen** aus dem Host-Tree nach Commit 2 — kanonische Quelle nur Wheel/Vorlage. |
| **[`app/__init__.py`](../../app/__init__.py)** | **Keine** Änderung erwartet — `pkgutil.extend_path` bindet viertes Segment `app.providers` ein. |
| **Consumer** (`core`, `services`, `main`, Tests) | Bei Variante **B:** **keine** Importstring-Änderung. |
| **[`app/ollama_client.py`](../../app/ollama_client.py)** | **Entfällt** im Host; Konsumenten nutzen direkt **`app.providers.ollama_client`**. |
| **`[tool.setuptools.packages.find]`** im Host | Sicherstellen, dass **`app/providers`** nicht mehr aus dem Host-Tree gebündelt wird (Ordner entfernt = typischerweise ausreichend). |

---

## 5. `pyproject`- / `file:`-Abhängigkeitsmodell

### 5.1 Wheel `linux-desktop-chat-providers` (Skizze)

- **`[project] name`:** `linux-desktop-chat-providers`  
- **`requires-python`:** konsistent mit Host (`>=3.10`).  
- **`dependencies`:** mindestens **`aiohttp`** (siehe [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §2 — HTTP-Client im Paket). Keine Abhängigkeit zu **`app.core`**, **`app.services`**, **`PySide6`**.  
- **`[tool.setuptools.packages.find]`:** `where = ["src"]`, `include = ["app*"]` o. ä. — analog [`linux-desktop-chat-pipelines/pyproject.toml`](../../linux-desktop-chat-pipelines/pyproject.toml).  
- **`[project.optional-dependencies] dev`:** `pytest`, `build` für lokale Vorlagen-Verifikation.

### 5.2 Host

```toml
[project]
dependencies = [
  # … bestehend inkl. features, ui_contracts, pipelines …
  "linux-desktop-chat-providers @ file:./linux-desktop-chat-providers",
]
```

- Host behält **`aiohttp`** in den Gesamt-`dependencies`, solange andere Segmente es nutzen; das **Provider-Wheel** deklariert **`aiohttp`** trotzdem **eigenständig** (saubere Installation des Pakets allein).

### 5.3 PEP-621 / `dependency_groups.builtins`

- **`app.features.dependency_packaging`:** Aufnahme von **`linux-desktop-chat-providers`** in der **core**-`python_packages`-Liste (Monorepo-Muster wie bei Pipelines) — **bei Ausführung** mit `validate_pep621_pyproject_alignment` / Release-Matrix abgleichen.

---

## 6. Auswirkungen auf `app/packaging/landmarks.py` und `test_package_map_contract`

| Thema | Vorgehen (bei Ausführung) |
|-------|---------------------------|
| **`EXTENDED_APP_TOP_PACKAGES` / Landmarken** | Pfade, die **`app/providers`** als **Host-Unterverzeichnis** erwarten, auf **eingebettete Vorlage** oder **installiertes Paket** umstellen — analog Pipelines/UI-Contracts. |
| **`tests/architecture/test_package_map_contract.py`** | **`importlib.util.find_spec("app.providers")`** muss nach Installation **auflösbar** sein; Host-Tree darf **`app/providers/`** nicht mehr enthalten. |
| **Hilfsmodul (Arbeitsname)** | z. B. `app_providers_source_root()` parallel zu `app_pipelines_source_root()` — **Quellwurzel** für AST-Walks: eingebettetes `linux-desktop-chat-providers/src/app/providers` **oder** `importlib`-Pfad des installierten Pakets. |

---

## 7. CI- / `find_spec`- / Editable-Install-Plan

| Schritt | Inhalt |
|---------|--------|
| **Lokales / GHA-Setup** | Host: `pip install -e ".[dev]"` **plus** `pip install -e ./linux-desktop-chat-providers` (und bestehende Editables für features, ui_contracts, pipelines) — **analog** [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md). |
| **Verify** | Kurzcheck: `python -c "from app.providers import OllamaClient, LocalOllamaProvider; print('ok')"` sowie `find_spec("app.providers")` nicht `None`. |
| **`test_providers_public_surface_guard.py`** | Nach Cut: Implementierungspfad gegen **installierte** / Vorlagen-Quelle; Ausschluss nicht existenter Host-Pfade unter `app/providers/`. |
| **`test_segment_dependency_rules.py`** | Segment **`providers`**: `.py`-Dateien aus **`app_providers_source_root()`** mit Präfix `providers/…` — analog Pipelines. |
| **`test_provider_orchestrator_governance_guards.py`**, **`test_service_governance_guards.py`** | Sicherstellen, dass die Umgebung das **Providers-Wheel** lädt; Pfade in Fehlermeldungen ggf. auf neue Wurzel. |
| **`app/qa/git_qa_report.py`** | Segment-Zuordnung: Änderungen unter `linux-desktop-chat-providers/src/app/providers/**` → **providers** (analog Pipelines §4.2). |

---

## 8. Umgang mit dem entfernten Root-Pfad `app/ollama_client.py`

| Aspekt | Planung |
|--------|---------|
| **Rolle** | Kein Host-Re-Export mehr; kanonischer Importpfad ist `app.providers.ollama_client`. |
| **Nach Physical Split** | Aufrufer importieren `OllamaClient` direkt aus dem installierten Provider-Paket. |
| **`KNOWN_IMPORT_EXCEPTIONS`** | Kein Eintrag `ollama_client.py` → `providers` mehr erforderlich. |
| **Tests** | Live/Smoke-Tests nutzen direkt `app.providers.ollama_client` ([`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) §3.1). |

---

## 9. Umgang mit Core↔Providers-Variante A / B / D als Vorbedingung

**Bindend:** [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §1.3 und [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md).

| Variante | Auswirkung auf Physical Split (Packaging-Ebene) |
|----------|---------------------------------------------------|
| **A** (Übergang: `core` importiert weiterhin `providers`) | **Providers-Wheel** kann **vor** einem späteren **`ldc-core`-Wheel** extrahiert werden; sobald zwei Wheels existieren, ist **`ldc-core` → `ldc-providers`** als Abhängigkeit **explizit** zu deklarieren (Schichtbruch bewusst dokumentiert, Exit-Kriterium aus Boundary-Dokument). **Host-Monolith** heute: eine `pyproject`-Datei — keine doppelte Deklaration nötig, bis Core gesplittet wird. |
| **B / D** (Ziel: `core` importiert `providers` nicht) | **`KNOWN_IMPORT_EXCEPTIONS`** für `core/models/orchestrator.py` kann **nach Refactoring** entfallen; Physical Split der Provider wird **unabhängiger** von einer späteren Core-Extraktion. **Vorbedingung:** Refactoring **vor oder mit** Commit 2 **oder** bewusste Staffelung („erst Wheel, dann Entkopplung“) **schriftlich** festhalten. |
| **Nicht entschieden** | **Risiko:** Wheel-Abhängigkeitsgraph und Guard-Story für einen späteren **Core-Split** bleiben uneindeutig — **empfohlen:** Entscheidung **vor Commit 1 oder spätestens vor Commit 2** dokumentieren (Issue/ADR/Update Boundary- oder Cut-Ready-Dokument). |

**Dieses Physical-Split-Dokument** setzt **keine** Variante durch — es **verlangt** die dokumentierte Vorbedingung für belastbare Release- und Abhängigkeitsfolgen.

---

## 10. Vorgeschlagene Commit-Reihenfolge (analog frühere Wellen)

| Commit | Inhalt (Zielbild) |
|--------|-------------------|
| **Commit 1 — Vorlage** | Verzeichnis **`linux-desktop-chat-providers/`** anlegen: `pyproject.toml`, `README`, `MIGRATION_CUT_LIST.md`, vollständiger Spiegel `src/app/providers/**`, Mindesttests, `pip install -e ".[dev]"`, `pytest`, `python -m build` grün. Host-Tree **`app/providers/`** zunächst **noch** vorhanden — Sync-Disziplin laut MIGRATION. |
| **Commit 2 — Host-Cut** | Host-`pyproject.toml`: `file:./linux-desktop-chat-providers`; **`app/providers/`** entfernen; **`landmarks.py`**, **`app_providers_source_root()`**, **`test_package_map_contract`**, Segment-AST, Public-Surface-Guard, QA-Segment-Mapping anpassen. *(Arbeitsname Doku: `PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`.)* |
| **Commit 3 — CI** | Workflows: Editables inkl. Provider-Vorlage; Verify-`find_spec`; Matrix konsistent mit Features/UI-Contracts/Pipelines. *(Arbeitsname: `PACKAGE_PROVIDERS_COMMIT3_CI.md`.)* |
| **Commit 4 — Welle-4-Abschluss** | Governance-Restabgleich, Stichprobe `pytest`, Doku-Cross-Links, ggf. Release-Notes/Changelog für **`linux-desktop-chat-providers`**. *(Arbeitsname: `PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md`.)* |

---

## 11. Klare Nicht-Ziele

- **Keine** Implementierung, **kein** Anlegen von **`linux-desktop-chat-providers/`**, **kein** Verschieben von Dateien und **kein** Patchen von Produktcode **in diesem Schritt**.  
- **Kein** Start von **Welle 4** allein durch die Existenz dieses Dokuments.  
- **Kein** PyPI-Release, **kein** finales Versionspinning gegen externes Index-Repository — bleibt später.  
- **Keine** Auflösung der **Hybrid-Segmente** (Overlay, Presets, `ui_application`↔Themes).  
- **Kein** Ersatz für die inhaltliche **Core↔Providers**-Analyse — nur **Vorbedingung** und Packaging-Folgen (§9).

---

## 12. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Variante **B**, Zielstruktur, Host/`pyproject`, Landmarken, CI, Brücke `app/ollama_client`, Vorbedingung A/B/D, Commit-Reihenfolge 1–4, Nicht-Ziele |
| 2026-03-25 | Doku-Kohärenz: Querverweise mit Cut-Ready, Split-Ready, Split-Plan §6.3, `PACKAGE_GUIDE` abgestimmt |
