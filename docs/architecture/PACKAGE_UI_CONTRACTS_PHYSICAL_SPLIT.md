# `app.ui_contracts` — Physischer Split (Variante B, Monorepo)

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Importpfad- und Packaging-Entscheidung**; Commits **1–4** im Monorepo (Vorlage, Host-Cut, CI, **Welle-2-Abschluss** — [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md)).  
**Bezug:** [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md), [`PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](PACKAGE_UI_CONTRACTS_SPLIT_READY.md), [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md), [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md) (Analogiemodell), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.8 / Matrix

---

## 0. Commit-1-Vorlage (im Host-Monorepo eingebettet)

Bis zur Auslagerung als eigenes Git-Repository liegt die **ausführbare Repo-Vorlage** unter:

**[`linux-desktop-chat-ui-contracts/`](../../linux-desktop-chat-ui-contracts/)** (Verzeichnis im Wurzelverzeichnis dieses Repos).

Inhalt: [`pyproject.toml`](../../linux-desktop-chat-ui-contracts/pyproject.toml), [`README.md`](../../linux-desktop-chat-ui-contracts/README.md), [`MIGRATION_CUT_LIST.md`](../../linux-desktop-chat-ui-contracts/MIGRATION_CUT_LIST.md), vollständiger Quellspiegel [`src/app/ui_contracts/`](../../linux-desktop-chat-ui-contracts/src/app/ui_contracts/), minimale Tests unter [`tests/unit/`](../../linux-desktop-chat-ui-contracts/tests/unit/). Verifikation: siehe README (`pip install -e ".[dev]"`, `pytest`, `python -m build`).

**Nach Commit 2:** Der Host hat **`app/ui_contracts/`** entfernt; kanonische Quelle ist die Vorlage / installiertes `app.ui_contracts` — siehe [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md).

---

## 1. Entscheidungsvorlage: Importpfad nach dem Cut

### Variante A — Neues Top-Level `ldc_ui_contracts` (oder `linux_desktop_chat.ui_contracts`)

| | Host | `ui_application` | GUI | Tests/Guards | SemVer |
|---|------|------------------|-----|--------------|--------|
| **Vorteile** | Kein `app.*` aus fremdem Wheel; theoretisch klarere „Vendor“-Grenze. | Explizite Trennung von Host-`app` und Library. | — | Ein Paket, ein Import-Root in der Theorie. | Eigener Paketname, klare Library-Version. |
| **Nachteile** | **Pflicht:** alle `from app.ui_contracts` → neuer Pfad (hunderte Stellen in `gui`, `ui_application`, `ui_runtime`, `global_overlay`, Tests). | Gleicher Massen-Wechsel in Presentern/Adaptern/Ports. | Vollständige Such-/Ersetz- und Review-Last. | Alle Architektur-Guards und Smoke-Strings mit `app.ui_contracts` anpassen; Segment-`ui_contracts` in `arch_guard_config` semantisch umbenennen oder Mapping dokumentieren. | Jeder Major am Contracts-Paket erzwingt koordinierten Host-PR. |

### Variante B — Importpfad `app.ui_contracts` bleibt (Paket im Wheel unter `app/ui_contracts/`)

| | Host | `ui_application` | GUI | Tests/Guards | SemVer |
|---|------|------------------|-----|--------------|--------|
| **Vorteile** | **Kein** Importstring-Wechsel: `from app.ui_contracts import …` und `from app.ui_contracts.workspaces…` bleiben. | **Kein** Umbau (nur Dependency + ggf. CI). | Sinks/Panels unverändert. | AST-Guards auf **`app.ui_contracts`-Importe** bleiten gültig; Anpassung nur dort, wo **Dateipfade** unter `APP_ROOT / "ui_contracts"` genutzt werden (siehe §4). | Distribution `linux-desktop-chat-ui-contracts` versioniert die Verträge; Host pinnt `>=x.y`. |
| **Nachteile** | Zwei Distributions können `app.*` liefern — **nur eine** darf `app/ui_contracts` enthalten (Host-Tree **entfernen**). | — | — | `test_ui_layer_guardrails` muss Quelle per `importlib.util.find_spec("app.ui_contracts")` finden (analog Features). | `app` im Namen eines externen Wheels ist ungewöhnlich, bei Features jedoch **bewusst** gewählt und hier übernommen. |

### Variante B′ — Namespace `linux_desktop_chat.ui_contracts` + Shim `app.ui_contracts` im Host

| | Host | `ui_application` | GUI | Tests/Guards | SemVer |
|---|------|------------------|-----|--------------|--------|
| **Idee** | Wheel liefert `linux_desktop_chat/ui_contracts/`; Host hält dünnes `app/ui_contracts` als Re-Export. | Kann schrittweise auf Namespace umstellen. | — | Zwei Installationslagen + Reihenfolge-Risiko. | Shim-Deprecation über Releases steuerbar. |
| **Nachteile** | Mehr Moving Parts; doppelte Wahrheit bis Migration fertig. | Mehraufwand ohne Nutzen solange Variante B ausreicht. | — | Höhere Fehlerwahrscheinlichkeit. | — |

---

## 2. Verbindliche Empfehlung (`ui_contracts`)

**Variante B:** Die Distribution **`linux-desktop-chat-ui-contracts`** (Arbeitsname, PyPI-konform mit Bindestrichen) liefert das Python-Paket **`app.ui_contracts`** (Verzeichnisbaum `app/ui_contracts/` im Wheel, z. B. `src/app/ui_contracts/` im späteren Contracts-Repo). Der Host **entfernt** das lokale Verzeichnis **`app/ui_contracts/`** und deklariert **`linux-desktop-chat-ui-contracts>=…`** in `[project] dependencies`.

**Begründung (kurz):**

- **Null Breaking** für die große Importfläche in `app.gui`, `app.ui_application`, `app.ui_runtime`, `app.global_overlay` und Tests — konsistent mit der verbindlichen Entscheidung bei **`app.features`** ([`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md) §2).
- **SemVer** und **Cut-Ready-Doku** ([`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md)) bleiben auf dem **bekannten** Symbolraum `app.ui_contracts` aufsetzbar.
- **Variante A** bleibt optionale **Major-Migration** später, falls das Projekt global „kein `app.*` aus Drittwheels“ durchsetzt.
- **Variante B′** nur bei harter organisatorischer Ablehnung von `app.*` im externen Wheel — dann eher **A** mit einmaligem Import-Bump statt dauerhaftem Shim.

---

## 3. Packaging-Skizze (Zielbild; Vorlage im Monorepo unter §0)

### 3.1 Zielverzeichnisstruktur (Contracts-Repo bzw. eingebettete Vorlage)

```text
linux-desktop-chat-ui-contracts/     # eigenes Git-Repo (später) bzw. Monorepo-Vorlage (jetzt)
  pyproject.toml
  README.md
  src/
    app/
      ui_contracts/
        __init__.py
        common/
        workspaces/
        ...
  tests/                               # optional: Paket-eigene Tests + verschobene Architektur-Slices
```

- **`src/`-Layout** vermeidet versehentliche Imports aus dem Repo-Root ohne Installation.  
- **`app` nur als Präfix** für `app.ui_contracts` — kein vollständiger Host-`app`-Tree im Wheel.

### 3.2 `pyproject.toml` (Skizze)

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "linux-desktop-chat-ui-contracts"
version = "0.1.0"
description = "Qt-free UI contracts for Linux Desktop Chat (app.ui_contracts)"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
include = ["app*"]
```

### 3.3 Host-Abhängigkeit (nach Cut im Host-Repo)

```toml
[project]
dependencies = [
  "linux-desktop-chat-ui-contracts>=0.1.0",
  # ... bestehende deps
]
```

Host-`setuptools` / `[tool.setuptools.packages.find]` so anpassen, dass **`app/ui_contracts` nicht mehr aus dem Host-Tree** in dasselbe Wheel wie der Host gemappt wird (Ordner entfernen oder explizit ausschließen).

### 3.4 Build / lokale Verifikation (Vorlage)

```bash
cd linux-desktop-chat-ui-contracts
python3 -m pip install -e ".[dev]"
pytest
python3 -m build
python3 -c "from app.ui_contracts import ChatWorkspaceState; print('ok')"
```

---

## 4. Betroffene Host-, Test- und Guard-Stellen beim echten Cut

### 4.1 Host-Repository

| Bereich | Anpassung |
|---------|-----------|
| `pyproject.toml` | `linux-desktop-chat-ui-contracts` in `dependencies`; Pin-Range festlegen. |
| `app/ui_contracts/` | **Entfernen** aus dem Host-Tree (Quelle nur noch im Contracts-Repo/Wheel). |
| `app/gui/**`, `app/ui_application/**`, `app/ui_runtime/**`, `app/global_overlay/**` | Bei **Variante B:** **keine** Importstring-Änderung. |
| `app/packaging/landmarks.py` | Prüfen, ob Pfade/Landmarken `ui_contracts` als **Host-Unterverzeichnis** erwarten (`test_package_map_contract` o. Ä.). |

### 4.2 Guards / Architekturtests (Dateipfade — Monorepo erledigt)

| Datei | Umsetzung (Commits 2–4) |
|-------|-------------------------|
| [`tests/architecture/test_ui_layer_guardrails.py`](../../tests/architecture/test_ui_layer_guardrails.py) | Qt-Check über [`app_ui_contracts_source_root()`](../../tests/architecture/app_ui_contracts_source_root.py) / `find_spec` |
| [`tests/architecture/test_ui_contracts_public_surface_guard.py`](../../tests/architecture/test_ui_contracts_public_surface_guard.py) | Walk nur `PROJECT_ROOT`; Ausschluss `app/ui_contracts/…` dokumentiert (Host ohne diesen Tree) |
| [`tests/architecture/test_package_map_contract.py`](../../tests/architecture/test_package_map_contract.py) | `ui_contracts` wie `features` per `find_spec` |
| [`tests/architecture/test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) | Ausgelagerte `.py` unter installierter Quelle, Präfix `ui_contracts/` |
| [`tests/architecture/arch_guard_config.py`](../../tests/architecture/arch_guard_config.py) | Segment-Kanten unverändert; Quelle der Module: installiertes Paket |
| [`app/qa/git_qa_report.py`](../../app/qa/git_qa_report.py) | `segments_from_changed_files`: eingebetteter Pfad `linux-desktop-chat-ui-contracts/src/app/ui_contracts/**` → **ui_contracts** (Commit 4) |

Abschluss-Doku: [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md).

### 4.3 CI / Workflows

| Thema | Anpassung |
|-------|-----------|
| Monorepo-GitHub-Actions | **Erledigt** (Commit 3): [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md) — Host-`pip install -e ".[…]"` plus **`pip install -e ./linux-desktop-chat-ui-contracts`** (und Features-Editable). |
| Nur Wheel / ohne eingebetteten Ordner | Später: **`pip install linux-desktop-chat-ui-contracts==…`** vor `pytest` (PyPI-Pin statt `file:`). |

### 4.4 Tests unter `tests/` (Funktional)

- **Kein** massaler Import-Umstieg bei Variante B.  
- Stichprobe: `tests/contracts/`, `tests/unit/gui/`, `tests/unit/ui_application/` nach Installation des Pakets grün.

---

## 5. Verbleibende Restblocker (nach dieser Entscheidung)

| Blocker | Beschreibung |
|---------|----------------|
| **Ausführung (Commit 1)** | Eingebettete Vorlage §0 — **erledigt**; eigenständiges Git-Repo / PyPI-Release bleiben **offen**. |
| **`find_spec`-Migration** | **Erledigt** (Commit 2): `test_ui_layer_guardrails`, Segment-Scan, `test_package_map_contract`. |
| **Host `pyproject` / setuptools** | **Erledigt** (Commit 2): `linux-desktop-chat-ui-contracts @ file:./…`; Host-Tree ohne `app/ui_contracts/`. |
| **CI-Matrix (Monorepo)** | **Erledigt** (Commit 3) — [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md). |
| **Guard-/QA-Abschluss Welle 2** | **Erledigt** (Commit 4) — [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md). |
| **`ui_application` Hybrid** | Unverändert architektonisch; **kein** Umbau — nur gemeinsame Versionierung bei Contract-Breaks ([`PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](PACKAGE_UI_CONTRACTS_SPLIT_READY.md) §11). |

---

## 6. Execution Plan (Zielbild — kleine Schritte, später auszuführen)

| Schritt | Inhalt |
|---------|--------|
| **1 — Packaging** | **Erledigt** (Commit 1): Vorlage §0. |
| **2 — Host** | **Erledigt** (Commit 2): `file:`-Dependency + Entfernen `app/ui_contracts/` — [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md). |
| **3 — Guards** | **Erledigt** (Commit 2): `find_spec` / ausgelagerter Quell-Scan. |
| **4 — CI** | **Erledigt** (Commit 3) — [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md); PyPI-only-Checkout später. |
| **5 — Verifikation** | Monorepo: [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md) §5. |

---

## 7. Pytest-Kommandos (nach Cut im Host-Workspace, Zielbild)

```bash
pip install -e ../path/to/linux-desktop-chat-ui-contracts
pytest tests/architecture/test_ui_layer_guardrails.py \
  tests/architecture/test_ui_contracts_public_surface_guard.py -q
pytest tests/contracts/test_chat_ui_contracts.py \
  tests/contracts/test_settings_appearance_contracts.py -q
```

---

## 8. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Varianten A / B / B′, **verbindliche Empfehlung B**, Packaging-Skizze, Host/Guard/CI-Folgen, Execution Plan |
| 2026-03-25 | Querverweise in CUT_READY (§4/§5.2/§8), WAVE2_PREP §10, SPLIT_READY, PACKAGE_MAP, PACKAGE_GUIDE, SPLIT_PLAN §3.8/Matrix, WAVE1_PREP §2.5 |
| 2026-03-25 | §0 Commit-1-Vorlage `linux-desktop-chat-ui-contracts/` im Monorepo; Status/§3/§5/§3.4 angepasst |
| 2026-03-25 | Commit 2: Host-Cut lokal; Status/§0/§5/§6; Verweis [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md) |
| 2026-03-25 | Commit 3: CI-Workflows; §6 Schritt 4; Status-Kopf; [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md) |
| 2026-03-25 | Commit 4: §4.2 Tabelle + §6 Schritt 5; QA-Segment; [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md) |
