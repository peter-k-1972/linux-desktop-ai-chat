# Commit 4 — Welle 3 `app.pipelines`: Guard-/QA-Abschluss (Monorepo)

**Status:** Abschluss für die **physische Paketlage** von Pipelines im eingebetteten Monorepo: Public-Surface-Guard schließt die Implementierung über [`app_pipelines_source_root()`](../../tests/architecture/app_pipelines_source_root.py) aus (zusätzlich historisches `app/pipelines/` im Host); Segment-AST und `test_package_map_contract` nutzen seit Commit 2 installierte Quelle / `find_spec`; QA mappt `linux-desktop-chat-pipelines/src/app/pipelines/**` auf Segment **pipelines**; CI seit Commit 3. Verweisbare Doku-Links in SPLIT_READY/CUT_READY zeigen auf die Vorlage unter `linux-desktop-chat-pipelines/src/app/pipelines/`.

**Vorgänger:** [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](PACKAGE_PIPELINES_COMMIT2_LOCAL.md), [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md)  
**API / DoR:** [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md), [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md), [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md)

---

## 1. Was für `pipelines` im Monorepo jetzt vollständig abgeschlossen ist (Welle 3)

| Thema | Umsetzung |
|--------|-----------|
| Host | `linux-desktop-chat-pipelines @ file:./…`, kein `app/pipelines/` im Host-Tree, `extend_path` in `app/__init__.py` (Commit 2) |
| CI | Editables + Verify `app.pipelines` — Commit 3 |
| Segment-Verbote (`pipelines` → `gui` / …) | [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) + `app_pipelines_source_root()`, Präfix `pipelines/…` |
| `TARGET_PACKAGES` / `test_package_map_contract` | `pipelines` per `find_spec("app.pipelines")`, Landmarken in [`landmarks.py`](../../app/packaging/landmarks.py) |
| Public Surface (kanonische Submodule, keine `_*` von außen) | [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py): `_skip_as_pipelines_implementation()` / Private-Import-Scanner inkl. Vorlagen-Pfad `linux-desktop-chat-pipelines/src/app/pipelines/**` |
| QA-Segment-Spiegel | [`segments_from_changed_files()`](../../app/qa/git_qa_report.py) |
| Handbuch-/Tool-Pfade | [`tools/build_manual_index.py`](../../tools/build_manual_index.py) `chains`-Unit: `linux-desktop-chat-pipelines/src/app/pipelines/`; [`tools/auto_explain_manual.py`](../../tools/auto_explain_manual.py) Kurzlabel |
| Entwickler-Leitfaden | [`docs/DEVELOPER_GUIDE.md`](../../DEVELOPER_GUIDE.md) — Pipelines-Zeile |
| Architektur-Doku | [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md) — Repo-Links auf Vorlage; [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) §4.2/4.3 auf Erledigt-Stand |

---

## 2. Bewusst monorepo-spezifisch (bis PyPI / Repo-Split)

| Punkt | Begründung |
|--------|------------|
| `file:./linux-desktop-chat-pipelines` im Host-`pyproject.toml` | Kein Index-Pin / kein zweites Git-Checkout in Welle 3 |
| `REPO_LANDMARK_FILES` mit `linux-desktop-chat-pipelines/src/...` | Zeigt auf eingebettete Vorlage |
| `segments_from_changed_files` — Präfix `linux-desktop-chat-pipelines/...` | Nach Split ggf. andere Pfadlogik |

---

## 3. Später erst mit PyPI / echtem Repo-Split relevant

- Pin `linux-desktop-chat-pipelines>=x.y` statt `file:./…`
- CI ohne eingebetteten Ordner (Wheel aus Index oder zweiter Checkout)
- **Release-Notes / API-Changelog** für das Wheel (offen laut CUT_READY §5)
- Optionale Wiederverwendbare GitHub Action „Install Host + verify embedded distributions“
- Veraltete Markdown-Pfade `app/pipelines/…` in Handbuch, Release-Audit, FEATURES-Doku — schrittweise auf Vorlage oder „installiertes `app.pipelines`“

---

## 4. Restpunkte — **nicht** pipelines-spezifisch

- **`test_app_package_guards`** / Host-`app/`-Root-Policies, Root-Entrypoints, Startup-Governance
- **Hybrid-Segmente** (`ui_application`, `global_overlay`, Workflows-GUI, …)
- **Markdown-/Model-Gates** ohne Pipelines-Bezug
- **`PythonCallableExecutor`** / dynamisches `importlib` — Policy-Empfehlung SPLIT_READY §2.3, kein Packaging-Blocker

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

.venv/bin/pytest tests/architecture/test_pipelines_public_surface_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py -q

.venv/bin/pytest tests/unit/test_pipelines_*.py \
  tests/unit/workflows/test_tool_call_node_executor.py -q

.venv/bin/pytest tests/unit/dev/test_git_qa_report.py -q
.venv/bin/python tools/ci/release_matrix_ci.py validate
```

---

## 6. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Guard-Bereinigung, Tool-/Doku-Pfade, Abschlussliste |
