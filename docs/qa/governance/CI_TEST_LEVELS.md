# QA Level 3 – CI / Test-Gating-Struktur

**Datum:** 15. März 2026  
**Zweck:** Stufung der Testausführung für CI. Fast → Full → Live.

---

## 1. Test-Level (Stufen)

| Level | Beschreibung | Dauer | Verwendung |
|-------|--------------|-------|------------|
| **fast** | Unit, Contract – ohne DB, ohne Netzwerk | ~30s | Pre-Commit, schnelle Feedback-Schleife |
| **full** | + Integration, Async, Failure, Cross-Layer, Startup | ~2–5 min | PR-Check, Merge-Gate |
| **live** | Echte Ollama, RAG, Agent-Ausführung | variabel | Manuell, Nacht-Build |

---

## 2. pytest-Kommandos

### Standard (fast + full, ohne live/slow)

```bash
pytest -m "not live and not slow"
```

**Empfohlen für:** PR-Check, Merge-Gate, CI-Standard.

### Nur fast (schnell)

```bash
pytest -m "contract or (unit and not integration)"
```

Oder explizit:

```bash
pytest tests/unit tests/contracts -m "not live and not slow"
```

**Empfohlen für:** Pre-Commit, lokale Schnellprüfung.

### Full (ohne live)

```bash
pytest -m "not live and not slow"
```

**Empfohlen für:** PR, Merge.

### Live (manuell)

```bash
pytest -m "live"
```

**Voraussetzung:** Ollama läuft, ggf. ChromaDB.

---

## 3. Marker-Gruppen

| Gruppe | Marker | Enthalten |
|--------|--------|-----------|
| fast | `contract`, `unit` (ohne integration) | Schnelle Tests |
| full | `contract`, `unit`, `integration`, `async_behavior`, `failure_mode`, `cross_layer`, `startup`, `ui`, `smoke`, `golden_path` | Alles außer live/slow |
| live | `live` | Ollama, RAG, Agent |
| slow | `slow` | Langsame Tests |

---

## 4. Konkrete CI-Empfehlung

### GitHub Actions / GitLab CI (Beispiel)

```yaml
# Stufe 1: Fast (optional, für Pre-Commit)
test-fast:
  script: pytest tests/unit tests/contracts -m "not live and not slow" -q

# Stufe 2: Full (PR-Gate)
test-full:
  script: pytest -m "not live and not slow" -q

# Stufe 3: Live (optional, scheduled)
test-live:
  script: pytest -m "live" -q
  when: manual  # oder scheduled
```

### Lokale Entwicklung

```bash
# Schnell: vor jedem Commit
pytest tests/unit tests/contracts -q

# Voll: vor Merge
pytest -m "not live and not slow"
```

---

## 5. Bestehende Marker (pytest.ini)

| Marker | Zweck |
|--------|-------|
| unit | Unit-Tests |
| ui | UI-Tests |
| smoke | Smoke |
| integration | Integration |
| live | Live (Ollama etc.) |
| slow | Langsam |
| golden_path | E2E |
| regression | Regression |
| async_behavior | Async |
| contract | Contract |
| failure_mode | Failure |
| cross_layer | Cross-Layer |
| state_consistency | State |
| startup | Startup |
| fast | Schnell |
| full | Voll |

---

## 6. Qualitäts-Gate (Mindestanforderung)

```bash
# Alle Tests müssen grün sein (ohne live/slow)
pytest -m "not live and not slow" --tb=short
```

**Gate:** Exit Code 0 für Merge.

---

## 7. QA-Cockpit (CI-Integration)

Das QA-Cockpit generiert `docs/qa/QA_STATUS.md` mit Governance-Signalen.

### Ausführung

```bash
# Mit venv (empfohlen)
.venv/bin/python scripts/qa/qa_cockpit.py

# Oder
python scripts/qa/qa_cockpit.py
```

### CI-Integration (Beispiel)

```yaml
# Nach test-full, vor Merge
qa-cockpit:
  script:
    - python scripts/qa/qa_cockpit.py --json
  artifacts:
    paths:
      - docs/qa/QA_STATUS.md
      - docs/qa/QA_STATUS.json
```

### Empfohlene Reihenfolge

1. `pytest -m "not live and not slow"` – Tests
2. `pytest tests/meta/ -v` – Drift-Sentinels (Marker, EventType)
3. `python3 scripts/qa/generate_qa_control_center.py` – Control Center (Steuerungsboard)
4. `python scripts/qa/qa_cockpit.py` – Status-Report

### Optionen

| Option | Wirkung |
|--------|---------|
| (keine) | Generiert docs/qa/QA_STATUS.md |
| `--json` | Zusätzlich docs/qa/QA_STATUS.json |

---

*CI Test Levels erstellt am 15. März 2026. QA-Cockpit ergänzt.*
