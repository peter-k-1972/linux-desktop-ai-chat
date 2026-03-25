# Commit 3 — CI auf installierte `linux-desktop-chat-pipelines` ausgerichtet

**Status:** Umgesetzt im Monorepo: alle Python/pytest-Workflows installieren nach dem Host-`pip install -e ".[…]"` zusätzlich **`pip install -e ./linux-desktop-chat-pipelines`** (neben Features und UI-Contracts), damit `app.pipelines` nicht aus veralteten `site-packages`-Kopien stammt — vgl. [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](PACKAGE_PIPELINES_COMMIT2_LOCAL.md) §2. Jobs mit expliziter Verify-Phase prüfen **`find_spec('app.pipelines')`** neben `app.features` und `app.ui_contracts`.

**Vorgänger:** [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](PACKAGE_PIPELINES_COMMIT2_LOCAL.md)  
**Bezug:** [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md), [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md), Analogien [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md), [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md)

---

## 1. Angepasste Workflows

| Workflow | Änderung |
|----------|----------|
| [`.github/workflows/pytest-full.yml`](../../.github/workflows/pytest-full.yml) | Kommentar; nach Host-Install **editable** `linux-desktop-chat-pipelines`; **Verify** `app.pipelines` vor pytest |
| [`.github/workflows/edition-smoke-matrix.yml`](../../.github/workflows/edition-smoke-matrix.yml) | Kommentar; editable Pipelines in **prepare** und **edition-smoke**; **Verify** erweitert |
| [`.github/workflows/plugin-validation-smoke.yml`](../../.github/workflows/plugin-validation-smoke.yml) | Kommentar; **`paths`**: `linux-desktop-chat-pipelines/**`; editable + Verify in **prepare** und **plugin-smoke** |
| [`.github/workflows/context-observability.yml`](../../.github/workflows/context-observability.yml) | Kommentar; editable Pipelines nach den anderen eingebetteten Paketen |
| [`.github/workflows/model-usage-gate.yml`](../../.github/workflows/model-usage-gate.yml) | Kommentar; editable Pipelines |
| [`.github/workflows/markdown-quality.yml`](../../.github/workflows/markdown-quality.yml) | Kommentar; editable Pipelines (einheitliches Monorepo-Install / PEP-621-Kontext) |
| [`tools/ci/release_matrix_ci.py`](../../tools/ci/release_matrix_ci.py) | Modul-Docstring: Voraussetzungen inkl. `linux-desktop-chat-pipelines` vor `validate` |

---

## 2. Unverändert (bewusst)

| Thema | Begründung |
|--------|------------|
| **`edition-smoke-matrix` `on:`-Trigger** | Läuft weiter auf allen PRs zu `main`/`develop` — keine neuen `paths`-Filter. |
| **Kombinierte Composite Action** | Nicht eingeführt — YAML-Duplikat bewusst klein gehalten (**Commit 4** / spätere Konsolidierung). |
| **`release_matrix_ci.py` Logik** | Keine funktionale Änderung; nur Docstring. |

---

## 3. Monorepo-Annahmen (weiter gültig)

- Checkout enthält **`linux-desktop-chat-pipelines/`** neben Host-Root; **`file:./linux-desktop-chat-pipelines`** im Host-`pyproject.toml` ist auflösbar.
- **`GITHUB_WORKSPACE`** = Host-Root; **`LDC_REPO_ROOT=${{ github.workspace }}`** in den Jobs unverändert.
- Kein zweiter Checkout nur für Pipelines; kein separates PyPI-Wheel in dieser Welle.

---

## 4. CI-Pfade, die jetzt „Commit-3-korrekt“ sind

- **Plugin-Validation-PR-Trigger:** auch Änderungen unter **`linux-desktop-chat-pipelines/**`**.
- **pytest-full / Edition-Smoke / Plugin-Smoke:** konsistente Kette Host → editable Features → editable UI-Contracts → **editable Pipelines** + Verify wo vorhanden.
- **Gates ohne eigene Verify-Zeile** (context-observability, model-usage-gate, markdown-quality): gleiche Install-Kette, damit transitive Imports und PEP-621-Checks nicht an fehlendem `app.pipelines` scheitern.

---

## 5. Restpunkte nach Commit 4 (Welle 3)

- **Guard-/Doku-Abschluss Pipelines:** [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md).
- **Wiederverwendbare Action** „install host + verify embedded distributions“ (Features + UI-Contracts + Pipelines) — optional, produktübergreifend.
- **PyPI-Pin** statt `file:./…`: Workflows ohne eingebettete Verzeichnisse anpassen.
- **Release-Notes / Changelog** für `linux-desktop-chat-pipelines` (siehe [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) §5).

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
.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.features')"
.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.ui_contracts')"
.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.pipelines')"
.venv/bin/python tools/ci/release_matrix_ci.py validate
.venv/bin/pytest tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py -q
```

---

## 7. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: alle Workflows + `release_matrix_ci`-Docstring |
| 2026-03-25 | §5: Verweis Commit 4 Welle-3-Abschluss |
