# Commit 4 — Welle 1 `app.features`: Guard-/Test-Abschluss (Monorepo)

**Status:** Abschlussentscheidungen für die **physische Paketlage** der Feature-Plattform im eingebetteten Monorepo: Guards lesen `app.features` über installiertes Paket bzw. [`app_features_source_root()`](../../tests/architecture/app_features_source_root.py); Segment-AST-Guards prüfen die ausgelagerte Quelle wieder explizit.

**Vorgänger:** [`PACKAGE_FEATURES_COMMIT2_LOCAL.md`](PACKAGE_FEATURES_COMMIT2_LOCAL.md), [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md)  
**API / DoR:** [`PACKAGE_FEATURES_CUT_READY.md`](PACKAGE_FEATURES_CUT_READY.md)

---

## 1. Was für `features` jetzt vollständig abgeschlossen ist (Welle 1)

| Thema | Umsetzung |
|--------|-----------|
| Host-Consumer | `linux-desktop-chat-features @ file:./…`, kein `app/features/` im Host-Tree, `extend_path` in `app/__init__.py` |
| CI | `pip install -e ".[…]"`, `LDC_REPO_ROOT`, Pfadtrigger, Verify-Schritte — siehe Commit 3 |
| Architektur-Guards (Dateizugriff) | [`app_features_source_root()`](../../tests/architecture/app_features_source_root.py) in Edition-/Feature-System-Guards |
| Segment-Verbote (`features` → `gui` / …) | [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) scannt wieder **alle** `.py` unter der installierten `app.features`-Quelle (synthetisches Präfix `features/…` für `app_module_from_relpath`) |
| Öffentliche Importoberfläche / Entry-Point | unverändert vertraglich; Tests [`test_features_public_surface_guard`](../../tests/architecture/test_features_public_surface_guard.py), [`test_entry_point_contract_guard`](../../tests/architecture/test_entry_point_contract_guard.py) |
| QA-Segment-Spiegel | [`segments_from_changed_files()`](../../app/qa/git_qa_report.py) mappt `linux-desktop-chat-features/src/app/features/**` → Segment **features** (Reports analog zu früher `app/features/`) |
| Matrix / PEP-621 robust | [`validate_internal_plugin_smoke_consistency` / `validate_release_matrix_consistency`](../../linux-desktop-chat-features/src/app/features/release_matrix.py): optional ``repo_root`` (setzt [`release_matrix_ci.py`](../../tools/ci/release_matrix_ci.py)); [`validate_pep621_pyproject_alignment`](../../linux-desktop-chat-features/src/app/features/dependency_packaging.py) normalisiert erwartete Core-Namen mit :func:`_requirement_line_to_distribution_name` |

---

## 2. Bewusst monorepo-spezifisch (bis PyPI / Repo-Split)

| Punkt | Begründung |
|--------|------------|
| `file:./linux-desktop-chat-features` im Host-`pyproject.toml` | Kein separates Release-Repo / keine Wheel-Pin aus dem Index in Welle 1 |
| `REPO_LANDMARK_FILES` mit Pfad `linux-desktop-chat-features/src/...` | Landmarks zeigen auf eingebettete Vorlage |
| `segments_from_changed_files` — Pfadpräfix `linux-desktop-chat-features/...` | Nur dieser eingebettete Baum; nach Split ggf. generischer „Repo-Wurzel der Features-Distribution“ oder weg von Pfadheuristik |
| `release_matrix._repo_root_for_matrix_checks` | Host-`tests/unit/features` am Monorepo-Root |

---

## 3. Später erst mit PyPI / echtem Repo-Split relevant

- Pin `linux-desktop-chat-features>=x.y` statt `file:./…`
- CI ohne eingebettetes Verzeichnis (nur Index oder zweites Checkout)
- Optional: Namespace-Shim oder Umbenennung Importpfad (nicht Welle 1)
- Wiederverwendbare GitHub Action für Install + Verify (Commit 3 Restliste)

---

## 4. Restpunkte — **nicht** features-spezifisch

- **`test_app_package_guards.test_app_root_only_allowed_files`** und weitere Host-`app/`-Root-Policies
- **Hybrid-Segmente**, `ui_contracts`-Wellen, QML-Governance
- **Markdown-/Model-Gates** ohne Bezug zu `app.features`

---

## 5. Empfohlene Abschluss-Verifikation

**Pip-Reihenfolge (Monorepo):** Nach `pip install -e ".[dev]"` zusätzlich **`pip install -e ./linux-desktop-chat-features`**, damit `app.features` aus dem Arbeitsbaum (`src/`) geladen wird und nicht eine veraltete **Kopie** aus dem `file:`-Installations-Schritt. Alternativ: `pip install --no-cache-dir --force-reinstall "linux-desktop-chat-features @ file:./linux-desktop-chat-features"`.

```bash
cd Linux-Desktop-Chat
export LDC_REPO_ROOT="$(pwd)"
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install -e ./linux-desktop-chat-features

.venv/bin/pytest tests/architecture/test_segment_dependency_rules.py \
  tests/architecture/test_feature_system_guards.py \
  tests/architecture/test_edition_manifest_guards.py \
  tests/architecture/test_features_public_surface_guard.py \
  tests/architecture/test_entry_point_contract_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_plugin_validation_workflow_guards.py -q

.venv/bin/pytest tests/unit/features/ tests/unit/dev/test_git_qa_report.py -q
.venv/bin/python tools/ci/release_matrix_ci.py validate
```

---

## 6. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung nach Commit-4-Guard-Bereinigung |
