# Physischer Split `app.persistence` (Runbook / Vorbereitung)

**Projekt:** Linux Desktop Chat  
**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.7 (`ldc-workspace-data`), kanonische Karten [`PACKAGE_MAP.md`](PACKAGE_MAP.md).  
**Vorgänger-Runbooks:** [`PACKAGE_PROJECTS_PHYSICAL_SPLIT.md`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md), [`PACKAGE_WORKFLOWS_PHYSICAL_SPLIT.md`](PACKAGE_WORKFLOWS_PHYSICAL_SPLIT.md).

**Status dieses Dokuments:** **Vorbereitung** — physischer Cut und Wheel-Scaffold sind **nicht** Gegenstand dieses Commits. **Vor** dem Cut ist die **DB-URL-/Root-Auflösung** von der bisherigen Dateitiefe zu entkoppeln (siehe §6–§7).

---

## 1. Zielbild des Splits

| Feld | Inhalt |
|------|--------|
| **Ziel** | Kanonische **Python-Quelle** von `app.persistence` liegt im Monorepo unter einer eingebetteten Distribution (Arbeitsname **`linux-desktop-chat-persistence`**) unter **`…/src/app/persistence/`**; das Host-Verzeichnis **`app/persistence/`** entfällt nach dem Cut. |
| **Produkt** | Eingebettetes Wheel (PEP 621), Bindung im Host per `file:./linux-desktop-chat-persistence` (später optional PyPI-Pin) — analog `linux-desktop-chat-projects` / `linux-desktop-chat-workflows`. |
| **Einordnung** | Dritter Baustein der **`ldc-workspace-data`**-Story neben [`app.projects`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md) und [`app.workflows`](PACKAGE_WORKFLOWS_PHYSICAL_SPLIT.md). |
| **Nicht-Ziel** | Keine Umbenennung des Importpfads **`app.persistence`**, keine Erweiterung der öffentlichen Oberfläche aus Split-Komfort, keine Refactors der ORM-Modelle oder Service-Logik nur wegen des Umzugs. |

---

## 2. Zielstruktur des neuen Wheels

| | Pfad / Vorgabe |
|---|----------------|
| **Monorepo-Root (Arbeitsname)** | `linux-desktop-chat-persistence/` (Top-Level, analog [`linux-desktop-chat-projects/`](../../linux-desktop-chat-projects/)) |
| **Quellbaum** | `linux-desktop-chat-persistence/src/app/persistence/**/*.py` (1:1 aus ehemaligem Host-Baum `app/persistence/`) |
| **Build** | `[tool.setuptools.packages.find]` mit `where = ["src"]`, `include = ["app*"]` |
| **Begleitdateien** | `pyproject.toml`, `README.md`; Host-Tests bleiben primär im Monorepo-Host (optional später Wheel-Smokes). |

*Umsetzung und Anlage des Verzeichnisses erfolgen erst nach Erfüllung von §6–§7 und nach Freigabe dieses Runbooks.*

---

## 3. Import- und Namespace-Invariante

| Regel | Inhalt |
|-------|--------|
| **Variante B** | Alle Importstrings bleiben **`from app.persistence…`** / **`import app.persistence`** — kein Präfixwechsel. |
| **Namespace** | Host-[`app/__init__.py`](../../app/__init__.py) behält **`pkgutil.extend_path`**; das Wheel erweitert denselben **`app`**-Namespace. |
| **Öffentliche Oberfläche** | Paket-Root [`app/persistence/__init__.py`](../../app/persistence/__init__.py) exportiert nach Cut weiterhin u. a. `Base`, `get_database_url`, `get_engine`, `get_session_factory`, `session_scope` — Abgleich mit Guards nach Einführung von `test_persistence_split_readiness_guards.py` (siehe §9). |

---

## 4. Bekannte Konsumenten / Kopplungen

| Bereich | Rolle |
|---------|--------|
| **`app/services/*`** | Breite Nutzung von `session_scope`, `enums`, `orm.models`, `base` (Model-Usage, lokale Modelle, Katalog, Quotas). |
| **`app/agents/agent_task_runner.py`** | Lazy-Import von `app.persistence.enums`. |
| **`app/services/chat_service.py`** | Lazy-Import von `UsageType`. |
| **`alembic/env.py`** | Lädt `Base`, `orm.models` (Registrierung), `get_database_url` — läuft im Host-Kontext; Voraussetzung: installiertes `app.persistence` nach Cut. |
| **`scripts/qa/run_context_experiment.py`** | Engine/Reset für Experimente. |
| **Tests** | u. a. `tests/unit/test_phase_a_orm_services.py`, `test_phase_b_model_chat_runtime.py`, `test_unified_model_catalog_service.py`, `test_model_usage_*`, `test_local_model_scanner_service.py`, `tests/integration/test_model_usage_sqlite_file_gate.py`, `tests/test_chat_streaming_toggle.py`. |

**Abgrenzung:** `app.workflows.persistence` (**`linux-desktop-chat-workflows`**) ist ein **anderes** Paket — kein Merge mit `app.persistence`.

**Segment-Policy:** `persistence` bleibt Backbone ohne direkte `app.gui`-Kante (bestehende Segment-Regeln unverändert).

---

## 5. Notwendige Packaging-Abhängigkeiten

| Abhängigkeit | Begründung |
|---------------|------------|
| **`SQLAlchemy>=2.0`** (Wheel-`dependencies`) | ORM, Engine, Session — bereits im Host vorhanden; Wheel muss für isolierte Installierbarkeit dieselbe Mindestlinie deklarieren. |
| **Host-Module** (`app.services`, `app.agents`, …) | **Keine** PEP-508-Zeile im Persistence-Wheel zwingend: Konsumenten liegen im Host; Importrichtung **Host → persistence**, nicht umgekehrt. |
| **`alembic`** | Verbleibt **Host**-Concern; Persistence-Wheel liefert nur importierbare Metadata/URL-Hilfen. |

**Governance:** Bei Cut Abgleich mit [`PACKAGE_MAP.md`](PACKAGE_MAP.md) und Release-Matrix / `dependency_packaging`-Drift-Checks.

---

## 6. Hauptblocker: DB-URL-Default und Dateitiefe

Die heutige Default-Logik in [`app/persistence/session.py`](../../app/persistence/session.py) leitet ohne gesetztes `LINUX_DESKTOP_CHAT_DATABASE_URL` den SQLite-Pfad vom **Monorepo-Root** ab über **`Path(__file__).resolve().parents[2]`**.

Das setzt voraus, dass `session.py` genau **zwei** Ebenen unter dem Repo-Root liegt (`app/persistence/session.py`). Nach Verlegung nach **`…/src/app/persistence/session.py`** ist **`parents[2]` nicht mehr der Monorepo-Root** — Default würde **falsch** (z. B. unter `src/`), mit Risiko für **`chat_history.db`**, Alembic-Erwartungen und lokale Entwickler-Workflows.

**Festlegung:** Ein physischer Cut ist **erst zulässig**, wenn der Default **nicht mehr** an dieser festen Dateitiefe hängt (oder wenn ein in diesem Runbook explizit beschriebener Ersatzmechanismus die bisherige Semantik **garantiert**).

---

## 7. Empfohlene Minimalstrategie für den Vor-Schritt (Festlegung, keine Umsetzung)

| # | Strategieelement |
|---|------------------|
| S1 | **Zielsemantik festhalten:** Ohne `LINUX_DESKTOP_CHAT_DATABASE_URL` soll weiterhin dieselbe **fachliche** Bedeutung gelten wie heute: SQLite-Datei **`chat_history.db` am Monorepo-Root** bei typischem `pip install -e .` am Root (sofern das Produkt das beibehalten will — Abweichung nur mit Release-Note). |
| S2 | **Root-Erkennung unabhängig von Pakettiefe:** z. B. Aufwärtssuche nach einem vereinbarten Anker (z. B. Host-`pyproject.toml` mit Projektname `linux-desktop-chat`), oder zentraler Hilfsfunktion im Host, die das Persistence-Modul nur **konfiguriert** — konkrete Wahl im Implementierungs-PR, aber **ohne** Wiederholung des `parents[2]`-Musters relativ zu `session.py` im Wheel. |
| S3 | **Env-Override unverändert prioritär:** `LINUX_DESKTOP_CHAT_DATABASE_URL` bleibt die höchste Priorität (Tests, CI, Sonderpfade). |
| S4 | **Alembic und Doku:** Nach Implementierung von S1–S3 kurz verifizieren, dass `alembic/env.py` und Betriebsdoku dieselbe URL-Quelle erwarten; bei Semantikänderung Drift in Architektur-/Operations-Doku abstimmen. |

Dieser Abschnitt ist **nur** die governance-taugliche Vorgabe; die konkrete Code-Implementierung erfolgt in einem **separaten** Schritt vor oder unmittelbar am Anfang der Split-Implementierung.

---

## 8. Host-`pyproject.toml`-Nachzug (nach Cut)

- Eintrag in **`[project].dependencies`:**  
  `"linux-desktop-chat-persistence @ file:./linux-desktop-chat-persistence"`  
  (Reihenfolge konsistent zu bestehenden `file:`-Einträgen.)
- Sicherstellen, dass **`app/persistence/`** im Host-Tree **nicht** mehr existiert bzw. nicht mehr vom Host-`packages.find` erfasst wird.

---

## 9. Guard- / SYSTEM_MAP- / Doku-Nachzug

| Artefakt | Vorgabe |
|----------|---------|
| **Hilfsmodul** | Analog [`tests/architecture/app_projects_source_root.py`](../../tests/architecture/app_projects_source_root.py): `app_persistence_source_root()` via `importlib.util.find_spec("app.persistence")`. |
| **Split-Readiness-Guards** | Neues Modul z. B. `test_persistence_split_readiness_guards.py`: kein Qt/`app.gui`, dokumentierte minimale Außenkanten (Ist: voraussichtlich **keine** `app.*`-Imports aus dem Persistence-Paket außer intern `app.persistence.*`); Abgleich `__all__` am Paket-Root. |
| **`tools/generate_system_map.py`** | `_inject_embedded_app_namespace_lines` um Zeile ergänzen, z. B. `linux-desktop-chat-persistence/src/app/persistence/   # Import app.persistence`. |
| **`docs/SYSTEM_MAP.md`** | Regenerieren und committen (`python3 tools/generate_system_map.py`). |
| **`PACKAGE_MAP.md`** | Zeile „Projekte / Persistenz“ / Persistence-Pfad auf eingebettetes Wheel und Status „physisch gesplittet“. |
| **`PACKAGE_SPLIT_PLAN.md`** | Matrix §3.7 / Zeile `persistence`: Ist-Pfad und Verweis auf **dieses Runbook**. |
| **Streu-Doku** | Pfade `app/persistence/` schrittweise auf logischen Importpfad bzw. Wheel-Pfad vereinheitlichen (kein Blocker für technischen Cut, reduziert Release-Drift). |

---

## 10. Validierungs- und Abnahmekriterien

Nach Umsetzung von **Vor-Schritt (§7)** und **physischem Cut** (separate PRs möglich):

| # | Kriterium |
|---|-----------|
| V1 | `pip install -e .` am Monorepo-Root; `find_spec("app.persistence")` zeigt auf **`linux-desktop-chat-persistence/.../persistence`**. |
| V2 | Kurzimporte: `from app.persistence import Base, session_scope, get_database_url` sowie Stichprobe aus `app.services` ohne `ModuleNotFoundError`. |
| V3 | **Default-DB:** Ohne Env-Override liegt bzw. wird erwartungsgemäß **`chat_history.db` am Monorepo-Root** verwendet (oder dokumentierte, bewusst geänderte Semantik + Release-Note). |
| V4 | `pytest tests/architecture/test_persistence_split_readiness_guards.py -q` grün (sobald angelegt). |
| V5 | Volle Host-Suite grün (mindestens alle bisherigen Persistence- und Model-Usage-bezogenen Tests). |
| V6 | Alembic: Import von `alembic/env.py` bzw. bestehender Migrations-Workflow ohne Regression. |
| V7 | Regeneriertes **`docs/SYSTEM_MAP.md`** zeigt eingebetteten Persistence-Pfad. |

---

## 11. Empfohlene Commit-Reihenfolge

1. **DB-URL-/Root-Entkopplung** (§7): Code + gezielte Tests/Doku — **ohne** Verschieben von `app/persistence/`; Abnahme: V3-Semantik + relevante Tests grün.  
2. **Wheel-Scaffold + Verschiebung:** `linux-desktop-chat-persistence/` anlegen, Quellen verschieben, Host-`pyproject` binden, Host-`app/persistence/` entfernen.  
3. **Guards + SYSTEM_MAP-Generator + regenerierte SYSTEM_MAP.**  
4. **Kanonical Doku:** `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md`; Status dieses Runbooks auf „umgesetzt“ anheben.  
5. **Streu-Doku** (optional eigener Commit): Pfade in FEATURES/operations konsolidieren.

---

## Referenz: Ist-Stand Blocker (zur Traceability)

Die Default-URL darf nicht dauerhaft von **`parents[2]` relativ zu `session.py`** abhängen — siehe §6. Nach Entkopplung ist dieser Abschnitt historisch; die Implementierung dokumentiert die gewählte Root-Strategie in Code-Kommentar oder kurzem ADR-Verweis.
