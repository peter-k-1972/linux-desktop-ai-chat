# `app.cli` — Physischer Split (Variante B, Monorepo)

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Importpfad- und Packaging-Planung** für **Welle 5** — **keine** ausgeführten Commits, **keine** Codeänderungen und **kein** Anlegen von Verzeichnissen **durch dieses Dokument allein**.  
**Bezug:** [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) (**kanonisch:** API, SemVer, Consumer, Guards, transitive Abhängigkeiten, DoR), [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) (Ist-Analyse), [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.9 / §6.4, [`app/__init__.py`](../../app/__init__.py) (`pkgutil.extend_path`), Analogiemodell [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) / [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md)

**Ausführungs-/Abschluss-Dokumente (Arbeitsnamen):** z. B. `PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md` — beschreiben den **Ist-Zustand nach** Umsetzung; dieses Physical-Split-Dokument ist die **Planungsgrundlage**.

---

## 1. Zweck und Einordnung

### 1.1 Zweck

Dieses Dokument legt fest:

- die **Packaging-Variante** für die Distribution **`linux-desktop-chat-cli`**,  
- die **Zielstruktur** der eingebetteten Vorlage im Monorepo,  
- **Host-`pyproject`**, **`pkgutil.extend_path`**, **Guards**, **Landmarken** und **CI** — **was bei Ausführung** des Physical Split anzupassen ist,  
- eine **Commit-Reihenfolge** analog der Wellen 3–4,  
- **Risiken** (transitive Kopplung, kein Standalone-Wheel) und **Nicht-Ziele**.

### 1.2 Einordnung Welle 5

| Phase | Dokument / Artefakt |
|--------|---------------------|
| Strategie | [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md) |
| Ist / Split-Readiness | [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) |
| API / DoR / Blocker | [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) |
| **Packaging & Ausführungsplan** | **dieses Dokument** |
| Abschluss (nach Umsetzung) | [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md) |

### 1.3 Abgrenzung

| Thema | Wo |
|--------|-----|
| Öffentliche Oberfläche, SemVer-Zonen, Consumer-Matrix | [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) |
| Direkte/transitive Importkette, „kein Standalone“ | [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) §6, [`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) §3.2 |
| **Kein** Code, **kein** `pyproject`-Patch **in diesem Schritt** | nur dieses Dokument |

---

## 2. Zielstruktur

**Zielbild** des eingebetteten Projekts **`linux-desktop-chat-cli/`** (Monorepo-Vorlage; später eigenes Git-Repo optional):

```text
linux-desktop-chat-cli/
  pyproject.toml
  README.md
  MIGRATION_CUT_LIST.md          # Sync Host ↔ Vorlage bis Host-Cut (analog Providers/Pipelines)
  src/
    app/
      __init__.py                # Namespace-Markierung für installierbares app.cli
      cli/
        __init__.py
        context_replay.py
        context_repro_run.py
        context_repro_batch.py
        context_repro_registry_list.py
        context_repro_registry_rebuild.py
        context_repro_registry_set_status.py
  tests/                         # Mindesttests der Vorlage (z. B. test_imports, test_basic_runtime)
```

- **`src/`-Layout:** vermeidet unbeabsichtigte Imports aus dem Repo-Root ohne Installation.  
- **Nur** der Teilbaum **`app/cli/`** (plus schlankes **`src/app/__init__.py`**) — kein weiterer Host-`app/*`-Inhalt im CLI-Wheel.  
- Modul- und Dateiliste **bindend** wie in [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) §2.

---

## 3. Variante B (Namespace-Paket)

### 3.1 Kurzvergleich (analog Pipelines / Providers)

| Variante | Kurz |
|----------|------|
| **A — neuer Import-Root** (nicht `app.cli`) | Massenwechsel aller `from app.cli…` in Tests, Doku, Guards — nur bei globalem „kein `app.*` aus Drittwheels“. |
| **B — `app.cli` bleibt** | Wheel liefert **`app.cli`** unter `src/app/cli/`; Host entfernt **`app/cli/`**; [`pkgutil.extend_path`](../../app/__init__.py) im Host-`app` reicht (wie Features, UI-Contracts, Pipelines, Providers). |
| **B′ — Shim im Host** | Doppelte Wahrheit; nur wenn **B** organisatorisch abgelehnt wird — dann eher **A** mit einmaligem Bump. |

### 3.2 Verbindliche Empfehlung

**Variante B:** Die Distribution **`linux-desktop-chat-cli`** liefert das Python-Paket **`app.cli`**. Der Host **entfernt** nach dem Cut das Verzeichnis **`app/cli/`** und deklariert die Abhängigkeit **`linux-desktop-chat-cli`** in `[project] dependencies` (Monorepo: zunächst per `file:`-Pfad, siehe §4).

**Begründung (kurz):**

- **Null Breaking** für die dokumentierte Importfläche ([`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) §5): `tests/cli/*`, `python -m app.cli.<modul>`.  
- Konsistenz mit **`linux-desktop-chat-features`**, **`linux-desktop-chat-ui-contracts`**, **`linux-desktop-chat-pipelines`**, **`linux-desktop-chat-providers`**.  
- **SemVer** und Public Surface bleiben auf **`app.cli`** (Submodule-first, Cut-Ready §3).

---

## 4. Host-Integration

### 4.1 `pkgutil.extend_path`

[`app/__init__.py`](../../app/__init__.py) nutzt bereits **`pkgutil.extend_path`** — **keine** zusätzliche Host-Änderung erforderlich, um das aus dem Wheel/Editable geladene Segment **`app.cli`** einzubinden.

### 4.2 Abhängigkeit im Host-`pyproject.toml`

**Konzeptionell** (TOML-Tabellenform, wie in einigen Toolchains üblich):

```toml
[project]
dependencies = [
  # …
]

[tool.*]  # nur als Kontrast: PEP 621 nutzt typischerweise String-Dependencies, siehe unten
```

**Kanonisch in diesem Monorepo** (PEP 621 **String** in `[project].dependencies`, analog [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) §5.2):

```toml
[project]
dependencies = [
  # … bestehend inkl. features, ui_contracts, pipelines, providers …
  "linux-desktop-chat-cli @ file:./linux-desktop-chat-cli",
]
```

- **Editable im Entwickler-Setup / CI:** zusätzlich  
  `pip install -e ./linux-desktop-chat-cli`  
  (entspricht der Idee von **develop = true** an der Pfad-Abhängigkeit — Umsetzung erfolgt über **pip**, nicht zwingend über eine TOML-`[tool]`-Sektion).  
- **Hinweis:** Eine Zeile der Form `linux-desktop-chat-cli = { path = "./linux-desktop-chat-cli", develop = true }` ist **kein** Standardfeld unter `[project]` in PEP 621; wer sie einsetzt, bricht den Abgleich mit [`app.features.dependency_packaging`](../../linux-desktop-chat-features/src/app/features/dependency_packaging.py) — im **Linux Desktop Chat**-Repo gilt die **`file:`-String-Form** wie bei den anderen eingebetteten Distributionen.

### 4.3 Host-Tree

| Bereich | Maßnahme (bei Ausführung) |
|---------|----------------------------|
| **`app/cli/`** | **Entfernen** aus dem Host nach Commit 2 — kanonische Quelle nur Vorlage/installiertes Paket. |
| **`[tool.setuptools.packages.find]`** im Host | Sicherstellen, dass **`app/cli`** nicht mehr aus dem Host-Tree gebündelt wird (Ordner entfernt = typischerweise ausreichend). |
| **Consumer** (`tests/cli`, Doku) | Bei Variante **B:** **keine** Importstring-Änderung. |

---

## 5. Commit-Plan

| Commit | Inhalt (Zielbild) |
|--------|-------------------|
| **Commit 1 — CLI-Vorlage** | Verzeichnis **`linux-desktop-chat-cli/`**: `pyproject.toml`, `README.md`, `MIGRATION_CUT_LIST.md`, vollständiger Spiegel `src/app/cli/**` + `src/app/__init__.py`, Mindesttests unter `tests/`; lokal: `pip install -e ".[dev]"`, `pytest` grün. Host-`app/cli/` zunächst **optional noch** parallel — dann Sync-Disziplin laut **MIGRATION_CUT_LIST** bis Commit 2. |
| **Commit 2 — Host-Cut** | Host-`pyproject.toml`: `linux-desktop-chat-cli @ file:./linux-desktop-chat-cli`; **`app/cli/`** entfernen; **`landmarks.py`**, **`app_cli_source_root()`**, **`test_package_map_contract`** (`find_spec("app.cli")`), Segment-AST mit Präfix `cli/…`, **Public-Surface-Guard**, Git-QA-Segment **`linux-desktop-chat-cli/src/app/cli/**` → `cli`; **`dependency_groups.builtins`**: `linux-desktop-chat-cli` in **core**-`python_packages`. |
| **Commit 3 — CI** | Workflows: nach Host-Install **`pip install -e ./linux-desktop-chat-cli`**; Verify **`importlib.util.find_spec("app.cli")`** (und ggf. Kurz-`python -c`); `paths`-Filter für `linux-desktop-chat-cli/**` wo nötig — analog Providers/Pipelines. |
| **Commit 4 — Wave-Closeout** | Governance-Restabgleich, Doku-Cross-Links, Stichprobe `pytest` — [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md). |

---

## 6. CI-Änderungen

| Schritt | Inhalt |
|---------|--------|
| **Editable** | `pip install -e ./linux-desktop-chat-cli` **zusätzlich** zu Host `pip install -e ".[dev]"` und den bestehenden Editables (features, ui_contracts, pipelines, providers) — wie in **pytest-full**, **edition-smoke-matrix**, **plugin-validation-smoke** und konsistenten Workflows. |
| **Verify** | `python -c "import importlib.util as u; assert u.find_spec('app.cli') is not None"` (oder äquivalente einzeilige Prüfung). |
| **Hinweis** | Ohne installiertes **`linux-desktop-chat-cli`** schlagen Architekturtests fehl, die `app_cli_source_root()` / `find_spec("app.cli")` nutzen — CI muss die Reihenfolge **Install → Verify → pytest** einhalten. |

---

## 7. Architektur-Guards

| Artefakt | Rolle bei Ausführung |
|----------|----------------------|
| [`test_cli_public_surface_guard.py`](../../tests/architecture/test_cli_public_surface_guard.py) | **Pflicht:** kanonische `app.cli`-Submodule außerhalb der CLI-Implementierung; keine `_*`-Imports von außen; CLI-Quellbaum gegen **`FORBIDDEN_IMPORT_RULES`** für Segment **`cli`**. |
| [`app_cli_source_root.py`](../../tests/architecture/app_cli_source_root.py) | Liefert die **Quellwurzel** des installierten/editable **`app.cli`** (Vorlage oder `site-packages`) für AST-Scans. |
| [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py) | `TARGET_PACKAGES` enthält **`cli`**; Kanten **`cli` → `gui` / `ui_application` / `ui_runtime`** — unverändert sachlich; Quelle der CLI-Dateien nur noch aus Wheel/Vorlage. |
| [`segment_dependency_rules.py`](../../tests/architecture/segment_dependency_rules.py) | `FORBIDDEN_SEGMENT_EDGES` inkl. **`(cli, gui)`**; Segment-AST bindet **`app_cli_source_root()`** mit synthetischem Präfix **`cli/…`** ein. |
| [`test_package_map_contract.py`](../../tests/architecture/test_package_map_contract.py) | **`find_spec("app.cli")`** nach Installation; Landmarken-Dateien unter `linux-desktop-chat-cli/…`. |
| [`app/qa/git_qa_report.py`](../../app/qa/git_qa_report.py) | Änderungen unter `linux-desktop-chat-cli/src/app/cli/**` → Segment **cli**. |

---

## 8. Post-Split-Verifikation

Nach erfolgreichem Cut (Zielbild — **bei Ausführung** durchführen):

| Prüfung | Erwartung |
|---------|-----------|
| **Import** | `import app.cli` bzw. `from app.cli.context_replay import run_replay` (mit vollem Host) |
| **`-m`-Einstieg** | `python -m app.cli.context_replay` (mit gültigem Fixture/Args; voller Host für Laufzeitkette) |
| **Architektur** | z. B. `pytest tests/architecture/test_cli_public_surface_guard.py tests/architecture/test_segment_dependency_rules.py tests/architecture/test_package_map_contract.py -q` |
| **CLI-Tests Host** | `pytest tests/cli/ -q` |
| **Vorlage** | `pytest linux-desktop-chat-cli/tests/ -q` |
| **Release-Matrix** | `python tools/ci/release_matrix_ci.py validate` |

Ausführliche Kommandoliste ggf. in [`PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md`](PACKAGE_CLI_COMMIT4_WAVE5_CLOSEOUT.md) §5.

---

## 9. Risiken

| Risiko | Beschreibung |
|--------|--------------|
| **Transitive Service-Kopplung** | CLI importiert **`app.context.replay.*`**; zur Laufzeit entsteht die Kette über **Engine** und **`chat_service`** bis **`app.chat` / `app.core`** ([`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md) §6). Jede Änderung dort kann CLI-Verhalten beeinflussen — **ohne** dass das CLI-Wheel diese Module enthält. |
| **Kein Standalone-Wheel** | **`linux-desktop-chat-cli`** allein ersetzt **nicht** den Host; Installation nur Sinn **neben** `linux-desktop-chat` (oder gleichwertiger Gesamtinstallation). Missverständnis „nur CLI pip installieren“ führt zu Laufzeitfehlern. |
| **Doppelte Quelle** | Zwischen Commit 1 und 2: Host-`app/cli/` **und** Vorlage — **Drift-Risiko** ohne Disziplin laut **MIGRATION_CUT_LIST**. |
| **CI-Reihenfolge** | Fehlendes **`pip install -e ./linux-desktop-chat-cli`** → `find_spec("app.cli")` **None** → Architekturtests rot. |

---

## 10. Nicht-Ziele

- **Keine** Entkopplung von **`chat_service`** / **`app.chat`** / **`app.core`** als Voraussetzung für diesen Physical Split — bewusst **nicht** Ziel (Variante B + Host).  
- **Keine** Änderung der **CLI-API** (`run_*`, Submodule-first, `-m`-Einstiege) — siehe [`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md).  
- **Kein** neues CLI-Framework (**argparse** / **click** / **typer** o. ä.) — Ist bleibt **`sys.argv`** in `main()`.  
- **Keine** Implementierung und **kein** Wellenstart **allein durch** dieses Dokument.  
- **Kein** PyPI-Release / finales Index-Pinning — späteres Thema.  
- **Keine** Auflösung anderer Hybrid- oder Segment-Themen außerhalb **`app.cli`**.

---

## 11. `pyproject`-Skizze (Distribution `linux-desktop-chat-cli`)

**Zielbild** (Details im Repo unter [`linux-desktop-chat-cli/pyproject.toml`](../../linux-desktop-chat-cli/pyproject.toml) sobald Vorlage gefüllt ist):

- **`[project] name`:** `linux-desktop-chat-cli`  
- **`requires-python`:** konsistent mit Host (`>=3.10`)  
- **`dependencies`:** **keine** PyPI-Pakete über die Stdlib hinaus für die CLI-Module selbst; **fachliche** Abhängigkeit zu **`app.context`** bleibt **implizit über den Host** ([`PACKAGE_CLI_SPLIT_READY.md`](PACKAGE_CLI_SPLIT_READY.md) §5).  
- **`[tool.setuptools.packages.find]`:** `where = ["src"]`, `include = ["app*"]` — analog Pipelines/Providers.  
- **`[project.optional-dependencies] dev`:** mindestens **`pytest`** für Vorlagen-Tests.  
- **Keine** `[project.scripts]`-Einträge **erforderlich**, solange Einstieg **`python -m app.cli.<modul>`** kanonisch bleibt ([`PACKAGE_CLI_CUT_READY.md`](PACKAGE_CLI_CUT_READY.md)).

---

## 12. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Welle 5 Physical-Split-Plan — Variante B, Zielstruktur, Host/`file:`, Commit 1–4, CI, Guards, Verifikation, Risiken, Nicht-Ziele, `pyproject`-Skizze |
