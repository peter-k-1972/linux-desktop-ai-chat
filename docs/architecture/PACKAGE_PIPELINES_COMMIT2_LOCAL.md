# Commit 2 — Host nutzt `linux-desktop-chat-pipelines` (lokal & Monorepo)

**Status:** Umgesetzt im Monorepo: Host-`pyproject` referenziert die eingebettete Vorlage per `file:./linux-desktop-chat-pipelines`, Verzeichnis **`app/pipelines/` ist entfernt**; `app.pipelines` kommt aus dem installierten Paket (editable oder Wheel). `app.__path__` bleibt per `pkgutil.extend_path` mit weiteren `app/*`-Segmenten zusammengeführt (wie bei `app.features` / `app.ui_contracts`).

**Bezug:** [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md), [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md), Commit 1: Vorlage [`linux-desktop-chat-pipelines/`](../../linux-desktop-chat-pipelines/). **CI Commit 3:** [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md).

---

## 1. Was Commit 2 geändert hat

| Änderung | Ort |
|----------|-----|
| Abhängigkeit | Host [`pyproject.toml`](../../pyproject.toml): `linux-desktop-chat-pipelines @ file:./linux-desktop-chat-pipelines` |
| Geteiltes `app`-Paket | [`app/__init__.py`](../../app/__init__.py): Kommentar ergänzt (`extend_path` unverändert) |
| Quellbaum Pipelines | Verzeichnis **`app/pipelines/` entfernt** — Quelle nur [`linux-desktop-chat-pipelines/src/app/pipelines/`](../../linux-desktop-chat-pipelines/src/app/pipelines/) |
| PEP-621 / core-Gruppe | [`linux-desktop-chat-features/.../dependency_groups/builtins.py`](../../linux-desktop-chat-features/src/app/features/dependency_groups/builtins.py): `linux-desktop-chat-pipelines` in **core**-`python_packages` (Drift-Check zu `project.dependencies`) |
| Landmarken | [`app/packaging/landmarks.py`](../../app/packaging/landmarks.py): `linux-desktop-chat-pipelines/pyproject.toml`, `.../src/app/pipelines/__init__.py` |
| Guards / Tests | [`tests/architecture/app_pipelines_source_root.py`](../../tests/architecture/app_pipelines_source_root.py); [`test_package_map_contract.py`](../../tests/architecture/test_package_map_contract.py) (`pipelines` per `find_spec("app.pipelines")`); [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) (Scan mit Präfix `pipelines/`); [`segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py) Modul-Doku; [`app/qa/git_qa_report.py`](../../app/qa/git_qa_report.py) `segments_from_changed_files`; [`tests/unit/dev/test_git_qa_report.py`](../../tests/unit/dev/test_git_qa_report.py) |
| Öffentliche Oberfläche | [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py): unveränderte Regeln; Host-Pfad `app/pipelines/**` existiert nicht mehr — Ausschluss über weiterhin leeren Host-Zweig |

---

## 2. Lokale Install-Strategie (bevorzugt)

**Ein Repo-Root, eingebettete Vorlage** — wie bei Features und UI-Contracts.

```bash
cd /path/to/Linux-Desktop-Chat
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

`pip install -e .` zieht die `file:`-Abhängigkeiten mit. **Wichtig:** Wenn `pip` eine Dependency als **Kopie** in `site-packages` legt (ohne editable-Link), kann Quelltext veralten — dann explizit editable nachziehen (gleiches Muster wie [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md) §2):

```bash
.venv/bin/pip install -e ./linux-desktop-chat-features
.venv/bin/pip install -e ./linux-desktop-chat-ui-contracts
.venv/bin/pip install -e ./linux-desktop-chat-pipelines
```

Die Zeile für **`linux-desktop-chat-features`** bleibt **zwingend**, wenn `builtins.py` (PEP-621/core-Liste) geändert wurde. Für **Pipelines** ist editable sinnvoll, wenn du unter `linux-desktop-chat-pipelines/src/app/pipelines/` arbeitest und sofortige Tests ohne Neuinstallation willst.

---

## 3. Bekannte Rest-/CI-Themen

- **Commit 3 (CI):** umgesetzt — [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md).
- **Ohne Installation:** Importe `app.pipelines` und Architekturtests, die `find_spec` / `app_pipelines_source_root()` nutzen, schlagen fehl — erwartetes Verhalten.
- **Eigenes PyPI-Pin** statt `file:./…`: später `linux-desktop-chat-pipelines>=x.y` — Entwickler- und CI-Workflow anpassen.
- **Doku-Drift:** Architektur-Doku für Welle 3 ist in SPLIT_READY/PHYSICAL_SPLIT/CUT_READY und [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md) konsolidiert; ältere Handbücher/Audits können noch `app/pipelines/`-Pfade zeigen.

---

## 4. Verifikationskommandos (nach Commit 2)

```bash
cd Linux-Desktop-Chat
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install -e ./linux-desktop-chat-pipelines

.venv/bin/python -c "from app.pipelines import PipelineEngine, PipelineService; print('ok')"

.venv/bin/pytest tests/architecture/test_pipelines_public_surface_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py \
  tests/unit/dev/test_git_qa_report.py -q

.venv/bin/pytest tests/unit/test_pipelines_models.py \
  tests/unit/test_pipelines_engine.py \
  tests/unit/test_pipelines_service.py \
  tests/unit/test_pipelines_executors.py \
  tests/unit/workflows/test_tool_call_node_executor.py -q

.venv/bin/pytest tests/unit/features/test_dependency_packaging.py::test_pep621_pyproject_alignment_clean -q
```

---

## 5. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Commit 2 Pipelines im Monorepo (Host-Cut, Guards, Doku) |
| 2026-03-25 | Header §3: Verweis Commit 3 CI |
