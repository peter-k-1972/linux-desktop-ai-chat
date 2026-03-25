# Commit 4 — Welle 4 `app.providers`: Abschluss (Monorepo)

**Status:** Abschluss der **physischen Paketlage** und der zugehörigen Guards/QA/CI für `app.providers` im eingebetteten Monorepo. Die kanonische Implementierung liegt in der Distribution **`linux-desktop-chat-providers`** (Vorlage [`linux-desktop-chat-providers/`](../../linux-desktop-chat-providers/)); der Host-Tree enthält kein `app/providers/` mehr. Importpfad unverändert **`app.providers`** (Namespace über `pkgutil.extend_path` im Host-`app`).

**Vorgänger:** [`PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`](PACKAGE_PROVIDERS_COMMIT2_LOCAL.md), [`PACKAGE_PROVIDERS_COMMIT3_CI.md`](PACKAGE_PROVIDERS_COMMIT3_CI.md)  
**API / DoR / Packaging:** [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md), [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md), [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md)

---

## 1. Commits 1–3 — Kurzüberblick

| Commit | Inhalt |
|--------|--------|
| **Commit 1 (Vorlage)** | Verzeichnis **`linux-desktop-chat-providers/`**: `pyproject.toml`, README, `MIGRATION_CUT_LIST.md`, vollständiger Spiegel **`src/app/providers/**`**. Zusätzlich **`src/app/utils/env_loader.py`** (+ `__init__.py`), damit `cloud_ollama_provider` isoliert importierbar bleibt (siehe [`PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`](PACKAGE_PROVIDERS_COMMIT2_LOCAL.md) §1). Mindesttests, lokaler editable-Install und Build grün. |
| **Commit 2 (Host-Cut)** | Host-[`pyproject.toml`](../../pyproject.toml): **`linux-desktop-chat-providers @ file:./linux-desktop-chat-providers`**. **`app/providers/`** im Host entfernt. **`app/ollama_client.py`** bleibt **Übergangsbrücke** (Re-Export aus `app.providers.ollama_client`). Landmarken, `test_package_map_contract` (`find_spec("app.providers")`), Segment-AST mit [`app_providers_source_root()`](../../tests/architecture/app_providers_source_root.py) und Präfix `providers/…`, Public-Surface-Guard, Provider-Orchestrator-Guards (Pfad über installierte Quelle), `ALLOWED_PROVIDER_STRING_FILES` auf Vorlagenpfade, Git-QA **`linux-desktop-chat-providers/src/app/providers/**` → Segment `providers`**, **`…/src/app/utils/**` → `utils`**. **`builtins.core.python_packages`:** `linux-desktop-chat-providers` (PEP-621-Drift). |
| **Commit 3 (CI)** | Alle relevanten Workflows: nach Host-Install zusätzlich **`pip install -e ./linux-desktop-chat-providers`**; Verify **`find_spec('app.providers')`** und Kurzimport **`LocalOllamaProvider`** wo die anderen eingebetteten Distributionen bereits verifiziert werden; Plugin-Validation **`paths`** inkl. `linux-desktop-chat-providers/**`. [`PACKAGE_PROVIDERS_COMMIT3_CI.md`](PACKAGE_PROVIDERS_COMMIT3_CI.md), Docstring in [`tools/ci/release_matrix_ci.py`](../../tools/ci/release_matrix_ci.py). |

---

## 2. Finaler Zustand nach Welle 4

| Thema | Zustand |
|--------|---------|
| **Distribution** | `linux-desktop-chat-providers` (eingebettet, `file:./…` im Host) |
| **Import** | `from app.providers import …` / Submodule wie in [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md) §3.2 |
| **Host** | Kein Verzeichnis **`app/providers/`** |
| **Brücke** | **`app/ollama_client.py`** → Re-Export aus `app.providers.ollama_client` (transitional, bewusst) |
| **CI** | Editables + Verify integriert ([`PACKAGE_PROVIDERS_COMMIT3_CI.md`](PACKAGE_PROVIDERS_COMMIT3_CI.md)) |
| **PEP-621 / core** | `linux-desktop-chat-providers` in **`DependencyGroupDescriptor.python_packages`** der Gruppe **core** ([`builtins.py`](../../linux-desktop-chat-features/src/app/features/dependency_groups/builtins.py)) |
| **Package-Map-Vertrag** | `providers` per **`find_spec("app.providers")`**; Landmarken unter `linux-desktop-chat-providers/…` ([`landmarks.py`](../../app/packaging/landmarks.py)) |
| **Segment-AST** | [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) + **`app_providers_source_root()`**, synthetisches Präfix **`providers/`** |
| **Public Surface** | [`test_providers_public_surface_guard.py`](../../tests/architecture/test_providers_public_surface_guard.py) |
| **Provider-Governance** | u. a. [`test_provider_orchestrator_governance_guards.py`](../../tests/architecture/test_provider_orchestrator_governance_guards.py), [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py) `ALLOWED_PROVIDER_STRING_FILES` mit Pfaden unter `linux-desktop-chat-providers/src/app/providers/` |
| **QA-Segmente** | [`segments_from_changed_files()`](../../app/qa/git_qa_report.py) |

---

## 3. Monorepo-spezifisch (bewusst, bis PyPI / Repo-Split)

| Punkt | Begründung |
|--------|------------|
| `file:./linux-desktop-chat-providers` im Host-`pyproject.toml` | Kein Index-Pin in Welle 4 |
| Doppelte **`app.utils.env_loader`** (Host + Vorlage) | Nur für isolierbares Provider-Wheel; Inhaltliche Parität zwischen beiden Dateien beibehalten ([`PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`](PACKAGE_PROVIDERS_COMMIT2_LOCAL.md) §1) |
| `REPO_LANDMARK_FILES` / Handbuch-Tools | Verweise auf eingebettete Vorlage `linux-desktop-chat-providers/src/…` |

---

## 4. Offene Restpunkte — **ohne** Wellenabschluss-Blocker

- **PyPI-Pin** statt `file:./linux-desktop-chat-providers` und CI ohne eingebetteten Ordner (Wheel aus Index oder zweiter Checkout) — siehe [`PACKAGE_PROVIDERS_COMMIT3_CI.md`](PACKAGE_PROVIDERS_COMMIT3_CI.md) §5.
- **Release-Notes / API-Changelog** für das Wheel (offen laut physischer Split-/Cut-Ready-Doku, wo erwähnt).
- **Übergangsbrücke `app/ollama_client.py`** und zugehörige **Governance-Ausnahmen** in `arch_guard_config` (`KNOWN_IMPORT_EXCEPTIONS` u. ä.) — später optional bereinigen, wenn alle Konsumenten direkt `app.providers.ollama_client` nutzen.
- **Veraltete Pfade `app/providers/…`** in älteren Handbüchern, Release-Audit, LaTeX/Manual-Index — schrittweise auf Vorlage oder „installiertes `app.providers`“ umstellen (gleiche Kategorie wie bei Pipelines nach Welle 3).
- **Grenze Core ↔ Providers** (Dokumente wie [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md)): weiterführendes Architekturthema; **keine** neue Entscheidung in Welle 4 getroffen.
- **Nicht providers-spezifisch:** Hybrid-Segmente, Root-/Startup-Governance, sonstige Repo-weiten Guards — unverändert eigenständige Themen.

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

.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.providers')"
.venv/bin/python -c "from app.providers import LocalOllamaProvider; from app.ollama_client import OllamaClient; print('ok')"

.venv/bin/pytest tests/architecture/test_providers_public_surface_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py \
  tests/architecture/test_provider_orchestrator_governance_guards.py -q

.venv/bin/pytest tests/unit/dev/test_git_qa_report.py -q
.venv/bin/python tools/ci/release_matrix_ci.py validate
```

---

## 6. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Welle-4-Abschluss, Commits 1–3, finaler Zustand, Restpunkte |
