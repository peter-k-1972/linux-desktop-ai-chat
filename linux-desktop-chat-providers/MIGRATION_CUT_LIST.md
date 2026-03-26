# Cut-Liste: `linux-desktop-chat-providers` (Commit 1 → späterer Host-Cut)

**Stand:** Vorlage im Host-Monorepo unter `linux-desktop-chat-providers/`. Nach Auslagerung als eigenes Repo bleibt diese Datei im Providers-Repo; der Host verweist in seiner Doku auf die veröffentlichte Version.

**Ab Welle 6:** **`app.utils`** nur aus **`linux-desktop-chat-utils`**; kein `src/app/utils/`-Spiegel mehr. In **`pyproject.toml`** gibt es **keine** `file:`-Abhängigkeit auf `utils` (pip löst relative `file:`-URLs gegen das **aktuelle Arbeitsverzeichnis** auf — bricht z. B. bei `pip install -e ./linux-desktop-chat-providers` vom Repo-Root). Der **Host** listet `linux-desktop-chat-utils` und `linux-desktop-chat-providers` getrennt; isoliert: siehe **`README.md`** (zuerst `utils` installieren).

---

## 1. 1:1 aus `app/providers/` ins Providers-Repo (`src/app/providers/`)

Alle Python-Module — **ohne Importpfad-Änderung** (weiter `app.providers.*` intern):

| Bereich | Pfade |
|---------|--------|
| Paket-Root | `__init__.py`, `base_provider.py`, `ollama_client.py`, `local_ollama_provider.py`, `cloud_ollama_provider.py`, `orchestrator_provider_factory.py` |

**Repo-spezifische Anpassungen am Produktcode:** keine für Commit 1 (Quelle = Spiegel des Hosts).

**Zusätzlich im Providers-Repo (nicht unter `app/providers/` im Host):**

- `src/app/__init__.py` — Paketmarker für installierbares `app.providers`.
- ~~`src/app/utils/`~~ — **entfernt (Welle 6):** `app.utils` kommt aus `linux-desktop-chat-utils`.

---

## 2. Dokumentation

| Mit ins Providers-Repo | Bleibt / primär im Host |
|------------------------|-------------------------|
| `README.md`, `MIGRATION_CUT_LIST.md`, `pyproject.toml` | `docs/architecture/PACKAGE_PROVIDERS_*.md`, `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md` |

---

## 3. Tests

### Im Providers-Repo (`tests/`) — minimale **isolierte** Suite

Läuft mit installiertem **`linux-desktop-chat-utils`** (siehe **`README.md`**: z. B. `pip install -e ../linux-desktop-chat-utils` vor `pip install -e .` im Providers-Ordner, oder beide `-e` vom Repo-Root):

| Datei | Inhalt |
|-------|--------|
| `test_imports.py` | Smoke: Root-Exports aus `app.providers` |
| `test_basic_runtime.py` | Leichtgewichtige Laufzeit (z. B. Client schließen, Factory) |

### Nur im Host — volle Integration / Governance

| Testdatei / Muster | Grund |
|--------------------|-------|
| `tests/architecture/test_provider_orchestrator_governance_guards.py` | Host-Segment-Regeln |
| `tests/unit/test_ollama_*.py` | können weiter auf `app.providers` zeigen |

---

## 4. Nicht mitwandern (Commit 1)

- `app/services/**`, `app/core/**`, Host-`pyproject.toml`, `.github/workflows/` (spätere Commits).
- Öffentliche Oberflächen- und Segment-Guards im Host.

---

## 5. Sync-Hinweis (Host-Cut)

**Richtung:** **Host → Vorlage** für `app/providers/**`.

1. **`app/providers/**`** im Host und **`linux-desktop-chat-providers/src/app/providers/**`** müssen fachlich übereinstimmen — keine divergierenden Änderungen nur in einem Baum.
2. **`app.utils`** wird in **`linux-desktop-chat-utils`** gepflegt; keine manuelle Spiegelung in die Provider-Vorlage.
