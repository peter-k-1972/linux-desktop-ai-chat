# Cut-Liste: `linux-desktop-chat-providers` (Commit 1 → späterer Host-Cut)

**Stand:** Vorlage im Host-Monorepo unter `linux-desktop-chat-providers/`. Nach Auslagerung als eigenes Repo bleibt diese Datei im Providers-Repo; der Host verweist in seiner Doku auf die veröffentlichte Version.

---

## 1. 1:1 aus `app/providers/` ins Providers-Repo (`src/app/providers/`)

Alle Python-Module — **ohne Importpfad-Änderung** (weiter `app.providers.*` intern):

| Bereich | Pfade |
|---------|--------|
| Paket-Root | `__init__.py`, `base_provider.py`, `ollama_client.py`, `local_ollama_provider.py`, `cloud_ollama_provider.py`, `orchestrator_provider_factory.py` |

**Repo-spezifische Anpassungen am Produktcode:** keine für Commit 1 (Quelle = Spiegel des Hosts).

**Zusätzlich im Providers-Repo (nicht unter `app/providers/` im Host):**

- `src/app/__init__.py` — Paketmarker für installierbares `app.providers`.
- `src/app/utils/__init__.py`, `src/app/utils/env_loader.py` — **Spiegel** von `app/utils/` im Host, weil `cloud_ollama_provider.py` `from app.utils.env_loader import load_env` nutzt. **Sync-Regel:** Änderungen am Host-`app/utils/env_loader.py` (und ggf. `__init__.py`) **ebenfalls** in die Vorlage übernehmen, bis eine Entkopplung erfolgt.

---

## 2. Dokumentation

| Mit ins Providers-Repo | Bleibt / primär im Host |
|------------------------|-------------------------|
| `README.md`, `MIGRATION_CUT_LIST.md`, `pyproject.toml` | `docs/architecture/PACKAGE_PROVIDERS_*.md`, `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md` |

---

## 3. Tests

### Im Providers-Repo (`tests/`) — minimale **isolierte** Suite

Läuft **ohne** installierten Host (`app.services`, `app.gui`, Architektur-Guards):

| Datei | Inhalt |
|-------|--------|
| `test_imports.py` | Smoke: Root-Exports aus `app.providers` |
| `test_basic_runtime.py` | Leichtgewichtige Laufzeit (z. B. Client schließen, Factory) |

### Nur im Host — volle Integration / Governance

| Testdatei / Muster | Grund |
|--------------------|--------|
| `tests/architecture/test_provider_orchestrator_governance_guards.py` | Host-Segment-Regeln |
| `tests/unit/test_ollama_*.py` | können weiter auf Host-`app/providers` zeigen bis Commit 2 |

---

## 4. Nicht mitwandern (Commit 1)

- `app/services/**`, `app/core/**`, Host-`pyproject.toml`, `.github/workflows/` (spätere Commits).
- Öffentliche Oberflächen- und Segment-Guards im Host.

---

## 5. Sync-Hinweis (bis zum Host-Cut)

**Richtung:** **Host → Vorlage** (Copy-Quelle ist der Host).

1. **`app/providers/**`** im Host und **`linux-desktop-chat-providers/src/app/providers/**`** müssen **byte-identisch** (oder fachlich identisch) bleiben — **keine** divergierenden Änderungen nur in einem Baum.
2. **`app/utils/env_loader.py`** und **`app/utils/__init__.py`** im Host ↔ **`src/app/utils/`** in der Vorlage — bei Änderungen am Host **mitspiegeln**.

**Commit 2** darf erst starten, wenn beide Stände (Provider-Baum + genannte `utils`-Dateien) **abgestimmt** sind und die Vorlage installierbar/testbar bleibt.
