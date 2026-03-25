# Commit 2 — Host nutzt `linux-desktop-chat-features` (lokal & Monorepo)

**Status:** Umgesetzt im Monorepo: Host-`pyproject` referenziert die eingebettete Vorlage, `app/features/` ist entfernt, `app.__path__` wird per `pkgutil.extend_path` mit dem Wheel/editable-`app`-Segment zusammengeführt.

**Bezug:** [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md), [`PACKAGE_FEATURES_CUT_READY.md`](PACKAGE_FEATURES_CUT_READY.md), CI: [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md), Welle-1-Abschluss: [`PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md)

---

## 1. Was Commit 2 geändert hat

| Änderung | Ort |
|----------|-----|
| Abhängigkeit | Host [`pyproject.toml`](../../pyproject.toml): `linux-desktop-chat-features @ file:./linux-desktop-chat-features` |
| Geteiltes `app`-Paket | [`app/__init__.py`](../../app/__init__.py): `extend_path` |
| Quellbaum Feature-Plattform | Verzeichnis **`app/features/` entfernt** — Quelle nur noch unter [`linux-desktop-chat-features/src/app/features/`](../../linux-desktop-chat-features/src/app/features/) |
| Landmarken-Pfade | [`app/packaging/landmarks.py`](../../app/packaging/landmarks.py): `REPO_LANDMARK_FILES` zeigen auf `linux-desktop-chat-features/src/app/features/…` |
| Guards | [`tests/architecture/app_features_source_root.py`](../../tests/architecture/app_features_source_root.py) + Anpassungen in `test_package_map_contract`, `test_feature_system_guards`, `test_edition_manifest_guards` |
| CI-Pfadfilter (minimal) | [`.github/workflows/plugin-validation-smoke.yml`](../../.github/workflows/plugin-validation-smoke.yml): `linux-desktop-chat-features/src/app/features/**` statt `app/features/**` |

---

## 2. Lokale Install-Strategie (bevorzugt)

**Ein Repo-Root, eingebettete Vorlage** — keine `../`-Pfade nötig.

```bash
cd /path/to/Linux-Desktop-Chat
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

`pip install -e .` zieht **`linux-desktop-chat-features @ file:./linux-desktop-chat-features`** automatisch mit (editable auf die Vorlage).

**Reihenfolge:** `pip install -e ".[dev]"` kann eine **eingefrorene** `file:`-Kopie von `linux-desktop-chat-features` legen — für Arbeit an der Feature-Quelle danach **`pip install -e ./linux-desktop-chat-features`** ausführen (siehe [`PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md`](PACKAGE_FEATURES_COMMIT4_WAVE1_CLOSEOUT.md) § 5).

```bash
.venv/bin/pip install -e ./linux-desktop-chat-features
.venv/bin/pip install -e ".[dev]"
# oder nach Host-Install erneut:
.venv/bin/pip install -e ./linux-desktop-chat-features
```

**Hinweis PEP 668:** ohne venv schlägt `pip install` auf manchen Distributionen fehl — immer venv nutzen.

---

## 3. Anpassungen nur in der Distribution `linux-desktop-chat-features` (Commit-2-Follow-up)

| Problem | Lösung |
|---------|--------|
| `release_matrix._repo_root_for_matrix_checks` fand `tests/unit/features` nicht (editable/`site-packages`) | Umgebung `LDC_REPO_ROOT` / `GITHUB_WORKSPACE`, sonst `cwd`, sonst Vorfahren von `__file__` |
| PEP-621-Drift: URL-Dependency in `project.dependencies` | `_requirement_line_to_distribution_name` versteht `name @ file:…`; **core**-Gruppe enthält `linux-desktop-chat-features` in [`dependency_groups/builtins.py`](../../linux-desktop-chat-features/src/app/features/dependency_groups/builtins.py) |

---

## 4. Bekannte Rest-/CI-Themen

- **Commit 3 (CI):** Workflows, `LDC_REPO_ROOT`, Pfadtrigger — siehe [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md).
- **`test_app_package_guards.test_app_root_only_allowed_files`** kann weiterhin wegen anderer Root-Dateien unter `app/` scheitern (unabhängig von Commit 2).
- **Eigenes PyPI-Pin** statt `file:./…`: später `linux-desktop-chat-features>=x.y` — dann Entwickler- und CI-Workflow ohne eingebettete Vorlage anpassen (Commit 4).

---

## 5. Verifikationskommandos (nach Commit 2)

```bash
cd Linux-Desktop-Chat
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"

.venv/bin/python -c "from app.features import ENTRY_POINT_GROUP, FeatureDescriptor; print(ENTRY_POINT_GROUP)"

.venv/bin/pytest tests/architecture/test_package_map_contract.py \
  tests/architecture/test_feature_system_guards.py \
  tests/architecture/test_edition_manifest_guards.py \
  tests/architecture/test_features_public_surface_guard.py \
  tests/architecture/test_entry_point_contract_guard.py -q

.venv/bin/pytest tests/unit/features/ -q

.venv/bin/python tools/ci/release_matrix_ci.py print-matrix-json | head -c 200
```

---

## 6. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung nach Umsetzung Commit 2 im Monorepo |
