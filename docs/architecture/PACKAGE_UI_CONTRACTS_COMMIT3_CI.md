# Commit 3 — CI auf installierte `linux-desktop-chat-ui-contracts` ausgerichtet

**Status:** Umgesetzt im Monorepo: alle Python/pytest-Workflows installieren nach dem Host-`pip install -e ".[…]"` zusätzlich **`pip install -e ./linux-desktop-chat-features`** und **`pip install -e ./linux-desktop-chat-ui-contracts`** (vermeidet veraltete `site-packages`-Kopien der eingebetteten Pakete, vgl. [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md) §2). Matrix-/Plugin-Jobs prüfen **`find_spec('app.ui_contracts')`** neben `app.features`.

**Vorgänger:** [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md)  
**Bezug:** [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md), [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md), Features-Analogon [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md)

---

## 1. Angepasste Workflows

| Workflow | Änderung |
|----------|----------|
| [`.github/workflows/pytest-full.yml`](../../.github/workflows/pytest-full.yml) | Kommentar; nach Host-Install **editables** Features + UI-Contracts; **Verify** `app.features` + `app.ui_contracts` vor pytest |
| [`.github/workflows/edition-smoke-matrix.yml`](../../.github/workflows/edition-smoke-matrix.yml) | Kommentar; editables in **prepare** und **edition-smoke**; **Verify** erweitert |
| [`.github/workflows/plugin-validation-smoke.yml`](../../.github/workflows/plugin-validation-smoke.yml) | Kommentar; **`paths`**: `linux-desktop-chat-ui-contracts/**`; editables + Verify in **prepare** und **plugin-smoke** |
| [`.github/workflows/context-observability.yml`](../../.github/workflows/context-observability.yml) | Kurzkommentar; editables nach `pip install -e ".[rag,dev]"` |
| [`.github/workflows/model-usage-gate.yml`](../../.github/workflows/model-usage-gate.yml) | Kurzkommentar; editables |
| [`.github/workflows/markdown-quality.yml`](../../.github/workflows/markdown-quality.yml) | Kurzkommentar; editables (einheitliches Monorepo-Setup / PEP-621-Kontext) |
| [`tools/ci/release_matrix_ci.py`](../../tools/ci/release_matrix_ci.py) | Modul-Docstring: Voraussetzungen Features + UI-Contracts / PEP-621 |

---

## 2. Unverändert (bewusst)

| Thema | Begründung |
|--------|------------|
| **`edition-smoke-matrix` `on:`-Trigger** | Läuft weiter auf allen PRs zu `main`/`develop` — keine neuen `paths`-Filter (Abwägung Laufzeit vs. Risiko unverändert). |
| **Kombinierte Composite Action** | Nicht eingeführt — YAML-Duplikat bewusst klein gehalten (Commit 4 / spätere Welle). |
| **`release_matrix_ci.py` Logik** | Keine funktionale Änderung; nur Docstring. Kein direkter `ui_contracts`-Import im Skript. |

---

## 3. Monorepo-Annahmen (weiter gültig)

- Checkout enthält **`linux-desktop-chat-features/`** und **`linux-desktop-chat-ui-contracts/`** neben dem Host-Root; beide **`file:./…`**-Einträge im Host-`pyproject.toml` sind auflösbar.
- **`GITHUB_WORKSPACE`** = Host-Root; **`LDC_REPO_ROOT=${{ github.workspace }}`** in den Jobs wie bei Features Commit 3.
- Kein zweiter GitHub-Checkout nur für Contracts; kein PyPI-Wheel in dieser Welle.

---

## 4. CI-Pfade, die jetzt „Commit-3-korrekt“ sind

- **Plugin-Validation-PR-Trigger:** auch Änderungen unter **`linux-desktop-chat-ui-contracts/**`** (neben Features, `pyproject.toml`, …).
- **Alle pytest-/Matrix-Jobs:** konsistente Install-Kette Host → **editable Features** → **editable UI-Contracts**.
- **Frühfail:** `pytest-full`, Edition-/Plugin-Matrix mit **Verify** für `app.ui_contracts`, bevor teure Suites laufen.

---

## 5. Restpunkte (nach Commit 4 Welle 2)

- **Monorepo-Abschluss `ui_contracts`:** erledigt in [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md).
- **PyPI-Pin** statt `file:./…`: Workflows ohne eingebettete Verzeichnisse anpassen.
- **Wiederverwendbare Action** „install monorepo host + verify embedded distributions“.
- **`test_app_package_guards` / App-Root-Policy:** produktübergreifend, nicht `ui_contracts`-spezifisch.

---

## 6. Verifikationskommandos (lokal, spiegelt CI-Kern)

```bash
cd Linux-Desktop-Chat
export LDC_REPO_ROOT="$(pwd)"
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install -e ./linux-desktop-chat-features
.venv/bin/pip install -e ./linux-desktop-chat-ui-contracts
.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.features')"
.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.ui_contracts')"
.venv/bin/python tools/ci/release_matrix_ci.py validate
.venv/bin/pytest tests/architecture/test_ui_layer_guardrails.py \
  tests/architecture/test_package_map_contract.py -q
```

---

## 7. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: alle Workflows + `release_matrix_ci`-Docstring |
| 2026-03-25 | §5: Verweis Commit 4 Welle-2-Abschluss |
