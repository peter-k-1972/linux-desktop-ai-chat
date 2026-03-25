# Commit 3 — CI auf installierte `linux-desktop-chat-features` ausgerichtet

**Status:** Umgesetzt im Monorepo-Checkout: Workflows verlassen sich auf `pip install -e ".[…]"` (zieht `linux-desktop-chat-features @ file:./linux-desktop-chat-features`), setzen **`LDC_REPO_ROOT`** für Pfad-Checks in `app.features.release_matrix`, und die Plugin-Pipeline triggert bei allen relevanten Änderungen an der eingebetteten Distribution.

**Vorgänger:** [`PACKAGE_FEATURES_COMMIT2_LOCAL.md`](PACKAGE_FEATURES_COMMIT2_LOCAL.md)  
**Bezug:** [`PACKAGE_FEATURES_CUT_READY.md`](PACKAGE_FEATURES_CUT_READY.md), [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md)

---

## 1. Angepasste Workflows

| Workflow | Änderung |
|----------|----------|
| [`.github/workflows/plugin-validation-smoke.yml`](../../.github/workflows/plugin-validation-smoke.yml) | Kommentar Monorepo/Distribution; **`paths`**: `linux-desktop-chat-features/**`, **`pyproject.toml`**; **`LDC_REPO_ROOT`** auf allen Jobs; Schritt **Verify app.features** nach `pip install` |
| [`.github/workflows/edition-smoke-matrix.yml`](../../.github/workflows/edition-smoke-matrix.yml) | Kommentar; **`LDC_REPO_ROOT`**; **Verify app.features** nach `pip install` |
| [`.github/workflows/pytest-full.yml`](../../.github/workflows/pytest-full.yml) | Kurzkommentar zu Features-Dependency; **`LDC_REPO_ROOT`** |
| [`.github/workflows/context-observability.yml`](../../.github/workflows/context-observability.yml) | **`LDC_REPO_ROOT`** |
| [`.github/workflows/model-usage-gate.yml`](../../.github/workflows/model-usage-gate.yml) | **`LDC_REPO_ROOT`** |
| [`.github/workflows/markdown-quality.yml`](../../.github/workflows/markdown-quality.yml) | **`LDC_REPO_ROOT`** |
| [`tools/ci/release_matrix_ci.py`](../../tools/ci/release_matrix_ci.py) | Modul-Docstring: Install-Voraussetzung + `GITHUB_WORKSPACE` / `LDC_REPO_ROOT` |

---

## 2. Unverändert (bewusst)

| Workflow | Begründung |
|----------|------------|
| Alle genannten | Weiterhin **kein** separater `pip install ./linux-desktop-chat-features` nötig — der Host-`pyproject.toml`-Eintrag genügt bei `pip install -e .`. |
| `pytest-full`, `context-observability`, `model-usage-gate`, `markdown-quality` | Kein zusätzlicher **Verify**-Schritt: volle Suite bzw. gemarkte Tests scheitern ohnehin bei fehlendem `app.features`. |

---

## 3. Monorepo-Annahmen (bis Commit 4 / PyPI)

- Checkout enthält **`linux-desktop-chat-features/`** neben dem Host-Root; **`file:./linux-desktop-chat-features`** ist auflösbar.
- **`GITHUB_WORKSPACE`** zeigt auf den Host-Repo-Root (Standard bei `actions/checkout@v4`); **`LDC_REPO_ROOT`** wird explizit gleich gesetzt, damit `release_matrix._repo_root_for_matrix_checks()` zuverlässig **`tests/unit/features`** findet (zusätzlich zu `GITHUB_WORKSPACE` im Code).
- Es gibt **keinen** zweiten GitHub-Repo-Checkout nur für Features; kein Release einer separaten Wheel-Version in dieser Welle.

---

## 4. CI-Pfade, die jetzt „Commit-3-korrekt“ sind

- **Trigger Plugin-Smoke:** Änderungen unter **`linux-desktop-chat-features/**`** (nicht nur `src/app/features`), plus **`pyproject.toml`** (Pin/Dependency).
- **Matrix/Validierung:** Läuft weiter über **`tools/ci/release_matrix_ci.py`** und **`app.features.*`** nach Installation — keine Verweise auf entferntes Host-**`app/features/`**.
- **Alle Python-Jobs mit pytest / Matrix:** **`LDC_REPO_ROOT=${{ github.workspace }}`**, konsistent mit lokalen Empfehlungen in Commit 2.

---

## 5. Restpunkte nach Commit 3

- **Commit 4 (Welle 1 Abschluss):** Guard-/Test-Bereinigung für ausgelagerte `app.features`-Quelle — siehe [`PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md).
- **PyPI-Pin** statt `file:./…`: Workflows dann ohne eingebettetes Verzeichnis (eigenes Checkout-Modell oder `pip install linux-desktop-chat-features>=…`).
- **Wiederverwendbare Action** „install host + verify features“, um YAML-Duplikat zu reduzieren.
- **`edition-smoke-matrix`:** optionale **`paths`**-Filter, um bei rein dokumentarischen PRs Laufzeit zu sparen (Abwägung vs. Integrationsrisiko).
- **`test_app_package_guards` / App-Root-Policy:** nicht features-spezifisch; ggf. separat bereinigen.

---

## 6. Verifikationskommandos (lokal, spiegelt CI-Kern)

```bash
cd Linux-Desktop-Chat
export LDC_REPO_ROOT="$(pwd)"
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -c "import importlib.util as u; assert u.find_spec('app.features')"
.venv/bin/python tools/ci/release_matrix_ci.py validate
.venv/bin/python tools/ci/release_matrix_ci.py print-matrix-json | head -c 200
```

---

## 7. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung nach Commit-3-Workflow-Anpassungen |
