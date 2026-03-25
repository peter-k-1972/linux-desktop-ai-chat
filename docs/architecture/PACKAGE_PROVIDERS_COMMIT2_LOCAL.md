# Commit 2 — Host nutzt `linux-desktop-chat-providers` (lokal & Monorepo)

**Status:** Host-`pyproject` referenziert die eingebettete Vorlage per `file:./linux-desktop-chat-providers`, Verzeichnis **`app/providers/` ist entfernt**; `app.providers` kommt aus der installierten Distribution (editable oder Wheel). `app.__path__` bleibt per `pkgutil.extend_path` mit weiteren `app/*`-Segmenten zusammengeführt.

**Bezug:** [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md), Commit-1-Vorlage [`linux-desktop-chat-providers/`](../../linux-desktop-chat-providers/).

---

## 1. `src/app/utils/env_loader.py` in der Vorlage (bewusste Ausnahme)

Die Distribution enthält neben `src/app/providers/**` minimal **`src/app/utils/__init__.py`** und **`src/app/utils/env_loader.py`**, weil `cloud_ollama_provider` `app.utils.env_loader` importiert — sonst wäre das Paket **allein** (ohne Host) nicht importierbar.

Im **vollständigen Monorepo** existiert weiterhin der Host-Baum **`app/utils/env_loader.py`** (kanonisch für Produktcode). Beide liegen im Namespace `app.utils` (gleiches `extend_path`-Muster wie bei anderen Segmenten). **Inhaltliche Parität** zwischen Host-`env_loader` und der Kopie in `linux-desktop-chat-providers/src/app/utils/` bleibt Pflicht (wie früher der Sync zwischen Host- und Vorlagen-`providers`).

**QA-Segmentierung:** Änderungen unter `linux-desktop-chat-providers/src/app/utils/**` werden in `segments_from_changed_files` als Segment **`utils`** geführt (nicht `providers`), damit Reports nicht vorgeben, es handle sich um Provider-Implementierung.

---

## 2. Was Commit 2 geändert hat (Kurz)

| Änderung | Ort |
|----------|-----|
| Abhängigkeit | Host [`pyproject.toml`](../../pyproject.toml): `linux-desktop-chat-providers @ file:./linux-desktop-chat-providers` |
| Geteiltes `app`-Paket | [`app/__init__.py`](../../app/__init__.py): Kommentar (`extend_path` unverändert) |
| Quellbaum Providers | Verzeichnis **`app/providers/` entfernt** — Quelle [`linux-desktop-chat-providers/src/app/providers/`](../../linux-desktop-chat-providers/src/app/providers/) |
| PEP-621 / core-Gruppe | [`linux-desktop-chat-features/.../builtins.py`](../../linux-desktop-chat-features/src/app/features/dependency_groups/builtins.py): `linux-desktop-chat-providers` in **core**-`python_packages` |
| Landmarken | [`app/packaging/landmarks.py`](../../app/packaging/landmarks.py): `linux-desktop-chat-providers/pyproject.toml`, `.../src/app/providers/__init__.py` |
| Guards / Tests | [`tests/architecture/app_providers_source_root.py`](../../tests/architecture/app_providers_source_root.py); [`test_package_map_contract.py`](../../tests/architecture/test_package_map_contract.py); [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py); [`test_providers_public_surface_guard.py`](../../tests/architecture/test_providers_public_surface_guard.py); [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py) `ALLOWED_PROVIDER_STRING_FILES`; [`test_provider_orchestrator_governance_guards.py`](../../tests/architecture/test_provider_orchestrator_governance_guards.py); [`app/qa/git_qa_report.py`](../../app/qa/git_qa_report.py); [`test_git_qa_report.py`](../../tests/unit/dev/test_git_qa_report.py) |
| Hilfsskripte | [`scripts/dev/architecture_map.py`](../../scripts/dev/architecture_map.py); [`tools/generate_system_map.py`](../../tools/generate_system_map.py); [`tools/build_manual_index.py`](../../tools/build_manual_index.py); [`tools/auto_explain_manual.py`](../../tools/auto_explain_manual.py) |
| Übergangsbrücke | [`app/ollama_client.py`](../../app/ollama_client.py): unverändert Re-Export aus `app.providers.ollama_client` |

---

## 3. Lokale Installation (bevorzugt)

```bash
cd /path/to/Linux-Desktop-Chat
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install -e ./linux-desktop-chat-providers
```

---

## 4. Verifikationskommandos (nach Commit 2)

```bash
.venv/bin/python -c "from app.providers import LocalOllamaProvider; from app.ollama_client import OllamaClient; print('ok')"

.venv/bin/pytest tests/architecture/test_providers_public_surface_guard.py \
  tests/architecture/test_package_map_contract.py \
  tests/architecture/test_segment_dependency_rules.py \
  tests/architecture/test_provider_orchestrator_governance_guards.py \
  tests/unit/dev/test_git_qa_report.py -q

.venv/bin/pytest tests/unit/features/test_dependency_packaging.py::test_pep621_pyproject_alignment_clean -q
```

---

## 5. CI / Closeout

**Commit 3 (CI):** [`PACKAGE_PROVIDERS_COMMIT3_CI.md`](PACKAGE_PROVIDERS_COMMIT3_CI.md).

**Commit 4 (Closeout)** — separater Schritt / Welle-4-Abschluss.
