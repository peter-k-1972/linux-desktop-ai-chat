# Test Execution Report — Linux Desktop Chat

**Rolle:** QA / technische Verifikation (nur Ausführung & Dokumentation, keine Code-Fixes)  
**Datum:** 2026-03-21  
**Umgebung (Hauptlauf):** Python 3.12.3, Projekt-Virtualenv `.venv`, `pip install -r requirements.txt`

---

## 1. Zusammenfassung

| Kriterium | Ergebnis (mit `.venv`) |
|-----------|-------------------------|
| Collection Errors | **0** (1414 Tests gesammelt) |
| Failures | **0** |
| Errors (Laufzeit) | **0** |
| Timeouts | **Keine** (kein aktives `pytest-timeout` in `pytest.ini`; Lauf endete normal) |
| Skips | **6** (bedingt durch fehlende optionale Artefakte, siehe unten) |

---

## 2. Referenz: Lauf ohne Virtualenv (System-Python)

Zur Einordnung der lokalen „CI-ähnlichen“ Ausführung wurde zusätzlich versucht, mit dem systemweiten `python3` / `pip` wie im Workflow zu installieren und zu sammeln.

| Schritt | Ergebnis |
|---------|----------|
| `pip install -r requirements.txt` (systemweit) | **Fehlgeschlagen** — PEP 668 *externally-managed-environment* |
| `pytest --collect-only` ohne vorherige Installation in venv | **30 Collection Errors** — u. a. `ModuleNotFoundError: qasync`, `ModuleNotFoundError: deepdiff` |

**Ursache:** Auf dem Prüfhost blockiert die Distribution die systemweite Paketinstallation; ohne aktiviertes Virtualenv fehlen die in `requirements.txt` deklarierten Pakete, obwohl sie dort eingetragen sind.

**Implikation für CI:** GitHub Actions (`actions/setup-python`) installiert typischerweise in eine isolierte Präfix-Umgebung — dort ist dieses spezifische PEP-668-Problem in der Regel nicht identisch. **Lokal** entspricht die CI-Simulation zuverlässig einem Befehlssatz **plus** aktivem venv (siehe Abschnitt 4).

---

## 3. Pytest FULL RUN (komplette Suite)

**Kommandos:**

```bash
.venv/bin/pytest --collect-only -q    # CI-Schritt „collect-only“
.venv/bin/pytest -q --tb=short --durations=20
```

| Metrik | Wert |
|--------|------|
| Gesammelte Tests | **1414** (in ~0,67 s) |
| Exit-Code | **0** |
| Wandzeit (Full Run) | **~124,3 s** |
| Langsamster Test (Call) | `tests/integration/test_chat_prompt_integration.py::test_prompt_menu_with_prompts` — **9,16 s** |
| Weitere auffällige Laufzeiten | Architektur-Drift-Radar ~5,9 s; App-Startup-Smoke ~4,0 s (siehe `TEST_STABILITY_REPORT.md`) |

### 3.1 Skips (vollständiger Lauf)

Alle Skips waren **erwartbare** Bedingungen (fehlende Dateien/Artefakte):

| Datei / Test | Grund (Auszug) |
|--------------|----------------|
| `tests/qa/coverage_map/test_coverage_map_governance.py` (mehrere) | `QA_TEST_INVENTORY.json`, `QA_TEST_STRATEGY.json`, `QA_KNOWLEDGE_GRAPH.json`, `QA_AUTOPILOT_V3.json` nicht vorhanden |
| `tests/qa/test_inventory/test_inventory_governance.py` | `REGRESSION_CATALOG.md` existiert nicht |

**Hinweis:** Das sind **keine** Failures; die Suite gilt unter pytest als erfolgreich mit Skip.

### 3.2 Warnungen / Nebenbefunde (kein Test-Failure)

- Am Ende des Full Runs erschienen Meldungen zu **nicht geschlossenen `aiohttp.ClientSession`**-Instanzen (Ressourcen-Warnung, nicht als Test-Fehler gewertet).

---

## 4. CI-Simulation (lokal)

**Workflow-Referenz:** `.github/workflows/pytest-full.yml`

| CI-Schritt | Lokales Äquivalent | Ergebnis |
|------------|-------------------|----------|
| Python 3.12 | 3.12.3 | OK |
| `pip install -r requirements.txt` | `.venv/bin/pip install -r requirements.txt` | OK |
| `pytest --collect-only -q` | `.venv/bin/pytest --collect-only -q` | **OK** (Wandzeit ~1,2 s) |
| `pytest -q --tb=short` | `.venv/bin/pytest -q --tb=short --durations=20` | **OK** |

Abweichung: Lokaler **System-Python** ohne venv entspricht dem Workflow **nicht** (siehe Abschnitt 2).

---

## 5. PARTIAL RUNS (Verzeichnisweise)

Alle Läufe mit `.venv/bin/pytest -q --tb=short <pfad>`.

| Verzeichnis | Gesammelt (laut `pytest --collect-only`) | Wandzeit | Exit |
|-------------|------------------------------------------|----------|------|
| `tests/unit` | 275 | ~3,5 s | 0 |
| `tests/architecture` | 113 | ~12,3 s | 0 |
| `tests/chat` | 86 | ~4,0 s | 0 |
| `tests/context` | 145 | ~19,4 s | 0 |
| `tests/qa` | 248 | ~30,6 s | 0 |

**Skips:** Nur im Partial `tests/qa` dieselben **6** Skips wie im Full Run (Governance/Inventory-Artefakte).

---

## 6. EDGE CASES (gezielte Unterläufe)

Fokus: **DB-Schreibpfade**, **Kontext-Injection**, **Provider/Ollama-nahe Unit- und Cross-Layer-Tests** (ohne separate Live-Infrastruktur-Pflicht für die gewählten Dateien).

**Kommando:**

```bash
.venv/bin/pytest -q --tb=short \
  tests/test_db_files.py \
  tests/integration/test_sqlite.py \
  tests/structure/test_chat_context_injection.py \
  tests/unit/test_ollama_stream_chat_simulation.py \
  tests/unit/test_ollama_ndjson_stream.py \
  tests/cross_layer/test_prompt_apply_affects_real_request.py
```

| Metrik | Wert |
|--------|------|
| Gesammelte Tests | **39** |
| Exit-Code | **0** |
| Wandzeit | **~2,7 s** |

---

## 7. Failures mit Ursache

**Keine** Test-Failures und **keine** Laufzeit-Errors in der verifizierten Konfiguration (`.venv` + `requirements.txt`).

Collection-Failures traten **nur** ohne funktionierende Dependency-Installation auf (Abschnitt 2).

---

## 8. Methodik / Einschränkungen

- **Ein** vollständiger grüner Durchlauf dokumentiert; wiederholte Serien für Flake-Nachweis siehe `TEST_STABILITY_REPORT.md`.
- Ein zweiter Full-Run an `pytest | tail` hing (Pipe-Puffer / Blockierung); dieser wurde abgebrochen — **kein** Einfluss auf den ersten vollständigen erfolgreichen Lauf.
