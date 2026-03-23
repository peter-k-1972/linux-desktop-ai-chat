# Phase A – ORM-Fundament Model-Usage (Abschlussbericht)

## A. Ist-Analyse (Kurzfassung)

| Bereich | Befund |
|--------|--------|
| **Persistenz bisher** | SQLite über `DatabaseManager` und diverse Repositories mit **rohem sqlite3**; **kein SQLAlchemy/Alembic** im Anwendungscode. |
| **„ORM-Struktur“** | Phase A **stellt** die kanonische ORM-Schicht bereit unter `app/persistence/`; Legacy-Tabellen bleiben unverändert. |
| **Provider / API-Key** | Logische Konfiguration in `AppSettings` / Umgebung; **keine** Tabelle `provider_credentials` – `provider_credential_id` ist vorbereitet (nullable), ohne FK. |
| **Modell-IDs** | Weiterhin `app.core.models.registry` (Domain „LLM-Modelle“); SQLAlchemy-Entitäten liegen bewusst unter `app.persistence.orm`, um Namenskollisionen zu vermeiden. |

## B. Umsetzungsplan → erledigt

1. Abhängigkeiten: `SQLAlchemy>=2.0`, `alembic>=1.13` in `requirements.txt`.
2. Paket `app/persistence/`: `Base`, Session/Engine, Enums, ORM-Modelle.
3. Alembic: `alembic.ini`, `alembic/env.py`, Revision `phase_a_001`.
4. Services: `model_usage_service`, `model_usage_aggregation_service`, `model_quota_service`, `local_model_registry_service`.
5. Domain-Helfer: `app/domain/model_usage/periods.py` (UTC, Woche ab Montag).
6. Tests: `tests/unit/test_phase_a_orm_services.py`.
7. Entfernt: frühere sqlite3-Usage-Repository-Schicht, GUI-/Runtime-Usage-Hooks (nicht Teil Phase A).

## C. Neue Dateien

- `app/persistence/base.py`, `session.py`, `enums.py`, `__init__.py`
- `app/persistence/orm/models.py`, `app/persistence/orm/__init__.py`
- `app/domain/model_usage/__init__.py`, `app/domain/model_usage/periods.py`
- `app/services/model_usage_service.py`
- `app/services/model_usage_aggregation_service.py`
- `app/services/model_quota_service.py`
- `app/services/local_model_registry_service.py`
- `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`
- `alembic/versions/phase_a_001_model_usage_foundation.py`
- `tests/unit/test_phase_a_orm_services.py`
- `docs/PHASE_A_ORM_REPORT.md`

## D. Geänderte Dateien

- `requirements.txt` (SQLAlchemy, Alembic)
- `app/core/models/orchestrator.py` (zurück auf schlanken Chat ohne Usage)
- `app/services/chat_service.py` (wieder direkt `OllamaClient`)
- `app/core/config/settings.py` (Entfernung der Usage-Settings-Flags)
- `app/services/infrastructure.py` (Entfernung Usage/Orchestrator-Resets)
- `app/core/models/__init__.py` (kein `get_model_orchestrator`)
- `app/gui/domains/operations/chat/panels/chat_details_panel.py` (kein Usage-Panel)
- `app/gui/domains/settings/panels/model_settings_panel.py` (kein Usage-Card)

## E. Architekturentscheidungen

1. **Gemeinsame DB-Datei**: Standard-URL `sqlite:///…/chat_history.db` (Projektroot), überschreibbar mit `LINUX_DESKTOP_CHAT_DATABASE_URL` (wie in Alembic `env.py`).
2. **Zeitstempel**: ORM mit `server_default=func.now()` bzw. `false()`/`true()` für Booleans; Migration nutzt `CURRENT_TIMESTAMP` für SQLite-Kompatibilität.
3. **Ledger-Feld `estimated_tokens`**: als **Boolean** umgesetzt (Spezifikation Phase A); Gesamtzahlen bleiben in `prompt_tokens` / `completion_tokens` / `total_tokens`.
4. **Aggregationsschlüssel**: eindeutig über `(model_id, provider_id_key, provider_credential_id_key, scope_type, scope_ref_key, period_type, period_start)`; Sentinel `-1` / leere Strings statt SQL-NULL in Unique-Keys.
5. **Total-Periode**: fester Anker `1970-01-01T00:00:00+00:00` in `period_starts["total"]`.
6. **Upsert**: SQLite `INSERT … ON CONFLICT DO UPDATE` über `index_elements` (SQLAlchemy 2).
7. **Keine Businesslogik in ORM-Klassen**; Services kapseln Validierung, Aggregation, Quota-Logik.

## F. Funktional nach Phase A

- Anlegen und Abfragen von `ModelUsageRecord` inkl. Validierung und Status/Estimated-Flag.
- Inkrementelle Aggregationen + vollständiger **Rebuild** aus dem Ledger.
- Quota-Policies laden, **effektive Limits** (strengstes Limit), **Snapshot** aus Aggregaten, **Preflight-Vorbereitung** (`evaluate_usage_against_quota`).
- Storage-Roots und `ModelAsset` inkl. Verfügbarkeit und Modell-Verknüpfung; Pfadnormalisierung.
- Migration `phase_a_001` auf frischer DB verifiziert; Seed-Policy `offline_default` (mode `none`).

## G. Bewusst offen für Phase B

- Runtime-Instrumentierung aller Modellaufrufe (Orchestrator / ChatService).
- GUI für Usage/Quotas/Artefakte.
- Vollständiger Verzeichnis-Scanner für `~/ai/` oder konfigurierte Roots.
- Tabelle / ORM für **Provider Credentials** und echte FKs auf `provider_credential_id`.
- Erweiterte Policy-Matcher (z. B. Wildcards für `provider_id` überall vereinheitlichen).
- Abbruch/Cancel: konsistentes `CANCELLED` in der Aufrufkette.

## H. Tests

- `pytest tests/unit/test_phase_a_orm_services.py` – ORM-Defaults, Unique-Constraints, Usage-, Aggregations-, Quota- und Registry-Pfade.
- Gesamtlauf `tests/unit/` grün nach Integration.
