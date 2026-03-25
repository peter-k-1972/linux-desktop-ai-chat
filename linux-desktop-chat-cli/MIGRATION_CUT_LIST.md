# Cut-Liste: `linux-desktop-chat-cli` (Commit 1 → Host-Cut)

**Stand:** Eingebettete Vorlage im Host-Monorepo unter `linux-desktop-chat-cli/`. Nach Auslagerung als eigenes Repo bleibt diese Datei im CLI-Repo; der Host verweist in seiner Doku auf die veröffentlichte Version.

---

## 1. 1:1 aus `app/cli/` ins CLI-Repo (`src/app/cli/`)

Alle Python-Module — **ohne Importpfad-Änderung** (weiter `app.cli.*` intern):

| Bereich | Pfade |
|---------|--------|
| Paket-Root | `__init__.py`, `context_replay.py`, `context_repro_run.py`, `context_repro_batch.py`, `context_repro_registry_list.py`, `context_repro_registry_rebuild.py`, `context_repro_registry_set_status.py` |

**Repo-spezifische Anpassungen am Produktcode:** keine für Commit 1 (Quelle = Spiegel des Hosts vor Cut).

**Zusätzlich im CLI-Repo (nicht unter `app/cli/` im Host):**

- `src/app/__init__.py` — Namespace-Markierung für installierbares `app.cli` (Variante B, `pkgutil.extend_path` im Host-`app`).

---

## 2. Dokumentation

| Mit ins CLI-Repo | Bleibt / primär im Host |
|------------------|-------------------------|
| `README.md`, `MIGRATION_CUT_LIST.md`, `pyproject.toml` | `docs/architecture/PACKAGE_CLI_*.md`, `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md` |

---

## 3. Tests

### Im CLI-Repo (`tests/`) — minimale Suite

| Datei | Inhalt |
|-------|--------|
| `test_imports.py` | Smoke: Paket `app.cli` importierbar; erwartete Module auf der Platte |
| `test_basic_runtime.py` | Laufzeit-Smoke für `run_*`-Symbole **nur**, wenn Host-Domäne `app.context` installiert ist (sonst Skip) |

### Nur im Host — volle Integration / Governance

| Testdatei / Muster | Grund |
|--------------------|--------|
| `tests/architecture/test_cli_public_surface_guard.py` | Public Surface, verbotene Kanten aus `FORBIDDEN_IMPORT_RULES` |
| `tests/cli/test_context_*_cli.py` | End-to-End gegen Replay-/Repro-Fixtures |

---

## 4. Nicht mitwandern (Commit 1)

- `app/context/**`, `app/services/**`, Host-`pyproject.toml`, `.github/workflows/` (spätere Commits).
- Öffentliche Oberflächen- und Segment-Guards im Host.

---

## 5. Sync-Hinweis (bis zum Host-Cut)

**Richtung:** **Host → Vorlage** (Copy-Quelle ist der Host), solange beide Bäume existieren.

1. **`app/cli/**`** im Host und **`linux-desktop-chat-cli/src/app/cli/**`** müssen **inhaltlich identisch** bleiben — **keine** divergierenden Änderungen nur in einem Baum.
2. Nach Host-Cut ist **nur** die Vorlage unter `linux-desktop-chat-cli/src/app/cli/` die kanonische Quelle für das Segment `app.cli`.

**Ist-Abweichung (möglich):** Fehlt **`app/cli/`** im Host bereits (früherer Cut), entfällt die Parallelphase; **kanonisch** ist dann **`linux-desktop-chat-cli/src/app/cli/`** — Änderungen nur dort, bis Commit 2 dokumentiert nachgezogen wird.

**Laufzeit:** CLI-Module importieren **`app.context.replay.*`**. Isoliertes `pip install -e .` **ohne** Host `linux-desktop-chat` liefert keine vollständigen Replay-/Repro-Läufe; siehe `README.md`.
