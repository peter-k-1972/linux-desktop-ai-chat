# Commit 3 — CI auf installierte `linux-desktop-chat-providers` ausgerichtet

**Status:** Umgesetzt im Monorepo: alle Python/pytest-Workflows installieren nach dem Host-`pip install -e ".[…]"` zusätzlich **`pip install -e ./linux-desktop-chat-providers`** (neben Features, UI-Contracts und Pipelines), damit `app.providers` nicht aus veralteten `site-packages`-Kopien stammt — vgl. [`PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`](PACKAGE_PROVIDERS_COMMIT2_LOCAL.md) §3. Jobs mit expliziter Verify-Phase prüfen **`find_spec('app.providers')`** und einen kurzen Import von **`LocalOllamaProvider`** (wie bei den anderen eingebetteten Distributionen).

**Vorgänger:** [`PACKAGE_PROVIDERS_COMMIT2_LOCAL.md`](PACKAGE_PROVIDERS_COMMIT2_LOCAL.md)  
**Bezug:** [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md), [`PACKAGE_PROVIDERS_CUT_READY.md`](PACKAGE_PROVIDERS_CUT_READY.md), Analogien [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md), [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md), [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md)

---

## 1. Angepasste Workflows

| Workflow | Änderung |
|----------|----------|
| [`.github/workflows/pytest-full.yml`](../../.github/workflows/pytest-full.yml) | Kommentar; nach Host-Install **editable** `linux-desktop-chat-providers`; **Verify** `app.providers` + Kurzimport vor pytest |
| [`.github/workflows/edition-smoke-matrix.yml`](../../.github/workflows/edition-smoke-matrix.yml) | Kommentar; editable Providers in **prepare** und **edition-smoke**; **Verify** erweitert |
| [`.github/workflows/plugin-validation-smoke.yml`](../../.github/workflows/plugin-validation-smoke.yml) | Kommentar; **`paths`**: `linux-desktop-chat-providers/**`; editable + Verify in **prepare** und **plugin-smoke** |
| [`.github/workflows/context-observability.yml`](../../.github/workflows/context-observability.yml) | Kommentar; editable Providers nach den anderen eingebetteten Paketen |
| [`.github/workflows/model-usage-gate.yml`](../../.github/workflows/model-usage-gate.yml) | Kommentar; editable Providers |
| [`.github/workflows/markdown-quality.yml`](../../.github/workflows/markdown-quality.yml) | Kommentar; editable Providers (einheitliches Monorepo-Install / PEP-621-Kontext) |
| [`tools/ci/release_matrix_ci.py`](../../tools/ci/release_matrix_ci.py) | Modul-Docstring: Voraussetzungen inkl. `linux-desktop-chat-providers` vor `validate` |

---

## 2. Unverändert (bewusst)

| Thema | Begründung |
|--------|------------|
| **`edition-smoke-matrix` `on:`-Trigger** | Läuft weiter auf allen PRs zu `main`/`develop` — keine neuen `paths`-Filter. |
| **Architekturtests** | Nutzen weiterhin `app_providers_source_root()` / `find_spec("app.providers")` (Commit 2); in CI liefern die editables die aktuelle Quelle. |
| **Release-Matrix / `builtins.core`** | `linux-desktop-chat-providers` steht bereits in `DependencyGroupDescriptor.python_packages` (PEP-621-Drift-Check); keine Logikänderung in `release_matrix_ci.py`. |
| **Git-QA-Segmente** | `segments_from_changed_files`: `linux-desktop-chat-providers/src/app/providers/**` → **providers** (Commit 2). |

---

## 3. Monorepo-Annahmen (weiter gültig)

- Checkout enthält **`linux-desktop-chat-providers/`** neben Host-Root; **`file:./linux-desktop-chat-providers`** im Host-`pyproject.toml` ist auflösbar.
- **`GITHUB_WORKSPACE`** = Host-Root; **`LDC_REPO_ROOT=${{ github.workspace }}`** in den Jobs unverändert.
- Kein zweiter Checkout nur für Providers; kein separates PyPI-Wheel in dieser Welle.

---

## 4. CI-Pfade, die jetzt „Commit-3-korrekt“ sind

- **Plugin-Validation-PR-Trigger:** auch Änderungen unter **`linux-desktop-chat-providers/**`**.
- **pytest-full / Edition-Smoke / Plugin-Smoke:** konsistente Kette Host → editable Features → editable UI-Contracts → editable Pipelines → **editable Providers** + Verify wo vorhanden.
- **Gates ohne eigene Verify-Zeile** (context-observability, model-usage-gate, markdown-quality): gleiche Install-Kette, damit transitive Imports und PEP-621-Checks nicht an fehlendem `app.providers` scheitern.

---

## 5. PyPI / spätere Entkopplung

- **PyPI-Pin** statt `file:./linux-desktop-chat-providers`: Host-`pyproject` und alle Workflows anpassen; Release-Notes für die Distribution (siehe [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md)).
- Nach Publish: CI kann `pip install linux-desktop-chat-providers>=…` nutzen, wenn das Repo keine eingebettete Vorlage mehr mitführt.

---

## 6. Verifikationskommandos (lokal, spiegelt CI-Kern)

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
.venv/bin/python - <<'PY'
from app.providers import LocalOllamaProvider
print("providers ok")
PY
.venv/bin/python tools/ci/release_matrix_ci.py validate
.venv/bin/pytest tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py -q
```

---

## 7. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Workflows + `release_matrix_ci`-Docstring |
