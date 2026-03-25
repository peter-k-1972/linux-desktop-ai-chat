# Technische Readiness: `app.cli` (Welle 5)

**Projekt:** Linux Desktop Chat  
**Status:** Interner Ist-Scan nach Auslagerung in **`linux-desktop-chat-cli`** — ergänzt Decision Memo und Split-Plan.  
**Bezug:** [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.4

---

## 1. Struktur (vor/nach Cut)

| Modul | Rolle | Eintritt |
|--------|--------|----------|
| `context_replay` | Replay aus JSON → `get_context_replay_service()` | `python -m app.cli.context_replay <file>` |
| `context_repro_run` | Einzelner Repro-Case | `python -m app.cli.context_repro_run <json>` |
| `context_repro_batch` | Verzeichnis mit `*.json` | `python -m app.cli.context_repro_batch <dir>` |
| `context_repro_registry_list` | Registry lesen | `python -m app.cli.context_repro_registry_list <registry.json>` |
| `context_repro_registry_rebuild` | Index aus Repro-Baum | `python -m app.cli.context_repro_registry_rebuild <root> <registry.json>` |
| `context_repro_registry_set_status` | Status am Artefakt setzen | `python -m app.cli.context_repro_registry_set_status …` |

Kanonische Quelle: **`linux-desktop-chat-cli/src/app/cli/`**; Importpfad unverändert **`app.cli.*`**.

---

## 2. Abhängigkeiten

| Ziel | Verwendung |
|------|------------|
| **`app.context.replay.*`** | `canonicalize`, `repro_case_runner`, `replay_service`, Registry-/Indexer-Services |

**Nicht** importiert: `app.gui`, `app.ui_application`, `app.ui_runtime`, `app.services` (direkt).

**Implizit:** Laufzeit der CLIs setzt vollständigen Host-Kontext (DB/Settings über `context`-Schicht) voraus — die Wheel **`linux-desktop-chat-cli`** allein ist keine eigenständige Produkt-Installation ohne Host.

---

## 3. Öffentliche Oberfläche (Guard)

Außerhalb des Pakets nur:

- `from app.cli import …` (Root), oder
- `from app.cli.<kanonisches_submodul> import …`

mit Submodulen:

`context_replay`, `context_repro_run`, `context_repro_batch`, `context_repro_registry_list`, `context_repro_registry_rebuild`, `context_repro_registry_set_status`.

Test: `tests/architecture/test_cli_public_surface_guard.py`.

---

## 4. Architektur-Compliance

- **Segment-AST:** `cli` → `gui` verboten ([`segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py)); eingebettete Quelle unter synthetischem Präfix `cli/…`.
- **`FORBIDDEN_IMPORT_RULES`:** `cli` → `gui`, `ui_application`, `ui_runtime` ([`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py)); Zusatztest im CLI-Public-Surface-Modul.

---

## 5. Consumer (Host-Repo)

| Ort | Nutzung |
|-----|---------|
| `tests/cli/test_context_repro_cli.py` | `app.cli.context_repro_*` |
| `tests/cli/test_context_replay_cli.py` | `app.cli.context_replay` |
| Doku (`docs/DEVELOPER_GUIDE.md`, `docs/05_developer_guide/`, `docs_manual/`) | Aufruf `python -m app.cli.<modul>` |

---

## 6. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung nach technischer Vorbereitung / Host-Cut `app/cli/` |
