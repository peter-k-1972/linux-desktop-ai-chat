# Commit 2 — Host nutzt `linux-desktop-chat-ui-contracts` (lokal & Monorepo)

**Status:** Umgesetzt im Monorepo: Host-`pyproject` referenziert die eingebettete Vorlage, `app/ui_contracts/` ist **entfernt**; `app.__path__` bleibt per `pkgutil.extend_path` mit dem editable/Wheel-`app`-Segment zusammengeführt (bereits durch Commit 2 `app.features`).

**Bezug:** [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md), [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md), Commit 1: Vorlage [`linux-desktop-chat-ui-contracts/`](../../linux-desktop-chat-ui-contracts/). **CI Commit 3:** [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md) (Features-Analogon: [`PACKAGE_FEATURES_COMMIT3_CI.md`](PACKAGE_FEATURES_COMMIT3_CI.md)).

---

## 1. Was Commit 2 geändert hat

| Änderung | Ort |
|----------|-----|
| Abhängigkeit | Host [`pyproject.toml`](../../pyproject.toml): `linux-desktop-chat-ui-contracts @ file:./linux-desktop-chat-ui-contracts` |
| Geteiltes `app`-Paket | [`app/__init__.py`](../../app/__init__.py): Kommentar ergänzt (`extend_path` unverändert) |
| Quellbaum UI-Verträge | Verzeichnis **`app/ui_contracts/` entfernt** — Quelle nur [`linux-desktop-chat-ui-contracts/src/app/ui_contracts/`](../../linux-desktop-chat-ui-contracts/src/app/ui_contracts/) |
| PEP-621 / core-Gruppe | [`linux-desktop-chat-features/.../dependency_groups/builtins.py`](../../linux-desktop-chat-features/src/app/features/dependency_groups/builtins.py): `linux-desktop-chat-ui-contracts` in **core**-`python_packages` (Drift-Check zu `project.dependencies`) |
| Landmarken | [`app/packaging/landmarks.py`](../../app/packaging/landmarks.py): `linux-desktop-chat-ui-contracts/pyproject.toml`, `.../src/app/ui_contracts/__init__.py` |
| Guards / Tests | [`tests/architecture/app_ui_contracts_source_root.py`](../../tests/architecture/app_ui_contracts_source_root.py); [`test_ui_layer_guardrails.py`](../../tests/architecture/test_ui_layer_guardrails.py) (Qt-Check über `find_spec`); [`test_package_map_contract.py`](../../tests/architecture/test_package_map_contract.py) (`ui_contracts` wie `features`); [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) (Scan der ausgelagerten Quelle mit Präfix `ui_contracts/`); [`segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py) Doku |

---

## 2. Lokale Install-Strategie (bevorzugt)

**Ein Repo-Root, eingebettete Vorlage** — wie bei Features.

```bash
cd /path/to/Linux-Desktop-Chat
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

`pip install -e .` installiert beide `file:`-Abhängigkeiten mit. **Wichtig:** Wenn `pip` die Dependency `linux-desktop-chat-features` als **Kopie** in `site-packages` legt (ohne editable-Link), kann `app.features.dependency_groups.builtins` veralten — dann schlägt `test_pep621_pyproject_alignment_clean` fehl. **Immer** nach dem ersten Host-Install (und nach Änderungen an `builtins.py`) ausführen:

```bash
.venv/bin/pip install -e ./linux-desktop-chat-features
.venv/bin/pip install -e ./linux-desktop-chat-ui-contracts
```

(gleiches Muster wie [`PACKAGE_FEATURES_COMMIT2_LOCAL.md`](PACKAGE_FEATURES_COMMIT2_LOCAL.md) §2 — Features-Zeile ist **zwingend** für aktuelle PEP-621-/core-Liste.)

---

## 3. Bekannte Rest-/CI-Themen

- **Commit 3 (CI):** umgesetzt — [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md).
- **Andere Architekturtests** (`test_app_package_guards`, Root-Entrypoints, Startup-Governance) können im Arbeitsbaum unabhängig von `ui_contracts` rot sein — nicht Gegenstand von Commit 2.
- **Eigenes PyPI-Pin** statt `file:./…`: später `linux-desktop-chat-ui-contracts>=x.y` — Entwickler- und CI-Workflow anpassen.
- **Doku-Links** in älteren Architekturdateien können noch `app/ui_contracts/...` zeigen; kanonische Quelle ist die Vorlage bzw. installiertes `app.ui_contracts`.

---

## 4. Verifikationskommandos (nach Commit 2)

```bash
cd Linux-Desktop-Chat
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"

.venv/bin/python -c "from app.ui_contracts import ChatWorkspaceState, SettingsErrorInfo; print('ok')"

.venv/bin/pytest tests/architecture/test_ui_layer_guardrails.py \
  tests/architecture/test_ui_contracts_public_surface_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py -q

.venv/bin/pytest tests/contracts/test_chat_ui_contracts.py \
  tests/contracts/test_settings_appearance_contracts.py -q

.venv/bin/pytest tests/unit/features/test_dependency_packaging.py::test_pep621_pyproject_alignment_clean -q
```

(Letzteres prüft den PEP-621-Abgleich inkl. neuer core-Dependency.)

---

## 5. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung nach Umsetzung Commit 2 `ui_contracts` im Monorepo |
| 2026-03-25 | Bezug/§3: Commit 3 CI verlinkt; Header **Bezug** aktualisiert |
| 2026-03-25 | Verweis Commit 4: [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md) |
