# `app.features` — Physischer Split (Vorbereitung, ohne Repo-Anlage)

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Packaging- und Pfadentscheidung** für den ersten echten Cut; **keine** Ausführung in diesem Dokument  
**Bezug:** [`PACKAGE_FEATURES_CUT_READY.md`](PACKAGE_FEATURES_CUT_READY.md), [`PACKAGE_FEATURES_COMMIT2_LOCAL.md`](PACKAGE_FEATURES_COMMIT2_LOCAL.md) (Host + eingebettete Vorlage, lokal), [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md) (GitHub Actions), [`PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md) (Welle 1 Abschluss), [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)

---

## 0. Commit-1-Vorlage (im Host-Monorepo eingebettet)

Bis zur Auslagerung als eigenes Git-Repository liegt die **ausführbare Repo-Vorlage** unter:

**`linux-desktop-chat-features/`** (Verzeichnis im Wurzelverzeichnis dieses Repos).

Inhalt: produktives [`pyproject.toml`](../../linux-desktop-chat-features/pyproject.toml), [`README.md`](../../linux-desktop-chat-features/README.md), [`MIGRATION_CUT_LIST.md`](../../linux-desktop-chat-features/MIGRATION_CUT_LIST.md), vollständiger Quellbaum [`src/app/features/`](../../linux-desktop-chat-features/src/app/features/), minimale Tests unter [`tests/unit/`](../../linux-desktop-chat-features/tests/unit/). Verifikation: siehe README (venv, `pytest`, `python -m build`).

---

## 1. Entscheidungsvorlage: Importpfad nach dem Cut

### Variante A — Neues Top-Level `ldc_features`

| | Host | Plugins | CI | SemVer |
|---|------|---------|-----|--------|
| **Vorteile** | Klare Trennung „Vendor-Library“ vs. `app`; keine Überlagerung von `app.*` aus zwei Distributions. | Eindeutige Abhängigkeit `linux-desktop-chat-features` + `import ldc_features`. | Einfaches Modell: ein Paket, ein Root. | Saubere Library-Versionierung unter eigenem Namen. |
| **Nachteile** | **Pflicht:** alle `from app.features` → `from ldc_features` (oder dauerhafter Shim in `app/features`). | **Breaking:** bisherige Doku/Beispiele `app.features` anpassen; Plugin-Autoren müssen migrieren. | Alle `app.features.*`-Strings in Skripten/Workflows anpassen (oder Shim). | Host + Features müssen Major-Versionen abstimmen bei API-Brüchen. |

### Variante B — Importpfad `app.features` bleibt (Paket im Wheel unter `app/features/`)

| | Host | Plugins | CI | SemVer |
|---|------|---------|-----|--------|
| **Vorteile** | **Kein** Importstring-Wechsel: `from app.features import …` unverändert. | **Kein** Breaking: weiter `app.features` wie in [`PLUGIN_AUTHORING_GUIDE.md`](../developer/PLUGIN_AUTHORING_GUIDE.md). | `tools/ci` behält `app.features.release_matrix` / `dependency_packaging` (nach `pip install linux-desktop-chat-features`). | Distribution `linux-desktop-chat-features` versioniert die Feature-Plattform; Host pinnt `>=x.y`. |
| **Nachteile** | Zwei Distributions können theoretisch `app.*` liefern — **nur eine** darf `app/features` enthalten (Host-Tree entfernen). | — | Tests/Guards, die **`APP_ROOT / "features"`** lesen, müssen auf installiertes Paket umgestellt werden (siehe § 5). | „`app` im Namen“ in einem externen Wheel ist ungewöhnlich, aber technisch üblich genug. |

### Variante B′ — Namespace `linux_desktop_chat.features` + Shim `app.features` im Host

| | Host | Plugins | CI | SemVer |
|---|------|---------|-----|--------|
| **Idee** | Wheel liefert `linux_desktop_chat/features/`; Host behält dünnes `app/features/__init__.py`, das re-exportiert. | Entweder weiter `app.features` (Shim) oder direkt `linux_desktop_chat.features`. | Zwei Schichten zu installieren. | Shim kann deprecation über Major-Releases steuern. |
| **Nachteile** | Mehr Moving Parts; Shim-Pflege bis alle auf Namespace sind. | Dokumentations- und Support-Mehraufwand. | Höhere Fehlerwahrscheinlichkeit (falsche SITE-Packages-Reihenfolge). | — |

---

## 2. Verbindliche Empfehlung (Welle 1)

**Variante B:** Die Distribution **`linux-desktop-chat-features`** liefert das Python-Paket **`app.features`** (Verzeichnisbaum `app/features/` im Wheel, z. B. unter `src/app/features/` im Features-Repo). Der Host **entfernt** sein lokales `app/features` und deklariert **`linux-desktop-chat-features>=…`** in `[project] dependencies`.

**Begründung (kurz):** Null Breaking für Host-Importe und externe Plugins; Entry-Point-Gruppe `linux_desktop_chat.features` bleibt ohnehin metadatenbasiert; CI-Skripte behalten ihre Modulpfade nach Installation der Abhängigkeit.

**Variante A (`ldc_features`)** bleibt **optionale Major-Migration** später, wenn das Team eine strikte Trennung „kein `app.*` von Drittwheels“ durchsetzen will.

**Variante B′** nur, wenn organisatorisch **`app.*` im externen Wheel** verboten ist — dann Shim oder A wählen.

---

## 3. Packaging-Skizze (für das künftige Features-Repo)

### 3.1 Zielverzeichnisstruktur

```text
linux-desktop-chat-features/          # eigenes Git-Repo (später)
  pyproject.toml
  README.md
  src/
    app/
      features/
        __init__.py
        ...                             # heutiger Inhalt von app/features/
  tests/                                # optional: tests/unit/features + relevante Architekturtests verschieben
```

- **`src/`-Layout** vermeidet Import aus dem Repo-Root ohne Installation.  
- **`app` ist absichtlich** nur das übergeordnete Paketsegment für `app.features` (kein vollständiger Host-`app`-Tree im Wheel).

### 3.2 `pyproject.toml` (Skizze)

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "linux-desktop-chat-features"
version = "0.1.0"
description = "Feature platform for Linux Desktop Chat (app.features)"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
include = ["app*"]

# Keine project.entry-points hier nötig: Plugins registrieren weiterhin ihre eigenen EPs
# in der Gruppe "linux_desktop_chat.features".
```

### 3.3 Build / lokale Installation

```bash
cd linux-desktop-chat-features
python3 -m pip install -e .          # editable für Monorepo-Workspace / Entwicklung
python3 -m build                      # sdist + wheel für Release
```

### 3.4 Host-Abhängigkeit (nach Cut im Host-Repo)

In `linux-desktop-chat` / Host-`pyproject.toml`:

```toml
[project]
dependencies = [
  "linux-desktop-chat-features>=0.1.0",
  # ... bestehende deps (PySide6, ...)
]
```

Und **`include = ["app*"]` im Host** so anpassen, dass **`app/features` nicht mehr aus dem Host-Tree** gebaut wird (Ordner entfernt oder aus `exclude` — konkret: Verzeichnis `app/features` nur noch aus der Dependency).

---

## 4. Betroffene Host- und CI-Stellen beim echten Cut

### 4.1 Host-Repository (`linux-desktop-chat`)

| Bereich | Anpassung |
|---------|-----------|
| `pyproject.toml` | `linux-desktop-chat-features` in `dependencies`; Kommentar zu PEP-621-Drift (`dependency_packaging`) beibehalten — Modul kommt aus installiertem Paket. |
| `app/features/` | **Entfernen** (Quelle lebt nur im Features-Repo). |
| `run_gui_shell.py`, `app/gui/**` | Keine Änderung der Importstrings bei Variante B. |
| `examples/plugins/ldc_plugin_example` | `requires` / README: statt „nur Host installieren“ ggf. **`linux-desktop-chat-features`** explizit als Abhängigkeit des Beispiels für isolierte Umgebungen. |
| `app/packaging/landmarks.py` | Pfade zu Doku im Features-Repo ergänzen/verschieben; `REPO_LANDMARK_FILES` prüfen. |

### 4.2 CI / Werkzeuge

| Pfad | Anpassung |
|------|-----------|
| `tools/ci/release_matrix_ci.py` | Unveränderte Importe `app.features.release_matrix` / `dependency_packaging`, sobald das Features-Paket in der Job-Umgebung installiert ist. |
| `.github/workflows/*.yml` | Schritt **`pip install -e ../linux-desktop-chat-features`** oder **`pip install linux-desktop-chat-features==…`** vor `pytest` / Matrix-Skripten (je nach Mono- vs. Multi-Checkout). |
| `edition-smoke-matrix.yml`, `plugin-validation-smoke.yml` | Gleiches: sicherstellen, dass `app.features` importierbar ist (von Wheel). |

### 4.3 Tests / Guards (kritisch)

Diese lesen **Dateien unter** `APP_ROOT / "features"` und brechen, wenn `app/features` nur noch in `site-packages` liegt:

| Datei / Modul | Maßnahme |
|---------------|----------|
| `tests/architecture/test_edition_manifest_guards.py` | Pfade durch `importlib.util.find_spec("app.features")` → `origin` / Paketverzeichnis ersetzen, oder Datei-Inhalte über eingecheckte **Snapshot-Kopien** in `tests/fixtures/` (nicht empfohlen). |
| `tests/architecture/test_feature_system_guards.py` | `_iter_py_files_under("features")` auf Spezifikationsort des Pakets umstellen. |
| `tests/architecture/test_package_map_contract.py` | Prüfen, ob `TARGET_PACKAGES` / `EXTENDED` und Landmarken noch `features` als **Unterverzeichnis des Host-APP_ROOT** erwarten — ggf. `features` aus Host-`TARGET_PACKAGES` entfernen und nur als installierte Dependency dokumentieren (Architektur-Policy-Update). |

Segment-Guards (`segment_dependency_rules`, `arch_guard_config`) behalten logisch das Segment **`features`**; die **physische Lage** wechselt von Workspace zu site-packages — AST-Import-Tests bleiben gültig.

---

## 5. Execution Plan (kleine Commits — Zielbild)

| Commit | Inhalt |
|--------|--------|
| **1 — Packaging vorbereiten** | Neues Features-Repo (oder Branch) mit `src/app/features/`, `pyproject.toml`, `README`, `python -m build` grün; noch **kein** Host-Umbau. |
| **2 — Host: Abhängigkeit + Entfernen `app/features`** | Host-`pyproject` mit Pin; Verzeichnis `app/features` aus Host entfernt; lokaler Check: `pip install -e ../linux-desktop-chat-features` + `import app.features`. |
| **3 — CI umstellen** | Workflows: Installation Features-Paket vor Tests/Matrix; ggf. Checkout zweites Repo oder Wheel aus Artefakt. |
| **4 — Verifikation** | Guards auf `find_spec` umstellen; voll `pytest`, `release_matrix_ci.py`, Plugin-Smoke; Doku (PACKAGE_MAP, PLUGIN_GUIDE, CUT_READY) final an „zwei Distributions“ anpassen. |

Abhängigkeiten zwischen 2 und 3 können in einem Monorepo mit **zwei Roots** im gleichen Workflow zusammenfallen; die Commit-Trennung bleibt für Reviewbarkeit sinnvoll.

---

## 6. Pytest-Kommandos (nach Cut im Host-Workspace)

```bash
pip install -e ../path/to/linux-desktop-chat-features
pytest tests/architecture/test_features_public_surface_guard.py \
  tests/architecture/test_entry_point_contract_guard.py \
  tests/architecture/test_package_map_contract.py -q
pytest tests/unit/features/ -q
python3 tools/ci/release_matrix_ci.py
```

---

## 7. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Varianten A/B/B′, verbindliche Empfehlung B, Packaging-Skizze, Host/CI/Test-Impact, Execution Plan |
| 2026-03-25 | § 0: eingebettete Commit-1-Vorlage `linux-desktop-chat-features/` |
