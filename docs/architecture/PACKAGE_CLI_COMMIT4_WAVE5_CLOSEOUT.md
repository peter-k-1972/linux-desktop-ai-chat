# Commit 4 — Welle 5 `app.cli`: Abschluss (Monorepo)

**Status:** Abschluss der **physischen Paketlage** und der zugehörigen Guards/QA/CI für `app.cli` im eingebetteten Monorepo. Die kanonische Implementierung liegt in der Distribution **`linux-desktop-chat-cli`** (Vorlage [`linux-desktop-chat-cli/`](../../linux-desktop-chat-cli/)); der Host-Tree enthält kein `app/cli/` mehr. Importpfad unverändert **`app.cli`** (Namespace über `pkgutil.extend_path` im Host-`app`).

**Vorgänger / API:** [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md), [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md), [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md)  
**Parallele Wellen:** Welle 3 [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md), Welle 4 [`PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md`](PACKAGE_PROVIDERS_COMMIT4_WAVE4_CLOSEOUT.md)

---

## 1. Übersicht Commit 1–4

| Commit | Inhalt |
|--------|--------|
| **Commit 1 (Vorlage)** | Verzeichnis **`linux-desktop-chat-cli/`**: `pyproject.toml`, `README.md`, `MIGRATION_CUT_LIST.md`, vollständiger Spiegel **`src/app/cli/**`**, `src/app/__init__.py`. Tests: `tests/test_imports.py` (Paketmarker + Dateibaum), `tests/test_basic_runtime.py` (Skip, wenn `app.context` fehlt). Keine neuen PyPI-Laufzeitabhängigkeiten (stdlib + impliziter Host). |
| **Commit 2 (Host-Cut)** | Host-[`pyproject.toml`](../../pyproject.toml): **`linux-desktop-chat-cli @ file:./linux-desktop-chat-cli`** (gleiches Muster wie Features/UI-Contracts/Pipelines/Providers). **`app/cli/`** im Host entfernt. Landmarken [`landmarks.py`](../../app/packaging/landmarks.py), `test_package_map_contract` (`find_spec("app.cli")`), Segment-AST mit [`app_cli_source_root()`](../../tests/architecture/app_cli_source_root.py) und synthetischem Präfix **`cli/…`**, Public-Surface-Guard [`test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py), Git-QA **`linux-desktop-chat-cli/src/app/cli/**` → Segment **cli**. **`builtins.core.python_packages`:** `linux-desktop-chat-cli` (PEP-621-Drift). |
| **Commit 3 (CI)** | Workflows u. a. [`pytest-full.yml`](../../.github/workflows/pytest-full.yml), [`edition-smoke-matrix.yml`](../../.github/workflows/edition-smoke-matrix.yml), [`plugin-validation-smoke.yml`](../../.github/workflows/plugin-validation-smoke.yml), [`context-observability.yml`](../../.github/workflows/context-observability.yml), [`model-usage-gate.yml`](../../.github/workflows/model-usage-gate.yml), [`markdown-quality.yml`](../../.github/workflows/markdown-quality.yml): nach Host-Install **`pip install -e ./linux-desktop-chat-cli`**; Verify **`find_spec('app.cli')`** plus Kurzsnippet `print("cli ok")` (siehe Workflow-„Verify“-Steps). [`release_matrix_ci.py`](../../tools/ci/release_matrix_ci.py) dokumentiert/validiert eingebettete Distributionen inkl. CLI. |
| **Commit 4 (Wave Closeout)** | Dieses Dokument; [`PACKAGE_MAP.md`](PACKAGE_MAP.md) (CLI → **abgeschlossen**); [`PACKAGE_GUIDE.md`](../../docs/developer/PACKAGE_GUIDE.md) (Segment CLI, Importpfad, Guard-Verweis); Governance-Restabgleich ohne API-/Laufzeitänderung. |

---

## 2. Finaler Zustand nach Welle 5

| Thema | Zustand |
|--------|---------|
| **Distribution** | `linux-desktop-chat-cli` (eingebettet, `file:./…` im Host) |
| **Import** | Submodule-first wie in [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) §3; Einstieg weiterhin **`python -m app.cli.<modul>`** (keine neuen Console-Scripts) |
| **Host** | Kein Verzeichnis **`app/cli/`** |
| **Laufzeit** | CLI bleibt **nicht standalone**: transitive Kette über `app.context` → Engine → `chat_service` → `app.chat` / `app.core` (Cut-Ready §6) |
| **CI** | Editables + `find_spec` integriert |
| **PEP-621 / core** | `linux-desktop-chat-cli` in **`DependencyGroupDescriptor.python_packages`** der Gruppe **core** ([`builtins.py`](../../linux-desktop-chat-features/src/app/features/dependency_groups/builtins.py)) |
| **Package-Map-Vertrag** | `cli` per **`find_spec("app.cli")`**; Landmarken unter `linux-desktop-chat-cli/…` |
| **Segment-AST** | [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) + **`app_cli_source_root()`** |
| **Public Surface** | [`test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py) |

---

## 3. Monorepo-spezifisch (bewusst, bis PyPI / Repo-Split)

| Punkt | Begründung |
|--------|------------|
| `file:./linux-desktop-chat-cli` im Host-`pyproject.toml` | Kein Index-Pin in Welle 5; gleiches Muster wie andere eingebettete Distributionen |
| Isolierte CLI-Tests ohne Host | `test_basic_runtime.py` skipped, wenn `app.context` fehlt — erwartbar für `pip install -e ./linux-desktop-chat-cli` allein |
| `REPO_LANDMARK_FILES` / Handbuch-Tools | Verweise auf eingebettete Vorlage `linux-desktop-chat-cli/src/…` |

---

## 4. Offene Restpunkte — **ohne** Wellenabschluss-Blocker

- **PyPI-Pin** statt `file:./linux-desktop-chat-cli` und CI ohne eingebetteten Ordner — späteres Release-Thema.
- **Release-Notes / API-Changelog** für öffentliche `run_*`-Oberfläche (Cut-Ready §3.2), sobald ein Wheel veröffentlicht wird.
- **Veraltete Pfade `app/cli/…`** in älteren Handbüchern, LaTeX/Manual-Index — schrittweise auf Vorlage bzw. „installiertes `app.cli`“ umstellen.
- **Nicht CLI-spezifisch:** Hybrid-Segmente, Root-/Startup-Governance, sonstige Repo-weiten Guards — unverändert eigenständige Themen.

---

## 5. Empfohlene Abschluss-Verifikation

```bash
cd Linux-Desktop-Chat
export LDC_REPO_ROOT="$(pwd)"
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install -e ./linux-desktop-chat-features
.venv/bin/pip install -e ./linux-desktop-chat-ui-contracts
.venv/bin/pip install -e ./linux-desktop-chat-pipelines
.venv/bin/pip install -e ./linux-desktop-chat-providers
.venv/bin/pip install -e ./linux-desktop-chat-cli

.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.cli') is not None; print('cli ok')"

.venv/bin/pytest tests/architecture/test_cli_public_surface_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py \
  tests/cli/ -q

.venv/bin/pytest linux-desktop-chat-cli/tests/ -q
.venv/bin/python tools/ci/release_matrix_ci.py validate
```

---

## 6. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Welle-5-Abschluss, Commits 1–3, finaler Zustand, Restpunkte |
| 2026-03-25 | §1 auf „Commit 1–4“ erweitert; CI-Workflow-Liste inkl. `cli ok`-Verify ergänzt |
