# Commit 4 — Welle 2 `app.ui_contracts`: Guard-/QA-Abschluss (Monorepo)

**Status:** Abschluss für die **physische Paketlage** der UI-Verträge im eingebetteten Monorepo: Architektur-Guards nutzen [`app_ui_contracts_source_root()`](../../tests/architecture/app_ui_contracts_source_root.py) bzw. `find_spec("app.ui_contracts")`; Segment-AST-Guards scannen die ausgelagerte Quelle; QA-Segment-Heuristik erkennt Änderungen unter `linux-desktop-chat-ui-contracts/src/app/ui_contracts/**`.

**Vorgänger:** [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md), [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md)  
**API / DoR:** [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md), [`PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](PACKAGE_UI_CONTRACTS_SPLIT_READY.md)

---

## 1. Was für `ui_contracts` im Monorepo jetzt vollständig abgeschlossen ist (Welle 2)

| Thema | Umsetzung |
|--------|-----------|
| Host-Consumer | `linux-desktop-chat-ui-contracts @ file:./…`, kein `app/ui_contracts/` im Host-Tree, `extend_path` in `app/__init__.py` |
| CI | Editables + Verify — Commit 3 |
| Qt-Freiheit (`ui_contracts`) | [`test_ui_layer_guardrails`](../../tests/architecture/test_ui_layer_guardrails.py) über installierte Quelle |
| Segment-Verbote (`ui_contracts` → `gui` / …) | [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) inkl. synthetisches Präfix `ui_contracts/…` |
| Private-Symbol-Imports | [`test_ui_contracts_public_surface_guard.py`](../../tests/architecture/test_ui_contracts_public_surface_guard.py) — Walk nur Host-`PROJECT_ROOT`; Docstring Commit 4 |
| `TARGET_PACKAGES` / `test_package_map_contract` | `ui_contracts` per `find_spec` wie `features` |
| Landmarken | [`app/packaging/landmarks.py`](../../app/packaging/landmarks.py) — eingebettete Vorlage |
| QA-Segment-Spiegel | [`segments_from_changed_files()`](../../app/qa/git_qa_report.py) mappt `linux-desktop-chat-ui-contracts/src/app/ui_contracts/**` → **ui_contracts** |

---

## 2. Bewusst monorepo-spezifisch (bis PyPI / Repo-Split)

| Punkt | Begründung |
|--------|------------|
| `file:./linux-desktop-chat-ui-contracts` im Host-`pyproject.toml` | Kein Index-Pin / kein zweites Git-Checkout in Welle 2 |
| `REPO_LANDMARK_FILES` mit `linux-desktop-chat-ui-contracts/src/...` | Zeigt auf eingebettete Vorlage |
| `segments_from_changed_files` — Pfadpräfix `linux-desktop-chat-ui-contracts/...` | Nach Split ggf. andere Pfadlogik oder Wegfall der Heuristik |

---

## 3. Später erst mit PyPI / echtem Repo-Split relevant

- Pin `linux-desktop-chat-ui-contracts>=x.y` statt `file:./…`
- CI ohne eingebetteten Ordner (Wheel aus Index oder zweiter Checkout)
- Optional: Wiederverwendbare GitHub Action „Install Host + verify embedded distributions“
- Architektur-Doku mit veralteten Links `../../app/ui_contracts/...` schrittweise auf Vorlagenpfad oder generische „installiertes `app.ui_contracts`“-Formulierung

---

## 4. Restpunkte — **nicht** `ui_contracts`-spezifisch

- **`test_app_package_guards`** / Host-`app/`-Root-Policies, Root-Entrypoints, Startup-Governance
- **Hybrid-Segmente** (`ui_application`, `global_overlay`, …)
- **Markdown-/Model-Gates** ohne Contracts-Bezug
- **`app.features`** / Welle 1 — eigenständig in [`PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md)

---

## 5. Empfohlene Abschluss-Verifikation

```bash
cd Linux-Desktop-Chat
export LDC_REPO_ROOT="$(pwd)"
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install -e ./linux-desktop-chat-features
.venv/bin/pip install -e ./linux-desktop-chat-ui-contracts

.venv/bin/pytest tests/architecture/test_ui_layer_guardrails.py \
  tests/architecture/test_ui_contracts_public_surface_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py -q

.venv/bin/pytest tests/unit/dev/test_git_qa_report.py -q
.venv/bin/python tools/ci/release_matrix_ci.py validate
```

---

## 6. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: QA-Segment-Mapping + Public-Surface-Docstring; Abschlussliste |
