# `app.pipelines` — Physischer Split (Variante B, Monorepo)

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Importpfad- und Packaging-Entscheidung**; **Commit-1-Vorlage** unter [`linux-desktop-chat-pipelines/`](../../linux-desktop-chat-pipelines/); **Commit 2:** [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](PACKAGE_PIPELINES_COMMIT2_LOCAL.md); **Commit 3 (CI):** [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md); **Commit 4 (Welle-3-Abschluss):** [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md).  
**Bezug:** [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md), [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md), [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](PACKAGE_FEATURES_PHYSICAL_SPLIT.md) / [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) (Analogiemodell), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.5 / §4 / §6.2

---

## 0. Commit-1-Vorlage (im Host-Monorepo eingebettet)

Die **ausführbare Repo-Vorlage** liegt unter:

**[`linux-desktop-chat-pipelines/`](../../linux-desktop-chat-pipelines/)** (Verzeichnis im Wurzelverzeichnis dieses Repos).

Inhalt: [`pyproject.toml`](../../linux-desktop-chat-pipelines/pyproject.toml), [`README.md`](../../linux-desktop-chat-pipelines/README.md), [`MIGRATION_CUT_LIST.md`](../../linux-desktop-chat-pipelines/MIGRATION_CUT_LIST.md), vollständiger Quellspiegel [`src/app/pipelines/`](../../linux-desktop-chat-pipelines/src/app/pipelines/), minimale Tests unter [`tests/unit/`](../../linux-desktop-chat-pipelines/tests/unit/). Verifikation: siehe README (`pip install -e ".[dev]"`, `pytest`, `python -m build`).

**Nach Commit 2:** Der Host hat **kein** Verzeichnis mehr `app/pipelines/`; kanonische Quelle ist die Vorlage bzw. installiertes `app.pipelines` ([`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](PACKAGE_PIPELINES_COMMIT2_LOCAL.md)). Historisch: bis Commit 2 mussten Host-Tree und Vorlage parallel synchron gehalten werden ([`MIGRATION_CUT_LIST.md`](../../linux-desktop-chat-pipelines/MIGRATION_CUT_LIST.md) §5).

---

## 1. Entscheidungsvorlage: Importpfad nach dem Cut

### Variante A — Neues Top-Level `ldc_pipelines` (oder `linux_desktop_chat.pipelines`)

| | Host | Services-Fassade | Workflow (`tool_call`) | Tests/Guards | SemVer |
|---|------|------------------|------------------------|--------------|--------|
| **Vorteile** | Kein `app.*` aus einem Drittwheel; „Vendor“-Paket klar benannt. | — | — | Ein theoretischer Import-Root. | Eigener Distribution-Name ohne `app`-Präfix im Modul. |
| **Nachteile** | **Pflicht:** alle `from app.pipelines` → neuer Pfad in `app/services/pipeline_service.py`, `app/workflows/.../tool_call.py`, sämtlichen `tests/unit/test_pipelines_*.py`, Stubs, ggf. Doku. | Gleicher Wechsel. | Gleicher Wechsel. | `test_pipelines_public_surface_guard`, `test_segment_dependency_rules`, `arch_guard_config` (`TARGET_PACKAGES` / Kanten auf `pipelines`) semantisch anpassen oder Mapping-Doku. | Koordinierter Major beim Wechsel. |

### Variante B — Importpfad `app.pipelines` bleibt (Paket im Wheel unter `app/pipelines/`)

| | Host | Services-Fassade | Workflow (`tool_call`) | Tests/Guards | SemVer |
|---|------|------------------|------------------------|--------------|--------|
| **Vorteile** | **Kein** Importstring-Wechsel für bestehende Consumer. | `from app.pipelines import …` unverändert. | `from app.pipelines import get_executor_registry` unverändert. | AST-Guards auf `app.pipelines` bleiben gültig; Anpassungen nur bei **Dateipfad**-Annahmen (`APP_ROOT / "pipelines"`) und Segment-Scan (Quelle wie bei Features/UI-Contracts). | Distribution **`linux-desktop-chat-pipelines`** versioniert die Bibliothek; Host pinnt `>=x.y`. |
| **Nachteile** | Zwei Distributions können `app.*` liefern — **nur eine** darf `app/pipelines` besitzen; Host-Tree **`app/pipelines/` entfernen**. | — | — | `app/__init__.py` nutzt weiterhin `extend_path` (bereits für `features` / `ui_contracts`). | `app` im Wheel-Namespace ist ungewöhnlich, bei diesem Repo aber **bewusst** mit Welle 1/2 abgestimmt. |

### Variante B′ — Namespace `linux_desktop_chat.pipelines` + Shim `app.pipelines` im Host

| | Host | Consumer | Tests/Guards | SemVer |
|---|------|----------|--------------|--------|
| **Idee** | Wheel liefert `linux_desktop_chat/pipelines/`; Host hält dünnes `app/pipelines` als Re-Export. | Schrittweise Migration möglich. | Zwei Installationslagen, Reihenfolge-Risiko. | Shim-Deprecation über Releases. |
| **Nachteile** | Mehr Moving Parts ohne Mehrwert, solange Variante B ausreicht. | — | Höhere Fehlerwahrscheinlichkeit. | — |

---

## 2. Verbindliche Empfehlung (`app.pipelines`)

**Variante B:** Die Distribution **`linux-desktop-chat-pipelines`** (Arbeitsname, PyPI-konform mit Bindestrichen) liefert das Python-Paket **`app.pipelines`** (Verzeichnisbaum `app/pipelines/` im Wheel, z. B. `src/app/pipelines/` im Pipelines-Repo bzw. in der Vorlage). Der Host **entfernt** das lokale Verzeichnis **`app/pipelines/`** und deklariert **`linux-desktop-chat-pipelines>=…`** in `[project] dependencies` (Monorepo zunächst `file:./linux-desktop-chat-pipelines`).

**Begründung (kurz):**

- **Null Breaking** für die kleine, aber kritische Importfläche: [`app/services/pipeline_service.py`](../../app/services/pipeline_service.py), [`app/workflows/execution/node_executors/tool_call.py`](../../app/workflows/execution/node_executors/tool_call.py), Unit-Tests und Public-Surface-Guard — konsistent mit **`app.features`** und **`app.ui_contracts`**.
- **SemVer** und [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md) bleiben auf dem etablierten Symbolraum `app.pipelines`.
- **Variante A** bleibt optionale **Major-Migration**, falls das Projekt global „kein `app.*` aus Drittwheels“ durchsetzt.
- **Variante B′** nur bei harter organisatorischer Ablehnung von `app.*` im externen Wheel — dann eher **A** mit einmaligem Import-Bump statt dauerhaftem Shim.

---

## 3. Packaging-Skizze (Ist: Vorlage §0)

### 3.1 Zielverzeichnisstruktur (Vorlage / späteres Repo)

```text
linux-desktop-chat-pipelines/        # Monorepo-Vorlage (später) bzw. eigenes Git-Repo
  pyproject.toml
  README.md
  src/
    app/
      pipelines/
        __init__.py
        models/
        engine/
        services/
        executors/
        registry/
  tests/                               # optional: Paket-eigene / verschobene Unit-Tests
```

- **`src/`-Layout** vermeidet Imports aus dem Repo-Root ohne Installation.  
- **`app` nur als Präfix** für `app.pipelines` — kein vollständiger Host-`app`-Tree im Wheel.

### 3.2 `pyproject.toml`

Kanonisch im Verzeichnis [`linux-desktop-chat-pipelines/pyproject.toml`](../../linux-desktop-chat-pipelines/pyproject.toml) (inkl. `[project.optional-dependencies] dev` mit `pytest`, `build`).

### 3.3 Host-Abhängigkeit (nach Cut im Host-Repo)

```toml
[project]
dependencies = [
  "linux-desktop-chat-pipelines>=0.1.0",
  # ... bestehende deps inkl. features/ui_contracts nach Bedarf
]
```

Monorepo vor PyPI: z. B. `linux-desktop-chat-pipelines @ file:./linux-desktop-chat-pipelines`.

Host-`setuptools` / `[tool.setuptools.packages.find]` so wählen, dass **`app/pipelines` nicht mehr aus dem Host-Tree** ins Host-Wheel gebündelt wird (Verzeichnis entfernen oder explizit ausschließen).

### 3.4 Build / lokale Verifikation (Zielbild)

```bash
cd linux-desktop-chat-pipelines
python3 -m pip install -e .
python3 -m build
python3 -c "from app.pipelines import PipelineEngine, get_executor_registry; print('ok')"
```

---

## 4. Betroffene Host-, Test- und Guard-Stellen beim echten Cut

### 4.1 Host-Repository

| Bereich | Anpassung |
|---------|-----------|
| `pyproject.toml` | `linux-desktop-chat-pipelines` in `dependencies`; Pin oder `file:` im Monorepo. |
| `app/pipelines/` | **Entfernen** aus dem Host-Tree (Quelle nur noch Wheel/Vorlage). |
| [`app/__init__.py`](../../app/__init__.py) | Bereits `pkgutil.extend_path` — drittes `app/*`-Segment aus weiterem Wheel **ohne** weitere Codeänderung nutzbar. |
| `app/services/pipeline_service.py`, `app/workflows/.../tool_call.py` | Bei **Variante B:** **keine** Importstring-Änderung. |

### 4.2 Guards / Architekturtests

| Datei / Thema | Umsetzung (bei Ausführung) |
|---------------|----------------------------|
| [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py) | **Erledigt (Commit 4):** Ausschluss der Implementierung über `app_pipelines_source_root()` + legacy `app/pipelines/`; siehe [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md). |
| [`test_segment_dependency_rules.py`](../../tests/architecture/test_segment_dependency_rules.py) | **Erledigt (Commit 2):** `app_pipelines_source_root()`, Präfix `pipelines/…`. |
| [`test_package_map_contract.py`](../../tests/architecture/test_package_map_contract.py) | **Erledigt (Commit 2):** `find_spec("app.pipelines")`, Landmarken. |
| [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py) | Segment `pipelines` / Kanten unverändert; Quelle nur installiert. |
| [`app/qa/git_qa_report.py`](../../app/qa/git_qa_report.py) | **Erledigt (Commit 2/4):** Präfix `linux-desktop-chat-pipelines/src/app/pipelines/**` → **pipelines**. |

### 4.3 CI / Workflows

| Thema | Anpassung |
|-------|-----------|
| GitHub Actions / lokale CI | **Erledigt (Commit 3):** [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md). |
| Nur Index-Checkout | Später: `pip install linux-desktop-chat-pipelines==…` ohne eingebetteten Ordner. |

### 4.4 Funktionale Tests

| Bereich | Hinweis |
|---------|---------|
| `tests/unit/test_pipelines_*.py` | Bei Variante B: **kein** Import-Umstieg; Lauf nur mit installiertem Paket. |
| `tests/unit/workflows/test_tool_call_node_executor.py` | Indirekte Kante Workflows → `app.pipelines`; gleiches Modell. |
| `tests/architecture/test_service_governance_guards.py` | `get_pipeline_service` unverändert; sicherstellen, dass Umgebung Pipelines-Wheel lädt. |

---

## 5. Verbleibende Restblocker (nach Commit 1)

| Blocker | Beschreibung |
|---------|----------------|
| **Commit-1-Vorlage** | **Erledigt** — [`linux-desktop-chat-pipelines/`](../../linux-desktop-chat-pipelines/). |
| **Host-Cut** | **Erledigt (Commit 2)** — siehe [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](PACKAGE_PIPELINES_COMMIT2_LOCAL.md). |
| **Guards / Segment-AST / QA-Pfade** | **Erledigt** — Commit 2 + Commit 4 [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md). |
| **CI** | **Erledigt (Commit 3)** — [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md). |
| **Release-Notes / Changelog** | Für `linux-desktop-chat-pipelines` — **offen**. |
| **`landmarks.py`** | **Erledigt (Commit 2)** — Pfade zur eingebetteten Vorlage eingetragen. |

---

## 6. Execution Plan (Zielbild — später auszuführen)

| Schritt | Inhalt |
|---------|--------|
| **1 — Packaging** | **Erledigt:** Vorlage §0; `pip install -e ".[dev]"`, `pytest`, `python -m build` in `linux-desktop-chat-pipelines/`. |
| **2 — Host** | **Erledigt (Commit 2):** `file:`-Dependency, `app/pipelines/` entfernt; `extend_path` unverändert. |
| **3 — Guards** | **Commit 2:** Segment-AST, `test_package_map_contract`. **Commit 4:** Public-Surface-Guard verfeinert — [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md). |
| **4 — CI** | **Erledigt (Commit 3):** Workflows — editables + Verify für `app.pipelines` wo vorgesehen. |
| **5 — Abschluss** | **Erledigt (Commit 4):** Welle-3-Closeout-Doku + Stichprobe `pytest` siehe Closeout §5. |

---

## 7. Pytest-Kommandos (Zielbild nach Host-Cut)

```bash
# Nach Installation des Pipelines-Wheels (editable oder Wheel):
pytest tests/architecture/test_pipelines_public_surface_guard.py \
       tests/unit/test_pipelines_models.py \
       tests/unit/test_pipelines_engine.py \
       tests/unit/test_pipelines_service.py \
       tests/unit/test_pipelines_executors.py \
       tests/unit/workflows/test_tool_call_node_executor.py -q
```

---

## 8. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Varianten A / B / B′, **verbindliche Empfehlung B**, Wheel-Name `linux-desktop-chat-pipelines`, Host-/Guard-/CI-Folgen; **keine** Vorlage in diesem Lauf |
| 2026-03-25 | §0: eingebettete Vorlage `linux-desktop-chat-pipelines/`; Status-Kopf; §3.2 Verweis auf echtes `pyproject.toml`; §5–§6 Commit 1 erledigt |
